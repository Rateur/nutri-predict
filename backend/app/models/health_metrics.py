import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class HealthMetrics(Base):
    __tablename__ = "health_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    
    # Données biométriques chiffrées (AES-256 / Fernet)
    height_encrypted: Mapped[str] = mapped_column(String, nullable=False)
    weight_encrypted: Mapped[str] = mapped_column(String, nullable=False)
    
    # Métabolisme de base (formule de Mifflin-St Jeor)
    basal_metabolic_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Horodatage délégué à PostgreSQL
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relation vers l'utilisateur
    user: Mapped["User"] = relationship("User", back_populates="health_metrics")
