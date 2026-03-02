from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Date, BigInteger, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class Municipality(Base):
    __tablename__ = "municipality"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    short_name: Mapped[str] = mapped_column(String(50))
    siga_code: Mapped[Optional[str]] = mapped_column(String(100))


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    street: Mapped[str] = mapped_column(String(150))
    exterior_number: Mapped[Optional[str]] = mapped_column(String(10))
    interior_number: Mapped[Optional[str]] = mapped_column(String(10))
    cross_street_1: Mapped[Optional[str]] = mapped_column(String(100))
    cross_street_2: Mapped[Optional[str]] = mapped_column(String(100))
    neighborhood: Mapped[Optional[str]] = mapped_column(String(100))
    municipality_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("municipality.id"))
    postal_code: Mapped[Optional[str]] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    municipality: Mapped[Optional["Municipality"]] = relationship(lazy="joined")


class Client(Base, TimestampMixin):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    paternal_surname: Mapped[str] = mapped_column(String(50))
    maternal_surname: Mapped[Optional[str]] = mapped_column(String(50))
    rfc: Mapped[Optional[str]] = mapped_column(String(13))
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    address_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("address.id"))
    phone_1: Mapped[Optional[str]] = mapped_column(String(20))
    phone_2: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    address: Mapped[Optional["Address"]] = relationship(lazy="joined")

    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.paternal_surname]
        if self.maternal_surname:
            parts.append(self.maternal_surname)
        return " ".join(parts)

    @property
    def full_address(self) -> str:
        if not self.address:
            return ""
        a = self.address
        parts = [a.street]
        if a.exterior_number:
            parts.append(f"#{a.exterior_number}")
        if a.neighborhood:
            parts.append(f", {a.neighborhood}")
        if a.municipality:
            parts.append(f", {a.municipality.short_name}")
        return " ".join(parts)
