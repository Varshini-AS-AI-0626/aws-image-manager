from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class UserInDB(UserCreate):
    hashed_password: str


class TokenData(BaseModel):
    username: str | None = None


class CreateAMI(BaseModel):
    ip: str


class UpdateLTI(BaseModel):
    launch_template_id: str


class CreateLTI(BaseModel):
    launch_template_name: str
