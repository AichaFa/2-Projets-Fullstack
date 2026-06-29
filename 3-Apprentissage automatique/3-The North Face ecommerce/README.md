# The North Face - Commerce électronique : dynamiser les ventes en ligne

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=flat-square&logo=jupyter&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.x-013243?style=flat-square&logo=numpy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
![spaCy](https://img.shields.io/badge/spaCy-3.x-09A3D5?style=flat-square&logo=spacy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.x-11557C?style=flat-square&logo=matplotlib&logoColor=white)
![License](https://img.shields.io/badge/Licence-MIT-green?style=flat-square)

---

## Présentation du projet

**The North Face** est une entreprise américaine spécialisée dans les articles de loisirs de plein air, fondée en 1968. Ce projet applique des techniques de **machine learning non supervisé** au catalogue de produits de leur site e-commerce afin de dynamiser les ventes en ligne à travers deux leviers principaux :

- Un **système de recommandation** suggérant des produits similaires à l'utilisateur ("Vous aimerez aussi...")
- Une **extraction de thèmes latents** pour challenger et enrichir la structure du catalogue

---

## Objectifs

| # | Objectif | Méthode |
|---|----------|---------|
| 1 | Identifier des groupes de produits aux descriptions similaires | DBSCAN + distance cosinus |
| 2 | Suggérer des produits complémentaires à un utilisateur | Système de recommandation basé sur les clusters |
| 3 | Extraire les thèmes latents des descriptions | LSA / TruncatedSVD |

---

## Structure du projet

```
.
├── 02-The_North_Face_ecommerce.ipynb   # Notebook principal
├── sample-data.csv                      # Catalogue de 500 produits
├── wordclouds_clusters.png              # Visualisation des clusters DBSCAN
├── wordclouds_topics.png                # Visualisation des thèmes LSA
├── lsa_variance.png                     # Graphique de variance expliquée
└── README.md
```

---

## Données

Le corpus est constitué de **500 descriptions de produits** du catalogue The North Face, issues du fichier `sample-data.csv` (deux colonnes : `id` et `description`).

Les descriptions sont au format HTML brut et contiennent des informations sur les matériaux, les usages, les caractéristiques techniques et les spécifications de chaque article.

---

## Pipeline technique

```
Données brutes (HTML)
        │
        ▼
Prétraitement spaCy
  ├── Suppression des balises HTML
  ├── Lemmatisation (token.lemma_)
  └── Suppression des stop words (token.is_stop)
        │
        ▼
Vectorisation TF-IDF
  ├── max_features = 5 000
  ├── min_df = 2  /  max_df = 0.90
  └── ngram_range = (1, 2)
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
Clustering DBSCAN               Modélisation LSA
(Partie 1 & 2)                    (Partie 3)
```

---

## Partie 1 - Clustering DBSCAN

L'algorithme **DBSCAN** (Density-Based Spatial Clustering of Applications with Noise) est appliqué sur la matrice TF-IDF avec la **distance cosinus**, particulièrement adaptée aux données textuelles.

### Paramètres

```python
DBSCAN(
    eps=0.72,
    min_samples=3,
    metric='cosine',
    algorithm='brute'
)
```

### Résultats

| Indicateur | Valeur |
|------------|--------|
| Nombre de clusters | **14** |
| Taux d'outliers | **4.4%** |
| Max produits / cluster | 242 |
| Min produits / cluster | 3 |

### Wordclouds des clusters

![Wordclouds par cluster DBSCAN](wordclouds_clusters.png)

Chaque nuage de mots révèle la thématique dominante d'un cluster : sous-vêtements techniques, vestes alpines, laine mérinos, chaussures, sacs à dos, etc.

---

## Partie 2 - Système de recommandation

La fonction `find_similar_items` exploite les clusters DBSCAN pour proposer les **5 produits les plus similaires** à un article donné, triés par **similarité cosinus décroissante** au sein du même cluster.

```python
def find_similar_items(item_id, dataframe=df, matrix=tfidf_matrix, n_recommendations=5):
    """
    Retourne les n produits les plus similaires au produit spécifié,
    triés par similarité cosinus décroissante au sein du même cluster.
    """
```

### Fonctionnement

1. Identifier le cluster DBSCAN du produit consulté
2. Calculer la similarité cosinus entre ce produit et tous ses voisins du même cluster
3. Retourner les 5 produits par ordre décroissant de similarité

> **Avantage clé :** le tri par similarité cosinus garantit que les recommandations sont les plus pertinentes du cluster — pas tirées au hasard.

Une interface utilisateur interactive est disponible via `input()` dans le notebook.

---

## Partie 3 - Modélisation thématique (LSA)

L'**Analyse Sémantique Latente (LSA)** utilise `TruncatedSVD` pour extraire des thèmes latents dans les descriptions. Contrairement au clustering, un produit peut être associé à **plusieurs thèmes simultanément**.

```python
N_COMPONENTS = 15

svd = TruncatedSVD(n_components=N_COMPONENTS, random_state=42)
normalizer = Normalizer(copy=True)
lsa_pipeline = make_pipeline(svd, normalizer)

topic_encoded_df = lsa_pipeline.fit_transform(tfidf_matrix)
```

### Résultats

| Indicateur | Valeur |
|------------|--------|
| Nombre de thèmes extraits | **15** |
| Variance totale expliquée | **26%** |
| Matrice résultante | `topic_encoded_df` (500 × 15) |

### Variance expliquée et wordclouds des thèmes

![Variance expliquée LSA](lsa_variance.png)

![Wordclouds par thème LSA](wordclouds_topics.png)

Les thèmes identifiés couvrent : coton organique, imperméabilité DWR, laine mérinos, spandex/nylon, chaussures, sacs à dos, protection solaire, polaire hydrostorm, etc.

---

## Installation

### Prérequis

```bash
pip install pandas numpy scikit-learn spacy wordcloud matplotlib
python -m spacy download en_core_web_sm
```

### Lancer le notebook

```bash
jupyter notebook 02-The_North_Face_ecommerce.ipynb
```

---

## Librairies utilisées

| Librairie | Usage |
|-----------|-------|
| `pandas` | Chargement et manipulation des données |
| `numpy` | Calculs matriciels |
| `re` | Nettoyage des balises HTML |
| `spacy` | Lemmatisation et suppression des stop words |
| `sklearn.TfidfVectorizer` | Vectorisation TF-IDF |
| `sklearn.DBSCAN` | Clustering |
| `sklearn.cosine_similarity` | Calcul de similarité |
| `sklearn.TruncatedSVD` | Décomposition LSA |
| `sklearn.Normalizer` | Normalisation L2 |
| `matplotlib` | Visualisations |
| `wordcloud` | Nuages de mots |

---

## Résultats clés

- **14 clusters sémantiques** cohérents identifiés avec seulement 4.4% d'outliers
- **Système de recommandation** opérationnel, triés par similarité cosinus décroissante
- **15 thèmes latents** extraits, sauvegardés dans `topic_encoded_df`
- Les deux approches (clustering et LSA) sont complémentaires : le clustering assigne chaque produit à un seul groupe, tandis que la LSA offre une représentation multi-thèmes plus nuancée

---

## Auteur

Projet réalisé dans le cadre d'une formation en Data Science.

## Stack Technique

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.x-013243?style=for-the-badge&logo=numpy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![spaCy](https://img.shields.io/badge/spaCy-3.x-09A3D5?style=for-the-badge&logo=spacy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.x-11557C?style=for-the-badge&logo=matplotlib&logoColor=white)

---

## Certification

> **Projet de certification — Bloc #3**
>
> Ce projet fait partie des livrables obligatoires pour la validation du **Bloc #3 : Apprentissage automatique** (supervisé et non supervisé) du certificat d'**Ingénieur en Apprentissage Automatique** (Concepteur Développeur en Science des Données).
>
> **Compétences évaluées et validées ici :**
> * Conception d'un pipeline de préparation de données textuelles (NLP) pour l'apprentissage des algorithmes (nettoyage HTML, lemmatisation spaCy, vectorisation TF-IDF).
> * Qualité de l'optimisation et pertinence du clustering non supervisé (sélection de l'Epsilon pour DBSCAN avec distance cosinus et réduction du taux d'outliers).
> * Performance de l'algorithme programmé et extraction sémantique multi-thèmes via décomposition LSA (TruncatedSVD et normalisation L2).