from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import BaseModel, EmailStr

# Contact Models


class ContactBase(SQLModel):
    name: str
    email: EmailStr
    phone: str


class Contact(ContactBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")


class ContactCreate(ContactBase):
    pass


class ContactUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

# User Models


class UserBase(SQLModel):
    username: str
    email: EmailStr


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
