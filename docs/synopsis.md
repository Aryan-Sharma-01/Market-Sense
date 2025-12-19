# Visual Sentiment Analysis for Market Prediction - Synopsis

## Project Title
**Visual Sentiment Analysis for Market Prediction: A Multi-Modal AI System**

## Problem Statement

Traditional market analysis relies heavily on numerical data and text-based news, often missing the rich contextual information embedded in visual content from social media platforms. Images and videos shared on platforms like Twitter, Reddit, and news websites contain valuable sentiment cues that can influence market movements. Current systems fail to effectively combine visual and textual information to predict short-term market trends for stocks and cryptocurrencies.

## Objectives

1. **Multi-Modal Analysis**: Develop an integrated system that processes both visual and textual information from social media content to extract comprehensive sentiment signals.

2. **Real-Time Processing**: Create a scalable pipeline capable of analyzing images and videos in real-time to capture market-moving sentiment as it emerges.

3. **Market Prediction**: Build predictive models that correlate extracted sentiment with historical market data to forecast short-term price movements.

4. **User Interface**: Design an intuitive dashboard that visualizes sentiment trends, predictions, and analysis results for traders and analysts.

## Technical Approach

### Computer Vision Layer
- **ResNet50 (PyTorch)**: Pre-trained CNN model for extracting high-level features from images and video frames, enabling visual sentiment understanding.

### Text Extraction & NLP
- **EasyOCR**: Open-source OCR engine for extracting text overlays from images and video thumbnails.
- **BeautifulSoup4**: Web scraping library for extracting article content directly from URLs (Money Control, financial news sites).
- **Hybrid Sentiment Analysis**: 
  - **Primary**: RoBERTa (Hugging Face Transformers) - Fine-tuned sentiment model (`cardiffnlp/twitter-roberta-base-sentiment-latest`)
  - **Fallback**: Advanced keyword-based sentiment analyzer with 50+ weighted financial keywords for robust analysis
  - **Context Enhancement**: Intelligent context-aware sentiment adjustment for financial news

### Fusion & Prediction
- **Advanced Multi-Modal Fusion**: Weighted combination (70% text, 30% image) with improved thresholds for accurate sentiment detection
- **Market Impact Analysis**: Intelligent impact level classification (HIGH_POSITIVE, MODERATE_POSITIVE, NEUTRAL, etc.) with time horizon detection
- **Key Insights Extraction**: Automated extraction of 5 most important financial statements and market-moving phrases
- **Time-Series Prediction**: LSTM-inspired models that correlate sentiment scores with market price movements over configurable time horizons (12-24 hours)
- **Smart Asset Detection**: Priority-based detection system for Indian market indices (NIFTY-50, SENSEX), global stocks, and cryptocurrencies

### Technology Stack
- **Backend**: Python, Flask, SQLAlchemy, SQLite, BeautifulSoup4, Requests
- **Frontend**: Next.js, TypeScript, React, Recharts
- **ML Frameworks**: PyTorch, Transformers (Hugging Face), EasyOCR
- **Data Sources**: Direct URL analysis (Money Control, financial news), Social media APIs (Twitter/Reddit), Market data APIs (Yahoo Finance, Alpha Vantage)

## Key Features

1. **Dual Input Modes**: 
   - **URL Analysis**: Direct URL input for financial news articles (Money Control, etc.) - automatically fetches and analyzes content
   - **Image Upload**: Upload images from social media, news articles, or presentations for instant sentiment analysis

2. **Intelligent Asset Detection**: 
   - Automatic detection of stock symbols, crypto symbols, and market indices from article text
   - Priority-based detection for Indian markets (NIFTY-50, SENSEX) and global assets
   - Context-aware symbol extraction with company name recognition

3. **Advanced Sentiment Analysis**:
   - **Hybrid Approach**: ML-based (RoBERTa) with keyword-based fallback for 100% reliability
   - **50+ Weighted Keywords**: Financial sentiment keywords with confidence scoring
   - **Context Enhancement**: Question detection, intensifier recognition, and market-specific adjustments
   - **Detailed Breakdown**: Separate scores for image, text, and combined sentiment with confidence metrics

4. **Market Impact Analysis**:
   - Impact level classification (HIGH_POSITIVE, MODERATE_POSITIVE, SLIGHTLY_POSITIVE, NEUTRAL, etc.)
   - Time horizon detection (IMMEDIATE, SHORT_TERM, LONG_TERM)
   - Positive/negative indicator counting for comprehensive market assessment
   - Actionable impact descriptions for traders

5. **Key Insights Extraction**: Automatically extracts and highlights the 5 most important financial statements and market-moving phrases from articles

6. **Enhanced Confidence Scoring**: Multi-factor confidence calculation based on sentiment strength, text length, asset detection, and financial terminology presence

7. **Price Prediction**: Generates short-term price predictions with confidence intervals based on sentiment analysis and historical patterns

8. **Professional Dashboard**: Real-time dashboard with detailed sentiment breakdowns, market impact visualization, key insights display, and comprehensive analysis results

## Expected Outcomes

- **Accuracy**: Achieve sentiment classification accuracy above 75% on social media content.
- **Prediction Performance**: Generate price movement predictions with directional accuracy suitable for short-term trading signals.
- **Scalability**: Process hundreds of images per hour with sub-second response times for individual analyses.
- **User Value**: Provide actionable insights that complement traditional technical and fundamental analysis.

## Applications

- **Day Traders**: Quick sentiment-based entry/exit signals for high-frequency trading.
- **Crypto Traders**: Real-time sentiment monitoring for volatile cryptocurrency markets.
- **Investment Analysts**: Supplementary sentiment data for comprehensive market research.
- **Algorithmic Trading**: Integration with automated trading systems for sentiment-driven strategies.

## Innovation Points

1. **URL-Based Analysis**: Direct financial article URL processing eliminates the need for manual screenshots - simply paste Money Control or any financial news URL for instant analysis.

2. **Hybrid Sentiment Engine**: Robust sentiment analysis combining ML models with keyword-based fallback ensures 100% uptime and accurate results even when ML services are unavailable.

3. **Advanced Market Intelligence**: 
   - Multi-level sentiment breakdown (image, text, combined)
   - Market impact classification with time horizon detection
   - Automated key insights extraction
   - Smart asset detection with priority-based matching

4. **Indian Market Focus**: Specialized detection and analysis for Indian market indices (NIFTY-50, SENSEX) with context-aware recognition of GDP, RBI, and market-specific terminology.

5. **Real-Time Processing**: End-to-end pipeline from URL/article to comprehensive analysis in under 5 seconds.

6. **Open-Source Models**: Leverages state-of-the-art pre-trained models (ResNet50, RoBERTa) without requiring extensive training data.

7. **Interdisciplinary Approach**: Combines web scraping, computer vision, NLP, and financial time-series analysis in a unified system.

## Future Enhancements

- Integration with live social media APIs for automated content collection
- Video frame analysis for CEO presentations and product launches
- Multi-asset portfolio sentiment tracking
- Historical backtesting and model refinement
- Advanced LSTM/Transformer architectures for improved prediction accuracy

## Conclusion

This project demonstrates the practical application of multi-modal AI in financial markets, showcasing how modern deep learning models can extract actionable insights from unstructured visual and textual data. By combining open-source computer vision and NLP models, the system provides a cost-effective solution for sentiment-driven market analysis.


