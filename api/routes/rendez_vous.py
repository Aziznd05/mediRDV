from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, time, datetime, timedelta, time as time_type
from typing import List, Optional

from api.database import get_db
from api import models, schemas

router = APIRouter(prefix="/rendez_vous", tags=["Rendez-vous"])


# --- Helpers ---
def creneau_chevauche(h1: time, d1: int, h2: time, d2: int) -> bool:
    """Deux créneaux se chevauchent-ils ?"""
    debut1 = datetime.combine(date.today(), h1)
    fin1 = debut1 + timedelta(minutes=d1)
    debut2 = datetime.combine(date.today(), h2)
    fin2 = debut2 + timedelta(minutes=d2)
    return debut1 < fin2 and debut2 < fin1


def est_dans_plage(db: Session, medecin_id: int, date_rdv: date, heure: time) -> bool:
    """RG-03 : le RDV doit être dans une plage ouverte du médecin."""
    jour_semaine = date_rdv.weekday()  # 0 = lundi
    plages = db.query(models.PlageHoraire).filter_by(
        medecin_id=medecin_id, jour_semaine=jour_semaine
    ).all()
    for p in plages:
        if p.heure_debut <= heure < p.heure_fin:
            return True
    return False


# --- Recherche du premier créneau libre (EF-11) ---
@router.get("/creneaux-libres", response_model=List[schemas.CreneauLibre])
def chercher_creneaux_libres(
    medecin_id: int,
    date_debut: date = Query(..., description="Date de début de recherche"),
    nb_jours: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
):
    """Cherche les premiers créneaux libres d'un médecin sur N jours."""
    resultats = []
    for offset in range(nb_jours):
        jour = date_debut + timedelta(days=offset)
        jour_semaine = jour.weekday()
        plages = db.query(models.PlageHoraire).filter_by(
            medecin_id=medecin_id, jour_semaine=jour_semaine
        ).all()
        if not plages:
            continue

        # Récupère les RDV existants ce jour-là
        rdv_jour = db.query(models.RendezVous).filter_by(
            medecin_id=medecin_id, date_rdv=jour
        ).filter(models.RendezVous.statut.in_(["Planifié", "Confirmé", "Honoré"])).all()

        for plage in plages:
            # Génère des créneaux de 20 min par défaut
            pas = 20
            courant = datetime.combine(jour, plage.heure_debut)
            fin_plage = datetime.combine(jour, plage.heure_fin)
            while courant + timedelta(minutes=pas) <= fin_plage:
                heure = courant.time()
                # Vérifie si libre
                libre = True
                for rdv in rdv_jour:
                    if creneau_chevauche(heure, pas, rdv.heure_debut, rdv.duree_minutes):
                        libre = False
                        break
                if libre:
                    resultats.append(schemas.CreneauLibre(
                        medecin_id=medecin_id,
                        date_rdv=jour,
                        heure_debut=heure,
                        duree_minutes=pas,
                    ))
                courant += timedelta(minutes=pas)

    # Limite à 10 résultats
    return resultats[:10]


# --- Création d'un RDV avec toutes les règles ---
@router.post("", response_model=schemas.RendezVousOut, status_code=201)
def creer_rdv(data: schemas.RendezVousCreate, db: Session = Depends(get_db)):
    # RG-04 : pas dans le passé, pas > 90 jours
    aujourdhui = date.today()
    if data.date_rdv < aujourdhui:
        raise HTTPException(400, "RG-04 : impossible de créer un RDV dans le passé")
    if data.date_rdv > aujourdhui + timedelta(days=90):
        raise HTTPException(400, "RG-04 : impossible de créer un RDV à plus de 90 jours")

    # Vérifie que le patient et le médecin existent
    if not db.query(models.Patient).get(data.patient_id):
        raise HTTPException(404, "Patient introuvable")
    if not db.query(models.Medecin).get(data.medecin_id):
        raise HTTPException(404, "Médecin introuvable")
    if not db.query(models.Specialite).get(data.specialite_id):
        raise HTTPException(404, "Spécialité introuvable")

    # RG-03 : le créneau doit être dans une plage ouverte
    if not est_dans_plage(db, data.medecin_id, data.date_rdv, data.heure_debut):
        raise HTTPException(400, "RG-03 : le médecin ne consulte pas à ce créneau")

    # RG-01 : un créneau médecin = un seul RDV actif
    rdv_medecin = db.query(models.RendezVous).filter_by(
        medecin_id=data.medecin_id, date_rdv=data.date_rdv
    ).filter(models.RendezVous.statut.in_(["Planifié", "Confirmé", "Honoré"])).all()
    for rdv in rdv_medecin:
        if creneau_chevauche(data.heure_debut, data.duree_minutes, rdv.heure_debut, rdv.duree_minutes):
            raise HTTPException(409, f"RG-01 : le médecin a déjà un RDV sur ce créneau (RDV id={rdv.id})")

    # RG-02 : un patient ne peut pas avoir deux RDV qui se chevauchent
    rdv_patient = db.query(models.RendezVous).filter_by(
        patient_id=data.patient_id, date_rdv=data.date_rdv
    ).filter(models.RendezVous.statut.in_(["Planifié", "Confirmé", "Honoré"])).all()
    for rdv in rdv_patient:
        if creneau_chevauche(data.heure_debut, data.duree_minutes, rdv.heure_debut, rdv.duree_minutes):
            raise HTTPException(409, f"RG-02 : le patient a déjà un RDV sur ce créneau (RDV id={rdv.id})")

    # Création
    rdv = models.RendezVous(
        **data.model_dump(),
        statut="Planifié",
        confirme=False,
    )
    db.add(rdv)
    db.commit()
    db.refresh(rdv)
    return rdv


# --- Annulation (RG-05) ---
@router.patch("/{rdv_id}/annuler", response_model=schemas.RendezVousOut)
def annuler_rdv(rdv_id: int, data: schemas.AnnulationInput, db: Session = Depends(get_db)):
    rdv = db.query(models.RendezVous).get(rdv_id)
    if not rdv:
        raise HTTPException(404, "RDV introuvable")

    if rdv.statut not in ("Planifié", "Confirmé"):
        raise HTTPException(400, f"Impossible d'annuler un RDV au statut {rdv.statut}")

    motifs_valides = {"Patient", "Médecin", "Clinique", "Autre"}
    if data.motif_annulation not in motifs_valides:
        raise HTTPException(400, f"RG-05 : motif invalide. Valeurs : {motifs_valides}")

    rdv.statut = "Annulé"
    rdv.motif_annulation = data.motif_annulation
    db.commit()
    db.refresh(rdv)
    # RG-06 : le créneau est immédiatement libre (implicite ici, car les requêtes filtrent sur statut actif)
    return rdv


# --- Changement de statut (RG-07) ---
@router.patch("/{rdv_id}/statut", response_model=schemas.RendezVousOut)
def changer_statut(rdv_id: int, data: schemas.StatutInput, db: Session = Depends(get_db)):
    rdv = db.query(models.RendezVous).get(rdv_id)
    if not rdv:
        raise HTTPException(404, "RDV introuvable")

    if data.statut not in ("Honoré", "Absent"):
        raise HTTPException(400, "Le statut ne peut être que 'Honoré' ou 'Absent'")

    if rdv.statut not in ("Planifié", "Confirmé"):
        raise HTTPException(400, f"Impossible de changer le statut d'un RDV {rdv.statut}")

    rdv.statut = data.statut
    db.commit()
    db.refresh(rdv)
    return rdv


# --- Liste des RDV (EF-15) ---
@router.get("", response_model=List[schemas.RendezVousOut])
def lister_rdv(
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    medecin_id: Optional[int] = None,
    specialite_id: Optional[int] = None,
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.RendezVous)
    if date_debut:
        q = q.filter(models.RendezVous.date_rdv >= date_debut)
    if date_fin:
        q = q.filter(models.RendezVous.date_rdv <= date_fin)
    if medecin_id:
        q = q.filter_by(medecin_id=medecin_id)
    if specialite_id:
        q = q.filter_by(specialite_id=specialite_id)
    if statut:
        q = q.filter_by(statut=statut)
    return q.order_by(models.RendezVous.date_rdv, models.RendezVous.heure_debut).all()