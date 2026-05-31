FROM python:3.11-slim

WORKDIR /code

# Dépendances système minimales pour XGBoost
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Code et modèle
COPY ./app.py /code/app.py
COPY ./best_model.joblib /code/best_model.joblib

# Port (Hugging Face Spaces utilise 7860 par défaut)
EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
