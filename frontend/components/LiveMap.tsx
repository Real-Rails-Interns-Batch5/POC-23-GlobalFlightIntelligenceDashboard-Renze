'use client';

import { useEffect, useRef } from 'react';
import L from 'leaflet';

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
}

interface Airport {
  code: string;
  name: string;
  lat: number;
  lng: number;
  city: string;
}

interface Props {
  flights: Flight[];
  airports: Airport[];
  onAirportClick: (code: string) => void;
}

export default function LiveMap({ flights, airports, onAirportClick }: Props) {
  const mapRef     = useRef<L.Map | null>(null);
  const mapDivRef  = useRef<HTMLDivElement>(null);
  const markersRef = useRef<L.Marker[]>([]);
  const airportRef = useRef<L.Marker[]>([]);

  useEffect(() => {
    if (mapRef.current || !mapDivRef.current) return;

    const map = L.map(mapDivRef.current, {
  center: [20, 10],
  zoom: 2,
  minZoom: 2,
  maxZoom: 18,
  zoomControl: true,
  worldCopyJump: true,
  maxBounds: L.latLngBounds(
    L.latLng(-85, -Infinity),
    L.latLng(85,  Infinity)
  ),
  maxBoundsViscosity: 1.0,
});

    mapRef.current = map;

    L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      {
        attribution: '© OpenStreetMap © CartoDB',
        maxZoom: 18,
        noWrap: false,   // tiles repeat horizontally — enables infinite sideways pan
      }
    ).addTo(map);

    // Just fix layout after mount — no fitBounds, no view locking
    setTimeout(() => map.invalidateSize(), 150);
    setTimeout(() => map.invalidateSize(), 600);

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Update flight markers
  useEffect(() => {
    if (!mapRef.current) return;
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    flights.forEach(flight => {
      if (!flight.lat || !flight.lng) return;
      const isLive = flight.source?.toLowerCase().includes('live');
      const color  = isLive ? '#34d399' : '#fbbf24';

      const icon = L.divIcon({
        className: '',
        html: `<div style="
          transform: rotate(${flight.heading}deg);
          font-size: 16px;
          line-height: 1;
          filter: drop-shadow(0 0 4px ${color});
          color: ${color};
        ">✈</div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10],
      });

      const marker = L.marker([flight.lat, flight.lng], { icon })
        .bindTooltip(`
          <div style="background:#0B1117;border:1px solid #1F2937;padding:8px 12px;border-radius:8px;color:#e2e8f0;font-size:12px;min-width:160px">
            <div style="font-weight:700;font-size:14px;color:#38BDF8;margin-bottom:4px">${flight.callsign}</div>
            <div>🌍 ${flight.country}</div>
            <div>📡 Alt: ${flight.altitude.toLocaleString()} m</div>
            <div>⚡ Speed: ${flight.speed} kts</div>
            <div>🧭 Heading: ${flight.heading}°</div>
            <div style="margin-top:4px;font-size:10px;color:#475569">${flight.source}</div>
          </div>
        `, { permanent: false, opacity: 1, className: 'custom-tooltip' })
        .addTo(mapRef.current!);

      markersRef.current.push(marker);
    });
  }, [flights]);

  // Airport markers
  useEffect(() => {
    if (!mapRef.current || airports.length === 0) return;
    airportRef.current.forEach(m => m.remove());
    airportRef.current = [];

    airports.forEach(ap => {
      const icon = L.divIcon({
        className: '',
        html: `<div style="
          width:28px;height:28px;
          background:rgba(129,140,248,0.2);
          border:2px solid #818CF8;
          border-radius:50%;
          display:flex;align-items:center;justify-content:center;
          font-size:12px;cursor:pointer;color:white;font-weight:700;
        " title="${ap.name}">${ap.code.slice(0, 2)}</div>`,
        iconSize: [28, 28],
        iconAnchor: [14, 14],
      });

      const marker = L.marker([ap.lat, ap.lng], { icon })
        .bindTooltip(`
          <div style="background:#0B1117;border:1px solid #818CF8;padding:8px 12px;border-radius:8px;color:#e2e8f0;font-size:12px">
            <div style="font-weight:700;color:#818CF8">${ap.code} — ${ap.city}</div>
            <div style="color:#94a3b8">${ap.name}</div>
            <div style="margin-top:4px;font-size:11px;color:#38BDF8;cursor:pointer">Click to drill down</div>
          </div>
        `, { permanent: false, opacity: 1, className: 'custom-tooltip' })
        .on('click', () => onAirportClick(ap.code))
        .addTo(mapRef.current!);

      airportRef.current.push(marker);
    });
  }, [airports, onAirportClick]);

  return (
  <div 
    ref={mapDivRef} 
    style={{ 
      position: 'absolute',
      inset: 0,
      width: '100%', 
      height: '100%',
    }} 
  />
);
}
