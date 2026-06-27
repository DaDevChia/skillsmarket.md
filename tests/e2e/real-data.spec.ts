import { expect, test } from '@playwright/test';

test('interactive chart has range + zoom controls and a hover readout', async ({ page }) => {
  await page.goto('/skills/machine-learning');
  await expect(page.getByTestId('interactive-chart')).toBeVisible();
  await expect(page.getByTestId('history-chart')).toBeVisible();
  for (const id of ['chart-range-30', 'chart-range-90', 'chart-range-all', 'chart-zoom-in', 'chart-zoom-out']) {
    await expect(page.getByTestId(id)).toBeVisible();
  }
  await page.getByTestId('chart-range-30').click();
  await page.getByTestId('chart-zoom-in').click();
  // Hover the chart -> the readout shows a value.
  const box = await page.getByTestId('history-chart').boundingBox();
  await page.mouse.move(box!.x + box!.width * 0.5, box!.y + box!.height * 0.5);
  await expect(page.getByTestId('chart-readout')).toContainText(/pts|pan/);
});

test('skill detail shows live market evidence and SkillsFuture course sections', async ({ page }) => {
  await page.goto('/skills/python');
  await expect(page.getByTestId('live-evidence')).toBeVisible();
  await expect(page.getByTestId('skill-courses')).toBeVisible();
});

test('add a skill on the board: known skill navigates to its quote', async ({ page }) => {
  await page.goto('/skills');
  await expect(page.getByTestId('add-skill')).toBeVisible();
  await page.getByTestId('add-skill-input').fill('Python');
  await page.getByTestId('research-skill-button').click();
  await expect(page).toHaveURL(/\/skills\/python$/);
  await expect(page.getByTestId('skill-detail-page')).toBeVisible();
});

test('add an unknown skill returns a clearly-labelled result (research off in test)', async ({ page }) => {
  await page.goto('/skills');
  await page.getByTestId('add-skill-input').fill('Zzqq Nonexistent Skill 9000');
  await page.getByTestId('research-skill-button').click();
  await expect(page.getByTestId('research-result')).toBeVisible();
  // Research is opt-in; disabled in tests -> honest message, never a fake number.
  await expect(page.getByTestId('research-disabled')).toBeVisible();
});

test('sources page shows real ingestion status', async ({ page }) => {
  await page.goto('/sources');
  await expect(page.getByTestId('ingestion-status')).toBeVisible();
  await expect(page.getByTestId('ingestion-status')).toContainText(/MyCareersFuture/);
  await expect(page.getByTestId('ingestion-status')).toContainText(/SkillsFuture/);
});
