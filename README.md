# Visual Sentiment Analysis for Market Prediction

An AI-powered system that analyzes images and videos from social media to gauge public sentiment and predict short-term market movements of stocks and cryptocurrencies.

## Tech Stack

- **Backend**: Python, Flask, SQLite
- **Frontend**: Next.js, TypeScript, React
- **ML Models**: 
  - ResNet (CNN) for image feature extraction
  - OCR (Tesseract/EasyOCR) for text extraction
  - Sentiment Classifier (BERT/RoBERTa)
  - LSTM/Transformer for time-series prediction
- **Data Sources**: Twitter/Reddit APIs, Yahoo Finance, Alpha Vantage

## Project Structure

- `backend/`: Flask API with ML inference services
- `frontend/`: Next.js dashboard for visualization
- `models/`: Pre-trained models and training scripts
- `data/`: Datasets and sample data
- `docs/`: Documentation

## Quick Start

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
flask --app app.main run --debug
```

### Frontend
```bash
cd frontend
pnpm install
pnpm dev
```


