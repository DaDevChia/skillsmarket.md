import { expect, test } from '@playwright/test';
import path from 'path';

const FIXTURES = path.join(__dirname, 'fixtures');

test('AI workbench renders highlighted document, actions and tabs for an example', async ({ page }) => {
  await page.goto('/resume');
  await page.getByTestId('example-profile-admin-to-data').click();

  await expect(page.getByTestId('workbench')).toBeVisible();
  const viewer = page.getByTestId('document-viewer');
  await expect(viewer).toBeVisible();

  // Evidence highlights render from the actual document text.
  const highlights = page.getByTestId('resume-highlight');
  await expect.poll(() => highlights.count()).toBeGreaterThan(0);

  // Clicking a highlight reveals why it mattered + confidence.
  await highlights.first().click();
  await expect(page.getByTestId('highlight-detail')).toBeVisible();
  await expect(page.getByTestId('highlight-detail')).toContainText(/confidence/i);

  // 3–5 concrete actions, each learn action carrying a SkillsFuture course link.
  const actions = page.getByTestId('action-card');
  await expect.poll(() => actions.count()).toBeGreaterThanOrEqual(3);
  await expect(page.getByTestId('action-list').getByTestId('course-link').first()).toBeVisible();
  await expect(page.getByTestId('action-list').getByTestId('course-link').first()).toHaveAttribute(
    'href',
    /myskillsfuture\.gov\.sg/,
  );
});

test('workbench tabs switch between skills, courses and sources', async ({ page }) => {
  await page.goto('/resume');
  await page.getByTestId('example-profile-fresh-grad-analytics').click();
  await expect(page.getByTestId('workbench-tabs')).toBeVisible();

  await page.getByTestId('tab-sources').click();
  await expect(page.getByTestId('workbench-tab-sources')).toBeVisible();
  await expect(page.getByTestId('data-pipeline')).toBeVisible();
  await expect(page.getByTestId('data-limits')).toBeVisible();

  await page.getByTestId('tab-skills').click();
  await expect(page.getByTestId('workbench-tab-skills').getByTestId('skills-list')).toBeVisible();
});

test('progress states show while analysing', async ({ page }) => {
  // Slow the analysis response so the progress stepper is observable.
  await page.route('**/api/resume/analyze-example/**', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 900));
    await route.continue();
  });
  await page.goto('/resume');
  await page.getByTestId('example-profile-logistics-coordinator').click();
  await expect(page.getByTestId('analysis-progress')).toBeVisible();
  await expect(page.getByTestId('progress-step-0')).toBeVisible();
  await expect(page.getByTestId('personal-skill-index')).toBeVisible();
});

for (const file of ['resume.txt', 'resume.pdf', 'resume.docx']) {
  test(`highlights render after uploading ${file}`, async ({ page }) => {
    await page.goto('/resume');
    await page.getByTestId('resume-upload-input').setInputFiles(path.join(FIXTURES, file));
    await expect(page.getByTestId('personal-skill-index')).toBeVisible();
    await expect(page.getByTestId('document-viewer')).toBeVisible();
    await expect.poll(() => page.getByTestId('resume-highlight').count()).toBeGreaterThan(0);
  });
}

test('pasted text produces highlights', async ({ page }) => {
  await page.goto('/resume');
  await page
    .getByTestId('resume-paste-box')
    .fill('Operations analyst skilled in Python and Microsoft Excel. Reduced costs by 25%. Bachelor degree.');
  await page.getByTestId('analyze-text-button').click();
  await expect(page.getByTestId('document-viewer')).toBeVisible();
  await expect.poll(() => page.getByTestId('resume-highlight').count()).toBeGreaterThan(0);
});
