# NutriPredict - Research & Data Science (Bloc 1)

Ce répertoire est dédié à l'acquisition, à l'analyse et à la modélisation des données pour le projet NutriPredict.

## Objectifs
- **Acquisition** : extraction des données nutritionnelles depuis l'API OpenFoodFacts.
- **Analyse (EDA)** : exploration statistique des variables nutritionnelles (nutriscore, nutriments).
- **Modélisation** : entraînement de modèles prédictifs recommandant des ajustements alimentaires basés sur les métriques de santé.

## Structure
- `data/raw/` : données brutes (JSON, CSV).
- `data/processed/` : données nettoyées et transformées.
- `notebooks/` : analyses exploratoires et prototypes de modèles.
- `scripts/` : pipelines d'ingestion et de prétraitement.

## Ingestion des données
Le script `scripts/ingest_off.py` récupère les produits de la catégorie "biscuits" sur le marché français.
Les champs extraits sont :
- `code` : identifiant unique (code-barres).
- `product_name` : nom du produit.
- `nutriscore_grade` : note nutri-score.
- `nutriments` : détails nutritionnels pour 100g.
