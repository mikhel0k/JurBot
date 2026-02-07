from app.models.Company import Company
from app.repository.BaseRepository import BaseRepository


class CompanyRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(Company)