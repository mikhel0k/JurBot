from datetime import date
from typing import Annotated, Optional

from pydantic import BaseModel, Field

from app.schemas.fields import Id


class DocumentBase(BaseModel):
    type: Annotated[
        str,
        Field(
            ...,
            max_length=150,
            description="Type or name of the document (e.g. contract, order, act).",
        ),
    ]
    file_path: Annotated[
        str,
        Field(
            ...,
            max_length=255,
            description="Path or identifier of the stored file.",
        ),
    ]
    created_at: Annotated[
        date,
        Field(..., description="Date when the document was created or uploaded."),
    ]


class DocumentCreate(DocumentBase):
    employee_id: Id


class DocumentUpdate(BaseModel):
    type: Annotated[
        Optional[str],
        Field(None, max_length=150, description="New type or name of the document."),
    ]
    file_path: Annotated[
        Optional[str],
        Field(None, max_length=255, description="New path or identifier of the file."),
    ]
    created_at: Annotated[
        Optional[date],
        Field(None, description="New creation or upload date."),
    ]


class DocumentResponse(DocumentBase):
    id: Id
    employee_id: Id

    model_config = {"from_attributes": True}
