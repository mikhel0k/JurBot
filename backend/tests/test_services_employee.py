import json
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import NotFoundError
from app.schemas import EmployeeCreate, EmployeeUpdate
from app.services.EmployeeService import create_employee, dismiss_employees, get_employee, list_employees, update_employee


def _valid_employee_create():
    return EmployeeCreate(
        email="employee@company.ru",
        phone_number="+79991234567",
        first_name="Иван",
        last_name="Иванов",
        middle_name="Иванович",
        position="Менеджер",
        salary=Decimal("50000.00"),
        status="active",
        hire_date=date(2020, 1, 15),
        passport_series="1234",
        passport_number="567890",
        passport_issued_date=date(2015, 5, 20),
        passport_issued_place="ОВД Москвы",
        passport_issued_code="770-001",
        inn="123456789012",
        snils="12345678901",
        address="г. Москва, ул. Ленина, 1",
    )


def _mock_employee(employee_id: int = 1, company_id: int = 1):
    e = MagicMock()
    e.id = employee_id
    e.company_id = company_id
    e.email = "employee@company.ru"
    e.phone_number = "+79991234567"
    e.first_name = "Иван"
    e.last_name = "Иванов"
    e.middle_name = "Иванович"
    e.position = "Менеджер"
    e.salary = Decimal("50000.00")
    e.status = "active"
    e.hire_date = date(2020, 1, 15)
    e.passport_series = "1234"
    e.passport_number = "567890"
    e.passport_issued_date = date(2015, 5, 20)
    e.passport_issued_place = "ОВД Москвы"
    e.passport_issued_code = "770-001"
    e.inn = "123456789012"
    e.snils = "12345678901"
    e.address = "г. Москва, ул. Ленина, 1"
    return e


@pytest.fixture
def session():
    s = AsyncMock()
    s.commit = AsyncMock()
    return s


@pytest.fixture
def redis():
    r = AsyncMock()
    r.get = AsyncMock(return_value=None)
    r.set = AsyncMock()
    return r


class TestListEmployees:
    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_list_employees_returns_all_for_company(self, repo_cls, session):
        emp1 = _mock_employee(employee_id=1, company_id=1)
        emp2 = _mock_employee(employee_id=2, company_id=1)
        repo_cls.return_value.get_all_by_company_id = AsyncMock(return_value=[emp1, emp2])
        result = await list_employees(session, repo_cls.return_value, 1)
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2
        repo_cls.return_value.get_all_by_company_id.assert_awaited_once_with(session, 1)

    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_list_employees_empty(self, repo_cls, session):
        repo_cls.return_value.get_all_by_company_id = AsyncMock(return_value=[])
        result = await list_employees(session, repo_cls.return_value, 1)
        assert result == []


class TestCreateEmployee:
    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.Employee")
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_create_employee_success(self, repo_cls, mock_employee_cls, session, redis):
        mock_employee_cls.return_value = MagicMock()
        created = _mock_employee(employee_id=5, company_id=1)
        repo_cls.return_value.create = AsyncMock(return_value=created)
        result = await create_employee(session, redis, repo_cls.return_value, _valid_employee_create(), 1)
        assert result is not None
        assert result.id == 5
        assert result.company_id == 1
        assert result.first_name == "Иван"
        redis.set.assert_awaited_once()
        call_args = redis.set.await_args
        assert call_args[0][0] == "employee_5"
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_create_employee_repository_error_propagates(self, repo_cls, session, redis):
        repo_cls.return_value.create = AsyncMock(side_effect=RuntimeError("DB error"))
        with pytest.raises(RuntimeError):
            await create_employee(session, redis, repo_cls.return_value, _valid_employee_create(), 1)


class TestGetEmployee:
    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_get_employee_from_cache_same_company(self, repo_cls, session, redis):
        repo_cls.return_value.get_by_id = AsyncMock()
        cached = {
            "id": 1,
            "company_id": 1,
            "email": "e@e.ru",
            "phone_number": "+79991234567",
            "first_name": "Иван",
            "last_name": "Иванов",
            "middle_name": "И.",
            "position": "Директор",
            "salary": 100000.0,
            "status": "active",
            "hire_date": "2020-01-15",
            "passport_series": "1234",
            "passport_number": "567890",
            "passport_issued_date": "2015-05-20",
            "passport_issued_place": "ОВД",
            "passport_issued_code": "770",
            "inn": "1234567890",
            "snils": "12345678901",
            "address": "Москва",
        }
        redis.get = AsyncMock(return_value=json.dumps(cached))
        result = await get_employee(session, redis, repo_cls.return_value, 1, 1)
        assert result is not None
        assert result.id == 1
        assert result.company_id == 1
        assert result.first_name == "Иван"
        repo_cls.return_value.get_by_id.assert_not_awaited()

    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_get_employee_from_cache_wrong_company_raises_404(self, repo_cls, session, redis):
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)
        cached = {
            "id": 1,
            "company_id": 2,
            "email": "e@e.ru",
            "phone_number": "+79991234567",
            "first_name": "Иван",
            "last_name": "Иванов",
            "middle_name": "И.",
            "position": "Директор",
            "salary": 100000.0,
            "status": "active",
            "hire_date": "2020-01-15",
            "passport_series": "1234",
            "passport_number": "567890",
            "passport_issued_date": "2015-05-20",
            "passport_issued_place": "ОВД",
            "passport_issued_code": "770",
            "inn": "1234567890",
            "snils": "12345678901",
            "address": "Москва",
        }
        redis.get = AsyncMock(return_value=json.dumps(cached))
        with pytest.raises(NotFoundError) as exc_info:
            await get_employee(session, redis, repo_cls.return_value, 1, 1)
        assert "not found" in exc_info.value.detail.lower() or "owner" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_get_employee_from_db_and_caches(self, repo_cls, session, redis):
        redis.get = AsyncMock(return_value=None)
        employee_in_db = _mock_employee(employee_id=1, company_id=1)
        repo_cls.return_value.get_by_id = AsyncMock(return_value=employee_in_db)
        result = await get_employee(session, redis, repo_cls.return_value, 1, 1)
        assert result is not None
        assert result.id == 1
        assert result.company_id == 1
        redis.set.assert_awaited_once()
        assert redis.set.await_args[0][0] == "employee_1"

    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_get_employee_not_found_raises_404(self, repo_cls, session, redis):
        redis.get = AsyncMock(return_value=None)
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundError) as exc_info:
            await get_employee(session, redis, repo_cls.return_value, 999, 1)
        assert "not found" in exc_info.value.detail.lower() or "owner" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_get_employee_wrong_company_raises_404(self, repo_cls, session, redis):
        redis.get = AsyncMock(return_value=None)
        employee_other_company = _mock_employee(employee_id=1, company_id=2)
        repo_cls.return_value.get_by_id = AsyncMock(return_value=employee_other_company)
        with pytest.raises(NotFoundError) as exc_info:
            await get_employee(session, redis, repo_cls.return_value, 1, 1)
        assert "not found" in exc_info.value.detail.lower() or "owner" in exc_info.value.detail.lower()


class TestUpdateEmployee:
    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_update_employee_success(self, repo_cls, session, redis):
        old_employee = _mock_employee(employee_id=1, company_id=1)
        updated_employee = _mock_employee(employee_id=1, company_id=1)
        updated_employee.first_name = "Пётр"
        repo_cls.return_value.get_by_id = AsyncMock(return_value=old_employee)
        repo_cls.return_value.update = AsyncMock(return_value=updated_employee)
        data = EmployeeUpdate(first_name="Пётр")
        result = await update_employee(session, redis, repo_cls.return_value, 1, data, 1)
        assert result is not None
        assert result.first_name == "Пётр"
        redis.set.assert_awaited_once()
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_update_employee_not_found_raises_404(self, repo_cls, session, redis):
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)
        data = EmployeeUpdate(first_name="Пётр")
        with pytest.raises(NotFoundError) as exc_info:
            await update_employee(session, redis, repo_cls.return_value, 999, data, 1)
        assert "not found" in exc_info.value.detail.lower() or "owner" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_update_employee_wrong_company_raises_404(self, repo_cls, session, redis):
        employee_other_company = _mock_employee(employee_id=1, company_id=2)
        repo_cls.return_value.get_by_id = AsyncMock(return_value=employee_other_company)
        data = EmployeeUpdate(first_name="Пётр")
        with pytest.raises(NotFoundError) as exc_info:
            await update_employee(session, redis, repo_cls.return_value, 1, data, 1)
        assert "not found" in exc_info.value.detail.lower() or "owner" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_update_employee_partial(self, repo_cls, session, redis):
        old_employee = _mock_employee(employee_id=1, company_id=1)
        updated_employee = _mock_employee(employee_id=1, company_id=1)
        updated_employee.salary = Decimal("60000.00")
        repo_cls.return_value.get_by_id = AsyncMock(return_value=old_employee)
        repo_cls.return_value.update = AsyncMock(return_value=updated_employee)
        data = EmployeeUpdate(salary=Decimal("60000.00"))
        result = await update_employee(session, redis, repo_cls.return_value, 1, data, 1)
        assert result.salary == Decimal("60000.00")
        repo_cls.return_value.update.assert_awaited_once()


class TestDismissEmployees:
    @pytest.fixture
    def redis_with_delete(self, redis):
        redis.delete = AsyncMock()
        return redis

    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_dismiss_one_employee_success(self, repo_cls, session, redis_with_delete):
        emp = _mock_employee(employee_id=1, company_id=1)
        repo_cls.return_value.get_by_id = AsyncMock(return_value=emp)
        repo_cls.return_value.delete = AsyncMock()
        result = await dismiss_employees(session, redis_with_delete, repo_cls.return_value, [1], 1)
        assert result["message"] == "Employees dismissed successfully"
        repo_cls.return_value.get_by_id.assert_awaited_once_with(session, 1)
        repo_cls.return_value.delete.assert_awaited_once_with(session, emp)
        redis_with_delete.delete.assert_awaited_once_with("employee_1")
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_dismiss_multiple_employees_success(self, repo_cls, session, redis_with_delete):
        emp1 = _mock_employee(employee_id=1, company_id=1)
        emp2 = _mock_employee(employee_id=2, company_id=1)
        repo_cls.return_value.get_by_id = AsyncMock(side_effect=[emp1, emp2])
        repo_cls.return_value.delete = AsyncMock()
        result = await dismiss_employees(session, redis_with_delete, repo_cls.return_value, [1, 2], 1)
        assert result["message"] == "Employees dismissed successfully"
        assert repo_cls.return_value.get_by_id.await_count == 2
        assert repo_cls.return_value.delete.await_count == 2
        assert redis_with_delete.delete.await_count == 2
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_dismiss_employee_not_found_raises_404(self, repo_cls, session, redis_with_delete):
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)
        repo_cls.return_value.delete = AsyncMock()
        with pytest.raises(NotFoundError) as exc_info:
            await dismiss_employees(session, redis_with_delete, repo_cls.return_value, [999], 1)
        assert "not found" in exc_info.value.detail.lower() or "owner" in exc_info.value.detail.lower()
        assert repo_cls.return_value.delete.await_count == 0

    @pytest.mark.asyncio
    @patch("app.services.EmployeeService.EmployeeRepository")
    async def test_dismiss_employee_wrong_company_raises_404(self, repo_cls, session, redis_with_delete):
        emp_other = _mock_employee(employee_id=1, company_id=2)
        repo_cls.return_value.get_by_id = AsyncMock(return_value=emp_other)
        repo_cls.return_value.delete = AsyncMock()
        with pytest.raises(NotFoundError):
            await dismiss_employees(session, redis_with_delete, repo_cls.return_value, [1], 1)
        assert repo_cls.return_value.delete.await_count == 0
