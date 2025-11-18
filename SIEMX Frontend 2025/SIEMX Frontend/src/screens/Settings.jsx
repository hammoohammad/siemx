import React from 'react';

export default function Settings() {
  return (
    <div className="space-y-4 max-w-2xl">
      <h2 className="text-xl font-semibold">Settings</h2>
      <div className="card space-y-3">
        <div>
          <label className="block text-sm text-slate-400 mb-1">Theme</label>
          <select className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3">
            <option>Dark</option>
            <option>Light</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-slate-400 mb-1">Notification Email</label>
          <input className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3" placeholder="security@company.com" />
        </div>
        <button className="btn">Save</button>
      </div>
    </div>
  );
}
