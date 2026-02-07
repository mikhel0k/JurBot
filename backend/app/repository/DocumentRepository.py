from app.models.Document import Document
from app.repository.BaseRepository import BaseRepository


class DocumentRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(Document)