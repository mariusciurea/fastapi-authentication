from pydantic import BaseModel, field_validator


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str


class CommandExecution(BaseModel):
    device: str
    command: str

    @field_validator("command")
    @classmethod
    def validate_command(cls, value: str):
        """Allow only commands that start with show"""
        if not value.lower().startswith("show"):
            raise ValueError("Only show commands are allowed")

        return value