from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from datetime import date, timedelta
from typing import Optional

from api.database import get_db
from api import models

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/kpis")
def kpis(db: Session = Depends(get_db)):
    """Indicateurs clés du jour (EF-20)."""
    aujourdhui = date.today()
    total = db.query(models.RendezVous).filter_by(date_rdv=aujourdhui).count()
    honorés = db.query(models.RendezVous).filter_by(date_rdv=aujourdhui, statut="Honoré").count()
    absents = db.query(models.RendezVous).filter_by(date_rdv=aujourdhui, statut="Absent").count()
    planifies = db.query(models.RendezVous).filter_by(date_rdv=aujourdhui, statut="Planifié").count()

    # Taux d'occupation sur 30 jours
    date_debut = aujourdhui - timedelta(days=30)
    total_30 = db.query(models.RendezVous).filter(
        models.RendezVous.date_rdv >= date_debut
    ).count()
    absents_30 = db.query(models.RendezVous).filter(
        models.RendezVous.date_rdv >= date_debut,
        models.RendezVous.statut == "Absent"
    ).count()
    taux_absence = (absents_30 / total_30 * 100) if total_30 else 0

    return {
        "date": str(aujourdhui),
        "rdv_aujourdhui": total,
        "honores_aujourdhui": honorés,
        "absents_aujourdhui": absents,
        "planifies_aujourdhui": planifies,
        "taux_absence_30j": round(taux_absence, 2),
        "total_30j": total_30,
    }


@router.get("/heatmap")
def heatmap(db: Session = Depends(get_db)):
    """Répartition jour×heure (EF-21)."""
    q = db.query(
        models.RendezVous.date_rdv,
        models.RendezVous.heure_debut,
    ).all()
    from datetime import datetime
    result = {}
    for d, h in q:
        jour = d.weekday()  # 0=lundi
        heure = h.hour if hasattr(h, "hour") else int(str(h)[:2])
        cle = f"{jour}-{heure}"
        result[cle] = result.get(cle, 0) + 1
    return result


@router.get("/evolution")
def evolution(db: Session = Depends(get_db)):
    """Évolution mensuelle (EF-22) — compatible SQLite et PostgreSQL."""
    from sqlalchemy import text
    from api.config import settings

    # Détecte le type de base
    is_postgres = settings.database_url.startswith("postgresql")

    if is_postgres:
        requete = text("""
            SELECT to_char(date_rdv, 'YYYY-MM') AS mois,
                   COUNT(*) AS total,
                   SUM(CASE WHEN statut = 'Absent' THEN 1 ELSE 0 END) AS absents
            FROM rendez_vous
            GROUP BY mois
            ORDER BY mois
        """)
    else:
        requete = text("""
            SELECT strftime('%Y-%m', date_rdv) AS mois,
                   COUNT(*) AS total,
                   SUM(CASE WHEN statut = 'Absent' THEN 1 ELSE 0 END) AS absents
            FROM rendez_vous
            GROUP BY mois
            ORDER BY mois
        """)

    resultat = db.execute(requete).fetchall()
    return [{"mois": r[0], "total": r[1], "absents": r[2]} for r in resultat]


@router.get("/specialites")
def stats_specialites(db: Session = Depends(get_db)):
    """Top spécialités (EF-21)."""
    q = db.query(
        models.Specialite.nom,
        func.count(models.RendezVous.id).label("total"),
    ).join(models.RendezVous, models.RendezVous.specialite_id == models.Specialite.id)\
     .group_by(models.Specialite.nom)\
     .order_by(func.count(models.RendezVous.id).desc()).all()
    return [{"nom": n, "total": t} for n, t in q]