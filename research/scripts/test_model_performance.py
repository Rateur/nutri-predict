import os
import joblib
import pandas as pd
import pytest
from sklearn.metrics import mean_absolute_error, r2_score

def test_model_performance():
    # Chemins absolus
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    model_path = os.path.join(base_dir, 'backend', 'nutri_predict_rf_model.joblib')
    test_data_path = os.path.join(base_dir, 'research', 'data', 'processed', 'ml_test_dataset.parquet')
    
    assert os.path.exists(model_path), f"Le modèle {model_path} est introuvable."
    assert os.path.exists(test_data_path), f"Le dataset de test {test_data_path} est introuvable."
    
    # Chargement
    model = joblib.load(model_path)
    df_test = pd.read_parquet(test_data_path)
    
    # Définition des features et target (basé sur le feature engineering)
    # Les features attendues par le RandomForest (identique au payload API) :
    # user_bmr, biscuit_calories_100g, portion_g
    target_col = 'weight_delta_grams'
    
    # Vérification que les colonnes existent
    features = ['user_bmr', 'biscuit_calories_100g', 'portion_g']
    for col in features + [target_col]:
        assert col in df_test.columns, f"La colonne {col} est manquante dans le test dataset."
        
    X_test = df_test[features]
    y_test = df_test[target_col]
    
    # Inférence
    y_pred = model.predict(X_test)
    
    # Calcul des métriques
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\nRésultats du modèle sur le Test Set :")
    print(f"MAE : {mae:.4f}")
    print(f"R²  : {r2:.4f}")
    
    # Assertions strictes d'acceptation RNCP
    assert mae < 5.0, f"MAE trop élevée : {mae:.2f} (Attendu < 5.0)"
    assert r2 > 0.95, f"R² trop faible : {r2:.4f} (Attendu > 0.95)"
