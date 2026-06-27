import { SourcesPanel } from '../components/SourcesPanel';
import type { MarketSummary } from '../types';

export function SourcesPage({ summary }: { summary: MarketSummary }) {
  return (
    <div className="page sources-page" data-testid="sources-page">
      <section className="page-head">
        <h1>Sources &amp; data pipeline</h1>
        <p className="muted">
          Exactly what feeds the numbers — and what doesn’t. MyCareersFuture is the underlying source;
          Apify is the ingestion crawler; SkillsFuture is for course recommendations; LinkedIn is not ingested.
        </p>
      </section>
      <SourcesPanel summary={summary} />
    </div>
  );
}
