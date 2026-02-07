from app.models.Employee import Employee
from app.repository.BaseRepository import BaseRepository


class EmployeeRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(Employee)