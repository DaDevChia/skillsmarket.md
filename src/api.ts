import type {
  Explanation,
  MarketSummary,
  ResumeAnalysis,
  ResumeExampleMeta,
  SkillDetail,
  SkillResearchResult,
} from './types';

async function asJson<T>(response: Response): Promise<T> {
  if (!response.ok) throw new Error(`API returned ${response.status}`);
  return (await response.json()) as T;
}

export async function getMarketSummary(): Promise<MarketSummary> {
  return asJson<MarketSummary>(await fetch('/api/market/summary'));
}

export async function getResumeExamples(): Promise<ResumeExampleMeta[]> {
  const body = await asJson<{ examples: ResumeExampleMeta[] }>(
    await fetch('/api/resume/examples'),
  );
  return body.examples;
}

export async function analyzeResumeText(text: string): Promise<ResumeAnalysis> {
  return asJson<ResumeAnalysis>(
    await fetch('/api/resume/analyze-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    }),
  );
}

export async function analyzeResumeExample(id: string): Promise<ResumeAnalysis> {
  return asJson<ResumeAnalysis>(
    await fetch(`/api/resume/analyze-example/${encodeURIComponent(id)}`, { method: 'POST' }),
  );
}

export async function uploadResume(file: File): Promise<ResumeAnalysis> {
  const form = new FormData();
  form.append('file', file);
  const response = await fetch('/api/resume/upload', { method: 'POST', body: form });
  if (!response.ok) {
    // Surface the backend's specific reason (415 unsupported, 422 unreadable, …).
    let detail = `Upload failed (${response.status})`;
    try {
      const body = await response.json();
      if (body?.detail) detail = String(body.detail);
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail);
  }
  return (await response.json()) as ResumeAnalysis;
}

export async function explainSkill(name: string): Promise<Explanation> {
  return asJson<Explanation>(await fetch(`/api/explain/skill/${encodeURIComponent(name)}`));
}

export async function getSkillDetail(skillId: string): Promise<SkillDetail> {
  return asJson<SkillDetail>(await fetch(`/api/skill/${encodeURIComponent(skillId)}`));
}

export async function researchSkill(name: string): Promise<SkillResearchResult> {
  return asJson<SkillResearchResult>(
    await fetch('/api/skill/research', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    }),
  );
}

export async function analyzeManualSkills(skills: string[]): Promise<ResumeAnalysis> {
  return asJson<ResumeAnalysis>(
    await fetch('/api/resume/analyze-skills', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ skills }),
    }),
  );
}

export async function genaiShock(): Promise<MarketSummary & { shock: { label: string; message: string } }> {
  return asJson(await fetch('/api/shocks/genai', { method: 'POST' }));
}
