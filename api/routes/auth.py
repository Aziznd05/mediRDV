from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from api.database import get_db
from api import models, schemas
from api.auth import (
    hasher_mot_de_passe, verifier_mot_de_passe,
    creer_token, get_current_user, require_role,
)

router = APIRouter(prefix="/auth", tags=["Authentification"])

ROLES_VALIDES = {"agent", "medecin", "responsable", "direction", "admin"}


@router.post("/register", response_model=schemas.UserOut, status_code=201)
def inscrire(
    data: schemas.UserCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_role("admin")),
):
    """Création d'utilisateur — réservée à l'admin."""
    if data.role not in ROLES_VALIDES:
        raise HTTPException(400, f"Rôle invalide. Valeurs : {ROLES_VALIDES}")

    if db.query(models.User).filter_by(username=data.username).first():
        raise HTTPException(409, "Ce nom d'utilisateur existe déjà")
    if db.query(models.User).filter_by(email=data.email).first():
        raise HTTPException(409, "Cet email existe déjà")

    user = models.User(
        username=data.username,
        email=data.email,
        role=data.role,
        medecin_id=data.medecin_id,
        hashed_password=hasher_mot_de_passe(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/bootstrap")
def bootstrap_admin(db: Session = Depends(get_db)):
    """Crée l'admin initial si aucun utilisateur n'existe. À appeler une seule fois."""
    if db.query(models.User).count() > 0:
        raise HTTPException(400, "Des utilisateurs existent déjà, bootstrap impossible.")
    admin = models.User(
        username="admin",
        email="admin@baobabs.sn",
        role="admin",
        hashed_password=hasher_mot_de_passe("AdminBaobabs2026!"),
    )
    db.add(admin)
    db.commit()
    return {"message": "Admin créé", "username": "admin", "password": "AdminBaobabs2026!"}


@router.post("/login", response_model=schemas.Token)
def login(data: schemas.LoginInput, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=data.username).first()
    if not user or not verifier_mot_de_passe(data.password, user.hashed_password):
        raise HTTPException(401, "Identifiants incorrects")
    if not user.actif:
        raise HTTPException(403, "Compte désactivé")

    token = creer_token({"sub": user.username, "role": user.role})
    return schemas.Token(
        access_token=token, role=user.role, username=user.username
    )

@router.post("/token", response_model=schemas.Token)
def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Endpoint compatible OAuth2 (utilisé par Swagger UI)."""
    user = db.query(models.User).filter_by(username=form_data.username).first()
    if not user or not verifier_mot_de_passe(form_data.password, user.hashed_password):
        raise HTTPException(401, "Identifiants incorrects")
    if not user.actif:
        raise HTTPException(403, "Compte désactivé")

    token = creer_token({"sub": user.username, "role": user.role})
    return schemas.Token(
        access_token=token, role=user.role, username=user.username
    )

@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user


@router.get("/users", response_model=List[schemas.UserOut])
def lister_utilisateurs(
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_role("admin")),
):
    return db.query(models.User).all()