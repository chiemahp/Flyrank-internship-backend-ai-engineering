"""A small server-rendered inventory app with a persistent SQLite database."""

import os
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "items.db")))
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@asynccontextmanager
async def lifespan(_: FastAPI):
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 120),
                description TEXT NOT NULL DEFAULT ''
                    CHECK(length(description) <= 1000)
            )
            """
        )
    yield


app = FastAPI(title="Assignment 4 - Docker Full Stack", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    with connect() as connection:
        items = connection.execute("SELECT id, name, description FROM items ORDER BY id").fetchall()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"items": items},
    )


@app.post("/items")
def create_item(
    name: Annotated[str, Form(min_length=1, max_length=120)],
    description: Annotated[str, Form(max_length=1000)] = "",
) -> RedirectResponse:
    with connect() as connection:
        connection.execute(
            "INSERT INTO items (name, description) VALUES (?, ?)",
            (name.strip(), description.strip()),
        )
    return RedirectResponse("/", status_code=303)


@app.post("/items/{item_id}/delete")
def delete_item(item_id: int) -> RedirectResponse:
    with connect() as connection:
        connection.execute("DELETE FROM items WHERE id = ?", (item_id,))
    return RedirectResponse("/", status_code=303)
