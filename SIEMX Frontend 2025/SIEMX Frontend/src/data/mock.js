import { format } from 'date-fns';

function randInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

const IPs = ['10.0.0.2','10.0.1.4','172.16.3.22','192.168.0.24','192.168.1.50','203.0.113.7'];
const Dest = ['auth-service','db.internal','admin-portal','fileserver','mail','vpn'];
const Statuses = ['Open','Investigating','Resolved'];
const Actions = ['Blocked IP','Disabled user','Quarantined host','None'];
const Levels = ['Low','Medium','High'];

export function generateInitialData() {
  const timeNow = Date.now();
  const alerts = Array.from({ length: 40 }).map((_, i) => makeAlert(timeNow - i * 60000));
  const logs = Array.from({ length: 40 }).map((_, i) => makeLog(timeNow - i * 45000));
  const trend = makeTrend();
  const distribution = makeDistribution(alerts);
  const topSources = makeTopSources(alerts);
  const insights = Array.from({ length: 10 }).map(() => makeInsight());
  return { alerts, logs, trend, distribution, topSources, insights };
}

function makeAlert(ts) {
  const level = pick(Levels);
  return {
    id: cryptoRandomId(),
    timestamp: format(ts, 'HH:mm:ss'),
    source: pick(IPs),
    destination: pick(Dest),
    level: level,
    status: pick(Statuses),
    action: level === 'High' ? pick(['Blocked IP', 'Disabled user']) : pick(Actions),
  };
}

function makeLog(ts) {
  const level = pick(Levels);
  return {
    id: cryptoRandomId(),
    timestamp: format(ts, 'HH:mm:ss'),
    level,
    message: `${level} event from ${pick(IPs)} targeting ${pick(Dest)} - code ${randInt(1000,9999)}`,
  };
}

function makeTrend() {
  return Array.from({ length: 24 }).map((_, i) => ({
    time: `${i}:00`,
    count: randInt(5, 40)
  }));
}

function makeDistribution(alerts) {
  const high = alerts.filter(a => a.level === 'High').length;
  const medium = alerts.filter(a => a.level === 'Medium').length;
  const low = alerts.filter(a => a.level === 'Low').length;
  return [
    { name: 'High', value: high },
    { name: 'Medium', value: medium },
    { name: 'Low', value: low },
  ];
}

function makeTopSources(alerts) {
  const counts = {};
  for (const a of alerts) counts[a.source] = (counts[a.source] || 0) + 1;
  return Object.entries(counts)
    .map(([source, count]) => ({ source, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);
}

function makeInsight() {
  const ip = pick(IPs);
  const msg = pick([
    `Blocked IP ${ip} due to repeated login failures`,
    `Disabled user on ${pick(Dest)} for anomalous activity`,
    `Quarantined host communicating with C2 server`,
    `Raised baseline for ${pick(Dest)} based on behavior`,
    `Recommended MFA enforcement for admin accounts`,
  ]);
  return msg;
}

function cryptoRandomId() {
  // Fallback for environments without crypto.randomUUID
  if (crypto?.randomUUID) return crypto.randomUUID();
  return 'id-' + Math.random().toString(36).slice(2, 10);
}

export function nextTick(data) {
  const ts = Date.now();
  const newAlert = makeAlert(ts);
  const newLog = makeLog(ts);
  const alerts = [newAlert, ...data.alerts].slice(0, 60);
  const logs = [newLog, ...data.logs].slice(0, 60);
  const trend = data.trend.map((t, idx) => ({ ...t, count: Math.max(0, t.count + (idx % 3 === 0 ? randInt(-2, 5) : randInt(-1, 2))) }));
  const distribution = makeDistribution(alerts);
  const topSources = makeTopSources(alerts);
  const maybeNewInsight = Math.random() < 0.3 ? [makeInsight(), ...data.insights] : data.insights;
  return { alerts, logs, trend, distribution, topSources, insights: maybeNewInsight.slice(0, 30) };
}
