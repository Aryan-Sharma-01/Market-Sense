# Architecture Diagrams

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Next.js Dashboard (TypeScript/React)                    │   │
│  │  - Image Upload Component                                 │   │
│  │  - Dashboard Statistics                                   │   │
│  │  - Recent Analyses Display                                 │   │
│  │  - Real-time Data Refresh                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API Layer                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Flask REST API (Python)                                 │   │
│  │  - /api/analyze (POST) - Image analysis                  │   │
│  │  - /api/analyze-url (POST) - URL-based analysis          │   │
│  │  - /api/assets (GET) - Asset listing                     │   │
│  │  - /api/dashboard (GET) - Statistics                      │   │
│  │  - /api/predict (POST) - Price prediction                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                             │
        ▼                                             ▼
┌──────────────────┐                    ┌──────────────────┐
│  ML Services     │                    │  Database Layer   │
│  Pipeline        │                    │  (SQLite)         │
└──────────────────┘                    └──────────────────┘
```

## Multi-Modal Analysis Pipeline

```
        ┌─────────────┐      ┌─────────────┐
        │ Image Input │      │  URL Input  │
        │  (Upload)   │      │  (Article)  │
        └──────┬──────┘      └──────┬──────┘
               │                    │
               │                    ▼
               │            ┌──────────────┐
               │            │ BeautifulSoup │
               │            │  Web Scraper │
               │            │              │
               │            │ Extract Text │
               │            │  + Images    │
               │            └──────┬───────┘
               │                   │
        ┌──────┴───────────────────┴──────┐
        │                                    │
        ▼                                    ▼
┌──────────────┐                      ┌──────────────┐
│  ResNet50    │                      │   EasyOCR    │
│  (PyTorch)   │                      │   (OCR)      │
│              │                      │              │
│ Extract      │                      │ Extract      │
│ Image        │                      │ Text         │
│ Features     │                      │ Overlays     │
└──────┬───────┘                      └──────┬───────┘
       │                                      │
       │                                      ▼
       │                            ┌──────────────┐
       │                            │   RoBERTa    │
       │                            │ (Transformers│
       │                            │   Hugging    │
       │                            │    Face)     │
       │                            │              │
       │                            │ Text         │
       │                            │ Sentiment    │
       │                            │ (Hybrid:     │
       │                            │  RoBERTa +   │
       │                            │  Keywords)   │
       │                            └──────┬───────┘
       │                                   │
       └───────────┬──────────────────────┘
                   │
                   ▼
          ┌─────────────────┐
          │  Advanced       │
          │  Fusion Module  │
          │                 │
          │ Weighted Combine│
          │ (70% Text +     │
          │  30% Image)     │
          │ Context Enhance │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │  Asset Detection│
          │  (Priority-based│
          │   NIFTY/SENSEX) │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │  Market Impact  │
          │  Analysis       │
          │                 │
          │ - Impact Level  │
          │ - Time Horizon  │
          │ - Indicators   │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │  Key Insights   │
          │  Extraction     │
          │  (Top 5 phrases)│
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │  Prediction     │
          │  Engine         │
          │                 │
          │ LSTM-inspired   │
          │ Price Forecast  │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │  SQLite DB      │
          │  Storage        │
          └─────────────────┘
```

## Component Interaction Sequence

```
User          Frontend        Flask API      Services         Database
 │               │                │               │               │
 │──URL/Image───>│               │               │               │
 │               │──POST /analyze─>│              │               │
 │               │  -url          │               │               │
 │               │                │──fetch URL──>│               │
 │               │                │  (if URL)    │               │
 │               │                │              │               │
 │               │                │<─article─────│               │
 │               │                │  content     │               │
 │               │                │              │               │
 │               │                │──extract───>│               │
 │               │                │  features    │               │
 │               │                │              │               │
 │               │                │<─image──────│               │
 │               │                │  features    │               │
 │               │                │              │               │
 │               │                │──OCR───────>│               │
 │               │                │  extract     │               │
 │               │                │              │               │
 │               │                │<─text───────│               │
 │               │                │              │               │
 │               │                │──detect─────>│               │
 │               │                │  asset       │               │
 │               │                │              │               │
 │               │                │<─asset───────│               │
 │               │                │  symbol     │               │
 │               │                │              │               │
 │               │                │──sentiment──>│               │
 │               │                │  (hybrid)    │               │
 │               │                │              │               │
 │               │                │<─sentiment───│               │
 │               │                │  + keywords  │               │
 │               │                │              │               │
 │               │                │──fuse───────>│               │
 │               │                │  combine     │               │
 │               │                │              │               │
 │               │                │<─combined────│               │
 │               │                │  sentiment   │               │
 │               │                │              │               │
 │               │                │──impact─────>│               │
 │               │                │  analyze     │               │
 │               │                │              │               │
 │               │                │<─impact──────│               │
 │               │                │  + insights  │               │
 │               │                │              │               │
 │               │                │──save───────>│               │
 │               │                │              │               │
 │               │                │              │──INSERT──────>│
 │               │                │              │               │
 │               │                │              │<─success─────│
 │               │                │<─analysis────│               │
 │               │                │  (detailed)  │               │
 │               │<─JSON Response─│              │               │
 │<─Display───────│                │              │               │
 │  (Advanced UI) │                │              │               │
```

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    External Data Sources                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Twitter    │  │    Reddit    │  │  News Sites   │      │
│  │    API       │  │     API     │  │   (Scraping) │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │               │
│         └─────────────────┴──────────────────┘               │
│                            │                                   │
│                            ▼                                   │
│                   ┌─────────────────┐                         │
│                   │  Image/Video    │                         │
│                   │  Content        │                         │
│                   └────────┬────────┘                         │
└────────────────────────────┼──────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Processing     │
                    │  Pipeline       │
                    └────────┬────────┘
                             │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  ResNet50    │    │   EasyOCR    │    │   RoBERTa    │
│  Features    │    │   Text       │    │  Sentiment   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Fusion &       │
                  │  Prediction     │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  SQLite DB      │
                  │  - Assets       │
                  │  - Analyses     │
                  │  - Predictions  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Dashboard      │
                  │  Visualization  │
                  └─────────────────┘
```

## Technology Stack Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────┐      │
│  │   Next.js Frontend   │    │   Flask Backend      │      │
│  │   - React/TS         │◄──►│   - Python           │      │
│  │   - Recharts         │    │   - REST API         │      │
│  └──────────────────────┘    └──────────────────────┘      │
│                                                              │
┌─────────────────────────────────────────────────────────────┐
│                    ML/AI Framework Layer                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   PyTorch    │  │ Transformers │  │   EasyOCR    │      │
│  │              │  │  (Hugging    │  │              │      │
│  │  ResNet50    │  │    Face)     │  │  OCR Engine  │      │
│  │  CNN Model   │  │  RoBERTa     │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ BeautifulSoup│  │  Keyword     │  │  Advanced   │      │
│  │  Web Scraper │  │  Sentiment   │  │  Analysis   │      │
│  │              │  │  Analyzer    │  │  Engine     │      │
│  │  URL Fetch   │  │  (50+ words)│  │  (Impact +  │      │
│  │  + Extract   │  │              │  │   Insights) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
┌─────────────────────────────────────────────────────────────┐
│                    Data & Storage Layer                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   SQLite     │  │   NumPy      │  │   Pandas     │      │
│  │   Database   │  │   Arrays     │  │   DataFrames │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Python     │  │   Node.js    │  │   HTTP/      │      │
│  │   3.10+      │  │   18+       │  │   REST       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Model Architecture Details

### ResNet50 Feature Extraction
```
Input Image (224x224x3)
    │
    ▼
┌─────────────────┐
│  Conv Block     │  (7x7, 64 filters)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Max Pool       │  (3x3, stride 2)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ResNet Blocks  │  (4 stages, 2048 features)
│  - Bottleneck   │
│  - Skip Conns   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Global Avg     │
│  Pooling        │
└────────┬────────┘
         │
         ▼
    [2048 features]
```

### RoBERTa Sentiment Pipeline
```
Extracted Text
    │
    ▼
┌─────────────────┐
│  Tokenization   │  (BPE, 50k vocab)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  RoBERTa Base   │  (12 layers, 768 dim)
│  Transformer    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Classification │  (3 classes)
│  Head           │  (POS/NEG/NEU)
└────────┬────────┘
         │
         ▼
    Sentiment Score
    + Confidence
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Environment                     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Load Balancer                          │    │
│  └──────────────────┬─────────────────────────────────┘    │
│                     │                                        │
│         ┌───────────┴───────────┐                          │
│         │                        │                          │
│         ▼                        ▼                          │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │  Frontend    │      │  Backend     │                    │
│  │  (Next.js)   │      │  (Flask)     │                    │
│  │              │      │              │                    │
│  │  Static      │      │  API Server  │                    │
│  │  Hosting     │      │  + ML Models│                    │
│  └──────────────┘      └──────┬───────┘                    │
│                               │                             │
│                               ▼                             │
│                      ┌──────────────┐                       │
│                      │  Database    │                       │
│                      │  (PostgreSQL │                       │
│                      │   / SQLite)  │                       │
│                      └──────────────┘                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Advanced Analysis Pipeline

```
                    ┌─────────────┐
                    │  Article    │
                    │  Text       │
                    └──────┬──────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────┐                      ┌──────────────┐
│  Hybrid      │                      │  Asset       │
│  Sentiment   │                      │  Detection   │
│  Analysis    │                      │              │
│              │                      │ - Priority   │
│ - RoBERTa    │                      │   Matching   │
│   (ML)       │                      │ - NIFTY-50   │
│ - Keywords   │                      │ - SENSEX     │
│   (Fallback) │                      │ - Stocks     │
│ - Context    │                      │ - Crypto     │
│   Enhance    │                      └──────┬───────┘
└──────┬───────┘                             │
       │                                     │
       └───────────┬─────────────────────────┘
                   │
                   ▼
          ┌─────────────────┐
          │  Market Impact  │
          │  Classifier     │
          │                 │
          │ - HIGH_POSITIVE │
          │ - MODERATE_*    │
          │ - NEUTRAL       │
          │ - Time Horizon  │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │  Key Insights   │
          │  Extractor      │
          │                 │
          │ - Top 5 phrases │
          │ - Financial     │
          │   keywords      │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │  Confidence     │
          │  Calculator     │
          │                 │
          │ Multi-factor    │
          │ scoring         │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │  Final Report   │
          │  Generation     │
          └─────────────────┘
```

## Notes

- **ResNet50**: Pre-trained on ImageNet, used for visual feature extraction
- **RoBERTa**: Fine-tuned on Twitter data for financial sentiment (with keyword-based fallback)
- **EasyOCR**: Supports 80+ languages, GPU-accelerated
- **BeautifulSoup4**: Web scraping for direct URL analysis (Money Control, financial news)
- **Hybrid Sentiment**: ML model (RoBERTa) with 50+ weighted keyword fallback for 100% reliability
- **Fusion Strategy**: Advanced weighted combination (70% text, 30% image) with context enhancement
- **Asset Detection**: Priority-based system prioritizing Indian market indices (NIFTY-50, SENSEX)
- **Market Impact**: Multi-level classification with time horizon detection and indicator counting
- **Key Insights**: Automated extraction of top 5 market-moving phrases
- **Prediction Model**: Simplified LSTM-inspired architecture (can be extended to full LSTM/Transformer)


