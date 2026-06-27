import React from 'react';
import { getSkillDetail } from '../api';
import { Link } from '../router';
import { InteractiveChart } from '../components/InteractiveChart';
import { SourceBadges } from '../components/SourceBadge';
import { ConfidenceChip } from '../components/ConfidenceChip';
import type { SkillDetail } from '../types';

function money(value: number | null | undefined) {
  return value == null ? '—' : `$${Number(value).toLocaleString()}`;
}

export function SkillDetailPage({ skillId }: { skillId: string }) {
  const [detail, setDetail] = React.useState<SkillDetail | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let live = true;
    setDetail(null);
    setError(null);
    getSkillDetail(skillId)
      .then((data) => live && setDetail(data))
      .catch((err) => live && setError(err instanceof Error ? err.message : 'Not found'));
    return () => {
      live = false;
    };
  }, [skillId]);

  if (error) {
    return (
      <div className="page" data-testid="skill-detail-page">
        <Link to="/skills" className="back-link" data-testid="back-to-board">← Skill board</Link>
        <p className="intake-error">That skill isn’t on the board.</p>
      </div>
    );
  }
  if (!detail) {
    return (
      <div className="page" data-testid="skill-detail-page">
        <div className="loading">Loading quote…</div>
      </div>
    );
  }

  const s = detail.skill;
  const m = detail.methodology;
  const st = detail.stats;
  const up = s.change >= 0;

  return (
    <div className="page skill-detail-page" data-testid="skill-detail-page">
      <nav className="page-nav">
        <Link to="/skills" className="back-link" data-testid="back-to-board">← Skill board</Link>
        <span className="page-title">Stock analysis</span>
      </nav>

      <section className="panel quote-header">
        <div className="quote-id">
          <span className="big-sym">{s.symbol}</span>
          <div>
            <h1>{s.name}</h1>
            <span className="muted">{s.sector}</span>
          </div>
        </div>
        <div className="quote-figures">
          <div className="big-price" data-testid="detail-price">{s.price.toFixed(1)} <small>pts</small></div>
          <div className={`detail-change ${up ? 'positive' : 'negative'}`}>
            {up ? '▲' : '▼'} {Math.abs(s.change).toFixed(1)} today · {st.change_30d >= 0 ? '+' : ''}{st.change_30d}% 30d · {st.change_90d >= 0 ? '+' : ''}{st.change_90d}% 90d
          </div>
          <div className="quote-chips">
            <SourceBadges badges={detail.source_badges} />
            <ConfidenceChip level={detail.confidence.level} score={detail.confidence.score} />
          </div>
        </div>
      </section>

      <section className="panel" data-testid="history-section">
        <header className="panel-head">
          <h2>Historical valuation</h2>
          <span className="panel-tag" data-testid="history-label">{detail.history_label}</span>
        </header>
        <InteractiveChart history={detail.history} baseline={m.baseline} />
        <div className="hist-stats">
          <span>90d high <b>{st.high}</b></span>
          <span>90d low <b>{st.low}</b></span>
          <span>30d <b className={st.change_30d >= 0 ? 'positive' : 'negative'}>{st.change_30d >= 0 ? '+' : ''}{st.change_30d}%</b></span>
          <span>90d <b className={st.change_90d >= 0 ? 'positive' : 'negative'}>{st.change_90d >= 0 ? '+' : ''}{st.change_90d}%</b></span>
          <span>trend <b>{st.trend}</b></span>
        </div>
      </section>

      <section className="panel analyst-note" data-testid="analyst-note">
        <header className="panel-head"><h2>Analyst note</h2></header>
        <p>{detail.analyst_note}</p>
      </section>

      <section className="panel" data-testid="live-evidence">
        <header className="panel-head">
          <h2>Live market evidence</h2>
          {detail.live_evidence.found ? (
            <span className="source-badge badge-mcf">MyCareersFuture · {detail.live_evidence.fetched_at?.slice(0, 10)}</span>
          ) : (
            <span className="panel-tag">not in latest live sweep</span>
          )}
        </header>
        {detail.live_evidence.found ? (
          <>
            <p className="evidence-stats">
              <b>{detail.live_evidence.demand}</b> real job posts ·
              salary <b>{money(detail.live_evidence.salary_min)}–{money(detail.live_evidence.salary_max)}</b> ·
              top sector <b>{detail.live_evidence.top_sector}</b>
            </p>
            <ul className="job-list">
              {(detail.live_evidence.sample_jobs ?? []).map((job) => (
                <li key={job.uuid}>
                  <a href={job.url} target="_blank" rel="noreferrer" data-testid="live-job-link">{job.title} ↗</a>
                  <span className="muted"> · {money(job.salary_min)}–{money(job.salary_max)} · {job.sector}</span>
                </li>
              ))}
            </ul>
          </>
        ) : (
          <p className="muted">No real MyCareersFuture postings matched this exact skill in the latest sweep. The seeded index still applies.</p>
        )}
      </section>

      <section className="panel" data-testid="skill-courses">
        <header className="panel-head">
          <h2>SkillsFuture courses</h2>
          {detail.courses.found ? (
            <span className="source-badge badge-catalogue">MySkillsFuture · {detail.courses.fetched_at?.slice(0, 10)}</span>
          ) : (
            <span className="panel-tag">no direct course match</span>
          )}
        </header>
        {detail.courses.found ? (
          <ul className="course-detail-list">
            {detail.courses.matches.map((course) => (
              <li key={course.ref}>
                <a href={course.url ?? '#'} target="_blank" rel="noreferrer" data-testid="course-detail-link">{course.title} ↗</a>
                <span className="muted"> · {course.provider} · ${course.fee} · {course.hours}h</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted">No exact title match in the MySkillsFuture directory for this skill.</p>
        )}
      </section>

      <section className="panel" data-testid="methodology-breakdown">
        <header className="panel-head">
          <h2>How this rating is built</h2>
          <span className="panel-tag">no black-box numbers</span>
        </header>
        <ul className="method-list">
          <li><b>Demand score</b><span>{m.weighted_demand}</span><em>{m.demand_explainer}</em></li>
          <li><b>Supply / applicant proxy</b><span>{m.supply_proxy}</span><em>{m.supply_explainer}</em></li>
          <li><b>Salary / job-money proxy</b><span>{m.salary_mid == null ? 'not present' : m.salary_mid}</span><em>{m.salary_explainer}</em></li>
          <li><b>Support count</b><span>{m.support}</span><em>Number of backing rows behind the quote.</em></li>
          <li><b>Frozen divisor</b><span>{m.divisor}</span><em>{m.divisor_explainer}</em></li>
          <li><b>Baseline</b><span>{m.baseline}</span><em>{m.baseline_explainer}</em></li>
          <li><b>Provenance</b><span>{m.provenance}</span><em>Seeded fixture vs live proxy snapshot.</em></li>
        </ul>
        <code>price = {m.formula}</code>
      </section>

      <section className="panel" data-testid="confidence-section">
        <header className="panel-head">
          <h2>Confidence &amp; limitations</h2>
          <ConfidenceChip level={detail.confidence.level} score={detail.confidence.score} />
        </header>
        <ul className="limits-list">
          {detail.confidence.limitations.map((limit) => (
            <li key={limit}>{limit}</li>
          ))}
        </ul>
      </section>

      <section className="panel" data-testid="shock-effect">
        <header className="panel-head">
          <h2>Scenario · GenAI shock</h2>
          <span className={`shock-tag shock-${detail.shock.effect}`}>{detail.shock.effect}</span>
        </header>
        <p>{detail.shock.note}</p>
      </section>
    </div>
  );
}
