"""Smoke test : vérification rapide que l'application démarre et répond correctement.

Ce script est exécuté DANS le conteneur (via `docker exec`), donc il appelle localhost:5000.
Code de sortie 0 = PASSED, 1 = FAILED (c'est ce code qui rend le stage Jenkins vert ou rouge).
"""
import json
import os
import sys
import time
import urllib.error as ue
import urllib.request as u

BASE = "http://localhost:5000"
EXPECTED_VERSION = os.getenv("EXPECTED_VERSION", "")  # renseignée seulement pour le pipeline release


def get(path):
    """Retourne (code_http, json_ou_None)."""
    try:
        with u.urlopen(BASE + path, timeout=5) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except ue.HTTPError as e:
        return e.code, None


def wait_ready(max_seconds=20):
    """Attend que l'application ait démarré."""
    for _ in range(max_seconds):
        try:
            if get("/health")[0] == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def t_health():
    code, h = get("/health")
    ok = code == 200 and h["status"] == "ok"
    if EXPECTED_VERSION:
        ok = ok and h["version"] == EXPECTED_VERSION
    return ok, f"version={h['version']} python={h['python']} (attendue: {EXPECTED_VERSION or 'non verifiee'})"


def t_liste():
    code, data = get("/api/gouvernorats")
    return code == 200 and len(data) == 24, f"{len(data) if data else 0} gouvernorats (attendu: 24)"


def t_filtre():
    code, data = get("/api/gouvernorats?region=Centre-Est")
    noms = [g["nom"] for g in data] if data else []
    return code == 200 and "Sousse" in noms, f"Centre-Est -> {noms}"


def t_detail():
    code, g = get("/api/gouvernorats/Sousse")
    return code == 200 and g["region"] == "Centre-Est", f"Sousse -> {g}"


def t_404():
    code, _ = get("/api/gouvernorats/Atlantide")
    return code == 404, f"code recu: {code} (attendu: 404)"


TESTS = [
    ("GET /health", t_health),
    ("GET /api/gouvernorats (24 elements)", t_liste),
    ("GET /api/gouvernorats?region=Centre-Est (contient Sousse)", t_filtre),
    ("GET /api/gouvernorats/Sousse", t_detail),
    ("GET /api/gouvernorats/Atlantide (404 attendu)", t_404),
]

if __name__ == "__main__":
    if not wait_ready():
        print("FAILED application non joignable apres 20 s")
        sys.exit(1)
    results = []
    for name, fn in TESTS:
        try:
            ok, detail = fn()
        except Exception as e:  # une erreur inattendue = test échoué
            ok, detail = False, f"erreur: {e}"
        results.append(ok)
        print(("PASSED" if ok else "FAILED"), name, "-", detail)
    sys.exit(0 if all(results) else 1)
