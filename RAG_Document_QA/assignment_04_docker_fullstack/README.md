# Assignment 4 — Containerize a full stack

This project includes a FastAPI backend, server-rendered Jinja2 frontend, and
SQLite persistence. Docker Compose builds and runs the app; a named volume keeps
the database when the container is replaced.

## Run with Docker Compose

From this directory:

```powershell
docker compose up --build
```

Visit `http://localhost:8000`; use `docker compose down` to stop. The named
volume is preserved by default. To delete it, explicitly run
`docker compose down --volumes`.

## Run without Docker

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

The UI adds and deletes inventory items. `/health` is available for a basic container health check.
