# Auditeur de Cohérence Médicale

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)

## Présentation du projet

Ce projet vise à renforcer la sécurité des patients en automatisant la vérification de la cohérence entre une **radiographie thoracique** et son **compte rendu radiologique**.

En radiologie, l'image et le texte cheminent séparément dans le système d'information hospitalier ; un compte rendu peut être associé par erreur au mauvais examen. Notre système joue le rôle d'un **filet de sécurité** : il reçoit une paire (image, texte) et estime la probabilité qu'ils décrivent réellement le même examen.

Il ne s'agit pas de poser un diagnostic, mais de fournir un **outil d'audit** qui signale les paires incohérentes pour une revue humaine. L'approche est **multimodale** : le modèle analyse simultanément l'image et le texte.

## Problématique

Le besoin métier (éviter qu'un compte rendu soit rattaché à la mauvaise radiographie) est traduit en un problème de **classification binaire** : pour une paire (image, texte), prédire **cohérent (1)** ou **incohérent (0)**, et restituer un score de cohérence.

## Données

Les sources sont publiques mais volumineuses (plus de 10 Go), elles ne sont donc pas hébergées sur ce dépôt. À télécharger séparément :

- **Images (CheXpert Small)** : https://www.kaggle.com/datasets/mimsadiislam/chexpert
- **Rapports (CheXpert Plus)** : https://stanfordaimi.azurewebsites.net/datasets/5158c524-d3ab-4e02-96e9-6ee9efc110a1
- **Étiquettes de pathologies (CheXbert)** : fichiers JSON fournis avec CheXpert (on utilise `impression_fixed.json`, le plus fiable).

L'alignement entre rapports, images et étiquettes se fait sur le **chemin de l'image** (`path_to_image`), qui identifie de façon unique le patient, l'étude et la vue.

### Respect des données personnelles

Il s'agit de données de santé, utilisées **dé-identifiées** telles que fournies par les organismes sources, exclusivement dans un cadre de recherche et de formation, sans aucune tentative de ré-identification, et selon un principe de minimisation (une seule image par patient).

## Préparation des données

L'étape clé du projet est la construction d'un jeu d'entraînement équilibré.

- **Anti-fuite de données** : on ne conserve qu'une seule image par patient, tirée au hasard, pour éviter que le modèle reconnaisse un patient plutôt que d'apprendre la cohérence.
- **Jeu équilibré** : 18 000 paires cohérentes et 18 000 paires incohérentes, soit 36 000 exemples.
- **Fabrication des incohérences** : les paires cohérentes existent naturellement ; les incohérentes sont fabriquées en échangeant les rapports entre patients, de façon calibrée selon deux dimensions :
  - le **niveau de difficulté** de l'incohérence (Total, Solid, Easy), déterminé en comparant les vecteurs de pathologies ;
  - la **proximité clinique**, via un regroupement des pathologies en quatre familles (coeur, opacités pulmonaires, espace pleural, lésions focales et os), avec des incohérences entre familles différentes ou au sein d'une même famille.
- **Quotas** visés : 40 % Total entre familles, 24 % Solid entre familles, 16 % Easy entre familles, 20 % au sein d'une même famille.

Cette calibration rend la tâche réaliste : le modèle apprend aussi sur des incohérences subtiles, cliniquement proches, et pas seulement sur des erreurs grossières.

## Modélisation

Deux encodeurs médicaux pré-entraînés ont été comparés, du plus simple au plus performant.

### BiomedCLIP (Vision Transformer + PubMedBERT)

Quatre approches de complexité croissante :

- **Similarité cosinus** entre vecteurs globaux d'image et de texte (référence sans apprentissage).
- **Régression logistique** sur un vecteur enrichi (image, texte, différence absolue, produit terme à terme).
- **Attention croisée + MLP** : chaque mot du rapport interroge chaque région de l'image, encodeurs gelés.
- **Ajustement léger par LoRA** : adaptateurs entraînables injectés dans les couches d'attention.

### BioViL-T (CXR-BERT + encodeur image dédié) - modèle retenu

Modèle spécialement conçu pour les radiographies thoraciques et leurs comptes rendus.

- **Similarité cosinus** entre vecteurs globaux.
- **Attention croisée + MLP**, précédée d'une couche de projection qui aligne la dimension des patches d'image sur celle des tokens de texte. C'est la configuration finalement retenue.

## Résultats

- BioViL-T, similarité : ROC-AUC d'environ 0,86, exactitude d'environ 0,78.
- BioViL-T, attention croisée (modèle retenu) : ROC-AUC d'environ 0,95, exactitude d'environ 0,88.

Le gain entre la similarité et l'attention croisée mesure l'apport de la fusion fine entre régions de l'image et mots du rapport. Les scores reflètent une tâche volontairement difficile (incohérences subtiles), donc plus réalistes.

## Application de démonstration

Une interface (MIROIR) permet de charger une paire image-rapport, ou d'en modifier le texte, et d'obtenir en temps réel un score de cohérence et un verdict (MATCH ou MISMATCH) selon un seuil réglable. Elle met en oeuvre le modèle BioViL-T retenu.

- **Démo en ligne** : [Application MIROIR sur Hugging Face Spaces](https://davidformation-demo-fullstack.hf.space/)
- **Vidéo de démonstration** : [Présentation du projet sur YouTube](https://www.youtube.com/watch?v=y1y41r66rJI)

## Organisation locale des fichiers

Le projet est organisé en dossiers numérotés selon les étapes du pipeline. Pour exécuter les notebooks en local, le dossier de travail doit être structuré ainsi :

```
Auditeur_Coherence_Medicale/
├── 1_exploration/                      (notebooks d'exploration, non officiels)
├── 2_preparation_donnees/
│   └── create_dataset_sample.ipynb
├── 3_modelisation/
│   ├── models_biomed_clip.ipynb
│   ├── models_biovil_t.ipynb
│   └── anciennes_versions/
├── 4_application/
│   └── appli_demo_V2.py
├── 5-Presentation/
└── CheXpert/                           (donnees brutes, exclues du depot via .gitignore)
    ├── df_chexpert_plus_240401.csv
    ├── chexbert_labels/
    │   └── impression_fixed.json
    ├── CheXpert-v1.0-small/            (contient les images)
    │   ├── train/
    │   └── valid/
    └── chexpert_plus_dataset_sample.csv   (genere par create_dataset_sample.ipynb)
```

Les jeux de données (CSV des rapports, étiquettes JSON, images) sont à télécharger depuis les sources indiquées plus haut, puis à placer dans le dossier `CheXpert/` comme ci-dessus.

Les notebooks de `2_preparation_donnees/` et `3_modelisation/` étant placés un niveau sous la racine du projet, ils référencent le dossier de données via le chemin relatif `../CheXpert/`. Le jeu de données intermédiaire `chexpert_plus_dataset_sample.csv`, produit par `create_dataset_sample.ipynb`, est écrit et relu depuis ce même dossier `CheXpert/`, afin de rester accessible aux deux notebooks de modélisation malgré le changement de dossier.

## Installation et exécution

Environnement Python (3.10 recommandé) :

```
pip install pandas numpy scikit-learn matplotlib pillow tqdm torch torchvision open_clip_torch transformers peft torchinfo plotly hi-ml-multimodal
```

Ordre d'exécution des notebooks :

1. `2_preparation_donnees/create_dataset_sample.ipynb` : construit le jeu de données (préparation et fabrication des incohérences).
2. `3_modelisation/models_biomed_clip.ipynb` : modélisation BiomedCLIP (les quatre approches).
3. `3_modelisation/models_biovil_t.ipynb` : modélisation BioViL-T (similarité puis attention croisée, modèle retenu).

Chaque notebook doit être exécuté depuis son propre dossier (kernel Jupyter démarré dans `2_preparation_donnees/` ou `3_modelisation/` selon le cas), pour que les chemins relatifs vers `../CheXpert/` soient résolus correctement.

Une carte graphique compatible accélère fortement l'entraînement et l'extraction des caractéristiques ; à défaut, l'exécution sur processeur reste possible mais nettement plus longue.

## Limites et perspectives

- Les incohérences sont fabriquées artificiellement : soignées, mais elles ne couvrent pas toute la diversité des erreurs réelles.
- Le périmètre est restreint à une image par patient.
- Le système est une aide à la décision, il ne remplace pas le radiologue.

Pistes d'amélioration : fabriquer des incohérences encore plus subtiles à l'aide de modèles de langage ou d'outils d'extraction comme RadGraph ; ajouter une carte d'attention (Grad-CAM) surlignant les régions décisives ; valider sur de vraies erreurs annotées par des radiologues.

## Équipe

Projet réalisé en équipe par Aïcha Fathellah, David Herbez, Samer Mechhour et Sohaib El Maaroufi.

---

## Certification

> **Projet de certification — Bloc 6**
>
> Ce projet fait partie des livrables mobilisés pour la validation du **Bloc 6 : concevoir et déployer une solution d'intelligence artificielle**.
>
> **Compétences mises en œuvre dans ce projet :**
> - Exploration et comparaison rigoureuse de plusieurs approches de modélisation multimodale (similarité, régression logistique, attention croisée, ajustement par LoRA).
> - Évaluation reproductible des modèles : seuils calculés sur l'entraînement seul, métriques de classification complètes, arrêt anticipé pour éviter le sur-apprentissage.
> - Déploiement d'une démonstration interactive en production (Streamlit, Hugging Face Spaces, suivi des expériences via MLflow).
