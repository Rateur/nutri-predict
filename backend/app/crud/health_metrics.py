import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health_metrics import HealthMetrics
from app.schemas.health_metrics import HealthMetricsCreate
from app.core.security import encrypt_health_data


async def create_health_metrics(
    db: AsyncSession, *, obj_in: HealthMetricsCreate, user_id: uuid.UUID
) -> HealthMetrics:
    """
    Crée une nouvelle entrée de métriques de santé après chiffrement 
    des données biométriques (AES-256-GCM).
    """
    # Chiffrement STRICT au niveau CRUD avant création de l'objet ORM
    height_encrypted = encrypt_health_data(str(obj_in.height))
    weight_encrypted = encrypt_health_data(str(obj_in.weight))

    db_obj = HealthMetrics(
        user_id=user_id,
        height_encrypted=height_encrypted,
        weight_encrypted=weight_encrypted,
        basal_metabolic_rate=obj_in.basal_metabolic_rate,
    )
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_latest_health_metrics_by_user(
    db: AsyncSession, user_id: uuid.UUID
) -> Optional[HealthMetrics]:
    """
    Récupère la mesure la plus récente pour un utilisateur donné.
    """
    query = (
        select(HealthMetrics)
        .where(HealthMetrics.user_id == user_id)
        .order_by(HealthMetrics.recorded_at.desc())
        .limit(1)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()
