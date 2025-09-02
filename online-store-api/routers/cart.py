from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict, List
import json
import uuid
from datetime import datetime

from ..models import CartItem, CartResponse, CartItemResponse, Product, User, Order
from ..database import get_session
from ..auth import get_current_user

router = APIRouter()

# In-memory cart storage (in production, use Redis or database)
user_carts: Dict[int, List[CartItem]] = {}


def save_order_to_file(order: Order):
    try:
        with open("orders.json", "r") as f:
            orders = json.load(f)
    except FileNotFoundError:
        orders = []

    order_dict = {
        "id": order.id,
        "user_id": order.user_id,
        "items": [item.dict() for item in order.items],
        "total_amount": order.total_amount,
        "created_at": order.created_at.isoformat()
    }
    orders.append(order_dict)

    with open("orders.json", "w") as f:
        json.dump(orders, f, indent=2)


@router.post("/add/")
def add_to_cart(
    cart_item: CartItem,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Verify product exists and has sufficient stock
    product = session.get(Product, cart_item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock < cart_item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    # Initialize user cart if not exists
    if current_user.id not in user_carts:
        user_carts[current_user.id] = []

    # Check if item already in cart
    user_cart = user_carts[current_user.id]
    for item in user_cart:
        if item.product_id == cart_item.product_id:
            item.quantity += cart_item.quantity
            break
    else:
        user_cart.append(cart_item)

    return {"message": "Item added to cart successfully"}


@router.get("/", response_model=CartResponse)
def get_cart(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.id not in user_carts:
        return CartResponse(items=[], total_amount=0.0)

    cart_items = []
    total_amount = 0.0

    for cart_item in user_carts[current_user.id]:
        product = session.get(Product, cart_item.product_id)
        if product:
            item_total = product.price * cart_item.quantity
            cart_items.append(CartItemResponse(
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                quantity=cart_item.quantity,
                total=item_total
            ))
            total_amount += item_total

    return CartResponse(items=cart_items, total_amount=total_amount)


@router.post("/checkout/")
def checkout(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.id not in user_carts or not user_carts[current_user.id]:
        raise HTTPException(status_code=400, detail="Cart is empty")

    cart_items = []
    total_amount = 0.0

    # Process each cart item
    for cart_item in user_carts[current_user.id]:
        product = session.get(Product, cart_item.product_id)
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Product {cart_item.product_id} not found")

        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {product.name}"
            )

        # Update product stock
        product.stock -= cart_item.quantity
        session.add(product)

        # Add to order items
        item_total = product.price * cart_item.quantity
        cart_items.append(CartItemResponse(
            product_id=product.id,
            product_name=product.name,
            price=product.price,
            quantity=cart_item.quantity,
            total=item_total
        ))
        total_amount += item_total

    # Create order
    order = Order(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        items=cart_items,
        total_amount=total_amount,
        created_at=datetime.now()
    )

    # Save order to file
    save_order_to_file(order)

    # Clear cart
    user_carts[current_user.id] = []

    # Commit database changes
    session.commit()

    return {
        "message": "Order placed successfully",
        "order_id": order.id,
        "total_amount": order.total_amount
    }


@router.delete("/clear/")
def clear_cart(current_user: User = Depends(get_current_user)):
    if current_user.id in user_carts:
        user_carts[current_user.id] = []
    return {"message": "Cart cleared successfully"}
