from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List

from .models import Contact, ContactCreate, ContactUpdate, User, UserLogin, UserCreate
from .database import create_db_and_tables, get_session
from .auth import get_current_user, authenticate_user, create_access_token, create_user
from .middleware import IPLoggingMiddleware

# Create FastAPI app
app = FastAPI(title="Address Book API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add IP logging middleware
app.add_middleware(IPLoggingMiddleware)

# Create database tables on startup


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Authentication endpoints


@app.post("/auth/register")
def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    user = create_user(user_data, session)
    return {"message": "User registered successfully", "user_id": user.id}


@app.post("/auth/login")
def login(
    user_data: UserLogin,
    session: Session = Depends(get_session)
):
    user = authenticate_user(user_data.username, user_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Contact endpoints


@app.post("/contacts/", response_model=Contact)
def create_contact(
    contact: ContactCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_contact = Contact.from_orm(contact)
    db_contact.user_id = current_user.id
    session.add(db_contact)
    session.commit()
    session.refresh(db_contact)
    return db_contact


@app.get("/contacts/", response_model=List[Contact])
def get_contacts(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    contacts = session.exec(
        select(Contact)
        .where(Contact.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return contacts


@app.get("/contacts/{contact_id}", response_model=Contact)
def get_contact(
    contact_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Ensure user can only access their own contacts
    if contact.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this contact"
        )

    return contact


@app.put("/contacts/{contact_id}", response_model=Contact)
def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_contact = session.get(Contact, contact_id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Ensure user can only update their own contacts
    if db_contact.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this contact"
        )

    contact_data = contact.dict(exclude_unset=True)
    for key, value in contact_data.items():
        setattr(db_contact, key, value)

    session.add(db_contact)
    session.commit()
    session.refresh(db_contact)
    return db_contact


@app.delete("/contacts/{contact_id}")
def delete_contact(
    contact_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Ensure user can only delete their own contacts
    if contact.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this contact"
        )

    session.delete(contact)
    session.commit()
    return {"message": "Contact deleted successfully"}


@app.get("/contacts/search/{query}", response_model=List[Contact])
def search_contacts(
    query: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    contacts = session.exec(
        select(Contact).where(
            (Contact.user_id == current_user.id) &
            (
                (Contact.name.contains(query)) |
                (Contact.email.contains(query)) |
                (Contact.phone.contains(query))
            )
        )
    ).all()
    return contacts


@app.get("/user/profile")
def get_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }

# Health check endpoint


@app.get("/")
def root():
    return {"message": "Address Book API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
