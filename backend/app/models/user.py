from sqlalchemy import ForeignKey, String, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional

from .base import Base, TimestampMixin

class AppUser(Base, TimestampMixin):
    """
    Usuarios de la aplicación móvil y web.
    Relacionado 1:1 con un Empleado.
    """
    
    __tablename__ = "app_user"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id"), unique=True)
    
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[Optional[datetime]]
    
    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="user")
    
    __all__ = ["AppUser"]
    
    __table_args__ = (
        Index("idx_app_user_employee", "employee_id"),
    )
