'use client';
import { useEffect, useState, useRef } from 'react';

interface Flight {
  id: string;
  callsign: string;
  origin?: string | null;
  dest?: string | null;
  altitude: number;
}

interface Alert {
  severity: string;
}

interface Snapshot {
  timestamp: string;
  flights?: Flight[];
  alerts?: Alert[];
}

export default function HistoricalReplay() {
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [source, setSource] = useState('');
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/replay')
      .then(r => r.json())
      .then(d => {
        setSnapshots(d.snapshots || []);
        setSource(d.source || '');
      });
  }, []);

  useEffect(() => {
    if (playing) {
      intervalRef.current = setInterval(() => {
        setIndex(i => {
          if (i >= snapshots.length - 1) {
            setPlaying(false);
            return i;
          }
          return i + 1;
        });
      }, 800);
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [playing, snapshots.length]);

  const snap = snapshots[index];
  const isLive = source.toLowerCase().includes('live');
  const sourceSummary = isLive ? 'OpenSky-based replay simulation.' : 'Using mock replay data.';

  return (
    <div className="glass" style={{ padding: 16 }}>
      <div style={{ marginBottom: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: '#f1f5f9' }}>Historical Replay</div>
          <span className={isLive ? 'badge-live' : 'badge-mock'} style={{ fontSize: 10 }}>
            {isLive ? 'Live OpenSky' : 'Mock fallback'}
          </span>
        </div>
        <div style={{ fontSize: 11, color: '#64748b', marginTop: 4, lineHeight: 1.35 }}>
          {source ? sourceSummary : 'Loading replay source.'}
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
        <button onClick={() => setIndex(0)} style={btnStyle}>⏮</button>
        <button onClick={() => setIndex(i => Math.max(0, i - 1))} style={btnStyle}>◀</button>
        <button onClick={() => setPlaying(p => !p)} style={{ ...btnStyle, background: 'rgba(56,189,248,0.2)', color: '#38BDF8', minWidth: 70 }}>
          {playing ? '⏸ Pause' : '▶ Play'}
        </button>
        <button onClick={() => setIndex(i => Math.min(snapshots.length - 1, i + 1))} style={btnStyle}>▶</button>
        <button onClick={() => setIndex(snapshots.length - 1)} style={btnStyle}>⏭</button>

        <input
          type="range" min={0} max={Math.max(0, snapshots.length - 1)} value={index}
          onChange={e => setIndex(Number(e.target.value))}
          style={{ flex: 1, accentColor: '#38BDF8' }}
        />
        <span style={{ fontSize: 11, color: '#64748b', minWidth: 50, textAlign: 'right' }}>
          {snapshots.length ? index + 1 : 0}/{snapshots.length}
        </span>
      </div>

      {snap && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div style={{ fontSize: 12, color: '#38BDF8' }}>
            {new Date(snap.timestamp).toLocaleString()}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
            <div style={statBox}>
              <div style={{ fontSize: 20, fontWeight: 700, color: '#34d399' }}>{snap.flights?.length}</div>
              <div style={{ fontSize: 11, color: '#64748b' }}>Flights tracked</div>
            </div>
            <div style={statBox}>
              <div style={{ fontSize: 20, fontWeight: 700, color: '#f87171' }}>{snap.alerts?.length}</div>
              <div style={{ fontSize: 11, color: '#64748b' }}>Demo alerts</div>
            </div>
            <div style={statBox}>
              <div style={{ fontSize: 20, fontWeight: 700, color: '#818CF8' }}>
                {snap.alerts?.filter(a => a.severity === 'high').length}
              </div>
              <div style={{ fontSize: 11, color: '#64748b' }}>High severity</div>
            </div>
          </div>

          <div style={{ fontSize: 12, color: '#94a3b8', fontWeight: 600, marginTop: 4 }}>Flights at this moment</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 220, overflowY: 'auto' }}>
            {snap.flights?.slice(0, 10).map(f => (
              <div key={f.id} style={{
                display: 'flex', justifyContent: 'space-between',
                padding: '5px 10px', background: 'rgba(255,255,255,0.02)',
                borderRadius: 6, fontSize: 11,
              }}>
                <span style={{ color: '#38BDF8', fontWeight: 600 }}>{f.callsign}</span>
                <span style={{ color: '#64748b' }}>{f.origin || 'OpenSky'} -&gt; {f.dest || 'live state'}</span>
                <span style={{ color: '#34d399' }}>{f.altitude.toLocaleString()} m</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

const btnStyle: React.CSSProperties = {
  background: 'rgba(255,255,255,0.05)',
  border: '1px solid rgba(255,255,255,0.1)',
  color: '#e2e8f0',
  padding: '5px 10px',
  borderRadius: 6,
  cursor: 'pointer',
  fontSize: 13,
};

const statBox: React.CSSProperties = {
  background: 'rgba(255,255,255,0.02)',
  border: '1px solid rgba(255,255,255,0.06)',
  borderRadius: 8,
  padding: '10px 12px',
  textAlign: 'center',
};
