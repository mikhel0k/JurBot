from datetime import date

from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.Base import Base


class Document(Base):
    __tablename__ = 'documents'

    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey('employees.id'), nullable=False)
    type: Mapped[str] = mapped_column(String(150), nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)
    