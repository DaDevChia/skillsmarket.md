import React from 'react';
import type { ResumeAnalysis } from '../types';

// The AI analyst readout. Renders only when the LLM ran and its output survived
// grounding (analysis.ai present). When absent, ResumeAnalysisPanel shows an
// honest deterministic-fallback note instead — never an error wall.
export function AiAnalystPanel({ analysis }: { analysis: ResumeAnalysis }) {
  const ai = analysis.ai;
  if (!ai) return null;

  return (
    <section className="panel ai-analyst" data-testid="ai-analyst">
      <header className="panel-head">
        <h2>AI analyst readout</h2>
        <span className="panel-tag ai-tag" data-testid="ai-assisted-badge" title={ai.model ?? undefined}>
          ✦ AI-assisted{ai.model ? ` · ${ai.model}` : ''}
        </span>
      </header>

      {ai.summary && <p className="ai-summary" data-testid="ai-summary">{ai.summary}</p>}

      {ai.role_fit && (
        <div className="ai-rolefit">
          <span className="ai-kicker">Best-fit direction</span>
          <p>{ai.role_fit}</p>
        </div>
      )}

      <div className="ai-skill-cols">
        {ai.strongest_skills.length > 0 && (
          <div className="ai-skill-col" data-testid="ai-strongest">
            <span className="ai-kicker">Strongest skills</span>
            <div className="ai-pills">
              {ai.strongest_skills.map((skill) => (
                <span key={skill} className="ai-pill strong">{skill}</span>
              ))}
            </div>
          </div>
        )}
        {ai.high_upside_skills.length > 0 && (
          <div className="ai-skill-col" data-testid="ai-upside">
            <span className="ai-kicker">High-upside to learn</span>
            <div className="ai-pills">
              {ai.high_upside_skills.map((skill) => (
                <span key={skill} className="ai-pill upside">{skill}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      {ai.next_moves.length > 0 && (
        <div className="ai-moves" data-testid="ai-next-moves">
          <span className="ai-kicker">Next moves</span>
          <ol>
            {ai.next_moves.map((move, index) => (
              <li key={index}>{move}</li>
            ))}
          </ol>
        </div>
      )}

      {ai.evidence.length > 0 && (
        <div className="ai-evidence" data-testid="ai-evidence">
          <span className="ai-kicker">Evidence from your text</span>
          <ul>
            {ai.evidence.map((item, index) => (
              <li key={index}>
                {item.skill && <b>{item.skill}: </b>}
                <q>{item.quote}</q>
              </li>
            ))}
          </ul>
        </div>
      )}

      <p className="ai-foot muted">
        AI-narrated, evidence-bounded: skills are matched to the live market and every quote is verbatim
        from your text — nothing invented. Prices and course links come from SkillsMarket data.
      </p>
    </section>
  );
}
