"""Tunisia Explorer : petite API + page web sur les gouvernorats de Tunisie.

L'application est volontairement simple : l'objectif du projet est le pipeline CI/CD.
Les variables APP_VERSION et GIT_COMMIT sont injectées par Docker au moment du build.
"""
import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .data import GOUVERNORATS

app = FastAPI(title="Tunisia Explorer")


@app.get("/", response_class=HTMLResponse)
def home():
    """Page web."""
    return (Path(__file__).parent / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health():
    """Statut de l'application + infos de build (utilisé par le smoke test)."""
    return {
        "status": "ok",
        "version": os.getenv("APP_VERSION", "dev"),
        "commit": os.getenv("GIT_COMMIT", "unknown"),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
    }


@app.get("/api/gouvernorats")
def liste(region: str | None = None):
    """Liste des gouvernorats, avec filtre optionnel ?region=Centre-Est."""
    if region is None:
        return GOUVERNORATS
    return [g for g in GOUVERNORATS if g["region"].lower() == region.strip().lower()]


@app.get("/api/gouvernorat/{nom}")
def detail(nom: str):
    """Détail d'un gouvernorat (erreur 404 s'il n'existe pas)."""
    for g in GOUVERNORATS:
        if g["nom"].lower() == nom.strip().lower():
            return g
    raise HTTPException(status_code=404, detail="Gouvernorat introuvable")


@app.get("/api/regions")
def regions():
    """Liste des régions avec le nombre de gouvernorats."""
    comptage = {}
    for g in GOUVERNORATS:
        comptage[g["region"]] = comptage.get(g["region"], 0) + 1
    return [{"region": r, "total": n} for r, n in sorted(comptage.items())]
