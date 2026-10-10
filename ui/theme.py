import streamlit as st

COULEURS = {
    "vert_fonce": "#0F5132",
    "vert": "#198754",
    "vert_clair": "#D1E7DD",
    "bleu": "#0D6EFD",
    "rouge": "#DC3545",
    "orange": "#FD7E14",
    "gris": "#6C757D",
    "fond": "#F8F9FA",
}

def injecter_css():
    st.markdown(f"""
    <style>
    /* Police générale */
    html, body, [class*="css"] {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}

    /* Fond */
    .main {{
        background-color: {COULEURS['fond']};
    }}

    /* Header */
    header[data-testid="stHeader"] {{
        background-color: {COULEURS['vert_fonce']};
    }}

    /* Cartes KPI */
    .kpi-card {{
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 5px solid {COULEURS['vert']};
        transition: transform 0.2s;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.1);
    }}
    .kpi-card.rouge {{ border-left-color: {COULEURS['rouge']}; }}
    .kpi-card.orange {{ border-left-color: {COULEURS['orange']}; }}
    .kpi-card.bleu {{ border-left-color: {COULEURS['bleu']}; }}

    .kpi-label {{
        font-size: 0.85rem;
        color: {COULEURS['gris']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }}
    .kpi-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {COULEURS['vert_fonce']};
        margin-top: 4px;
    }}
    .kpi-sub {{
        font-size: 0.8rem;
        color: {COULEURS['gris']};
        margin-top: 4px;
    }}

    /* Titres */
    h1 {{
        color: {COULEURS['vert_fonce']};
        font-weight: 700;
    }}
    h2, h3 {{
        color: {COULEURS['vert_fonce']};
        font-weight: 600;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: white;
        border-right: 1px solid #E9ECEF;
    }}

    /* Boutons */
    .stButton > button {{
        border-radius: 10px;
        font-weight: 600;
        padding: 8px 18px;
        transition: all 0.2s;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(25,135,84,0.2);
    }}

    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }}

    /* Tableaux */
    .dataframe {{
        border-radius: 12px !important;
        overflow: hidden !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def carte_kpi(label, valeur, sous_titre="", couleur="vert"):
    classe = f"kpi-card {couleur}" if couleur != "vert" else "kpi-card"
    st.markdown(f"""
    <div class="{classe}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{valeur}</div>
        <div class="kpi-sub">{sous_titre}</div>
    </div>
    """, unsafe_allow_html=True)

