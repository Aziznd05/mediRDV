"""
Script de nettoyage du fichier rendez_vous_medirdv_brut.csv
Produit : data/propre/rendez_vous_medirdv_propre.csv
Rapport : docs/rapport_nettoyage.md
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
from datetime import datetime

# --- Chemins ---
RACINE = Path(__file__).resolve().parent.parent
CHEMIN_BRUT = RACINE / "data" / "brut" / "rendez_vous_medirdv_brut.csv"
CHEMIN_PROPRE = RACINE / "data" / "propre" / "rendez_vous_medirdv_propre.csv"
CHEMIN_RAPPORT = RACINE / "docs" / "rapport_nettoyage.md"

# Pour le rapport
log = []

def tracer(msg):
    print(msg)
    log.append(msg)

# --- 1. Chargement ---
tracer("## 1. Chargement")
df = pd.read_csv(CHEMIN_BRUT, encoding="utf-8", sep=",")
n0 = len(df)
tracer(f"- Lignes initiales : **{n0}**")

# --- 2. Suppression des doublons ---
tracer("\n## 2. Doublons")
n_avant = len(df)
df = df.drop_duplicates(subset="id_rdv", keep="first").reset_index(drop=True)
tracer(f"- Lignes supprimées (id_rdv dupliqués) : **{n_avant - len(df)}**")
tracer(f"- Lignes restantes : **{len(df)}**")

# --- 3. Normalisation des dates ---
tracer("\n## 3. Dates")

def parser_date(val):
    if pd.isna(val):
        return pd.NaT
    val = str(val).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

df["date_prise"] = df["date_prise"].apply(parser_date).dt.strftime("%Y-%m-%d")
df["date_rdv"]   = df["date_rdv"].apply(parser_date).dt.strftime("%Y-%m-%d")

n_dates_manquantes = df["date_rdv"].isna().sum()
tracer(f"- Dates invalides après parsing : **{n_dates_manquantes}**")

# --- 4. Normalisation des heures ---
tracer("\n## 4. Heures")

def parser_heure(val):
    if pd.isna(val):
        return None
    val = str(val).strip().lower().replace("h", ":")
    try:
        h, m = val.split(":")
        h, m = int(h), int(m)
        if 0 <= h < 24 and 0 <= m < 60:
            return f"{h:02d}:{m:02d}"
    except (ValueError, AttributeError):
        return None
    return None

df["heure_rdv"] = df["heure_rdv"].apply(parser_heure)

# Signalement des heures hors plage 08:00 - 18:00
def heure_hors_plage(h):
    if h is None:
        return False
    hh = int(h.split(":")[0])
    return hh < 8 or hh >= 18

n_heures_hors = df["heure_rdv"].apply(heure_hors_plage).sum()
tracer(f"- Heures hors plage 08:00-18:00 : **{n_heures_hors}** (conservées, à examiner)")

# --- 5. Normalisation des durées ---
tracer("\n## 5. Durées")
durees_valides = {15, 20, 30}
n_durees_invalides = (~df["duree_min"].isin(durees_valides)).sum()
df.loc[~df["duree_min"].isin(durees_valides), "duree_min"] = np.nan
tracer(f"- Durées invalides remises à NaN : **{n_durees_invalides}**")

# --- 6. Normalisation des spécialités ---
tracer("\n## 6. Spécialités")
mapping_specialites = {
    "médecine générale": "Médecine générale",
    "medecine generale": "Médecine générale",
    "mg": "Médecine générale",
    "gynécologie-obstétrique": "Gynécologie-obstétrique",
    "gynecologie": "Gynécologie-obstétrique",
    "gynéco": "Gynécologie-obstétrique",
    "gynecologie-obstetrique": "Gynécologie-obstétrique",
    "pédiatrie": "Pédiatrie",
    "pediatrie": "Pédiatrie",
    "cardiologie": "Cardiologie",
    "dermatologie": "Dermatologie",
    "dermato": "Dermatologie",
    "ophtalmologie": "Ophtalmologie",
    "ophtalmo": "Ophtalmologie",
    "orl": "ORL",
    "o.r.l": "ORL",
    "endocrinologie": "Endocrinologie",
    "endocrino": "Endocrinologie",
    "kinésithérapie": "Kinésithérapie",
    "kinesitherapie": "Kinésithérapie",
    "kiné": "Kinésithérapie",
}

def normaliser_specialite(val):
    if pd.isna(val):
        return None
    v = str(val).strip().lower()
    return mapping_specialites.get(v, str(val).strip())

df["specialite"] = df["specialite"].apply(normaliser_specialite)
n_spe_restantes = df["specialite"].nunique()
tracer(f"- Spécialités après normalisation : **{n_spe_restantes}** (attendu : 9)")

# --- 7. Normalisation du sexe ---
tracer("\n## 7. Sexe")
mapping_sexe = {
    "f": "F", "femme": "F",
    "m": "M", "h": "M", "homme": "M",
}

def normaliser_sexe(val):
    if pd.isna(val):
        return None
    return mapping_sexe.get(str(val).strip().lower(), str(val).strip())

df["sexe"] = df["sexe"].apply(normaliser_sexe)
tracer(f"- Valeurs distinctes après normalisation : **{sorted(df['sexe'].dropna().unique())}**")

# --- 8. Normalisation du statut ---
tracer("\n## 8. Statut")
mapping_statut = {
    "honoré": "Honoré",
    "honore": "Honoré",
    "ok": "Honoré",
    "venu": "Honoré",
    "absent": "Absent",
    "no-show": "Absent",
    "non venu": "Absent",
    "planifié": "Planifié",
    "planifie": "Planifié",
    "confirmé": "Confirmé",
    "confirme": "Confirmé",
    "annulé": "Annulé",
    "annule": "Annulé",
}

def normaliser_statut(val):
    if pd.isna(val):
        return None
    return mapping_statut.get(str(val).strip().lower(), str(val).strip())

df["statut"] = df["statut"].apply(normaliser_statut)
tracer(f"- Valeurs distinctes après normalisation : **{sorted(df['statut'].dropna().unique())}**")

# --- 9. Normalisation du téléphone ---
tracer("\n## 9. Téléphone")

def normaliser_telephone(val):
    if pd.isna(val):
        return None
    v = re.sub(r"\D", "", str(val))
    if v.startswith("00221"):
        v = v[5:]
    elif v.startswith("221"):
        v = v[3:]
    if len(v) == 9 and v[:2] in {"70", "75", "76", "77", "78"}:
        return v
    return None

n_tel_avant = df["telephone"].notna().sum()
df["telephone"] = df["telephone"].apply(normaliser_telephone)
n_tel_apres = df["telephone"].notna().sum()
tracer(f"- Téléphones valides avant : **{n_tel_avant}**")
tracer(f"- Téléphones valides après : **{n_tel_apres}**")

# --- 10. Normalisation du confirme ---
tracer("\n## 10. Confirme")
df["confirme"] = df["confirme"].fillna("Non")
df["confirme"] = df["confirme"].apply(lambda x: "Oui" if str(x).strip().lower() == "oui" else "Non")
tracer(f"- Valeurs : **{df['confirme'].value_counts().to_dict()}**")

# --- 11. Normalisation du canal ---
tracer("\n## 11. Canal")
df["canal"] = df["canal"].fillna("Non renseigné")
df["canal"] = df["canal"].str.strip()
tracer(f"- Valeurs : **{df['canal'].value_counts().to_dict()}**")

# --- 12. Normalisation motif_annulation ---
tracer("\n## 12. Motif d'annulation")
df.loc[df["statut"] != "Annulé", "motif_annulation"] = np.nan
n_annul_sans_motif = ((df["statut"] == "Annulé") & df["motif_annulation"].isna()).sum()
tracer(f"- Annulations sans motif : **{n_annul_sans_motif}** (à compléter)")

# --- 13. Colonnes finales ---
tracer("\n## 13. Colonnes finales")
colonnes_finales = [
    "id_rdv", "date_prise", "date_rdv", "heure_rdv", "duree_min",
    "specialite", "medecin_id", "medecin_nom",
    "patient_id", "patient_nom", "patient_prenom", "sexe", "date_naissance",
    "telephone", "quartier", "canal", "confirme", "statut",
    "motif_annulation", "agent_saisie",
]
df = df[colonnes_finales]
tracer(f"- Dimensions finales : **{df.shape}**")

# --- 14. Export ---
CHEMIN_PROPRE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(CHEMIN_PROPRE, index=False, encoding="utf-8")
tracer(f"\n## 14. Export\n- Fichier exporté : `{CHEMIN_PROPRE}`")

# --- 15. Rapport ---
CHEMIN_RAPPORT.parent.mkdir(parents=True, exist_ok=True)
with open(CHEMIN_RAPPORT, "w", encoding="utf-8") as f:
    f.write("# Rapport de nettoyage MédiRDV\n\n")
    f.write(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    f.write("\n".join(log))

print(f"\nRapport écrit dans {CHEMIN_RAPPORT}")
print("Terminé.")