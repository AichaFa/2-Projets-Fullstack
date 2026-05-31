FROM python:3.11-slim

# 1. Dépendances système minimales pour XGBoost (installées en root au début)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Création de l'utilisateur non-root exigé par Hugging Face
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

# 3. Dossier de travail (dans l'espace de l'utilisateur)
WORKDIR /app

# 4. Copie et installation des dépendances Python (avec attribution des droits à user)
COPY --chown=user requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# 5. Copie du code et du modèle (avec attribution des droits à user)
COPY --chown=user ./app.py /app/app.py
COPY --chown=user ./best_model.joblib /app/best_model.joblib

# 6. Exposition du port et lancement
EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
#lancement de l'application FastAPI avec Uvicorn, en écoutant sur toutes les interfaces réseau (0.0.0.0) et sur le port 7860.


