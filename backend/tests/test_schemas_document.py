from datetime import date
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.schemas.Document import DocumentCreate, DocumentResponse, DocumentUpdate


def _valid_document_base():
    return {
        "type": "Трудовой договор",
        "file_path": "/uploads/doc_123.pdf",
        "created_at": date(2024, 1, 15),
    }


class TestDocumentCreate:
    def test_valid(self):
        data = {**_valid_document_base(), "employee_id": 1}
        obj = DocumentCreate(**data)
        assert obj.employee_id == 1
        assert obj.type == "Трудовой договор"
        assert obj.file_path == "/uploads/doc_123.pdf"
        assert obj.created_at == date(2024, 1, 15)

    def test_employee_id_required(self):
        data = _valid_document_base()
        with pytest.raises(ValidationError):
            DocumentCreate(**data)

    def test_employee_id_positive_only(self):
        data = {**_valid_document_base(), "employee_id": 0}
        with pytest.raises(ValidationError):
            DocumentCreate(**data)
        data["employee_id"] = -1
        with pytest.raises(ValidationError):
            DocumentCreate(**data)

    def test_type_required(self):
        data = {**_valid_document_base(), "employee_id": 1}
        del data["type"]
        with pytest.raises(ValidationError):
            DocumentCreate(**data)

    def test_type_max_length_150_valid(self):
        data = {**_valid_document_base(), "employee_id": 1}
        data["type"] = "X" * 150
        obj = DocumentCreate(**data)
        assert len(obj.type) == 150

    def test_type_over_150_invalid(self):
        data = {**_valid_document_base(), "employee_id": 1}
        data["type"] = "x" * 151
        with pytest.raises(ValidationError):
            DocumentCreate(**data)

    def test_file_path_required(self):
        data = {**_valid_document_base(), "employee_id": 1}
        del data["file_path"]
        with pytest.raises(ValidationError):
            DocumentCreate(**data)

    def test_file_path_max_length_255_valid(self):
        data = {**_valid_document_base(), "employee_id": 1}
        data["file_path"] = "/" + "x" * 254
        obj = DocumentCreate(**data)
        assert len(obj.file_path) == 255

    def test_file_path_over_255_invalid(self):
        data = {**_valid_document_base(), "employee_id": 1}
        data["file_path"] = "x" * 256
        with pytest.raises(ValidationError):
            DocumentCreate(**data)

    def test_created_at_required(self):
        data = {**_valid_document_base(), "employee_id": 1}
        del data["created_at"]
        with pytest.raises(ValidationError):
            DocumentCreate(**data)

    def test_created_at_invalid_type_rejected(self):
        data = {**_valid_document_base(), "employee_id": 1}
        data["created_at"] = "2024-01-15"
        obj = DocumentCreate(**data)
        assert obj.created_at == date(2024, 1, 15)
        data["created_at"] = "not-a-date"
        with pytest.raises(ValidationError):
            DocumentCreate(**data)


class TestDocumentUpdate:
    def test_all_optional(self):
        obj = DocumentUpdate(type=None, file_path=None, created_at=None)
        assert obj.type is None
        assert obj.file_path is None
        assert obj.created_at is None

    def test_partial_type(self):
        obj = DocumentUpdate(type="Приказ", file_path=None, created_at=None)
        assert obj.type == "Приказ"

    def test_update_type_max_150_valid(self):
        obj = DocumentUpdate(type="X" * 150, file_path=None, created_at=None)
        assert len(obj.type) == 150

    def test_update_type_over_150_invalid(self):
        with pytest.raises(ValidationError):
            DocumentUpdate(type="X" * 151, file_path=None, created_at=None)

    def test_update_file_path_max_255_valid(self):
        obj = DocumentUpdate(type=None, file_path="x" * 255, created_at=None)
        assert len(obj.file_path) == 255

    def test_update_file_path_over_255_invalid(self):
        with pytest.raises(ValidationError):
            DocumentUpdate(type=None, file_path="x" * 256, created_at=None)

    def test_update_created_at(self):
        d = date(2025, 6, 1)
        obj = DocumentUpdate(type=None, file_path=None, created_at=d)
        assert obj.created_at == d


class TestDocumentResponse:
    def test_from_attributes(self):
        mock = MagicMock()
        mock.id = 1
        mock.employee_id = 10
        mock.type = "Договор"
        mock.file_path = "/path/to/file.pdf"
        mock.created_at = date(2024, 6, 1)
        obj = DocumentResponse.model_validate(mock)
        assert obj.id == 1
        assert obj.employee_id == 10
        assert obj.type == "Договор"

    def test_id_and_employee_id_positive(self):
        with pytest.raises(ValidationError):
            DocumentResponse(
                id=0,
                employee_id=1,
                type="X",
                file_path="/x",
                created_at=date(2024, 1, 1),
            )
        with pytest.raises(ValidationError):
            DocumentResponse(
                id=1,
                employee_id=0,
                type="X",
                file_path="/x",
                created_at=date(2024, 1, 1),
            )

    def test_serialization_roundtrip(self):
        obj = DocumentResponse(
            id=1,
            employee_id=2,
            type="Договор",
            file_path="/a/b.pdf",
            created_at=date(2024, 1, 1),
        )
        d = obj.model_dump()
        obj2 = DocumentResponse.model_validate(d)
        assert obj2.id == obj.id
        assert obj2.employee_id == obj.employee_id
        assert obj2.type == obj.type
        assert obj2.created_at == obj.created_at

    def test_model_dump_json(self):
        obj = DocumentResponse(
            id=1,
            employee_id=2,
            type="X",
            file_path="/x",
            created_at=date(2024, 1, 1),
        )
        js = obj.model_dump_json()
        assert "1" in js
        assert "X" in js
