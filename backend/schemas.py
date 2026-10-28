"""
Proxy de compatibilité pour les schémas de prédiction.
Permet d'importer directement depuis la racine du dossier backend si requis.
"""
from app.schemas.predict import PredictionRequest, PredictionResponse

__all__ = ["PredictionRequest", "PredictionResponse"]
