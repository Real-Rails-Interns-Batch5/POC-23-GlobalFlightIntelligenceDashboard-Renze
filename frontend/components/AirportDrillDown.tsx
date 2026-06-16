'use client';
import { useEffect, useState } from 'react';

interface Props {
  code: string;
  onClose: () => void;
}

interface Flight {
  id: string;
  callsign: string;
  origin?: string | null;
  dest?: string | null;
  speed: number;
}

interface AirportDetail {
  mode?: string;
  source?: string;
  airport?: {
    code: string;
    city: string;
    name: string;
  };
  traffic?: number;
  flights?: Flight[];
}

export default function AirportDrillDown({ code, onClose }: Props) {
  const [data, setData] = useState<AirportDetail | null>(null);

  useEffect(() => {
    fetch(`http://localhost:8000/api/airport/${code}`)
      .then(r => r.json())
      .then(setData);
  }, [code]);

  if (!data) return (
    <div className="glass" style={{ padding: 16, color: '#64748b', fontSize: 13 }}>
      Loading {code}...
    </div>
  );

  const isLive = data.mode === 'live' || data.source?.toLowerCase().includes('live');
  const sourceSummary = isLive ? 'Nearby OpenSky aircraft.' : 'Using mock airport data.';

  return (
    <div className="glass" style={{ padding: 20 }}>
      <div
        style={{
          color: '#38BDF8',
          fontSize: 12,
          fontWeight: 700,
          letterSpacing: '1.5px',
          marginBottom: 12,
          textTransform: 'uppercase',
        }}
      >
        Airport Intelligence
      </div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: 12,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 18,
              fontWeight: 700,
              color: '#818CF8',
              marginBottom: 4,
            }}
          >
            {data.airport?.code} - {data.airport?.city}
          </div>

          <div
            style={{
              fontSize: 13,
              color: '#94a3b8',
              marginBottom: 8,
            }}
          >
            {data.airport?.name}
          </div>

          <span className={isLive ? 'badge-live' : 'badge-mock'}>
            {isLive ? 'Live OpenSky' : 'Mock fallback'}
          </span>
        </div>
        <button onClick={onClose} style={{
          background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)',
          color: '#f87171', borderRadius: 6, padding: '3px 10px', cursor: 'pointer', fontSize: 12,
        }}>x</button>
      </div>

      <div style={{ fontSize: 11, color: '#64748b', marginBottom: 12, lineHeight: 1.35 }}>
        {sourceSummary}
      </div>

      <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
        <div style={{ flex: 1, background: 'rgba(129,140,248,0.08)', borderRadius: 8, padding: '10px 12px', textAlign: 'center' }}>
          <div style={{ fontSize: 20, fontWeight: 700, color: '#818CF8' }}>{data.traffic || 0}</div>
          <div style={{ fontSize: 11, color: '#64748b' }}>{isLive ? 'Nearby live aircraft' : 'Daily movements'}</div>
        </div>
        <div style={{ flex: 1, background: 'rgba(56,189,248,0.08)', borderRadius: 8, padding: '10px 12px', textAlign: 'center' }}>
          <div style={{ fontSize: 20, fontWeight: 700, color: '#60a5fa' }}>{data.flights?.length}</div>
          <div style={{ fontSize: 11, color: '#64748b' }}>Tracked flights</div>
        </div>
      </div>

      <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 6, fontWeight: 600 }}>Recent flights</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {data.flights?.slice(0, 4).map(f => (
          <div key={f.id} style={{
            display: 'flex', justifyContent: 'space-between',
            padding: '6px 10px', background: 'rgba(255,255,255,0.02)',
            borderRadius: 6, fontSize: 12,
          }}>
            <span style={{ color: '#60a5fa', fontWeight: 600 }}>{f.callsign}</span>
            <span style={{ color: '#64748b' }}>
              {f.origin || 'OpenSky'} -&gt; {f.dest || 'live state'}
            </span>
            <span style={{ color: '#34d399' }}>{f.speed} kts</span>
          </div>
        ))}
      </div>
    </div>
  );
}
