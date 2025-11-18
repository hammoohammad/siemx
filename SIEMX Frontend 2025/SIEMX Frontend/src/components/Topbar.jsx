import React from 'react';
import { Bell, Search, User } from 'lucide-react';

export default function Topbar() {
  return (
    <header className="sticky top-0 z-10 bg-slate-950/70 backdrop-blur border-b border-slate-800">
      <div className="flex items-center gap-3 p-4">
        <div className="flex-1">
          <div className="relative">
            <input
              type="text"
              placeholder="Search alerts, IPs, users..."
              className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 pl-9 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <Search className="absolute left-2.5 top-2.5 text-slate-400" size={18} />
          </div>
        </div>
        <button className="btn" aria-label="Notifications">
          <Bell size={18} />
        </button>
        <button className="btn" aria-label="Profile">
          <User size={18} />
        </button>
      </div>
    </header>
  );
}
