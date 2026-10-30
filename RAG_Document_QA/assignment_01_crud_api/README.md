# Assignment 1 — CRUD API

A standalone FastAPI service with create, read, update, and delete operations
for items. Data is held in memory and resets when the process restarts.

## Run

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API.

| Method | Route | Result |
|---|---|---|
| `POST` | `/items` | Create an item |
| `GET` | `/items` | List all items |
| `GET` | `/items/{item_id}` | Read one item |
| `PUT` | `/items/{item_id}` | Replace an item |
| `DELETE` | `/items/{item_id}` | Delete an item |

The in-memory store is intentional here; database persistence is covered by
Assignment 2.
