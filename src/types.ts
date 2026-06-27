// Shared SkillsMarket types. Kept framework-free so both the market board and
// the resume portfolio views read from one contract.

export type Skill = {
  id: string;
  symbol: string;
  name: string;
  sector: string;
  price: number;
  change: number;
  demand: number;
  supply_proxy: number;
  source_row_count: number;
  provenance: string;
  unit: string;
  spark: number[];
  change_30d: number;
  source_badges: string[];
  salary_mid?: number | null;
  salary_premium?: number | null;
};

export type HistoryPoint = { day: number; price: number };

export type SkillDetail = {
  skill: Skill;
  history: HistoryPoint[];
  history_label: string;
  stats: {
    high: number;
    low: number;
    first: number;
    last: number;
    change_30d: number;
    change_90d: number;
    trend: string;
  };
  methodology: {
    weighted_demand: number;
    supply_proxy: number;
    salary_mid: number | null;
    salary_premium: number | null;
    support: number;
    divisor: number;
    baseline: number;
    raw_score: number;
    formula: string;
    provenance: string;
    demand_explainer: string;
    supply_explainer: string;
    salary_explainer: string;
    divisor_explainer: string;
    baseline_explainer: string;
  };
  confidence: { level: string; score: number; support: number; limitations: string[] };
  source_badges: string[];
  live_evidence: LiveEvidence;
  courses: SkillCourses;
  shock: { name: string; effect: string; multiplier: number; note: string };
  analyst_note: string;
};

export type Sector = {
  name: string;
  symbol: string;
  index: number;
  change: number;
  demand: number;
};

export type Provenance = { signal: string; status: string; source: string };

export type DataSource = {
  name: string;
  role: string;
  kind: string;
  status: string;
  label: string;
  access: string;
  use: string;
  url?: string;
  actor?: string;
  dataset_id?: string;
};

export type PipelineStage = {
  id: string;
  label: string;
  kind: string;
  detail: string;
};

export type Snapshot = {
  snapshot_id?: string;
  kind?: string;
  created_at?: string;
  record_count?: number;
};

export type MarketSummary = {
  baseline: number;
  divisor: number;
  skills: Skill[];
  sectors: Sector[];
  provenance: Provenance[];
  data_sources: DataSource[];
  pipeline: PipelineStage[];
  limits: string[];
  baseline_explainer: string;
  snapshot: Snapshot;
  data_mode: string;
  ingestion: IngestionMeta;
};

export type IngestionMeta = {
  mycareersfuture: { jobs: number; skills: number; fetched_at: string } | null;
  skillsfuture: { courses: number; matched_skills: number; fetched_at: string; dataset_id: string } | null;
};

export type LiveJob = {
  title: string;
  uuid: string;
  url: string;
  salary_min: number | null;
  salary_max: number | null;
  sector: string;
};

export type LiveEvidence = {
  found: boolean;
  source?: string;
  fetched_at?: string;
  demand?: number;
  salary_min?: number | null;
  salary_max?: number | null;
  salary_mid?: number | null;
  top_sector?: string | null;
  sample_jobs?: LiveJob[];
};

export type CourseMatch = {
  ref: string;
  title: string;
  provider: string;
  fee: number | string | null;
  hours: number | string | null;
  url: string | null;
};

export type SkillCourses = {
  found: boolean;
  source?: string;
  fetched_at?: string;
  matches: CourseMatch[];
};

export type SkillResearch = {
  name: string;
  provenance: string;
  disclaimer: string;
  model: string;
  sector: string;
  scarcity: string;
  est_index: number;
  est_salary_min: number | null;
  est_salary_max: number | null;
  summary: string;
  role_direction: string;
  course_query: string;
};

export type SkillResearchResult = {
  name: string;
  on_market: boolean;
  skill_id: string | null;
  price?: number;
  sector?: string;
  source_badges?: string[];
  courses: SkillCourses;
  research: SkillResearch | null;
  research_enabled?: boolean;
};

export type Explanation = {
  skill: string;
  symbol: string;
  price: number;
  weighted_demand: number;
  supply_proxy: number;
  divisor: number;
  source_rows: number;
  formula: string;
  provenance: string;
  plain: string;
};

export type ResumeExampleMeta = { id: string; label: string; role: string };

export type IndexedResumeSkill = {
  name: string;
  matched_skill: string | null;
  price: number | null;
  baseline_delta: number | null;
  sector: string | null;
  status: 'strength' | 'gap' | 'unmatched';
  evidence: string[];
};

export type ResumeAction = {
  type: string;
  title: string;
  skill: string | null;
  why: string;
  how_to_prove: string;
  role_direction: string;
  market_price: number | null;
  course_query: string | null;
  course_url: string | null;
  course_note: string;
};

export type ResumeHighlight = {
  start: number;
  end: number;
  text: string;
  category: 'skill' | 'weak' | 'role' | 'education' | 'achievement';
  label: string;
  detail: string;
  confidence: number;
  skill: string | null;
  affects: string | null;
};

export type ParsedResume = {
  name: string | null;
  current_role: string | null;
  skills: string[];
  evidence: Record<string, string[]>;
};

export type ResumeEvidenceQuote = { skill: string; quote: string };

export type ResumeAiInsight = {
  mode: string;
  model: string | null;
  summary: string;
  strongest_skills: string[];
  high_upside_skills: string[];
  role_fit: string;
  next_moves: string[];
  evidence: ResumeEvidenceQuote[];
};

export type ResumeAnalysis = {
  source: string;
  parsed: ParsedResume;
  document_text: string;
  personal_index: number;
  baseline: number;
  skills: IndexedResumeSkill[];
  strengths: IndexedResumeSkill[];
  gaps: IndexedResumeSkill[];
  highlights: ResumeHighlight[];
  actions: ResumeAction[];
  methodology_summary: string;
  analysis_mode: 'ai_assisted' | 'deterministic';
  ai: ResumeAiInsight | null;
};
