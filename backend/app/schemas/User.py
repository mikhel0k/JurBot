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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "phone_number": "+79991234567",
                    "full_name": "Иван Иванов",
                    "password": "securepassword123",
                }
            ]
        }
    }


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


class Confirm(BaseModel):
    """JTI (из register/login) и 6-значный код из email."""
    jti: str
    code: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"jti": "550e8400-e29b-41d4-a716-446655440000", "code": "123456"}]
        }
    }


class Login(BaseModel):
    email: Email
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"email": "user@example.com", "password": "secret123"}]
        }
    }


class LoginCachePayload(BaseModel):
    """Формат данных в Redis при подтверждении входа (ключ: {jti}_{code})."""
    id: int
    email: str
    phone_number: str
    full_name: str
