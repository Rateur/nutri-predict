from fastapi import APIRouter, HTTPException, Depends, Request
from app.schemas.predict import PredictionRequest, PredictionResponse
from app.services.ml_service import MLService
from app.core.auth import verify_api_key
from app.core.limiter import limiter
import structlog
from prometheus_client import Histogram
import time

logger = structlog.get_logger(__name__)

ml_inference_histogram = Histogram(
    "ml_weight_delta_grams",
    "Distribution of predicted weight delta in grams"
)
# Sécurisation du routeur avec l'authentification par clé d'API statique
router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])

def get_ml_service() -> MLService:
    """
    Dépendance pour obtenir l'instance de MLService.
    Facilite l'écriture des tests unitaires en permettant de mocker le service.
    """
    return MLService()

@router.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["prediction"],
    summary="Prédit la variation de poids de l'utilisateur.",
    description="Prend en compte le métabolisme de base (BMR), les calories du biscuit aux 100g, et la portion en grammes pour prédire la variation de poids."
)
@limiter.limit("5/minute")
def predict_weight(
    request: Request,
    payload: PredictionRequest,
    service: MLService = Depends(get_ml_service)
) -> PredictionResponse:
    """
    Endpoint POST pour exécuter l'inférence du modèle RandomForest.
    """
    logger.info("predict_weight_requested", user_bmr=payload.user_bmr, portion_g=payload.portion_g)
    try:
        start_time = time.time()
        result = service.predict_weight(payload)
        duration = time.time() - start_time
        
        # Enregistrement de la métrique
        ml_inference_histogram.observe(result.predicted_weight_delta_grams)
        
        logger.info("predict_weight_success", 
                    predicted_delta=result.predicted_weight_delta_grams,
                    duration_seconds=duration)
        return result
    except FileNotFoundError as e:
        logger.error("predict_weight_model_missing", error=str(e))
        # Erreur spécifique de fichier modèle manquant
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de configuration du serveur : le modèle prédictif est introuvable."
        )
    except Exception as e:
        logger.error("predict_weight_internal_error", error=str(e))
        # Capture de toute autre exception inattendue pour ne pas exposer de stack trace interne
        raise HTTPException(
            status_code=500,
            detail=f"Une erreur interne est survenue lors du calcul de la prédiction."
        )

