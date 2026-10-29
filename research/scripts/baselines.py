"""
Points de repère du R² de Nutri-Predict, sur le même découpage que le notebook 02.

Le notebook découpe les 5000 cas simulés en 80/20 (random_state=42). Ce découpage a
ensuite été figé par generate_test_split.py : ml_training_dataset.parquet contient
les 4000 cas d'entraînement, ml_test_dataset.parquet les 1000 cas de test.
On relit donc ces deux fichiers, sans redécouper.

Lancer depuis la racine du dépôt : python research/scripts/baselines.py
"""
import os

import duckdb
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")
FEATURES = ["user_bmr", "biscuit_calories_100g", "portion_g"]  # comme dans le notebook
TARGET = "weight_delta_grams"


def charger(nom):
    return duckdb.query(f"SELECT * FROM '{os.path.join(DATA_DIR, nom)}'").to_df()


train = charger("ml_training_dataset.parquet")
test = charger("ml_test_dataset.parquet")
assert (len(train), len(test)) == (4000, 1000), "découpage inattendu : 4000 / 1000 attendus"

X_train, y_train = train[FEATURES], train[TARGET]
X_test, y_test = test[FEATURES], test[TARGET]

# 1. Régression linéaire : le point de comparaison simple.
lineaire = LinearRegression().fit(X_train, y_train)
print(f"Regression lineaire     R2 = {r2_score(y_test, lineaire.predict(X_test)):.4f}")

# 2. Plafond dû au bruit. La cible vaut balance_calorique / 7.7 + un bruit gaussien
# (moyenne 0, écart-type 2 g), cf. notebook 01. Ce bruit est imprévisible : le meilleur
# modèle possible est la formule sans bruit. Son R2 sur le test est le maximum atteignable.
formule = test["balance_calorique"] / 7.7
print(f"Maximum possible (bruit) R2 = {r2_score(y_test, formule):.4f}")

# 3. RandomForest, mêmes réglages que le notebook (100 arbres) et que le run 1 MLflow (50 arbres).
for n_arbres in (100, 50):
    foret = RandomForestRegressor(n_estimators=n_arbres, random_state=42, n_jobs=-1).fit(X_train, y_train)
    print(f"RandomForest {n_arbres:>3} arbres   R2 = {r2_score(y_test, foret.predict(X_test)):.4f}")
