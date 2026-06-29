# Defi du Taux de Conversion - Data Science Weekly

## Contexte

www.datascienceweekly.org est une newsletter hebdomadaire redigee par des data scientists independants. N'importe qui peut s'inscrire sur le site en indiquant son adresse e-mail pour recevoir chaque semaine des actualites sur la science des donnees.

Les data scientists a l'origine de la newsletter souhaitent mieux comprendre le comportement des visiteurs de leur site. L'objectif est de construire un modele capable de predire si un visiteur va s'abonner a la newsletter, a partir de quelques informations sur son profil et son comportement de navigation.

Ce projet s'inscrit dans le cadre d'une competition de type Kaggle. La metrique imposee pour evaluer les performances est le score F1. Ce choix se justifie par le fort desequilibre des classes du jeu de donnees, rendant une metrique comme l'exactitude (accuracy) trompeuse.

---

## Structure du projet


```

2-defi-du-taux-de-conversion/
│
├── data/
│   ├── conversion_data_train.csv     # Donnees d'entrainement (avec etiquettes)
│   └── conversion_data_test.csv      # Donnees de test (sans etiquettes)
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
├── 02-Conversion_rate_challenge_template.ipynb # Template fourni
├── predictions_soumission.csv                  # Predictions finales a soumettre
└── README.md                                   # Ce fichier

```

---

## Description des donnees

### Jeu d'entrainement : `conversion_data_train.csv`

- Lignes : 284 578 (apres suppression des 2 valeurs aberrantes) x 6 colonnes
- Contient la variable cible : `converted`

### Jeu de test : `conversion_data_test.csv`

- Lignes : 31 620 x 5 colonnes
- Ne contient pas la variable cible (utilise pour generer les predictions finales a soumettre)

### Description des variables

| Variable | Type | Description |
|---|---|---|
| country | Categorielle | Pays du visiteur : China, Germany, UK, US |
| age | Numerique | Age du visiteur (en annees) |
| new_user | Binaire | 1 = nouvel utilisateur, 0 = utilisateur existant |
| source | Categorielle | Source du trafic : Ads, Seo, Direct |
| total_pages_visited | Numerique | Nombre de pages visitees lors de la session |
| converted | Cible (0/1) | 1 = abonne a la newsletter, 0 = non abonne |

---

## Principaux resultats de l'analyse exploratoire (EDA)

### Desequilibre des classes

Le jeu de donnees presente un fort desequilibre :
- Non convertis : 275 400 visiteurs (96,77 %)
- Convertis : 9 178 visiteurs (3,23 %)

Ce desequilibre impose des strategies de modelisation specifiques : l'utilisation du parametre `class_weight='balanced'` pour la regression logistique et les forets aleatoires, tandis que les algorithmes de boosting de gradient adaptent de maniere native leur fonction de perte au fil des iterations.

### Valeurs aberrantes detectees

La variable `age` contenait deux individus avec des valeurs superieures a 100 ans (dont une valeur a 123 ans), ce qui s'apparente a des erreurs manifestes de saisie. Ces observations representant moins de 0,001 % des donnees, elles ont ete retirees du jeu d'entrainement pour ne pas biaiser l'apprentissage des modeles.

### Correlations avec la variable cible

| Variable | Correlation lineaire |
|---|---|
| total_pages_visited | +0,529 |
| country (encode) | +0,077 |
| age | -0,089 |
| new_user | -0,152 |
| source (encode) | -0,003 |

La variable `total_pages_visited` montre la correlation la plus significative avec l'acte d'abonnement.

### Taux de conversion par segment de pages visitees

| Segment | Taux de conversion |
|---|---|
| 1-3 pages | 0,0 % |
| 4-7 pages | 0,3 % |
| 8-15 pages | 10,9 % |
| 16+ pages | 94,3 % |

### Taux de conversion par variable categorielle

Taux par pays :
- Germany : 6,2 %
- UK : 5,2 %
- US : 3,8 %
- China : 0,1 %

Note methodologique : Le taux de la Chine est anormalement bas. Cela suggere une contrainte d'ordre technique ou reglementaire liee a l'infrastructure web locale plutot qu'un desinteret culturel pour la science des donnees.

Taux par source de trafic :
- Ads : 3,5 %
- Seo : 3,3 %
- Direct : 2,8 %

Taux par statut utilisateur :
- Utilisateur existant (new_user=0) : 7,2 %
- Nouvel utilisateur (new_user=1) : 1,4 %

---

## Modelisation et Methodologie

### Pretraitements et Robustesse

Pour garantir la scientificite de la demarche et repondre aux standards RNCP, les regles suivantes ont ete appliquees :
1. Partitionnement des donnees : Division en 80 % pour l'entrainement et 20 % pour la validation, avec une strategie de stratification basee sur la variable cible afin de conserver les proportions initiales de la classe minoritaire.
2. Prevention des fuites d'information (Data Leakage) : L'encodage des variables categorielles via `LabelEncoder` et le calcul des parametres de normalisation via `StandardScaler` ont ete exclusivement calcules (methode `fit`) sur l'ensemble d'entrainement, puis appliques (methode `transform`) sur l'ensemble de validation et de test.
3. Reproductibilite : Toutes les operations impliquant une part de hasard ont ete figees avec la graine de reproductibilite `random_state=42`.

### Performances des modeles sur l'ensemble de validation

| Modele | Score F1 | ROC-AUC |
|---|---|---|
| Regression logistique (baseline) | 0,4969 | 0,9840 |
| Random Forest | 0,5593 | 0,9846 |
| Gradient Boosting | 0,7556 | 0,9856 |

### Hyperparametres du meilleur modele (Gradient Boosting)

```python
GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.8,
    random_state=42
)

```

### Importance des variables (Critere de Gini)

| Variable | Importance relative | Part relative |
| --- | --- | --- |
| total_pages_visited | 0,8741 | 87,6 % |
| new_user | 0,0585 | 5,9 % |
| country | 0,0415 | 4,2 % |
| age | 0,0250 | 2,5 % |
| source | 0,0010 | 0,1 % |

---

## Predictions finales

Apres validation, le modele de Gradient Boosting a ete re-entraine sur l'integralite du jeu de donnees d'entrainement disponible afin de maximiser la quantite d'information utilisee avant la phase de deploiement.

* Fichier produit : `predictions_soumission.csv`
* Volume de lignes : 31 620
* Nombre de conversions predites : 834 (soit un taux de conversion predit de 2,64 %)

---

## Recommandations metier

1. Augmenter la profondeur des sessions utilisateurs (Priorite haute) : La variable liee au nombre de pages visitees represente plus de 87 % de l'importance du modele. Il convient de developper des fonctionnalites favorisant l'engagement (recommandation d'articles croises, apercus de newsletters precedentes) pour inciter le visiteur a franchir le palier des 8 pages, a partir duquel le taux de conversion augmente drastiquement.
2. Mise en place d'actions de reciblage (Priorite haute) : Les utilisateurs deja enregistres convertissent 5 fois plus que les nouveaux visiteurs (7,2 % contre 1,4 %). Un programme de retargeting par e-mail ou sur les reseaux professionnels est fortement conseille.
3. Campagnes ciblees sur les jeunes actifs et etudiants (Priorite moyenne) : La tranche d'age 18-25 ans affiche les meilleurs resultats de conversion. Les partenariats strategiques avec des plateformes d'apprentissage et des formations specialisees en data science constituent un levier d'acquisition optimal.
4. Audit technique sur la region Chine (Priorite basse) : Le taux de 0,1 % necessite une analyse des temps de chargement du site ou des blocages reseaux potentiels afin de verifier si le produit est correctement accessible sur ce marche.

---

## Configuration et Utilisation

### Dependances requises

* pandas
* numpy
* matplotlib
* seaborn
* scikit-learn

Installation des paquets :

```bash
pip install pandas numpy matplotlib seaborn scikit-learn

```

### Executer le projet

1. Deposer les fichiers sources au format CSV dans le repertoire `data/`.
2. Verifier l'existence d'un dossier cree nomme `graphiques/` a la racine du projet pour stocker les visualisations de l'EDA.
3. Executer pas a pas le notebook `02-Conversion_rate_challenge.ipynb` depuis un environnement Jupyter.
4. Le fichier de soumission standardise `predictions_soumission.csv` est genere automatiquement a la racine a la fin du script.

---

## Certification RNCP

> **Projet de certification - Bloc #3**
> Ce livrable repond aux competences obligatoires requises pour la validation du **Bloc #3 : Apprentissage automatique** (supervise et non supervise) du titre d'**Ingenieur en Apprentissage Automatique** (Concepteur Developpeur en Science des Donnees).
> **Competences demontrees et evaluees :**
> * Exploration de donnees (EDA) et ingenierie des variables (Feature Engineering) : Traitement des valeurs aberrantes et encodage isole des variables.
> * Strategie de modelisation predictive complete : Conception d'une solution de reference (baseline) suivie de l'evaluation de modeles d'ensembles complexes (Random Forest et Gradient Boosting).
> * Gestion industrielle du desequilibre de classes : Arbitrage oriente metrique metier par l'optimisation specifique du score F1 et analyse de l'espace de decision grace aux courbes ROC-AUC.
> * Reproductibilite des experiences et structuration de code : Respect des pipelines scikit-learn pour interdire toute fuite d'information.