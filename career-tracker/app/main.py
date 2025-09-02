from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional

from .models import JobApplication, JobApplicationCreate, JobApplicationUpdate, User
from .database import create_db_and_tables, get_session
from .auth import get_current_user, authenticate_user, UserLogin
from .middleware import UserAgentMiddleware

# Create FastAPI app
app = FastAPI(title="Career Tracker API", version="1.0.0")

# Add custom middleware
app.add_middleware(UserAgentMiddleware)

# Create database tables on startup


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

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

# Job Application endpoints


@app.post("/applications/", response_model=JobApplication)
def create_job_application(
    application: JobApplicationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_application = JobApplication.from_orm(application)
    db_application.user_id = current_user.id
    session.add(db_application)
    session.commit()
    session.refresh(db_application)
    return db_application


@app.get("/applications/", response_model=List[JobApplication])
def get_job_applications(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    applications = session.exec(
        select(JobApplication)
        .where(JobApplication.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return applications


@app.get("/applications/search", response_model=List[JobApplication])
def search_job_applications(
    status: Optional[str] = Query(
        None, description="Filter by application status"),
    company: Optional[str] = Query(None, description="Filter by company name"),
    position: Optional[str] = Query(None, description="Filter by position"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        query = select(JobApplication).where(
            JobApplication.user_id == current_user.id)

        if status:
            # Validate status
            valid_statuses = ["pending", "interview", "rejected", "accepted"]
            if status.lower() not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                )
            query = query.where(JobApplication.status.ilike(f"%{status}%"))

        if company:
            query = query.where(JobApplication.company.ilike(f"%{company}%"))

        if position:
            query = query.where(JobApplication.position.ilike(f"%{position}%"))

        applications = session.exec(query).all()
        return applications

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing search query: {str(e)}"
        )


@app.get("/applications/{application_id}", response_model=JobApplication)
def get_job_application(
    application_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    application = session.get(JobApplication, application_id)
    if not application:
        raise HTTPException(
            status_code=404, detail="Job application not found")

    # Ensure user can only access their own applications
    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this application"
        )

    return application


@app.put("/applications/{application_id}", response_model=JobApplication)
def update_job_application(
    application_id: int,
    application: JobApplicationUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_application = session.get(JobApplication, application_id)
    if not db_application:
        raise HTTPException(
            status_code=404, detail="Job application not found")

    # Ensure user can only update their own applications
    if db_application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this application"
        )

    application_data = application.dict(exclude_unset=True)
    for key, value in application_data.items():
        setattr(db_application, key, value)

    session.add(db_application)
    session.commit()
    session.refresh(db_application)
    return db_application


@app.delete("/applications/{application_id}")
def delete_job_application(
    application_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    application = session.get(JobApplication, application_id)
    if not application:
        raise HTTPException(
            status_code=404, detail="Job application not found")

    # Ensure user can only delete their own applications
    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this application"
        )

    session.delete(application)
    session.commit()
    return {"message": "Job application deleted successfully"}

# Health check endpoint


@app.get("/")
def root():
    return {"message": "Career Tracker API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
