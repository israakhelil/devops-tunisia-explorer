# Version de Python choisie au moment du build (--build-arg PY_VERSION=3.11 ou 3.12)
ARG PY_VERSION=3.12

# ---------- Étape 1 : installer les dépendances ----------
FROM python:${PY_VERSION}-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- Étape 2 : tests unitaires (uniquement avec --target test) ----------
FROM python:${PY_VERSION}-slim AS test
WORKDIR /app
COPY --from=builder /install /usr/local
RUN pip install --no-cache-dir pytest httpx
COPY app/ ./app/
COPY tests/ ./tests/
RUN python -m pytest -v

# ---------- Étape 3 : image finale (légère) ----------
FROM python:${PY_VERSION}-slim
ARG APP_VERSION=dev
ARG GIT_COMMIT=unknown
ENV APP_VERSION=${APP_VERSION} GIT_COMMIT=${GIT_COMMIT}
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ ./app/
RUN useradd -m appuser
USER appuser
EXPOSE 5000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
