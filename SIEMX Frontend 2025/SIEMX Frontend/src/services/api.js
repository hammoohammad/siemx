import { BACKEND_HTTP_URL } from '../config';

// Prefer absolute backend URL if provided; otherwise use relative path (Vite proxy in dev)
const BASE = BACKEND_HTTP_URL || '';

async function getJson(path) {
  const url = `${BASE}${path}`; // in dev, goes through Vite proxy
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchAlerts() {
  return getJson('/api/alerts');
}

export async function fetchLogs() {
  return getJson('/api/logs');
}

export async function fetchInsights() {
  return getJson('/api/insights');
}
