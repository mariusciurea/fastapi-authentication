from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from src.auth.auth import get_current_machine_user
from src.data_models.models import CommandExecution, User


command_router = APIRouter()


def get_command_data(device: str, command: str) -> CommandExecution:
    try:
        return CommandExecution(device=device, command=command)
    except ValidationError as exc:
        errors = exc.errors()
        message = errors[0].get("msg") if errors else "Invalid command"
        raise HTTPException(status_code=422, detail=message)


@command_router.get("/execute-command", response_model=CommandExecution, tags=["commands"])
def execute_command(
    command_data: CommandExecution = Depends(get_command_data),
    _current_machine: User = Depends(get_current_machine_user),
):
    return command_data
