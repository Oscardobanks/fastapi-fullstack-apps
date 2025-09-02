from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# Note Models


class NoteBase(SQLModel):
    title: str
    content: str


class Note(NoteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)


class NoteCreate(NoteBase):
    pass


class NoteUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
