import React from 'react';
import RecentLogs from '../components/RecentLogs';
import useLiveData from '../services/useLiveData';

export default function Logs() {
  const { logs } = useLiveData();
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Logs</h2>
      <RecentLogs logs={logs} />
    </div>
  );
}
