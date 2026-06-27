import { expect, test } from '@playwright/test';

// The full (~100) skills list is sortable by every column and searchable.

test('skills list sorts numerically and alphabetically', async ({ page }) => {
  await page.goto('/skills');
  const list = page.getByTestId('skills-list');
  await expect(list).toBeVisible();
  await expect.poll(() => list.locator('.skills-trow').count()).toBeGreaterThanOrEqual(100);

  // Default sort is price descending → prices are non-increasing.
  const pricesDesc = (await list.locator('.skills-trow .td.price').allInnerTexts()).map(Number);
  expect(pricesDesc).toEqual([...pricesDesc].sort((a, b) => b - a));

  // Toggle to ascending.
  await page.getByTestId('sort-price').click();
  const pricesAsc = (await list.locator('.skills-trow .td.price').allInnerTexts()).map(Number);
  expect(pricesAsc).toEqual([...pricesAsc].sort((a, b) => a - b));

  // Sort by name ascending → names are alphabetical.
  await page.getByTestId('sort-name').click();
  const names = await list.locator('.skills-trow .td.name').allInnerTexts();
  expect(names).toEqual([...names].sort((a, b) => a.localeCompare(b)));
});

test('sort headers expose aria-sort state', async ({ page }) => {
  await page.goto('/skills');
  await page.getByTestId('sort-symbol').click();
  await expect(page.getByTestId('sort-symbol')).toHaveAttribute('aria-sort', 'ascending');
  await page.getByTestId('sort-symbol').click();
  await expect(page.getByTestId('sort-symbol')).toHaveAttribute('aria-sort', 'descending');
});

test('skills list is searchable', async ({ page }) => {
  await page.goto('/skills');
  const list = page.getByTestId('skills-list');
  const rows = list.locator('.skills-trow');
  await expect(list).toBeVisible();
  await expect.poll(() => rows.count()).toBeGreaterThanOrEqual(100);
  const total = await rows.count();

  await page.getByTestId('skills-search').fill('cloud');
  await expect.poll(() => rows.count()).toBeLessThan(total);
  const count = await rows.count();
  expect(count).toBeGreaterThan(0);
  // Every visible row matches the query in name or sector.
  for (const text of await rows.allInnerTexts()) {
    expect(text.toLowerCase()).toContain('cloud');
  }
});

test('skills list filters by sector', async ({ page }) => {
  await page.goto('/skills');
  const list = page.getByTestId('skills-list');
  const rows = list.locator('.skills-trow');
  await expect.poll(() => rows.count()).toBeGreaterThanOrEqual(100);
  const total = await rows.count();
  await page.getByTestId('sector-filter').selectOption('Cybersecurity');
  await expect.poll(() => rows.count()).toBeLessThan(total);
  for (const text of await rows.allInnerTexts()) {
    expect(text).toContain('Cybersecurity');
  }
});
