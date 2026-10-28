import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud import health_metrics as crud_health_metrics
from app.schemas.health_metrics import HealthMetricsCreate, HealthMetricsResponse

router = APIRouter()


@router.post("/", response_model=HealthMetricsResponse)
async def create_user_health_metrics(
    *,
    db: AsyncSession = Depends(get_db),
    metrics_in: HealthMetricsCreate,
    user_id: uuid.UUID # Dans une version finale, ce sera extrait du token JWT (get_current_user)
) -> Any:
    """
    Crée une nouvelle mesure de santé (poids, taille, BMR).
    Les données biométriques sont chiffrées avant stockage.
    """
    return await crud_health_metrics.create_health_metrics(
        db=db, obj_in=metrics_in, user_id=user_id
    )


@router.get("/latest", response_model=HealthMetricsResponse)
async def read_latest_user_health_metrics(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID
) -> Any:
    """
    Récupère la mesure la plus récente pour l'utilisateur.
    Le déchiffrement est opéré automatiquement par le validateur Pydantic.
    """
    metrics = await crud_health_metrics.get_latest_health_metrics_by_user(
        db=db, user_id=user_id
    )
    
    if not metrics:
        raise HTTPException(
            status_code=404,
            detail="Aucune donnée de santé trouvée pour cet utilisateur."
        )
        
    return metrics
