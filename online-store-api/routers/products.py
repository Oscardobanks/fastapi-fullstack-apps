from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from ..models import Product, ProductCreate, ProductUpdate, User
from ..database import get_session
from ..auth import get_current_admin_user

# Public router for products
router = APIRouter()

# Admin router for products
admin_router = APIRouter()


@router.get("/", response_model=List[Product])
def get_products(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    products = session.exec(select(Product).offset(skip).limit(limit)).all()
    return products


@router.get("/{product_id}", response_model=Product)
def get_product(
    product_id: int,
    session: Session = Depends(get_session)
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@admin_router.post("/products/", response_model=Product)
def create_product(
    product: ProductCreate,
    session: Session = Depends(get_session),
):
    db_product = Product.from_orm(product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@admin_router.put("/products/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product: ProductUpdate,
    session: Session = Depends(get_session),
):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    product_data = product.dict(exclude_unset=True)
    for key, value in product_data.items():
        setattr(db_product, key, value)

    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@admin_router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    session.delete(product)
    session.commit()
    return {"message": "Product deleted successfully"}
