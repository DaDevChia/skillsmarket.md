import { Sparkline } from './Sparkline';
import { SourceBadges } from './SourceBadge';
import type { Skill } from '../types';

export function QuoteCard({ skill, onOpen }: { skill: Skill; onOpen: (skill: Skill) => void }) {
  const up = skill.change >= 0;
  return (
    <button
      type="button"
      className="quote-card"
      data-testid={`quote-card-${skill.id}`}
      onClick={() => onOpen(skill)}
    >
      <div className="quote-top">
        <span className="quote-sym">{skill.symbol}</span>
        <span className={up ? 'positive' : 'negative'}>
          {up ? '▲' : '▼'} {Math.abs(skill.change).toFixed(1)}
        </span>
      </div>
      <div className="quote-name">{skill.name}</div>
      <div className="quote-price">
        {skill.price.toFixed(1)} <small>pts</small>
      </div>
      <Sparkline data={skill.spark} />
      <div className="quote-badges">
        <SourceBadges badges={skill.source_badges} />
      </div>
    </button>
  );
}
