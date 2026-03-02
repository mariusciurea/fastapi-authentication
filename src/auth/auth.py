from datetime import timedelta, datetime
from typing import Optional

from fastapi import Depends, HTTPException, status

from src.data_models.models import User
from src.settings import get_settings, ph
from src.auth.schemes import USER_OAUTH2_SCHEME, M2M_OAUTH2_SCHEME
from src.auth.jwt_utils import decode_token, get_sub

from jose import jwt

settings = get_settings()


def verify_password(plain_password, hashed_password):
    return ph.verify(hashed_password, plain_password)


def authenticate_user(username: str, password: str):
    user = settings.USER.get(username)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user


def authenticate_client(client_id: str, client_secret: str):
    client = settings.M2M_CLIENTS.get(client_id)
    if not client:
        return False
    if not verify_password(client_secret, client["client_secret"]):
        return False
    return client


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# dependency for user
def get_current_human_user(token: str = Depends(USER_OAUTH2_SCHEME)) -> User:
    payload = decode_token(token)
    sub = get_sub(payload)

    token_type = payload.get("type", "user")
    if token_type != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires a user token",
        )

    user = settings.USER.get(sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return User(username=sub)


# dep for agents
def get_current_machine_client(token: str = Depends(M2M_OAUTH2_SCHEME)) -> User:
    payload = decode_token(token)
    sub = get_sub(payload)

    token_type = payload.get("type")
    if token_type != "m2m":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires an m2m token",
        )

    client = settings.M2M_CLIENTS.get(sub)
    if not client:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Client not found")

    return User(username=f"machine:{sub}")
