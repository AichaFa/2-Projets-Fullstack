# Plan your trip with Kayak

Pipeline ETL complet qui recommande les **5 meilleures destinations** et les **20 meilleurs hotels** en France, en combinant des donnees meteorologiques et hotelieres collectees automatiquement, puis stockees sur une infrastructure cloud AWS.

## Contexte et objectif

L'equipe marketing souhaite un outil de recommandation de destinations base sur des donnees reelles. Aucune base n'existant au depart, le projet collecte, nettoie, stocke et restitue les donnees de bout en bout :

- coordonnees geographiques des villes,
- previsions meteorologiques,
- offre hoteliere (nom, note, lien, description).

Le perimetre couvre les 35 villes francaises imposees par le cahier des charges.

## Architecture du pipeline

```
Geocodage (Nominatim)
        |
   API Meteo (OpenWeatherMap)        Scraping hotels (Selenium / Booking.com)
        |                                         |
        +---------------- ETL (Pandas) -----------+
                          |
              Nettoyage, geocodage des hotels, scoring
                          |
              Data Lake (AWS S3, fichiers CSV)
                          |
              Data Warehouse (AWS RDS / PostgreSQL)
                          |
              Visualisation (Plotly Express, cartes Mapbox)
```

## Sources de donnees

| Source | Usage | Acces |
|---|---|---|
| Nominatim (OpenStreetMap) | Coordonnees GPS des villes et des hotels | Gratuit, sans cle |
| OpenWeatherMap (endpoint forecast 5 j / 3 h) | Temperature, probabilite et volume de pluie | Cle API gratuite |
| Booking.com | Hotels : nom, note, lien, description | Scraping Selenium |

## Structure du depot

```
.
├── README.md
├── requirements.txt
├── .gitignore
├── 01-Plan_your_trip_with_Kayak_Projet.ipynb
├── 01-Plan_your_trip_with_Kayak_Projet.html
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
│   ├── top5_destinations.png
│   ├── top20_hotels.png
│   └── workflow_kayak.jpg
└── docs/
    └── Kayak_Story_slides.pptx
```

## Installation

```bash
pip install -r requirements.txt
```

Le scraping necessite Google Chrome installe localement ; le bon pilote est telecharge automatiquement par `webdriver-manager`.

## Configuration des cles

Les identifiants ne figurent jamais dans le code. Copier les fichiers d'exemple, les renommer sans le suffixe `.example`, et les completer :

```
config/openweather.env      (OPENWEATHER_API_KEY)
config/aws.env              (cles AWS S3 + RDS)
```

Ces fichiers reels sont exclus du versionnement par le `.gitignore`.

## Execution

Lancer le notebook `01-Plan_your_trip_with_Kayak_Projet.ipynb` dans l'ordre des sections. Les fichiers de sortie sont ecrits automatiquement dans `data/` :

1. Geocodage des 35 villes (Nominatim).
2. Collecte meteo (agregation sur l'horizon de prevision).
3. Scraping des hotels (Selenium, checkpoint apres chaque ville).
4. Nettoyage, geocodage des hotels, agregation et calcul du score.
5. Envoi des 4 CSV transformes vers S3.
6. Injection des deux tables dans RDS.
7. Cartes Top 5 destinations et Top 20 hotels.

## Donnees produites

| Fichier | Contenu |
|---|---|
| `villes_coords.csv` | 35 villes + coordonnees GPS (donnees brutes) |
| `hotels_booking_35_villes.csv` | Hotels scrapes (donnees brutes) |
| `villes_meteo_coords.csv` | Villes + meteo agregee |
| `hotels_cleaned_full.csv` | Hotels nettoyes + coordonnees par etablissement |
| `villes_scores_aggregated.csv` | Note hoteliere moyenne par ville |
| `kayak_final_enriched_data.csv` | Dataset final enrichi et scored |

## Methodologie

**Geocodage.** Nominatim convertit chaque nom de ville (et chaque hotel) en coordonnees GPS, avec une pause d'une seconde par requete pour respecter la limite du service.

**Meteo.** L'endpoint gratuit `forecast` renvoie des previsions sur 5 jours par pas de 3 heures. Plutot que de retenir un seul creneau, on **agrege l'ensemble de l'horizon** : temperature moyenne, probabilite de pluie moyenne et volume de pluie cumule. L'API One Call sur 7 jours necessitant desormais un moyen de paiement enregistre, ce choix maintient un cout nul.

**Scraping.** Booking.com chargeant son contenu en JavaScript, `requests` ne suffit pas : Selenium pilote un navigateur Chrome headless, avec scroll progressif pour declencher le chargement differe et un checkpoint CSV apres chaque ville.

**Nettoyage.** Suppression des hotels sans note, deduplication par couple (nom, ville), et completion des descriptions manquantes.

## Score de voyage

Chaque critere est ramene sur une echelle commune par normalisation min-max, puis pondere :

```
travel_score = ( 0,4 x temperature_norm
               + 0,4 x note_hoteliere_norm
               + 0,2 x faible_pluie_norm ) x 100
```

Cette approche evite de melanger des unites differentes (degres, notes) et rend la ponderation transparente et ajustable.

## Stockage cloud

- **Data Lake (S3) :** les 4 CSV transformes sont deposes dans un bucket, comme couche de stockage brut scalable et peu couteux.
- **Data Warehouse (RDS / PostgreSQL) :** deux tables relationnelles, `cities` (une ligne par ville) et `hotels` (plusieurs lignes par ville), reliees par la cle `city_id`.

## Visualisations

Deux cartes interactives Plotly Express (fond Mapbox OpenStreetMap) :

- **Top 5 destinations** : couleur selon la temperature, taille selon le score de voyage.
- **Top 20 hotels** : positionnes a leurs coordonnees propres, couleur et taille selon la note.

## Conformite au RGPD

Le projet ne collecte aucune donnee personnelle de personne physique. Les donnees sont publiques et non nominatives (villes, meteo, fiches d'etablissements). Les principes appliques : minimisation des champs collectes, protection des cles et identifiants via des fichiers `.env` non versionnes, cadences d'appel raisonnables, et acces restreint a l'infrastructure AWS.

## Limites et perspectives

- Le scraping reste dependant de la structure de Booking.com et de ses protections anti-bot.
- Le geocodage par nom d'hotel peut echouer : un repli sur les coordonnees du centre-ville est alors applique.
- Perspectives : automatisation hebdomadaire (AWS Lambda + EventBridge), enrichissement du score avec les prix de transport (API SNCF), et integration du volume de pluie cumule.
