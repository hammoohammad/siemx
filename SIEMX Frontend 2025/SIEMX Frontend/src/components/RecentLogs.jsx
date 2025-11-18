import React, { useMemo, useState } from 'react';

const severities = ['All', 'High', 'Medium', 'Low'];

export default function RecentLogs({ logs }) {
  const [filter, setFilter] = useState('All');
  const filtered = useMemo(() => {
    if (filter === 'All') return logs;
    return logs.filter(l => l.level === filter);
  }, [logs, filter]);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">Recent Logs</h3>
        <div className="flex gap-2">
          {severities.map(s => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`badge border ${filter === s ? 'bg-primary-500/20 text-primary-300 border-primary-500/30' : 'bg-slate-800 text-slate-300 border-slate-700'}`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>
      <div className="max-h-64 overflow-auto text-sm">
        <ul className="space-y-2">
          {filtered.map((l) => (
            <li key={l.id} className="flex items-center justify-between border border-slate-800 rounded-lg p-2 bg-slate-900/50">
              <span className="text-slate-400">{l.timestamp}</span>
              <span className="flex-1 mx-3 text-slate-200">{l.message}</span>
              <span className={`badge border ${l.level === 'High' ? 'bg-red-500/15 text-red-400 border-red-500/30' : l.level === 'Medium' ? 'bg-orange-500/15 text-orange-400 border-orange-500/30' : 'bg-green-500/15 text-green-400 border-green-500/30'}`}>{l.level}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
