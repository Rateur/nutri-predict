import secrets
import logging
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

logger = logging.getLogger(__name__)

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Vérifie la validité de la clé d'API statique passée en entête.
    Utilise secrets.compare_digest pour se prémunir contre les attaques temporelles (timing attacks).
    """
    if not api_key:
        logger.warning("[Security] Tentative d'accès sans clé d'API.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé d'API manquante."
        )

    config_api_key = settings.API_KEY
    if not config_api_key:
        logger.error("[Security] Erreur: API_KEY n'est pas configurée dans les variables d'environnement.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur de configuration interne du serveur."
        )
        
    if not secrets.compare_digest(api_key, config_api_key):
        logger.warning("[Security] Tentative d'accès avec une clé d'API invalide.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé d'API invalide ou non autorisée."
        )
    return api_key
