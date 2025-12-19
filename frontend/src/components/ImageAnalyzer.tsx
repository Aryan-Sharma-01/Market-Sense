'use client';

import React, { useState } from 'react';
import { analyzeImage, analyzeUrl } from '../lib/api';
import styles from '../../styles/Dashboard.module.css';

export default function ImageAnalyzer() {
  const [mode, setMode] = useState<'url' | 'image'>('url');
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState('');
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (mode === 'url') {
      if (!url) {
        setError('Please enter a URL');
        return;
      }
    } else {
      if (!file) {
        setError('Please select an image file');
        return;
      }
    }

    setLoading(true);
    setError(null);
    try {
      let response;
      if (mode === 'url') {
        response = await analyzeUrl(url, symbol || undefined);
      } else {
        response = await analyzeImage(file!, symbol || '');
      }
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.analyzerSection}>
      <h2>Analyze Article</h2>
      
      <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem' }}>
        <button
          type="button"
          onClick={() => {
            setMode('url');
            setFile(null);
            setResult(null);
            setError(null);
          }}
          style={{
            padding: '0.5rem 1.5rem',
            background: mode === 'url' ? '#667eea' : '#e5e7eb',
            color: mode === 'url' ? 'white' : '#374151',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: mode === 'url' ? '600' : '400',
          }}
        >
          📰 Analyze URL
        </button>
        <button
          type="button"
          onClick={() => {
            setMode('image');
            setUrl('');
            setResult(null);
            setError(null);
          }}
          style={{
            padding: '0.5rem 1.5rem',
            background: mode === 'image' ? '#667eea' : '#e5e7eb',
            color: mode === 'image' ? 'white' : '#374151',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: mode === 'image' ? '600' : '400',
          }}
        >
          🖼️ Upload Image
        </button>
      </div>

      <form onSubmit={handleSubmit} className={styles.analyzerForm}>
        {mode === 'url' ? (
          <div className={styles.formGroup}>
            <label>Article URL</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.moneycontrol.com/news/..."
              required
            />
            <small style={{ color: '#6b7280', fontSize: '0.85rem' }}>
              Paste any Money Control or financial news article URL
            </small>
          </div>
        ) : (
          <div className={styles.formGroup}>
            <label>Image File</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              required
            />
          </div>
        )}
        
        <div className={styles.formGroup}>
          <label>Asset Symbol (Optional - Auto-detected if blank)</label>
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            placeholder="Leave blank to auto-detect (e.g., NIFTY-50, SENSEX, BTC-USD, TSLA)"
          />
          <small style={{ color: '#6b7280', fontSize: '0.85rem' }}>
            The system will automatically detect stock/crypto symbols from the article
          </small>
        </div>
        
        <button type="submit" disabled={loading} className={styles.submitButton}>
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>

      {error && <div className={styles.error}>{error}</div>}

      {result && (
        <div style={{ marginTop: '2rem' }}>
          {/* Header Section */}
          <div className={styles.resultCard} style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ marginBottom: '1rem', color: '#1f2937' }}>📊 Analysis Results</h3>
            {result.article_title && (
              <h4 style={{ fontSize: '1.2rem', marginBottom: '1rem', color: '#374151', lineHeight: '1.5' }}>
                {result.article_title}
              </h4>
            )}
            <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
              {result.detected_asset && (
                <div>
                  <strong style={{ color: '#6b7280' }}>Detected Asset:</strong>{' '}
                  <span style={{ color: '#667eea', fontWeight: 'bold', fontSize: '1.1rem' }}>
                    {result.detected_asset}
                  </span>
                  {result.asset_name && result.asset_name !== result.detected_asset && (
                    <span style={{ color: '#6b7280' }}> ({result.asset_name})</span>
                  )}
                </div>
              )}
              {result.asset_type && (
                <div>
                  <strong style={{ color: '#6b7280' }}>Type:</strong>{' '}
                  <span style={{ textTransform: 'capitalize' }}>{result.asset_type}</span>
                </div>
              )}
              {result.full_text_length && (
                <div>
                  <strong style={{ color: '#6b7280' }}>Text Analyzed:</strong>{' '}
                  {result.full_text_length.toLocaleString()} characters
                </div>
              )}
            </div>
          </div>

          {/* Sentiment Analysis Section */}
          {result.sentiment_analysis && (
            <div className={styles.resultCard} style={{ marginBottom: '1.5rem' }}>
              <h4 style={{ marginBottom: '1rem', color: '#1f2937' }}>💭 Sentiment Analysis</h4>
              
              {result.sentiment_analysis.summary && (
                <div style={{ 
                  padding: '1rem', 
                  background: '#f0f9ff', 
                  borderRadius: '8px', 
                  marginBottom: '1rem',
                  borderLeft: '4px solid #3b82f6'
                }}>
                  <p style={{ margin: 0, lineHeight: '1.6', color: '#1e40af' }}>
                    {result.sentiment_analysis.summary}
                  </p>
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
                {result.sentiment_analysis.image_sentiment && (
                  <div style={{ padding: '1rem', background: '#f9fafb', borderRadius: '8px' }}>
                    <div style={{ color: '#6b7280', fontSize: '0.9rem', marginBottom: '0.5rem' }}>Image Sentiment</div>
                    <div style={{ 
                      fontSize: '1.2rem', 
                      fontWeight: '600',
                      color: result.sentiment_analysis.image_sentiment.label === 'POSITIVE' ? '#10b981' : 
                             result.sentiment_analysis.image_sentiment.label === 'NEGATIVE' ? '#ef4444' : '#6b7280'
                    }}>
                      {result.sentiment_analysis.image_sentiment.label}
                    </div>
                    <div style={{ color: '#6b7280', fontSize: '0.85rem', marginTop: '0.25rem' }}>
                      Score: {(result.sentiment_analysis.image_sentiment.score * 100).toFixed(1)}%
                    </div>
                  </div>
                )}
                {result.sentiment_analysis.text_sentiment && (
                  <div style={{ padding: '1rem', background: '#f9fafb', borderRadius: '8px' }}>
                    <div style={{ color: '#6b7280', fontSize: '0.9rem', marginBottom: '0.5rem' }}>Text Sentiment</div>
                    <div style={{ 
                      fontSize: '1.2rem', 
                      fontWeight: '600',
                      color: result.sentiment_analysis.text_sentiment.label === 'POSITIVE' ? '#10b981' : 
                             result.sentiment_analysis.text_sentiment.label === 'NEGATIVE' ? '#ef4444' : '#6b7280'
                    }}>
                      {result.sentiment_analysis.text_sentiment.label}
                    </div>
                    <div style={{ color: '#6b7280', fontSize: '0.85rem', marginTop: '0.25rem' }}>
                      Score: {(result.sentiment_analysis.text_sentiment.score * 100).toFixed(1)}%
                    </div>
                  </div>
                )}
                {result.sentiment_analysis.combined_sentiment && (
                  <div style={{ padding: '1rem', background: '#f9fafb', borderRadius: '8px', border: '2px solid #667eea' }}>
                    <div style={{ color: '#6b7280', fontSize: '0.9rem', marginBottom: '0.5rem' }}>Combined Sentiment</div>
                    <div style={{ 
                      fontSize: '1.4rem', 
                      fontWeight: '700',
                      color: result.sentiment_analysis.combined_sentiment.label === 'POSITIVE' ? '#10b981' : 
                             result.sentiment_analysis.combined_sentiment.label === 'NEGATIVE' ? '#ef4444' : '#6b7280'
                    }}>
                      {result.sentiment_analysis.combined_sentiment.label}
                    </div>
                    <div style={{ color: '#667eea', fontSize: '0.9rem', marginTop: '0.5rem', fontWeight: '600' }}>
                      Confidence: {(result.sentiment_analysis.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Market Impact Section */}
          {result.market_impact && (
            <div className={styles.resultCard} style={{ marginBottom: '1.5rem' }}>
              <h4 style={{ marginBottom: '1rem', color: '#1f2937' }}>📈 Market Impact Analysis</h4>
              <div style={{ 
                padding: '1rem', 
                background: result.market_impact.impact_level.includes('POSITIVE') ? '#ecfdf5' : 
                           result.market_impact.impact_level.includes('NEGATIVE') ? '#fef2f2' : '#f9fafb',
                borderRadius: '8px',
                borderLeft: `4px solid ${
                  result.market_impact.impact_level.includes('POSITIVE') ? '#10b981' : 
                  result.market_impact.impact_level.includes('NEGATIVE') ? '#ef4444' : '#6b7280'
                }`
              }}>
                <div style={{ marginBottom: '0.75rem' }}>
                  <strong style={{ color: '#374151' }}>Impact Level: </strong>
                  <span style={{ 
                    fontWeight: '600',
                    color: result.market_impact.impact_level.includes('POSITIVE') ? '#10b981' : 
                           result.market_impact.impact_level.includes('NEGATIVE') ? '#ef4444' : '#6b7280'
                  }}>
                    {result.market_impact.impact_level.replace('_', ' ')}
                  </span>
                </div>
                <p style={{ margin: '0.5rem 0', lineHeight: '1.6', color: '#374151' }}>
                  {result.market_impact.impact_description}
                </p>
                <div style={{ marginTop: '1rem', display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                  <div>
                    <strong style={{ color: '#6b7280' }}>Time Horizon: </strong>
                    <span>{result.market_impact.time_horizon.replace('_', ' ')}</span>
                  </div>
                  <div>
                    <strong style={{ color: '#6b7280' }}>Positive Indicators: </strong>
                    <span style={{ color: '#10b981' }}>{result.market_impact.positive_indicators_count}</span>
                  </div>
                  <div>
                    <strong style={{ color: '#6b7280' }}>Negative Indicators: </strong>
                    <span style={{ color: '#ef4444' }}>{result.market_impact.negative_indicators_count}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Key Insights Section */}
          {result.key_insights && result.key_insights.length > 0 && (
            <div className={styles.resultCard} style={{ marginBottom: '1.5rem' }}>
              <h4 style={{ marginBottom: '1rem', color: '#1f2937' }}>🔍 Key Insights</h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {result.key_insights.map((insight: string, index: number) => (
                  <li key={index} style={{ 
                    marginBottom: '0.75rem', 
                    padding: '0.75rem', 
                    background: '#f9fafb', 
                    borderRadius: '6px',
                    borderLeft: '3px solid #667eea',
                    lineHeight: '1.6'
                  }}>
                    <span style={{ color: '#667eea', marginRight: '0.5rem' }}>•</span>
                    {insight}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Text Preview */}
          {result.text_preview && (
            <div className={styles.resultCard}>
              <h4 style={{ marginBottom: '1rem', color: '#1f2937' }}>📄 Article Text Preview</h4>
              <p style={{ lineHeight: '1.8', color: '#374151' }}>
                {result.text_preview}
                {result.full_text_length > 500 && '...'}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}


