"""
EF-25 : Score de risque d'absence par RDV.
Régression logistique + Random Forest.
Métriques : AUC, précision, rappel, matrice de confusion.
"""
import sys
from pathlib import Path
RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score,
    confusion_matrix, classification_report,
)

# --- Chargement ---
df = pd.read_csv(RACINE / "data" / "propre" / "rendez_vous_medirdv_propre.csv", encoding="utf-8")
df["date_rdv"] = pd.to_datetime(df["date_rdv"], errors="coerce")
df["date_prise"] = pd.to_datetime(df["date_prise"], errors="coerce")
df["date_naissance"] = pd.to_datetime(df["date_naissance"], errors="coerce")

# On ne garde que les RDV échus (Honoré ou Absent)
df = df[df["statut"].isin(["Honoré", "Absent"])].copy()
print(f"{len(df)} RDV échus")

# --- Variables ---
df["delai"] = (df["date_rdv"] - df["date_prise"]).dt.days
df["jour_semaine"] = df["date_rdv"].dt.weekday
df["heure"] = df["heure_rdv"].str[:2].astype(int)
df["age"] = ((df["date_rdv"] - df["date_naissance"]).dt.days / 365.25).fillna(40)
df["est_confirme"] = (df["confirme"] == "Oui").astype(int)
df["cible_absent"] = (df["statut"] == "Absent").astype(int)

# Historique d'absence par patient
hist = df.groupby("patient_id")["cible_absent"].agg(["sum", "count"])
hist["taux_absence_hist"] = hist["sum"] / hist["count"]
df = df.merge(hist[["taux_absence_hist"]], left_on="patient_id", right_index=True, how="left")
df["taux_absence_hist"] = df["taux_absence_hist"].fillna(0)

# Encodage spécialité
df = pd.get_dummies(df, columns=["specialite"], prefix="spe")

# --- Features ---
features = ["delai", "jour_semaine", "heure", "age", "est_confirme", "taux_absence_hist"]
features += [c for c in df.columns if c.startswith("spe_")]

X = df[features].fillna(0)
y = df["cible_absent"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)
print(f"Train : {len(X_train)} | Test : {len(X_test)} | Taux absence : {y.mean():.2%}")

# --- Modèle 1 : Régression logistique ---
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

logreg = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
logreg.fit(X_train_s, y_train)
proba_lr = logreg.predict_proba(X_test_s)[:, 1]
auc_lr = roc_auc_score(y_test, proba_lr)

# --- Modèle 2 : Random Forest ---
rf = RandomForestClassifier(n_estimators=200, max_depth=10, class_weight="balanced", random_state=42)
rf.fit(X_train, y_train)
proba_rf = rf.predict_proba(X_test)[:, 1]
auc_rf = roc_auc_score(y_test, proba_rf)

# --- Choix du seuil par coût/bénéfice ---
# Coût d'un appel de relance : 1
# Coût d'un créneau perdu : 10
# On choisit le seuil qui minimise : (FN * 10) + (FP * 1)
def seuil_optimal(y_true, proba, cout_fp=1, cout_fn=10):
    seuils = np.arange(0.05, 0.95, 0.05)
    couts = []
    for s in seuils:
        pred = (proba >= s).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
        couts.append(cout_fp * fp + cout_fn * fn)
    idx = int(np.argmin(couts))
    return seuils[idx], couts[idx]

seuil_lr, cout_lr = seuil_optimal(y_test, proba_lr)
seuil_rf, cout_rf = seuil_optimal(y_test, proba_rf)

# --- Métriques finales ---
def metriques(y_true, proba, seuil, nom_modele):
    pred = (proba >= seuil).astype(int)
    cm = confusion_matrix(y_true, pred)
    return {
        "modele": nom_modele,
        "auc": round(roc_auc_score(y_true, proba), 3),
        "seuil": round(float(seuil), 2),
        "precision": round(precision_score(y_true, pred), 3),
        "rappel": round(recall_score(y_true, pred), 3),
        "matrice_confusion": cm.tolist(),
    }

resultats = [
    metriques(y_test, proba_lr, seuil_lr, "Régression logistique"),
    metriques(y_test, proba_rf, seuil_rf, "Random Forest"),
]

print("\n=== Résultats modèles ===")
for r in resultats:
    print(f"\n{r['modele']} : AUC={r['auc']} | seuil={r['seuil']} | précision={r['precision']} | rappel={r['rappel']}")
    print(f"  Matrice : {r['matrice_confusion']}")

# --- Feature importance (Random Forest) ---
importances = pd.DataFrame({
    "variable": X.columns,
    "importance": rf.feature_importances_,
}).sort_values("importance", ascending=False).head(10)

print("\n=== Top 10 variables (Random Forest) ===")
print(importances.to_string(index=False))

# --- Sauvegarde ---
sortie = RACINE / "data" / "propre" / "score_absence_metriques.json"
with open(sortie, "w", encoding="utf-8") as f:
    json.dump({
        "resultats": resultats,
        "importances": importances.to_dict(orient="records"),
        "hypothese_couts": {"cout_appel_relance": 1, "cout_creneau_perdu": 10},
    }, f, ensure_ascii=False, indent=2)

print(f"\n✅ Métriques sauvegardées dans {sortie}")