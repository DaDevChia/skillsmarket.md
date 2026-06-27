import React from 'react';
import type { ResumeHighlight } from '../types';

const CATEGORY_LABEL: Record<string, string> = {
  skill: 'Skill',
  weak: 'Common skill',
  role: 'Role / title',
  education: 'Education / cert',
  achievement: 'Achievement',
};

const LEGEND = ['skill', 'weak', 'role', 'education', 'achievement'];

export function DocumentViewer({
  text,
  highlights,
  selected,
  onSelect,
}: {
  text: string;
  highlights: ResumeHighlight[];
  selected: ResumeHighlight | null;
  onSelect: (highlight: ResumeHighlight | null) => void;
}) {
  const sorted = [...highlights].sort((a, b) => a.start - b.start);
  const segments: React.ReactNode[] = [];
  let cursor = 0;
  sorted.forEach((highlight, index) => {
    if (highlight.start > cursor) {
      segments.push(<span key={`p${index}`}>{text.slice(cursor, highlight.start)}</span>);
    }
    const isActive =
      selected !== null && selected.start === highlight.start && selected.end === highlight.end;
    segments.push(
      <mark
        key={`h${index}`}
        className={`hl hl-${highlight.category}${isActive ? ' active' : ''}`}
        data-testid="resume-highlight"
        data-category={highlight.category}
        tabIndex={0}
        role="button"
        onClick={() => onSelect(highlight)}
        onKeyDown={(event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            onSelect(highlight);
          }
        }}
      >
        {highlight.text}
      </mark>,
    );
    cursor = highlight.end;
  });
  if (cursor < text.length) segments.push(<span key="pend">{text.slice(cursor)}</span>);

  return (
    <section className="panel document-viewer" data-testid="document-viewer">
      <header className="panel-head">
        <h2>Document evidence</h2>
        <span className="panel-tag">{highlights.length} highlights · click to inspect</span>
      </header>
      <div className="doc-legend">
        {LEGEND.map((category) => (
          <span key={category} className="legend-chip">
            <i className={`hl-swatch hl-${category}`} /> {CATEGORY_LABEL[category]}
          </span>
        ))}
      </div>
      <pre className="doc-body" data-testid="document-body">
        {segments}
      </pre>
      {selected && (
        <div className="highlight-detail" data-testid="highlight-detail" role="status">
          <div className="hl-detail-top">
            <span className={`hl-chip hl-${selected.category}`}>{CATEGORY_LABEL[selected.category]}</span>
            <span className="muted">confidence {(selected.confidence * 100).toFixed(0)}%</span>
            <button type="button" className="hl-close" aria-label="Close" onClick={() => onSelect(null)}>
              ×
            </button>
          </div>
          {selected.skill && <p className="hl-detail-skill">{selected.skill}</p>}
          <p>{selected.detail}</p>
          {selected.affects && <p className="muted">Feeds recommendation: Learn {selected.affects}</p>}
        </div>
      )}
    </section>
  );
}
