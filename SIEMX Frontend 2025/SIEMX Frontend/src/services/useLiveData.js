import { useEffect, useMemo, useRef, useState } from 'react';
import { BACKEND_HTTP_URL, BACKEND_WS_URL } from '../config';
import { fetchAlerts, fetchLogs, fetchInsights } from './api';

function normalizeAlert(a) {
  return {
    id: a.id || a._id || `${a.timestamp || Date.now()}-${a.source || ''}-${a.destination || ''}`,
    timestamp: a.timestamp || a.time || a.ts || '',
    source: a.source || a.src || a.ip || 'unknown',
    destination: a.destination || a.dst || a.target || 'unknown',
    level: a.level || a.severity || 'Low',
    status: a.status || a.state || 'Open',
    action: a.action || a.response || 'None',
  };
}

function normalizeLog(l) {
  return {
    id: l.id || l._id || `${l.timestamp || Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    timestamp: l.timestamp || l.time || l.ts || '',
    level: l.level || l.severity || 'Low',
    message: l.message || l.msg || '',
  };
}

export default function useLiveData() {
  const [alerts, setAlerts] = useState([]);
  const [logs, setLogs] = useState([]);
  const [insights, setInsights] = useState([]);
  const wsRef = useRef(null);

  // HTTP initial fetch + polling fallback
  useEffect(() => {
    let mounted = true;
    async function loadAll() {
      try {
        const [a, l, i] = await Promise.allSettled([
          fetchAlerts(),
          fetchLogs(),
          fetchInsights(),
        ]);
        if (!mounted) return;
        if (a.status === 'fulfilled' && Array.isArray(a.value)) setAlerts(a.value.map(normalizeAlert));
        if (l.status === 'fulfilled' && Array.isArray(l.value)) setLogs(l.value.map(normalizeLog));
        if (i.status === 'fulfilled') setInsights(Array.isArray(i.value) ? i.value : []);
      } catch {}
    }
    loadAll();
    const id = setInterval(loadAll, 4000);
    return () => { mounted = false; clearInterval(id); };
  }, []);

  // Optional WebSocket live updates
  useEffect(() => {
    const wsUrl = BACKEND_WS_URL || (import.meta.env.DEV ? (window.location.origin.replace('http', 'ws') + '/ws') : '');
    if (!wsUrl) return;
    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data);
          if (data.type === 'alert') setAlerts((prev) => [normalizeAlert(data.payload), ...prev].slice(0, 200));
          if (data.type === 'log') setLogs((prev) => [normalizeLog(data.payload), ...prev].slice(0, 500));
          if (data.type === 'insight') setInsights((prev) => [data.payload, ...prev].slice(0, 100));
          if (Array.isArray(data.alerts)) setAlerts(data.alerts.map(normalizeAlert));
          if (Array.isArray(data.logs)) setLogs(data.logs.map(normalizeLog));
          if (Array.isArray(data.insights)) setInsights(data.insights);
        } catch {}
      };
      ws.onerror = () => {};
      ws.onclose = () => {};
      return () => { try { ws.close(); } catch {} };
    } catch {
      // ignore WS errors; HTTP polling continues
    }
  }, []);

  const trend = useMemo(() => {
    // derive simple per-hour counts from logs timestamps if parseable
    const buckets = new Array(24).fill(0);
    logs.forEach((l) => {
      const d = new Date(l.timestamp || Date.now());
      if (!isNaN(d)) buckets[d.getHours()] += 1;
    });
    return buckets.map((count, h) => ({ time: `${h}:00`, count }));
  }, [logs]);

  const distribution = useMemo(() => {
    const counts = { High: 0, Medium: 0, Low: 0 };
    const src = alerts.length > 0 ? alerts : logs;
    src.forEach((x) => { counts[x.level] = (counts[x.level] || 0) + 1; });
    return [
      { name: 'High', value: counts.High || 0 },
      { name: 'Medium', value: counts.Medium || 0 },
      { name: 'Low', value: counts.Low || 0 },
    ];
  }, [alerts, logs]);

  const topSources = useMemo(() => {
    const map = new Map();
    alerts.forEach((a) => map.set(a.source, (map.get(a.source) || 0) + 1));
    return Array.from(map.entries())
      .map(([source, count]) => ({ source, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8);
  }, [alerts]);

  return { alerts, logs, insights, trend, distribution, topSources };
}
