"""
Proxy de compatibilité pour le service de Machine Learning.
Permet d'importer directement depuis la racine du dossier backend si requis.
"""
from app.services.ml_service import MLService

__all__ = ["MLService"]
