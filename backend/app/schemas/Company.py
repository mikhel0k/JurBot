from typing import Annotated, Optional
from pydantic import BaseModel, Field

from app.schemas.fields import Id


class CompanyBase(BaseModel):
    name: Annotated[
        str,
        Field(
            ...,
            min_length=3,
            max_length=255,
            description="Official or trade name of the company.",
        ),
    ]
    inn: Annotated[
        str,
        Field(
            ...,
            min_length=10,
            max_length=10,
            description="Tax identification number (INN); 10 digits for legal entities.",
        ),
    ]
    snils: Annotated[
        str,
        Field(
            ...,
            min_length=11,
            max_length=11,
            description="Insurance number (SNILS); 11 digits in XXX-XXX-XXX XX format.",
        ),
    ]
    address: Annotated[
        str,
        Field(
            ...,
            min_length=3,
            max_length=255,
            description="Legal or actual address of the company.",
        ),
    ]


class CompanyCreate(CompanyBase):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "ООО Рога и копыта",
                    "inn": "7707083893",
                    "snils": "12345678901",
                    "address": "г. Москва, ул. Примерная, д. 1",
                }
            ]
        }
    }


class CompanyUpdate(BaseModel):
    name: Annotated[
        Optional[str],
        Field(
            None,
            min_length=3,
            max_length=255,
            description="New official or trade name of the company.",
        ),
    ]
    inn: Annotated[
        Optional[str],
        Field(
            None,
            min_length=10,
            max_length=10,
            description="New tax identification number (INN); 10 digits.",
        ),
    ]
    snils: Annotated[
        Optional[str],
        Field(
            None,
            min_length=11,
            max_length=11,
            description="New insurance number (SNILS); 11 digits.",
        ),
    ]
    address: Annotated[
        Optional[str],
        Field(
            None,
            min_length=3,
            max_length=255,
            description="New legal or actual address of the company.",
        ),
    ]


class CompanyResponse(CompanyBase):
    id: Id
    owner_id: Id

    model_config = {"from_attributes": True}
