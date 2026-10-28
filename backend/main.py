"""
Proxy de compatibilité pour le point d'entrée de l'application.
Permet de lancer ou d'importer l'application directement depuis la racine du dossier backend.
"""
from app.main import app

__all__ = ["app"]
