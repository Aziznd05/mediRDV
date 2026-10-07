from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api.config import settings
from api.database import get_db
from api import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


def hasher_mot_de_passe(mdp: str) -> str:
    return pwd_context.hash(mdp)


def verifier_mot_de_passe(mdp: str, hash_: str) -> bool:
    return pwd_context.verify(mdp, hash_)


def creer_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter_by(username=username).first()
    if user is None or not user.actif:
        raise credentials_exception
    return user


def require_role(*roles_autorises: str):
    """Dépendance qui vérifie que l'utilisateur a un rôle autorisé."""
    def verificateur(user: models.User = Depends(get_current_user)) -> models.User:
        if user.role not in roles_autorises:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rôle '{user.role}' non autorisé. Requis : {roles_autorises}",
            )
        return user
    return verificateur


def log_action(
    db: Session,
    user: Optional[models.User],
    action: str,
    entite: str,
    entite_id: Optional[int] = None,
    details: Optional[str] = None,
):
    log = models.ActionLog(
        user_id=user.id if user else None,
        action=action,
        entite=entite,
        entite_id=entite_id,
        details=details,
    )
    db.add(log)
    db.commit()