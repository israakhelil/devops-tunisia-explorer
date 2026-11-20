# Tunisia Explorer — Pipeline CI/CD (Git, Jenkins, Docker)

Projet « Introduction au DevOps » — ISG Sousse, 3 LIG.

## Application
API FastAPI + page web listant les 24 gouvernorats de Tunisie par région.

| Endpoint | Rôle |
|---|---|
| `GET /` | Page web (filtre par région) |
| `GET /health` | Statut, version, commit, version de Python |
| `GET /api/gouvernorats?region=Centre-Est` | Liste (filtre optionnel) |
| `GET /api/gouvernorats/{nom}` | Détail (404 si inconnu) |
| `GET /api/regions` | Régions et nombre de gouvernorats |

## Workflow Git
`main` (protégée) ← `dev` ← `feature/*` · tags `vX.Y.Z` pour les versions.

## Pipelines Jenkins (dossier `ci/`)
| Pipeline | Fichier | Déclencheur |
|---|---|---|
| Build & Smoke | `ci/Jenkinsfile.pr` | Pull Request vers `dev` |
| Build complet | `ci/Jenkinsfile.dev` | Push sur `dev` |
| Build versionné | `ci/Jenkinsfile.release` | Tag `vX.Y.Z` |

Chaque pipeline : Checkout → Setup → Build → Run (Docker) → Smoke Test → Archive Artifacts (+ Cleanup),
avec build / run / smoke exécutés **en parallèle** pour Python 3.11 et 3.12.

## Lancer en local
```
pip install -r requirements.txt pytest httpx
python -m pytest
uvicorn app.main:app --port 5000
docker build --build-arg PY_VERSION=3.12 -t tunisia-explorer:local .
docker run -d --name api-local -p 5000:5000 tunisia-explorer:local
docker exec -i api-local python - < scripts/smoke_check.py
```
