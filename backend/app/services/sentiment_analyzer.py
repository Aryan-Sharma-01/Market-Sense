"""Advanced sentiment analysis with keyword-based fallback."""
from __future__ import annotations

import re
from typing import Any

# Financial sentiment keywords with weights
POSITIVE_KEYWORDS = {
    # Strong positive
    "surge": 0.9, "soar": 0.9, "rally": 0.9, "jump": 0.85, "spike": 0.85,
    "record high": 0.95, "all-time high": 0.95, "new high": 0.9, "peak": 0.85,
    "beat": 0.8, "exceed": 0.8, "outperform": 0.85, "surpass": 0.8,
    "strong": 0.75, "robust": 0.8, "solid": 0.7, "healthy": 0.7,
    "growth": 0.7, "expand": 0.7, "rise": 0.65, "increase": 0.65,
    "bullish": 0.9, "optimistic": 0.8, "positive": 0.75, "favorable": 0.75,
    "gain": 0.7, "profit": 0.7, "earnings beat": 0.85, "revenue growth": 0.75,
    "momentum": 0.7, "uptrend": 0.75, "recovery": 0.7, "rebound": 0.75,
    "accelerate": 0.75, "boost": 0.7, "improve": 0.65, "strengthen": 0.7,
}

NEGATIVE_KEYWORDS = {
    # Strong negative
    "plunge": 0.9, "crash": 0.95, "collapse": 0.95, "tumble": 0.85, "slump": 0.85,
    "record low": 0.95, "all-time low": 0.95, "new low": 0.9, "bottom": 0.85,
    "miss": 0.8, "disappoint": 0.8, "underperform": 0.85, "fall short": 0.8,
    "weak": 0.75, "poor": 0.8, "decline": 0.7, "drop": 0.7, "fall": 0.65,
    "bearish": 0.9, "pessimistic": 0.8, "negative": 0.75, "unfavorable": 0.75,
    "loss": 0.7, "deficit": 0.75, "earnings miss": 0.85, "revenue decline": 0.75,
    "downtrend": 0.75, "recession": 0.85, "crisis": 0.9, "concern": 0.7,
    "worry": 0.7, "risk": 0.65, "uncertainty": 0.7, "volatility": 0.65,
    "slowdown": 0.75, "contraction": 0.8, "deteriorate": 0.75, "weaken": 0.7,
}

NEUTRAL_KEYWORDS = {
    "stable": 0.5, "flat": 0.5, "unchanged": 0.5, "maintain": 0.5,
    "mixed": 0.5, "varied": 0.5, "uncertain": 0.5,
}


def analyze_sentiment_keywords(text: str) -> dict[str, Any]:
    """Analyze sentiment using keyword matching with weighted scoring."""
    if not text:
        return {"label": "NEUTRAL", "score": 0.5}

    text_lower = text.lower()
    
    # Count and weight positive keywords
    positive_score = 0.0
    positive_count = 0
    for keyword, weight in POSITIVE_KEYWORDS.items():
        count = text_lower.count(keyword)
        if count > 0:
            positive_score += weight * min(count, 3)  # Cap at 3 occurrences
            positive_count += count

    # Count and weight negative keywords
    negative_score = 0.0
    negative_count = 0
    for keyword, weight in NEGATIVE_KEYWORDS.items():
        count = text_lower.count(keyword)
        if count > 0:
            negative_score += weight * min(count, 3)
            negative_count += count

    # Normalize scores based on text length and keyword density
    text_length = len(text.split())
    if text_length > 0:
        # Normalize by text length (longer texts need more keywords)
        normalization_factor = max(1.0, text_length / 200)
        positive_score = positive_score / normalization_factor
        negative_score = negative_score / normalization_factor

    # Calculate net sentiment
    net_sentiment = positive_score - negative_score
    
    # Determine label and score
    if net_sentiment > 0.3:
        label = "POSITIVE"
        # Convert to 0-1 scale, with stronger signals getting higher scores
        score = min(0.95, 0.5 + (net_sentiment * 0.5))
    elif net_sentiment < -0.3:
        label = "NEGATIVE"
        score = min(0.95, 0.5 + (abs(net_sentiment) * 0.5))
    else:
        label = "NEUTRAL"
        # Even neutral can have some confidence based on keyword presence
        total_keywords = positive_count + negative_count
        if total_keywords > 0:
            score = 0.5 + (min(total_keywords, 10) * 0.02)  # Slight boost for keyword presence
        else:
            score = 0.5

    return {
        "label": label,
        "score": score,
        "positive_keywords": positive_count,
        "negative_keywords": negative_count,
        "net_sentiment": net_sentiment,
    }


def analyze_sentiment_hybrid(text: str) -> dict[str, Any]:
    """Hybrid sentiment analysis: Try ML model first, fallback to keyword analysis."""
    if not text:
        return {"label": "NEUTRAL", "score": 0.5}

    # Try ML-based sentiment first
    try:
        from .ml_services import get_sentiment_pipeline
        pipeline_obj = get_sentiment_pipeline()
        if pipeline_obj:
            result = pipeline_obj(text[:512])[0]  # Limit length for model
            label_map = {"LABEL_0": "NEGATIVE", "LABEL_1": "NEUTRAL", "LABEL_2": "POSITIVE"}
            label = label_map.get(result["label"], "NEUTRAL")
            ml_score = result["score"]
            
            # Use ML result
            return {"label": label, "score": ml_score, "method": "ml"}
    except Exception:
        pass  # Fall through to keyword analysis

    # Fallback to keyword-based analysis
    keyword_result = analyze_sentiment_keywords(text)
    keyword_result["method"] = "keyword"
    return keyword_result


def enhance_sentiment_with_context(text: str, base_sentiment: dict[str, Any]) -> dict[str, Any]:
    """Enhance sentiment analysis with contextual clues."""
    text_lower = text.lower()
    
    # Check for negation patterns that flip sentiment
    negation_words = ["not", "no", "never", "neither", "nobody", "none", "nothing", "nowhere"]
    
    # Check for intensifiers
    intensifiers = {
        "very": 1.2, "extremely": 1.3, "highly": 1.2, "significantly": 1.25,
        "substantially": 1.2, "dramatically": 1.3, "sharply": 1.25,
        "slightly": 0.8, "somewhat": 0.85, "moderately": 0.9,
    }
    
    # Check for question patterns (often indicate uncertainty)
    question_indicators = text.count("?") > 0 or any(word in text_lower for word in ["how", "what", "will", "may", "might", "could"])
    
    # Adjust score based on context
    adjusted_score = base_sentiment["score"]
    adjusted_label = base_sentiment["label"]
    
    # If it's a question about market reaction, it's often slightly positive (curiosity/interest)
    if question_indicators and "market" in text_lower:
        if adjusted_label == "NEUTRAL":
            adjusted_score = 0.55  # Slight positive bias for market questions
            adjusted_label = "POSITIVE"
    
    # Apply intensifier adjustments
    for intensifier, multiplier in intensifiers.items():
        if intensifier in text_lower:
            if adjusted_label != "NEUTRAL":
                adjusted_score = min(0.95, adjusted_score * multiplier)
            break
    
    return {
        "label": adjusted_label,
        "score": min(0.95, max(0.05, adjusted_score)),
        "original_score": base_sentiment["score"],
        "enhanced": True,
    }

