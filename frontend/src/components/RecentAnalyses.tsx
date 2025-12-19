import React from 'react';
import type { DashboardStats } from '../types/market';
import styles from '../../styles/Dashboard.module.css';

interface Props {
  data: DashboardStats;
}

export default function RecentAnalyses({ data }: Props) {
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return '#10b981';
      case 'negative':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  return (
    <div className={styles.recentSection}>
      <h2>Recent Analyses</h2>
      <div className={styles.analysesList}>
        {data.recent_analyses.map((analysis) => (
          <div key={analysis.id} className={styles.analysisCard}>
            <div className={styles.analysisHeader}>
              <span className={styles.assetSymbol}>{analysis.asset_symbol}</span>
              <span
                className={styles.sentimentBadge}
                style={{ backgroundColor: getSentimentColor(analysis.sentiment) }}
              >
                {analysis.sentiment.toUpperCase()}
              </span>
            </div>
            <div className={styles.analysisMeta}>
              <span>Confidence: {(analysis.confidence * 100).toFixed(1)}%</span>
              <span>{new Date(analysis.created_at).toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


