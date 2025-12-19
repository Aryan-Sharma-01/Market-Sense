"""ORM entities for the market sentiment analysis backend."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(20), nullable=False)  # stock, crypto

    analyses: Mapped[list["SentimentAnalysis"]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )
    predictions: Mapped[list["MarketPrediction"]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Asset {self.symbol}>"


class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    image_path: Mapped[Optional[str]] = mapped_column(String(500))
    extracted_text: Mapped[Optional[str]] = mapped_column(Text)
    image_sentiment: Mapped[str] = mapped_column(String(20))  # positive, negative, neutral
    text_sentiment: Mapped[str] = mapped_column(String(20))
    combined_sentiment: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    extra_metadata: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    asset: Mapped[Asset] = relationship(back_populates="analyses")


class MarketPrediction(Base):
    __tablename__ = "market_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    predicted_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    price_change_percent: Mapped[float] = mapped_column(Float)
    sentiment_score: Mapped[float] = mapped_column(Float)
    prediction_horizon: Mapped[int] = mapped_column(Integer)  # hours
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    asset: Mapped[Asset] = relationship(back_populates="predictions")


def build_dummy_data() -> tuple[list[SentimentAnalysis], list[MarketPrediction]]:
    """Create sample sentiment analyses and predictions for testing."""
    btc = Asset(symbol="BTC-USD", name="Bitcoin", asset_type="crypto")
    tsla = Asset(symbol="TSLA", name="Tesla Inc", asset_type="stock")
    aapl = Asset(symbol="AAPL", name="Apple Inc", asset_type="stock")

    analyses = [
        SentimentAnalysis(
            asset=btc,
            source_url="https://twitter.com/example/status/123",
            extracted_text="Bitcoin reaches new all-time high! Bullish momentum continues.",
            image_sentiment="positive",
            text_sentiment="positive",
            combined_sentiment="positive",
            confidence=0.87,
        ),
        SentimentAnalysis(
            asset=tsla,
            source_url="https://reddit.com/r/stocks/example",
            extracted_text="Tesla announces new factory expansion plans",
            image_sentiment="positive",
            text_sentiment="positive",
            combined_sentiment="positive",
            confidence=0.75,
        ),
        SentimentAnalysis(
            asset=aapl,
            source_url="https://twitter.com/example/status/456",
            extracted_text="Apple faces supply chain challenges",
            image_sentiment="neutral",
            text_sentiment="negative",
            combined_sentiment="negative",
            confidence=0.65,
        ),
    ]

    predictions = [
        MarketPrediction(
            asset=btc,
            current_price=45000.0,
            predicted_price=46500.0,
            price_change_percent=3.33,
            sentiment_score=0.87,
            prediction_horizon=24,
            confidence=0.82,
        ),
        MarketPrediction(
            asset=tsla,
            current_price=250.0,
            predicted_price=258.5,
            price_change_percent=3.4,
            sentiment_score=0.75,
            prediction_horizon=12,
            confidence=0.78,
        ),
        MarketPrediction(
            asset=aapl,
            current_price=175.0,
            predicted_price=172.0,
            price_change_percent=-1.71,
            sentiment_score=-0.65,
            prediction_horizon=24,
            confidence=0.70,
        ),
    ]

    return analyses, predictions

