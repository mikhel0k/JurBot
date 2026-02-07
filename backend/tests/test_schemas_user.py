from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.schemas.User import UserCreate, UserResponse, UserUpdate


def _valid_user_create_payload():
    return {
        "email": "ivanov@example.com",
        "phone_number": "+79991234567",
        "full_name": "Иванов Иван Иванович",
        "password": "secret123",
    }


class TestUserCreate:
    def test_valid(self):
        data = _valid_user_create_payload()
        obj = UserCreate(**data)
        assert obj.email == data["email"]
        assert obj.phone_number == "+79991234567"
        assert obj.full_name == data["full_name"]
        assert obj.password == data["password"]

    def test_password_required(self):
        data = _valid_user_create_payload()
        del data["password"]
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_full_name_min_length_1_valid(self):
        data = _valid_user_create_payload()
        data["full_name"] = "X"
        obj = UserCreate(**data)
        assert obj.full_name == "X"

    def test_full_name_empty_invalid(self):
        data = _valid_user_create_payload()
        data["full_name"] = ""
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_full_name_max_length_150_valid(self):
        data = _valid_user_create_payload()
        data["full_name"] = "А" * 150
        obj = UserCreate(**data)
        assert len(obj.full_name) == 150

    def test_full_name_too_long_invalid(self):
        data = _valid_user_create_payload()
        data["full_name"] = "x" * 151
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_password_min_length_1_valid(self):
        data = _valid_user_create_payload()
        data["password"] = "1"
        obj = UserCreate(**data)
        assert obj.password == "1"

    def test_password_empty_invalid(self):
        data = _valid_user_create_payload()
        data["password"] = ""
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_password_max_length_255_valid(self):
        data = _valid_user_create_payload()
        data["password"] = "x" * 255
        obj = UserCreate(**data)
        assert len(obj.password) == 255

    def test_password_too_long_invalid(self):
        data = _valid_user_create_payload()
        data["password"] = "x" * 256
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_create_inherits_contact_validation(self):
        data = _valid_user_create_payload()
        data["email"] = "not-email"
        with pytest.raises(ValidationError):
            UserCreate(**data)
        data = _valid_user_create_payload()
        data["phone_number"] = "999"
        with pytest.raises(ValidationError):
            UserCreate(**data)


class TestUserUpdate:
    def test_all_optional(self):
        obj = UserUpdate(email=None, phone_number=None, full_name=None)
        assert obj.full_name is None

    def test_partial_update(self):
        obj = UserUpdate(email=None, phone_number=None, full_name="Петров Пётр")
        assert obj.full_name == "Петров Пётр"

    def test_full_name_min_length_1_valid(self):
        obj = UserUpdate(email=None, phone_number=None, full_name="X")
        assert obj.full_name == "X"

    def test_full_name_empty_invalid(self):
        with pytest.raises(ValidationError):
            UserUpdate(
                email=None,
                phone_number=None,
                full_name="",
            )

    def test_full_name_max_length_150_valid(self):
        obj = UserUpdate(email=None, phone_number=None, full_name="А" * 150)
        assert len(obj.full_name) == 150

    def test_full_name_too_long_invalid(self):
        with pytest.raises(ValidationError):
            UserUpdate(email=None, phone_number=None, full_name="x" * 151)

    def test_optional_contacts_can_be_set(self):
        obj = UserUpdate(
            email="new@mail.ru",
            phone_number="+79997654321",
            full_name="Новый",
        )
        assert obj.email == "new@mail.ru"
        assert obj.phone_number == "+79997654321"


class TestUserResponse:
    def test_from_attributes(self):
        mock = MagicMock()
        mock.id = 1
        mock.email = "u@u.ru"
        mock.phone_number = "+79991234567"
        mock.full_name = "Test User"
        obj = UserResponse.model_validate(mock)
        assert obj.id == 1
        assert obj.email == "u@u.ru"
        assert obj.full_name == "Test User"

    def test_response_has_no_password_field(self):
        assert "password" not in UserResponse.model_fields

    def test_response_dump_excludes_password(self):
        obj = UserResponse(id=1, email="a@b.ru", phone_number="+79991234567", full_name="X")
        d = obj.model_dump()
        assert "password" not in d
        assert d["id"] == 1
        assert d["email"] == "a@b.ru"
        assert d["full_name"] == "X"

    def test_id_required(self):
        with pytest.raises(ValidationError):
            UserResponse(
                email="a@b.ru",
                phone_number="+79991234567",
                full_name="X",
            )

    def test_id_positive_only(self):
        with pytest.raises(ValidationError):
            UserResponse(id=0, email="a@b.ru", phone_number="+79991234567", full_name="X")
        with pytest.raises(ValidationError):
            UserResponse(id=-1, email="a@b.ru", phone_number="+79991234567", full_name="X")

    def test_id_valid(self):
        obj = UserResponse(id=1, email="a@b.ru", phone_number="+79991234567", full_name="X")
        assert obj.id == 1

    def test_serialization_roundtrip(self):
        obj = UserResponse(id=1, email="a@b.ru", phone_number="+79991234567", full_name="Иван")
        d = obj.model_dump()
        obj2 = UserResponse.model_validate(d)
        assert obj2.id == obj.id
        assert obj2.email == obj.email
        assert obj2.full_name == obj.full_name

    def test_model_dump_json(self):
        obj = UserResponse(id=1, email="a@b.ru", phone_number="+79991234567", full_name="X")
        js = obj.model_dump_json()
        assert "password" not in js
        assert "1" in js
        assert "a@b.ru" in js
