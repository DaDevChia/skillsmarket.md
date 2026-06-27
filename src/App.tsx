import React from 'react';
import {
  analyzeManualSkills,
  analyzeResumeExample,
  analyzeResumeText,
  getMarketSummary,
  getResumeExamples,
  uploadResume,
} from './api';
import { ErrorState, Shell } from './components/Shell';
import { Ticker } from './components/Ticker';
import { LandingPage } from './pages/LandingPage';
import { ResumePage } from './pages/ResumePage';
import { SkillsBoardPage } from './pages/SkillsBoardPage';
import { SkillDetailPage } from './pages/SkillDetailPage';
import { MethodologyPage } from './pages/MethodologyPage';
import { SourcesPage } from './pages/SourcesPage';
import { navigate, routeSegments, useRoute } from './router';
import type { IndexedResumeSkill, MarketSummary, ResumeAnalysis, ResumeExampleMeta, Skill } from './types';

function useMarketSummary() {
  const [summary, setSummary] = React.useState<MarketSummary | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(true);

  const load = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setSummary(await getMarketSummary());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown API error');
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    void load();
  }, [load]);

  return { summary, error, loading, reload: load };
}

export function App() {
  const route = useRoute();
  const { summary, error, loading, reload } = useMarketSummary();
  const [examples, setExamples] = React.useState<ResumeExampleMeta[]>([]);
  const [analysis, setAnalysis] = React.useState<ResumeAnalysis | null>(null);
  const [analysisLoading, setAnalysisLoading] = React.useState(false);
  const [analysisError, setAnalysisError] = React.useState<string | null>(null);
  const [selectedSkill, setSelectedSkill] = React.useState<IndexedResumeSkill | null>(null);

  React.useEffect(() => {
    getResumeExamples()
      .then(setExamples)
      .catch(() => setExamples([]));
  }, []);

  const run = React.useCallback(async (task: Promise<ResumeAnalysis>) => {
    setAnalysisLoading(true);
    setAnalysisError(null);
    try {
      const result = await task;
      setAnalysis(result);
      setSelectedSkill(null);
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setAnalysisLoading(false);
    }
  }, []);

  // Ensure resume actions always land the user on the results page.
  const ensureResumeRoute = React.useCallback(() => {
    if (!window.location.pathname.startsWith('/resume')) navigate('/resume');
  }, []);

  const analyzeText = React.useCallback(
    (text: string) => {
      ensureResumeRoute();
      void run(analyzeResumeText(text));
    },
    [run, ensureResumeRoute],
  );
  const analyzeExample = React.useCallback(
    (id: string) => {
      ensureResumeRoute();
      void run(analyzeResumeExample(id));
    },
    [run, ensureResumeRoute],
  );
  const upload = React.useCallback(
    (file: File) => {
      ensureResumeRoute();
      void run(uploadResume(file));
    },
    [run, ensureResumeRoute],
  );
  const analyzeSkills = React.useCallback(
    (skills: string[]) => {
      ensureResumeRoute();
      void run(analyzeManualSkills(skills));
    },
    [run, ensureResumeRoute],
  );
  const openSkill = React.useCallback((skill: Skill) => navigate(`/skills/${skill.id}`), []);

  if (loading) {
    return (
      <Shell>
        <div className="loading">Opening the exchange…</div>
      </Shell>
    );
  }

  if (error || !summary) {
    return (
      <Shell>
        <ErrorState error={error || 'No data'} onRetry={reload} />
      </Shell>
    );
  }

  const segments = routeSegments(route);
  const onSkillByName = (name: string) => {
    const match = summary.skills.find((skill) => skill.name === name);
    if (match) navigate(`/skills/${match.id}`);
  };

  let page: React.ReactNode;
  if (segments[0] === 'resume') {
    page = (
      <ResumePage
        summary={summary}
        examples={examples}
        analysis={analysis}
        loading={analysisLoading}
        error={analysisError}
        selectedSkill={selectedSkill}
        onSelectSkill={setSelectedSkill}
        onAnalyzeText={analyzeText}
        onAnalyzeExample={analyzeExample}
        onUpload={upload}
        onAnalyzeSkills={analyzeSkills}
        onOpenSkill={openSkill}
      />
    );
  } else if (segments[0] === 'skills' && segments[1]) {
    page = <SkillDetailPage skillId={segments[1]} />;
  } else if (segments[0] === 'skills') {
    page = <SkillsBoardPage summary={summary} onOpenSkill={openSkill} />;
  } else if (segments[0] === 'methodology') {
    page = <MethodologyPage summary={summary} />;
  } else if (segments[0] === 'sources') {
    page = <SourcesPage summary={summary} />;
  } else {
    page = <LandingPage summary={summary} onOpenSkill={openSkill} />;
  }

  return (
    <Shell mode={summary.data_mode}>
      <Ticker skills={summary.skills} sectors={summary.sectors} onSelect={onSkillByName} />
      {page}

      <footer className="terminal-footer">
        <span>SkillsMarket · Singapore skills exchange</span>
        <span className="muted">
          {summary.data_mode === 'real_proxy' ? 'Live proxy snapshot.' : 'Seeded fixture. No live snapshot loaded.'}
        </span>
      </footer>
    </Shell>
  );
}
