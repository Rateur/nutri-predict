import pytest
from fastapi.testclient import TestClient
from typing import Optional

# Imports demandés par les contraintes
from app.main import app
from app.api.endpoints.products import get_product_service
from app.schemas.product import ProductResponse

# 1. Création du MockProductService
class MockProductService:
    def get_product_by_barcode(self, barcode: str) -> Optional[ProductResponse]:
        """
        Mock de la logique de service. 
        Évite l'accès au fichier Parquet réel.
        """
        if barcode == "9999999999999":
            return None
        
        if barcode == "3017620422003":
            # Simulation d'un produit valide existant dans le dataset fictif
            return ProductResponse(
                code="3017620422003",
                product_name="Pâte à tartiner Nutella 400g",
                energy_kcal_100g=539.0,
                sugars_100g=56.3
            )
        
        return None

# 2. Application de l'override de dépendance avant l'initialisation du client
# Cela garantit que toute requête passant par FastAPI utilisera le Mock au lieu du vrai service.
app.dependency_overrides[get_product_service] = lambda: MockProductService()

from app.core.config import settings
client = TestClient(app)
headers = {"X-API-KEY": settings.API_KEY}

def test_read_product_unauthorized():
    """Vérifie qu'une requête sans clé d'API ou avec une clé invalide est rejetée avec un code 403."""
    # Sans clé
    response = client.get("/api/v1/products/3017620422003")
    assert response.status_code == 403
    
    # Avec clé invalide
    response = client.get("/api/v1/products/3017620422003", headers={"X-API-KEY": "wrong_key"})
    assert response.status_code == 403

def test_read_product_not_found():
    """Vérifie que l'API retourne 404 pour un produit inexistant via le mock."""
    response = client.get("/api/v1/products/9999999999999", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Produit introuvable dans le dataset OpenFoodFacts France."

def test_read_product_exists():
    """Vérifie que l'API peut lire un produit simulé via le service mocké."""
    barcode = "3017620422003"
    response = client.get(f"/api/v1/products/{barcode}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["code"] == barcode
    assert data["product_name"] == "Pâte à tartiner Nutella 400g"
    assert data["energy_kcal_100g"] == 539.0
    assert data["sugars_100g"] == 56.3

def test_read_product_internal_error_handling():
    """Optionnel : Vérifie que le schéma de réponse est bien respecté."""
    barcode = "3017620422003"
    response = client.get(f"/api/v1/products/{barcode}", headers=headers)
    
    # Validation Pydantic automatique par FastAPI via le response_model ProductResponse
    assert "code" in response.json()
    assert "product_name" in response.json()

