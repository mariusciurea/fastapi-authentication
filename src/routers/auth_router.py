from fastapi import HTTPException
from datetime import timedelta

from fastapi import APIRouter, Depends, Form

from src.data_models.models import Token
from src.settings import *
from src.auth.auth import authenticate_user, authenticate_client, create_access_token


settings = get_settings()

token_router = APIRouter(prefix="/auth")

@token_router.post("/token", response_model=Token, tags=["auth"])
def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password!")

    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "token_type": "bearer"}


@token_router.post("/m2m-token", response_model=Token, tags=["auth"])
def get_m2m_token(
    client_id: str = Form(...),
    client_secret: str = Form(...),
    grant_type: str = Form(default="client_credentials"),
):
    if grant_type != "client_credentials":
        raise HTTPException(status_code=400, detail="Unsupported grant type!")

    client = authenticate_client(client_id, client_secret)
    if not client:
        raise HTTPException(status_code=400, detail="Incorrect client credentials!")

    access_token = create_access_token(
        data={"sub": client["client_id"], "type": "m2m"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "token_type": "bearer"}