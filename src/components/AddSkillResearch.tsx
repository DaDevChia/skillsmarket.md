import React from 'react';
import { researchSkill } from '../api';
import { navigate } from '../router';
import { SourceBadges } from './SourceBadge';
import type { SkillResearchResult } from '../types';

// Add a skill: if it's on the board, jump to its quote; if not, the agent
// researches it live (LLM) and shows a clearly-labelled estimate + real courses.
export function AddSkillResearch() {
  const [name, setName] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [result, setResult] = React.useState<SkillResearchResult | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  async function run() {
    const query = name.trim();
    if (query.length < 2) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await researchSkill(query);
      if (data.on_market && data.skill_id) {
        navigate(`/skills/${data.skill_id}`);
        return;
      }
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Research failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel add-skill" data-testid="add-skill">
      <header className="panel-head">
        <h2>Add a skill · live research</h2>
        <span className="panel-tag">on the board → quote · new → AI-researched</span>
      </header>
      <div className="add-skill-row">
        <input
          type="text"
          className="skills-search"
          data-testid="add-skill-input"
          placeholder="e.g. Rust, Prompt Engineering, Quantum Computing…"
          value={name}
          onChange={(event) => setName(event.target.value)}
          onKeyDown={(event) => event.key === 'Enter' && run()}
          aria-label="Add a skill to research"
        />
        <button type="button" className="primary" data-testid="research-skill-button" disabled={loading || name.trim().length < 2} onClick={run}>
          {loading ? 'Researching…' : 'Add / research'}
        </button>
      </div>
      {error && <p className="intake-error">{error}</p>}

      {result && !result.on_market && (
        <div className="research-result" data-testid="research-result">
          {result.research ? (
            <>
              <div className="research-head">
                <h3>{result.research.name}</h3>
                <span className="source-badge badge-ai" data-testid="ai-badge">AI-RESEARCHED</span>
              </div>
              <p className="research-disclaimer" data-testid="research-disclaimer">{result.research.disclaimer}</p>
              <div className="research-grid">
                <div><dt>Est. index</dt><dd>{result.research.est_index.toFixed(0)}</dd></div>
                <div><dt>Scarcity</dt><dd>{result.research.scarcity}</dd></div>
                <div><dt>Sector</dt><dd>{result.research.sector}</dd></div>
                <div><dt>Est. salary</dt><dd>${result.research.est_salary_min ?? '—'}–{result.research.est_salary_max ?? '—'}</dd></div>
              </div>
              <p className="research-summary">{result.research.summary}</p>
              <p className="muted">Role direction: {result.research.role_direction} · via {result.research.model}</p>
            </>
          ) : (
            <p className="muted" data-testid="research-disabled">
              “{result.name}” isn’t on the board, and live AI research is currently disabled.
              {result.research_enabled === false ? ' Enable SKILLSMARKET_ENABLE_SKILL_RESEARCH to turn it on.' : ''}
            </p>
          )}
          {result.courses.found && (
            <ul className="course-detail-list">
              {result.courses.matches.map((course) => (
                <li key={course.ref}>
                  <a href={course.url ?? '#'} target="_blank" rel="noreferrer">{course.title} ↗</a>
                  <span className="muted"> · {course.provider} · ${course.fee}</span>
                </li>
              ))}
            </ul>
          )}
          <SourceBadges badges={['AI estimate', 'SkillsFuture courses']} />
        </div>
      )}
    </section>
  );
}
