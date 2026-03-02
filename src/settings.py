from pathlib import Path
from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings
# from passlib.context import CryptContext
from argon2 import PasswordHasher

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


# pwd_context = CryptContext(schemes=["bcrypt"])
ph = PasswordHasher()


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    SECRET_KEY: str = "2sdf234wrweddgdfgdfgfs2"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    USER: dict = {
        "marius": {
            "username": "marius",
            "password": ph.hash("Changeme_123")
        },
    }
    M2M_CLIENTS: dict = {
        "adk-agent-orchestrator": {
            "client_id": "adk-agent-orchestrator",
            "client_secret": ph.hash("AgentSecret_123"),
        }
    }


def get_settings():
    return Settings()