'use client';

import { useState, useEffect } from 'react';
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

const HEADER_HEIGHT = 60;

export default function Dashboard() {
  const [flights, setFlights]   = useState<any[]>([]);
  const [alerts, setAlerts]     = useState<any[]>([]);
  const [routes, setRoutes]     = useState<any[]>([]);
  const [airports, setAirports] = useState<any[]>([]);
  const [source, setSource]     = useState('');
  const [loading, setLoading]   = useState(true);
  const [filter, setFilter]     = useState({ country: '', minSpeed: 0, minAlt: 0 });
  const [selectedAirport, setSelectedAirport] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'map' | 'replay'>('map');
  const [showIntro, setShowIntro] = useState(true);

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
      setSource(fData.source      || '');
    } catch (e) {
      console.error('Fetch error:', e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 15000);
    return () => clearInterval(interval);
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
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: '100vh', background: '#030712',
      }}>
        <div style={{ textAlign: 'center', color: '#38BDF8' }}>
          <div style={{ fontSize: 40, marginBottom: 16 }}>✈</div>
          <div style={{ fontSize: 18, fontWeight: 600 }}>Loading Flight Intelligence...</div>
          <div style={{ fontSize: 13, color: '#475569', marginTop: 8 }}>Connecting to data sources</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      height: '100vh',
      background: '#030712',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {showIntro && <Intro onComplete={() => setShowIntro(false)} />}

      {/* ══════════════════════════════════════
          HEADER — full width, fixed height
      ══════════════════════════════════════ */}
      <header style={{
        height: HEADER_HEIGHT,
        minHeight: HEADER_HEIGHT,
        flexShrink: 0,
        background: 'rgba(3,7,18,0.92)',
        borderBottom: '1px solid #1F2937',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        zIndex: 100,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <span style={{ fontSize: 24 }}>✈</span>
          <div>
            <div style={{
              fontSize: 20, fontWeight: 800, color: '#f8fafc',
              letterSpacing: '1px', textTransform: 'uppercase',
            }}>
              GLOBAL FLIGHT INTELLIGENCE
            </div>
            <div style={{ fontSize: 12, color: '#94a3b8' }}>Real-Time Aviation Intelligence Platform</div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span className={source.includes('live') ? 'badge-live' : 'badge-mock'}>
            {source.includes('live') ? 'LIVE' : 'SYNTHETIC'}
          </span>
          <span style={{ fontSize: 12, color: '#64748b' }}>{filteredFlights.length} flights</span>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', lineHeight: 1.2 }}>
            <span style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase', letterSpacing: '1px' }}>
              Last Updated
            </span>
            <span style={{ fontSize: 12, color: '#38BDF8', fontWeight: 600 }}>
              {new Date().toLocaleTimeString()}
            </span>
          </div>
        </div>
      </header>

      {/* ══════════════════════════════════════
          BODY — 70 / 30 split, fills remaining height
      ══════════════════════════════════════ */}
      <div style={{
        flex: 1,
        display: 'flex',
        overflow: 'hidden',        // children scroll independently
        minHeight: 0,
      }}>

        {/* ════════════════════════════
            LEFT 70% — MAP STAGE
        ════════════════════════════ */}
        <div style={{
          width: '70%',
          flexShrink: 0,
          display: 'flex',
          flexDirection: 'column',  // tab bar on top, map fills the rest
          borderRight: '1px solid #1F2937',
          overflow: 'hidden',
          minHeight: 0,
        }}>

          {/* ── Combined bar: tab buttons LEFT · legend pills RIGHT ── */}
          <div style={{
            height: 44,
            minHeight: 44,
            flexShrink: 0,
            background: '#0a0f1a',
            borderBottom: '1px solid #1F2937',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 16px',
          }}>
            {/* Tab buttons */}
            <div style={{ display: 'flex', gap: 8 }}>
              {(['map', 'replay'] as const).map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  style={{
                    padding: '6px 16px',
                    borderRadius: 8,
                    border: activeTab === tab
                      ? '1px solid rgba(56,189,248,0.5)'
                      : '1px solid #1F2937',
                    background: activeTab === tab
                      ? 'rgba(56,189,248,0.15)'
                      : 'transparent',
                    color: activeTab === tab ? '#38BDF8' : '#64748b',
                    boxShadow: activeTab === tab
                      ? '0 0 12px rgba(56,189,248,0.2)'
                      : 'none',
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  {tab === 'map' ? '🗺 Live Map' : '⏪ Historical Replay'}
                </button>
              ))}
            </div>

            {/* Legend pills — only shown when map is active */}
            {activeTab === 'map' && (
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <span style={{
                  background: 'rgba(52,211,153,0.12)',
                  border: '1px solid rgba(52,211,153,0.3)',
                  color: '#34d399',
                  padding: '4px 10px',
                  borderRadius: '999px',
                  fontSize: 11,
                  fontWeight: 600,
                }}>🟢 LIVE FLIGHTS</span>
                <span style={{
                  background: 'rgba(251,191,36,0.12)',
                  border: '1px solid rgba(251,191,36,0.3)',
                  color: '#fbbf24',
                  padding: '4px 10px',
                  borderRadius: '999px',
                  fontSize: 11,
                  fontWeight: 600,
                }}>🟡 SYNTHETIC</span>
                <span style={{
                  background: 'rgba(129,140,248,0.12)',
                  border: '1px solid rgba(129,140,248,0.3)',
                  color: '#818CF8',
                  padding: '4px 10px',
                  borderRadius: '999px',
                  fontSize: 11,
                  fontWeight: 600,
                }}>🔵 AIRPORTS</span>
              </div>
            )}
          </div>

          {/* ── Map / Replay — fills all remaining space ── */}
          <div style={{ flex: 1, minHeight: 0, overflow: 'hidden', position: 'relative', height: '100%' }}>
            {activeTab === 'map'
              ? <LiveMap
                  flights={filteredFlights}
                  airports={airports}
                  onAirportClick={setSelectedAirport}
                />
              : <HistoricalReplay />
            }
          </div>
        </div>

        {/* ════════════════════════════
            RIGHT 30% — INTELLIGENCE SIDEBAR
        ════════════════════════════ */}
        <aside style={{
          width: '30%',
          flexShrink: 0,
          background: '#0B1117',
          overflowY: 'auto',
          overflowX: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          minHeight: 0,
        }}>

         
          
          {/* ── SECTION A — Intelligence Layer (Stats + Alerts) ── */}
          <section style={{ borderBottom: '1px solid #1F2937', padding: '14px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: 12,
            }}>
              <span style={{
                fontSize: 12, fontWeight: 700, color: '#94a3b8',
                textTransform: 'uppercase', letterSpacing: '0.8px',
              }}>
                🛰 Intelligence Layer
              </span>
              <span style={{
                fontSize: 10, fontWeight: 600, color: '#818CF8',
                background: 'rgba(129,140,248,0.12)',
                border: '1px solid rgba(129,140,248,0.3)',
                padding: '2px 8px', borderRadius: 20,
                textTransform: 'uppercase', letterSpacing: '0.5px',
              }}>
                
              </span>
            </div>
            <div style={{ overflowX: 'auto', paddingBottom: 4 }}>
              <StatsBar flights={filteredFlights} alerts={alerts} routes={routes} />
            </div>

             {/* ── SECTION D — Filters ── */}
          <section style={{ borderBottom: '1px solid #1F2937', padding: '14px' }}>
            <div style={{
              fontSize: 11, fontWeight: 700, color: '#94a3b8',
              textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 8,
            }}>
              🔍 Filters 
            </div>
            <FilterBar filter={filter} onChange={setFilter} />
          </section>

            <div style={{ marginTop: 12 }}>
              <AlertCards alerts={alerts} />
            </div>
          </section>

          {/* ── Route Density ── */}
          <section style={{ borderBottom: '1px solid #1F2937', padding: '14px' }}>
            <div style={{
              fontSize: 11, fontWeight: 700, color: '#94a3b8',
              textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 8,
            }}>
              
            </div>
            <div style={{ overflowX: 'auto' }}>
              <RouteDensity routes={routes} />
            </div>
          </section>

          {/* ── SECTION B — Why This Matters ── */}
          <section style={{ borderBottom: '1px solid #1F2937', padding: '14px' }}>
            <div style={{
              fontSize: 11, fontWeight: 700, color: '#94a3b8',
              textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 8,
            }}>
              
            </div>
            <WhyThisMatters />
          </section>

          {/* ── SECTION C — Who Controls the Rail ── */}
          <section style={{ borderBottom: '1px solid #1F2937', padding: '14px' }}>
            <div style={{
              fontSize: 11, fontWeight: 700, color: '#94a3b8',
              textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 8,
            }}>
              🏛 Who Controls the Rail
            </div>
            {/*
              No more overflowX: auto here — WhoControlsTheRail now uses
              a 2-column grid that fits naturally inside the 30% sidebar.
            */}
            <WhoControlsTheRail />
          </section>

          

          {/* ── SECTION E — Download ── */}
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

        </aside>
      </div>

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