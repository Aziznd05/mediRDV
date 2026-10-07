import streamlit as st
import pandas as pd
from ui import api_client as api


def afficher():
    st.markdown("# 👥 Patients")

    tab1, tab2 = st.tabs(["📋 Liste", "➕ Nouveau"])

    with tab1:
        patients = api.get_patients()
        if "_erreur" in patients:
            st.error(f"Erreur : {patients['_erreur']}")
        elif not patients:
            st.info("Aucun patient enregistré.")
        else:
            df = pd.DataFrame(patients)
            recherche = st.text_input("🔍 Rechercher (nom, prénom, téléphone)")
            if recherche:
                mask = df.astype(str).apply(
                    lambda r: r.str.contains(recherche, case=False).any(), axis=1
                )
                df = df[mask]
            st.markdown(f"**{len(df)} patients**")
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        with st.form("form_patient"):
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Nom *")
                date_naissance = st.date_input("Date de naissance", value=None)
            with col2:
                prenom = st.text_input("Prénom *")
                sexe = st.selectbox("Sexe", ["F", "M"])
            telephone = st.text_input("Téléphone (9 chiffres)", max_chars=9)

            soumis = st.form_submit_button("✅ Créer le patient", type="primary")
            if soumis:
                if not nom or not prenom:
                    st.error("Nom et prénom sont obligatoires.")
                else:
                    data = {
                        "nom": nom, "prenom": prenom,
                        "sexe": sexe,
                        "telephone": telephone or None,
                    }
                    if date_naissance:
                        data["date_naissance"] = str(date_naissance)
                    res = api._post("/referentiels/patients", json=data)
                    if "_erreur" in res:
                        st.error(f"❌ {res['_erreur']}")
                    else:
                        st.success(f"✅ Patient créé (id={res['id']})")