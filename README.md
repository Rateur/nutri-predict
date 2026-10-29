# Nutri-Predict

[![Backend CI](https://github.com/Rateur/nutri-predict/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/Rateur/nutri-predict/actions/workflows/backend-ci.yml)
[![CD Deployment Pipeline](https://github.com/Rateur/nutri-predict/actions/workflows/cd-deployment.yml/badge.svg)](https://github.com/Rateur/nutri-predict/actions/workflows/cd-deployment.yml)

Systeme de Machine Learning de bout en bout predisant l'impact ponderal d'une consommation calorique donnee. Developpe dans le cadre du Titre RNCP Developpeur en Intelligence Artificielle -- Simplon / Lyon 2026.

> Ce depot public reprend l'etat final du projet, nettoye : aucune cle ni aucun mot de passe. L'historique de developpement reste prive.

---

## Table des matieres

- [Apercu du projet](#apercu-du-projet)
- [Architecture technique](#architecture-technique)
- [Securite](#securite)
- [Installation et deploiement](#installation-et-deploiement)
- [Tests](#tests)
- [Points de repere](#points-de-repere)
- [Rapports RNCP](#rapports-rncp)

---

## Apercu du projet

Nutri-Predict expose une API de prediction nutritionnelle entrainee sur les donnees OpenFoodFacts. L'utilisateur soumet un profil biometrique et une consommation calorique ; le modele retourne une estimation d'impact ponderal.

Le projet couvre l'ensemble du cycle de vie d'un systeme IA : ingestion de donnees, modelisation, exposition via API REST, interface web, monitoring et pipeline CI/CD.

Les calories des biscuits viennent d'OpenFoodFacts (licence ODbL). Le metabolisme, la portion et la variation de poids sont simules : la cible est calculee par une formule avec du bruit (voir `research/notebooks/01_eda_predictive_modeling.ipynb`).

---

## Architecture technique

```
nutri-predict/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/     # Routes FastAPI (predict, products, health_metrics)
│   │   ├── core/              # Config, auth API Key, chiffrement AES-256, rate limiter
│   │   ├── models/            # Modeles SQLAlchemy (User, HealthMetrics)
│   │   ├── schemas/           # Schemas Pydantic (validation entree/sortie)
│   │   ├── services/          # Logique metier (MLService singleton)
│   │   └── main.py            # Point d'entree FastAPI, middlewares, CORS
│   ├── tests/                 # Tests unitaires et d'integration (Pytest, 13 tests)
│   ├── Dockerfile
│   └── requirements.txt
├── research/
│   ├── data/processed/        # Datasets Parquet (ml_training_dataset)
│   ├── models/                # Modele serialise (nutri_predict_rf_model.joblib)
│   ├── notebooks/             # EDA, feature engineering, entrainement
│   └── scripts/               # MLflow experiment, evaluation ML, ingestion
├── frontend/                  # Interface web (HTML / Vanilla JS)
├── monitoring/                # Config Prometheus, dashboards Grafana
├── docs/                      # Rapports RNCP PDF (E1-E5), screenshots
├── .github/workflows/         # CI (lint, tests, validation ML) + CD (Docker, GHCR)
└── docker-compose.yml
```

**Stack principale**

| Couche | Technologie |
|--------|-------------|
| Traitement donnees | DuckDB, Apache Parquet |
| Base de donnees | PostgreSQL 16, modelisation Merise |
| Backend | FastAPI, Python 3.12, Pydantic v2 |
| Machine Learning | Scikit-Learn -- `RandomForestRegressor` (R2=0.985, MAE=2.09g) |
| Frontend | Vanilla JS |
| MLOps | MLflow (tracking des experimentations) |
| Observabilite | Structlog (JSON), Prometheus, Grafana |
| Deploiement | Docker, GitHub Actions, GHCR |

---

## Securite

Les donnees biometriques (BMR, poids, taille) ne sont jamais stockees en clair.

- **Chiffrement AES-256-GCM** -- implemente dans `backend/app/core/security.py`. La cle est injectee au runtime via variable d'environnement, jamais presente dans le code source.
- **Authentification API Key** -- verification via `X-API-KEY` header (`backend/app/core/auth.py`).
- **Rate Limiting** -- SlowAPI, 5 req/min par IP sur les endpoints sensibles (`backend/app/core/limiter.py`).
- **Headers de securite** -- CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy (middleware dans `main.py`).
- **CORS restreint** -- origines autorisees configurables via `.env`.

---

## Installation et deploiement

### Prerequis

- Docker et Docker Compose
- Python 3.12+ (pour le developpement local)

### 1. Configurer les variables d'environnement

```bash
cp .env.example .env
# Renseigner ENCRYPTION_KEY (32 octets, base64 URL-safe) et API_KEY.
# Generer une cle :
python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
```

Reporter la meme valeur d'`API_KEY` dans `frontend/app.js`. C'est une cle de demo : le front la lit en clair. En production, le front passerait par un serveur qui garde la cle.

### 2. Demarrer l'infrastructure

```bash
docker compose up -d --build
```

| Service | URL |
|---------|-----|
| API (Swagger) | `http://localhost:8000/docs` |
| Frontend | `http://localhost:5500` |
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3000` (admin/admin par defaut, a changer avec `GRAFANA_PASSWORD`) |

### 3. Developpement local (sans Docker)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Tests

```bash
# Tests unitaires et d'integration backend (13 tests)
PYTHONPATH=backend pytest backend/tests/ -v

# Validation des performances du modele (R2 > 0.95, MAE < 5.0)
PYTHONPATH=. pytest research/scripts/test_model_performance.py -v
```

Les seuils de performance sont verifies automatiquement a chaque push via le pipeline CI (`test-ml-performance`).

---

## Points de repere

Les donnees sont simulees : la cible contient un bruit de 2 g d'ecart-type. Sur le jeu de test (1000 cas) :

- **Regression lineaire** : R2 = 0.959.
- **Maximum possible** : R2 = 0.993. C'est le R2 de la formule sans bruit ; le bruit interdit d'aller plus haut.
- **RandomForest** : R2 = 0.985, avec 100 arbres comme avec 50.
- Pour verifier : `python research/scripts/baselines.py` (dependances : `research/requirements.txt`).

---

## Rapports RNCP

Ce projet est le livrable d'evaluation du Titre RNCP37827 Developpeur IA. Les rapports PDF sont disponibles dans `docs/`.

| Epreuve | Rapport | Competences |
|---------|---------|-------------|
| E1 | `docs/RAPPORT_E1.pdf` -- Base de Donnees et Ingestion Data | C1 a C5 |
| E2 | `docs/RAPPORT_E2.pdf` -- Developpement Backend et API | C6 a C8 |
| E3 | `docs/RAPPORT_E3.pdf` -- Intelligence Artificielle et MLOps | C9 a C13 |
| E4 | `docs/RAPPORT_E4.pdf` -- CI/CD, DevOps et Monitoring | C14 a C17 |
| E5 | `docs/RAPPORT_E5.pdf` -- Gestion de Projet Agile | C18 a C20 |

---

*Projet realise par Valentin Peries -- Simplon Lyon, promotion 2026.*