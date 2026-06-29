# Speed Dating Analysis - Qu'est-ce qui déclenche l'étincelle ?

Analyse exploratoire des données de l'expérience de speed dating de l'Université Columbia (2002-2004), appliquée à la stratégie produit de Tinder.

## Contexte

L'équipe marketing de Tinder a observé une baisse du nombre de matchs et a commandé cette étude pour comprendre **ce qui attire les gens les uns vers les autres**.
Le dataset couvre **8 378 rencontres** entre participants qui se sont notés sur 6 critères et ont indiqué s'ils souhaitaient un second rendez-vous.

## Dataset

- **Source :** Columbia University Speed Dating Experiment (2002-2004)
- **Lignes :** 8 378 rencontres (une ligne = un speed date entre deux personnes)
- **Colonnes :** 195 variables (démographie, auto-perception, notes, style de vie)
- **Variable cible :** `match` - 1 si les deux ont dit oui (taux moyen : **16,5 %**)

[Download CSV](https://full-stack-assets.s3.eu-west-3.amazonaws.com/M03-EDA/Speed+Dating+Data.csv) | [Data Dictionary](https://full-stack-assets.s3.eu-west-3.amazonaws.com/M03-EDA/Speed+Dating+Data+Key.doc)

## Questions de recherche

| # | Question |
|---|----------|
| Q1 | Quels sont les critères les moins désirables chez un partenaire ? Cela diffère-t-il selon le genre ? |
| Q2 | Quelle importance les gens accordent-ils à l'attractivité par rapport à son impact réel ? |
| Q3 | Les intérêts communs comptent-ils plus que la même origine raciale ? |
| Q4 | Les gens peuvent-ils estimer correctement leur valeur perçue sur le marché des rencontres ? |
| Q5 | Vaut-il mieux être le premier ou le dernier speed date de la soirée ? |

## Résultats clés

- **L'attractivité domine** (corr = 0.49) : le critère le plus prédictif, pourtant sous-déclaré (moyenne déclarée : 22.5/100). Biais de désirabilité sociale confirmé.
- **L'humour et les intérêts communs suivent** (corr = 0.41 et 0.40) : des signaux actionnables pour un algorithme de matching.
- **Les intérêts communs l'emportent sur l'origine raciale** par 3x : +3.3 pts de taux de match contre +1.0 pt.
- **L'auto-perception est peu fiable** : surestimation de l'attractivité de +0.9 pt, de la sincérité de +1.13 pt. Corrélation auto-note / note réelle = **0.175**.
- **La fatigue décisionnelle se confirme, avec un effet modéré** : le taux d'acceptation décline régulièrement au fil de la soirée, de 43.2 % (1er tiers) à 39.2 % (3e tiers), soit environ -4 pts ; l'écart est de -3.6 pts entre le tout premier et le tout dernier rendez-vous de la soirée. La corrélation position/décision reste faible (-0.03).

## Recommandations pour Tinder

1. **Valoriser la photo** - l'attractivité est le premier filtre ; aider les utilisateurs à choisir leur meilleure photo.
2. **Algorithme Passions** - pondérer les tags d'intérêts dans le matching (signal 3x plus fort que l'origine raciale).
3. **Limiter les swipes par session** - lutter contre la fatigue décisionnelle via une limite quotidienne ou des pauses suggérées.
4. **Calibration de profil** - un feedback anonymisé aide les utilisateurs à aligner leurs attentes sur la réalité du marché.

## Structure du projet

```
.
├── 01-Speed_Dating.ipynb          # Notebook d'analyse principal (EDA + visualisations)
├── Speed_Dating_Storytelling.pdf  # Présentation executive (5 slides)
└── README.md
```

## Stack Technique

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-%2311557c.svg?style=for-the-badge&logo=python&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-%234C72B0.svg?style=for-the-badge&logo=python&logoColor=white)

---

## Certification

> 📊 **Projet de certification — Bloc #2**
>
> Ce projet fait partie des livrables obligatoires pour la validation du **Bloc #2 : Analyse exploratoire des données** du certificat d'**Ingénieur en Apprentissage Automatique** (Concepteur Développeur en Science des Données).
>
> **Compétences évaluées et validées ici :**
> * Pertinence de la méthodologie de nettoyage et de préparation des données (gestion des valeurs manquantes, types de données).
> * Choix et efficacité des analyses statistiques effectuées (analyses univariées, distributions, matrices de corrélation de Pearson).
> * Clarté, simplicité des graphiques construits et pertinence business des recommandations formulées.
