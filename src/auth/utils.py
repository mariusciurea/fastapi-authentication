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
        print(username)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = settings.USER.get(username)
    if user is None:
        raise credentials_exception
    return User(username=username)