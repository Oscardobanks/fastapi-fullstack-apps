from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from sqlmodel import Session, select

from .models import User
from .database import get_session

# Security
security = HTTPBearer()

# Simple user storage (in production, use proper database and hashing)
users_db = {
    "admin": {"username": "admin", "password": "admin123", "email": "admin@example.com", "id": 1},
    "user1": {"username": "user1", "password": "user123", "email": "user1@example.com", "id": 2},
    "user2": {"username": "user2", "password": "user456", "email": "user2@example.com", "id": 3}
}


def authenticate_user(username: str, password: str) -> User | None:
    user_data = users_db.get(username)
    if user_data and user_data["password"] == password:
        return User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            # In production, this would be hashed
            hashed_password=user_data["password"]
        )
    return None


def get_current_user(
    token: str = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    # Simple token validation - using username as token
    username = token.credentials
    user_data = users_db.get(username)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return User(
        id=user_data["id"],
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=user_data["password"]
    )
