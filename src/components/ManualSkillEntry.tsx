import React from 'react';

export function ManualSkillEntry({
  allSkillNames,
  onSubmit,
  loading,
}: {
  allSkillNames: string[];
  onSubmit: (skills: string[]) => void;
  loading: boolean;
}) {
  const [chips, setChips] = React.useState<string[]>([]);
  const [text, setText] = React.useState('');

  function add(value: string) {
    const name = value.trim();
    if (name && !chips.some((c) => c.toLowerCase() === name.toLowerCase())) {
      setChips([...chips, name]);
    }
    setText('');
  }

  return (
    <div className="manual-entry" data-testid="manual-skill-entry">
      <label className="field-label" htmlFor="manual-skill-input">
        …or key in your own skills
      </label>
      <div className="chip-input">
        {chips.map((chip) => (
          <span key={chip} className="skill-chip" data-testid="manual-chip">
            {chip}
            <button type="button" aria-label={`Remove ${chip}`} onClick={() => setChips(chips.filter((c) => c !== chip))}>
              ×
            </button>
          </span>
        ))}
        <input
          id="manual-skill-input"
          data-testid="manual-skill-input"
          list="manual-skill-options"
          value={text}
          placeholder="Type a skill, press Enter"
          onChange={(event) => setText(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              event.preventDefault();
              add(text);
            }
          }}
        />
        <datalist id="manual-skill-options">
          {allSkillNames.map((name) => (
            <option key={name} value={name} />
          ))}
        </datalist>
      </div>
      <button
        type="button"
        className="primary"
        data-testid="analyze-skills-button"
        disabled={loading || chips.length === 0}
        onClick={() => onSubmit(chips)}
      >
        Index my {chips.length || ''} skill{chips.length === 1 ? '' : 's'}
      </button>
    </div>
  );
}
