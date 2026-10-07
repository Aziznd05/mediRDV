import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta
from ui import api_client as api
from ui.theme import carte_kpi, COULEURS


def afficher():
    st.markdown("# 📊 Tableau de bord")
    st.markdown(f"*Vue d'ensemble — {date.today().strftime('%A %d %B %Y')}*")

    # --- KPI Cards ---
    kpis = api.get_kpis()
    if "_erreur" in kpis:
        st.error(f"Impossible de charger les KPIs : {kpis['_erreur']}")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        carte_kpi("RDV aujourd'hui", kpis["rdv_aujourdhui"], f"{kpis['planifies_aujourdhui']} planifiés", "bleu")
    with c2:
        carte_kpi("Honorés", kpis["honores_aujourdhui"], "sur la journée", "vert")
    with c3:
        carte_kpi("Absents", kpis["absents_aujourdhui"], "sur la journée", "rouge")
    with c4:
        taux = kpis["taux_absence_30j"]
        couleur = "rouge" if taux > 14 else "orange" if taux > 11 else "vert"
        carte_kpi("Taux absence 30j", f"{taux}%", "objectif : ≤ 11%", couleur)

    st.markdown("---")

    # --- Heatmap + Top spécialités ---
    col_g, col_d = st.columns([2, 1])

    with col_g:
        st.markdown("### 🗓️ Répartition jour × heure")
        hm = api.get_heatmap()
        if "_erreur" not in hm and hm:
            jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
            matrice = pd.DataFrame(0, index=jours, columns=range(8, 19))
            for cle, val in hm.items():
                j, h = cle.split("-")
                j = int(j); h = int(h)
                if j < 6 and 8 <= h < 19:
                    matrice.iloc[j, h - 8] = val

            fig = px.imshow(
                matrice,
                labels=dict(x="Heure", y="", color="Nb RDV"),
                color_continuous_scale=[[0, "#F8F9FA"], [0.3, "#D1E7DD"], [0.6, "#198754"], [1, "#0F5132"]],
                aspect="auto", text_auto=True,
            )
            fig.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor="white",
                coloraxis_colorbar=dict(title="RDV", thickness=12),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_d:
        st.markdown("### 🩺 Top spécialités")
        spe = api.get_specialites_stats()
        if "_erreur" not in spe and spe:
            df = pd.DataFrame(spe).head(6)
            fig = px.bar(
                df, x="total", y="nom", orientation="h",
                color="total",
                color_continuous_scale=["#D1E7DD", "#198754", "#0F5132"],
            )
            fig.update_layout(
                height=350, showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10),
                yaxis=dict(categoryorder="total ascending", title=""),
                xaxis=dict(title=""),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig, use_container_width=True)

    # --- Évolution mensuelle ---
    st.markdown("---")
    st.markdown("### 📈 Évolution mensuelle")
    ev = api.get_evolution()
    if "_erreur" not in ev and ev:
        df = pd.DataFrame(ev)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df["mois"], y=df["total"],
            name="Total RDV",
            marker_color=COULEURS["vert"],
        ))
        fig.add_trace(go.Scatter(
            x=df["mois"], y=df["absents"],
            name="Absents", mode="lines+markers",
            line=dict(color=COULEURS["rouge"], width=3),
        ))
        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white",
            hovermode="x unified",
            legend=dict(orientation="h", y=-0.2),
        )
        st.plotly_chart(fig, use_container_width=True)