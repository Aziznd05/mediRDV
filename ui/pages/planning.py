import streamlit as st
import pandas as pd
from datetime import date, timedelta
from ui import api_client as api


def afficher():
    st.markdown("# 🗓️ Planning des rendez-vous")

    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        jour = st.date_input("Date de début", value=date.today())
    with col2:
        periode = st.selectbox("Période", ["Jour", "Semaine", "Mois"], index=1)
    with col3:
        statut = st.selectbox("Statut", ["Tous", "Planifié", "Confirmé", "Honoré", "Absent", "Annulé"])

    if periode == "Jour":
        date_fin = jour
    elif periode == "Semaine":
        date_fin = jour + timedelta(days=6)
    else:
        date_fin = jour + timedelta(days=29)

    params = {"date_debut": jour, "date_fin": date_fin}
    if statut != "Tous":
        params["statut"] = statut
    rdv = api.get_rdv(**params)

    if "_erreur" in rdv:
        st.error(f"Erreur API : {rdv['_erreur']}")
        return

    if not rdv:
        st.info("Aucun rendez-vous sur cette période.")
        return

    df = pd.DataFrame(rdv)
    st.markdown(f"**{len(df)} rendez-vous** du {jour.strftime('%d/%m')} au {date_fin.strftime('%d/%m')}")

    # Couleur par statut
    def badge(s):
        map_ = {
            "Honoré": "🟢 Honoré",
            "Absent": "🔴 Absent",
            "Annulé": "⚫ Annulé",
            "Confirmé": "🔵 Confirmé",
            "Planifié": "🟡 Planifié",
        }
        return map_.get(s, s)

    df["statut_aff"] = df["statut"].apply(badge)

    st.dataframe(
        df[["id", "date_rdv", "heure_debut", "duree_minutes", "specialite_id",
            "medecin_id", "patient_id", "statut_aff"]].rename(columns={
            "id": "RDV", "date_rdv": "Date", "heure_debut": "Heure",
            "duree_minutes": "Durée (min)", "specialite_id": "Spécialité",
            "medecin_id": "Médecin", "patient_id": "Patient",
            "statut_aff": "Statut",
        }),
        use_container_width=True, hide_index=True,
    )