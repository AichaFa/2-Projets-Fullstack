# 💘 Speed Dating Analysis — What Sparks the Connection?

Exploratory data analysis of the Columbia University speed dating experiment (2002–2004), applied to Tinder product strategy.

## Context

Tinder's marketing team observed a decrease in matches and commissioned this study to understand **what makes people interested in each other**.  
The dataset covers **8,378 speed dates** between participants who rated each other on 6 attributes and indicated whether they'd want a second date.

## Dataset

- **Source:** Columbia University Speed Dating Experiment (2002–2004)
- **Rows:** 8,378 encounters (one row = one speed date between two people)
- **Columns:** 195 variables (demographics, self-perception, ratings, lifestyle)
- **Target variable:** `match` — 1 if both agreed to a second date (avg. rate: **16%**)

📥 [Download CSV](https://full-stack-assets.s3.eu-west-3.amazonaws.com/M03-EDA/Speed+Dating+Data.csv) | [Data Dictionary](https://full-stack-assets.s3.eu-west-3.amazonaws.com/M03-EDA/Speed+Dating+Data+Key.doc)

## Research Questions

| # | Question |
|---|----------|
| Q1 | What are the least desirable attributes in a partner? Does this differ by gender? |
| Q2 | How important do people *think* attractiveness is vs. its *real* impact? |
| Q3 | Are shared interests more important than shared racial background? |
| Q4 | Can people accurately predict their own perceived value on the dating market? |
| Q5 | Is it better to be someone's first speed date of the night or their last? |

## Key Findings

- **Attractiveness dominates** (corr = 0.49): the strongest predictor of a yes, yet people under-report its importance (declared avg: 22.5/100). Classic social desirability bias.
- **Humor and shared interests follow** (corr = 0.41 and 0.40): actionable signals for a matching algorithm.
- **Shared interests beat shared race** by 3×: +3.3 pts of match rate vs. +1.0 pt.
- **Self-perception is unreliable**: participants overestimate their attractiveness by +0.9 pt, sincerity by +1.1 pt. Correlation between self-rating and actual rating = **0.175**.
- **Decision fatigue is real**: acceptance rate drops from 43.2% (early dates) to 39.6% (late dates) — a −3.6 pt penalty for being seen last.

## Recommendations for Tinder

1. **Boost photo quality** — attractiveness is the #1 filter; help users pick their best photo.
2. **Passion-based algorithm** — weight shared interest tags in matching (3× stronger signal than race).
3. **Limit swipes per session** — combat decision fatigue by introducing daily limits or suggested breaks.
4. **Profile calibration** — anonymized feedback helps users align expectations with market reality.

## Project Structure

```
.
├── 01-Speed_Dating.ipynb       # Main analysis notebook (EDA + visualizations)
├── Speed_Dating_Storytelling.pdf  # Executive presentation (5 slides)
└── README.md
```

## Stack

- Python 3.10
- pandas, numpy — data manipulation
- matplotlib, seaborn — visualizations

## Certification

⚠️ This project is part of the mandatory deliverables for **Bloc #2** certification.
