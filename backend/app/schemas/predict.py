from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    """
    Schéma de validation pour la requête de prédiction de poids.
    Valide les données biométriques et nutritionnelles saisies par l'utilisateur.
    """
    user_bmr: float = Field(
        ...,
        gt=0.0,
        le=5000.0,
        description="Métabolisme de base de l'utilisateur en kcal, calculé via Mifflin-St Jeor.",
        examples=[1800.5]
    )
    biscuit_calories_100g: float = Field(
        ...,
        gt=0.0,
        le=900.0,
        description="Valeur énergétique du biscuit pour 100g en kcal. Ne peut dépasser la densité calorique maximale.",
        examples=[450.0]
    )
    portion_g: float = Field(
        ...,
        gt=0.0,
        le=1000.0,
        description="Portion consommée en grammes.",
        examples=[30.0]
    )

class PredictionResponse(BaseModel):
    """
    Schéma de validation pour la réponse de prédiction de poids.
    Retourne la variation de poids estimée en grammes.
    """
    predicted_weight_delta_grams: float = Field(
        ...,
        description="Variation pondérale estimée en grammes (peut être positive ou négative).",
        examples=[15.2]
    )
