export interface Asset {
  id: number;
  symbol: string;
  name: string;
  asset_type: string;
}

export interface SentimentAnalysis {
  id: number;
  source_url?: string;
  extracted_text?: string;
  combined_sentiment: string;
  confidence: number;
  created_at: string;
}

export interface MarketPrediction {
  id: number;
  current_price: number;
  predicted_price: number;
  price_change_percent: number;
  sentiment_score: number;
  confidence: number;
  created_at: string;
}

export interface DashboardStats {
  stats: {
    total_assets: number;
    total_analyses: number;
    total_predictions: number;
  };
  recent_analyses: Array<{
    id: number;
    asset_symbol: string;
    sentiment: string;
    confidence: number;
    created_at: string;
  }>;
}


