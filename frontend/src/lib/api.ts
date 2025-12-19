import type { Asset, DashboardStats, MarketPrediction, SentimentAnalysis } from '../types/market';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:5500';

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return fetchAPI<DashboardStats>('/api/dashboard');
}

export async function getAssets(): Promise<{ assets: Asset[] }> {
  return fetchAPI<{ assets: Asset[] }>('/api/assets');
}

export async function getAssetAnalyses(assetId: number): Promise<{
  asset: Asset;
  analyses: SentimentAnalysis[];
}> {
  return fetchAPI<{ asset: Asset; analyses: SentimentAnalysis[] }>(`/api/assets/${assetId}/analyses`);
}

export async function getAssetPredictions(assetId: number): Promise<{
  asset: Asset;
  predictions: MarketPrediction[];
}> {
  return fetchAPI<{ asset: Asset; predictions: MarketPrediction[] }>(`/api/assets/${assetId}/predictions`);
}

export async function analyzeImage(
  imageFile: File,
  symbol: string,
  sourceUrl?: string
): Promise<{
  analysis_id: number;
  extracted_text: string;
  image_sentiment: string;
  text_sentiment: string;
  combined_sentiment: string;
  confidence: number;
}> {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('symbol', symbol);
  if (sourceUrl) {
    formData.append('source_url', sourceUrl);
  }

  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

export async function analyzeUrl(
  url: string,
  symbol?: string
): Promise<{
  analysis_id: number;
  article_title: string;
  detected_asset: string;
  asset_name: string;
  asset_type?: string;
  source_url?: string;
  text_preview: string | null;
  full_text_length: number;
  sentiment_analysis: {
    image_sentiment: { label: string; score: number };
    text_sentiment: { label: string; score: number };
    combined_sentiment: { label: string; score: number };
    confidence: number;
    summary: string;
  };
  market_impact: {
    impact_level: string;
    impact_description: string;
    time_horizon: string;
    positive_indicators_count: number;
    negative_indicators_count: number;
    sentiment_score: number;
  };
  key_insights: string[];
  analysis_timestamp?: string;
}> {
  const response = await fetch(`${API_BASE}/api/analyze-url`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url, symbol: symbol || '' }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: response.statusText }));
    throw new Error(error.error || `API error: ${response.statusText}`);
  }

  return response.json();
}
