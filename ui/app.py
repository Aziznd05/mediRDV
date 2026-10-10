import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import streamlit as st
from ui.theme import injecter_css, COULEURS
from ui.views import dashboard, planning, prise_rdv, patients, login

st.set_page_config(
    page_title="MédiRDV — Clinique Les Baobabs",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

injecter_css()

# --- Garde d'authentification ---
if "token" not in st.session_state:
    login.afficher()
    st.stop()

# --- Sidebar ---
with st.sidebar:

      # Logo clinique
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.image(str(logo_path), use_container_width=True)

    st.markdown(f"""
    <div style="text-align:center; margin-bottom: 20px;">
        <h2 style="color:{COULEURS['vert_fonce']}; margin: 8px 0 4px 0; font-size: 1.4rem;">MédiRDV</h2>
        <p style="color:{COULEURS['gris']}; font-size: 0.8rem; margin: 0;">
        Clinique Les Baobabs<br>Dakar, Sénégal
        </p>
    </div>
    """, unsafe_allow_html=True)
  
    st.markdown("---")

    st.markdown(f"""
    <div style="background-color: {COULEURS['vert_clair']}; padding: 10px 14px; border-radius: 10px; margin-bottom: 12px;">
        <div style="font-size: 0.7rem; color: {COULEURS['gris']}; text-transform: uppercase;">Connecté</div>
        <div style="font-weight: 700; color: {COULEURS['vert_fonce']};">{st.session_state.get('username', '?')}</div>
        <div style="font-size: 0.75rem; color: {COULEURS['gris']}; text-transform: capitalize;">{st.session_state.get('role', '?')}</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [" Tableau de bord", "Planning", " Prise de RDV", "Patients"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    if st.button(" Se déconnecter", use_container_width=True):
        for k in ["token", "role", "username"]:
            st.session_state.pop(k, None)
        st.rerun()

    st.markdown(f"""
    <div style="font-size: 0.75rem; color: {COULEURS['gris']}; text-align: center; margin-top: 12px;">
        Version 1.0.0<br>
        <em>AO-CLB-2026-01</em>
    </div>
    """, unsafe_allow_html=True)


# --- Routage ---
if page == " Tableau de bord":
    dashboard.afficher()
elif page == " Planning":
    planning.afficher()
elif page == " Prise de RDV":
    prise_rdv.afficher()
elif page == " Patients":
    patients.afficher()