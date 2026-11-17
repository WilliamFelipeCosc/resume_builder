import { expect, test } from '@playwright/test';

test('synthetic form and dialog support keyboard, Escape and focus restoration', async ({ page }) => {
  await page.goto('http://127.0.0.1:4179/tests/fixtures/m1-t6/');
  const trigger = page.getByRole('button', { name: 'Open dialog' });
  await page.keyboard.press('Tab');
  await expect(trigger).toBeFocused();
  await page.keyboard.press('Enter');
  const dialog = page.getByRole('dialog', { name: 'Example form' });
  await expect(dialog).toBeVisible();
  const input = page.getByRole('textbox', { name: 'Name' });
  await expect(input).toBeFocused();
  await page.keyboard.type('Synthetic');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('button', { name: 'Save' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.getByLabel('Saved value')).toHaveText('Synthetic');
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden();
  await expect(trigger).toBeFocused();
  await page.keyboard.press('Enter');
  await page.getByRole('button', { name: 'Close' }).focus();
  await page.keyboard.press('Enter');
  await expect(dialog).toBeHidden();
  await expect(trigger).toBeFocused();
});
