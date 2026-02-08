from datetime import date
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.Base import Base



class Employee(Base):
    __tablename__ = 'employees'

    company_id: Mapped[int] = mapped_column(Integer, ForeignKey('companies.id'), nullable=False)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    position: Mapped[str] = mapped_column(String(150), nullable=False)
    salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(150), nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    passport_series: Mapped[str] = mapped_column(String(10), nullable=False)
    passport_number: Mapped[str] = mapped_column(String(10), nullable=False)
    passport_issued_date: Mapped[date] = mapped_column(Date, nullable=False)
    passport_issued_place: Mapped[str] = mapped_column(String(255), nullable=False)
    passport_issued_code: Mapped[str] = mapped_column(String(10), nullable=False)
    inn: Mapped[str] = mapped_column(String(12), nullable=False)
    snils: Mapped[str] = mapped_column(String(11), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)

    company: Mapped['Company'] = relationship('Company', back_populates='employees')
    documents: Mapped[list['Document']] = relationship('Document', back_populates='employee')