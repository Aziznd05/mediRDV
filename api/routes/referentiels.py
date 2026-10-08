from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from api.database import get_db
from api import models, schemas
from api.auth import get_current_user, require_role, log_action

router = APIRouter(prefix="/referentiels", tags=["Référentiels"])

# Rôles autorisés à gérer les référentiels
ROLES_GESTION = ("admin", "responsable")
# Rôles autorisés à créer/modifier les patients
ROLES_PATIENTS = ("admin", "responsable", "agent")


# --- Spécialités ---
@router.get("/specialites", response_model=List[schemas.SpecialiteOut])
def lister_specialites(
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    return db.query(models.Specialite).all()


@router.post("/specialites", response_model=schemas.SpecialiteOut, status_code=201)
def creer_specialite(
    data: schemas.SpecialiteCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(*ROLES_GESTION)),
):
    existe = db.query(models.Specialite).filter_by(nom=data.nom).first()
    if existe:
        raise HTTPException(400, "Cette spécialité existe déjà")
    spe = models.Specialite(**data.model_dump())
    db.add(spe)
    db.commit()
    db.refresh(spe)
    log_action(db, user, "creation", "specialite", spe.id, f"nom={spe.nom}")
    return spe


# --- Patients ---
@router.get("/patients", response_model=List[schemas.PatientOut])
def lister_patients(
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    return db.query(models.Patient).all()


@router.post("/patients", response_model=schemas.PatientOut, status_code=201)
def creer_patient(
    data: schemas.PatientCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(*ROLES_PATIENTS)),
):
    # EF-04 : détecter les doublons
    doublon = db.query(models.Patient).filter_by(
        nom=data.nom, prenom=data.prenom, date_naissance=data.date_naissance
    ).first()
    if doublon:
        raise HTTPException(409, f"Patient déjà existant (id={doublon.id})")

    patient = models.Patient(**data.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    log_action(db, user, "creation", "patient", patient.id,
               f"{patient.nom} {patient.prenom}")
    return patient