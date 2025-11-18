import React from 'react';

export default function AIInsights({ insights }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">AI Insights</h3>
      </div>
      <ul className="space-y-2 text-sm">
        {insights.map((i, idx) => (
          <li key={idx} className="flex items-start gap-2">
            <span className="badge border bg-cyan-500/15 text-cyan-400 border-cyan-500/30">Action</span>
            <span className="text-slate-300">{i}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
