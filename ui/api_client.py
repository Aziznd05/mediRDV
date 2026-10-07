import requests
from datetime import date

API_URL = "http://127.0.0.1:8000"

def _get(path, params=None):
    try:
        r = requests.get(f"{API_URL}{path}", params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        return {"_erreur": str(e)}

def _post(path, json=None):
    try:
        r = requests.post(f"{API_URL}{path}", json=json, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        try:
            return {"_erreur": r.json().get("detail", str(e))}
        except Exception:
            return {"_erreur": str(e)}
    except requests.exceptions.RequestException as e:
        return {"_erreur": str(e)}


# --- API publique ---
def get_kpis():
    return _get("/analytics/kpis")

def get_heatmap():
    return _get("/analytics/heatmap")

def get_evolution():
    return _get("/analytics/evolution")

def get_specialites_stats():
    return _get("/analytics/specialites")

def get_specialites():
    return _get("/referentiels/specialites")

def get_patients():
    return _get("/referentiels/patients")

def get_medecins():
    # À ajouter côté API plus tard. En attendant, on simule.
    return []

def get_rdv(date_debut=None, date_fin=None, medecin_id=None, statut=None):
    params = {}
    if date_debut: params["date_debut"] = str(date_debut)
    if date_fin: params["date_fin"] = str(date_fin)
    if medecin_id: params["medecin_id"] = medecin_id
    if statut: params["statut"] = statut
    return _get("/rendez_vous", params=params)

def creer_rdv(data):
    return _post("/rendez_vous", json=data)

def annuler_rdv(rdv_id, motif):
    try:
        r = requests.patch(
            f"{API_URL}/rendez_vous/{rdv_id}/annuler",
            json={"motif_annulation": motif}, timeout=5
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        try: return {"_erreur": r.json().get("detail", str(e))}
        except Exception: return {"_erreur": str(e)}

def chercher_creneaux(medecin_id, date_debut, nb_jours=7):
    return _get("/rendez_vous/creneaux-libres", params={
        "medecin_id": medecin_id,
        "date_debut": str(date_debut),
        "nb_jours": nb_jours,
    })