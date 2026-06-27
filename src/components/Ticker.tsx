import React from 'react';
import type { Sector, Skill } from '../types';

// Market atmosphere: a scrolling tape of skill/sector quotes. Pauses on hover so
// a user can actually read a quote (Task 13 interaction polish).
export function Ticker({
  skills,
  sectors,
  onSelect,
}: {
  skills: Skill[];
  sectors: Sector[];
  onSelect: (skill: string) => void;
}) {
  const [paused, setPaused] = React.useState(false);
  const items = [
    ...skills.slice(0, 10).map((s) => ({ label: s.symbol, name: s.name, value: s.price, change: s.change, type: 'skill' as const })),
    ...sectors.map((s) => ({ label: s.symbol, name: s.name, value: s.index, change: s.change, type: 'sector' as const })),
  ];

  return (
    <section
      className="ticker"
      aria-label="Market ticker"
      data-testid="big-board"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      <div className={`ticker-track${paused ? ' paused' : ''}`}>
        {[...items, ...items].map((item, index) => (
          <button
            key={`${item.label}-${index}`}
            type="button"
            className="ticker-item"
            onClick={() => item.type === 'skill' && onSelect(item.name)}
          >
            <b>{item.label}</b> {item.value.toFixed(1)}{' '}
            <span className={item.change >= 0 ? 'positive' : 'negative'}>
              {item.change >= 0 ? '▲' : '▼'} {Math.abs(item.change).toFixed(1)}
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}
