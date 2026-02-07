from typing import Annotated
from pydantic import Field
from pydantic import BaseModel

from app.schemas.fields import (
    BaseContacts,
    BaseOptionalContacts,
    Id,
    Email,
)


class UserBase(BaseContacts):
    full_name: Annotated[
        str,
        Field(
            ...,
            min_length=1,
            max_length=150,
            description="Full name of the user (surname, first name, patronymic).",
        ),
    ]


class UserCreate(UserBase):
    password: Annotated[
        str,
        Field(
            ...,
            min_length=1,
            max_length=255,
            description="Plain-text password; stored as hash, never returned.",
        ),
    ]


class UserUpdate(BaseOptionalContacts):
    full_name: Annotated[
        str | None,
        Field(
            None,
            min_length=1,
            max_length=150,
            description="New full name of the user.",
        ),
    ]


class UserResponse(UserBase):
    id: Id

    model_config = {"from_attributes": True}


class Confirm_Registration(BaseModel):
    jti: str
    code: str


class Login(BaseModel):
    email: Email
    password: str