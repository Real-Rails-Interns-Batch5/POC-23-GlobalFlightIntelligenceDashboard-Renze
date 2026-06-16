'use client';

interface Flight {
  country?: string;
  altitude: number;
  speed: number;
}

interface Alert {
  severity: string;
}

interface Route {
  from?: string;
  to?: string;
}

interface Props {
  flights: Flight[];
  alerts:  Alert[];
  routes:  Route[];
}

export default function StatsBar({ flights, alerts, routes }: Props) {
  const countries  = new Set(flights.map(f => f.country)).size;
  const airborne   = flights.filter(f => f.altitude > 1000).length;
  const highAlerts = alerts.filter(a => a.severity === 'high').length;
  const avgSpeed   = flights.length
    ? Math.round(flights.reduce((s, f) => s + f.speed, 0) / flights.length)
    : 0;

  const stats = [
    { label: 'Total Flights',    value: flights.length,  color: '#38BDF8', icon: '✈' },
    { label: 'Airborne',         value: airborne,         color: '#34d399', icon: '🛫' },
    { label: 'Countries',        value: countries,        color: '#818CF8', icon: '🌍' },
    { label: 'Active Routes',    value: routes.length,    color: '#38bdf8', icon: '🛣' },
    { label: 'High Alerts',      value: highAlerts,       color: '#f87171', icon: '🚨' },
    { label: 'Avg Speed (kts)',  value: avgSpeed,         color: '#fbbf24', icon: '⚡' }
  ];

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(6, 1fr)',
      gap: 12,
    }}>
      {stats.map(s => (
        <div key={s.label} className="stat-tile" style={{ padding: '16px 18px', cursor: 'default' }}>
          <div style={{ fontSize: 20, marginBottom: 6 }}>{s.icon}</div>
          <div
  style={{
    fontSize: s.label === 'System Status' ? 18 : 22,
    fontWeight: 700,
    color: s.color,
  }}
>
  {s.value}
</div>
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>{s.label}</div>
        </div>
      ))}
    </div>
  );
}
