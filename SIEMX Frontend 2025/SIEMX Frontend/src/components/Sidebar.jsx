import React from 'react';
import { NavLink } from 'react-router-dom';
import { Shield, Bell, List, Brain, Settings as SettingsIcon, LayoutDashboard } from 'lucide-react';
import clsx from 'clsx';

const nav = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/alerts', label: 'Alerts', icon: Bell },
  { to: '/logs', label: 'Logs', icon: List },
  { to: '/ai-actions', label: 'AI Actions', icon: Brain },
  { to: '/settings', label: 'Settings', icon: SettingsIcon },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800 p-4 hidden md:flex flex-col gap-2">
      <div className="flex items-center gap-2 mb-4">
        <Shield className="text-neon-lime" />
        <span className="font-bold tracking-wide">SIEMX</span>
      </div>
      <nav className="flex flex-col gap-1">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2 rounded-lg border border-transparent hover:bg-slate-800 text-slate-300 hover:text-white',
                isActive && 'bg-slate-800 border-slate-700 text-white'
              )
            }
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto text-xs text-slate-500">© {new Date().getFullYear()} SIEMX</div>
    </aside>
  );
}
