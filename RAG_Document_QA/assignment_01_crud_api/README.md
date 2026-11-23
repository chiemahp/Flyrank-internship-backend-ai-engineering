# Assignment 1 — CRUD API

This project is a small FastAPI application that manages a simple `Item` resource using an in-memory store. It demonstrates the basic CRUD operations needed for a backend API: create, read, update, and delete.

## Features

- FastAPI application with automatic OpenAPI docs
- In-memory persistence for `Item` records
- Validation for item names and descriptions
- Health check endpoint
- Thread-safe updates using a lock

## Project files

- `main.py` — API logic and data model
- `requirements.txt` — Python dependencies

## Requirements

- Python 3.10+
- pip

## Setup and run

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

After starting the server, open the Swagger UI here:

- `http://127.0.0.1:8000/docs`

## API endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/health` | Returns the app health status |
| `POST` | `/items` | Creates a new item |
| `GET` | `/items` | Lists all items |
| `GET` | `/items/{item_id}` | Gets a single item by ID |
| `PUT` | `/items/{item_id}` | Updates an item |
| `DELETE` | `/items/{item_id}` | Deletes an item |

## Example request

Create an item:

```json
{
  "name": "Laptop",
  "description": "14-inch ultrabook"
}
```

Response:

```json
{
  "id": 1,
  "name": "Laptop",
  "description": "14-inch ultrabook"
}
```

## Notes

- Data is stored in memory only and is lost when the server process restarts.
- The API is intentionally simple and is meant to support learning and assignment work.
