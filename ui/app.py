import sys
from pathlib import Path

# Ajoute la racine du projet (medirdv/) au chemin Python
RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import streamlit as st
from ui.theme import injecter_css, COULEURS
from ui.views import dashboard, planning, prise_rdv, patients

st.set_page_config(
    page_title="MédiRDV — Clinique Les Baobabs",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

injecter_css()

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding: 20px 0;">
        <div style="font-size: 3rem;">🏥</div>
        <h2 style="color:{COULEURS['vert_fonce']}; margin: 8px 0 4px 0;">MédiRDV</h2>
        <p style="color:{COULEURS['gris']}; font-size: 0.85rem; margin: 0;">
        Clinique Les Baobabs<br>Dakar, Sénégal
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["📊 Tableau de bord", "🗓️ Planning", "➕ Prise de RDV", "👥 Patients"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    st.markdown(f"""
    <div style="font-size: 0.75rem; color: {COULEURS['gris']}; text-align: center;">
        Version 1.0.0<br>
        <em>AO-CLB-2026-01</em>
    </div>
    """, unsafe_allow_html=True)

# --- Routage ---
if page == "📊 Tableau de bord":
    dashboard.afficher()
elif page == "🗓️ Planning":
    planning.afficher()
elif page == "➕ Prise de RDV":
    prise_rdv.afficher()
elif page == "👥 Patients":
    patients.afficher()