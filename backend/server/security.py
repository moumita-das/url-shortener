from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
import jwt

from settings import settings

pwd = PasswordHash.recommended()
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

def _make_token(user_id: str) -> str:
    """Generate a JWT token for the given user ID."""

    payload = {
        "sub": user_id,
        "exp": datetime.now() + timedelta(minutes=600)  # Token expires in 10 hours
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token

def get_password_hash(password: str) -> str:
    """Hash a password using the recommended algorithm."""
    return pwd.hash(password)

def verify_password(plain_password: str, hashed_password: str, user_id: str) -> dict:
    """Verify a password against its hash."""
    if pwd.verify(plain_password, hashed_password):
        return {
            "token_type": "bearer",
            "access_token": _make_token(user_id=user_id) 
        }

def current_user(token: str = Depends(oauth2)) -> str:
    """Retrieve the current user from the JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")