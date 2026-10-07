import streamlit as st
from ui import api_client as api
from ui.theme import COULEURS


def afficher():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align:center; margin-bottom: 30px;">
            <div style="font-size: 4rem;">🏥</div>
            <h1 style="color:{COULEURS['vert_fonce']}; margin: 8px 0 4px 0;">MédiRDV</h1>
            <p style="color:{COULEURS['gris']}; margin: 0;">
            Clinique Les Baobabs · Dakar, Sénégal
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur", placeholder="admin")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("🔓 Se connecter", use_container_width=True, type="primary")

            if submitted:
                if not username or not password:
                    st.error("Veuillez remplir les deux champs.")
                else:
                    with st.spinner("Connexion en cours..."):
                        res = api.login(username, password)
                    if "_erreur" in res:
                        st.error(f"❌ {res['_erreur']}")
                    else:
                        st.session_state["token"] = res["access_token"]
                        st.session_state["role"] = res["role"]
                        st.session_state["username"] = res["username"]
                        st.success("Connexion réussie !")
                        st.rerun()

        st.markdown(f"""
        <div style="text-align:center; margin-top: 24px; color: {COULEURS['gris']}; font-size: 0.8rem;">
            Compte de démo : <code>admin</code> / <code>AdminBaobabs2026!</code>
        </div>
        """, unsafe_allow_html=True)