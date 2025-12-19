"""Advanced analysis service for detailed market sentiment insights."""
from __future__ import annotations

import re
from typing import Any

from .ml_services import analyze_sentiment, detect_asset_from_text


def extract_key_insights(text: str, max_insights: int = 5) -> list[str]:
    """Extract key insights and important statements from text."""
    if not text:
        return []

    # Find sentences with financial/market keywords
    financial_keywords = [
        "growth", "surge", "decline", "rise", "fall", "beat", "miss", "expect",
        "forecast", "projection", "estimate", "analyst", "market", "stock",
        "price", "earnings", "revenue", "profit", "loss", "high", "low",
        "record", "all-time", "quarter", "year", "percent", "%", "gdp",
        "inflation", "rate", "cut", "hike"
    ]

    sentences = re.split(r'[.!?]+', text)
    insights = []

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:  # Skip very short sentences
            continue

        sentence_lower = sentence.lower()
        # Check if sentence contains financial keywords
        keyword_count = sum(1 for keyword in financial_keywords if keyword in sentence_lower)

        if keyword_count >= 2:  # At least 2 financial keywords
            # Clean up the sentence
            sentence = re.sub(r'\s+', ' ', sentence).strip()
            if len(sentence) > 200:
                sentence = sentence[:200] + "..."
            insights.append(sentence)

        if len(insights) >= max_insights:
            break

    return insights[:max_insights]


def analyze_market_impact(text: str, sentiment_score: float) -> dict[str, Any]:
    """Analyze potential market impact based on content and sentiment."""
    text_lower = text.lower()

    # Detect market-moving keywords
    positive_indicators = [
        "beat", "surge", "rise", "growth", "high", "record", "strong",
        "positive", "bullish", "gain", "rally", "outperform"
    ]
    negative_indicators = [
        "decline", "fall", "drop", "miss", "weak", "negative", "bearish",
        "loss", "concern", "risk", "worry", "downturn"
    ]

    positive_count = sum(1 for word in positive_indicators if word in text_lower)
    negative_count = sum(1 for word in negative_indicators if word in text_lower)

    # Determine impact level with adjusted thresholds (more sensitive)
    # Also consider keyword counts
    keyword_bias = (positive_count - negative_count) * 0.1
    adjusted_score = sentiment_score + keyword_bias
    
    if adjusted_score > 0.4 or (sentiment_score > 0.3 and positive_count > negative_count + 2):
        impact_level = "HIGH_POSITIVE"
        impact_description = "Strong positive sentiment suggests potential upward movement in the market"
    elif adjusted_score > 0.15 or (sentiment_score > 0.1 and positive_count > negative_count):
        impact_level = "MODERATE_POSITIVE"
        impact_description = "Moderate positive sentiment indicates potential gains and bullish momentum"
    elif adjusted_score < -0.4 or (sentiment_score < -0.3 and negative_count > positive_count + 2):
        impact_level = "HIGH_NEGATIVE"
        impact_description = "Strong negative sentiment indicates potential downward pressure and bearish conditions"
    elif adjusted_score < -0.15 or (sentiment_score < -0.1 and negative_count > positive_count):
        impact_level = "MODERATE_NEGATIVE"
        impact_description = "Moderate negative sentiment suggests potential decline and cautious market conditions"
    else:
        # Even neutral can have slight bias
        if positive_count > negative_count:
            impact_level = "SLIGHTLY_POSITIVE"
            impact_description = "Mixed sentiment with slight positive bias, market may see modest gains"
        elif negative_count > positive_count:
            impact_level = "SLIGHTLY_NEGATIVE"
            impact_description = "Mixed sentiment with slight negative bias, market may see modest decline"
        else:
            impact_level = "NEUTRAL"
            impact_description = "Balanced sentiment, market may remain stable with limited directional movement"

    # Detect time horizon mentions
    time_horizon = "SHORT_TERM"  # default
    if any(word in text_lower for word in ["monday", "tuesday", "week", "immediate", "today"]):
        time_horizon = "IMMEDIATE"
    elif any(word in text_lower for word in ["month", "quarter", "long-term", "sustained"]):
        time_horizon = "LONG_TERM"

    return {
        "impact_level": impact_level,
        "impact_description": impact_description,
        "time_horizon": time_horizon,
        "positive_indicators_count": positive_count,
        "negative_indicators_count": negative_count,
        "sentiment_score": sentiment_score,
    }


def calculate_confidence_score(text: str, sentiment_score: float, asset_detected: bool) -> float:
    """Calculate confidence score based on multiple factors."""
    if not text:
        return 0.0

    # Base confidence from sentiment strength
    base_confidence = abs(sentiment_score)

    # Boost confidence if text is substantial
    text_length_factor = min(1.0, len(text) / 2000)  # Max at 2000 chars

    # Boost if asset was detected
    asset_factor = 0.2 if asset_detected else 0.0

    # Boost if text contains financial terminology
    financial_terms = ["market", "stock", "price", "growth", "earnings", "revenue", "analyst"]
    term_count = sum(1 for term in financial_terms if term in text.lower())
    term_factor = min(0.2, term_count * 0.03)

    confidence = (base_confidence * 0.5) + (text_length_factor * 0.2) + asset_factor + term_factor
    return min(0.95, max(0.1, confidence))  # Clamp between 0.1 and 0.95


def generate_sentiment_summary(text_sentiment: str, image_sentiment: str, combined_sentiment: str, confidence: float) -> str:
    """Generate a human-readable summary of sentiment analysis."""
    sentiment_map = {
        "POSITIVE": "positive",
        "NEGATIVE": "negative",
        "NEUTRAL": "neutral"
    }

    text_sent = sentiment_map.get(text_sentiment.upper(), "neutral")
    image_sent = sentiment_map.get(image_sentiment.upper(), "neutral")
    combined_sent = sentiment_map.get(combined_sentiment.upper(), "neutral")

    confidence_pct = confidence * 100

    if combined_sent == "positive":
        if confidence > 0.7:
            summary = f"Strong positive sentiment detected with {confidence_pct:.1f}% confidence. Both text and visual analysis indicate bullish market conditions."
        else:
            summary = f"Moderate positive sentiment detected with {confidence_pct:.1f}% confidence. The analysis suggests favorable market conditions."
    elif combined_sent == "negative":
        if confidence > 0.7:
            summary = f"Strong negative sentiment detected with {confidence_pct:.1f}% confidence. Both text and visual analysis indicate bearish market conditions."
        else:
            summary = f"Moderate negative sentiment detected with {confidence_pct:.1f}% confidence. The analysis suggests cautious market conditions."
    else:
        summary = f"Neutral sentiment detected with {confidence_pct:.1f}% confidence. Mixed signals suggest market stability with no strong directional bias."

    # Add alignment note
    if text_sent == image_sent:
        summary += " Text and visual sentiment are aligned, increasing reliability."
    else:
        summary += f" Note: Text sentiment is {text_sent} while visual sentiment is {image_sent}, showing some divergence."

    return summary


def detect_asset_priority(text: str) -> str:
    """Improved asset detection with priority for market indices."""
    if not text:
        return None

    text_lower = text.lower()

    # Priority 1: Indian market indices (most specific)
    if "nifty" in text_lower or "nifty 50" in text_lower:
        return "NIFTY-50"
    if "sensex" in text_lower or "bse" in text_lower:
        return "SENSEX"

    # Priority 2: Indian market context
    indian_market_terms = ["indian market", "indian equity", "stock market", "equity market", "dalal street"]
    if any(term in text_lower for term in indian_market_terms):
        # Check which index is mentioned more
        nifty_count = text_lower.count("nifty")
        sensex_count = text_lower.count("sensex") + text_lower.count("bse")
        if nifty_count > sensex_count:
            return "NIFTY-50"
        elif sensex_count > 0:
            return "SENSEX"
        else:
            return "NIFTY-50"  # Default to Nifty for Indian market articles

    # Priority 3: Use existing detection
    return detect_asset_from_text(text)

