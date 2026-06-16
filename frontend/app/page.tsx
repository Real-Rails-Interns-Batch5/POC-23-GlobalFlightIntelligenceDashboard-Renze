'use client';

import { useState, useEffect, useCallback } from 'react';
import dynamic from 'next/dynamic';
import AlertCards from '@/components/AlertCards';
import StatsBar from '@/components/StatsBar';
import WhyThisMatters from '@/components/WhyThisMatters';
import WhoControlsTheRail from '@/components/WhoControlsTheRail';
import RouteDensity from '@/components/RouteDensity';
import AirportDrillDown from '@/components/AirportDrillDown';
import FilterBar from '@/components/FilterBar';
import HistoricalReplay from '@/components/HistoricalReplay';
import Intro from '@/components/Intro';

const LiveMap = dynamic(() => import('@/components/LiveMap'), { ssr: false });

interface Flight {
  id: string;
  callsign: string;
  lat: number;
  lng: number;
  altitude: number;
  speed: number;
  heading: number;
  country: string;
  source: string;
  origin?: string | null;
  dest?: string | null;
}

interface Alert {
  id: string;
  callsign: string;
  type: string;
  severity: string;
  airport: string;
  message: string;
  timestamp: string;
  source: string;
}

interface Route {
  from: string;
  to: string;
  flights: number;
}

interface Airport {
  code: string;
  name: string;
  lat: number;
  lng: number;
  city: string;
}

export default function Dashboard() {
  const [flights, setFlights]     = useState<Flight[]>([]);
  const [alerts, setAlerts]       = useState<Alert[]>([]);
  const [routes, setRoutes]       = useState<Route[]>([]);
  const [airports, setAirports]   = useState<Airport[]>([]);
  const [sourceMode, setSourceMode] = useState<'live' | 'mock' | ''>('');
  const [alertSource, setAlertSource] = useState('');
  const [routeSource, setRouteSource] = useState('');
  const [loading, setLoading]     = useState(true);
  const [filter, setFilter]       = useState({ country: '', minSpeed: 0, minAlt: 0 });
  const [selectedAirport, setSelectedAirport] = useState<string | null>(null);
  const [showIntro, setShowIntro] = useState(true);
  const [activeSection, setActiveSection] = useState<'intelligence' | 'replay'>('intelligence');
  const handleAirportClick = useCallback((code: string) => setSelectedAirport(code), []);

  async function fetchAll() {
    try {
      const [fRes, aRes, rRes, apRes] = await Promise.all([
        fetch('http://localhost:8000/api/flights'),
        fetch('http://localhost:8000/api/alerts'),
        fetch('http://localhost:8000/api/routes'),
        fetch('http://localhost:8000/api/airports'),
      ]);
      const fData  = await fRes.json();
      const aData  = await aRes.json();
      const rData  = await rRes.json();
      const apData = await apRes.json();

      setFlights(fData.flights    || []);
      setAlerts(aData.alerts      || []);
      setRoutes(rData.routes      || []);
      setAirports(apData.airports || []);
      setSourceMode(fData.mode === 'live' ? 'live' : fData.mode === 'mock' ? 'mock' : '');
      setAlertSource(aData.source || '');
      setRouteSource(rData.source || '');
    } catch (e) {
      console.error('Fetch error:', e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const firstFetch = window.setTimeout(() => {
      fetchAll();
    }, 0);
    const interval = setInterval(fetchAll, 15000);
    return () => {
      window.clearTimeout(firstFetch);
      clearInterval(interval);
    };
  }, []);

  const filteredFlights = flights.filter(f => {
    if (filter.country  && !f.country?.toLowerCase().includes(filter.country.toLowerCase())) return false;
    if (filter.minSpeed && f.speed < filter.minSpeed) return false;
    if (filter.minAlt   && f.altitude < filter.minAlt) return false;
    return true;
  });

  function downloadData() {
    const blob = new Blob(
      [JSON.stringify({ flights: filteredFlights.slice(0, 20), alerts, routes }, null, 2)],
      { type: 'application/json' }
    );
    const url = URL.createObjectURL(blob);
    const a   = document.createElement('a');
    a.href    = url;
    a.download = 'flight-intelligence-sample.json';
    a.click();
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#030712' }}>
        <div style={{ textAlign: 'center', color: '#38BDF8' }}>
          <div style={{ fontSize: 40, marginBottom: 16 }}>✈</div>
          <div style={{ fontSize: 18, fontWeight: 600 }}>Loading Flight Intelligence...</div>
          <div style={{ fontSize: 13, color: '#475569', marginTop: 8 }}>Connecting to data sources</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ height: '100vh', background: '#030712', display: 'flex', overflow: 'hidden' }}>
      {showIntro && <Intro onComplete={() => setShowIntro(false)} />}

      {/* ════════════════════════════════════
          LEFT 70% — MAP ONLY, FULL HEIGHT
      ════════════════════════════════════ */}
      <div style={{
        width: '70%',
        flexShrink: 0,
        position: 'relative',
        borderRight: '1px solid #1F2937',
        overflow: 'hidden',
        height: '100vh',
      }}>
        {/* Legend pills — float top-center over map */}
        <div style={{
          position: 'absolute',
          top: 14,
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          gap: 8,
          zIndex: 1000,
          pointerEvents: 'none',
        }}>
          {[
            { label: '🟢 LIVE FLIGHTS', color: '#34d399', border: 'rgba(52,211,153,0.4)' },
            { label: '🟡 SYNTHETIC',    color: '#fbbf24', border: 'rgba(251,191,36,0.4)'  },
            { label: '🔵 AIRPORTS',     color: '#818CF8', border: 'rgba(129,140,248,0.4)' },
          ].map(p => (
            <span key={p.label} style={{
              background: 'rgba(10,15,26,0.85)',
              border: `1px solid ${p.border}`,
              color: p.color,
              padding: '5px 12px',
              borderRadius: 999,
              fontSize: 11,
              fontWeight: 600,
              backdropFilter: 'blur(8px)',
            }}>{p.label}</span>
          ))}
        </div>

        {/* Map fills entire left column */}
        <LiveMap
          flights={filteredFlights}
          airports={airports}
          onAirportClick={handleAirportClick}
        />
      </div>

      {/* ════════════════════════════════════
          RIGHT 30% — INTELLIGENCE SIDEBAR
      ════════════════════════════════════ */}
      <aside style={{
        width: '30%',
        flexShrink: 0,
        background: '#0B1117',
        height: '100vh',
        overflowY: 'auto',
        overflowX: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}>

        {/* ── SIDEBAR HEADER (replaces top navbar) ── */}
        <div style={{
          padding: '16px 16px 12px',
          borderBottom: '1px solid #1F2937',
          background: 'rgba(3,7,18,0.95)',
          flexShrink: 0,
          position: 'sticky',
          top: 0,
          zIndex: 50,
        }}>
          {/* Title row */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
            <span style={{ fontSize: 20 }}>✈</span>
            <div>
              <div style={{
                fontSize: 15,
                fontWeight: 800,
                color: '#f8fafc',
                letterSpacing: '0.8px',
                textTransform: 'uppercase',
                whiteSpace: 'nowrap',
                lineHeight: 1.2,
              }}>
                GLOBAL FLIGHT INTELLIGENCE
              </div>
              <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>
                Real-Time Aviation Intelligence Platform
              </div>
            </div>
          </div>

          {/* Status row */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className={sourceMode === 'live' ? 'badge-live' : 'badge-mock'}>
                {sourceMode === 'live' ? 'Live OpenSky' : 'Mock fallback'}
              </span>
              <span style={{ fontSize: 11, color: '#64748b' }}>
                {filteredFlights.length} flights
              </span>
            </div>
            <div style={{ textAlign: 'right', lineHeight: 1.3 }}>
              <div style={{ fontSize: 9, color: '#64748b', textTransform: 'uppercase', letterSpacing: '1px' }}>
                Last Updated
              </div>
              <div style={{ fontSize: 11, color: '#38BDF8', fontWeight: 700 }}>
                {new Date().toLocaleTimeString()}
              </div>
            </div>
          </div>
          <div style={{ fontSize: 10, color: '#64748b', marginTop: 8, lineHeight: 1.35 }}>
            {sourceMode === 'live' ? 'Live aircraft positions from OpenSky.' : 'Using mock fallback data.'}
          </div>
        </div>

        {/* ── TAB SWITCHER: Intelligence | Replay ── */}
        <div style={{ display: 'flex', borderBottom: '1px solid #1F2937', flexShrink: 0 }}>
          {(['intelligence', 'replay'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveSection(tab)}
              style={{
  flex: 1,
  padding: '11px 0',
  background: activeSection === tab ? 'rgba(56,189,248,0.08)' : 'transparent',
  borderTop: 'none',
  borderLeft: 'none',
  borderRight: 'none',
  borderBottom: activeSection === tab ? '2px solid #38BDF8' : '2px solid transparent',
  color: activeSection === tab ? '#38BDF8' : '#64748b',
  fontSize: 11,
  fontWeight: 700,
  cursor: 'pointer',
  letterSpacing: '0.5px',
  textTransform: 'uppercase' as const,
}}
            >
              {tab === 'intelligence' ? '🛰 Intelligence' : '⏪ Replay'}
            </button>
          ))}
        </div>

        {/* ── INTELLIGENCE TAB ── */}
        {activeSection === 'intelligence' ? (
          <>
            {/* SECTION A — Stats */}
            <section style={{ borderBottom: '1px solid #1F2937', padding: '14px' }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 10 }}>
                🛰 Intelligence Layer
              </div>
              <StatsBar flights={filteredFlights} alerts={alerts} routes={routes} />
            </section>

            {/* SECTION D — Filters */}
            <section style={{ borderBottom: '1px solid #1F2937', padding: '14px' }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 8 }}>
                🔍 Filters
              </div>
              <FilterBar filter={filter} onChange={setFilter} />
            </section>

            {/* Active Alerts */}
            <section style={{ borderBottom: '1px solid #1F2937', padding: '14px' }}>
              <AlertCards alerts={alerts} source={alertSource} />
            </section>

            {/* Route Density */}
            <section style={{ borderBottom: '1px solid #1F2937', padding: '14px' }}>
              
              <div style={{ overflowX: 'auto' }}>
                <RouteDensity routes={routes} source={routeSource} />
              </div>
            </section>

            {/* SECTION B — Why This Matters */}
            <section style={{ borderBottom: '1px solid #1F2937', padding: '14px' }}>
              
              <WhyThisMatters />
            </section>

            {/* SECTION C — Who Controls the Rail */}
            <section style={{ borderBottom: '1px solid #1F2937', padding: '14px' }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 8 }}>
                🏛 Who Controls the Rail
              </div>
              <WhoControlsTheRail />
            </section>

            {/* SECTION E — Download */}
            <section style={{ padding: '14px' }}>
              <button
                onClick={downloadData}
                style={{
                  width: '100%',
                  background: 'rgba(56,189,248,0.1)',
                  border: '1px solid rgba(56,189,248,0.3)',
                  color: '#38BDF8',
                  padding: '10px 0',
                  borderRadius: 8,
                  fontSize: 13,
                  cursor: 'pointer',
                  fontWeight: 600,
                  letterSpacing: '0.3px',
                }}
              >
                ⬇ Download Sample Data
              </button>
              <div style={{ textAlign: 'center', fontSize: 10, color: '#334155', marginTop: 10 }}>
                OpenSky Network + Synthetic mock engine · Next.js + FastAPI
              </div>
            </section>
          </>
        ) : (
          /* ── REPLAY TAB ── */
          <div style={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>
            <HistoricalReplay />
          </div>
        )}

      </aside>

      {/* ── AIRPORT DRILL-DOWN MODAL ── */}
      {selectedAirport && (
        <div style={{
          position: 'fixed', inset: 0,
          background: 'rgba(0,0,0,0.65)',
          backdropFilter: 'blur(6px)',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          zIndex: 9999,
        }}>
          <div style={{ width: '850px', maxWidth: '90vw' }}>
            <AirportDrillDown code={selectedAirport} onClose={() => setSelectedAirport(null)} />
          </div>
        </div>
      )}
    </div>
  );
}
