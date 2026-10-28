import pandas as pd
import duckdb
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

print("1. Chargement du dataset...")
df_ml = duckdb.query("SELECT * FROM 'research/data/processed/ml_training_dataset.parquet'").to_df()
print(f"Dataset chargé: {df_ml.shape}")

print("2. Préparation des données...")
X = df_ml[['user_bmr', 'biscuit_calories_100g', 'portion_g']]
y = df_ml['weight_delta_grams']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("3. Entraînement du modèle (n_jobs=1 pour éviter le crash)...")
model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=1)
model.fit(X_train, y_train)

print("4. Évaluation...")
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
print(f"R2 = {r2:.4f}, MAE = {mae:.2f} g")

print("5. Exportation...")
output_path = 'research/models/nutri_predict_rf_model.joblib'
joblib.dump(model, output_path)
print(f"Modèle ré-exporté avec succès: {output_path}")

print("6. Test de chargement...")
loaded = joblib.load(output_path)
test_pred = loaded.predict(pd.DataFrame([{'user_bmr': 1800.0, 'biscuit_calories_100g': 470.0, 'portion_g': 30.0}]))
print(f"Prédiction de test: {test_pred[0]:.2f} g")
