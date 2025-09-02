import json
import os
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from .models import User

# Security
security = HTTPBearer()


def load_users():
    users_file = "users.json"
    if os.path.exists(users_file):
        with open(users_file, "r") as f:
            users_data = json.load(f)
            return {user["username"]: User(**user) for user in users_data}
    else:
        # Create default users file
        default_users = [
            {"username": "admin", "password": "admin123", "is_active": True},
            {"username": "user", "password": "user123", "is_active": True}
        ]
        with open(users_file, "w") as f:
            json.dump(default_users, f, indent=2)
        return {user["username"]: User(**user) for user in default_users}


def authenticate_user(username: str, password: str) -> User | None:
    users = load_users()
    user = users.get(username)
    if user and user.password == password and user.is_active:
        return user
    return None


def get_current_user(token: str = Depends(security)) -> User:
    # Simple token validation - in production, use JWT
    users = load_users()
    username = token.credentials  # Using username as token for simplicity
    user = users.get(username)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
