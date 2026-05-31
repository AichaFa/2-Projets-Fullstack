"""
API de prédiction du prix de location - Projet Getaround
========================================================
Cette API expose un point de terminaison /predict qui renvoie le prix
de location journalier suggéré pour un véhicule, à partir de ses
caractéristiques.

Auteur : Projet déploiement
"""

from typing import List, Union
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Configuration de l'application
# ---------------------------------------------------------------------------
APP_TITLE = "Getaround - API de prédiction du prix de location"
APP_DESCRIPTION = (
    "Cette API expose un modèle de Machine Learning entraîné pour suggérer "
    "le prix journalier optimal d'une location de véhicule, à partir de ses "
    "caractéristiques techniques et de ses équipements."
)
APP_VERSION = "1.0.0"

MODEL_PATH = Path(__file__).resolve().parent / "best_model.joblib"

# Colonnes attendues dans l'ordre du modèle
FEATURE_COLUMNS = [
    "model_key", "mileage", "engine_power", "fuel", "paint_color",
    "car_type", "private_parking_available", "has_gps",
    "has_air_conditioning", "automatic_car", "has_getaround_connect",
    "has_speed_regulator", "winter_tires"
]

# Modalités acceptées (à titre informatif)
ACCEPTED_MODELS = [
    "Citroën", "Renault", "BMW", "Peugeot", "Audi", "Nissan", "Mitsubishi",
    "Mercedes", "Volkswagen", "Toyota", "SEAT", "Subaru", "Opel", "PGO",
    "Ferrari", "Other"
]
ACCEPTED_FUELS = ["diesel", "petrol", "hybrid_petrol", "electro"]
ACCEPTED_COLORS = ["black", "grey", "white", "red", "silver", "blue",
                   "orange", "beige", "brown", "green"]
ACCEPTED_CAR_TYPES = ["convertible", "coupe", "estate", "hatchback",
                      "sedan", "subcompact", "suv", "van"]

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url=None,        # on remplace par notre propre /docs
    redoc_url="/redoc"
)

# Chargement du modèle une fois au démarrage
try:
    model = joblib.load(MODEL_PATH)
    MODEL_LOADED = True
except Exception as exc:
    print(f"Erreur de chargement du modèle : {exc}")
    model = None
    MODEL_LOADED = False


# ---------------------------------------------------------------------------
# Schémas Pydantic
# ---------------------------------------------------------------------------
class PredictionInput(BaseModel):
    """Schéma d'entrée acceptant une liste de listes de caractéristiques.

    Ordre attendu des colonnes :
    [model_key, mileage, engine_power, fuel, paint_color, car_type,
     private_parking_available, has_gps, has_air_conditioning,
     automatic_car, has_getaround_connect, has_speed_regulator,
     winter_tires]
    """
    input: List[List[Union[str, int, float, bool]]] = Field(
        ...,
        examples=[[[
            "Citroën", 140411, 100, "diesel", "black", "convertible",
            True, True, False, False, True, True, True
        ]]]
    )


class PredictionOutput(BaseModel):
    prediction: List[float]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/", tags=["Accueil"])
async def root():
    """Point d'entrée par défaut. Vérifie que l'API est opérationnelle."""
    return {
        "message": "API Getaround opérationnelle",
        "version": APP_VERSION,
        "model_loaded": MODEL_LOADED,
        "documentation": "/docs"
    }


@app.get("/health", tags=["Accueil"])
async def health():
    """Indicateur de santé du service."""
    return {"status": "ok" if MODEL_LOADED else "model_missing"}


@app.post("/predict",
          tags=["Prédiction"],
          response_model=PredictionOutput,
          summary="Prédire le prix de location journalier")
async def predict(payload: PredictionInput):
    """Renvoie la prédiction du prix de location journalier (EUR/jour).

    Le format d'entrée attendu est conforme à la spécification :
    une liste de listes contenant, dans l'ordre, les caractéristiques du
    véhicule.

    Exemple :
        {
          "input": [["Citroën", 140411, 100, "diesel", "black",
                     "convertible", true, true, false, false, true,
                     true, true]]
        }

    Renvoie :
        {"prediction": [108.42]}
    """
    if not MODEL_LOADED:
        raise HTTPException(status_code=503,
                            detail="Modèle non chargé sur le serveur.")

    try:
        df_input = pd.DataFrame(payload.input, columns=FEATURE_COLUMNS)

        # Conversion explicite des booléens
        bool_cols = ["private_parking_available", "has_gps",
                     "has_air_conditioning", "automatic_car",
                     "has_getaround_connect", "has_speed_regulator",
                     "winter_tires"]
        for c in bool_cols:
            df_input[c] = df_input[c].astype(int)

        # Conversion des numériques
        df_input["mileage"] = df_input["mileage"].astype(int)
        df_input["engine_power"] = df_input["engine_power"].astype(int)

        preds = model.predict(df_input)
        return {"prediction": [round(float(p), 2) for p in preds]}

    except Exception as exc:
        raise HTTPException(status_code=400,
                            detail=f"Erreur lors de la prédiction : {exc}")


# ---------------------------------------------------------------------------
# Documentation HTML personnalisée à /docs
# ---------------------------------------------------------------------------
@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def custom_docs():
    """Page de documentation HTML stylée."""
    html = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Documentation - API Getaround</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                         "Helvetica Neue", Arial, sans-serif;
            background: #f5f7fb;
            color: #1f2937;
            line-height: 1.6;
        }
        .container { max-width: 960px; margin: 0 auto; padding: 40px 24px; }
        header {
            background: linear-gradient(135deg, #5b21b6 0%, #7c3aed 100%);
            color: white;
            padding: 48px 24px;
            text-align: center;
            border-radius: 12px;
            margin-bottom: 32px;
            box-shadow: 0 8px 24px rgba(91, 33, 182, 0.18);
        }
        h1 { font-size: 2.4em; margin-bottom: 8px; font-weight: 700; }
        header p { font-size: 1.05em; opacity: 0.95; }
        h2 {
            color: #5b21b6;
            margin: 32px 0 16px 0;
            font-size: 1.5em;
            border-bottom: 2px solid #e9d5ff;
            padding-bottom: 8px;
        }
        h3 { color: #4c1d95; margin: 20px 0 12px 0; font-size: 1.15em; }
        section {
            background: white;
            padding: 28px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }
        .endpoint {
            background: #f9fafb;
            border-left: 4px solid #7c3aed;
            padding: 16px 20px;
            border-radius: 6px;
            margin: 16px 0;
        }
        .method {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 0.85em;
            letter-spacing: 0.5px;
            margin-right: 12px;
        }
        .method.get { background: #dbeafe; color: #1e40af; }
        .method.post { background: #dcfce7; color: #166534; }
        code {
            background: #f3f4f6;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: "Monaco", "Consolas", monospace;
            font-size: 0.9em;
            color: #be185d;
        }
        pre {
            background: #1f2937;
            color: #e5e7eb;
            padding: 18px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 12px 0;
            font-size: 0.88em;
            line-height: 1.5;
        }
        pre code { background: none; color: inherit; padding: 0; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
        }
        th, td {
            padding: 10px 14px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        th { background: #f3f4f6; font-weight: 600; color: #374151; }
        ul { padding-left: 24px; margin: 8px 0; }
        li { margin: 4px 0; }
        footer {
            text-align: center;
            color: #6b7280;
            font-size: 0.9em;
            margin-top: 32px;
            padding: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>API Getaround - Prédiction du prix de location</h1>
            <p>Documentation des points de terminaison - Version 1.0.0</p>
        </header>

        <section>
            <h2>Présentation</h2>
            <p>Cette API met à disposition un modèle de Machine Learning
            entraîné pour suggérer le prix journalier optimal d'une location
            de véhicule sur la plateforme Getaround.</p>
            <p>Le modèle sous-jacent est un <strong>XGBoost Regressor</strong>
            avec les performances suivantes sur le jeu de test :</p>
            <ul>
                <li>Erreur absolue moyenne (MAE) : <strong>9,18 EUR</strong></li>
                <li>RMSE : <strong>12,82 EUR</strong></li>
                <li>R² : <strong>0,846</strong></li>
            </ul>
        </section>

        <section>
            <h2>Points de terminaison</h2>

            <div class="endpoint">
                <span class="method get">GET</span><code>/</code>
                <h3>Accueil</h3>
                <p>Renvoie un message confirmant que l'API est opérationnelle
                et l'état du chargement du modèle.</p>
                <h4>Exemple de réponse</h4>
<pre><code>{
  "message": "API Getaround opérationnelle",
  "version": "1.0.0",
  "model_loaded": true,
  "documentation": "/docs"
}</code></pre>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span><code>/health</code>
                <h3>Santé du service</h3>
                <p>Renvoie l'état de santé du service. Utile pour les
                vérifications automatiques.</p>
<pre><code>{"status": "ok"}</code></pre>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span><code>/predict</code>
                <h3>Prédiction du prix</h3>
                <p>Retourne le prix journalier estimé pour un ou plusieurs
                véhicules, à partir de leurs caractéristiques.</p>

                <h4>Schéma d'entrée</h4>
                <p>Le corps de la requête est un JSON dont la clé
                <code>input</code> contient une liste de listes. Chaque
                liste interne représente un véhicule et respecte l'ordre
                de colonnes suivant :</p>
                <table>
                    <tr><th>Position</th><th>Champ</th><th>Type</th><th>Exemple</th></tr>
                    <tr><td>1</td><td>model_key</td><td>chaîne</td><td>"Citroën"</td></tr>
                    <tr><td>2</td><td>mileage</td><td>entier</td><td>140411</td></tr>
                    <tr><td>3</td><td>engine_power</td><td>entier</td><td>100</td></tr>
                    <tr><td>4</td><td>fuel</td><td>chaîne</td><td>"diesel"</td></tr>
                    <tr><td>5</td><td>paint_color</td><td>chaîne</td><td>"black"</td></tr>
                    <tr><td>6</td><td>car_type</td><td>chaîne</td><td>"convertible"</td></tr>
                    <tr><td>7</td><td>private_parking_available</td><td>booléen</td><td>true</td></tr>
                    <tr><td>8</td><td>has_gps</td><td>booléen</td><td>true</td></tr>
                    <tr><td>9</td><td>has_air_conditioning</td><td>booléen</td><td>false</td></tr>
                    <tr><td>10</td><td>automatic_car</td><td>booléen</td><td>false</td></tr>
                    <tr><td>11</td><td>has_getaround_connect</td><td>booléen</td><td>true</td></tr>
                    <tr><td>12</td><td>has_speed_regulator</td><td>booléen</td><td>true</td></tr>
                    <tr><td>13</td><td>winter_tires</td><td>booléen</td><td>true</td></tr>
                </table>

                <h4>Exemple de requête (cURL)</h4>
<pre><code>curl -i -H "Content-Type: application/json" -X POST \\
  -d '{"input": [["Citroën", 140411, 100, "diesel", "black",
       "convertible", true, true, false, false, true, true, true]]}' \\
  https://votre-url/predict</code></pre>

                <h4>Exemple de requête (Python)</h4>
<pre><code>import requests

response = requests.post("https://votre-url/predict", json={
    "input": [["Citroën", 140411, 100, "diesel", "black",
               "convertible", True, True, False, False, True, True, True]]
})
print(response.json())</code></pre>

                <h4>Exemple de réponse</h4>
<pre><code>{
  "prediction": [108.42]
}</code></pre>
            </div>
        </section>

        <section>
            <h2>Modalités acceptées</h2>
            <h3>Marques (model_key)</h3>
            <p>Citroën, Renault, BMW, Peugeot, Audi, Nissan, Mitsubishi,
            Mercedes, Volkswagen, Toyota, SEAT, Subaru, Opel, PGO, Ferrari,
            Other</p>
            <h3>Carburants (fuel)</h3>
            <p>diesel, petrol, hybrid_petrol, electro</p>
            <h3>Couleurs (paint_color)</h3>
            <p>black, grey, white, red, silver, blue, orange, beige, brown,
            green</p>
            <h3>Types de véhicules (car_type)</h3>
            <p>convertible, coupe, estate, hatchback, sedan, subcompact,
            suv, van</p>
        </section>

        <footer>
            <p>Documentation interactive alternative disponible sur
            <code>/redoc</code></p>
        </footer>
    </div>
</body>
</html>
"""
    return HTMLResponse(content=html, status_code=200)


# ---------------------------------------------------------------------------
# Lancement
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
