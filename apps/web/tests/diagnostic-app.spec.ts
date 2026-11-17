import { expect, test } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { connect } from 'node:net';

const ORIGIN = 'http://127.0.0.1:8031';
const info = () => JSON.parse(readFileSync('/tmp/rb-web-harness.json', 'utf8')) as { socket: string; workerPid: number; apiPid: number; harnessPid: number };
const ticket = () => new Promise<string>((resolve, reject) => {
  const socket = connect(info().socket);
  let payload = '';
  socket.on('data', (chunk) => { payload += chunk; });
  socket.on('end', () => { resolve(JSON.parse(payload).ticket); });
  socket.on('error', reject);
});

test('FND-15 real API process restart invalidates browser cookie and permits new local opening', async ({ page }) => {
  await page.goto(ORIGIN + '/#bootstrap=' + await ticket());
  await expect(page.getByRole('button', { name: 'Executar diagnóstico de teste' })).toBeEnabled();
  await page.getByRole('button', { name: 'Executar diagnóstico de teste' }).click();
  await expect(page.getByRole('status')).toHaveText('succeeded', { timeout: 10000 });
  const persistedId = await page.getByTestId('execution-id').textContent();
  const oldPid = info().apiPid;
  process.kill(info().harnessPid, 'SIGHUP');
  await expect.poll(() => info().apiPid).not.toBe(oldPid);
  await expect.poll(async () => {
    try { return (await page.request.get(ORIGIN + '/api/health')).status(); }
    catch { return 0; }
  }).toBe(200);
  await page.reload();
  await expect(page.getByRole('button')).toHaveCount(0);
  expect((await page.request.get(ORIGIN + '/api/diagnostics/latest')).status()).toBe(401);
  await page.goto(ORIGIN + '/#bootstrap=' + await ticket());
  await expect(page.getByRole('button', { name: 'Executar diagnóstico de teste' })).toBeEnabled();
  await expect(page.getByRole('status')).toHaveText('succeeded');
  await expect(page.getByTestId('execution-id')).toHaveText(persistedId!);
});

test('FND-03/04/13/14 definitive same-origin Web/API/Redis/Worker fixture', async ({ page }) => {
  await page.goto(ORIGIN);
  await expect(page.getByText('Abra pelo comando local para iniciar uma sessão autorizada.')).toBeVisible();
  await expect(page.getByRole('button')).toHaveCount(0);
  expect((await page.request.get(ORIGIN + '/api/diagnostics/latest')).status()).toBe(401);
  const bootstrap = await ticket();
  await page.goto(ORIGIN + '/#bootstrap=' + bootstrap);
  const button = page.getByRole('button', { name: 'Executar diagnóstico de teste' });
  await expect(button).toBeEnabled();
  expect(new URL(page.url()).hash).toBe('');
  expect((await page.request.get(ORIGIN + '/tests/fixtures/m1-t6/')).status()).toBe(404);
  expect(await page.evaluate(() => document.cookie)).toBe('');
  expect(await page.evaluate(() => localStorage.length)).toBe(0);
  const cookies = await page.context().cookies();
  expect(cookies.find((cookie) => cookie.name === 'resume_session')).toMatchObject({ httpOnly: true, sameSite: 'Strict', expires: -1 });
  expect((await page.request.post(ORIGIN + '/api/session/bootstrap', { data: { ticket: bootstrap }, headers: { Origin: ORIGIN } })).status()).toBe(401);
  process.kill(info().workerPid, 'SIGSTOP');
  try {
    await button.click();
    await expect(button).toBeDisabled();
    await expect(page.getByRole('status')).toHaveText(/pending|queued/);
  } finally { process.kill(info().workerPid, 'SIGCONT'); }
  await expect(page.getByRole('status')).toHaveText('succeeded', { timeout: 10000 });
  await expect(page.getByText('diagnostic_completed · m0-v1')).toBeVisible();
  const id = await page.getByTestId('execution-id').textContent();
  expect(id).toMatch(/^[0-9a-f-]{36}$/);
  await expect(button).toBeEnabled();
  await page.reload();
  await expect(page.getByTestId('execution-id')).toHaveText(id!);
  await expect(page.getByRole('status')).toHaveText('succeeded');
  const response = await page.request.get(ORIGIN + '/api/diagnostics/latest');
  expect((await response.json()).execution).toMatchObject({ id, status: 'succeeded', attemptCount: 1, result: { message: 'diagnostic_completed', fixtureVersion: 'm0-v1' }, error: null, deliveryWarning: null });
  await page.context().clearCookies();
  await page.reload();
  await expect(page.getByRole('button')).toHaveCount(0);
  await expect(page.getByTestId('execution-id')).toHaveCount(0);
});
