from app.models.User import User
from app.repository.BaseRepository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(User)
