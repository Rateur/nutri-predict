import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.health_metrics import HealthMetrics


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Horodatage délégué à PostgreSQL pour éviter les dérives entre conteneurs
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relation vers les métriques de santé (1-n)
    health_metrics: Mapped[List["HealthMetrics"]] = relationship(
        "HealthMetrics", back_populates="user", cascade="all, delete-orphan"
    )
