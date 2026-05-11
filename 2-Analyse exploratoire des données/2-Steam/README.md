# Projet Steam - Analyse exploratoire de la plateforme de jeux vidéo

## Contexte

Analyse exploratoire complète (EDA) des jeux disponibles sur Steam, réalisée pour le compte d'**Ubisoft** afin d'orienter la stratégie de lancement d'un nouveau jeu vidéo.

Projet réalisé dans le cadre de la certification **CSDS - Jedha Bootcamp - Mai 2026**.

---

## Dataset

| Propriété | Valeur |
|-----------|--------|
| Source | AWS S3 |
| URL | `s3://full-stack-bigdata-datasets/Big_Data/Project_Steam/steam_game_output.json` |
| Format | JSON semi-structuré (schéma imbriqué) |
| Volume | 55 690 jeux après filtrage |

---

## Stack technique

`PySpark 4.1` - `Databricks Free Edition` - `AWS S3`

---

## Structure du projet

```
2-Steam/
├── Project_Steam_part1.html   - Notebook 1 : Analyse Macro
├── Project_Steam_part2.html   - Notebook 2 : Genres et Plateformes
└── archive/                   - Fichiers de travail (ipynb)
```

---

## Consulter les notebooks

### Fichiers HTML (recommandé)
- [Notebook 1 - Analyse Macro](./Project_Steam_part1.html)
- [Notebook 2 - Genres et Plateformes](./Project_Steam_part2.html)

### Liens Databricks (accès workspace personnel)
- [Notebook 1 - Databricks](https://dbc-d23f2ffb-9f5f.cloud.databricks.com/editor/notebooks/3659326689703957?o=7474656704147178#command/7337978027093016)
- [Notebook 2 - Databricks](https://dbc-d23f2ffb-9f5f.cloud.databricks.com/editor/notebooks/3659326689703959?o=7474656704147178#command/7337978027093036)

> Note : les liens Databricks nécessitent un accès au workspace. Privilégier les fichiers HTML.
### Apercu du schema des donnees dans Databricks
![Schema Databricks](./images/databricks_schema.png)
---

## Résultats clés

### Macro
| Indicateur | Résultat |
|------------|----------|
| Éditeur le plus prolifique | Big Fish Games - 422 jeux |
| Ubisoft | 9ème éditeur - 127 jeux |
| Année record | 2021 - 8 823 sorties |
| Langue dominante | English - 55 116 jeux |
| Jeux tous publics | 98.8% des jeux |

### Genres
| Indicateur | Résultat |
|------------|----------|
| Genre le plus représenté | Indie - 38 000+ jeux (marché saturé) |
| Genre le plus lucratif | Action - 3 milliards de propriétaires |
| Meilleur ratio d'avis | Game Development - 82% |

### Plateformes
| Plateforme | Part du marché |
|------------|---------------|
| Windows | 98% |
| Mac | 24% |
| Linux | 19% |

---

## Recommandations pour Ubisoft

- **Genre** : Action / Adventure - le plus lucratif avec 3 milliards de propriétaires
- **Plateforme** : Windows en priorité, Mac recommandé pour se différencier
- **Prix** : Entre 10 et 20 euros - zone optimale du marché
- **Langues** : EN + DE + FR + RU
