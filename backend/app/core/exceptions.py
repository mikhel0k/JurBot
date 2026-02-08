"""Кастомные исключения приложения. Конвертируются в HTTP-ответы через exception handler в main.py."""


class AppException(Exception):
    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail
        super().__init__(self.detail)


class NotFoundError(AppException):
    status_code = 404
    detail = "Not found"


class AlreadyExistsError(AppException):
    status_code = 400
    detail = "Already exists"


class UnauthorizedError(AppException):
    status_code = 401
    detail = "Unauthorized"


class InvalidCodeError(AppException):
    status_code = 401
    detail = "Invalid code"
