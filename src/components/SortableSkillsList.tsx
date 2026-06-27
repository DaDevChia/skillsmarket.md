import React from 'react';
import { Sparkline } from './Sparkline';
import { SourceBadges } from './SourceBadge';
import type { Skill } from '../types';

type SortKey = 'symbol' | 'name' | 'price' | 'change' | 'change_30d' | 'sector';

const COLUMNS: { key: SortKey; label: string; numeric?: boolean }[] = [
  { key: 'symbol', label: 'Sym' },
  { key: 'name', label: 'Skill' },
  { key: 'price', label: 'Price', numeric: true },
  { key: 'change', label: 'Chg', numeric: true },
  { key: 'change_30d', label: '30d', numeric: true },
  { key: 'sector', label: 'Sector' },
];

// Full, sortable, searchable, sector-filterable board. Sparkline + source badge
// per row. Rows open the individual skill stock-analysis page.
export function SortableSkillsList({
  skills,
  onSelect,
}: {
  skills: Skill[];
  onSelect: (skill: Skill) => void;
}) {
  const [sortKey, setSortKey] = React.useState<SortKey>('price');
  const [dir, setDir] = React.useState<'asc' | 'desc'>('desc');
  const [query, setQuery] = React.useState('');
  const [sector, setSector] = React.useState('all');

  const sectors = React.useMemo(
    () => ['all', ...Array.from(new Set(skills.map((s) => s.sector))).sort()],
    [skills],
  );

  function toggle(key: SortKey) {
    if (key === sortKey) setDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    else {
      setSortKey(key);
      setDir(key === 'price' || key === 'change' || key === 'change_30d' ? 'desc' : 'asc');
    }
  }

  const needle = query.trim().toLowerCase();
  const filtered = skills.filter((skill) => {
    if (sector !== 'all' && skill.sector !== sector) return false;
    if (!needle) return true;
    return (
      skill.name.toLowerCase().includes(needle) ||
      skill.symbol.toLowerCase().includes(needle) ||
      skill.sector.toLowerCase().includes(needle)
    );
  });
  const sorted = [...filtered].sort((a, b) => {
    const av = a[sortKey];
    const bv = b[sortKey];
    const cmp = typeof av === 'number' && typeof bv === 'number' ? av - bv : String(av).localeCompare(String(bv));
    return dir === 'asc' ? cmp : -cmp;
  });

  return (
    <section className="panel skills-list-panel" data-testid="skills-list">
      <header className="panel-head">
        <h2>Skill market board</h2>
        <span className="panel-tag">{skills.length} skills · seeded snapshot</span>
      </header>

      <div className="list-controls">
        <input
          type="search"
          className="skills-search"
          data-testid="skills-search"
          placeholder="Search skill, symbol, or sector…"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          aria-label="Search skills"
        />
        <select
          className="sector-filter"
          data-testid="sector-filter"
          value={sector}
          onChange={(event) => setSector(event.target.value)}
          aria-label="Filter by sector"
        >
          {sectors.map((option) => (
            <option key={option} value={option}>
              {option === 'all' ? 'All sectors' : option}
            </option>
          ))}
        </select>
      </div>
      <p className="skills-count muted" data-testid="skills-count">
        Showing {sorted.length} of {skills.length}
      </p>

      <div className="skills-table">
        <div className="skills-thead">
          {COLUMNS.map((col) => (
            <button
              key={col.key}
              type="button"
              className={`th${col.numeric ? ' num' : ''}`}
              data-testid={`sort-${col.key}`}
              aria-sort={sortKey === col.key ? (dir === 'asc' ? 'ascending' : 'descending') : 'none'}
              onClick={() => toggle(col.key)}
            >
              {col.label}
              {sortKey === col.key ? (dir === 'asc' ? ' ▲' : ' ▼') : ''}
            </button>
          ))}
          <span className="th">Trend</span>
          <span className="th">Source</span>
        </div>
        {sorted.map((skill) => (
          <button
            key={skill.name}
            type="button"
            className="skills-trow"
            data-testid={`skill-list-row-${skill.id}`}
            onClick={() => onSelect(skill)}
          >
            <span className="td sym" data-label="Sym">{skill.symbol}</span>
            <span className="td name" data-label="Skill">{skill.name}</span>
            <span className="td num price" data-label="Price" data-testid={`price-${skill.id}`}>
              {skill.price.toFixed(1)}
            </span>
            <span className={`td num ${skill.change >= 0 ? 'positive' : 'negative'}`} data-label="Change">
              {skill.change >= 0 ? '+' : ''}
              {skill.change.toFixed(1)}
            </span>
            <span className={`td num ${skill.change_30d >= 0 ? 'positive' : 'negative'}`} data-label="30d">
              {skill.change_30d >= 0 ? '+' : ''}
              {skill.change_30d.toFixed(1)}%
            </span>
            <span className="td sector" data-label="Sector">{skill.sector}</span>
            <span className="td spark" data-label="Trend"><Sparkline data={skill.spark} /></span>
            <span className="td src" data-label="Source"><SourceBadges badges={skill.source_badges} /></span>
          </button>
        ))}
      </div>
    </section>
  );
}
