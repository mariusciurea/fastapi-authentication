"""Main entrypoint"""

from fastapi import FastAPI

from src.auth.routers import token_router
from src.routers.get_me_router import me_router

app = FastAPI()
app.include_router(token_router)
app.include_router(me_router)



