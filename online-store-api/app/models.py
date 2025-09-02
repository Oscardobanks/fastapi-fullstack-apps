from sqlmodel import SQLModel, Field
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Product Models


class ProductBase(SQLModel):
    name: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(SQLModel):
    name: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)

# Cart Models


class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int
    total: float


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_amount: float

# Order Models


class Order(BaseModel):
    id: str
    user_id: int
    items: List[CartItemResponse]
    total_amount: float
    created_at: datetime

# User Models


class UserBase(SQLModel):
    username: str
    email: str
    is_admin: bool = False


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
