from datetime import datetime, timedelta, timezone
import smtplib
from email.mime.text import MIMEText
from typing import Optional

import bcrypt
import jwt
from starlette.responses import Response

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

ACCESS_TOKEN_DURATION_MIN = 30
REFRESH_TOKEN_DURATION_MIN = 30 * 24 * 60
ACCESS_TOKEN_COOKIE_MAX_AGE = 30 * 60
REFRESH_TOKEN_COOKIE_MAX_AGE = 30 * 24 * 60 * 60

_jwt_private_key: Optional[str] = None
_jwt_public_key: Optional[str] = None


def _get_jwt_private_key() -> str:
    """Ленивая загрузка приватного ключа при первом использовании."""
    global _jwt_private_key
    if _jwt_private_key is None:
        if not settings.JWT_PRIVATE_KEY.exists():
            raise RuntimeError(
                f"JWT private key not found: {settings.JWT_PRIVATE_KEY}. "
                "Create jwt_tokens/ and add jwt-private.pem (see README)."
            )
        _jwt_private_key = settings.JWT_PRIVATE_KEY.read_text()
    return _jwt_private_key


def _get_jwt_public_key() -> str:
    """Ленивая загрузка публичного ключа при первом использовании."""
    global _jwt_public_key
    if _jwt_public_key is None:
        if not settings.JWT_PUBLIC_KEY.exists():
            raise RuntimeError(
                f"JWT public key not found: {settings.JWT_PUBLIC_KEY}. "
                "Create jwt_tokens/ and add jwt-public.pem (see README)."
            )
        _jwt_public_key = settings.JWT_PUBLIC_KEY.read_text()
    return _jwt_public_key


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_token(data_dict: dict, duration: int = 30) -> str:
    data = data_dict.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=duration)
    data.update({"exp": expire})
    return jwt.encode(data, _get_jwt_private_key(), algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, _get_jwt_public_key(), algorithms=[settings.ALGORITHM])


def set_token(response: Response, token: str, key: str, max_age: int, path: str = "/") -> None:
    """Выставляет cookie с токеном (httponly, secure в prod, samesite=lax)."""
    response.set_cookie(
        key=key,
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.SECURE_COOKIES,
        max_age=max_age,
        path=path,
    )


def clear_token(response: Response, key: str, path: str = "/") -> None:
    """Удаляет cookie с токеном."""
    response.delete_cookie(key=key, path=path, httponly=True, samesite="lax", secure=settings.SECURE_COOKIES)


def send_code_email_gmail(to_email: str, code: str) -> None:
    """Отправляет код на email. Если Gmail не настроен (dev/test), только логирует и не падает."""
    if not settings.SEND_LOGIN_CODE_EMAIL or not settings.LOGIN_FOR_GMAIL or not settings.PASSWORD_FOR_GMAIL:
        logger.warning(
            "Email not configured (SEND_LOGIN_CODE_EMAIL=%s, LOGIN_FOR_GMAIL set=%s); "
            "skipping send for %s",
            settings.SEND_LOGIN_CODE_EMAIL,
            bool(settings.LOGIN_FOR_GMAIL),
            to_email,
        )
        return
    msg = MIMEText(f"Ваш код подтверждения: {code}\nДействует 10 минут.", "plain", "utf-8")
    msg["Subject"] = "Код подтверждения"
    msg["From"] = settings.LOGIN_FOR_GMAIL
    msg["To"] = to_email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(settings.LOGIN_FOR_GMAIL, settings.PASSWORD_FOR_GMAIL)
        server.sendmail(settings.LOGIN_FOR_GMAIL, [to_email], msg.as_string())
    logger.info("Code email sent to %s", to_email) 
