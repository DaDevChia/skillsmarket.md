import React from 'react';
import { Link } from '../router';
import { ResumeIntake } from '../components/ResumeIntake';
import { ResumeAnalysisPanel } from '../components/ResumeAnalysisPanel';
import { AiAnalystPanel } from '../components/AiAnalystPanel';
import { SkillsGlobe } from '../components/SkillsGlobe';
import { DocumentViewer } from '../components/DocumentViewer';
import { ActionList } from '../components/ActionList';
import { AnalysisProgress, ANALYSIS_STAGES } from '../components/AnalysisProgress';
import { SortableSkillsList } from '../components/SortableSkillsList';
import { SourcesPanel } from '../components/SourcesPanel';
import type {
  IndexedResumeSkill,
  MarketSummary,
  ResumeAnalysis,
  ResumeExampleMeta,
  ResumeHighlight,
  Skill,
} from '../types';

function useProgress(loading: boolean): number {
  const [step, setStep] = React.useState(0);
  React.useEffect(() => {
    if (!loading) return;
    setStep(0);
    const id = setInterval(() => setStep((s) => Math.min(s + 1, ANALYSIS_STAGES.length - 1)), 260);
    return () => clearInterval(id);
  }, [loading]);
  return step;
}

type Tab = 'skills' | 'courses' | 'sources';

export function ResumePage({
  summary,
  examples,
  analysis,
  loading,
  error,
  selectedSkill,
  onSelectSkill,
  onAnalyzeText,
  onAnalyzeExample,
  onUpload,
  onAnalyzeSkills,
  onOpenSkill,
}: {
  summary: MarketSummary;
  examples: ResumeExampleMeta[];
  analysis: ResumeAnalysis | null;
  loading: boolean;
  error: string | null;
  selectedSkill: IndexedResumeSkill | null;
  onSelectSkill: (skill: IndexedResumeSkill | null) => void;
  onAnalyzeText: (text: string) => void;
  onAnalyzeExample: (id: string) => void;
  onUpload: (file: File) => void;
  onAnalyzeSkills: (skills: string[]) => void;
  onOpenSkill: (skill: Skill) => void;
}) {
  const step = useProgress(loading);
  const [highlight, setHighlight] = React.useState<ResumeHighlight | null>(null);
  const [tab, setTab] = React.useState<Tab>('skills');
  const resultsRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    setHighlight(null);
  }, [analysis]);

  // When a fresh analysis lands, bring the reader straight to the results so the
  // workbench never feels hidden below the fold (especially after upload/paste).
  React.useEffect(() => {
    if (!loading && analysis && resultsRef.current) {
      resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
      resultsRef.current.focus?.({ preventScroll: true });
    }
  }, [loading, analysis]);

  const courseActions = analysis ? analysis.actions.filter((action) => action.course_url) : [];

  return (
    <div className="resume-page" data-testid="resume-page">
      <nav className="page-nav">
        <Link to="/" className="back-link" data-testid="back-to-overview">
          ← Market overview
        </Link>
        <span className="page-title">Resume analyst workbench</span>
      </nav>

      <ResumeIntake
        examples={examples}
        allSkillNames={summary.skills.map((skill) => skill.name)}
        onAnalyzeText={onAnalyzeText}
        onAnalyzeExample={onAnalyzeExample}
        onUpload={onUpload}
        onAnalyzeSkills={onAnalyzeSkills}
        loading={loading}
        error={error}
      />

      {loading && <AnalysisProgress step={step} done={false} />}

      {!loading && analysis && (
        <div ref={resultsRef} tabIndex={-1} className="resume-results" data-testid="resume-results">
          {analysis.ai ? (
            <AiAnalystPanel analysis={analysis} />
          ) : (
            <section className="panel ai-fallback" data-testid="ai-fallback">
              <span className="panel-tag" data-testid="analysis-mode-badge">⚙ Deterministic analysis</span>
              <p className="muted">
                The AI analyst is offline right now, so this is SkillsMarket's deterministic, evidence-grounded
                readout — fully usable. Every skill below is matched and priced against the live market.
              </p>
            </section>
          )}

          <div className="workbench" data-testid="workbench">
            <div className="wb-doc">
              <DocumentViewer
                text={analysis.document_text}
                highlights={analysis.highlights}
                selected={highlight}
                onSelect={setHighlight}
              />
            </div>
            <div className="wb-read">
              <ResumeAnalysisPanel
                analysis={analysis}
                selectedSkill={selectedSkill}
                onSelectSkill={onSelectSkill}
              />
            </div>
            <div className="wb-act">
              <ActionList actions={analysis.actions} />
            </div>
            <div className="wb-globe">
              <SkillsGlobe skills={analysis.skills} onSelect={onSelectSkill} />
            </div>
          </div>

          <section className="panel workbench-tabs" data-testid="workbench-tabs">
            <div className="tab-bar" role="tablist">
              <button type="button" role="tab" aria-selected={tab === 'skills'} className={`tab ${tab === 'skills' ? 'active' : ''}`} data-testid="tab-skills" onClick={() => setTab('skills')}>
                All skills
              </button>
              <button type="button" role="tab" aria-selected={tab === 'courses'} className={`tab ${tab === 'courses' ? 'active' : ''}`} data-testid="tab-courses" onClick={() => setTab('courses')}>
                Courses
              </button>
              <button type="button" role="tab" aria-selected={tab === 'sources'} className={`tab ${tab === 'sources' ? 'active' : ''}`} data-testid="tab-sources" onClick={() => setTab('sources')}>
                Sources
              </button>
            </div>

            {tab === 'skills' && (
              <div className="tab-panel" data-testid="workbench-tab-skills">
                <SortableSkillsList skills={summary.skills} onSelect={onOpenSkill} />
              </div>
            )}
            {tab === 'courses' && (
              <div className="tab-panel" data-testid="workbench-tab-courses">
                <p className="muted">
                  Curated MySkillsFuture course searches for your recommended skills — not live enrolment results.
                </p>
                <ul className="course-tab-list">
                  {courseActions.map((action, index) => (
                    <li key={`${action.skill}-${index}`}>
                      <a className="course-link" data-testid="course-link" href={action.course_url ?? '#'} target="_blank" rel="noreferrer">
                        {action.course_query} ↗
                      </a>
                      <span className="muted"> · {action.title}</span>
                    </li>
                  ))}
                </ul>
                <a className="ghost-button" href="https://courses.myskillsfuture.gov.sg/search?termOrigin=ORGANIC" target="_blank" rel="noreferrer">
                  Open MySkillsFuture directory
                </a>
              </div>
            )}
            {tab === 'sources' && (
              <div className="tab-panel" data-testid="workbench-tab-sources">
                <SourcesPanel summary={summary} />
              </div>
            )}
          </section>
        </div>
      )}

      {!loading && !analysis && (
        <section className="panel result-empty" data-testid="result-empty">
          <h2>Your analyst readout appears here.</h2>
          <p className="muted">
            Upload a PDF/DOCX/TXT, paste text, or pick an example. You get progress states, a highlighted
            document, your Skill Index, 3–5 next moves with course links, and the data pipeline.
          </p>
          <ul className="empty-points">
            <li>100 = Singapore median skill price.</li>
            <li>Evidence is highlighted from your actual text — nothing invented.</li>
            <li>Upload PDF/DOCX/TXT, paste, pick an example, or key in your own skills.</li>
          </ul>
        </section>
      )}
    </div>
  );
}
