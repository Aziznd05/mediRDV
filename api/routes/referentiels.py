from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from api.database import get_db
from api import models, schemas

router = APIRouter(prefix="/referentiels", tags=["Référentiels"])


# --- Spécialités ---
@router.get("/specialites", response_model=List[schemas.SpecialiteOut])
def lister_specialites(db: Session = Depends(get_db)):
    return db.query(models.Specialite).all()


@router.post("/specialites", response_model=schemas.SpecialiteOut, status_code=201)
def creer_specialite(data: schemas.SpecialiteCreate, db: Session = Depends(get_db)):
    existe = db.query(models.Specialite).filter_by(nom=data.nom).first()
    if existe:
        raise HTTPException(400, "Cette spécialité existe déjà")
    spe = models.Specialite(**data.model_dump())
    db.add(spe)
    db.commit()
    db.refresh(spe)
    return spe


# --- Patients ---
@router.get("/patients", response_model=List[schemas.PatientOut])
def lister_patients(db: Session = Depends(get_db)):
    return db.query(models.Patient).all()


@router.post("/patients", response_model=schemas.PatientOut, status_code=201)
def creer_patient(data: schemas.PatientCreate, db: Session = Depends(get_db)):
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
    return patient