"""Main entrypoint"""

from fastapi import FastAPI

from src.routers.auth_router import token_router
from src.routers.execute_command_router import command_router
from src.routers.get_me_router import me_router

app = FastAPI()
app.include_router(token_router)
app.include_router(me_router)
app.include_router(command_router)



