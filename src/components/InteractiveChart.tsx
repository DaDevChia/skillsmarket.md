import React from 'react';
import type { HistoryPoint } from '../types';

const W = 760;
const H = 300;
const PAD_L = 46;
const PAD_R = 14;
const PAD_T = 14;
const PAD_B = 30;
const PLOT_W = W - PAD_L - PAD_R;
const PLOT_H = H - PAD_T - PAD_B;

const clamp = (value: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, value));

type Pt = { x: number; y: number };

// Catmull-Rom -> cubic Bézier so the (already smooth) daily series renders as a
// continuous premium curve instead of straight segments between points.
function smoothPath(pts: Pt[]): string {
  if (pts.length < 2) return pts.length ? `M ${pts[0].x} ${pts[0].y}` : '';
  let d = `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)}`;
  const t = 0.5 / 3;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] || pts[i];
    const p1 = pts[i];
    const p2 = pts[i + 1];
    const p3 = pts[i + 2] || p2;
    const c1x = p1.x + (p2.x - p0.x) * t;
    const c1y = p1.y + (p2.y - p0.y) * t;
    const c2x = p2.x - (p3.x - p1.x) * t;
    const c2y = p2.y - (p3.y - p1.y) * t;
    d += ` C ${c1x.toFixed(1)} ${c1y.toFixed(1)} ${c2x.toFixed(1)} ${c2y.toFixed(1)} ${p2.x.toFixed(1)} ${p2.y.toFixed(1)}`;
  }
  return d;
}

// A Bloomberg-style interactive price chart: scroll/drag to pan, wheel or +/- to
// zoom, range buttons (30/90/All), Y price axis + X day axis, and a hover/touch
// crosshair with a value tooltip.
export function InteractiveChart({ history, baseline }: { history: HistoryPoint[]; baseline: number }) {
  const n = history.length;
  const [view, setView] = React.useState({ start: 0, end: Math.max(0, n - 1) });
  const [hover, setHover] = React.useState<number | null>(null);
  const svgRef = React.useRef<SVGSVGElement | null>(null);
  const drag = React.useRef<{ x: number; start: number; end: number } | null>(null);

  React.useEffect(() => {
    setView({ start: 0, end: Math.max(0, n - 1) });
  }, [n]);

  if (n < 2) return <div className="history-chart-empty muted">No history available.</div>;

  const vStart = clamp(Math.round(view.start), 0, n - 2);
  const vEnd = clamp(Math.round(view.end), vStart + 1, n - 1);
  const slice = history.slice(vStart, vEnd + 1);
  const prices = slice.map((p) => p.price);
  const min = Math.min(...prices, baseline);
  const max = Math.max(...prices, baseline);
  const range = max - min || 1;

  const xAt = (i: number) => PAD_L + (i / (slice.length - 1)) * PLOT_W;
  const yAt = (v: number) => PAD_T + PLOT_H - ((v - min) / range) * PLOT_H;
  const pts: Pt[] = slice.map((p, i) => ({ x: xAt(i), y: yAt(p.price) }));
  const linePath = smoothPath(pts);
  const bottom = (PAD_T + PLOT_H).toFixed(1);
  const area = `${linePath} L ${pts[pts.length - 1].x.toFixed(1)} ${bottom} L ${pts[0].x.toFixed(1)} ${bottom} Z`;
  const up = prices[prices.length - 1] >= prices[0];
  const last = pts[pts.length - 1];

  function setRange(days: number) {
    if (days >= n) setView({ start: 0, end: n - 1 });
    else setView({ start: n - 1 - days, end: n - 1 });
  }
  function zoom(factor: number) {
    const size = vEnd - vStart;
    const center = (vStart + vEnd) / 2;
    const half = clamp((size * factor) / 2, 3, n / 2);
    setView({ start: clamp(center - half, 0, n - 2), end: clamp(center + half, 1, n - 1) });
  }

  function pointIndexFromClientX(clientX: number): number {
    const rect = svgRef.current!.getBoundingClientRect();
    const svgX = ((clientX - rect.left) / rect.width) * W;
    const frac = clamp((svgX - PAD_L) / PLOT_W, 0, 1);
    return Math.round(frac * (slice.length - 1));
  }

  function onPointerDown(event: React.PointerEvent<SVGSVGElement>) {
    (event.target as Element).setPointerCapture?.(event.pointerId);
    drag.current = { x: event.clientX, start: vStart, end: vEnd };
  }
  function onPointerMove(event: React.PointerEvent<SVGSVGElement>) {
    setHover(pointIndexFromClientX(event.clientX));
    if (!drag.current) return;
    const rect = svgRef.current!.getBoundingClientRect();
    const dxFrac = ((event.clientX - drag.current.x) / rect.width) * (slice.length - 1);
    const shift = Math.round(-dxFrac);
    const size = drag.current.end - drag.current.start;
    let start = clamp(drag.current.start + shift, 0, n - 1 - size);
    setView({ start, end: start + size });
  }
  function onPointerUp() {
    drag.current = null;
  }
  function onWheel(event: React.WheelEvent<SVGSVGElement>) {
    event.preventDefault();
    zoom(event.deltaY > 0 ? 1.2 : 0.83);
  }

  const baseY = yAt(baseline);
  const hoverPoint = hover != null && hover >= 0 && hover < slice.length ? slice[hover] : null;
  // Y ticks
  const yTicks = [min, min + range / 2, max].map((v) => ({ v, y: yAt(v) }));
  // X ticks (~4)
  const xTickCount = Math.min(4, slice.length);
  const xTicks = Array.from({ length: xTickCount }, (_, k) => {
    const i = Math.round((k / (xTickCount - 1)) * (slice.length - 1));
    return { i, day: slice[i].day, x: xAt(i) };
  });

  return (
    <div className="interactive-chart" data-testid="interactive-chart">
      <div className="chart-controls">
        <div className="chart-ranges">
          <button type="button" data-testid="chart-range-30" onClick={() => setRange(30)}>30D</button>
          <button type="button" data-testid="chart-range-90" onClick={() => setRange(90)}>90D</button>
          <button type="button" data-testid="chart-range-all" onClick={() => setRange(n)}>ALL</button>
        </div>
        <div className="chart-zoom">
          <button type="button" aria-label="Zoom in" data-testid="chart-zoom-in" onClick={() => zoom(0.7)}>＋</button>
          <button type="button" aria-label="Zoom out" data-testid="chart-zoom-out" onClick={() => zoom(1.4)}>－</button>
        </div>
      </div>
      <svg
        ref={svgRef}
        className="history-chart"
        data-testid="history-chart"
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label="Interactive seeded historical price series"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerLeave={() => { onPointerUp(); setHover(null); }}
        onWheel={onWheel}
      >
        <defs>
          <linearGradient id="cfUp" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgba(0,255,156,0.28)" />
            <stop offset="100%" stopColor="rgba(0,255,156,0)" />
          </linearGradient>
          <linearGradient id="cfDown" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgba(255,92,122,0.26)" />
            <stop offset="100%" stopColor="rgba(255,92,122,0)" />
          </linearGradient>
        </defs>
        {yTicks.map((tick) => (
          <g key={`y${tick.v.toFixed(1)}`}>
            <line x1={PAD_L} x2={W - PAD_R} y1={tick.y} y2={tick.y} className="chart-grid" />
            <text x={PAD_L - 6} y={tick.y + 3} className="chart-axis-label" textAnchor="end">{tick.v.toFixed(0)}</text>
          </g>
        ))}
        {xTicks.map((tick) => (
          <text key={`x${tick.i}`} x={tick.x} y={H - 10} className="chart-axis-label" textAnchor="middle">
            {tick.day === 0 ? 'now' : `${Math.abs(tick.day)}d`}
          </text>
        ))}
        <line x1={PAD_L} x2={W - PAD_R} y1={baseY} y2={baseY} className="chart-baseline" />
        <text x={W - PAD_R} y={baseY - 4} className="chart-baseline-label" textAnchor="end">baseline {baseline.toFixed(0)}</text>
        <path d={area} className={`chart-area ${up ? 'up' : 'down'}`} fill={up ? 'url(#cfUp)' : 'url(#cfDown)'} stroke="none" />
        <path d={linePath} className={`chart-line ${up ? 'up' : 'down'}`} fill="none" />
        {/* Today's price marker — the anchor point of the modelled path. */}
        <circle cx={last.x} cy={last.y} r="6" className={`chart-now-halo ${up ? 'up' : 'down'}`} />
        <circle cx={last.x} cy={last.y} r="3" className={`chart-now-dot ${up ? 'up' : 'down'}`} />
        {hoverPoint && (
          <g>
            <line x1={xAt(hover!)} x2={xAt(hover!)} y1={PAD_T} y2={PAD_T + PLOT_H} className="chart-crosshair" />
            <circle cx={xAt(hover!)} cy={yAt(hoverPoint.price)} r="4" className={`chart-dot ${up ? 'up' : 'down'}`} />
            {(() => {
              const cx = xAt(hover!);
              const labelW = 92;
              const lx = clamp(cx - labelW / 2, PAD_L, W - PAD_R - labelW);
              return (
                <g className="chart-tip" pointerEvents="none">
                  <rect x={lx} y={PAD_T + 2} width={labelW} height={30} rx="5" className="chart-tip-box" />
                  <text x={lx + labelW / 2} y={PAD_T + 14} textAnchor="middle" className="chart-tip-price">
                    {hoverPoint.price.toFixed(1)} pts
                  </text>
                  <text x={lx + labelW / 2} y={PAD_T + 26} textAnchor="middle" className="chart-tip-day">
                    {hoverPoint.day === 0 ? 'today' : `${Math.abs(hoverPoint.day)}d ago`}
                  </text>
                </g>
              );
            })()}
          </g>
        )}
      </svg>
      <div className="chart-readout" data-testid="chart-readout">
        {hoverPoint ? (
          <span>{hoverPoint.day === 0 ? 'today' : `${Math.abs(hoverPoint.day)}d ago`}: <b>{hoverPoint.price.toFixed(1)} pts</b></span>
        ) : (
          <span className="muted">Modelled valuation path, seeded from today's price · drag to pan · wheel or ＋/－ to zoom · hover for value</span>
        )}
      </div>
    </div>
  );
}
