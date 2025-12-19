"""ML services for image analysis, OCR, sentiment, and market prediction."""
from __future__ import annotations

import io
import re
from typing import Any, Optional

import numpy as np
from PIL import Image

try:
    import torch
    from torchvision import models, transforms
except ImportError:
    torch = None
    models = None
    transforms = None

try:
    from transformers import pipeline
except ImportError:
    pipeline = None

try:
    import easyocr
except ImportError:
    easyocr = None

# Global model instances (lazy-loaded)
_image_model: Any = None
_sentiment_pipeline: Any = None
_ocr_reader: Any = None


def get_image_model():
    """Load ResNet50 for image feature extraction."""
    if torch is None or models is None or transforms is None:
        raise ImportError("PyTorch and torchvision are required. Install with: pip install torch torchvision")
    global _image_model
    if _image_model is None:
        model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        model.eval()
        _image_model = model
    return _image_model


def get_sentiment_pipeline():
    """Load sentiment analysis pipeline."""
    if pipeline is None:
        raise ImportError("Transformers library is required. Install with: pip install transformers")
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            device=0 if torch and torch.cuda.is_available() else -1,
        )
    return _sentiment_pipeline


def get_ocr_reader():
    """Initialize EasyOCR reader."""
    global _ocr_reader
    if _ocr_reader is None and easyocr is not None:
        _ocr_reader = easyocr.Reader(["en"], gpu=torch.cuda.is_available())
    return _ocr_reader


def extract_image_features(image_bytes: bytes) -> np.ndarray:
    """Extract features from image using ResNet50."""
    if transforms is None:
        raise ImportError("torchvision is required for image feature extraction")
    model = get_image_model()
    transform = transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        features = model(image_tensor)
        features_np = features.squeeze().cpu().numpy()

    return features_np


def extract_text_from_image(image_bytes: bytes) -> str:
    """Extract text from image using OCR."""
    reader = get_ocr_reader()
    if reader is None:
        return ""

    image = Image.open(io.BytesIO(image_bytes))
    image_np = np.array(image)

    results = reader.readtext(image_np)
    extracted_text = " ".join([result[1] for result in results])
    return extracted_text


def analyze_sentiment(text: str) -> dict[str, Any]:
    """Analyze text sentiment using RoBERTa."""
    if not text.strip():
        return {"label": "NEUTRAL", "score": 0.5}

    pipeline_obj = get_sentiment_pipeline()
    result = pipeline_obj(text)[0]

    label_map = {"LABEL_0": "NEGATIVE", "LABEL_1": "NEUTRAL", "LABEL_2": "POSITIVE"}
    label = label_map.get(result["label"], "NEUTRAL")

    return {"label": label, "score": result["score"]}


def infer_image_sentiment(image_features: np.ndarray) -> dict[str, Any]:
    """Infer sentiment from image features (simplified heuristic)."""
    feature_mean = np.mean(image_features)
    feature_std = np.std(image_features)

    if feature_mean > 0.1:
        sentiment = "POSITIVE"
        confidence = min(0.9, 0.5 + abs(feature_mean) * 0.5)
    elif feature_mean < -0.1:
        sentiment = "NEGATIVE"
        confidence = min(0.9, 0.5 + abs(feature_mean) * 0.5)
    else:
        sentiment = "NEUTRAL"
        confidence = 0.6

    return {"label": sentiment, "score": confidence}


def combine_sentiments(image_sent: dict, text_sent: dict) -> dict[str, Any]:
    """Combine image and text sentiments with improved weighting."""
    image_label = image_sent["label"]
    text_label = text_sent["label"]
    image_score = image_sent.get("score", 0.5)
    text_score = text_sent.get("score", 0.5)

    # Weight text sentiment more heavily (70%) since it's more reliable for financial news
    # Image sentiment gets 30% weight
    text_weight = 0.7
    image_weight = 0.3

    # Convert labels to numeric scores
    label_to_score = {"POSITIVE": 1.0, "NEUTRAL": 0.0, "NEGATIVE": -1.0}
    
    image_numeric = label_to_score.get(image_label, 0.0) * image_score
    text_numeric = label_to_score.get(text_label, 0.0) * text_score

    # Weighted combination
    combined_numeric = (text_numeric * text_weight) + (image_numeric * image_weight)
    
    # Determine final label with more nuanced thresholds
    if combined_numeric > 0.15:  # Lower threshold for positive
        final_label = "POSITIVE"
        final_score = min(0.95, 0.5 + abs(combined_numeric) * 0.5)
    elif combined_numeric < -0.15:  # Lower threshold for negative
        final_label = "NEGATIVE"
        final_score = min(0.95, 0.5 + abs(combined_numeric) * 0.5)
    else:
        final_label = "NEUTRAL"
        # Even neutral can have confidence based on how close to neutral it is
        final_score = 0.5 + (0.1 * (1 - abs(combined_numeric)))

    return {
        "label": final_label,
        "score": final_score,
        "image_sentiment": image_label,
        "text_sentiment": text_label,
        "combined_numeric": combined_numeric,
    }


def predict_price_change(sentiment_score: float, current_price: float, horizon_hours: int = 24) -> dict[str, Any]:
    """Simple LSTM-inspired prediction (simplified for demo)."""
    volatility_factor = 0.02
    sentiment_impact = sentiment_score * volatility_factor * (horizon_hours / 24.0)

    predicted_price = current_price * (1 + sentiment_impact)
    price_change_percent = sentiment_impact * 100

    confidence = min(0.95, 0.6 + abs(sentiment_score) * 0.3)

    return {
        "predicted_price": round(predicted_price, 2),
        "price_change_percent": round(price_change_percent, 2),
        "confidence": round(confidence, 2),
    }


# Asset detection mappings
COMPANY_TO_SYMBOL = {
    "apple": "AAPL",
    "tesla": "TSLA",
    "microsoft": "MSFT",
    "google": "GOOGL",
    "amazon": "AMZN",
    "meta": "META",
    "facebook": "META",
    "nvidia": "NVDA",
    "netflix": "NFLX",
    "jpmorgan": "JPM",
    "bank of america": "BAC",
    "goldman sachs": "GS",
    "bitcoin": "BTC-USD",
    "ethereum": "ETH-USD",
    "btc": "BTC-USD",
    "eth": "ETH-USD",
    "crypto": "BTC-USD",  # default fallback
    # Indian market indices
    "nifty": "NIFTY-50",
    "nifty 50": "NIFTY-50",
    "sensex": "SENSEX",
    "bse": "SENSEX",
    "nse": "NIFTY-50",
}

CRYPTO_KEYWORDS = ["bitcoin", "btc", "ethereum", "eth", "crypto", "cryptocurrency", "blockchain"]

INDIAN_MARKET_KEYWORDS = [
    "nifty", "sensex", "bse", "nse", "indian market", "indian equity", 
    "indian stock", "dalal street", "mumbai market", "bombay stock"
]


def detect_asset_from_text(text: str) -> Optional[str]:
    """Automatically detect asset symbol from text using pattern matching and keyword lookup."""
    if not text:
        return None

    text_lower = text.lower()

    # 1. Look for explicit stock symbols (1-5 uppercase letters, possibly with dash)
    stock_pattern = r'\b([A-Z]{1,5}(?:-[A-Z]+)?)\b'
    matches = re.findall(stock_pattern, text)
    # Common abbreviations to exclude
    excluded_abbrevs = {
        "USD", "EUR", "GBP", "INR", "API", "CEO", "CFO", "AI", "ML", 
        "GDP", "RBI", "MPC", "FII", "DII", "IPO", "ETF", "NSE", "BSE"
    }
    for match in matches:
        # Filter out common non-stock words
        if match not in excluded_abbrevs:
            # Check if it looks like a stock symbol
            if len(match) <= 5 or "-" in match:
                return match.upper()

    # 2. Look for company names in text
    for company, symbol in COMPANY_TO_SYMBOL.items():
        if company in text_lower:
            return symbol

    # 3. Look for Indian market indices
    for keyword in INDIAN_MARKET_KEYWORDS:
        if keyword in text_lower:
            if "nifty" in text_lower:
                return "NIFTY-50"
            elif "sensex" in text_lower or "bse" in text_lower:
                return "SENSEX"
            else:
                return "NIFTY-50"  # default Indian market

    # 4. Look for crypto keywords
    for keyword in CRYPTO_KEYWORDS:
        if keyword in text_lower:
            # Try to find specific crypto
            if "bitcoin" in text_lower or "btc" in text_lower:
                return "BTC-USD"
            elif "ethereum" in text_lower or "eth" in text_lower:
                return "ETH-USD"
            else:
                return "BTC-USD"  # default crypto

    # 5. Look for Indian market context (GDP, RBI, market reactions)
    indian_context_keywords = ["gdp", "rbi", "mpc", "indian market", "stock market", "equity market"]
    if any(keyword in text_lower for keyword in indian_context_keywords):
        # Check if it's specifically about Indian markets
        if any(ind_term in text_lower for ind_term in ["india", "indian", "mumbai", "bombay", "dalal"]):
            # Prefer Nifty if mentioned, otherwise Sensex, otherwise default to Nifty
            if "nifty" in text_lower:
                return "NIFTY-50"
            elif "sensex" in text_lower:
                return "SENSEX"
            else:
                return "NIFTY-50"  # Default for Indian market articles

    # 6. Look for common financial terms that might indicate a stock
    financial_terms = ["stock", "shares", "equity", "trading", "market", "price", "earnings"]
    if any(term in text_lower for term in financial_terms):
        # Try to extract company name before these terms
        for term in financial_terms:
            idx = text_lower.find(term)
            if idx > 0:
                # Look for capitalized words before the term (likely company name)
                before_text = text[:idx]
                words = re.findall(r'\b([A-Z][a-z]+)\b', before_text)
                if words:
                    # Check if any word matches a known company
                    for word in words[-3:]:  # Check last 3 capitalized words
                        if word.lower() in COMPANY_TO_SYMBOL:
                            return COMPANY_TO_SYMBOL[word.lower()]

    return None


