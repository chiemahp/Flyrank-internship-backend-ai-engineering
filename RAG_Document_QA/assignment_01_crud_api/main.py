"""Small in-memory CRUD API for the assignment's Item resource."""

from itertools import count
from threading import Lock

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Assignment 1 - CRUD API", version="1.0.0")


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)


class Item(ItemCreate):
    id: int


_items: dict[int, Item] = {}
_ids = count(1)
_lock = Lock()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate) -> Item:
    with _lock:
        item = Item(id=next(_ids), **payload.model_dump())
        _items[item.id] = item
        return item


@app.get("/items", response_model=list[Item])
def list_items() -> list[Item]:
    with _lock:
        return list(_items.values())


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    with _lock:
        item = _items.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, payload: ItemCreate) -> Item:
    with _lock:
        if item_id not in _items:
            raise HTTPException(status_code=404, detail="Item not found")
        item = Item(id=item_id, **payload.model_dump())
        _items[item_id] = item
        return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    with _lock:
        if _items.pop(item_id, None) is None:
            raise HTTPException(status_code=404, detail="Item not found")
