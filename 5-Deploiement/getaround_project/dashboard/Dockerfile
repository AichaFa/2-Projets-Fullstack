FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Création du dossier data et copie
RUN mkdir -p /app/data
COPY ./dashboard.py /app/dashboard.py
COPY ./data/get_around_delay_analysis.xlsx /app/data/get_around_delay_analysis.xlsx

EXPOSE 7860

CMD ["streamlit", "run", "dashboard.py", "--server.port=7860", "--server.address=0.0.0.0"]
