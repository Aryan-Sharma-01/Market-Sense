import Head from 'next/head';
import { useState, useEffect } from 'react';
import DashboardStats from '../components/DashboardStats';
import RecentAnalyses from '../components/RecentAnalyses';
import ImageAnalyzer from '../components/ImageAnalyzer';
import { getDashboardStats, type DashboardStats as DashboardStatsType } from '../lib/api';
import styles from '../../styles/Dashboard.module.css';

export default function Home() {
  const [data, setData] = useState<DashboardStatsType>({
    stats: { total_assets: 0, total_analyses: 0, total_predictions: 0 },
    recent_analyses: [],
  });
  const [loading, setLoading] = useState(true);

  const refreshData = async () => {
    setLoading(true);
    try {
      const newData = await getDashboardStats();
      setData(newData);
    } catch (err) {
      console.error('Failed to refresh:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
  }, []);

  return (
    <div className={styles.container}>
      <Head>
        <title>Market Sentiment Analyzer</title>
        <meta name="description" content="Visual sentiment analysis for market prediction" />
      </Head>

      <header className={styles.header}>
        <h1>Market Sentiment Analyzer</h1>
        <p>Upload any financial article or image - automatically detects stocks/crypto and analyzes sentiment</p>
      </header>

      <main className={styles.main}>
        <div className={styles.dashboardSection}>
          <div className={styles.sectionHeader}>
            <h2>Dashboard</h2>
            <button onClick={refreshData} disabled={loading} className={styles.refreshButton}>
              {loading ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
          <DashboardStats data={data} />
          <RecentAnalyses data={data} />
        </div>

        <ImageAnalyzer />
      </main>
    </div>
  );
}

