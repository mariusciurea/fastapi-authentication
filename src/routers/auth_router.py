import base64
from datetime import timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.data_models.models import Token
from src.settings import get_settings
from src.auth.auth import authenticate_user, authenticate_client, create_access_token


settings = get_settings()
token_router = APIRouter(prefix="/auth")


# dependencies
def get_client_credentials(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Basic "):
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    encoded = auth.split(" ")[1]
    decoded = base64.b64decode(encoded).decode("utf-8")

    return decoded.split(":")


# endpoints
@token_router.post("/token", response_model=Token, tags=["auth"])
def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password!")

    access_token = create_access_token(
        data={"sub": user["username"], "type": "user"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@token_router.post("/m2m-token", response_model=Token, tags=["auth"])
def get_m2m_token(credentials: tuple = Depends(get_client_credentials)):
    client_id, client_secret = credentials
    client = authenticate_client(client_id, client_secret)
    if not client:
        raise HTTPException(status_code=400, detail="Incorrect client credentials!")

    access_token = create_access_token(
        data={"sub": client["client_id"], "type": "m2m"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}