"""CRUD API backed by a local SQLite database using SQLAlchemy 2."""

import os
from collections.abc import Generator

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./items.db")
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
app = FastAPI(title="Assignment 2 - Database API", version="1.0.0")


class Base(DeclarativeBase):
    pass


class ItemRecord(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False, default="")


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)


class ItemRead(ItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/items", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate, session: Session = Depends(get_session)
) -> ItemRecord:
    item = ItemRecord(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@app.get("/items", response_model=list[ItemRead])
def list_items(session: Session = Depends(get_session)) -> list[ItemRecord]:
    return list(session.scalars(select(ItemRecord).order_by(ItemRecord.id)))


@app.get("/items/{item_id}", response_model=ItemRead)
def get_item(item_id: int, session: Session = Depends(get_session)) -> ItemRecord:
    item = session.get(ItemRecord, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/items/{item_id}", response_model=ItemRead)
def update_item(
    item_id: int, payload: ItemCreate, session: Session = Depends(get_session)
) -> ItemRecord:
    item = session.get(ItemRecord, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in payload.model_dump().items():
        setattr(item, field, value)
    session.commit()
    session.refresh(item)
    return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, session: Session = Depends(get_session)) -> None:
    item = session.get(ItemRecord, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
