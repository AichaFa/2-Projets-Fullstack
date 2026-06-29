# Walmart - Prédiction des ventes hebdomadaires

## Présentation

Ce projet construit un modèle de machine learning capable de prédire les ventes hebdomadaires des magasins Walmart à partir d'indicateurs économiques tels que le prix du carburant, le taux de chômage, l'IPC et la température. L'objectif est d'aider l'équipe marketing de Walmart à mieux comprendre les facteurs qui influencent les ventes et à planifier ses futures campagnes.

---

## Structure du projet

Le projet est divisé en trois parties :

- **Partie 1** - Analyse exploratoire des données (EDA) et prétraitement
- **Partie 2** - Régression linéaire (modèle de référence)
- **Partie 3** - Régressions régularisées (Ridge et Lasso) pour réduire le surapprentissage

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
| CPI | Indice des prix à la consommation (IPC) |
| Unemployment | Taux de chômage dans la région |

Volume : 150 observations au départ, 71 après nettoyage (suppression des cibles manquantes puis retrait des valeurs aberrantes), réparties en 56 observations d'entraînement et 15 de test.

---

## Installation

Cloner le dépôt puis installer les dépendances :

```bash
pip install -r requirements.txt
```

**Stack technique :** Python, pandas, NumPy, scikit-learn, Matplotlib, Seaborn.

---

## Utilisation

Ouvrir le notebook et exécuter toutes les cellules dans l'ordre :

```bash
jupyter notebook Walmart_sales_Project.ipynb
```

Le fichier `Walmart_Store_sales.csv` doit se trouver dans le même répertoire que le notebook.

---

## Méthodologie

### Partie 1 - EDA et prétraitement

L'exploration des données comprend l'analyse des distributions, l'évolution temporelle des ventes, la comparaison par magasin et une matrice de corrélation. Les étapes de prétraitement appliquées avec [pandas](https://pandas.pydata.org/) :

- Les lignes où `Weekly_Sales` est manquant sont supprimées (aucune imputation sur la variable cible).
- La colonne `Date` est décomposée en features numériques : `Year`, `Month` et `Day`. La feature `DayOfWeek` est écartée car constante (toutes les observations sont des vendredis, variance nulle).
- Les valeurs aberrantes situées hors de la plage [moyenne - 3 écarts-types, moyenne + 3 écarts-types] sont retirées pour `Temperature`, `Fuel_Price`, `CPI` et `Unemployment`.

Pipeline de prétraitement construit avec [scikit-learn](https://scikit-learn.org/) :

- Les variables catégorielles (`Store`, `Holiday_Flag`) sont encodées avec `OneHotEncoder` (`drop='first'` pour éviter la colinéarité).
- Les variables numériques sont normalisées avec `StandardScaler` : `Temperature`, `Fuel_Price`, `CPI`, `Unemployment`, `Year`, `Month`, `Day`.

### Partie 2 - Régression linéaire

Un modèle `LinearRegression` est entraîné dans un pipeline [scikit-learn](https://scikit-learn.org/). Les performances sont évaluées sur les ensembles d'entraînement et de test via R², MAE et RMSE. Les coefficients sont extraits via l'attribut `.coef_` afin d'identifier les variables les plus importantes.

### Partie 3 - Régression régularisée

Les modèles `Ridge` (pénalité L2) et `Lasso` (pénalité L1) sont entraînés pour réduire le surapprentissage. Le paramètre `alpha` est optimisé pour chaque modèle via `GridSearchCV` avec une validation croisée à 5 plis.

---

## Résultats

| Modèle | R² Train | R² Test | MAE Test | RMSE Test |
|--------|----------|---------|----------|-----------|
| Régression linéaire | 0.9865 | 0.9313 | 127 770 $ | 149 685 $ |
| Ridge (alpha = 0.1) | 0.9821 | 0.9365 | 117 536 $ | 143 863 $ |
| Lasso (alpha = 1000) | 0.9844 | 0.9438 | 114 353 $ | 135 369 $ |

> Résultats obtenus avec `random_state=42`. Les valeurs peuvent légèrement varier selon le volume de données après retrait des valeurs aberrantes.

Le modèle Lasso obtient la meilleure performance en généralisation et effectue une sélection de variables en annulant les coefficients les moins pertinents (ici 2 coefficients sur 26).

---

## Conclusions principales

- L'identifiant du magasin est de loin le facteur le plus déterminant sur les ventes.
- Les ventes affichent une tendance haussière d'une année sur l'autre.
- Un taux de chômage élevé est associé à des ventes plus faibles (effet capté par le coefficient du modèle).
- Une hausse de l'IPC est associée à une baisse des ventes, traduisant une perte de pouvoir d'achat des consommateurs (corrélation la plus élevée parmi les indicateurs économiques : |r| = 0,287).
- Les semaines avec jours fériés génèrent en moyenne 7,5 % de ventes supplémentaires.

> Les corrélations individuelles des indicateurs économiques avec la cible restent faibles (IPC 0,287, température 0,166, chômage 0,055). C'est leur combinaison dans le modèle qui permet de quantifier leur influence respective.

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

## Limites et perspectives

**Limites :**

- Jeu de données réduit (71 observations après nettoyage, dont 15 seulement en test) : les métriques sont indicatives et demandent confirmation sur un volume plus important.
- Le retrait des valeurs aberrantes supprime près de la moitié des observations ; une approche moins destructrice (winsorisation, filtrage par écart interquartile) pourrait être envisagée.
- L'optimum de l'`alpha` du Lasso est atteint au bord de la grille testée ; élargir la recherche (5000, 10000) permettrait de le confirmer.
- La régression linéaire suppose une relation linéaire entre les variables explicatives et la cible.

**Perspectives :**

- Tester des modèles non linéaires (Random Forest, gradient boosting) tout en conservant des outils d'interprétation.
- Enrichir le jeu de données avec des sources externes (météo, évènements locaux).
- Encoder la saisonnalité du mois avec un encodage cyclique (sinus/cosinus).
- Industrialiser le modèle via une API de prédiction et un suivi de la dérive en production.

---

## Références

- [scikit-learn - LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
- [scikit-learn - Ridge](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html)
- [scikit-learn - Lasso](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html)
- [scikit-learn - GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html)

---

## Certification

> Projet réalisé dans le cadre de la validation du **Bloc #3 - Apprentissage automatique** (supervisé et non supervisé), au sein du titre Concepteur Développeur en Science des Données.
>
> **Compétences évaluées :**
>
> - Robustesse de la préparation des données : gestion des valeurs manquantes, encodage One-Hot, normalisation avec StandardScaler et filtrage des valeurs aberrantes.
> - Performance et optimisation des modèles : suivi du R², de la MAE et de la RMSE, optimisation de l'hyperparamètre via GridSearchCV avec validation croisée.
> - Diagnostic du modèle : gestion du surapprentissage et amélioration de la généralisation grâce aux régularisations Ridge et Lasso.
