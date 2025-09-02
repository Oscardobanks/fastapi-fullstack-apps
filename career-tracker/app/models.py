from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# Job Application Models


class JobApplicationBase(SQLModel):
    company: str
    position: str
    # pending, interview, rejected, accepted
    status: str = Field(default="pending")
    date_applied: datetime = Field(default_factory=datetime.now)


class JobApplication(JobApplicationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")


class JobApplicationCreate(JobApplicationBase):
    pass


class JobApplicationUpdate(SQLModel):
    company: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None
    date_applied: Optional[datetime] = None

# User Models for Authentication


class UserBase(SQLModel):
    username: str
    email: str


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str


class UserLogin(BaseModel):
    username: str
    password: str
