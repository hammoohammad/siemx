import React, { useMemo } from 'react';
import SummaryCards from '../components/SummaryCards';
import AlertsTable from '../components/AlertsTable';
import AIInsights from '../components/AIInsights';
import ChartsSection from '../components/ChartsSection';
import RecentLogs from '../components/RecentLogs';
import useLiveData from '../services/useLiveData';

export default function Dashboard() {
  const { alerts, logs, insights, trend, distribution, topSources } = useLiveData();

  const stats = useMemo(() => ({
    // Fall back to logs when there are no alerts so the dashboard still shows activity
    total: alerts.length > 0 ? alerts.length : logs.length,
    high: alerts.length > 0 ? alerts.filter(a => a.level === 'High').length : logs.filter(l => l.level === 'High').length,
    medium: alerts.length > 0 ? alerts.filter(a => a.level === 'Medium').length : logs.filter(l => l.level === 'Medium').length,
    low: alerts.length > 0 ? alerts.filter(a => a.level === 'Low').length : logs.filter(l => l.level === 'Low').length,
    activeResponses: insights.filter(i => (i || '').toLowerCase().includes('blocked') || (i || '').toLowerCase().includes('disabled')).length,
  }), [alerts, logs, insights]);

  return (
    <div className="space-y-4">
      <SummaryCards stats={stats} />
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="xl:col-span-2 space-y-4">
          <AlertsTable alerts={alerts.slice(0, 10)} />
          <ChartsSection trend={trend} distribution={distribution} topSources={topSources} />
        </div>
        <div className="xl:col-span-1 space-y-4">
          <AIInsights insights={insights.slice(0, 6)} />
          <RecentLogs logs={logs.slice(0, 12)} />
        </div>
      </div>
    </div>
  );
}
