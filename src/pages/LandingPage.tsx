import { Link } from '../router';
import { QuoteCard } from '../components/QuoteCard';
import type { MarketSummary, Skill } from '../types';

export function LandingPage({
  summary,
  onOpenSkill,
}: {
  summary: MarketSummary;
  onOpenSkill: (skill: Skill) => void;
}) {
  const top = [...summary.skills].sort((a, b) => b.price - a.price).slice(0, 6);
  const movers = [...summary.skills]
    .sort((a, b) => Math.abs(b.change_30d) - Math.abs(a.change_30d))
    .slice(0, 6);

  return (
    <>
      <section className="hero" aria-label="SkillsMarket hero">
        <h1>The Singapore skills exchange.</h1>
        <p className="hero-sub">
          Price your resume against {summary.skills.length} skills. See what’s scarce, what’s common, and
          the single best move next — read like a trading terminal, not a black box.
        </p>
        <div className="hero-cta">
          <Link to="/resume" className="cta-button" data-testid="cta-analyze-resume">
            Analyse my resume →
          </Link>
          <Link to="/skills" className="ghost-button" data-testid="cta-browse-skills">
            Browse the skill board
          </Link>
        </div>
      </section>

      <section className="landing-section">
        <header className="section-head">
          <h2>Top quotes</h2>
          <Link to="/skills" className="muted section-link">full board →</Link>
        </header>
        <div className="quote-grid" data-testid="top-quotes">
          {top.map((skill) => (
            <QuoteCard key={skill.id} skill={skill} onOpen={onOpenSkill} />
          ))}
        </div>
      </section>

      <section className="landing-section">
        <header className="section-head"><h2>Biggest 30-day movers</h2></header>
        <div className="quote-grid">
          {movers.map((skill) => (
            <QuoteCard key={skill.id} skill={skill} onOpen={onOpenSkill} />
          ))}
        </div>
      </section>

      <section className="landing-section">
        <header className="section-head"><h2>Sector indices</h2></header>
        <div className="sector-grid" data-testid="sector-indices">
          {summary.sectors.map((sec) => (
            <div key={sec.name} className="sector-cell">
              <b>{sec.name}</b>
              <span>{sec.index.toFixed(1)}</span>
              <em className={sec.change >= 0 ? 'positive' : 'negative'}>
                {sec.change >= 0 ? '+' : ''}
                {sec.change.toFixed(1)}
              </em>
            </div>
          ))}
        </div>
      </section>

      <section className="landing-section explore-row">
        <Link to="/methodology" className="explore-card" data-testid="explore-methodology">
          <b>Methodology →</b>
          <span>How prices and ratings are built. No black-box numbers.</span>
        </Link>
        <Link to="/sources" className="explore-card" data-testid="explore-sources">
          <b>Sources &amp; pipeline →</b>
          <span>MyCareersFuture, Apify, SkillsFuture — and what we don’t ingest.</span>
        </Link>
      </section>
    </>
  );
}
