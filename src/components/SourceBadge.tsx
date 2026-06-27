function badgeClass(label: string): string {
  const key = label.toLowerCase();
  if (key.includes('seed')) return 'badge-seeded';
  if (key.includes('career')) return 'badge-mcf';
  if (key.includes('catalog')) return 'badge-catalogue';
  if (key.includes('real')) return 'badge-live';
  return 'badge-default';
}

export function SourceBadge({ label }: { label: string }) {
  return (
    <span className={`source-badge ${badgeClass(label)}`} data-testid="source-badge">
      {label}
    </span>
  );
}

export function SourceBadges({ badges }: { badges: string[] }) {
  return (
    <span className="source-badges">
      {badges.map((badge) => (
        <SourceBadge key={badge} label={badge} />
      ))}
    </span>
  );
}
