from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List
import os

from .models import Student, StudentCreate, StudentUpdate, User, UserLogin
from .database import create_db_and_tables, get_session
from .auth import authenticate_user, get_current_user
from .middleware import LoggingMiddleware

# Create FastAPI app
app = FastAPI(title="University Management System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom logging middleware
app.add_middleware(LoggingMiddleware)

# Security
security = HTTPBearer()

# Create database tables on startup


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

# Authentication endpoint


@app.post("/auth/login")
def login(user_data: UserLogin):
    user = authenticate_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    return {"access_token": user.username, "token_type": "bearer"}

# Student CRUD endpoints


@app.post("/students/", response_model=Student)
def create_student(
    student: StudentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_student = Student.from_orm(student)
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student


@app.get("/students/", response_model=List[Student])
def read_students(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    students = session.exec(select(Student).offset(skip).limit(limit)).all()
    return students


@app.get("/students/{student_id}", response_model=Student)
def read_student(
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific student by ID (requires authentication)"""
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.put("/students/{student_id}", response_model=Student)
def update_student(
    student_id: int,
    student: StudentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update a student (requires authentication)"""
    db_student = session.get(Student, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    student_data = student.dict(exclude_unset=True)
    for key, value in student_data.items():
        setattr(db_student, key, value)

    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student


@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a student (requires authentication)"""
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    session.delete(student)
    session.commit()
    return {"message": "Student deleted successfully"}

# Health check endpoint


@app.get("/")
def root():
    return {"message": "University Management System API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
