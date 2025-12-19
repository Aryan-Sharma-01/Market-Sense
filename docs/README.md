# Documentation

This folder contains project documentation including architecture diagrams, API specifications, and usage guides.

## Project Overview

The Visual Sentiment Analysis for Market Prediction system combines:
- **Computer Vision**: ResNet50 for image feature extraction
- **OCR**: EasyOCR for text extraction from images
- **NLP**: RoBERTa-based sentiment analysis
- **Time-Series Prediction**: LSTM-inspired price prediction models

## Quick Start

1. **Backend Setup**:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   flask --app app.main run --debug
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```

3. **Access**: Open `http://localhost:3000` in your browser

## Architecture

- **Backend**: Flask REST API with SQLite database
- **Frontend**: Next.js with TypeScript
- **ML Models**: Pre-trained models loaded on-demand
- **Database**: SQLite with seeded demo data


