"""
Script d'entraînement du modèle de pricing.

Exécution : python train_model.py
"""
from pathlib import Path
import warnings

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings('ignore')

np.random.seed(42)

# Chemins portables : relatifs au fichier source, fonctionnent depuis
# n'importe quel répertoire courant (Windows, Linux, macOS, Docker).
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "get_around_pricing_project.csv"
MODEL_OUTPUT = BASE_DIR / "models" / "best_model.joblib"


def load_and_clean(path):
    """Charge le CSV et applique les filtres de nettoyage."""
    df = pd.read_csv(path).drop(columns=['Unnamed: 0'])
    df = df[df['mileage'] >= 0]
    df = df[df['engine_power'] > 0]
    df = df[df['mileage'] <= 500000]
    df = df[(df['rental_price_per_day'] >= 30) & (df['rental_price_per_day'] <= 350)]
    rare = df['model_key'].value_counts()[df['model_key'].value_counts() < 20].index
    df['model_key'] = df['model_key'].replace(rare, 'Other')
    return df


def build_pipeline(model):
    """Construit le pipeline scikit-learn : prétraitement + modèle."""
    cat_cols = ['model_key', 'fuel', 'paint_color', 'car_type']
    num_cols = ['mileage', 'engine_power']
    bool_cols = ['private_parking_available', 'has_gps', 'has_air_conditioning',
                 'automatic_car', 'has_getaround_connect', 'has_speed_regulator',
                 'winter_tires']
    pre = ColumnTransformer([
        ('num', StandardScaler(), num_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore', drop='first'), cat_cols),
        ('bool', 'passthrough', bool_cols)
    ])
    return Pipeline([('preprocessor', pre), ('regressor', model)])


def main():
    """Entraîne plusieurs modèles, sélectionne le meilleur et le sauvegarde."""
    df = load_and_clean(DATA_PATH)
    print(f"Lignes après nettoyage : {len(df)}")

    y = df['rental_price_per_day']
    X = df.drop(columns=['rental_price_per_day'])
    bool_cols = ['private_parking_available', 'has_gps', 'has_air_conditioning',
                 'automatic_car', 'has_getaround_connect', 'has_speed_regulator',
                 'winter_tires']
    for c in bool_cols:
        X[c] = X[c].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    mlflow.set_experiment("getaround_pricing")

    models = {
        'LinearRegression': LinearRegression(),
        'Ridge': Ridge(alpha=1.0, random_state=42),
        'RandomForest': RandomForestRegressor(
            n_estimators=200, max_depth=15,
            random_state=42, n_jobs=-1
        ),
        'GradientBoosting': GradientBoostingRegressor(
            n_estimators=200, max_depth=5,
            learning_rate=0.05, random_state=42
        ),
        'XGBoost': xgb.XGBRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            random_state=42, verbosity=0, n_jobs=-1
        ),
    }

    best_mae = float('inf')
    best_pipe = None
    best_name = None

    for name, m in models.items():
        with mlflow.start_run(run_name=name):
            pipe = build_pipeline(m)
            pipe.fit(X_train, y_train)
            preds = pipe.predict(X_test)
            mae = mean_absolute_error(y_test, preds)
            rmse = np.sqrt(mean_squared_error(y_test, preds))
            r2 = r2_score(y_test, preds)

            mlflow.log_param('model', name)
            mlflow.log_metric('test_mae', mae)
            mlflow.log_metric('test_rmse', rmse)
            mlflow.log_metric('test_r2', r2)
            mlflow.sklearn.log_model(pipe, name="model")

            print(f"  {name:18s} MAE={mae:6.2f}  RMSE={rmse:6.2f}  R²={r2:.4f}")

            if mae < best_mae:
                best_mae = mae
                best_pipe = pipe
                best_name = name

    MODEL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipe, MODEL_OUTPUT)
    print(f"\nMeilleur modèle : {best_name} (MAE={best_mae:.2f})")
    print(f"Sauvegardé dans : {MODEL_OUTPUT}")


if __name__ == "__main__":
    main()
