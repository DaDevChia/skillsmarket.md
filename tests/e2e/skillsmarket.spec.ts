import { expect, test } from '@playwright/test';

// Market board lives on /skills now; sources on /sources. Landing is a slim overview.

test('1. landing overview shows ticker, quotes and sector indices', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'The Singapore skills exchange.' })).toBeVisible();
  await expect(page.getByTestId('big-board')).toBeVisible(); // ticker
  await expect(page.getByTestId('top-quotes')).toBeVisible();
  await expect(page.getByTestId('sector-indices')).toBeVisible();
});

test('2. a skills board row opens the skill detail page', async ({ page }) => {
  await page.goto('/skills');
  await page.getByTestId('skill-list-row-microsoft-excel').click();
  await expect(page).toHaveURL(/\/skills\/microsoft-excel$/);
  await expect(page.getByRole('heading', { name: /Microsoft Excel/ })).toBeVisible();
  await expect(page.getByTestId('methodology-breakdown')).toContainText('frozen_divisor');
});

test('3. sources page labels the pipeline, provenance and the baseline honestly', async ({ page }) => {
  await page.goto('/sources');
  const panel = page.getByTestId('sources-panel');
  await expect(panel).toBeVisible();
  await expect(panel.getByTestId('baseline-explainer')).toContainText('100 =');
  await expect(panel.getByTestId('data-pipeline')).toContainText('MyCareersFuture postings');
  await expect(panel.getByTestId('data-pipeline')).toContainText('Apify ingestion');
  await expect(panel.getByTestId('data-limits')).toContainText(/proxy/i);
  await expect(panel.getByTestId('provenance-status-skill-demand')).toHaveText('seeded');
});

test('4. GenAI shock reprices skills without moving the baseline', async ({ page }) => {
  await page.goto('/skills');
  const baselineCopy = page.getByText('National baseline: 100');
  await expect(baselineCopy).toBeVisible();
  const before = await page.getByTestId('price-microsoft-excel').textContent();

  await page.getByTestId('shock-button').click();
  await expect(page.getByTestId('shock-banner')).toContainText(/Automation is modelled as a demand shift/);
  await expect(baselineCopy).toBeVisible();
  await expect(page.getByTestId('price-microsoft-excel')).not.toHaveText(before ?? '');

  await page.getByTestId('reset-button').click();
  await expect(page.getByTestId('shock-banner')).toHaveCount(0);
});

test('5. API failure shows a graceful error state, not a blank dashboard', async ({ page }) => {
  await page.route('**/api/market/summary', (route) => route.fulfill({ status: 500, body: 'boom' }));
  await page.goto('/');
  await expect(page.getByTestId('api-error-state')).toBeVisible();
  await expect(page.getByText('Market feed unavailable')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Retry' })).toBeVisible();
});

test('6. mobile viewport keeps the board reachable via nav', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/skills');
  await expect(page.getByTestId('big-board')).toBeVisible();
  await expect(page.getByTestId('skills-list')).toBeVisible();
});
