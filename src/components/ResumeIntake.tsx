import React from 'react';
import { ManualSkillEntry } from './ManualSkillEntry';
import type { ResumeExampleMeta } from '../types';

const SAMPLE_TEXT =
  'Admin executive with 12 years in scheduling, procurement coordination, Microsoft Excel ' +
  'reporting, and customer service. Builds weekly operations dashboards and wants to move into ' +
  'data-enabled operations.';

export function ResumeIntake({
  examples,
  allSkillNames,
  onAnalyzeText,
  onAnalyzeExample,
  onUpload,
  onAnalyzeSkills,
  loading,
  error,
}: {
  examples: ResumeExampleMeta[];
  allSkillNames: string[];
  onAnalyzeText: (text: string) => Promise<void> | void;
  onAnalyzeExample: (id: string) => Promise<void> | void;
  onUpload: (file: File) => Promise<void> | void;
  onAnalyzeSkills: (skills: string[]) => Promise<void> | void;
  loading: boolean;
  error: string | null;
}) {
  const [text, setText] = React.useState('');
  const fileRef = React.useRef<HTMLInputElement>(null);

  return (
    <section className="panel intake" data-testid="resume-intake">
      <header className="panel-head">
        <h2>Upload resume. Get your skill index.</h2>
        <span className="panel-tag">no account · no ranking · just a market readout</span>
      </header>

      <label className="field-label" htmlFor="resume-paste-box">
        Paste resume text
      </label>
      <textarea
        id="resume-paste-box"
        data-testid="resume-paste-box"
        className="paste-box"
        placeholder="Paste your resume or a few lines about what you do…"
        value={text}
        onChange={(event) => setText(event.target.value)}
        rows={6}
      />

      <div className="intake-actions">
        <button
          type="button"
          className="primary"
          data-testid="analyze-text-button"
          disabled={loading || text.trim().length < 20}
          onClick={() => onAnalyzeText(text.trim())}
        >
          Get my skill index
        </button>
        <button
          type="button"
          className="ghost-button"
          data-testid="sample-fill-button"
          onClick={() => setText(SAMPLE_TEXT)}
        >
          Use a sample
        </button>
        <button
          type="button"
          className="ghost-button"
          data-testid="upload-resume-button"
          disabled={loading}
          onClick={() => fileRef.current?.click()}
        >
          Upload PDF / DOCX / TXT
        </button>
        <input
          ref={fileRef}
          type="file"
          accept=".txt,.pdf,.docx,text/plain,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          data-testid="resume-upload-input"
          hidden
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) void onUpload(file);
            event.target.value = '';
          }}
        />
      </div>

      <p className="intake-divider">Or try an example profile.</p>
      <div className="example-grid">
        {examples.map((example) => (
          <button
            key={example.id}
            type="button"
            className="example-chip"
            data-testid={`example-profile-${example.id}`}
            disabled={loading}
            onClick={() => onAnalyzeExample(example.id)}
          >
            <b>{example.label}</b>
            <span>{example.role}</span>
          </button>
        ))}
      </div>

      <ManualSkillEntry allSkillNames={allSkillNames} onSubmit={onAnalyzeSkills} loading={loading} />

      {loading && <p className="intake-status" role="status">Reading the tape…</p>}
      {error && (
        <p className="intake-error" role="alert" data-testid="resume-error">
          {error}
        </p>
      )}
    </section>
  );
}
