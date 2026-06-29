# Plan your trip with Kayak

Pipeline ETL complet qui recommande les **5 meilleures destinations** et les **20 meilleurs hôtels** en France, en combinant des données météorologiques et hôtelières collectées automatiquement, puis stockées sur une infrastructure cloud AWS.

## Contexte et objectif

L'équipe marketing souhaite un outil de recommandation de destinations fondé sur des données réelles. Aucune base n'existant au départ, le projet collecte, nettoie, stocke et restitue les données de bout en bout :

- coordonnées géographiques des villes,
- prévisions météorologiques,
- offre hôtelière (nom, note, lien, description).

Le périmètre couvre les 35 villes françaises imposées par le cahier des charges.

## Architecture du pipeline

```
Géocodage (Nominatim)
        |
   API Météo (OpenWeatherMap)        Scraping hôtels (Selenium / Booking.com)
        |                                         |
        +---------------- ETL (Pandas) -----------+
                          |
              Nettoyage, géocodage des hôtels, scoring
                          |
              Data Lake (AWS S3, fichiers CSV)
                          |
              Data Warehouse (AWS RDS / PostgreSQL)
                          |
              Visualisation (Plotly Express, cartes Mapbox)
```

## Sources de données

| Source | Usage | Accès |
|---|---|---|
| Nominatim (OpenStreetMap) | Coordonnées GPS des villes et des hôtels | Gratuit, sans clé |
| OpenWeatherMap (endpoint forecast 5 j / 3 h) | Température, probabilité et volume de pluie | Clé API gratuite |
| Booking.com | Hôtels : nom, note, lien, description | Scraping Selenium |

## Structure du dépôt

```
Projet-Planifiez votre voyage avec Kayak/
├── README.md
├── requirements.txt
├── .gitignore
├── 01-Plan_your_trip_with_Kayak_Projet.ipynb
├── config/
│   ├── aws.env.example
│   └── openweather.env.example
├── data/
│   ├── villes_coords.csv
│   ├── hotels_booking_35_villes.csv
│   ├── villes_meteo_coords.csv
│   ├── hotels_cleaned_full.csv
│   ├── villes_scores_aggregated.csv
│   └── kayak_final_enriched_data.csv
├── images/
│   ├── Top 5 Destinations.png
│   └── Top 20 Hotels les mieux notes en France.png
└── docs/
    ├── 01-Plan_your_trip_with_Kayak_Projet.html
    ├── Kayak_Story_slides.pptx
    ├── Kayak_Story_slides.pdf
    └── DISCOURS_KAYAK.docx
```

## Installation

```bash
pip install -r requirements.txt
```

Le scraping nécessite Google Chrome installé localement ; le bon pilote est téléchargé automatiquement par `webdriver-manager`.

## Configuration des clés

Les identifiants ne figurent jamais dans le code. Copier les fichiers d'exemple, les renommer sans le suffixe `.example`, et les compléter :

```
config/openweather.env      (OPENWEATHER_API_KEY)
config/aws.env              (clés AWS S3 + RDS)
```

Ces fichiers réels sont exclus du versionnement par le `.gitignore`.

## Exécution

Lancer le notebook `01-Plan_your_trip_with_Kayak_Projet.ipynb` dans l'ordre des sections. Les fichiers de sortie sont écrits automatiquement dans `data/` :

1. Géocodage des 35 villes (Nominatim).
2. Collecte météo (agrégation sur l'horizon de prévision).
3. Scraping des hôtels (Selenium, checkpoint après chaque ville).
4. Nettoyage, géocodage des hôtels, agrégation et calcul du score.
5. Envoi des 4 CSV transformés vers S3.
6. Injection des deux tables dans RDS.
7. Cartes Top 5 destinations et Top 20 hôtels.

## Données produites

| Fichier | Contenu |
|---|---|
| `villes_coords.csv` | 35 villes + coordonnées GPS (données brutes) |
| `hotels_booking_35_villes.csv` | Hôtels scrapés (données brutes) |
| `villes_meteo_coords.csv` | Villes + météo agrégée |
| `hotels_cleaned_full.csv` | Hôtels nettoyés + coordonnées par établissement |
| `villes_scores_aggregated.csv` | Note hôtelière moyenne par ville |
| `kayak_final_enriched_data.csv` | Dataset final enrichi et noté |

## Méthodologie

**Géocodage.** Nominatim convertit chaque nom de ville (et chaque hôtel) en coordonnées GPS, avec une pause d'une seconde par requête pour respecter la limite du service.

**Météo.** L'endpoint gratuit `forecast` renvoie des prévisions sur 5 jours par pas de 3 heures. Plutôt que de retenir un seul créneau, on **agrège l'ensemble de l'horizon** : température moyenne, probabilité de pluie moyenne et volume de pluie cumulé. L'API One Call sur 7 jours étant devenue payante (moyen de paiement requis), ce choix maintient un coût nul tout en répondant à l'exigence du livrable.

**Scraping.** Booking.com chargeant son contenu en JavaScript, `requests` ne suffit pas : Selenium pilote un navigateur Chrome headless, avec défilement progressif pour déclencher le chargement différé et un checkpoint CSV après chaque ville.

**Nettoyage.** Suppression des hôtels sans note, déduplication par couple (nom, ville), et complétion des descriptions manquantes.

## Score de voyage

Chaque critère est ramené sur une échelle commune par normalisation min-max, puis pondéré :

```
travel_score = ( 0,4 x temperature_norm
               + 0,4 x note_hoteliere_norm
               + 0,2 x faible_pluie_norm ) x 100
```

Cette approche évite de mélanger des unités différentes (degrés, notes) et rend la pondération transparente et ajustable.

## Stockage cloud

- **Data Lake (S3) :** les 4 CSV transformés sont déposés dans un bucket, comme couche de stockage brut scalable et peu coûteux.
- **Data Warehouse (RDS / PostgreSQL) :** deux tables relationnelles, `cities` (une ligne par ville) et `hotels` (plusieurs lignes par ville), reliées par la clé `city_id`.

## Visualisations

Deux cartes interactives Plotly Express (fond Mapbox OpenStreetMap) :

- **Top 5 destinations** : couleur selon la température, taille selon le score de voyage.
- **Top 20 hôtels** : positionnés à leurs coordonnées propres, couleur et taille selon la note.

## Conformité au RGPD

Le projet ne collecte aucune donnée personnelle de personne physique. Les données sont publiques et non nominatives (villes, météo, fiches d'établissements). Les principes appliqués : minimisation des champs collectés, protection des clés et identifiants via des fichiers `.env` non versionnés, cadences d'appel raisonnables, et accès restreint à l'infrastructure AWS.

## Limites et perspectives

- Le scraping reste dépendant de la structure de Booking.com et de ses protections anti-robot, ce qui limite le nombre d'hôtels récupérés par ville.
- Le géocodage par nom d'hôtel peut échouer : un repli sur les coordonnées du centre-ville est alors appliqué.
- Perspectives : automatisation hebdomadaire (AWS Lambda + EventBridge), enrichissement du score avec les prix de transport (API SNCF), et intégration du volume de pluie cumulé.

## Stack Technique

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![Selenium](https://img.shields.io/badge/-selenium-%43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)

---

## Certification

> 📊 **Projet de certification — Bloc #1**
>
> Ce projet fait partie des livrables obligatoires pour la validation du **Bloc #1 : Construire et gérer une infrastructure de données** du certificat d'**Ingénieur en Apprentissage Automatique** (Concepteur Développeur en Science des Données).
>
> **Compétences évaluées et validées ici :**
> * Qualité des données extraites du web (Scraping Booking) et transférées vers le Data Lake.
> * Robustesse, efficacité et conformité RGPD du processus ETL (Pandas, Nominatim, OpenWeatherMap).
> * Accessibilité et structuration des données disponibles dans l'entrepôt de données (AWS RDS / PostgreSQL).