"""
Script MLflow + Generation de graphiques pour les rapports RNCP.
Lance une experience MLflow avec le modele NutriPredict
et genere les graphiques (learning curve, feature importance, residus).
"""
import os
import sys
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, learning_curve, GridSearchCV
from sklearn.metrics import mean_absolute_error, r2_score
import mlflow
import mlflow.sklearn

# ── Chemins ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "research", "data", "processed", "ml_training_dataset.parquet")
ASSETS_DIR = os.path.join(BASE_DIR, "docs", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# ── Style matplotlib pro ──
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': '#fafafa',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
})

# ── 1. Chargement des donnees ──
print("=" * 60)
print("  NutriPredict - Experimentation MLflow + Graphiques")
print("=" * 60)
print()
print("[1/6] Chargement du dataset...")
df = pd.read_parquet(DATA_PATH)
print(f"      {df.shape[0]} lignes, {df.shape[1]} colonnes")

X = df[['user_bmr', 'biscuit_calories_100g', 'portion_g']]
y = df['weight_delta_grams']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ── 2. Experience MLflow ──
print("[2/6] Lancement de l'experience MLflow...")
mlflow.set_tracking_uri(f"sqlite:///{os.path.join(BASE_DIR, 'mlruns.db')}")
mlflow.set_experiment("NutriPredict-RandomForest")

# Run 1 : Modele baseline (n_estimators=50)
with mlflow.start_run(run_name="RF_baseline_50trees"):
    model_50 = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
    model_50.fit(X_train, y_train)
    y_pred_50 = model_50.predict(X_test)
    r2_50 = r2_score(y_test, y_pred_50)
    mae_50 = mean_absolute_error(y_test, y_pred_50)

    mlflow.log_param("n_estimators", 50)
    mlflow.log_param("max_depth", "None")
    mlflow.log_param("random_state", 42)
    mlflow.log_metric("r2_score", r2_50)
    mlflow.log_metric("mae", mae_50)
    mlflow.log_metric("training_samples", len(X_train))
    mlflow.log_metric("test_samples", len(X_test))
    mlflow.sklearn.log_model(model_50, "model")
    print(f"      Run 1 (50 arbres)  : R2={r2_50:.4f}, MAE={mae_50:.2f}g")

# Run 2 : Modele optimise (n_estimators=100)
with mlflow.start_run(run_name="RF_optimized_100trees"):
    model_100 = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model_100.fit(X_train, y_train)
    y_pred_100 = model_100.predict(X_test)
    r2_100 = r2_score(y_test, y_pred_100)
    mae_100 = mean_absolute_error(y_test, y_pred_100)

    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", "None")
    mlflow.log_param("random_state", 42)
    mlflow.log_metric("r2_score", r2_100)
    mlflow.log_metric("mae", mae_100)
    mlflow.log_metric("training_samples", len(X_train))
    mlflow.log_metric("test_samples", len(X_test))
    mlflow.sklearn.log_model(model_100, "model")
    print(f"      Run 2 (100 arbres) : R2={r2_100:.4f}, MAE={mae_100:.2f}g")

# Run 3 : Modele avec profondeur limitee
with mlflow.start_run(run_name="RF_limited_depth_10"):
    model_d10 = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model_d10.fit(X_train, y_train)
    y_pred_d10 = model_d10.predict(X_test)
    r2_d10 = r2_score(y_test, y_pred_d10)
    mae_d10 = mean_absolute_error(y_test, y_pred_d10)

    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)
    mlflow.log_param("random_state", 42)
    mlflow.log_metric("r2_score", r2_d10)
    mlflow.log_metric("mae", mae_d10)
    mlflow.log_metric("training_samples", len(X_train))
    mlflow.log_metric("test_samples", len(X_test))
    mlflow.sklearn.log_model(model_d10, "model")
    print(f"      Run 3 (depth=10)   : R2={r2_d10:.4f}, MAE={mae_d10:.2f}g")

print("      MLflow : 3 runs enregistres avec succes.")

# ── 3. Learning Curve ──
print("[3/6] Generation de la Learning Curve...")
train_sizes, train_scores, test_scores = learning_curve(
    RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    X, y,
    train_sizes=np.linspace(0.1, 1.0, 10),
    cv=5,
    scoring='r2',
    n_jobs=-1
)

fig, ax = plt.subplots(figsize=(10, 6))
train_mean = train_scores.mean(axis=1)
train_std = train_scores.std(axis=1)
test_mean = test_scores.mean(axis=1)
test_std = test_scores.std(axis=1)

ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.15, color='#2B6CB0')
ax.fill_between(train_sizes, test_mean - test_std, test_mean + test_std, alpha=0.15, color='#E53E3E')
ax.plot(train_sizes, train_mean, 'o-', color='#2B6CB0', linewidth=2, label='Score Entrainement')
ax.plot(train_sizes, test_mean, 'o-', color='#E53E3E', linewidth=2, label='Score Validation (CV=5)')
ax.set_xlabel("Nombre d'echantillons d'entrainement")
ax.set_ylabel("Score R2")
ax.set_title("Learning Curve - RandomForestRegressor (NutriPredict)")
ax.legend(loc='lower right', fontsize=11)
ax.set_ylim(0.5, 1.05)
plt.tight_layout()
plt.savefig(os.path.join(ASSETS_DIR, "learning_curve.png"), dpi=150, bbox_inches='tight')
plt.close()
print("      learning_curve.png sauvegardee.")

# ── 4. Feature Importance ──
print("[4/6] Generation du graphique Feature Importance...")
importances = model_100.feature_importances_
feature_names = ['BMR Utilisateur', 'Calories Biscuit (100g)', 'Portion (g)']
indices = np.argsort(importances)[::-1]

fig, ax = plt.subplots(figsize=(8, 5))
colors = ['#2B6CB0', '#4299E1', '#63B3ED']
bars = ax.barh(
    [feature_names[i] for i in indices],
    [importances[i] for i in indices],
    color=[colors[i] for i in range(len(indices))],
    edgecolor='white',
    height=0.5
)
for bar, val in zip(bars, [importances[i] for i in indices]):
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
            f'{val:.3f}', va='center', fontweight='bold', fontsize=12)
ax.set_xlabel("Importance relative")
ax.set_title("Feature Importance - RandomForest (NutriPredict)")
ax.set_xlim(0, max(importances) + 0.08)
plt.tight_layout()
plt.savefig(os.path.join(ASSETS_DIR, "feature_importance.png"), dpi=150, bbox_inches='tight')
plt.close()
print("      feature_importance.png sauvegardee.")

# ── 5. Analyse des residus ──
print("[5/6] Generation du graphique des residus...")
y_pred = model_100.predict(X_test)
residus = y_test.values - y_pred

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Scatter des residus
ax1.scatter(y_pred, residus, alpha=0.4, s=15, color='#2B6CB0', edgecolors='none')
ax1.axhline(y=0, color='#E53E3E', linewidth=1.5, linestyle='--')
ax1.set_xlabel("Valeurs predites (g)")
ax1.set_ylabel("Residus (g)")
ax1.set_title("Residus vs Predictions")

# Histogramme des residus
ax2.hist(residus, bins=40, color='#2B6CB0', edgecolor='white', alpha=0.8)
ax2.axvline(x=0, color='#E53E3E', linewidth=1.5, linestyle='--')
ax2.set_xlabel("Residus (g)")
ax2.set_ylabel("Frequence")
ax2.set_title(f"Distribution des residus (MAE={mae_100:.2f}g)")

plt.tight_layout()
plt.savefig(os.path.join(ASSETS_DIR, "residus_analysis.png"), dpi=150, bbox_inches='tight')
plt.close()
print("      residus_analysis.png sauvegardee.")

# ── 6. Resume ──
print("[6/6] Resume des fichiers generes.")
print()
print("=" * 60)
print("  FICHIERS GENERES DANS docs/assets/")
print("=" * 60)
for f in sorted(os.listdir(ASSETS_DIR)):
    if f.endswith('.png'):
        size = os.path.getsize(os.path.join(ASSETS_DIR, f)) / 1024
        print(f"  - {f} ({size:.0f} Ko)")
print()
print("  MLflow UI accessible via :")
print(f"  $ mlflow ui --backend-store-uri sqlite:///{os.path.join(BASE_DIR, 'mlruns.db')} --port 5000")
print(f"  Puis ouvrir http://127.0.0.1:5000 dans le navigateur")
print("=" * 60)
