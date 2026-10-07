from api.routes import referentiels, rendez_vous, analytics
from fastapi import FastAPI
from api.config import settings
from api.database import Base, engine

# Import des modèles pour qu'ils soient enregistrés
from api import models  # noqa

# Crée les tables au démarrage (à remplacer par Alembic plus tard)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="API MédiRDV — gestion des rendez-vous médicaux",
)

@app.get("/", tags=["Racine"])
def racine():
    return {
        "app": settings.app_name,
        "version": settings.version,
        "status": "ok",
    }

@app.get("/health", tags=["Racine"])
def health():
    return {"status": "healthy"}
from fastapi import FastAPI
from api.config import settings
from api.database import Base, engine
from api import models  # noqa
from api.routes import referentiels
from api.routes import referentiels, rendez_vous
from api.routes import referentiels, rendez_vous, analytics
app.include_router(analytics.router)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="API MédiRDV — gestion des rendez-vous médicaux",
)

app.include_router(referentiels.router)
app.include_router(rendez_vous.router)
app.include_router(analytics.router)

@app.get("/", tags=["Racine"])
def racine():
    return {"app": settings.app_name, "version": settings.version, "status": "ok"}


@app.get("/health", tags=["Racine"])
def health():
    return {"status": "healthy"}

from api.routes import referentiels, rendez_vous