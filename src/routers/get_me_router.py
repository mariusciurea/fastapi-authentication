from fastapi import APIRouter, Depends

from src.data_models.models import User
from src.auth.utils import get_current_user


me_router = APIRouter()

@me_router.get("/me", response_model=User, tags=["me"])
def get_user(current_user: User = Depends(get_current_user)):
    return current_user