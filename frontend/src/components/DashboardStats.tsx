import React from 'react';
import type { DashboardStats as DashboardStatsType } from '../types/market';
import styles from '../../styles/Dashboard.module.css';

interface Props {
  data: DashboardStatsType;
}

export default function DashboardStats({ data }: Props) {
  return (
    <div className={styles.statsGrid}>
      <div className={styles.statCard}>
        <h3>Total Assets</h3>
        <p className={styles.statValue}>{data.stats.total_assets}</p>
      </div>
      <div className={styles.statCard}>
        <h3>Analyses</h3>
        <p className={styles.statValue}>{data.stats.total_analyses}</p>
      </div>
      <div className={styles.statCard}>
        <h3>Predictions</h3>
        <p className={styles.statValue}>{data.stats.total_predictions}</p>
      </div>
    </div>
  );
}


