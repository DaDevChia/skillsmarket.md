import type { MarketSummary } from '../types';

export function MethodologyPage({ summary }: { summary: MarketSummary }) {
  return (
    <div className="page methodology-page" data-testid="methodology-page">
      <section className="page-head">
        <h1>Methodology</h1>
        <p className="muted">How every skill price and rating is built — no black-box numbers.</p>
      </section>

      <section className="panel">
        <header className="panel-head"><h2>The price formula</h2></header>
        <code>price = (weighted_demand ÷ supply_proxy) ÷ frozen_divisor</code>
        <p>
          Each skill’s raw score is its weighted job-posting demand divided by a supply proxy. That raw
          score is divided by a frozen divisor so the median skill lands on 100.
        </p>
      </section>

      <section className="panel" data-testid="methodology-terms">
        <header className="panel-head"><h2>Every term, defined</h2></header>
        <ul className="method-list">
          <li><b>Demand score</b><span>weighted</span><em>Weighted job-posting support. Key skills count 1.5×, peripheral 1×, soft skills 0.25×.</em></li>
          <li><b>Supply / applicant proxy</b><span>avg applicants</span><em>Average applicants per posting that lists the skill. An imperfect supply proxy — more applicants = looser scarcity.</em></li>
          <li><b>Salary / job-money proxy</b><span>where present</span><em>Average salary midpoint of backing postings, used only where salary is present. A job-money signal, not a guaranteed wage.</em></li>
          <li><b>Support count</b><span>rows</span><em>How many backing rows sit behind a quote. Few rows = thin support = lower confidence.</em></li>
          <li><b>Provenance</b><span>seeded / live</span><em>Seeded fixture (this demo) vs a live proxy snapshot when one is ingested. Catalogue skills are seeded index values on the same scale.</em></li>
          <li><b>Frozen divisor</b><span>{summary.divisor}</span><em>Frozen so shocked or future snapshots stay comparable to the base market — the baseline doesn’t drift.</em></li>
          <li><b>Baseline = 100</b><span>median</span><em>{summary.baseline_explainer}</em></li>
        </ul>
      </section>

      <section className="panel" data-testid="methodology-confidence">
        <header className="panel-head"><h2>Confidence &amp; limitations</h2></header>
        <ul className="limits-list">
          {summary.limits.map((limit) => (
            <li key={limit}>{limit}</li>
          ))}
          <li>Confidence per skill scales with support count and is capped for seeded data.</li>
          <li>Historical charts are seeded backtests (deterministic), not live price history.</li>
        </ul>
      </section>

      <section className="panel" data-testid="methodology-baseline">
        <header className="panel-head"><h2>Why baseline 100 matters</h2></header>
        <p>
          100 is the median skill in the snapshot. It turns absolute, hard-to-read raw scores into a
          relative read: above 100 is scarcer / higher demand-to-supply; below 100 is more common. Because
          the divisor is frozen, a 120 today and a 120 after a market shock mean the same thing.
        </p>
      </section>
    </div>
  );
}
