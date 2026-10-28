import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.endpoints.predict import get_ml_service
from app.schemas.predict import PredictionResponse
from app.core.config import settings

# 1. Création d'un mock robuste pour MLService
class MockMLService:
    def predict_weight(self, request):
        # Simuler un crash interne si le métabolisme de base vaut 999.0
        if request.user_bmr == 999.0:
            raise ValueError("Simulation d'un plantage interne du modèle de régression.")
            
        # Simulation d'un calcul déterministe simple pour le succès du test
        # Exemple: 10% des calories de la portion
        calories_portion = (request.biscuit_calories_100g / 100.0) * request.portion_g
        simulated_delta = calories_portion * 0.1
        return PredictionResponse(predicted_weight_delta_grams=round(simulated_delta, 2))

# 2. Application de l'override de dépendance pour la suite de tests
app.dependency_overrides[get_ml_service] = lambda: MockMLService()

client = TestClient(app)
headers = {"X-API-KEY": settings.API_KEY}

def test_predict_unauthorized():
    """
    Vérifie qu'une requête sans clé d'API ou avec une clé invalide est rejetée avec un code HTTP 403.
    """
    payload = {
        "user_bmr": 1800.0,
        "biscuit_calories_100g": 450.0,
        "portion_g": 30.0
    }
    # Sans clé
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 403
    
    # Avec clé invalide
    response = client.post("/api/v1/predict", json=payload, headers={"X-API-KEY": "wrong_key"})
    assert response.status_code == 403

def test_predict_success():
    """
    Vérifie qu'une requête d'inférence avec des paramètres valides
    retourne un code HTTP 200 et la variation pondérale attendue.
    """
    payload = {
        "user_bmr": 1800.0,
        "biscuit_calories_100g": 450.0,
        "portion_g": 30.0
    }
    response = client.post("/api/v1/predict", json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "predicted_weight_delta_grams" in data
    # Pour 450 kcal/100g et portion 30g, calories = 135 kcal. simulated_delta = 13.5
    assert data["predicted_weight_delta_grams"] == 13.5  # (135 * 0.1) -> 13.5

def test_predict_validation_error_bmr():
    """
    Vérifie qu'un BMR utilisateur hors limites ou négatif est rejeté (HTTP 422).
    """
    payload = {
        "user_bmr": -50.0,  # Invalide: gt=0
        "biscuit_calories_100g": 450.0,
        "portion_g": 30.0
    }
    response = client.post("/api/v1/predict", json=payload, headers=headers)
    assert response.status_code == 422
    
    # BMR trop élevé (limite le=5000.0)
    payload_too_high = {
        "user_bmr": 6000.0,  # Invalide
        "biscuit_calories_100g": 450.0,
        "portion_g": 30.0
    }
    response = client.post("/api/v1/predict", json=payload_too_high, headers=headers)
    assert response.status_code == 422

def test_predict_validation_error_calories():
    """
    Vérifie qu'une valeur énergétique de biscuit hors limites est rejetée (HTTP 422).
    """
    payload = {
        "user_bmr": 1800.0,
        "biscuit_calories_100g": 1000.0,  # Invalide: le=900
        "portion_g": 30.0
    }
    response = client.post("/api/v1/predict", json=payload, headers=headers)
    assert response.status_code == 422

def test_predict_validation_error_portion():
    """
    Vérifie qu'une portion hors limites ou négative est rejetée (HTTP 422).
    """
    payload = {
        "user_bmr": 1800.0,
        "biscuit_calories_100g": 450.0,
        "portion_g": -5.0  # Invalide: gt=0
    }
    response = client.post("/api/v1/predict", json=payload, headers=headers)
    assert response.status_code == 422

def test_predict_internal_server_error():
    """
    Vérifie qu'un crash du service d'inférence (erreur levée par le modèle)
    est intercepté et se traduit par un code HTTP 500 propre et sans divulgation technique.
    """
    payload = {
        "user_bmr": 999.0,  # Déclenche la simulation d'exception dans le mock
        "biscuit_calories_100g": 450.0,
        "portion_g": 30.0
    }
    response = client.post("/api/v1/predict", json=payload, headers=headers)
    
    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "Une erreur interne est survenue lors du calcul de la prédiction."

def test_predict_rate_limiting():
    """
    Vérifie que slowapi rejette la 6ème requête d'inférence consécutive (dans la même minute)
    avec un code HTTP 429 (Too Many Requests).
    """
    payload = {
        "user_bmr": 1800.0,
        "biscuit_calories_100g": 450.0,
        "portion_g": 30.0
    }
    
    # Exécuter les requêtes dans la même minute
    # Comme slowapi est configuré à 5/minute pour predict_weight:
    # 5 requêtes doivent réussir (HTTP 200 ou 422/500 mais ici 200 car payload valide), et la 6ème doit renvoyer 429
    
    # On a déjà fait une requête réussie dans test_predict_success(), mais le test runner peut les exécuter dans le désordre.
    # Pour garantir le dépassement, on exécute 6 requêtes consécutives dans ce test indépendant
    responses = []
    for _ in range(6):
        res = client.post("/api/v1/predict", json=payload, headers=headers)
        responses.append(res.status_code)
    
    # Au moins l'une des requêtes (la dernière) doit avoir été bloquée avec un code 429
    assert 429 in responses

