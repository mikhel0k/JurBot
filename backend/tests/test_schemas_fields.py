import pytest
from pydantic import ValidationError

from app.schemas.fields import (
    EMAIL_MAX_LENGTH,
    PHONE_NUMBER_MAX_LENGTH,
    BaseContacts,
    BaseOptionalContacts,
)


class TestBaseContacts:
    def test_valid_email_and_phone_plus7(self):
        data = {
            "email": "user@example.com",
            "phone_number": "+79991234567",
        }
        obj = BaseContacts(**data)
        assert obj.email == "user@example.com"
        assert obj.phone_number == "+79991234567"

    def test_valid_phone_8_normalized_to_plus7(self):
        data = {
            "email": "a@b.ru",
            "phone_number": "89991234567",
        }
        obj = BaseContacts(**data)
        assert obj.phone_number == "+79991234567"

    def test_email_at_max_length_valid(self):
        local = "a" * (EMAIL_MAX_LENGTH - 10)
        email = f"{local}@mail.ru"
        assert len(email) <= EMAIL_MAX_LENGTH
        obj = BaseContacts(email=email, phone_number="+79991234567")
        assert obj.email == email

    def test_email_over_max_length_invalid(self):
        email = "a" * (EMAIL_MAX_LENGTH + 1) + "@x.ru"
        with pytest.raises(ValidationError):
            BaseContacts(email=email, phone_number="+79991234567")

    def test_phone_at_max_length_valid(self):
        # Валидатор допускает только +7 и 10 цифр (всего 12 символов)
        phone = "+7" + "9" * 10
        assert len(phone) == 12
        obj = BaseContacts(email="a@b.ru", phone_number=phone)
        assert obj.phone_number == phone

    def test_phone_over_max_length_invalid(self):
        # Больше 10 цифр после +7 не допускается
        phone = "+7" + "9" * 11
        with pytest.raises(ValidationError):
            BaseContacts(email="a@b.ru", phone_number=phone)

    def test_invalid_phone_not_starting_with_8_or_plus7(self):
        with pytest.raises(ValidationError) as exc_info:
            BaseContacts(email="a@b.ru", phone_number="9991234567")
        assert "phone_number" in str(exc_info.value) or "Phone number" in str(exc_info.value)

    def test_invalid_phone_with_letters(self):
        with pytest.raises(ValidationError):
            BaseContacts(email="a@b.ru", phone_number="+7abc1234567")

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            BaseContacts(email="not-an-email", phone_number="+79991234567")

    def test_missing_email(self):
        with pytest.raises(ValidationError):
            BaseContacts(phone_number="+79991234567")

    def test_missing_phone(self):
        with pytest.raises(ValidationError):
            BaseContacts(email="a@b.ru")

    def test_empty_email_invalid(self):
        with pytest.raises(ValidationError):
            BaseContacts(email="", phone_number="+79991234567")


class TestBaseOptionalContacts:
    def test_all_none(self):
        obj = BaseOptionalContacts(email=None, phone_number=None)
        assert obj.email is None
        assert obj.phone_number is None

    def test_valid_values(self):
        obj = BaseOptionalContacts(
            email="test@test.ru",
            phone_number="+79991234567",
        )
        assert obj.email == "test@test.ru"
        assert obj.phone_number == "+79991234567"

    def test_phone_8_normalized(self):
        obj = BaseOptionalContacts(email=None, phone_number="89991234567")
        assert obj.phone_number == "+79991234567"

    def test_phone_none_allowed(self):
        obj = BaseOptionalContacts(email="a@b.ru", phone_number=None)
        assert obj.phone_number is None

    def test_email_none_allowed(self):
        obj = BaseOptionalContacts(email=None, phone_number="+79991234567")
        assert obj.email is None

    def test_optional_email_at_max_length_valid(self):
        email = "x" * (EMAIL_MAX_LENGTH - 6) + "@x.com"
        obj = BaseOptionalContacts(email=email, phone_number="+79991234567")
        assert obj.email == email

    def test_optional_phone_invalid_still_raises(self):
        with pytest.raises(ValidationError):
            BaseOptionalContacts(email=None, phone_number="invalid")
