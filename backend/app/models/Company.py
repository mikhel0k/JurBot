from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.Base import Base


class Company(Base):
    __tablename__ = 'companies'

    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    inn: Mapped[str] = mapped_column(String(12), nullable=False)
    snils: Mapped[str] = mapped_column(String(11), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)

    owner: Mapped['User'] = relationship('User', back_populates='companies')
