# Assignment 2 — Connect a backend to a database

This independent FastAPI project stores items in SQLite through SQLAlchemy 2.
The database file is created on first startup.

## Run

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Browse to `http://127.0.0.1:8000/docs`. Override `DATABASE_URL` to use another
SQLAlchemy-supported database; install that database's driver separately.
SQLite is the default for a zero-service local demo.

The API exposes `POST`, `GET`, `PUT`, and `DELETE` at `/items`.
