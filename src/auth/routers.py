from fastapi import HTTPException
from datetime import timedelta

from fastapi import APIRouter, Depends

from src.data_models.models import Token
from src.settings import *
from src.auth.utils import authenticate_user, create_access_token


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