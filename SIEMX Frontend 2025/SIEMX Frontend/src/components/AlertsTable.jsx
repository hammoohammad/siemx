import React from 'react';
import clsx from 'clsx';

function levelClass(level) {
  return {
    High: 'bg-red-500/15 text-red-400 border-red-500/30',
    Medium: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
    Low: 'bg-green-500/15 text-green-400 border-green-500/30',
  }[level] || '';
}

export default function AlertsTable({ alerts }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">Real-Time Alerts</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="text-slate-400">
            <tr className="text-left">
              <th className="py-2 pr-4">Timestamp</th>
              <th className="py-2 pr-4">Source IP</th>
              <th className="py-2 pr-4">Destination</th>
              <th className="py-2 pr-4">Alert Level</th>
              <th className="py-2 pr-4">Status</th>
              <th className="py-2 pr-4">Action Taken</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {alerts.map((a) => (
              <tr key={a.id} className={clsx('hover:bg-slate-800/40', a.level === 'High' && 'bg-red-950/20', a.level === 'Medium' && 'bg-orange-950/10')}>
                <td className="py-2 pr-4 whitespace-nowrap">{a.timestamp}</td>
                <td className="py-2 pr-4">{a.source}</td>
                <td className="py-2 pr-4">{a.destination}</td>
                <td className="py-2 pr-4">
                  <span className={clsx('badge border', levelClass(a.level))}>{a.level}</span>
                </td>
                <td className="py-2 pr-4">{a.status}</td>
                <td className="py-2 pr-4 text-slate-300">{a.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
