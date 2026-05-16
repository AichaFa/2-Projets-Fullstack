# Défi du Taux de Conversion - Data Science Weekly

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat-square&logo=matplotlib&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-4C9BE8?style=flat-square&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)

## Contexte

www.datascienceweekly.org est une newsletter hebdomadaire rédigée par des data scientists indépendants. N'importe qui peut s'inscrire sur le site en indiquant son adresse e-mail pour recevoir chaque semaine des actualités sur la science des données.

Les data scientists à l'origine de la newsletter souhaitent mieux comprendre le comportement des visiteurs de leur site. L'objectif est de construire un modèle capable de prédire si un visiteur va s'abonner à la newsletter, à partir de quelques informations sur son profil et son comportement de navigation.

Ce projet s'inscrit dans le cadre d'une compétition de type Kaggle. La métrique imposée pour évaluer les performances est le **score F1**.

---

## Structure du projet

```
2-défi-du-taux-de-conversion/
│
├── data/
│   ├── conversion_data_train.csv     # Données d'entraînement (avec étiquettes)
│   └── conversion_data_test.csv      # Données de test (sans étiquettes)
│
├── graphiques/
│   ├── fig_01_distribution_cible.png
│   ├── fig_02_distribution_numeriques.png
│   ├── fig_03_taux_conversion_categoriel.png
│   ├── fig_04_matrice_correlation.png
│   ├── fig_05_pages_vs_conversion.png
│   ├── fig_06_confusion_lr.png
│   ├── fig_07_confusion_rf.png
│   ├── fig_08_confusion_gb.png
│   ├── fig_09_comparaison_modeles.png
│   ├── fig_10_courbes_roc.png
│   ├── fig_11_importance_variables.png
│   └── fig_12_leviers_conversion.png
│
├── 02-Conversion_rate_challenge.ipynb          # Notebook principal
├── 02-Conversion_rate_challenge_template.ipynb # Template fourni par le professeur
├── predictions_soumission.csv                  # Prédictions finales à soumettre
└── README.md                                   # Ce fichier
```

---

## Description des données

### Jeu d'entraînement : `conversion_data_train.csv`

- **284 578 lignes** (après suppression des 2 valeurs aberrantes) x 6 colonnes
- Contient la variable cible `converted`

### Jeu de test : `conversion_data_test.csv`

- **31 620 lignes** x 5 colonnes
- Ne contient pas la variable cible — utilisé pour générer les prédictions finales

### Description des variables

| Variable | Type | Description |
|---|---|---|
| `country` | Catégorielle | Pays du visiteur : China, Germany, UK, US |
| `age` | Numérique | Âge du visiteur (en années) |
| `new_user` | Binaire | 1 = nouvel utilisateur, 0 = utilisateur existant |
| `source` | Catégorielle | Source du trafic : Ads, Seo, Direct |
| `total_pages_visited` | Numérique | Nombre de pages visitées lors de la session |
| `converted` | **Cible** (0/1) | 1 = abonné à la newsletter, 0 = non abonné |

---

## Principaux résultats de l'analyse exploratoire (EDA)

### Déséquilibre des classes

Le jeu de données est fortement déséquilibré :

- Non convertis : 275 400 visiteurs (96,8 %)
- Convertis : 9 178 visiteurs (3,2 %)

Ce déséquilibre impose l'utilisation du paramètre `class_weight='balanced'` dans tous les modèles.

### Valeur aberrante détectée

La variable `age` contient 2 lignes avec un âge supérieur à 100 ans (dont une à 123 ans), clairement une erreur de saisie. Ces lignes ont été supprimées (moins de 0,001 % des données).

### Corrélations avec la variable cible

| Variable | Corrélation |
|---|---|
| `total_pages_visited` | +0,529 |
| `country` (encodé) | +0,077 |
| `age` | -0,089 |
| `new_user` | -0,152 |
| `source` (encodé) | -0,003 |

`total_pages_visited` est de loin la variable la plus corrélée avec la conversion.

### Taux de conversion par segment de pages visitées

| Segment | Taux de conversion |
|---|---|
| 1-3 pages | 0,0 % |
| 4-7 pages | 0,3 % |
| 8-15 pages | 10,9 % |
| 16+ pages | 94,3 % |

### Taux de conversion par variable catégorielle

**Par pays :**

| Pays | Taux |
|---|---|
| Germany | 6,2 % |
| UK | 5,2 % |
| US | 3,8 % |
| China | 0,1 % |

Note : le taux de la Chine (0,1 %) est très probablement lié à des contraintes d'accès à internet, et non à un comportement utilisateur.

**Par source de trafic :**

| Source | Taux |
|---|---|
| Ads | 3,5 % |
| Seo | 3,3 % |
| Direct | 2,8 % |

**Par statut utilisateur :**

| Statut | Taux |
|---|---|
| Utilisateur existant (new_user=0) | 7,2 % |
| Nouvel utilisateur (new_user=1) | 1,4 % |

Les utilisateurs existants convertissent 5 fois plus que les nouveaux visiteurs.

---

## Modélisation

### Prétraitement

- Encodage des variables catégorielles `country` et `source` via `LabelEncoder`
- Le `fit` est réalisé uniquement sur les données d'entraînement pour éviter toute fuite d'information vers le test
- Division train/validation : 80 % / 20 %, stratifiée sur la variable cible
- Normalisation via `StandardScaler` pour la régression logistique uniquement

### Modèles entraînés et performances sur la validation

| Modèle | Score F1 | ROC-AUC |
|---|---|---|
| Régression logistique (baseline) | 0,4969 | 0,9840 |
| Random Forest | 0,5593 | 0,9846 |
| **Gradient Boosting** | **0,7556** | **0,9856** |

### Paramètres du meilleur modèle : Gradient Boosting

```python
GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.8,
    random_state=42
)
```

### Importance des variables (Gradient Boosting - critère de Gini)

| Variable | Importance | Part |
|---|---|---|
| `total_pages_visited` | 0,8741 | 87,4 % |
| `new_user` | 0,0585 | 5,9 % |
| `country` | 0,0415 | 4,2 % |
| `age` | 0,0250 | 2,5 % |
| `source` | 0,0010 | 0,1 % |

---

## Prédictions finales

Le Gradient Boosting a été ré-entraîné sur la totalité des données d'entraînement avant de générer les prédictions sur le jeu de test, afin de maximiser la quantité d'information disponible.

- Fichier de sortie : `predictions_soumission.csv`
- Nombre de prédictions : 31 620
- Conversions prédites : 834 (2,64 %)

---

## Recommandations métier

**1. Augmenter le nombre de pages visitées par session** - priorité haute

C'est le levier le plus puissant (87,4 % de l'importance du modèle). Mettre en place des liens recommandés, une sidebar d'articles récents et des aperçus de numéros précédents pour inciter les visiteurs à explorer davantage de contenu. Au-delà de 15 pages visitées, le taux de conversion atteint 94,3 %.

**2. Cibler les utilisateurs existants via le retargeting** - priorité haute

Les visiteurs déjà connus convertissent 5 fois plus que les nouveaux (7,2 % contre 1,4 %). Mettre en place des mécanismes de reciblage pour inciter les visiteurs à revenir sur le site.

**3. Concentrer les campagnes sur la tranche 18-25 ans** - priorité moyenne

Cette tranche d'âge présente le meilleur taux de conversion (5,1 %). Elle correspond à des étudiants et jeunes professionnels actifs dans la data science. Cibler les partenariats avec des bootcamps et formations.

**4. Investiguer l'accessibilité du site en Chine** - priorité basse

Le taux de conversion de 0,1 % en Chine est très probablement lié à des contraintes techniques ou réglementaires (accès internet), et non à un manque d'intérêt pour le contenu.

---

## Dépendances

```
pandas
numpy
matplotlib
seaborn
scikit-learn
```

Installation :

```bash
pip install pandas numpy matplotlib seaborn scikit-learn
```

## Utilisation

1. Placer les fichiers CSV dans le dossier `data/`
2. Créer un dossier `graphiques/` à la racine du projet
3. Ouvrir et exécuter `02-Conversion_rate_challenge.ipynb` dans Jupyter
4. Le fichier `predictions_soumission.csv` est généré automatiquement à la racine du projet
