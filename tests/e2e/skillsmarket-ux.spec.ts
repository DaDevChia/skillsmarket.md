import { expect, test } from '@playwright/test';

// Resume flow now lives on its own /resume route. Landing has a clear CTA there.

const PASTE_TEXT =
  'Operations analyst using Python, Data Analysis, Microsoft Excel, dashboards, scheduling and ' +
  'administration for weekly reporting.';

test('1. landing CTA navigates to the resume page', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'The Singapore skills exchange.' })).toBeVisible();
  await page.getByTestId('cta-analyze-resume').click();
  await expect(page).toHaveURL(/\/resume$/);
  await expect(page.getByRole('heading', { name: /Upload resume/ })).toBeVisible();
  await expect(page.getByTestId('resume-paste-box')).toBeVisible();
  await expect(page.getByTestId('example-profile-admin-to-data')).toBeVisible();
});

test('2. example profile analysis shows skill index and next move', async ({ page }) => {
  await page.goto('/resume');
  await page.getByTestId('example-profile-admin-to-data').click();
  await expect(page.getByTestId('personal-skill-index')).toBeVisible();
  await expect(page.getByText('100 = Singapore median skill price.')).toBeVisible();
  await expect(page.getByTestId('next-move-card')).toContainText(/Add|Learn|Acquire/);
});

test('3. pasted resume text is analysed', async ({ page }) => {
  await page.goto('/resume');
  await page.getByTestId('resume-paste-box').fill(PASTE_TEXT);
  await page.getByTestId('analyze-text-button').click();
  await expect(page.getByTestId('personal-skill-index')).toBeVisible();
  await expect(page.getByTestId('resume-analysis')).toContainText('Python');
});

test('4. uploading a .txt resume is analysed', async ({ page }) => {
  await page.goto('/resume');
  await page.getByTestId('resume-upload-input').setInputFiles({
    name: 'resume.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from('Admin executive with Microsoft Excel, scheduling and customer service.'),
  });
  await expect(page.getByTestId('personal-skill-index')).toBeVisible();
});

test('5. an unsupported upload shows a clear error, not a silent failure', async ({ page }) => {
  await page.goto('/resume');
  await page.getByTestId('resume-upload-input').setInputFiles({
    name: 'photo.png',
    mimeType: 'image/png',
    buffer: Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a]),
  });
  await expect(page.getByTestId('resume-error')).toBeVisible();
  await expect(page.getByTestId('resume-error')).toContainText(/TXT|PDF|DOCX|paste/i);
});

test('6. baseline 100 is explained on the result', async ({ page }) => {
  await page.goto('/resume');
  await page.getByTestId('example-profile-fresh-grad-analytics').click();
  await expect(page.getByText('100 = Singapore median skill price.')).toBeVisible();
  await expect(page.getByText('Above 100 means scarcer. Below 100 means common.')).toBeVisible();
});

test('7. methodology lives on its own page', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('nav-methodology').click();
  await expect(page).toHaveURL(/\/methodology$/);
  await expect(page.getByTestId('methodology-page')).toBeVisible();
  await expect(page.getByTestId('methodology-terms')).toContainText('Frozen divisor');
});

test('8. skills globe renders after analysis', async ({ page }) => {
  await page.goto('/resume');
  await page.getByTestId('example-profile-admin-to-data').click();
  const globe = page.getByTestId('skills-globe');
  await expect(globe).toBeVisible();
  await expect(globe.locator('canvas')).toBeVisible();
});

test('9. clicking a skill opens a detail card', async ({ page }) => {
  await page.goto('/resume');
  await page.getByTestId('example-profile-admin-to-data').click();
  await expect(page.getByTestId('personal-skill-index')).toBeVisible();
  await page.getByTestId('below-baseline-skills').locator('button.skill-row').first().click();
  await expect(page.getByTestId('skill-detail')).toBeVisible();
  await expect(page.getByTestId('skill-detail')).toContainText(/points|Unpriced/);
});

test('10. captures terminal landing screenshot', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /Singapore skills exchange/ })).toBeVisible();
  await page.screenshot({ path: 'test-results/ux-screenshots/landing.png', fullPage: true });
});

test('11. captures analysed resume screenshot', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto('/resume');
  await page.getByTestId('example-profile-admin-to-data').click();
  await expect(page.getByTestId('personal-skill-index')).toBeVisible();
  await expect(page.getByTestId('skills-globe').locator('canvas')).toBeVisible();
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'test-results/ux-screenshots/analyzed-resume.png', fullPage: true });
});

test('12. captures methodology page screenshot', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto('/methodology');
  await expect(page.getByTestId('methodology-page')).toBeVisible();
  await page.screenshot({ path: 'test-results/ux-screenshots/methodology.png', fullPage: true });
});
