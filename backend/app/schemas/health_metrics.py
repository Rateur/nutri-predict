import uuid
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict, model_validator
from app.core.security import decrypt_health_data

class HealthMetricsBase(BaseModel):
    basal_metabolic_rate: Optional[float] = None

class HealthMetricsCreate(HealthMetricsBase):
    weight: float
    height: float

class HealthMetricsResponse(HealthMetricsBase):
    id: uuid.UUID
    user_id: uuid.UUID
    recorded_at: datetime
    weight: float
    height: float

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def decrypt_biometrics(cls, data: Any) -> Any:
        """
        Décodage automatique des champs cryptés lors de la lecture.
        """
        # Si data est une instance ORM
        if hasattr(data, 'weight_encrypted') and hasattr(data, 'height_encrypted'):
            # Injection dynamique des valeurs déchiffrées pour le schéma
            data.weight = float(decrypt_health_data(data.weight_encrypted))
            data.height = float(decrypt_health_data(data.height_encrypted))
        # Si data est un dictionnaire
        elif isinstance(data, dict) and 'weight_encrypted' in data and 'height_encrypted' in data:
            data['weight'] = float(decrypt_health_data(data['weight_encrypted']))
            data['height'] = float(decrypt_health_data(data['height_encrypted']))
        return data
