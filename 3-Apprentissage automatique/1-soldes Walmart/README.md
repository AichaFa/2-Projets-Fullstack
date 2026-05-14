# Walmart - Prédiction des ventes hebdomadaires

## Présentation

Ce projet consiste à construire un modèle de machine learning capable de prédire les ventes hebdomadaires des magasins Walmart en fonction d'indicateurs économiques tels que le prix du carburant, le taux de chômage, le CPI et la température. L'objectif est d'aider l'équipe marketing de Walmart à mieux comprendre les facteurs qui influencent les ventes et à planifier ses futures campagnes.

---

## Structure du projet

Le projet est divisé en trois parties :

- **Partie 1** - Analyse exploratoire des données (EDA) et prétraitement
- **Partie 2** - Modèle de régression linéaire (baseline)
- **Partie 3** - Modèles de régression régularisés (Ridge et Lasso) pour réduire l'overfitting

---

## Jeu de données

Le jeu de données contient les ventes hebdomadaires de plusieurs magasins Walmart ainsi que les variables suivantes :

| Colonne | Description |
|---------|-------------|
| Store | Identifiant du magasin |
| Date | Semaine concernée |
| Weekly_Sales | Variable cible - ventes hebdomadaires en dollars |
| Holiday_Flag | Indique si la semaine contient un jour férié |
| Temperature | Température moyenne dans la région |
| Fuel_Price | Prix du carburant dans la région |
| CPI | Indice des prix à la consommation |
| Unemployment | Taux de chômage dans la région |

---

## Installation

Cloner le dépôt puis installer les dépendances :

```bash
pip install -r requirements.txt
```

**Stack technique :**

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge&logo=matplotlib&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-4C72B0?style=for-the-badge&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

---

## Utilisation

Ouvrir le notebook et exécuter toutes les cellules dans l'ordre :

```bash
jupyter notebook Walmart_sales_solution.ipynb
```

Le fichier `Walmart_Store_sales.csv` doit se trouver dans le même répertoire que le notebook.

---

## Méthodologie

### Partie 1 - EDA et prétraitement

L'exploration des données comprend l'analyse des distributions, l'évolution temporelle des ventes, la comparaison par magasin et une heatmap de corrélation. Les étapes de prétraitement appliquées avec [pandas](https://pandas.pydata.org/) :

- Les lignes où `Weekly_Sales` est manquant sont supprimées (pas d'imputation sur la variable cible)
- La colonne `Date` est décomposée en features numériques : `Year`, `Month` et `Day`. La feature `DayOfWeek` est écartée car constante (toutes les observations sont des vendredis - variance nulle)
- Les outliers hors de la plage [moyenne - 3 écarts-types, moyenne + 3 écarts-types] sont retirés pour `Temperature`, `Fuel_Price`, `CPI` et `Unemployment`

Pipeline de prétraitement construit avec [scikit-learn](https://scikit-learn.org/) :

- Les variables catégorielles (`Store`, `Holiday_Flag`) sont encodées avec `OneHotEncoder`
- Les variables numériques sont normalisées avec `StandardScaler` : `Temperature`, `Fuel_Price`, `CPI`, `Unemployment`, `Year`, `Month`, `Day`

### Partie 2 - Régression linéaire

Un modèle `LinearRegression` est entraîné dans un Pipeline [scikit-learn](https://scikit-learn.org/). Les performances sont évaluées sur les ensembles d'entraînement et de test via R², MAE et RMSE. Les coefficients sont extraits via l'attribut `.coef_` afin d'identifier les features les plus importantes.

### Partie 3 - Régression régularisée

Les modèles `Ridge` (pénalisation L2) et `Lasso` (pénalisation L1) sont entraînés pour réduire l'overfitting. Le paramètre `alpha` est optimisé pour chaque modèle via `GridSearchCV` avec une validation croisée à 5 folds.

---

## Résultats

| Modèle | R² Train | R² Test | MAE Test | RMSE Test |
|--------|----------|---------|----------|-----------|
| Régression Linéaire | 0.9865 | 0.9313 | 127 770 $ | 149 685 $ |
| Ridge (alpha = 0.1) | 0.9821 | 0.9365 | 117 536 $ | 143 863 $ |
| Lasso (alpha = 1000) | 0.9844 | 0.9438 | 114 353 $ | 135 369 $ |

Le modèle Lasso obtient les meilleures performances en généralisation et effectue une sélection automatique de variables en annulant les coefficients les moins pertinents.

---

## Conclusions principales

- L'identifiant du magasin est de loin le facteur le plus déterminant sur les ventes
- Les ventes affichent une tendance haussière d'une année sur l'autre
- Un taux de chômage élevé est associé à des ventes plus faibles
- Une hausse de l'IPC (Indice des Prix à la Consommation) est associée à une baisse des ventes, traduisant une perte de pouvoir d'achat des consommateurs (corrélation la plus élevée parmi les indicateurs économiques : |r| = 0,287)
- Les semaines avec jours fériés génèrent en moyenne 7,5 % de ventes supplémentaires

---

## Implications pour le service marketing

Le modèle quantifie l'influence des indicateurs économiques et permet de formuler des recommandations opérationnelles directes :

| Indicateur | Signal détecté | Recommandation |
|------------|---------------|----------------|
| **Holiday_Flag** | +7,5 % de ventes sur les semaines de fêtes | Concentrer les budgets promotionnels sur ces périodes ; planifier les campagnes en avance |
| **CPI** | Coefficient négatif - hausse de l'IPC = baisse des ventes | Renforcer les offres de fidélisation et les promotions défensives lors des phases d'inflation |
| **Unemployment** | Coefficient négatif - chômage élevé = ventes faibles | Adapter la stratégie promotionnelle par zone géographique ; intensifier les offres dans les bassins d'emploi fragilisés |

> Aucun indicateur n'agit seul. Le modèle capture leur influence combinée : une campagne optimale devra croiser ces signaux simultanément.

---

## Références

- [scikit-learn - LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
- [scikit-learn - Ridge](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html)
- [scikit-learn - Lasso](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html)
- [scikit-learn - GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html)
