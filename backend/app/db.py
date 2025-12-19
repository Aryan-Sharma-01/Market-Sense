"""Database configuration helpers using SQLAlchemy."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker


class Base(DeclarativeBase):
    """Base class for ORM models."""


_SessionFactory: Optional[scoped_session] = None


def init_db(app: Flask) -> None:
    """Configure the SQLAlchemy engine and session factory for the app."""
    global _SessionFactory

    database_url = app.config.get("DATABASE_URL")
    if not database_url:
        instance_path = Path(app.instance_path)
        instance_path.mkdir(parents=True, exist_ok=True)
        database_url = f"sqlite:///{instance_path / 'market_sentiment.db'}"
        app.config["DATABASE_URL"] = database_url

    engine = create_engine(database_url, future=True)
    _SessionFactory = scoped_session(
        sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    )

    from .models import entities  # noqa: F401

    Base.metadata.create_all(engine)


def get_session():
    if _SessionFactory is None:
        raise RuntimeError("Database has not been initialised. Call init_db first.")
    return _SessionFactory()


def remove_session(exception: Exception | None = None) -> None:
    if _SessionFactory:
        _SessionFactory.remove()


