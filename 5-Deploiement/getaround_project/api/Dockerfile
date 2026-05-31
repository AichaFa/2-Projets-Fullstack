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
          # 1. Configuration de l'identité Git
          git config --global user.email "204518881+AichaFa@users.noreply.github.com"
          git config --global user.name "AichaFa"
          
          # 2. Clonage du Space Hugging Face existant
          git clone https://AichaFa:$HF_TOKEN@huggingface.co/spaces/AichaFaHugFace/getaround-api hf_space
          
          # 3. Nettoyage du contenu précédent (sauf le dossier .git caché)
          find hf_space -maxdepth 1 -not -name 'hf_space' -not -name '.git' -exec rm -rf {} \;
          
          # 4. Copie du nouveau contenu de l'API
          cp -r 5-Deploiement/getaround_project/api/* hf_space/
          
          # 5. Commit et Push dans l'historique linéaire de Hugging Face
          cd hf_space
          git add .
          git diff-index --quiet HEAD || git commit -m "Deploy: Synchronisation automatique de l'API"
          git push origin main
#lancement de l'application FastAPI avec Uvicorn, en écoutant sur toutes les interfaces réseau (0.0.0.0) et sur le port 7860.


