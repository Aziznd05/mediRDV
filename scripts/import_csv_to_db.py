"""
Importe le CSV propre dans la base SQLite MédiRDV.
Mapping : IDs texte du CSV -> IDs entiers auto-incrémentés en base.
"""
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

import pandas as pd
from datetime import datetime
from api.database import SessionLocal, Base, engine
from api import models

# Crée les tables si absentes
Base.metadata.create_all(bind=engine)

CHEMIN = RACINE / "data" / "propre" / "rendez_vous_medirdv_propre.csv"

# --- 1. Vider la base (idempotent) ---
db = SessionLocal()
for table in reversed(Base.metadata.sorted_tables):
    db.execute(table.delete())
db.commit()
print("Base vidée.")

# --- 2. Charger le CSV ---
df = pd.read_csv(CHEMIN, encoding="utf-8")
print(f"{len(df)} lignes à importer.")

# --- 3. Spécialités ---
specialites_uniques = df[["specialite", "duree_min"]].drop_duplicates(subset="specialite")
map_spe = {}
couleurs = {
    "Médecine générale": "#3B82F6",
    "Pédiatrie": "#10B981",
    "Gynécologie-obstétrique": "#EC4899",
    "Cardiologie": "#EF4444",
    "Dermatologie": "#F59E0B",
    "Ophtalmologie": "#8B5CF6",
    "ORL": "#06B6D4",
    "Endocrinologie": "#84CC16",
    "Kinésithérapie": "#6366F1",
}
for _, row in specialites_uniques.iterrows():
    spe = models.Specialite(
        nom=row["specialite"],
        duree_minutes=int(row["duree_min"]),
        couleur=couleurs.get(row["specialite"], "#6C757D"),
    )
    db.add(spe)
    db.flush()
    map_spe[row["specialite"]] = spe.id
db.commit()
print(f"{len(map_spe)} spécialités créées.")

# --- 4. Médecins ---
medecins_uniques = df[["medecin_id", "medecin_nom"]].drop_duplicates(subset="medecin_id")
map_med = {}
for _, row in medecins_uniques.iterrows():
    nom_complet = str(row["medecin_nom"]).replace("Dr ", "").strip()
    parties = nom_complet.split(" ", 1)
    prenom = parties[0] if parties else "?"
    nom = parties[1] if len(parties) > 1 else "?"
    med = models.Medecin(nom=nom, prenom=prenom, actif=True)
    db.add(med)
    db.flush()
    map_med[row["medecin_id"]] = med.id
db.commit()
print(f"{len(map_med)} médecins créés.")

# --- 5. Lien médecin <-> spécialité ---
liens = df[["medecin_id", "specialite"]].drop_duplicates()
for _, row in liens.iterrows():
    lien = models.MedecinSpecialite(
        medecin_id=map_med[row["medecin_id"]],
        specialite_id=map_spe[row["specialite"]],
    )
    db.add(lien)
db.commit()
print(f"{len(liens)} liens médecin-spécialité créés.")

# --- 6. Patients ---
patients_uniques = df[[
    "patient_id", "patient_nom", "patient_prenom", "sexe", "date_naissance", "telephone"
]].drop_duplicates(subset="patient_id")
map_pat = {}
for _, row in patients_uniques.iterrows():
    dn = pd.to_datetime(row["date_naissance"], errors="coerce")
    pat = models.Patient(
        nom=str(row["patient_nom"]).strip(),
        prenom=str(row["patient_prenom"]).strip(),
        sexe=row["sexe"] if pd.notna(row["sexe"]) else None,
        date_naissance=dn.date() if pd.notna(dn) else None,
        telephone=str(row["telephone"]) if pd.notna(row["telephone"]) else None,
    )
    db.add(pat)
    db.flush()
    map_pat[row["patient_id"]] = pat.id
db.commit()
print(f"{len(map_pat)} patients créés.")

# --- 7. Plages horaires (déduites des RDV existants) ---
plages_vues = set()
for _, row in df.iterrows():
    try:
        dt = pd.to_datetime(row["date_rdv"])
        jour_semaine = dt.weekday()
        heure = datetime.strptime(str(row["heure_rdv"]), "%H:%M").time()
    except Exception:
        continue
    cle = (row["medecin_id"], jour_semaine, heure)
    if cle in plages_vues:
        continue
    plages_vues.add(cle)

# On génère pour chaque médecin une plage standard sur chaque jour présent
from collections import defaultdict
plages_par_medecin = defaultdict(lambda: defaultdict(list))
for _, row in df.iterrows():
    try:
        dt = pd.to_datetime(row["date_rdv"])
        jour_semaine = dt.weekday()
        heure = datetime.strptime(str(row["heure_rdv"]), "%H:%M").time()
    except Exception:
        continue
    plages_par_medecin[row["medecin_id"]][jour_semaine].append(heure)

compteur = 0
for med_txt, jours in plages_par_medecin.items():
    for jour, heures in jours.items():
        if not heures:
            continue
        h_min = min(heures)
        h_max = max(heures)
        # Ajoute 1h de marge
        fin = (datetime.combine(datetime.today(), h_max).replace(hour=min(h_max.hour + 1, 18))).time()
        plage = models.PlageHoraire(
            medecin_id=map_med[med_txt],
            jour_semaine=jour,
            heure_debut=h_min,
            heure_fin=fin,
        )
        db.add(plage)
        compteur += 1
db.commit()
print(f"{compteur} plages horaires créées.")

# --- 8. Rendez-vous ---
compteur_rdv = 0
for _, row in df.iterrows():
    try:
        dt = pd.to_datetime(row["date_rdv"]).date()
        heure = datetime.strptime(str(row["heure_rdv"]), "%H:%M").time()
        dt_prise = pd.to_datetime(row["date_prise"]).date()
    except Exception:
        continue

    motif = row["motif_annulation"] if pd.notna(row["motif_annulation"]) else None
    confirme_bool = str(row["confirme"]).strip().lower() == "oui"

    rdv = models.RendezVous(
        patient_id=map_pat[row["patient_id"]],
        medecin_id=map_med[row["medecin_id"]],
        specialite_id=map_spe[row["specialite"]],
        date_rdv=dt,
        heure_debut=heure,
        duree_minutes=int(row["duree_min"]) if pd.notna(row["duree_min"]) else 20,
        statut=row["statut"],
        confirme=confirme_bool,
        motif_annulation=motif,
        canal=row["canal"] if pd.notna(row["canal"]) else None,
        agent_saisie=str(row["agent_saisie"]) if pd.notna(row["agent_saisie"]) else None,
        date_creation=datetime.combine(dt_prise, datetime.min.time()),
    )
    db.add(rdv)
    compteur_rdv += 1

    if compteur_rdv % 500 == 0:
        db.commit()
        print(f"  {compteur_rdv} RDV importés...")

db.commit()
db.close()
print(f"\n✅ Import terminé : {compteur_rdv} rendez-vous, {len(map_pat)} patients, {len(map_med)} médecins.")