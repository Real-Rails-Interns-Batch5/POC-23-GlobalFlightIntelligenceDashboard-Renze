'use client';

interface Filter {
  country: string;
  minSpeed: number;
  minAlt: number;
}

interface Props {
  filter: Filter;
  onChange: (f: Filter) => void;
}

export default function FilterBar({ filter, onChange }: Props) {
  return (
    <div className="glass" style={{ padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
      

      {/* Country filter */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <label style={{ fontSize: 12, color: '#64748b' }}>Country</label>
        <input
          type="text"
          placeholder="e.g. India"
          value={filter.country}
          onChange={e => onChange({ ...filter, country: e.target.value })}
          style={{
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: 6,
            padding: '5px 10px',
            color: '#e2e8f0',
            fontSize: 12,
            width: 120,
            outline: 'none',
          }}
        />
      </div>

      {/* Min speed filter */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <label style={{ fontSize: 12, color: '#64748b' }}>Min Speed (kts)</label>
        <input
          type="number"
          placeholder="0"
          value={filter.minSpeed || ''}
          onChange={e => onChange({ ...filter, minSpeed: Number(e.target.value) })}
          style={{
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: 6,
            padding: '5px 10px',
            color: '#e2e8f0',
            fontSize: 12,
            width: 100,
            outline: 'none',
          }}
        />
      </div>

      {/* Min altitude filter */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <label style={{ fontSize: 12, color: '#64748b' }}>Min Altitude (m)</label>
        <input
          type="number"
          placeholder="0"
          value={filter.minAlt || ''}
          onChange={e => onChange({ ...filter, minAlt: Number(e.target.value) })}
          style={{
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: 6,
            padding: '5px 10px',
            color: '#e2e8f0',
            fontSize: 12,
            width: 100,
            outline: 'none',
          }}
        />
      </div>

      {/* Clear button */}
      <button
        onClick={() => onChange({ country: '', minSpeed: 0, minAlt: 0 })}
        style={{
          background: 'rgba(239,68,68,0.1)',
          border: '1px solid rgba(239,68,68,0.2)',
          color: '#f87171',
          padding: '5px 12px',
          borderRadius: 6,
          fontSize: 12,
          cursor: 'pointer',
        }}
      >
        ✕ Clear
      </button>

      {/* Tooltip explaining filters */}
      <div style={{ marginLeft: 'auto', fontSize: 11, color: '#475569', fontStyle: 'italic' }}>
        Filters apply instantly to the map and all panels
      </div>
    </div>
  );
}