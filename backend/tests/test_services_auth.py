import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.schemas import UserCreate, Confirm, Login
from app.services.AuthService import (
    register,
    confirm_registration,
    login,
    confirm_login,
)


def _user_create():
    return UserCreate(
        email="user@example.com",
        phone_number="+79991234567",
        full_name="Иван Иванов",
        password="secret123",
    )


def _mock_user_in_db():
    u = MagicMock()
    u.id = 1
    u.email = "user@example.com"
    u.phone_number = "+79991234567"
    u.full_name = "Иван Иванов"
    u.password_hash = "$2b$12$dummy_hash"
    return u


@pytest.fixture
def session():
    s = AsyncMock()
    s.commit = AsyncMock()
    return s


@pytest.fixture
def redis():
    r = AsyncMock()
    r.exists = AsyncMock(return_value=False)
    r.get = AsyncMock(return_value=None)
    r.set = AsyncMock()
    r.delete = AsyncMock()
    return r


class TestRegister:
    @pytest.mark.asyncio
    @patch("app.services.AuthService.send_code_email_gmail")
    @patch("app.services.AuthService.UserRepository")
    async def test_register_success_returns_jti(self, repo_cls, send_mail, session, redis):
        repo_cls.return_value.get_by_email = AsyncMock(return_value=None)
        repo_cls.return_value.get_by_phone_number = AsyncMock(return_value=None)
        send_mail_sync = MagicMock()
        with patch("app.services.AuthService.asyncio.to_thread", new_callable=AsyncMock) as to_thread:
            to_thread.return_value = None
            jti = await register(session, redis, _user_create())
        assert jti is not None
        assert redis.set.await_count >= 3
        to_thread.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("app.services.AuthService.UserRepository")
    async def test_register_fails_if_email_in_redis(self, repo_cls, session, redis):
        redis.exists = AsyncMock(return_value=True)
        with pytest.raises(HTTPException) as exc_info:
            await register(session, redis, _user_create())
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    @patch("app.services.AuthService.UserRepository")
    async def test_register_fails_if_user_exists_in_db(self, repo_cls, session, redis):
        repo_cls.return_value.get_by_email = AsyncMock(return_value=_mock_user_in_db())
        with pytest.raises(HTTPException) as exc_info:
            await register(session, redis, _user_create())
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail.lower()


class TestConfirmRegistration:
    @pytest.mark.asyncio
    @patch("app.services.AuthService.User")
    @patch("app.services.AuthService.UserRepository")
    @patch("app.services.AuthService.create_token")
    async def test_confirm_registration_returns_tokens(self, create_token, repo_cls, mock_user_cls, session, redis):
        mock_user_cls.return_value = MagicMock()
        user_data = {
            "email": "user@example.com",
            "phone_number": "+79991234567",
            "full_name": "Иван Иванов",
            "password_hash": "hash",
        }
        redis.get = AsyncMock(return_value=json.dumps(user_data))
        created_user = _mock_user_in_db()
        repo_cls.return_value.create = AsyncMock(return_value=created_user)
        create_token.return_value = "fake_token"
        data = Confirm(jti="jti-123", code="123456")
        access, refresh = await confirm_registration(session, redis, data)
        assert access == "fake_token"
        assert refresh == "fake_token"
        session.commit.assert_awaited_once()
        assert redis.delete.await_count >= 1

    @pytest.mark.asyncio
    async def test_confirm_registration_invalid_code_raises_401(self, session, redis):
        redis.get = AsyncMock(return_value=None)
        data = Confirm(jti="jti-123", code="wrong")
        with pytest.raises(HTTPException) as exc_info:
            await confirm_registration(session, redis, data)
        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()


class TestLogin:
    @pytest.mark.asyncio
    @patch("app.services.AuthService.verify_password", return_value=True)
    @patch("app.services.AuthService.send_code_email_gmail")
    @patch("app.services.AuthService.UserRepository")
    async def test_login_success_returns_jti(self, repo_cls, send_mail, verify_pwd, session, redis):
        repo_cls.return_value.get_by_email = AsyncMock(return_value=_mock_user_in_db())
        with patch("app.services.AuthService.asyncio.to_thread", new_callable=AsyncMock) as to_thread:
            to_thread.return_value = None
            jti = await login(session, redis, Login(email="user@example.com", password="secret123"))
        assert jti is not None
        redis.set.assert_awaited_once()
        to_thread.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("app.services.AuthService.UserRepository")
    async def test_login_user_not_found_raises_401(self, repo_cls, session, redis):
        repo_cls.return_value.get_by_email = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc_info:
            await login(session, redis, Login(email="nobody@example.com", password="x"))
        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    @patch("app.services.AuthService.verify_password", return_value=False)
    @patch("app.services.AuthService.UserRepository")
    async def test_login_wrong_password_raises_401(self, repo_cls, verify_pwd, session, redis):
        repo_cls.return_value.get_by_email = AsyncMock(return_value=_mock_user_in_db())
        with pytest.raises(HTTPException) as exc_info:
            await login(session, redis, Login(email="user@example.com", password="wrong"))
        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()


class TestConfirmLogin:
    @pytest.mark.asyncio
    @patch("app.services.AuthService.CompanyRepository")
    @patch("app.services.AuthService.create_token")
    async def test_confirm_login_no_company_returns_message(self, create_token, repo_cls, session, redis):
        user_data = {"id": 1, "email": "u@u.ru", "phone_number": "+79991234567", "full_name": "User"}
        redis.get = AsyncMock(return_value=json.dumps(user_data))
        create_token.return_value = "fake_token"
        repo_cls.return_value.get_by_user_id = AsyncMock(return_value=None)
        data = Confirm(jti="jti", code="123456")
        access, refresh, message = await confirm_login(session, redis, data)
        assert access == "fake_token"
        assert refresh == "fake_token"
        assert "company" in message.lower() or "don't" in message.lower() or "do not" in message.lower()

    @pytest.mark.asyncio
    @patch("app.services.AuthService.CompanyRepository")
    @patch("app.services.AuthService.create_token")
    async def test_confirm_login_with_company_returns_success(self, create_token, repo_cls, session, redis):
        user_data = {"id": 1, "email": "u@u.ru", "phone_number": "+79991234567", "full_name": "User"}
        redis.get = AsyncMock(return_value=json.dumps(user_data))
        create_token.return_value = "fake_token"
        company = MagicMock()
        company.id = 10
        company.owner_id = 1
        company.name = "ООО"
        company.inn = "7707083893"
        company.snils = "12345678901"
        company.address = "Москва"
        repo_cls.return_value.get_by_user_id = AsyncMock(return_value=company)
        data = Confirm(jti="jti", code="123456")
        access, refresh, message = await confirm_login(session, redis, data)
        assert message == "success"
        redis.set.assert_awaited()

    @pytest.mark.asyncio
    async def test_confirm_login_invalid_code_raises_401(self, session, redis):
        redis.get = AsyncMock(return_value=None)
        data = Confirm(jti="jti", code="wrong")
        with pytest.raises(HTTPException) as exc_info:
            await confirm_login(session, redis, data)
        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()
