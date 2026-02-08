from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.Base import Base


class User(Base):
    __tablename__ = 'users'
    
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)

    companies: Mapped[list['Company']] = relationship('Company', back_populates='owner')