import React from 'react';
import type { IndexedResumeSkill, ResumeAction, ResumeAnalysis } from '../types';

function verdict(index: number, baseline: number): string {
  if (index >= baseline + 20) return 'Scarce portfolio. You price above the market.';
  if (index >= baseline) return 'At or above the national baseline.';
  if (index === 0) return 'No indexed skills detected yet.';
  return 'Below baseline. Common skills dominate your portfolio.';
}

function skillBlurb(skill: IndexedResumeSkill): string {
  if (skill.price == null) return 'Not yet on the SkillsMarket index.';
  if (skill.price >= 120) return 'Scarce. Differentiating in this market.';
  if (skill.price >= 100) return 'At baseline. Holds its value.';
  return 'Common. Useful, not differentiating.';
}

function SkillRow({
  skill,
  onSelect,
}: {
  skill: IndexedResumeSkill;
  onSelect: (skill: IndexedResumeSkill) => void;
}) {
  const delta = skill.baseline_delta ?? 0;
  return (
    <button type="button" className={`skill-row status-${skill.status}`} onClick={() => onSelect(skill)}>
      <span className="skill-name">{skill.name}</span>
      <span className="skill-price">{skill.price == null ? '—' : skill.price.toFixed(0)}</span>
      <span className={`skill-delta ${delta >= 0 ? 'positive' : 'negative'}`}>
        {skill.price == null ? 'unpriced' : `${delta >= 0 ? '+' : ''}${delta.toFixed(0)}`}
      </span>
    </button>
  );
}

export function ResumeAnalysisPanel({
  analysis,
  selectedSkill,
  onSelectSkill,
}: {
  analysis: ResumeAnalysis;
  selectedSkill: IndexedResumeSkill | null;
  onSelectSkill: (skill: IndexedResumeSkill | null) => void;
}) {
  const nextMove: ResumeAction | undefined =
    analysis.actions.find((action) => action.type === 'learn') ?? analysis.actions[0];
  const provenance = analysis.source.startsWith('example') ? 'seeded example' : 'your text · not stored';
  const aiAssisted = analysis.analysis_mode === 'ai_assisted';

  return (
    <section className="panel analysis" data-testid="resume-analysis">
      <header className="panel-head">
        <h2>Your skills portfolio</h2>
        <span className="head-tags">
          <span
            className={`panel-tag mode-tag ${aiAssisted ? 'ai' : 'det'}`}
            data-testid="portfolio-mode-badge"
          >
            {aiAssisted ? '✦ AI-assisted' : '⚙ Deterministic'}
          </span>
          <span className="panel-tag">{provenance}</span>
        </span>
      </header>

      <div className="index-block">
        <div className="index-figure">
          <span className="index-label">Your Skill Index</span>
          <strong data-testid="personal-skill-index">{analysis.personal_index.toFixed(0)}</strong>
        </div>
        <div className="index-baseline">
          <p className="baseline-line">100 = Singapore median skill price.</p>
          <p className="baseline-sub">Above 100 means scarcer. Below 100 means common.</p>
          <p className={`index-verdict ${analysis.personal_index >= analysis.baseline ? 'positive' : 'negative'}`}>
            {verdict(analysis.personal_index, analysis.baseline)}
          </p>
        </div>
      </div>

      <div className="next-move" data-testid="next-move-card">
        <span className="panel-tag">Best next move</span>
        <p className="next-move-title">{nextMove ? nextMove.title : 'Paste a fuller resume.'}</p>
        {nextMove && <p className="next-move-why">{nextMove.why}</p>}
      </div>

      <div className="skill-columns">
        <div className="skill-col" data-testid="top-skills">
          <h3>Top skills</h3>
          {analysis.strengths.length ? (
            analysis.strengths.map((skill) => (
              <SkillRow key={skill.name} skill={skill} onSelect={onSelectSkill} />
            ))
          ) : (
            <p className="muted">No skills above baseline yet.</p>
          )}
        </div>
        <div className="skill-col" data-testid="below-baseline-skills">
          <h3>Below baseline</h3>
          {analysis.gaps.length ? (
            analysis.gaps.map((skill) => (
              <SkillRow key={skill.name} skill={skill} onSelect={onSelectSkill} />
            ))
          ) : (
            <p className="muted">No common skills detected.</p>
          )}
        </div>
      </div>

      {selectedSkill && (
        <div className="skill-detail" data-testid="skill-detail" role="dialog" aria-label="Skill detail">
          <button type="button" className="close" aria-label="Close skill detail" onClick={() => onSelectSkill(null)}>
            ×
          </button>
          <p className="detail-name">{selectedSkill.name}</p>
          <p className="detail-points">
            {selectedSkill.price == null ? 'Unpriced' : `${selectedSkill.price.toFixed(0)} points`}
          </p>
          {selectedSkill.baseline_delta != null && (
            <p className={`detail-delta ${selectedSkill.baseline_delta >= 0 ? 'positive' : 'negative'}`}>
              {Math.abs(selectedSkill.baseline_delta).toFixed(0)}{' '}
              {selectedSkill.baseline_delta >= 0 ? 'above baseline' : 'below baseline'}
            </p>
          )}
          <p className="detail-blurb">{skillBlurb(selectedSkill)}</p>
          {selectedSkill.evidence.length > 0 && (
            <p className="detail-evidence">“{selectedSkill.evidence[0]}”</p>
          )}
        </div>
      )}
    </section>
  );
}
