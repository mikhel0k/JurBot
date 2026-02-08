import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.schemas import CompanyCreate, CompanyUpdate, CompanyResponse
from app.services.CompanyService import create_company, get_company, update_company


def _company_create():
    return CompanyCreate(
        name="ООО Рога и копыта",
        inn="7707083893",
        snils="12345678901",
        address="г. Москва, ул. Примерная, д. 1",
    )


def _mock_company(owner_id: int = 1, id: int = 1):
    c = MagicMock()
    c.id = id
    c.owner_id = owner_id
    c.name = "ООО Рога и копыта"
    c.inn = "7707083893"
    c.snils = "12345678901"
    c.address = "г. Москва, ул. Примерная, д. 1"
    return c


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def redis():
    r = AsyncMock()
    r.get = AsyncMock(return_value=None)
    r.set = AsyncMock()
    r.delete = AsyncMock()
    return r


class TestCreateCompany:
    @pytest.mark.asyncio
    @patch("app.services.CompanyService.Company")
    @patch("app.services.CompanyService.CompanyRepository")
    async def test_create_company_success(self, repo_cls, mock_company_cls, session, redis):
        mock_company_cls.return_value = MagicMock()
        repo_cls.return_value.get_by_user_id = AsyncMock(return_value=None)
        created = _mock_company(owner_id=1, id=5)
        repo_cls.return_value.create = AsyncMock(return_value=created)
        result = await create_company(session, redis, _company_create(), user_id=1)
        assert result is not None
        assert result.id == 5
        assert result.owner_id == 1
        assert result.name == _company_create().name
        redis.set.assert_awaited_once()
        call_args = redis.set.await_args
        assert call_args[0][0] == "company_1"
        assert json.loads(call_args[0][1])["name"] == _company_create().name

    @pytest.mark.asyncio
    @patch("app.services.CompanyService.CompanyRepository")
    async def test_create_company_already_exists_raises_400(self, repo_cls, session, redis):
        repo_cls.return_value.get_by_user_id = AsyncMock(return_value=_mock_company())
        create_mock = AsyncMock()
        repo_cls.return_value.create = create_mock
        with pytest.raises(HTTPException) as exc_info:
            await create_company(session, redis, _company_create(), user_id=1)
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail.lower()
        assert create_mock.await_count == 0


class TestGetCompany:
    @pytest.mark.asyncio
    @patch("app.services.CompanyService.CompanyRepository")
    async def test_get_company_from_cache(self, repo_cls, session, redis):
        get_by_user_mock = AsyncMock()
        repo_cls.return_value.get_by_user_id = get_by_user_mock
        cached = {"id": 1, "owner_id": 1, "name": "ООО", "inn": "7707083893", "snils": "12345678901", "address": "Москва"}
        redis.get = AsyncMock(return_value=json.dumps(cached))
        result = await get_company(session, redis, user_id=1)
        assert result is not None
        assert result.name == "ООО"
        assert result.owner_id == 1
        assert get_by_user_mock.await_count == 0

    @pytest.mark.asyncio
    @patch("app.services.CompanyService.CompanyRepository")
    async def test_get_company_from_db_and_caches(self, repo_cls, session, redis):
        redis.get = AsyncMock(return_value=None)
        company = _mock_company()
        repo_cls.return_value.get_by_user_id = AsyncMock(return_value=company)
        result = await get_company(session, redis, user_id=1)
        assert result is not None
        assert result.name == company.name
        redis.set.assert_awaited_once()
        assert redis.set.await_args[0][0] == "company_1"

    @pytest.mark.asyncio
    @patch("app.services.CompanyService.CompanyRepository")
    async def test_get_company_not_found_raises_404(self, repo_cls, session, redis):
        redis.get = AsyncMock(return_value=None)
        repo_cls.return_value.get_by_user_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc_info:
            await get_company(session, redis, user_id=999)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()


class TestUpdateCompany:
    @pytest.mark.asyncio
    @patch("app.services.CompanyService.CompanyRepository")
    async def test_update_company_success(self, repo_cls, session, redis):
        old_company = _mock_company()
        old_company.name = "Старое имя"
        updated_company = _mock_company()
        updated_company.name = "Новое имя"
        repo_cls.return_value.get_by_user_id = AsyncMock(return_value=old_company)
        repo_cls.return_value.update = AsyncMock(return_value=updated_company)
        redis.get = AsyncMock(return_value="cached_data")
        data = CompanyUpdate(name="Новое имя")
        result = await update_company(session, redis, user_id=1, company_data=data)
        assert result is not None
        assert result.name == "Новое имя"
        redis.delete.assert_awaited_once()
        redis.set.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("app.services.CompanyService.CompanyRepository")
    async def test_update_company_partial(self, repo_cls, session, redis):
        old_company = _mock_company()
        updated_company = _mock_company()
        updated_company.address = "Новый адрес"
        repo_cls.return_value.get_by_user_id = AsyncMock(return_value=old_company)
        repo_cls.return_value.update = AsyncMock(return_value=updated_company)
        redis.get = AsyncMock(return_value=None)
        data = CompanyUpdate(address="Новый адрес")
        result = await update_company(session, redis, user_id=1, company_data=data)
        assert result.address == "Новый адрес"
        repo_cls.return_value.update.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("app.services.CompanyService.CompanyRepository")
    async def test_update_company_not_found_raises_404(self, repo_cls, session, redis):
        repo_cls.return_value.get_by_user_id = AsyncMock(return_value=None)
        update_mock = AsyncMock()
        repo_cls.return_value.update = update_mock
        data = CompanyUpdate(name="Любое")
        with pytest.raises(HTTPException) as exc_info:
            await update_company(session, redis, user_id=999, company_data=data)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
        assert update_mock.await_count == 0
