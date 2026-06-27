export const ANALYSIS_STAGES = [
  'Extracting text',
  'Identifying evidence',
  'Matching skills',
  'Pricing against live market',
  'Consulting AI analyst',
  'Composing your readout',
];

export function AnalysisProgress({ step, done }: { step: number; done: boolean }) {
  return (
    <section className="panel analysis-progress" data-testid="analysis-progress">
      <header className="panel-head">
        <h2>{done ? 'Analysis complete' : 'Analysing your resume against the live market + AI analyst…'}</h2>
        <span className="panel-tag">SkillsMarket analyst</span>
      </header>
      <ol className="progress-steps">
        {ANALYSIS_STAGES.map((label, index) => {
          const state = done || index < step ? 'done' : index === step ? 'active' : 'pending';
          return (
            <li key={label} className={`progress-step ${state}`} data-testid={`progress-step-${index}`}>
              <span className="step-dot">{state === 'done' ? '✓' : index + 1}</span>
              <span className="step-label">{label}</span>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
