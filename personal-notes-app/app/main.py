from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List
import json
import os

from .models import Note, NoteCreate, NoteUpdate
from .database import create_db_and_tables, get_session
from .middleware import RequestCounterMiddleware

# Create FastAPI app
app = FastAPI(title="Personal Notes App", version="1.0.0")

# Add CORS middleware for multiple origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom request counter middleware
app.add_middleware(RequestCounterMiddleware)

# Create database tables on startup


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


def backup_notes_to_file(session: Session):
    try:
        notes = session.exec(select(Note)).all()
        notes_data = []
        for note in notes:
            notes_data.append({
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "created_at": note.created_at.isoformat()
            })

        with open("notes.json", "w") as f:
            json.dump(notes_data, f, indent=2)
    except Exception as e:
        print(f"Error backing up notes: {e}")

# Notes endpoints


@app.post("/notes/", response_model=Note)
def create_note(
    note: NoteCreate,
    session: Session = Depends(get_session)
):
    db_note = Note.from_orm(note)
    session.add(db_note)
    session.commit()
    session.refresh(db_note)

    # Backup notes after creating
    backup_notes_to_file(session)

    return db_note


@app.get("/notes/", response_model=List[Note])
def get_notes(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    notes = session.exec(select(Note).offset(skip).limit(limit)).all()
    return notes


@app.get("/notes/{note_id}", response_model=Note)
def get_note(
    note_id: int,
    session: Session = Depends(get_session)
):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.put("/notes/{note_id}", response_model=Note)
def update_note(
    note_id: int,
    note: NoteUpdate,
    session: Session = Depends(get_session)
):
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    note_data = note.dict(exclude_unset=True)
    for key, value in note_data.items():
        setattr(db_note, key, value)

    session.add(db_note)
    session.commit()
    session.refresh(db_note)

    # Backup notes after updating
    backup_notes_to_file(session)

    return db_note


@app.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    session: Session = Depends(get_session)
):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    session.delete(note)
    session.commit()

    # Backup notes after deleting
    backup_notes_to_file(session)

    return {"message": "Note deleted successfully"}


@app.get("/notes/search/{query}", response_model=List[Note])
def search_notes(
    query: str,
    session: Session = Depends(get_session)
):
    notes = session.exec(
        select(Note).where(
            (Note.title.contains(query)) | (Note.content.contains(query))
        )
    ).all()
    return notes


@app.get("/backup/restore")
def restore_from_backup(session: Session = Depends(get_session)):
    if not os.path.exists("notes.json"):
        raise HTTPException(status_code=404, detail="Backup file not found")

    try:
        with open("notes.json", "r") as f:
            notes_data = json.load(f)

        restored_count = 0
        for note_data in notes_data:
            # Check if note already exists
            existing_note = session.get(Note, note_data.get("id"))
            if not existing_note:
                db_note = Note(
                    title=note_data["title"],
                    content=note_data["content"]
                )
                session.add(db_note)
                restored_count += 1

        session.commit()
        return {"message": f"Restored {restored_count} notes from backup"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error restoring from backup: {str(e)}"
        )

# Health check endpoint


@app.get("/")
def root():
    return {"message": "Personal Notes App is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
