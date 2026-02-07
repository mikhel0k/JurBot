from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, Field, PositiveInt, field_validator

from app.core import validation_of_phone_number

EMAIL_MAX_LENGTH = 254
PHONE_NUMBER_MAX_LENGTH = 20

Id = Annotated[
    PositiveInt,
    Field(..., description="Unique identifier."),
]

Email = Annotated[
    EmailStr,
    Field(..., max_length=EMAIL_MAX_LENGTH, description="Email address."),
]
EmailOptional = Annotated[
    Optional[EmailStr],
    Field(None, max_length=EMAIL_MAX_LENGTH, description="Email address."),
]

PhoneNumber = Annotated[
    str,
    Field(
        ...,
        max_length=PHONE_NUMBER_MAX_LENGTH,
        description="Contact phone number.",
    ),
]
PhoneNumberOptional = Annotated[
    Optional[str],
    Field(
        None,
        max_length=PHONE_NUMBER_MAX_LENGTH,
        description="Contact phone number.",
    ),
]

class BaseContacts(BaseModel):
    email: Email
    phone_number: PhoneNumber

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        return validation_of_phone_number(v)


class BaseOptionalContacts(BaseModel):
    email: EmailOptional
    phone_number: PhoneNumberOptional

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return validation_of_phone_number(v)


__all__ = [
    "EMAIL_MAX_LENGTH",
    "PHONE_NUMBER_MAX_LENGTH",
    "Id",
    "BaseContacts",
    "BaseOptionalContacts",
]
