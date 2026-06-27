import { expect, test } from '@playwright/test';

test('top nav routes between all pages', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('top-nav')).toBeVisible();

  await page.getByTestId('nav-skills').click();
  await expect(page).toHaveURL(/\/skills$/);
  await expect(page.getByTestId('skills-list')).toBeVisible();

  await page.getByTestId('nav-methodology').click();
  await expect(page).toHaveURL(/\/methodology$/);
  await expect(page.getByTestId('methodology-page')).toBeVisible();

  await page.getByTestId('nav-sources').click();
  await expect(page).toHaveURL(/\/sources$/);
  await expect(page.getByTestId('sources-page')).toBeVisible();

  await page.getByTestId('nav-resume').click();
  await expect(page).toHaveURL(/\/resume$/);
  await expect(page.getByTestId('resume-intake')).toBeVisible();
});

test('landing shows quote cards with sparklines + source badges, click opens detail', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('top-quotes')).toBeVisible();
  const card = page.getByTestId('top-quotes').locator('.quote-card').first();
  await expect(card.getByTestId('sparkline')).toBeVisible();
  await expect(card.getByTestId('source-badge').first()).toBeVisible();
  await card.click();
  await expect(page.getByTestId('skill-detail-page')).toBeVisible();
});

test('skill detail page shows quote, seeded history and a methodology breakdown', async ({ page }) => {
  await page.goto('/skills');
  await page.getByTestId('skill-list-row-machine-learning').click();
  await expect(page).toHaveURL(/\/skills\/machine-learning$/);
  await expect(page.getByTestId('skill-detail-page')).toBeVisible();
  await expect(page.getByTestId('history-chart')).toBeVisible();
  await expect(page.getByTestId('history-label')).toContainText(/seeded historical proxy/i);
  const method = page.getByTestId('methodology-breakdown');
  await expect(method).toContainText('Demand score');
  await expect(method).toContainText('Supply / applicant proxy');
  await expect(method).toContainText('Frozen divisor');
  await expect(page.getByTestId('confidence-chip').first()).toBeVisible();
  await expect(page.getByTestId('analyst-note')).toBeVisible();
  await expect(page.getByTestId('source-badge').first()).toBeVisible();
  await expect(page.getByTestId('shock-effect')).toBeVisible();
});

test('skill detail is deep-linkable', async ({ page }) => {
  await page.goto('/skills/microsoft-excel');
  await expect(page.getByTestId('skill-detail-page')).toBeVisible();
  await expect(page.getByTestId('detail-price')).toBeVisible();
  await page.getByTestId('back-to-board').click();
  await expect(page).toHaveURL(/\/skills$/);
});

test('sources page is explicit: Apify, MyCareersFuture, SkillsFuture, LinkedIn not ingested', async ({ page }) => {
  await page.goto('/sources');
  const panel = page.getByTestId('sources-panel');
  await expect(panel).toContainText('MyCareersFuture');
  await expect(panel).toContainText('Apify');
  await expect(panel).toContainText('SkillsFuture');
  await expect(panel).toContainText('LinkedIn');
  await expect(panel).toContainText(/not currently ingested/i);
  await expect(page.getByTestId('data-pipeline')).toBeVisible();
});

test('methodology page defines every term', async ({ page }) => {
  await page.goto('/methodology');
  await expect(page.getByTestId('methodology-terms')).toContainText('Supply / applicant proxy');
  await expect(page.getByTestId('methodology-terms')).toContainText('Frozen divisor');
  await expect(page.getByTestId('methodology-baseline')).toContainText('100');
});

test('manual skill entry produces an index, actions and highlights', async ({ page }) => {
  await page.goto('/resume');
  const input = page.getByTestId('manual-skill-input');
  for (const skill of ['Python', 'Machine Learning', 'Microsoft Excel']) {
    await input.fill(skill);
    await input.press('Enter');
  }
  await expect(page.getByTestId('manual-chip')).toHaveCount(3);
  await page.getByTestId('analyze-skills-button').click();
  await expect(page.getByTestId('personal-skill-index')).toBeVisible();
  await expect(page.getByTestId('action-list')).toBeVisible();
  await expect.poll(() => page.getByTestId('resume-highlight').count()).toBeGreaterThan(0);
});
