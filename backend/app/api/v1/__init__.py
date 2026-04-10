# Реэкспорт модулей под именами в нижнем регистре (Linux чувствителен к регистру имён файлов)
from . import Auth
from . import Chat
from . import Company
from . import Employee

auth = Auth
chat = Chat
company = Company
employee = Employee

__all__ = ["auth", "chat", "company", "employee"]
