"""
Catalog / reference tables: Municipality, Address.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from geoalchemy2 import Geometry
from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.auth import AppUser  # noqa: F401
    from app.models.business import Client  # noqa: F401
    from app.models.incidents import (
        Hospital,
        Incident,
        TowProvider,
        TowService,
        Workshop,
    )


class Municipality(Base):
    __tablename__ = "municipality"
    __table_args__ = (
        UniqueConstraint("name", name="uq_municipality_name"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_name: Mapped[str] = mapped_column(String(50), nullable=False)
    siga_code: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    addresses: Mapped[list[Address]] = relationship(back_populates="municipality")


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    street: Mapped[str] = mapped_column(String(150), nullable=False)
    exterior_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    interior_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    cross_street_1: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cross_street_2: Mapped[str | None] = mapped_column(String(100), nullable=True)
    neighborhood: Mapped[str | None] = mapped_column(String(100), nullable=True)
    municipality_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("municipality.id"), nullable=True
    )
    postal_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    geom = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    municipality: Mapped[Municipality | None] = relationship(back_populates="addresses")
    clients: Mapped[list[Client]] = relationship(back_populates="address")
    incidents_origin: Mapped[list[Incident]] = relationship(
        back_populates="origin_address",
        foreign_keys="[Incident.origin_address_id]",
    )
    tow_services_origin: Mapped[list[TowService]] = relationship(
        back_populates="origin_address",
        foreign_keys="[TowService.origin_address_id]",
    )
    tow_services_destination: Mapped[list[TowService]] = relationship(
        back_populates="destination_address",
        foreign_keys="[TowService.destination_address_id]",
    )
    hospitals: Mapped[list[Hospital]] = relationship(back_populates="address")
    workshops: Mapped[list[Workshop]] = relationship(back_populates="address")
    tow_providers: Mapped[list[TowProvider]] = relationship(back_populates="address")
