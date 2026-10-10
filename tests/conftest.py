import sys
from pathlib import Path
RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.database import Base, engine, SessionLocal
from api import models
from api.auth import hasher_mot_de_passe


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Créer un admin de test
    if not db.query(models.User).filter_by(username="testadmin").first():
        admin = models.User(
            username="testadmin",
            email="testadmin@test.sn",
            role="admin",
            hashed_password=hasher_mot_de_passe("TestAdmin2026!"),
        )
        db.add(admin)
        db.commit()
    yield
    db.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def token(client):
    res = client.post("/auth/token", data={
        "username": "testadmin", "password": "TestAdmin2026!",
    })
    return res.json()["access_token"]


@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}