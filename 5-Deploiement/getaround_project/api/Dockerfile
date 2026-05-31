name: Deploy API to Hugging Face Spaces

on:
  push:
    branches: [ "main" ]
    paths:
      - '5-Deploiement/getaround_project/api/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Push to Hugging Face
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: |
          git config --global user.email "204518881+AichaFa@users.noreply.github.com"
          git config --global user.name "AichaFa"
          
          # Clonage propre du Space Hugging Face
          git clone https://AichaFa:$HF_TOKEN@huggingface.co/spaces/AichaFaHugFace/getaround-api hf_space
          
          # Copie des fichiers de l'API dans le dossier cloné
          cp -r 5-Deploiement/getaround_project/api/* hf_space/
          
          cd hf_space
          git add .
          git diff-index --quiet HEAD || git commit -m "Deploy: Update API content"
          
          # Le --force va écraser le conflit "fetch first" que tu as eu !
          git push origin main --force
#lancement de l'application FastAPI avec Uvicorn, en écoutant sur toutes les interfaces réseau (0.0.0.0) et sur le port 7860.


