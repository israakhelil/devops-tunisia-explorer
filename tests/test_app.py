"""Tests unitaires (lancés dans le pipeline dev, pendant le build Docker)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_24_gouvernorats():
    assert len(client.get("/api/gouvernorats").json()) == 24


def test_filtre_region():
    noms = [g["nom"] for g in client.get("/api/gouvernorats", params={"region": "Centre-Est"}).json()]
    assert "Sousse" in noms
    assert "Tunis" not in noms


def test_detail_et_404():
    assert client.get("/api/gouvernorats/Sousse").json()["region"] == "Centre-Est"
    assert client.get("/api/gouvernorats/Atlantide").status_code == 404


def test_regions():
    assert sum(r["total"] for r in client.get("/api/regions").json()) == 24
