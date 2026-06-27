import { expect, Page, test } from '@playwright/test';

// Guards against iPhone clipping across every page: nothing overflows the
// viewport horizontally, and explanatory text wraps rather than getting cut off.

const MOBILE = { width: 360, height: 780 };

async function expectNoHorizontalOverflow(page: Page) {
  const m = await page.evaluate(() => ({
    docScroll: document.documentElement.scrollWidth,
    docClient: document.documentElement.clientWidth,
    bodyScroll: document.body.scrollWidth,
  }));
  expect(m.docScroll, 'document should not scroll horizontally').toBeLessThanOrEqual(m.docClient + 1);
  expect(m.bodyScroll, 'body content should not exceed the viewport').toBeLessThanOrEqual(m.docClient + 1);
}

async function expectTextNotClipped(page: Page, selector: string) {
  for (const handle of await page.locator(selector).all()) {
    if (!(await handle.isVisible())) continue;
    const clipped = await handle.evaluate((el) => el.scrollWidth - el.clientWidth);
    expect(clipped, `${selector} should not be horizontally clipped`).toBeLessThanOrEqual(2);
  }
}

test('landing has no overflow on mobile', async ({ page }) => {
  await page.setViewportSize(MOBILE);
  await page.goto('/');
  await expect(page.getByTestId('top-quotes')).toBeVisible();
  await expectNoHorizontalOverflow(page);
  await expectTextNotClipped(page, '.hero-sub');
  await expectTextNotClipped(page, '.quote-name');
});

test('skills board has no overflow on mobile (cards)', async ({ page }) => {
  await page.setViewportSize(MOBILE);
  await page.goto('/skills');
  await expect(page.getByTestId('skills-list')).toBeVisible();
  const row = page.getByTestId('skill-list-row-data-analysis');
  await expect(row).toBeVisible();
  expect((await row.boundingBox())!.height).toBeGreaterThanOrEqual(44);
  await expectNoHorizontalOverflow(page);
});

test('skill detail has no overflow on mobile', async ({ page }) => {
  await page.setViewportSize(MOBILE);
  await page.goto('/skills/machine-learning');
  await expect(page.getByTestId('skill-detail-page')).toBeVisible();
  await expect(page.getByTestId('history-chart')).toBeVisible();
  await expectNoHorizontalOverflow(page);
  await expectTextNotClipped(page, '.analyst-note p');
  await expectTextNotClipped(page, '.method-list li em');
});

test('sources + methodology have no overflow on mobile', async ({ page }) => {
  await page.setViewportSize(MOBILE);
  await page.goto('/sources');
  await expect(page.getByTestId('sources-page')).toBeVisible();
  await expectNoHorizontalOverflow(page);
  await expectTextNotClipped(page, '.source-use');

  await page.goto('/methodology');
  await expect(page.getByTestId('methodology-page')).toBeVisible();
  await expectNoHorizontalOverflow(page);
  await expectTextNotClipped(page, '.method-list li em');
});

test('resume results have no overflow on mobile', async ({ page }) => {
  await page.setViewportSize(MOBILE);
  await page.goto('/resume');
  await page.getByTestId('example-profile-admin-to-data').click();
  await expect(page.getByTestId('personal-skill-index')).toBeVisible();
  await expectNoHorizontalOverflow(page);
  await expectTextNotClipped(page, '.next-move-why');
});

test('touch targets meet ~44px on mobile', async ({ page }) => {
  await page.setViewportSize(MOBILE);
  await page.goto('/resume');
  for (const id of ['example-profile-admin-to-data', 'analyze-text-button', 'upload-resume-button']) {
    const box = await page.getByTestId(id).boundingBox();
    expect(box!.height, `${id} tap target`).toBeGreaterThanOrEqual(40);
  }
});
