"""
Proxy de compatibilité pour le routeur de prédiction.
Permet d'importer le routeur directement depuis la racine du dossier backend si requis.
"""
from app.api.endpoints.predict import router, get_ml_service

__all__ = ["router", "get_ml_service"]
