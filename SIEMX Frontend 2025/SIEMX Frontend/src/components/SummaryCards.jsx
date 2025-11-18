import React from 'react';
import { Activity, AlertTriangle, ShieldX, ShieldCheck, Zap } from 'lucide-react';

function Stat({ title, value, icon: Icon, color }) {
  const colorClasses = {
    primary: 'bg-primary-500/20 text-primary-300',
    red: 'bg-red-500/20 text-red-400',
    orange: 'bg-orange-500/20 text-orange-400',
    green: 'bg-green-500/20 text-green-400',
    cyan: 'bg-cyan-500/20 text-cyan-400',
  };
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-slate-400">{title}</div>
          <div className="text-2xl font-semibold">{value}</div>
        </div>
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
          <Icon />
        </div>
      </div>
    </div>
  );
}

export default function SummaryCards({ stats }) {
  const cards = [
    { title: 'Total Alerts', value: stats.total, icon: Activity, color: 'primary' },
    { title: 'High Alerts', value: stats.high, icon: AlertTriangle, color: 'red' },
    { title: 'Medium Alerts', value: stats.medium, icon: ShieldX, color: 'orange' },
    { title: 'Low Alerts', value: stats.low, icon: ShieldCheck, color: 'green' },
    { title: 'Active Responses', value: stats.activeResponses, icon: Zap, color: 'cyan' },
  ];
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4">
      {cards.map((c) => (
        <Stat key={c.title} {...c} />
      ))}
    </div>
  );
}
