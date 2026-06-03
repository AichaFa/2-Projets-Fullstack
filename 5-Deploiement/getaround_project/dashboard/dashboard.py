"""
Tableau de bord - Analyse des retards Getaround
================================================
Application Streamlit permettant à l'équipe Produit d'explorer les
données de retard et de simuler l'impact d'un seuil de délai minimum
entre deux locations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Chemin portable : relatif au fichier source.
# Fonctionne depuis n'importe quel répertoire courant (Windows, Linux,
# macOS, Docker, Hugging Face Spaces).
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "get_around_delay_analysis.xlsx"

# Repli : si les données ne sont pas embarquées dans le dossier dashboard
# (cas d'un développement local avec un dossier data partagé à la racine
# du projet), on remonte d'un cran.
if not DATA_FILE.exists():
    DATA_FILE = BASE_DIR.parent / "data" / "get_around_delay_analysis.xlsx"

# ===========================================================================
# Configuration
# ===========================================================================
st.set_page_config(
    page_title="Getaround - Tableau de bord des retards",
    page_icon="G",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSS = """
<style>
    .main { background-color: #f8fafc; }
    .stMetric { background: white; padding: 16px; border-radius: 10px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
    h1 { color: #1e293b; font-weight: 700; }
    h2, h3 { color: #334155; }
    .section-card { background: white; padding: 24px; border-radius: 12px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 24px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ===========================================================================
# Chargement des données
# ===========================================================================
@st.cache_data
def load_data():
    df = pd.read_excel(DATA_FILE)
    return df


@st.cache_data
def prepare_chained(df):
    prev_info = df[["rental_id", "delay_at_checkout_in_minutes", "state"]].rename(
        columns={"rental_id": "previous_ended_rental_id",
                 "delay_at_checkout_in_minutes": "previous_delay",
                 "state": "previous_state"}
    )
    chained = df.dropna(subset=["previous_ended_rental_id"]).merge(
        prev_info, on="previous_ended_rental_id", how="left"
    )
    chained_full = chained.dropna(subset=["previous_delay"]).copy()
    chained_full["impact_minutes"] = (
        chained_full["previous_delay"]
        - chained_full["time_delta_with_previous_rental_in_minutes"]
    )
    chained_full["problematic"] = chained_full["impact_minutes"] > 0
    chained_full["previous_was_late"] = chained_full["previous_delay"] > 0
    return chained_full


df = load_data()
chained_full = prepare_chained(df)


# ===========================================================================
# Barre latérale - paramètres globaux
# ===========================================================================
st.sidebar.title("Paramètres de simulation")
st.sidebar.markdown("---")

scope = st.sidebar.radio(
    "Périmètre de la fonctionnalité",
    ["Toutes les voitures", "Connect uniquement", "Mobile uniquement"]
)

threshold = st.sidebar.slider(
    "Seuil minimum entre deux locations (minutes)",
    min_value=0, max_value=720, value=60, step=15
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filtrage de l'analyse")

show_outliers = st.sidebar.checkbox(
    "Afficher les valeurs aberrantes (retards extrêmes)", value=False
)


# ===========================================================================
# Filtrage selon le périmètre
# ===========================================================================
if scope == "Connect uniquement":
    scope_df = chained_full[chained_full["checkin_type"] == "connect"]
    scope_label = "Connect"
elif scope == "Mobile uniquement":
    scope_df = chained_full[chained_full["checkin_type"] == "mobile"]
    scope_label = "Mobile"
else:
    scope_df = chained_full
    scope_label = "Tous"


# ===========================================================================
# En-tête
# ===========================================================================
st.title("Tableau de bord - Analyse des retards Getaround")
st.markdown(
    "**Objectif** : aider l'équipe Produit à arbitrer entre la réduction des "
    "frictions liées aux retards et la préservation du chiffre d'affaires "
    "des propriétaires."
)
st.markdown("---")


# ===========================================================================
# Indicateurs clés
# ===========================================================================
st.subheader("Indicateurs clés du parc")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Locations totales", f"{len(df):,}".replace(",", " "))
with col2:
    end_pct = (df["state"] == "ended").mean() * 100
    st.metric("Taux d'achèvement", f"{end_pct:.1f}%")
with col3:
    delays = df[df["state"] == "ended"]["delay_at_checkout_in_minutes"].dropna()
    late_pct = (delays > 0).mean() * 100
    st.metric("Restitutions en retard", f"{late_pct:.1f}%")
with col4:
    chain_pct = len(chained_full) / len(df) * 100
    st.metric("Locations chaînées", f"{chain_pct:.1f}%")


# ===========================================================================
# Section 1 - Répartition des restitutions
# ===========================================================================
st.markdown("---")
st.subheader("1. Répartition des retards à la restitution")

col1, col2 = st.columns(2)
with col1:
    delays_df = df[df["state"] == "ended"].dropna(
        subset=["delay_at_checkout_in_minutes"]
    ).copy()

    def categorize(d):
        if d < 0:
            return "En avance"
        elif d == 0:
            return "À l'heure"
        elif d <= 30:
            return "Retard 0-30 min"
        elif d <= 60:
            return "Retard 30-60 min"
        elif d <= 120:
            return "Retard 1-2 h"
        elif d <= 360:
            return "Retard 2-6 h"
        else:
            return "Retard > 6 h"

    delays_df["categorie"] = delays_df["delay_at_checkout_in_minutes"].apply(categorize)
    order = ["En avance", "À l'heure", "Retard 0-30 min", "Retard 30-60 min",
             "Retard 1-2 h", "Retard 2-6 h", "Retard > 6 h"]
    cat_counts = delays_df["categorie"].value_counts().reindex(order)

    colors = ["#10b981", "#3b82f6", "#facc15", "#f97316", "#ef4444",
              "#dc2626", "#7f1d1d"]
    fig = go.Figure(go.Bar(
        x=order, y=cat_counts.values, marker_color=colors,
        text=[f"{int(v):,}".replace(",", " ") for v in cat_counts.values],
        textposition="outside"
    ))
    fig.update_layout(
        title="Répartition des restitutions par tranche de délai",
        xaxis_title="Catégorie", yaxis_title="Nombre de locations",
        template="plotly_white", height=380
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    if show_outliers:
        hist_data = delays_df["delay_at_checkout_in_minutes"]
        x_range = None
    else:
        hist_data = delays_df["delay_at_checkout_in_minutes"]
        x_range = [-300, 600]

    fig = px.histogram(
        delays_df, x="delay_at_checkout_in_minutes", color="checkin_type",
        nbins=80, color_discrete_map={"mobile": "#4C72B0", "connect": "#DD8452"},
        title="Distribution des délais par type de check-in",
        labels={"delay_at_checkout_in_minutes": "Délai (minutes)",
                "checkin_type": "Type"}
    )
    fig.add_vline(x=0, line_dash="dash", line_color="red")
    if x_range:
        fig.update_xaxes(range=x_range)
    fig.update_layout(template="plotly_white", height=380, barmode="overlay")
    fig.update_traces(opacity=0.7)
    st.plotly_chart(fig, use_container_width=True)


# ===========================================================================
# Section 2 - Impact des retards sur les locations chaînées
# ===========================================================================
st.markdown("---")
st.subheader("2. Impact des retards sur les locations chaînées")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Chaînages analysés (périmètre)", f"{len(scope_df):,}".replace(",", " "))
with col2:
    prob = int(scope_df["problematic"].sum())
    pct = prob / len(scope_df) * 100 if len(scope_df) else 0
    st.metric("Cas problématiques", f"{prob} ({pct:.1f}%)")
with col3:
    if scope_df["problematic"].sum():
        impact_med = scope_df.loc[scope_df["problematic"], "impact_minutes"].median()
        st.metric("Attente médiane (cas problématiques)", f"{impact_med:.0f} min")
    else:
        st.metric("Attente médiane", "N/A")

# Graphique : taux de problème selon le time_delta prévu
bins = [0, 30, 60, 120, 180, 360, 540, 720]
labels_b = ["0-30 min", "30-60 min", "1-2 h", "2-3 h", "3-6 h", "6-9 h", "9-12 h"]
scope_df_v = scope_df.copy()
scope_df_v["delta_cat"] = pd.cut(
    scope_df_v["time_delta_with_previous_rental_in_minutes"],
    bins=bins, labels=labels_b, include_lowest=True
)
prob_by_delta = scope_df_v.groupby("delta_cat", observed=True)["problematic"].agg(
    ["mean", "count"]
).reset_index()
prob_by_delta["pct"] = prob_by_delta["mean"] * 100

fig = go.Figure()
fig.add_trace(go.Bar(
    x=prob_by_delta["delta_cat"].astype(str),
    y=prob_by_delta["pct"],
    marker_color="#dc2626",
    text=[f"{v:.1f}%" for v in prob_by_delta["pct"]],
    textposition="outside",
    name="Taux de cas problématiques"
))
fig.update_layout(
    title=f"Taux de cas problématiques selon l'écart prévu entre locations - {scope_label}",
    xaxis_title="Écart prévu entre les deux locations",
    yaxis_title="% de cas problématiques",
    template="plotly_white", height=400
)
st.plotly_chart(fig, use_container_width=True)


# ===========================================================================
# Section 3 - Simulation du seuil
# ===========================================================================
st.markdown("---")
st.subheader("3. Simulation de l'impact du seuil choisi")

# Calculs pour le seuil sélectionné
blocked = (scope_df["time_delta_with_previous_rental_in_minutes"] < threshold).sum()
total_scope = len(scope_df)
prob_total = scope_df["problematic"].sum()
prob_solved = (
    (scope_df["time_delta_with_previous_rental_in_minutes"] < threshold)
    & scope_df["problematic"]
).sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        "Locations bloquées",
        f"{blocked}",
        f"{blocked/total_scope*100:.1f}% des chaînages" if total_scope else ""
    )
with col2:
    rev_impact = blocked / len(df) * 100
    st.metric("Part du CA impactée", f"{rev_impact:.2f}%")
with col3:
    st.metric(
        "Cas problématiques résolus",
        f"{prob_solved}",
        f"{prob_solved/prob_total*100:.1f}%" if prob_total else "N/A"
    )
with col4:
    if blocked:
        ratio = prob_solved / blocked * 100
        st.metric("Efficacité (résolus / bloqués)", f"{ratio:.1f}%")
    else:
        st.metric("Efficacité", "N/A")

# Courbe interactive
thresholds_range = list(range(0, 721, 15))
sim_data = []
for t in thresholds_range:
    b = (scope_df["time_delta_with_previous_rental_in_minutes"] < t).sum()
    s = ((scope_df["time_delta_with_previous_rental_in_minutes"] < t)
         & scope_df["problematic"]).sum()
    sim_data.append({
        "seuil": t,
        "pct_bloquees": b / total_scope * 100 if total_scope else 0,
        "pct_resolus": s / prob_total * 100 if prob_total else 0,
        "ca_impacte": b / len(df) * 100
    })
sim_df = pd.DataFrame(sim_data)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=sim_df["seuil"], y=sim_df["pct_bloquees"],
    mode="lines+markers", name="% chaînages bloqués",
    line=dict(color="#ef4444", width=3)
))
fig.add_trace(go.Scatter(
    x=sim_df["seuil"], y=sim_df["pct_resolus"],
    mode="lines+markers", name="% cas problématiques résolus",
    line=dict(color="#10b981", width=3)
))
fig.add_trace(go.Scatter(
    x=sim_df["seuil"], y=sim_df["ca_impacte"],
    mode="lines+markers", name="% du CA total impacté",
    line=dict(color="#f59e0b", width=3, dash="dash")
))
fig.add_vline(x=threshold, line_dash="dot", line_color="black",
              annotation_text=f"Seuil actuel : {threshold} min",
              annotation_position="top right")
fig.update_layout(
    title=f"Arbitrage : protection vs revenus - {scope_label}",
    xaxis_title="Seuil de délai minimum (minutes)",
    yaxis_title="Pourcentage",
    template="plotly_white", height=450
)
st.plotly_chart(fig, use_container_width=True)


# ===========================================================================
# Section 4 - Tableau récapitulatif des scénarios
# ===========================================================================
st.markdown("---")
st.subheader("4. Tableau récapitulatif - scénarios usuels")

scenarios = [15, 30, 60, 90, 120, 180, 240]
rows = []
for t in scenarios:
    row = {"Seuil (min)": t}
    for sname, sdf in [("Tous", chained_full),
                       ("Connect", chained_full[chained_full["checkin_type"] == "connect"]),
                       ("Mobile", chained_full[chained_full["checkin_type"] == "mobile"])]:
        b = (sdf["time_delta_with_previous_rental_in_minutes"] < t).sum()
        s = ((sdf["time_delta_with_previous_rental_in_minutes"] < t)
             & sdf["problematic"]).sum()
        pt = sdf["problematic"].sum()
        row[f"{sname} - bloqués"] = b
        row[f"{sname} - % résolus"] = f"{s/pt*100:.1f}%" if pt else "N/A"
    rows.append(row)

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ===========================================================================
# Section 5 - Recommandations
# ===========================================================================
st.markdown("---")
st.subheader("5. Recommandations")

st.markdown("""
<div class="section-card">

**Synthèse des analyses**

- Le retard à la restitution est un phénomène courant : environ **57 % des
  conducteurs rendent leur véhicule en retard** sur l'ensemble du parc.
- Les locations chaînées (8,6 % des locations) sont la principale source de
  friction : dans **12,6 % des cas**, le retard du conducteur précédent dépasse
  l'écart prévu entre les deux locations, ce qui provoque une attente directe.
- Le canal **Connect** présente un comportement plus discipliné (retard médian
  négatif) que le canal **Mobile**.

**Recommandation produit**

Sur la base de l'arbitrage entre revenus préservés et frictions résolues, un
seuil de **120 minutes** appliqué à l'ensemble du parc résout environ 80 % des
cas problématiques tout en n'impactant que ~3 % du chiffre d'affaires. Cette
combinaison constitue un point d'équilibre raisonnable.

Si l'équipe Produit souhaite minimiser l'impact business, un seuil de **60 à
90 minutes appliqué uniquement aux voitures Connect** constitue une alternative
prudente, avec moins de 1 % du CA impacté pour 70 à 80 % des cas problématiques
de ce segment résolus.

</div>
""", unsafe_allow_html=True)
