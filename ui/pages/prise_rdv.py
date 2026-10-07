import streamlit as st
import pandas as pd
from datetime import date, timedelta
from ui import api_client as api


def afficher():
    st.markdown("# ➕ Prise de rendez-vous")

    # Étape 1 : Recherche de créneau
    st.markdown("### 1️⃣ Rechercher un créneau libre")

    col1, col2, col3 = st.columns(3)
    with col1:
        medecin_id = st.number_input("ID Médecin", min_value=1, value=1, step=1)
    with col2:
        date_debut = st.date_input("À partir du", value=date.today())
    with col3:
        nb_jours = st.slider("Sur X jours", 1, 30, 7)

    if st.button("🔍 Chercher les créneaux libres", type="primary"):
        creneaux = api.chercher_creneaux(medecin_id, date_debut, nb_jours)
        if "_erreur" in creneaux:
            st.error(f"Erreur : {creneaux['_erreur']}")
        elif not creneaux:
            st.warning("Aucun créneau libre trouvé sur cette période.")
        else:
            st.session_state["creneaux"] = creneaux

    if "creneaux" in st.session_state and st.session_state["creneaux"]:
        df = pd.DataFrame(st.session_state["creneaux"])
        df["creneau"] = df["date_rdv"] + " — " + df["heure_debut"]
        choix = st.selectbox("Créneaux disponibles", df["creneau"].tolist())
        idx = df[df["creneau"] == choix].index[0]
        creneau_choisi = st.session_state["creneaux"][idx]

        st.markdown("### 2️⃣ Confirmer le rendez-vous")

        with st.form("form_rdv"):
            c1, c2 = st.columns(2)
            with c1:
                patient_id = st.number_input("ID Patient", min_value=1, value=1)
                specialite_id = st.number_input("ID Spécialité", min_value=1, value=2)
            with c2:
                canal = st.selectbox("Canal", ["Téléphone", "Guichet", "Recommandation médecin"])
                agent = st.text_input("Agent de saisie", value="AGT01")

            soumis = st.form_submit_button("✅ Créer le rendez-vous", type="primary")

            if soumis:
                data = {
                    "patient_id": patient_id,
                    "medecin_id": creneau_choisi["medecin_id"],
                    "specialite_id": specialite_id,
                    "date_rdv": creneau_choisi["date_rdv"],
                    "heure_debut": creneau_choisi["heure_debut"],
                    "duree_minutes": creneau_choisi["duree_minutes"],
                    "canal": canal,
                    "agent_saisie": agent,
                }
                res = api.creer_rdv(data)
                if "_erreur" in res:
                    st.error(f"❌ {res['_erreur']}")
                else:
                    st.success(f"✅ RDV créé (id={res['id']})")
                    st.balloons()
                    del st.session_state["creneaux"]