export function ShockSimulator({
  divisor,
  baseline,
  shocked,
  message,
  onShock,
  onReset,
}: {
  divisor: number;
  baseline: number;
  shocked: boolean;
  message: string | null;
  onShock: () => void;
  onReset: () => void;
}) {
  return (
    <section className="panel shock-panel" data-testid="shock-panel">
      <header className="panel-head">
        <h2>Market event</h2>
        <span className="panel-tag">National baseline: {baseline.toFixed(0)}</span>
      </header>
      <p className="muted">
        Model a structural shift, not a doom score: admin demand dips, AI / data / automation demand rises.
        The frozen divisor ({divisor.toFixed(4)}) holds, so the baseline stays at {baseline.toFixed(0)} and
        every quote stays comparable.
      </p>
      <div className="shock-actions">
        <button type="button" className="ghost-button" data-testid="shock-button" onClick={onShock}>
          GenAI breakthrough
        </button>
        <button type="button" className="ghost-button" data-testid="reset-button" disabled={!shocked} onClick={onReset}>
          Reset market
        </button>
      </div>
      {message && (
        <div className="shock-banner" role="status" data-testid="shock-banner">
          {message}
        </div>
      )}
    </section>
  );
}
