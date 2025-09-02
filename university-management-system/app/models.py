from sqlmodel import SQLModel, Field
from typing import Optional, List
from pydantic import BaseModel, EmailStr
import json

# Student Models


class StudentBase(SQLModel):
    name: str
    age: int
    email: EmailStr
    grades: str = Field(default="[]")  # Store as JSON string


class Student(StudentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    @property
    def grades_list(self) -> List[float]:
        """Convert grades JSON string to list"""
        try:
            return json.loads(self.grades)
        except (json.JSONDecodeError, TypeError):
            return []

    @grades_list.setter
    def grades_list(self, value: List[float]):
        """Convert grades list to JSON string"""
        self.grades = json.dumps(value)


class StudentCreate(StudentBase):
    grades: Optional[List[float]] = []

    def dict(self, **kwargs):
        d = super().dict(**kwargs)
        if 'grades' in d and isinstance(d['grades'], list):
            d['grades'] = json.dumps(d['grades'])
        return d


class StudentUpdate(SQLModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[EmailStr] = None
    grades: Optional[List[float]] = None

    def dict(self, **kwargs):
        d = super().dict(**kwargs)
        if 'grades' in d and d['grades'] is not None and isinstance(d['grades'], list):
            d['grades'] = json.dumps(d['grades'])
        return d

# User Models for Authentication


class User(BaseModel):
    username: str
    password: str
    is_active: bool = True


class UserLogin(BaseModel):
    username: str
    password: str
