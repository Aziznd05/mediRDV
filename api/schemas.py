from pydantic import BaseModel, ConfigDict
from datetime import date, time, datetime
from typing import Optional


class SpecialiteBase(BaseModel):
    nom: str
    duree_minutes: int
    couleur: Optional[str] = None


class SpecialiteCreate(SpecialiteBase):
    pass


class SpecialiteOut(SpecialiteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class PatientBase(BaseModel):
    nom: str
    prenom: str
    date_naissance: Optional[date] = None
    sexe: Optional[str] = None
    telephone: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientOut(PatientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class RendezVousBase(BaseModel):
    patient_id: int
    medecin_id: int
    specialite_id: int
    date_rdv: date
    heure_debut: time
    duree_minutes: int
    canal: Optional[str] = None
    agent_saisie: Optional[str] = None


class RendezVousCreate(RendezVousBase):
    pass


class RendezVousOut(RendezVousBase):
    id: int
    statut: str
    confirme: bool
    date_creation: datetime
    model_config = ConfigDict(from_attributes=True)