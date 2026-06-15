'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface Route {
  from: string;
  to: string;
  flights: number;
}

interface Props {
  routes: Route[];
}

export default function RouteDensity({ routes }: Props) {
  const data = routes
    .sort((a, b) => b.flights - a.flights)
    .slice(0, 8)
    .map(r => ({ name: `${r.from}→${r.to}`, flights: r.flights }));

  const colors = ['#38BDF8','#34d399','#818CF8','#fbbf24','#f87171','#38bdf8','#fb923c','#e879f9'];

  return (
    <div className="glass" style={{ padding: 16 }}>
      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#f1f5f9' }}>🛣 Route Density</div>
        <div style={{ fontSize: 11, color: '#475569', marginTop: 2 }}>
          Busiest routes by number of active flights · 
        </div>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 4, right: 8, left: -20, bottom: 40 }}>
          <XAxis
            dataKey="name"
            tick={{ fill: '#64748b', fontSize: 10 }}
            angle={-35}
            textAnchor="end"
            interval={0}
          />
          <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
          <Tooltip
            contentStyle={{ background: '#0B1117', border: '1px solid #1F2937', borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: '#38BDF8' }}
            itemStyle={{ color: '#e2e8f0' }}
          />
          <Bar dataKey="flights" radius={[4,4,0,0]}>
            {data.map((_, i) => <Cell key={i} fill={colors[i % colors.length]} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}