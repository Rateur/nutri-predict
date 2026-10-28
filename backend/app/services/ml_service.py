import os
import joblib
import pandas as pd
import logging
from app.schemas.predict import PredictionRequest, PredictionResponse

logger = logging.getLogger(__name__)


def _resolve_model_path() -> str | None:
    """
    Résout le chemin absolu vers le fichier joblib du modèle ML.
    Retourne le premier chemin valide trouvé, ou None si aucun n'existe.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))

    candidates = [
        # Chemin 1: Résolution absolue depuis l'emplacement du fichier source
        os.path.abspath(
            os.path.join(current_dir, "../../../research/models/nutri_predict_rf_model.joblib")
        ),
        # Chemin 2: Chemin relatif depuis le CWD (ex: backend/)
        os.path.abspath(
            os.path.join(os.getcwd(), "../research/models/nutri_predict_rf_model.joblib")
        ),
    ]

    for path in candidates:
        print(f"[MLService] Tentative de chargement du modèle: {path} (exists={os.path.exists(path)})")
        if os.path.exists(path):
            return path

    print(f"[MLService] ERREUR: Modèle introuvable dans aucun des chemins candidats.")
    return None


# Chargement singleton du modèle au niveau du module (une seule fois au démarrage ou au reload)
_MODEL = None
_model_path = _resolve_model_path()
if _model_path:
    try:
        _MODEL = joblib.load(_model_path)
        print(f"[MLService] Modèle ML chargé avec succès depuis : {_model_path}")
    except Exception as e:
        print(f"[MLService] Erreur lors de la désérialisation du modèle : {e}")
else:
    print("[MLService] ATTENTION: Le modèle ML n'a pas pu être chargé. L'endpoint /predict retournera une erreur 500.")


class MLService:
    """
    Service gérant l'inférence via le modèle Scikit-Learn pré-chargé.
    Le modèle est chargé au niveau du module (singleton) pour éviter un rechargement
    de 36 Mo à chaque requête HTTP.
    """

    def __init__(self) -> None:
        self.model = _MODEL

    def predict_weight(self, request: PredictionRequest) -> PredictionResponse:
        """
        Transforme la requête Pydantic en DataFrame pandas et effectue la prédiction.
        """
        if self.model is None:
            raise FileNotFoundError(
                "Le modèle de prédiction n'est pas disponible. "
                "Vérifiez que le fichier nutri_predict_rf_model.joblib est présent dans research/models/."
            )

        # Création du DataFrame avec le format exact requis par le modèle RandomForest
        input_df = pd.DataFrame([{
            "user_bmr": request.user_bmr,
            "biscuit_calories_100g": request.biscuit_calories_100g,
            "portion_g": request.portion_g
        }])

        # Inférence Scikit-Learn
        predictions = self.model.predict(input_df)
        predicted_value = float(predictions[0])

        return PredictionResponse(predicted_weight_delta_grams=predicted_value)
