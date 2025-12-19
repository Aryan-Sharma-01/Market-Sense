# Backend Service

Flask-based API for visual sentiment analysis and market prediction.

## Features

- Image feature extraction using ResNet50
- OCR text extraction from images
- Sentiment analysis using RoBERTa
- Market price prediction based on sentiment
- SQLite database with seeded demo data

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
flask --app app.main run --debug
```

## API Endpoints

- `GET /healthz` - Health check
- `GET /api/dashboard` - Dashboard statistics
- `GET /api/assets` - List all tracked assets
- `POST /api/analyze` - Analyze image for sentiment (multipart form: image, symbol, source_url)
- `GET /api/assets/<id>/analyses` - Get sentiment analyses for an asset
- `GET /api/assets/<id>/predictions` - Get predictions for an asset
- `POST /api/predict` - Create a market prediction


