import React from 'react';
import AlertsTable from '../components/AlertsTable';
import useLiveData from '../services/useLiveData';

export default function Alerts() {
  const { alerts } = useLiveData();
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Alerts</h2>
      <AlertsTable alerts={alerts} />
    </div>
  );
}
