from fastapi import APIRouter, Depends

from src.data_models.models import User
from src.auth.auth import get_current_human_user


me_router = APIRouter()

@me_router.get("/me", response_model=User, tags=["me"])
def get_user(current_user: User = Depends(get_current_human_user)):
    return current_user