"""Utility to populate database with dummy data."""
from __future__ import annotations

from sqlalchemy import select

from ..db import get_session
from ..models.entities import Asset, SentimentAnalysis, MarketPrediction, build_dummy_data


def ensure_seed_data() -> None:
    """Insert demo rows if the database is empty."""
    session = get_session()
    try:
        existing = session.scalars(select(Asset).limit(1)).first()
        if existing:
            return

        analyses, predictions = build_dummy_data()

        for analysis in analyses:
            session.add(analysis)
        for prediction in predictions:
            session.add(prediction)

        session.commit()
    finally:
        session.close()


