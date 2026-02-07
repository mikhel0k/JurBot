from datetime import date
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import BaseModel, Field

from app.schemas.fields import (
    BaseContacts,
    BaseOptionalContacts,
    Id,
)


class EmployeeBase(BaseModel, BaseContacts):
    first_name: Annotated[
        str,
        Field(..., max_length=150, description="Employee first name (given name)."),
    ]
    last_name: Annotated[
        str,
        Field(..., max_length=150, description="Employee last name (family name)."),
    ]
    middle_name: Annotated[
        str,
        Field(..., max_length=150, description="Employee patronymic or middle name."),
    ]
    position: Annotated[
        str,
        Field(..., max_length=150, description="Job title or position."),
    ]
    salary: Annotated[
        Decimal,
        Field(
            ...,
            description="Monthly or agreed salary; stored with 2 decimal places.",
        ),
    ]
    status: Annotated[
        str,
        Field(
            ...,
            max_length=150,
            description="Employment status (e.g. active, on leave, dismissed).",
        ),
    ]
    hire_date: Annotated[
        date,
        Field(..., description="Date when the employee was hired."),
    ]
    passport_series: Annotated[
        str,
        Field(..., max_length=10, description="Passport series (4 digits)."),
    ]
    passport_number: Annotated[
        str,
        Field(..., max_length=10, description="Passport number (6 digits)."),
    ]
    passport_issued_date: Annotated[
        date,
        Field(..., description="Date when the passport was issued."),
    ]
    passport_issued_place: Annotated[
        str,
        Field(..., max_length=255, description="Passport issuing authority name."),
    ]
    passport_issued_code: Annotated[
        str,
        Field(..., max_length=10, description="Division code."),
    ]
    inn: Annotated[
        str,
        Field(
            ...,
            min_length=10,
            max_length=12,
            description="Tax ID (INN); 10 or 12 digits.",
        ),
    ]
    snils: Annotated[
        str,
        Field(..., min_length=11, max_length=11, description="Insurance number (SNILS)."),
    ]
    address: Annotated[
        str,
        Field(..., max_length=255, description="Registration or residential address."),
    ]


class EmployeeCreate(EmployeeBase):
    company_id: Id


class EmployeeUpdate(BaseModel, BaseOptionalContacts):
    first_name: Annotated[
        Optional[str],
        Field(None, max_length=150, description="New first name."),
    ]
    last_name: Annotated[
        Optional[str],
        Field(None, max_length=150, description="New last name."),
    ]
    middle_name: Annotated[
        Optional[str],
        Field(None, max_length=150, description="New patronymic or middle name."),
    ]
    position: Annotated[
        Optional[str],
        Field(None, max_length=150, description="New job title or position."),
    ]
    salary: Annotated[
        Optional[Decimal],
        Field(None, description="New salary; 2 decimal places."),
    ]
    status: Annotated[
        Optional[str],
        Field(None, max_length=150, description="New employment status."),
    ]
    hire_date: Annotated[
        Optional[date],
        Field(None, description="New or corrected hire date."),
    ]
    passport_series: Annotated[
        Optional[str],
        Field(None, max_length=10, description="New passport series."),
    ]
    passport_number: Annotated[
        Optional[str],
        Field(None, max_length=10, description="New passport number."),
    ]
    passport_issued_date: Annotated[
        Optional[date],
        Field(None, description="New passport issue date."),
    ]
    passport_issued_place: Annotated[
        Optional[str],
        Field(None, max_length=255, description="New issuing authority."),
    ]
    passport_issued_code: Annotated[
        Optional[str],
        Field(None, max_length=10, description="New division code."),
    ]
    inn: Annotated[
        Optional[str],
        Field(None, min_length=10, max_length=12, description="New INN."),
    ]
    snils: Annotated[
        Optional[str],
        Field(None, min_length=11, max_length=11, description="New SNILS."),
    ]
    address: Annotated[
        Optional[str],
        Field(None, max_length=255, description="New address."),
    ]


class EmployeeResponse(EmployeeBase):
    id: Id
    company_id: Id

    model_config = {"from_attributes": True}
