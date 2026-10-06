from sqlalchemy import (
    Column, Integer, String, Date, Time, DateTime, ForeignKey, Boolean, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from api.database import Base


class Specialite(Base):
    __tablename__ = "specialites"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(80), unique=True, nullable=False)
    duree_minutes = Column(Integer, nullable=False, default=20)
    couleur = Column(String(20), nullable=True)

    medecins = relationship("MedecinSpecialite", back_populates="specialite")


class Medecin(Base):
    __tablename__ = "medecins"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(80), nullable=False)
    prenom = Column(String(80), nullable=False)
    actif = Column(Boolean, default=True)

    specialites = relationship("MedecinSpecialite", back_populates="medecin")
    plages = relationship("PlageHoraire", back_populates="medecin")
    indisponibilites = relationship("Indisponibilite", back_populates="medecin")
    rendez_vous = relationship("RendezVous", back_populates="medecin")


class MedecinSpecialite(Base):
    __tablename__ = "medecin_specialite"
    medecin_id = Column(Integer, ForeignKey("medecins.id"), primary_key=True)
    specialite_id = Column(Integer, ForeignKey("specialites.id"), primary_key=True)

    medecin = relationship("Medecin", back_populates="specialites")
    specialite = relationship("Specialite", back_populates="medecins")


class PlageHoraire(Base):
    __tablename__ = "plages_horaires"
    id = Column(Integer, primary_key=True, index=True)
    medecin_id = Column(Integer, ForeignKey("medecins.id"), nullable=False)
    jour_semaine = Column(Integer, nullable=False)  # 0=lundi ... 5=samedi
    heure_debut = Column(Time, nullable=False)
    heure_fin = Column(Time, nullable=False)

    medecin = relationship("Medecin", back_populates="plages")


class Indisponibilite(Base):
    __tablename__ = "indisponibilites"
    id = Column(Integer, primary_key=True, index=True)
    medecin_id = Column(Integer, ForeignKey("medecins.id"), nullable=False)
    debut = Column(DateTime, nullable=False)
    fin = Column(DateTime, nullable=False)
    motif = Column(String(200), nullable=True)

    medecin = relationship("Medecin", back_populates="indisponibilites")


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(80), nullable=False)
    prenom = Column(String(80), nullable=False)
    date_naissance = Column(Date, nullable=True)
    sexe = Column(String(1), nullable=True)  # F ou M
    telephone = Column(String(20), nullable=True)

    rendez_vous = relationship("RendezVous", back_populates="patient")


class RendezVous(Base):
    __tablename__ = "rendez_vous"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    medecin_id = Column(Integer, ForeignKey("medecins.id"), nullable=False)
    specialite_id = Column(Integer, ForeignKey("specialites.id"), nullable=False)
    date_rdv = Column(Date, nullable=False)
    heure_debut = Column(Time, nullable=False)
    duree_minutes = Column(Integer, nullable=False)
    statut = Column(String(20), nullable=False, default="Planifié")
    confirme = Column(Boolean, default=False)
    motif_annulation = Column(String(50), nullable=True)
    canal = Column(String(30), nullable=True)
    agent_saisie = Column(String(20), nullable=True)
    date_creation = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="rendez_vous")
    medecin = relationship("Medecin", back_populates="rendez_vous")
    specialite = relationship("Specialite")