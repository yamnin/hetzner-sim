# Hetzner Cloud Simulator

API en **Python (FastAPI)** con **PostgreSQL** que simula la API de Hetzner Cloud
(crear, listar, apagar/encender y borrar servidores). Corre en Docker con el mismo
stack que tendría un VPS Hetzner CX22: Ubuntu 24.04 + nginx + app + PostgreSQL,
limitado a 2 vCPU / 4 GB RAM.

## Requisitos (Windows)

- [Git](https://git-scm.com/download/win)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python 3.12](https://www.python.org/downloads/) (solo para correr tests sin Docker)

## Levantar el "servidor"

```bash
copy .env.example .env
docker compose up --build
```

- API: http://localhost:8080
- Documentación interactiva: http://localhost:8080/docs

## Ejemplos

```bash
curl -X POST http://localhost:8080/v1/servers -H "Content-Type: application/json" -d "{\"name\":\"web-1\",\"server_type\":\"cx22\",\"location\":\"fsn1\"}"
curl http://localhost:8080/v1/servers
curl -X POST http://localhost:8080/v1/servers/1/actions -H "Content-Type: application/json" -d "{\"action\":\"poweroff\"}"
curl -X DELETE http://localhost:8080/v1/servers/1
```

## Tests

Con PostgreSQL corriendo (`docker compose up db`):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
```

GitHub Actions ejecuta los tests contra un PostgreSQL real en cada push (`.github/workflows/ci.yml`).

## Estructura

```
app/            código de la API (FastAPI + SQLAlchemy)
tests/          tests con pytest
deploy/         nginx.conf y cloud-init.yml (para un Hetzner real)
Dockerfile      imagen Ubuntu 24.04 con la app
docker-compose.yml  stack que simula el VPS
```

## Pasar a un Hetzner real

1. Crea un servidor CX22 con Ubuntu 24.04 y pega `deploy/cloud-init.yml` en "Cloud config".
2. `ssh root@IP`, luego `git clone <tu-repo> && cd <repo> && cp .env.example .env`.
3. `docker compose up -d --build`.
