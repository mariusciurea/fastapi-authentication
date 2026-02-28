from datetime import timedelta, datetime
from typing import Optional

from src.settings import get_settings
from src.settings import ph, OAUTH_2_SCHEME
from src.data_models.models import User

from jose import jwt, JWTError

from fastapi import Depends, HTTPException, status



settings = get_settings()


def verify_password(plain_password, hashed_password):
    """Verify whether the plain password matches the hash"""
    return ph.verify(hashed_password, plain_password)


def authenticate_user(username: str, password: str):
    """Authenticate user"""
    user = settings.USER.get(username)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user


def authenticate_client(client_id: str, client_secret: str):
    """Authenticate machine client"""
    client = settings.M2M_CLIENTS.get(client_id)
    if not client:
        return False
    if not verify_password(client_secret, client["client_secret"]):
        return False
    return client


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates the JWT token"""
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(token: str = Depends(OAUTH_2_SCHEME)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    token_type = payload.get("type", "user")
    if token_type == "m2m":
        client = settings.M2M_CLIENTS.get(username)
        if client is None:
            raise credentials_exception
        return User(username=f"machine:{username}")

    user = settings.USER.get(username)
    if user is None:
        raise credentials_exception
    return User(username=username)


def get_current_human_user(current_user: User = Depends(get_current_user)):
    """Allow only human users"""
    if current_user.username.startswith("machine:"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Machines are not allowed on this endpoint",
        )
    return current_user


def get_current_machine_user(current_user: User = Depends(get_current_user)):
    """Allow only machine clients"""
    if not current_user.username.startswith("machine:"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only machine clients are allowed on this endpoint",
        )
    return current_user