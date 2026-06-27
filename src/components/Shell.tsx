import React from 'react';
import { Link } from '../router';
import { TopNav } from './TopNav';

export function Shell({ children, mode }: { children: React.ReactNode; mode?: string }) {
  const live = mode === 'real_proxy';
  return (
    <div className="terminal">
      <header className="topbar">
        <Link to="/" className="brand" aria-label="SkillsMarket home">
          <span className="brand-mark">◧</span> SKILLSMARKET
          <span className="brand-sub">SG SKILLS EXCHANGE</span>
        </Link>
        <span className={`status-pill ${live ? 'live' : 'seeded'}`} data-testid="data-mode">
          ● {live ? 'LIVE PROXY' : 'SEEDED SNAPSHOT'}
        </span>
      </header>
      <TopNav />
      {children}
    </div>
  );
}

export function ErrorState({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <section className="error-state" data-testid="api-error-state">
      <h2>Market feed unavailable</h2>
      <p>The SkillsMarket feed could not be reached ({error}). The board is paused rather than showing unverified numbers.</p>
      <button type="button" className="primary" onClick={onRetry}>
        Retry
      </button>
    </section>
  );
}
