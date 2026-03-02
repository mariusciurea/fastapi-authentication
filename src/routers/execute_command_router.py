import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from src.auth.auth import get_current_machine_client
from src.data_models.models import CommandExecution, User
from src.settings import get_settings

settings = get_settings()
command_router = APIRouter()


def get_command_data(device: str, command: str) -> CommandExecution:
    try:
        return CommandExecution(device=device, command=command)
    except ValidationError as exc:
        errors = exc.errors()
        message = errors[0].get("msg") if errors else "Invalid command"
        raise HTTPException(status_code=422, detail=message)


def read_router_data(file_path: Path):
    try:
        with open(file_path, "r") as fr:
            return json.load(fr)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")


@command_router.get("/execute-command", tags=["commands"])
def execute_command(
    command_data: CommandExecution = Depends(get_command_data),
    _current_machine: User = Depends(get_current_machine_client),
):
    router_data = read_router_data(settings.DATA_DIR / "cisco_show_commands.json")

    for cmd in router_data["commands"]:
        if cmd["command"] == command_data.command and cmd["device_name"] == command_data.device:
            return {
                "command": cmd["command"],
                "device_name": cmd["device_name"],
                "description": cmd["description"],
                "output": cmd["sample_output"],
            }

    raise HTTPException(status_code=404, detail="Command or device not found")