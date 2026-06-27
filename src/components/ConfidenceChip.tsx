export function ConfidenceChip({ level, score }: { level: string; score?: number }) {
  return (
    <span className={`confidence-chip conf-${level}`} data-testid="confidence-chip">
      confidence: {level}
      {score != null ? ` (${Math.round(score * 100)}%)` : ''}
    </span>
  );
}
