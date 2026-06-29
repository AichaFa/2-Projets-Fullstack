# AT&T Spam Detector - Detection de SMS frauduleux par Deep Learning

## Presentation du projet
Ce projet consiste a developper un outil de classification de texte automatise et scalable pour AT&T Inc., leader mondial des telecommunications. L'objectif est d'identifier et de filtrer en temps reel les messages indesarables (spams/phishing) des leur reception afin de securiser les utilisateurs et de soulager le processus de signalement manuel.

Le projet met en concurrence deux approches d'apprentissage profond (Deep Learning) appliquees au Traitement du Langage Naturel (NLP) : une architecture recurrente personnalisee et une approche moderne par transfert d'apprentissage.

---

## Jeu de donnees
Le modele est entraine sur un corpus de 5 572 messages bruts (reduits a 5 169 exemples uniques apres elimination des doublons).
* Repartition initiale : 87,37 % de messages legitimes (Ham) et 12,63 % de messages frauduleux (Spam).
* Pretraitement : Nettoyage textuel, tokenisation, application d'un decoupage stratifie (Train 80% / Test 20%) pour maintenir la proportion de spams, et mise en correspondance des longueurs par rembourrage (padding).

---

## Modeles et approches de Deep Learning

1. Modele 1 - Architecture sur-mesure (Embedding + BiLSTM)
   * Principe : Une couche d'apprentissage d'incorporation de mots (Embedding Layer) pour capter le vocabulaire propre aux SMS, couplee a un reseau recurrent bidirectionnel (BiLSTM) pour apprehender les dependances sequentielles du texte dans les deux sens de lecture.
   * Avantage : Infrastructure legere, vitesse d'inference tres rapide, ideal pour un deploiement sur serveurs de production standards sans GPU obligatoire.

2. Modele 2 - Transfert d'Apprentissage (DistilBERT)
   * Principe : Utilisation du modele de langage pre-entraine de pointe DistilBERT (issu de la bibliotheque Transformers d'Hugging Face) avec ajout d'une tete de classification dediee, affinee (fine-tuned) sur notre base de SMS.
   * Avantage : Comprehension semantique et contextuelle extremement poussee du langage humain, maximisant le pouvoir de discrimination.

---

## Resultats et Performances

Les performances mesurees sur le jeu de test independant (1 034 messages) revelent d'excellents scores :

| Metrique | Modele 1 (Embedding + BiLSTM) | Modele 2 (DistilBERT fine-tuned) |
|---|---|---|
| Precision globale (Accuracy) | 98,36 % | 98,26 % |
| Score F1 (Classe Spam) | 93,33 % | 92,91 % |
| Aire sous la courbe (AUC-ROC) | 98,40 % | 99,37 % |
| Seuil de decision optimise | 0,50 | 0,60 |

Recommandation operationnelle : Le Modele 2 (DistilBERT) offre la meilleure capacite de generalisation globale (AUC-ROC de 99,37 %). Cependant, si AT&T priorise une latence d'inference ultra-faible et un cout d'infrastructure minimal, le Modele 1 est immediatement deployable sur leurs architectures CPU actuelles.

---

## Stack Technique

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Transformers-Hugging%20Face-FFD21E?style=for-the-badge)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?style=for-the-badge&logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

---

## Certification

> 🕵️‍♂️ **Projet de certification — Bloc #4**
>
> Ce projet fait partie des livrables obligatoires pour la validation du **Bloc #4 : Apprentissage profond** (Deep Learning) du certificat d'**Ingénieur en Apprentissage Automatique** (*Concepteur Développeur en Science des Données — Certification RNCP de Niveau 7*).
>
> **Compétences évaluées et validées ici :**
> * Capacité à structurer, nettoyer et vectoriser des séquences textuelles complexes pour des réseaux de neurones (Tokenization, Padding, Tenseurs).
> * Conception, entraînement et régularisation d'une architecture de réseau récurrent bidirectionnel sur-mesure (Embedding + BiLSTM).
> * Implémentation d'une stratégie moderne de transfert d'apprentissage via un modèle de type Transformer (Fine-tuning de DistilBERT avec Hugging Face).
> * Optimisation des métriques de classification en environnement déséquilibré (Ajustement du seuil critique de décision, analyse des courbes AUC-ROC et F1-Score).
>
