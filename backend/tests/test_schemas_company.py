from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.schemas.Company import CompanyCreate, CompanyResponse, CompanyUpdate


def _valid_company_payload():
    return {
        "name": "ООО Рога и копыта",
        "inn": "7707083893",
        "snils": "12345678901",
        "address": "г. Москва, ул. Примерная, д. 1",
    }


class TestCompanyCreate:
    def test_valid(self):
        data = _valid_company_payload()
        obj = CompanyCreate(**data)
        assert obj.name == data["name"]
        assert obj.inn == data["inn"]
        assert obj.snils == data["snils"]
        assert obj.address == data["address"]

    def test_name_min_length_3_valid(self):
        data = _valid_company_payload()
        data["name"] = "ООО"
        obj = CompanyCreate(**data)
        assert obj.name == "ООО"

    def test_name_too_short_invalid(self):
        data = _valid_company_payload()
        data["name"] = "ab"
        with pytest.raises(ValidationError):
            CompanyCreate(**data)

    def test_name_max_length_255_valid(self):
        data = _valid_company_payload()
        data["name"] = "X" * 255
        obj = CompanyCreate(**data)
        assert len(obj.name) == 255

    def test_name_too_long_invalid(self):
        data = _valid_company_payload()
        data["name"] = "X" * 256
        with pytest.raises(ValidationError):
            CompanyCreate(**data)

    def test_inn_exactly_10_digits_valid(self):
        data = _valid_company_payload()
        data["inn"] = "1234567890"
        obj = CompanyCreate(**data)
        assert obj.inn == "1234567890"

    def test_inn_9_digits_invalid(self):
        data = _valid_company_payload()
        data["inn"] = "123456789"
        with pytest.raises(ValidationError):
            CompanyCreate(**data)

    def test_inn_11_digits_invalid(self):
        data = _valid_company_payload()
        data["inn"] = "12345678901"
        with pytest.raises(ValidationError):
            CompanyCreate(**data)

    def test_snils_exactly_11_valid(self):
        data = _valid_company_payload()
        data["snils"] = "12345678901"
        obj = CompanyCreate(**data)
        assert obj.snils == "12345678901"

    def test_snils_10_chars_invalid(self):
        data = _valid_company_payload()
        data["snils"] = "1234567890"
        with pytest.raises(ValidationError):
            CompanyCreate(**data)

    def test_snils_12_chars_invalid(self):
        data = _valid_company_payload()
        data["snils"] = "123456789012"
        with pytest.raises(ValidationError):
            CompanyCreate(**data)

    def test_address_min_length_3_valid(self):
        data = _valid_company_payload()
        data["address"] = "Мск"
        obj = CompanyCreate(**data)
        assert obj.address == "Мск"

    def test_address_too_short_invalid(self):
        data = _valid_company_payload()
        data["address"] = "ab"
        with pytest.raises(ValidationError):
            CompanyCreate(**data)

    def test_address_max_length_255_valid(self):
        data = _valid_company_payload()
        data["address"] = "X" * 255
        obj = CompanyCreate(**data)
        assert len(obj.address) == 255

    def test_address_too_long_invalid(self):
        data = _valid_company_payload()
        data["address"] = "X" * 256
        with pytest.raises(ValidationError):
            CompanyCreate(**data)


class TestCompanyUpdate:
    def test_all_optional(self):
        obj = CompanyUpdate(name=None, inn=None, snils=None, address=None)
        assert obj.name is None
        assert obj.inn is None
        assert obj.snils is None
        assert obj.address is None

    def test_partial_name(self):
        obj = CompanyUpdate(name="Новое имя", inn=None, snils=None, address=None)
        assert obj.name == "Новое имя"

    def test_update_name_min_length_3_valid(self):
        obj = CompanyUpdate(name="ООО", inn=None, snils=None, address=None)
        assert obj.name == "ООО"

    def test_update_name_too_short_invalid(self):
        with pytest.raises(ValidationError):
            CompanyUpdate(name="ab", inn=None, snils=None, address=None)

    def test_update_name_max_length_255_valid(self):
        obj = CompanyUpdate(name="X" * 255, inn=None, snils=None, address=None)
        assert len(obj.name) == 255

    def test_update_inn_exactly_10_valid(self):
        obj = CompanyUpdate(name=None, inn="1234567890", snils=None, address=None)
        assert obj.inn == "1234567890"

    def test_update_inn_9_invalid(self):
        with pytest.raises(ValidationError):
            CompanyUpdate(name=None, inn="123456789", snils=None, address=None)

    def test_update_snils_exactly_11_valid(self):
        obj = CompanyUpdate(name=None, inn=None, snils="12345678901", address=None)
        assert obj.snils == "12345678901"

    def test_update_snils_10_invalid(self):
        with pytest.raises(ValidationError):
            CompanyUpdate(name=None, inn=None, snils="1234567890", address=None)

    def test_update_address_min_3_max_255(self):
        obj = CompanyUpdate(name=None, inn=None, snils=None, address="Мск")
        assert obj.address == "Мск"
        obj = CompanyUpdate(name=None, inn=None, snils=None, address="X" * 255)
        assert len(obj.address) == 255
        with pytest.raises(ValidationError):
            CompanyUpdate(name=None, inn=None, snils=None, address="ab")


class TestCompanyResponse:
    def test_from_attributes(self):
        mock = MagicMock()
        mock.id = 1
        mock.owner_id = 10
        mock.name = "ООО Тест"
        mock.inn = "7707083893"
        mock.snils = "12345678901"
        mock.address = "Москва"
        obj = CompanyResponse.model_validate(mock)
        assert obj.id == 1
        assert obj.owner_id == 10
        assert obj.name == "ООО Тест"

    def test_id_and_owner_id_positive(self):
        with pytest.raises(ValidationError):
            CompanyResponse(
                id=0,
                owner_id=1,
                name="X" * 3,
                inn="1234567890",
                snils="12345678901",
                address="X" * 3,
            )
        with pytest.raises(ValidationError):
            CompanyResponse(
                id=1,
                owner_id=0,
                name="X" * 3,
                inn="1234567890",
                snils="12345678901",
                address="X" * 3,
            )

    def test_serialization_roundtrip(self):
        obj = CompanyResponse(
            id=1,
            owner_id=2,
            name="ООО",
            inn="1234567890",
            snils="12345678901",
            address="Москва",
        )
        d = obj.model_dump()
        obj2 = CompanyResponse.model_validate(d)
        assert obj2.id == obj.id
        assert obj2.owner_id == obj.owner_id
        assert obj2.name == obj.name
