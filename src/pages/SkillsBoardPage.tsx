import React from 'react';
import { genaiShock } from '../api';
import { SortableSkillsList } from '../components/SortableSkillsList';
import { ShockSimulator } from '../components/ShockSimulator';
import { AddSkillResearch } from '../components/AddSkillResearch';
import type { MarketSummary, Skill } from '../types';

export function SkillsBoardPage({
  summary,
  onOpenSkill,
}: {
  summary: MarketSummary;
  onOpenSkill: (skill: Skill) => void;
}) {
  const [skills, setSkills] = React.useState<Skill[]>(summary.skills);
  const [shocked, setShocked] = React.useState(false);
  const [shockMessage, setShockMessage] = React.useState<string | null>(null);

  async function shock() {
    try {
      const payload = await genaiShock();
      setSkills(payload.skills);
      setShockMessage(`${payload.shock.label}: ${payload.shock.message}`);
      setShocked(true);
    } catch {
      /* ignore */
    }
  }
  function reset() {
    setSkills(summary.skills);
    setShockMessage(null);
    setShocked(false);
  }

  return (
    <div className="page skills-page">
      <section className="page-head">
        <h1>Skill market board</h1>
        <p className="muted">
          {summary.skills.length} skills priced against the Singapore baseline. Click any row for the full
          stock analysis — quote, seeded history, and the rating breakdown.
        </p>
      </section>

      <AddSkillResearch />

      <ShockSimulator
        divisor={summary.divisor}
        baseline={summary.baseline}
        shocked={shocked}
        message={shockMessage}
        onShock={shock}
        onReset={reset}
      />

      <SortableSkillsList skills={skills} onSelect={onOpenSkill} />
    </div>
  );
}
