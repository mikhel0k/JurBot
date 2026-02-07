from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.schemas.Employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate


def _valid_employee_base():
    return {
        "email": "employee@company.ru",
        "phone_number": "+79991234567",
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "position": "Менеджер",
        "salary": Decimal("50000.00"),
        "status": "active",
        "hire_date": date(2020, 1, 15),
        "passport_series": "1234",
        "passport_number": "567890",
        "passport_issued_date": date(2015, 5, 20),
        "passport_issued_place": "ОВД Москвы",
        "passport_issued_code": "770-001",
        "inn": "123456789012",
        "snils": "12345678901",
        "address": "г. Москва, ул. Ленина, 1",
    }


class TestEmployeeCreate:
    def test_valid(self):
        data = {**_valid_employee_base(), "company_id": 1}
        obj = EmployeeCreate(**data)
        assert obj.company_id == 1
        assert obj.first_name == "Иван"
        assert obj.salary == Decimal("50000.00")
        assert obj.inn == "123456789012"

    def test_company_id_required(self):
        data = _valid_employee_base()
        with pytest.raises(ValidationError):
            EmployeeCreate(**data)

    def test_company_id_positive_only(self):
        data = {**_valid_employee_base(), "company_id": 0}
        with pytest.raises(ValidationError):
            EmployeeCreate(**data)
        data["company_id"] = -1
        with pytest.raises(ValidationError):
            EmployeeCreate(**data)

    def test_first_name_max_150(self):
        data = {**_valid_employee_base(), "company_id": 1}
        data["first_name"] = "X" * 150
        obj = EmployeeCreate(**data)
        assert len(obj.first_name) == 150
        data["first_name"] = "X" * 151
        with pytest.raises(ValidationError):
            EmployeeCreate(**data)

    def test_last_name_middle_name_position_status_max_150(self):
        for field in ("last_name", "middle_name", "position", "status"):
            data = {**_valid_employee_base(), "company_id": 1}
            data[field] = "X" * 150
            obj = EmployeeCreate(**data)
            assert len(getattr(obj, field)) == 150
            data[field] = "X" * 151
            with pytest.raises(ValidationError):
                EmployeeCreate(**data)

    def test_passport_series_number_code_max_10(self):
        for field in ("passport_series", "passport_number", "passport_issued_code"):
            data = {**_valid_employee_base(), "company_id": 1}
            data[field] = "X" * 10
            obj = EmployeeCreate(**data)
            assert len(getattr(obj, field)) == 10
            data[field] = "X" * 11
            with pytest.raises(ValidationError):
                EmployeeCreate(**data)

    def test_passport_issued_place_max_255(self):
        data = {**_valid_employee_base(), "company_id": 1}
        data["passport_issued_place"] = "X" * 255
        obj = EmployeeCreate(**data)
        assert len(obj.passport_issued_place) == 255
        data["passport_issued_place"] = "X" * 256
        with pytest.raises(ValidationError):
            EmployeeCreate(**data)

    def test_inn_10_digits_valid(self):
        data = {**_valid_employee_base(), "company_id": 1}
        data["inn"] = "1234567890"
        obj = EmployeeCreate(**data)
        assert obj.inn == "1234567890"

    def test_inn_12_digits_valid(self):
        data = {**_valid_employee_base(), "company_id": 1}
        data["inn"] = "123456789012"
        obj = EmployeeCreate(**data)
        assert obj.inn == "123456789012"

    def test_inn_9_invalid(self):
        data = {**_valid_employee_base(), "company_id": 1}
        data["inn"] = "123456789"
        with pytest.raises(ValidationError):
            EmployeeCreate(**data)

    def test_inn_13_invalid(self):
        data = {**_valid_employee_base(), "company_id": 1}
        data["inn"] = "1234567890123"
        with pytest.raises(ValidationError):
            EmployeeCreate(**data)

    def test_snils_exactly_11_valid(self):
        data = {**_valid_employee_base(), "company_id": 1}
        data["snils"] = "12345678901"
        obj = EmployeeCreate(**data)
        assert obj.snils == "12345678901"

    def test_snils_10_invalid(self):
        data = {**_valid_employee_base(), "company_id": 1}
        data["snils"] = "1234567890"
        with pytest.raises(ValidationError):
            EmployeeCreate(**data)

    def test_address_max_255(self):
        data = {**_valid_employee_base(), "company_id": 1}
        data["address"] = "X" * 255
        obj = EmployeeCreate(**data)
        assert len(obj.address) == 255
        data["address"] = "X" * 256
        with pytest.raises(ValidationError):
            EmployeeCreate(**data)

    def test_salary_decimal_accepted(self):
        data = {**_valid_employee_base(), "company_id": 1}
        data["salary"] = Decimal("0.01")
        obj = EmployeeCreate(**data)
        assert obj.salary == Decimal("0.01")

    def test_hire_date_and_passport_date_required(self):
        data = {**_valid_employee_base(), "company_id": 1}
        del data["hire_date"]
        with pytest.raises(ValidationError):
            EmployeeCreate(**data)
        data = {**_valid_employee_base(), "company_id": 1}
        del data["passport_issued_date"]
        with pytest.raises(ValidationError):
            EmployeeCreate(**data)

    def test_invalid_date_type_rejected(self):
        data = {**_valid_employee_base(), "company_id": 1}
        data["hire_date"] = "not-a-date"
        with pytest.raises(ValidationError):
            EmployeeCreate(**data)


class TestEmployeeUpdate:
    def test_all_optional(self):
        obj = EmployeeUpdate(
            email=None,
            phone_number=None,
            first_name=None,
            last_name=None,
            middle_name=None,
            position=None,
            salary=None,
            status=None,
            hire_date=None,
            passport_series=None,
            passport_number=None,
            passport_issued_date=None,
            passport_issued_place=None,
            passport_issued_code=None,
            inn=None,
            snils=None,
            address=None,
        )
        assert obj.first_name is None
        assert obj.salary is None

    def test_partial(self):
        obj = EmployeeUpdate(
            email=None,
            phone_number=None,
            first_name="Пётр",
            last_name=None,
            middle_name=None,
            position=None,
            salary=Decimal("60000"),
            status=None,
            hire_date=None,
            passport_series=None,
            passport_number=None,
            passport_issued_date=None,
            passport_issued_place=None,
            passport_issued_code=None,
            inn=None,
            snils=None,
            address=None,
        )
        assert obj.first_name == "Пётр"
        assert obj.salary == Decimal("60000")

    def test_update_first_name_max_150(self):
        obj = EmployeeUpdate(
            email=None,
            phone_number=None,
            first_name="X" * 150,
            last_name=None,
            middle_name=None,
            position=None,
            salary=None,
            status=None,
            hire_date=None,
            passport_series=None,
            passport_number=None,
            passport_issued_date=None,
            passport_issued_place=None,
            passport_issued_code=None,
            inn=None,
            snils=None,
            address=None,
        )
        assert len(obj.first_name) == 150
        with pytest.raises(ValidationError):
            EmployeeUpdate(
                email=None,
                phone_number=None,
                first_name="X" * 151,
                last_name=None,
                middle_name=None,
                position=None,
                salary=None,
                status=None,
                hire_date=None,
                passport_series=None,
                passport_number=None,
                passport_issued_date=None,
                passport_issued_place=None,
                passport_issued_code=None,
                inn=None,
                snils=None,
                address=None,
            )

    def test_update_inn_10_and_12_valid(self):
        obj = EmployeeUpdate(
            email=None,
            phone_number=None,
            first_name=None,
            last_name=None,
            middle_name=None,
            position=None,
            salary=None,
            status=None,
            hire_date=None,
            passport_series=None,
            passport_number=None,
            passport_issued_date=None,
            passport_issued_place=None,
            passport_issued_code=None,
            inn="1234567890",
            snils=None,
            address=None,
        )
        assert obj.inn == "1234567890"
        obj = EmployeeUpdate(
            email=None,
            phone_number=None,
            first_name=None,
            last_name=None,
            middle_name=None,
            position=None,
            salary=None,
            status=None,
            hire_date=None,
            passport_series=None,
            passport_number=None,
            passport_issued_date=None,
            passport_issued_place=None,
            passport_issued_code=None,
            inn="123456789012",
            snils=None,
            address=None,
        )
        assert obj.inn == "123456789012"

    def test_update_snils_11_valid(self):
        obj = EmployeeUpdate(
            email=None,
            phone_number=None,
            first_name=None,
            last_name=None,
            middle_name=None,
            position=None,
            salary=None,
            status=None,
            hire_date=None,
            passport_series=None,
            passport_number=None,
            passport_issued_date=None,
            passport_issued_place=None,
            passport_issued_code=None,
            inn=None,
            snils="12345678901",
            address=None,
        )
        assert obj.snils == "12345678901"


class TestEmployeeResponse:
    def test_from_attributes(self):
        mock = MagicMock()
        mock.id = 1
        mock.company_id = 5
        mock.first_name = "Иван"
        mock.last_name = "Иванов"
        mock.middle_name = "И."
        mock.email = "e@e.ru"
        mock.phone_number = "+79991234567"
        mock.position = "Директор"
        mock.salary = Decimal("100000")
        mock.status = "active"
        mock.hire_date = date(2019, 1, 1)
        mock.passport_series = "1234"
        mock.passport_number = "567890"
        mock.passport_issued_date = date(2010, 1, 1)
        mock.passport_issued_place = "ОВД"
        mock.passport_issued_code = "770"
        mock.inn = "1234567890"
        mock.snils = "12345678901"
        mock.address = "Москва"
        obj = EmployeeResponse.model_validate(mock)
        assert obj.id == 1
        assert obj.company_id == 5
        assert obj.first_name == "Иван"

    def test_id_and_company_id_positive(self):
        data = {**_valid_employee_base(), "company_id": 1}
        create_obj = EmployeeCreate(**data)
        mock = MagicMock()
        mock.id = 0
        mock.company_id = 1
        for attr, val in create_obj.model_dump().items():
            setattr(mock, attr, val)
        with pytest.raises(ValidationError):
            EmployeeResponse.model_validate(mock)

    def test_serialization_roundtrip(self):
        mock = MagicMock()
        mock.id = 1
        mock.company_id = 2
        for k, v in _valid_employee_base().items():
            setattr(mock, k, v)
        obj = EmployeeResponse.model_validate(mock)
        d = obj.model_dump()
        obj2 = EmployeeResponse.model_validate(d)
        assert obj2.id == obj.id
        assert obj2.company_id == obj.company_id
        assert obj2.first_name == obj.first_name
