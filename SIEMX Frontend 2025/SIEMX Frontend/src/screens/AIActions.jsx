import React from 'react';
import AIInsights from '../components/AIInsights';
import useLiveData from '../services/useLiveData';

export default function AIActions() {
  const { insights } = useLiveData();
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">AI Actions</h2>
      <AIInsights insights={insights} />
    </div>
  );
}
