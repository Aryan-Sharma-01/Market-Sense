"""API routes for market sentiment analysis."""
from __future__ import annotations

from flask import Blueprint, abort, jsonify, request
from sqlalchemy import func, select

from ..db import get_session
from ..models.entities import Asset, SentimentAnalysis, MarketPrediction
from ..services.ml_services import (
    combine_sentiments,
    detect_asset_from_text,
    extract_image_features,
    extract_text_from_image,
    infer_image_sentiment,
    predict_price_change,
)
from ..services.sentiment_analyzer import analyze_sentiment_hybrid, enhance_sentiment_with_context
from ..services.url_extractor import fetch_article_from_url
from ..services.advanced_analysis import (
    analyze_market_impact,
    calculate_confidence_score,
    extract_key_insights,
    generate_sentiment_summary,
    detect_asset_priority,
)

api_bp = Blueprint("api", __name__)


@api_bp.post("/analyze")
def analyze_image():
    """Analyze image for sentiment and extract text."""
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files["image"]
    asset_symbol = request.form.get("symbol", "").strip()
    source_url = request.form.get("source_url", "")

    image_bytes = image_file.read()

    # Extract features and text
    image_features = extract_image_features(image_bytes)
    extracted_text = extract_text_from_image(image_bytes)

    # Auto-detect asset symbol from text if not provided
    if not asset_symbol and extracted_text:
        detected_symbol = detect_asset_from_text(extracted_text)
        if detected_symbol:
            asset_symbol = detected_symbol

    # Fallback to generic symbol if still not found
    if not asset_symbol:
        asset_symbol = "MARKET-GENERAL"
        asset_name = "General Market"
        asset_type = "stock"
    else:
        # Determine asset type
        if "-USD" in asset_symbol.upper() or asset_symbol.upper() in ["BTC", "ETH"]:
            asset_type = "crypto"
            asset_name = asset_symbol.replace("-USD", "").upper()
        else:
            asset_type = "stock"
            asset_name = asset_symbol

    # Analyze sentiments
    image_sent = infer_image_sentiment(image_features)
    text_sent = analyze_sentiment(extracted_text) if extracted_text else {"label": "NEUTRAL", "score": 0.5}
    combined = combine_sentiments(image_sent, text_sent)

    # Get or create asset
    session = get_session()
    try:
        asset = session.scalar(select(Asset).where(Asset.symbol == asset_symbol))
        if not asset:
            asset = Asset(symbol=asset_symbol, name=asset_name, asset_type=asset_type)
            session.add(asset)
            session.commit()

        # Save analysis
        analysis = SentimentAnalysis(
            asset_id=asset.id,
            source_url=source_url,
            extracted_text=extracted_text,
            image_sentiment=image_sent["label"].lower(),
            text_sentiment=text_sent["label"].lower(),
            combined_sentiment=combined["label"].lower(),
            confidence=combined["score"],
        )
        session.add(analysis)
        session.commit()

        return jsonify(
            {
                "analysis_id": analysis.id,
                "detected_asset": asset_symbol,
                "asset_name": asset.name,
                "extracted_text": extracted_text,
                "image_sentiment": image_sent["label"],
                "text_sentiment": text_sent["label"],
                "combined_sentiment": combined["label"],
                "confidence": combined["score"],
            }
        )
    finally:
        session.close()


@api_bp.post("/analyze-url")
def analyze_url():
    """Analyze article from URL for sentiment."""
    data = request.json or {}
    url = data.get("url", "").strip()
    asset_symbol = data.get("symbol", "").strip()

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Fetch article content from URL
        article_data = fetch_article_from_url(url)
        extracted_text = article_data["text"]
        article_title = article_data["title"]
        image_bytes = article_data.get("image_bytes")

        # Auto-detect asset symbol from text if not provided (with priority)
        if not asset_symbol and extracted_text:
            detected_symbol = detect_asset_priority(extracted_text)
            if detected_symbol:
                asset_symbol = detected_symbol

        # Fallback to generic symbol if still not found
        if not asset_symbol:
            asset_symbol = "MARKET-GENERAL"
            asset_name = "General Market"
            asset_type = "stock"
        else:
            # Determine asset type
            if "-USD" in asset_symbol.upper() or asset_symbol.upper() in ["BTC", "ETH"]:
                asset_type = "crypto"
                asset_name = asset_symbol.replace("-USD", "").upper()
            elif asset_symbol in ["NIFTY-50", "SENSEX"]:
                asset_type = "index"
                asset_name = asset_symbol
            else:
                asset_type = "stock"
                asset_name = asset_symbol

        # Analyze text sentiment using hybrid approach
        if extracted_text:
            text_sent = analyze_sentiment_hybrid(extracted_text)
            # Enhance with context
            text_sent = enhance_sentiment_with_context(extracted_text, text_sent)
        else:
            text_sent = {"label": "NEUTRAL", "score": 0.5}

        # Analyze image if available
        # For articles, image sentiment should align more with text (images are usually illustrations)
        image_sent = {"label": "NEUTRAL", "score": 0.5}
        if image_bytes:
            try:
                image_features = extract_image_features(image_bytes)
                image_sent = infer_image_sentiment(image_features)
            except Exception:
                # If image processing fails, align with text sentiment (articles use illustrative images)
                if extracted_text:
                    image_sent = {
                        "label": text_sent["label"],
                        "score": text_sent["score"] * 0.8,  # Slightly lower confidence for inferred
                    }
                pass
        else:
            # No image available, align with text sentiment for articles
            if extracted_text:
                image_sent = {
                    "label": text_sent["label"],
                    "score": text_sent["score"] * 0.7,  # Lower confidence when no image
                }

        combined = combine_sentiments(image_sent, text_sent)

        # Advanced analysis - use combined_numeric if available, otherwise convert
        if "combined_numeric" in combined:
            sentiment_score = combined["combined_numeric"]  # Already in -1 to 1 scale
        else:
            # Fallback conversion
            if combined["label"] == "POSITIVE":
                sentiment_score = (combined["score"] - 0.5) * 2  # Convert 0.5-1.0 to 0.0-1.0
            elif combined["label"] == "NEGATIVE":
                sentiment_score = -((combined["score"] - 0.5) * 2)  # Convert to negative
            else:
                sentiment_score = 0.0

        # Calculate proper confidence
        confidence = calculate_confidence_score(extracted_text, sentiment_score, bool(asset_symbol))

        # Extract key insights
        key_insights = extract_key_insights(extracted_text, max_insights=5)

        # Analyze market impact
        market_impact = analyze_market_impact(extracted_text, sentiment_score)

        # Generate summary
        sentiment_summary = generate_sentiment_summary(
            text_sent["label"], image_sent["label"], combined["label"], confidence
        )

        # Get or create asset
        session = get_session()
        try:
            asset = session.scalar(select(Asset).where(Asset.symbol == asset_symbol))
            if not asset:
                asset = Asset(symbol=asset_symbol, name=asset_name, asset_type=asset_type)
                session.add(asset)
                session.commit()

            # Save analysis
            analysis = SentimentAnalysis(
                asset_id=asset.id,
                source_url=url,
                extracted_text=extracted_text[:5000] if extracted_text else None,  # Limit text length
                image_sentiment=image_sent["label"].lower(),
                text_sentiment=text_sent["label"].lower(),
                combined_sentiment=combined["label"].lower(),
                confidence=confidence,
            )
            session.add(analysis)
            session.commit()

            return jsonify(
                {
                    "analysis_id": analysis.id,
                    "article_title": article_title,
                    "detected_asset": asset_symbol,
                    "asset_name": asset.name,
                    "asset_type": asset_type,
                    "source_url": url,
                    "text_preview": extracted_text[:500] if extracted_text else None,
                    "full_text_length": len(extracted_text) if extracted_text else 0,
                    "sentiment_analysis": {
                        "image_sentiment": {
                            "label": image_sent["label"],
                            "score": image_sent.get("score", 0.5),
                        },
                        "text_sentiment": {
                            "label": text_sent["label"],
                            "score": text_sent.get("score", 0.5),
                        },
                        "combined_sentiment": {
                            "label": combined["label"],
                            "score": sentiment_score,
                        },
                        "confidence": confidence,
                        "summary": sentiment_summary,
                    },
                    "market_impact": market_impact,
                    "key_insights": key_insights,
                    "analysis_timestamp": analysis.created_at.isoformat(),
                }
            )
        finally:
            session.close()

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@api_bp.get("/assets")
def list_assets():
    """List all tracked assets."""
    session = get_session()
    try:
        assets = session.scalars(select(Asset)).all()
        return jsonify(
            {
                "assets": [
                    {
                        "id": a.id,
                        "symbol": a.symbol,
                        "name": a.name,
                        "asset_type": a.asset_type,
                    }
                    for a in assets
                ]
            }
        )
    finally:
        session.close()


@api_bp.get("/assets/<int:asset_id>/analyses")
def get_asset_analyses(asset_id: int):
    """Get sentiment analyses for an asset."""
    session = get_session()
    try:
        asset = session.get(Asset, asset_id)
        if not asset:
            abort(404, description="Asset not found")

        analyses = (
            session.scalars(
                select(SentimentAnalysis)
                .where(SentimentAnalysis.asset_id == asset_id)
                .order_by(SentimentAnalysis.created_at.desc())
            ).all()
        )

        return jsonify(
            {
                "asset": {"id": asset.id, "symbol": asset.symbol, "name": asset.name},
                "analyses": [
                    {
                        "id": a.id,
                        "source_url": a.source_url,
                        "extracted_text": a.extracted_text,
                        "combined_sentiment": a.combined_sentiment,
                        "confidence": a.confidence,
                        "created_at": a.created_at.isoformat(),
                    }
                    for a in analyses
                ],
            }
        )
    finally:
        session.close()


@api_bp.get("/assets/<int:asset_id>/predictions")
def get_asset_predictions(asset_id: int):
    """Get market predictions for an asset."""
    session = get_session()
    try:
        asset = session.get(Asset, asset_id)
        if not asset:
            abort(404, description="Asset not found")

        predictions = (
            session.scalars(
                select(MarketPrediction)
                .where(MarketPrediction.asset_id == asset_id)
                .order_by(MarketPrediction.created_at.desc())
            ).all()
        )

        return jsonify(
            {
                "asset": {"id": asset.id, "symbol": asset.symbol, "name": asset.name},
                "predictions": [
                    {
                        "id": p.id,
                        "current_price": p.current_price,
                        "predicted_price": p.predicted_price,
                        "price_change_percent": p.price_change_percent,
                        "sentiment_score": p.sentiment_score,
                        "confidence": p.confidence,
                        "created_at": p.created_at.isoformat(),
                    }
                    for p in predictions
                ],
            }
        )
    finally:
        session.close()


@api_bp.post("/predict")
def create_prediction():
    """Create a market prediction based on sentiment."""
    data = request.json or {}
    asset_id = data.get("asset_id")
    current_price = data.get("current_price")
    sentiment_score = data.get("sentiment_score", 0.0)
    horizon_hours = data.get("horizon_hours", 24)

    if not asset_id or not current_price:
        return jsonify({"error": "asset_id and current_price required"}), 400

    session = get_session()
    try:
        asset = session.get(Asset, asset_id)
        if not asset:
            abort(404, description="Asset not found")

        prediction_data = predict_price_change(sentiment_score, current_price, horizon_hours)

        prediction = MarketPrediction(
            asset_id=asset_id,
            current_price=current_price,
            predicted_price=prediction_data["predicted_price"],
            price_change_percent=prediction_data["price_change_percent"],
            sentiment_score=sentiment_score,
            prediction_horizon=horizon_hours,
            confidence=prediction_data["confidence"],
        )
        session.add(prediction)
        session.commit()

        return jsonify(
            {
                "prediction_id": prediction.id,
                "current_price": prediction.current_price,
                "predicted_price": prediction.predicted_price,
                "price_change_percent": prediction.price_change_percent,
                "confidence": prediction.confidence,
            }
        )
    finally:
        session.close()


@api_bp.get("/dashboard")
def get_dashboard_stats():
    """Get dashboard statistics."""
    session = get_session()
    try:
        total_assets = session.scalar(select(func.count(Asset.id))) or 0
        total_analyses = session.scalar(select(func.count(SentimentAnalysis.id))) or 0
        total_predictions = session.scalar(select(func.count(MarketPrediction.id))) or 0

        recent_analyses = (
            session.scalars(
                select(SentimentAnalysis).order_by(SentimentAnalysis.created_at.desc()).limit(5)
            ).all()
        )

        return jsonify(
            {
                "stats": {
                    "total_assets": total_assets,
                    "total_analyses": total_analyses,
                    "total_predictions": total_predictions,
                },
                "recent_analyses": [
                    {
                        "id": a.id,
                        "asset_symbol": a.asset.symbol,
                        "sentiment": a.combined_sentiment,
                        "confidence": a.confidence,
                        "created_at": a.created_at.isoformat(),
                    }
                    for a in recent_analyses
                ],
            }
        )
    finally:
        session.close()


