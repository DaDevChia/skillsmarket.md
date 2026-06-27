import { DataPipeline } from './DataPipeline';
import type { MarketSummary } from '../types';

function kindClass(kind: string): string {
  if (kind === 'underlying_source') return 'src-source';
  if (kind === 'ingestion_infrastructure') return 'src-infra';
  if (kind === 'course_source') return 'src-course';
  if (kind === 'reference_only' || kind === 'planned') return 'src-muted';
  return 'src-muted';
}

export function SourcesPanel({ summary }: { summary: MarketSummary }) {
  const mode = summary.data_mode === 'real_proxy' ? 'LIVE PROXY' : 'SEEDED FIXTURE';
  const stamp = summary.snapshot?.created_at?.slice(0, 19).replace('T', ' ') ?? 'n/a';

  return (
    <section className="panel sources-panel" data-testid="sources-panel">
      <header className="panel-head">
        <h2>Sources &amp; data pipeline</h2>
        <span className={`mode-badge ${summary.data_mode === 'real_proxy' ? 'live' : 'seeded'}`} data-testid="data-mode-badge">
          {mode}
        </span>
      </header>

      <p className="baseline-explainer" data-testid="baseline-explainer">
        {summary.baseline_explainer}
      </p>
      <p className="muted snapshot-line">
        Snapshot: <code>{summary.snapshot?.snapshot_id ?? 'fixture'}</code> · {summary.snapshot?.kind ?? 'fixture'} · {stamp}
      </p>

      <h3 className="sources-subhead">Live ingestion status</h3>
      <div className="ingestion-status" data-testid="ingestion-status">
        <div className="ingest-cell">
          <b>MyCareersFuture</b>
          {summary.ingestion?.mycareersfuture ? (
            <span>
              {summary.ingestion.mycareersfuture.jobs.toLocaleString()} real jobs ·{' '}
              {summary.ingestion.mycareersfuture.skills.toLocaleString()} skills ·{' '}
              {summary.ingestion.mycareersfuture.fetched_at?.slice(0, 10)}
            </span>
          ) : (
            <span className="muted">not swept (seeded fixture in use)</span>
          )}
        </div>
        <div className="ingest-cell">
          <b>SkillsFuture courses</b>
          {summary.ingestion?.skillsfuture ? (
            <span>
              {summary.ingestion.skillsfuture.courses.toLocaleString()} real courses ·{' '}
              {summary.ingestion.skillsfuture.matched_skills} skills matched ·{' '}
              {summary.ingestion.skillsfuture.fetched_at?.slice(0, 10)}
            </span>
          ) : (
            <span className="muted">not ingested</span>
          )}
        </div>
      </div>

      <h3 className="sources-subhead">How the pipeline flows</h3>
      <DataPipeline stages={summary.pipeline} />

      <h3 className="sources-subhead">What each source is</h3>
      <ul className="sources-list">
        {summary.data_sources.map((source) => (
          <li key={source.name} className={`source-row ${kindClass(source.kind)}`}>
            <div className="source-top">
              <b>{source.name}</b>
              <span className="source-label">{source.label}</span>
            </div>
            <p className="source-use">{source.use}</p>
          </li>
        ))}
      </ul>

      <h3 className="sources-subhead">Limits</h3>
      <ul className="limits-list" data-testid="data-limits">
        {summary.limits.map((limit) => (
          <li key={limit}>{limit}</li>
        ))}
      </ul>

      <h3 className="sources-subhead">Provenance</h3>
      <div className="provenance" data-testid="provenance-panel">
        {summary.provenance.map((row) => (
          <div key={row.signal} className="metric-row">
            <span>{row.signal}</span>
            <b data-testid={`provenance-status-${row.signal.toLowerCase().replace(/\s+/g, '-')}`}>{row.status}</b>
            <em>{row.source}</em>
          </div>
        ))}
      </div>
    </section>
  );
}
