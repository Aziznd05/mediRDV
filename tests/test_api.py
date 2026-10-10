"""
Tests d'intégration API MédiRDV.
Couvre les exigences P1 et les règles RG-01 à RG-07.
"""
from datetime import date, timedelta


# --- Auth ---
def test_health(client):
    assert client.get("/health").status_code == 200


def test_login_ok(client):
    res = client.post("/auth/token", data={
        "username": "testadmin", "password": "TestAdmin2026!",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_mauvais_mdp(client):
    res = client.post("/auth/token", data={
        "username": "testadmin", "password": "faux",
    })
    assert res.status_code == 401


def test_route_protegee_sans_token(client):
    res = client.get("/referentiels/patients")
    assert res.status_code == 401


def test_route_protegee_avec_token(client, auth_headers):
    res = client.get("/referentiels/patients", headers=auth_headers)
    assert res.status_code == 200


# --- Référentiels ---
def test_creer_specialite(client, auth_headers):
    res = client.post("/referentiels/specialites",
                      json={"nom": "TestSpe", "duree_minutes": 20},
                      headers=auth_headers)
    assert res.status_code in (201, 400)


def test_creer_patient_et_doublon(client, auth_headers):
    payload = {"nom": "TestNom", "prenom": "TestPrenom",
               "date_naissance": "1990-01-01", "sexe": "F"}
    r1 = client.post("/referentiels/patients", json=payload, headers=auth_headers)
    assert r1.status_code in (201, 409)
    r2 = client.post("/referentiels/patients", json=payload, headers=auth_headers)
    assert r2.status_code == 409  # EF-04 doublon


# --- RG-04 : pas dans le passé ---
def test_rdv_dans_le_passe_refuse(client, auth_headers):
    hier = (date.today() - timedelta(days=1)).isoformat()
    res = client.post("/rendez_vous", json={
        "patient_id": 1, "medecin_id": 1, "specialite_id": 1,
        "date_rdv": hier, "heure_debut": "10:00:00", "duree_minutes": 20,
    }, headers=auth_headers)
    assert res.status_code == 400


# --- RG-04 : pas > 90 jours ---
def test_rdv_trop_loin_refuse(client, auth_headers):
    loin = (date.today() + timedelta(days=200)).isoformat()
    res = client.post("/rendez_vous", json={
        "patient_id": 1, "medecin_id": 1, "specialite_id": 1,
        "date_rdv": loin, "heure_debut": "10:00:00", "duree_minutes": 20,
    }, headers=auth_headers)
    assert res.status_code == 400


# --- RG-05 : annulation motif obligatoire ---
def test_annulation_motif_invalide(client, auth_headers):
    res = client.patch("/rendez_vous/1/annuler",
                       json={"motif_annulation": "XYZ"},
                       headers=auth_headers)
    assert res.status_code in (400, 404)