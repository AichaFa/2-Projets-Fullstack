# Projet Getaround - Analyse des retards et optimisation du prix

## Démos en ligne

| Service | URL | Description |
|---|---|---|
| **API de prédiction** | https://aichafahugface-getaround-api.hf.space | Endpoint `/predict` pour suggérer un prix journalier |
| Documentation API | https://aichafahugface-getaround-api.hf.space/docs | Page HTML interactive avec exemples et schémas |
| **Tableau de bord** | https://aichafahugface-getaround-dashboard.hf.space | Analyse interactive des retards avec simulateur de seuil |

### Exemple d'appel à l'API (curl)

```bash
curl -X POST "https://aichafahugface-getaround-api.hf.space/predict" \
  -H "Content-Type: application/json" \
  -d '{"input": [["Citroën", 140411, 100, "diesel", "black", "convertible", true, true, false, false, true, true, true]]}'
```

Réponse attendue : `{"prediction": [107.97]}`

### Exemple d'appel à l'API (Python)

```python
import requests

response = requests.post(
    "https://aichafahugface-getaround-api.hf.space/predict",
    json={
        "input": [[
            "Citroën", 140411, 100, "diesel", "black", "convertible",
            True, True, False, False, True, True, True
        ]]
    }
)
print(response.json())
# Affiche : {'prediction': [107.97]}
```

---

## Présentation

Ce projet répond à une double problématique pour la plateforme de location de véhicules entre particuliers Getaround :

1. **Analyse des retards** : étudier l'impact des retours tardifs entre deux locations consécutives, et calibrer un seuil minimum de délai entre deux locations afin de réduire les frictions clients sans pénaliser les revenus des propriétaires.
2. **Optimisation du prix** : construire un modèle de Machine Learning qui suggère le prix journalier optimal d'une location à partir des caractéristiques du véhicule, et l'exposer via une API documentée.

## Structure du dépôt

```
getaround_project/
├── api/                          # API FastAPI de prédiction
│   ├── app.py                    # Code de l'API
│   ├── best_model.joblib         # Modèle sérialisé
│   ├── Dockerfile                # Image pour Hugging Face Spaces
│   └── requirements.txt          # Dépendances
├── dashboard/                    # Tableau de bord Streamlit
│   ├── dashboard.py              # Application Streamlit
│   ├── data/                     # Données de retards (xlsx)
│   ├── Dockerfile                # Image pour Hugging Face Spaces
│   └── requirements.txt          # Dépendances
├── data/                         # Données sources
│   ├── get_around_delay_analysis.xlsx
│   └── get_around_pricing_project.csv
├── figures/                      # Visualisations exportées
├── models/                       # Modèle entraîné et résultats
│   ├── best_model.joblib
│   └── model_results.csv
├── notebooks/                    # Notebook d'analyse complète
│   └── analyse_getaround.ipynb
├── train_model.py                # Script d'entraînement réutilisable
└── README.md
```

## Résultats principaux

### Analyse des retards

| Indicateur | Valeur |
|---|---|
| Locations totales analysées | 21 310 |
| Taux d'annulation | 15,3% |
| Restitutions en retard | 57,5% |
| Délai médian au checkout | +9 min |
| Locations chaînées | 8,6% (1 841) |
| Cas problématiques (attente subie) | 12,6% des chaînages |

**Recommandation principale** : un seuil de **120 minutes** appliqué à l'ensemble du parc résout 83% des cas problématiques pour un impact de moins de 3% sur le chiffre d'affaires. Une approche prudente alternative consiste à appliquer 60 minutes uniquement aux voitures Connect (impact CA inférieur à 1%).

### Modèle de pricing

| Modèle | MAE (EUR) | RMSE (EUR) | R² |
|---|---|---|---|
| Régression linéaire | 11,58 | 15,81 | 0,766 |
| Ridge | 11,56 | 15,79 | 0,766 |
| Random Forest | 9,64 | 13,56 | 0,828 |
| Gradient Boosting | 9,61 | 13,32 | 0,834 |
| **XGBoost (retenu)** | **9,18** | **12,82** | **0,846** |

Le modèle retenu est un XGBoost Regressor avec une MAE de 9,18 EUR sur le jeu de test, suffisamment précis pour suggérer un prix de référence aux propriétaires.

## Lancement local

Les scripts utilisent des chemins **portables** (relatifs au fichier source) : ils fonctionnent quel que soit le répertoire courant ou le système d'exploitation.

### Préparation de l'environnement

```bash
python -m venv venv
# Sous Windows
.\venv\Scripts\activate
# Sous Linux/macOS
source venv/bin/activate
```

### API

```bash
cd api
pip install -r requirements.txt
python app.py
```

L'API sera alors accessible dans votre navigateur sur `http://localhost:8000`, la documentation HTML sur `http://localhost:8000/docs` et l'interface OpenAPI alternative sur `http://localhost:8000/redoc`.

Exemple de requête sous Linux/macOS :

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": [["Citroën", 140411, 100, "diesel", "black", "convertible", true, true, false, false, true, true, true]]}'
```

Sous Windows (PowerShell) :

```powershell
$body = @{ input = @(,@("Citroën", 140411, 100, "diesel", "black", "convertible", $true, $true, $false, $false, $true, $true, $true)) } | ConvertTo-Json -Compress -Depth 4
Invoke-RestMethod -Uri http://localhost:8000/predict -Method POST -Body $body -ContentType "application/json"
```

Réponse attendue : `{"prediction": [107.97]}`

### Dashboard

```bash
cd dashboard
pip install -r requirements.txt
streamlit run dashboard.py
```

Le tableau de bord local sera alors accessible dans votre navigateur sur `http://localhost:8501`.

### Notebook

```bash
jupyter notebook notebooks/analyse_getaround.ipynb
```

Le notebook détecte automatiquement le dossier `data/` quel que soit son emplacement d'ouverture.

### Entraînement du modèle

```bash
python train_model.py
```

Le modèle est sauvegardé dans `models/best_model.joblib` et le pipeline est tracé dans `mlruns/`.

### MLflow UI

```bash
mlflow ui --backend-store-uri file:./mlruns
```

Interface accessible sur `http://localhost:5000`.

## Déploiement en production

Les deux composants (API et dashboard) sont conteneurisés et déployés sur Hugging Face Spaces (voir la section "Démos en ligne" en haut de ce document).

### API sur Hugging Face Spaces

1. Créer un nouveau Space de type **Docker** sur Hugging Face.
2. Pousser les fichiers du dossier `api/` (`app.py`, `requirements.txt`, `Dockerfile`, `best_model.joblib`).
3. Le Space est automatiquement construit et exposé sur une URL publique.

Endpoints accessibles :
- `GET /` - accueil
- `GET /health` - état du service
- `POST /predict` - prédiction du prix
- `GET /docs` - documentation HTML
- `GET /redoc` - documentation OpenAPI alternative

### Dashboard sur Hugging Face Spaces

1. Créer un second Space de type **Docker**.
2. Pousser les fichiers du dossier `dashboard/` (`dashboard.py`, `requirements.txt`, `Dockerfile`, `data/`).
3. Le tableau de bord est accessible sur l'URL du Space.

## Dépendances principales

- Python >= 3.12
- pandas, numpy, scikit-learn 1.8, xgboost 3.2
- mlflow pour le suivi d'expériences
- FastAPI + Uvicorn pour l'API
- Streamlit + Plotly pour le dashboard

## Licence

Projet pédagogique. Données fournies par Getaround.

## Stack technique

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-231F20?style=for-the-badge&logo=xgboost&logoColor=white)

---

## Certification

> Projet de certification - Bloc #5
>
> Ce projet fait partie des livrables obligatoires pour la validation du Bloc #5 : Déploiement et mise en production du certificat d'Ingénieur en Apprentissage Automatique (Concepteur Développeur en Science des Données).
>
> Compétences évaluées et validées ici :
> * Industrialisation et gestion du cycle de vie d'un modèle de régression (tracking des expériences, journalisation des hyperparamètres et sérialisation du modèle optimal avec MLflow).
> * Développement et exposition d'un service de prédiction Web scalable (conception d'une API REST avec FastAPI, validation stricte des données d'entrée via Pydantic et documentation OpenAPI).
> * Conception d'un tableau de bord d'aide à la décision métier et déploiement cloud (développement sous Streamlit pour simuler les seuils opérationnels et isolation des environnements d'exécution par conteneurisation Docker multi-services sur Hugging Face Spaces).