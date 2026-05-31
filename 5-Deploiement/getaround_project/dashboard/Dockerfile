FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Création du dossier data
RUN mkdir -p /code/data

# Code et données
COPY ./dashboard.py /code/dashboard.py
COPY ./data/get_around_delay_analysis.xlsx /code/data/get_around_delay_analysis.xlsx

EXPOSE 7860

CMD ["streamlit", "run", "dashboard.py", "--server.port=7860", "--server.address=0.0.0.0"]
