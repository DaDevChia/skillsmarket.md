import type { HistoryPoint } from '../types';

export function HistoryChart({ history, baseline }: { history: HistoryPoint[]; baseline: number }) {
  const w = 640;
  const h = 220;
  const pad = 30;
  if (!history || history.length < 2) {
    return <div className="history-chart-empty muted">No history available.</div>;
  }
  const prices = history.map((point) => point.price);
  const min = Math.min(...prices, baseline);
  const max = Math.max(...prices, baseline);
  const range = max - min || 1;
  const x = (index: number) => pad + (index / (history.length - 1)) * (w - 2 * pad);
  const y = (value: number) => h - pad - ((value - min) / range) * (h - 2 * pad);

  const line = history.map((point, index) => `${x(index).toFixed(1)},${y(point.price).toFixed(1)}`).join(' ');
  const area = `${pad.toFixed(1)},${(h - pad).toFixed(1)} ${line} ${(w - pad).toFixed(1)},${(h - pad).toFixed(1)}`;
  const up = prices[prices.length - 1] >= prices[0];
  const baseY = y(baseline);

  return (
    <svg
      className="history-chart"
      data-testid="history-chart"
      viewBox={`0 0 ${w} ${h}`}
      preserveAspectRatio="none"
      role="img"
      aria-label="Seeded historical price series"
    >
      <line x1={pad} x2={w - pad} y1={baseY} y2={baseY} className="chart-baseline" />
      <text x={w - pad} y={baseY - 4} className="chart-baseline-label" textAnchor="end">
        baseline {baseline.toFixed(0)}
      </text>
      <polyline points={area} className={`chart-area ${up ? 'up' : 'down'}`} />
      <polyline points={line} className={`chart-line ${up ? 'up' : 'down'}`} fill="none" />
    </svg>
  );
}
