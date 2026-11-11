import { test, expect } from '@playwright/test';
import { spawn, type ChildProcess } from 'node:child_process';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { createConnection } from 'node:net';
import { once } from 'node:events';

const root = resolve(import.meta.dirname, '../../..');

async function start(runtime: string, port = 0) {
  const process = spawn(join(root, '.venv/bin/python'), [
    join(root, 'tools/bootstrap_probe/probe.py'), '--runtime', runtime, '--port', String(port),
  ], { stdio: ['ignore', 'pipe', 'pipe'] });
  let logs = '';
  let errors = '';
  process.stdout.on('data', (chunk) => { logs += chunk.toString(); });
  process.stderr.on('data', (chunk) => { errors += chunk.toString(); });
  const origin = await new Promise<string>((accept, reject) => {
    const timeout = setTimeout(() => reject(new Error('Probe startup timeout')), 5000);
    process.stdout.on('data', () => {
      for (const line of logs.split('\n').filter(Boolean)) {
        const value = JSON.parse(line);
        if (value.origin) { clearTimeout(timeout); accept(value.origin); }
      }
    });
    process.on('exit', () => { clearTimeout(timeout); reject(new Error(`Probe exited: ${errors}`)); });
  });
  return { process, origin, logs: () => logs + errors };
}

async function stop(process: ChildProcess) {
  const done = once(process, 'exit');
  process.kill('SIGTERM');
  await done;
}

async function ticket(runtime: string): Promise<string> {
  return new Promise((accept, reject) => {
    const peer = createConnection(join(runtime, 'bootstrap.sock'));
    let body = '';
    peer.on('data', (chunk) => { body += chunk.toString(); });
    peer.on('end', () => accept(JSON.parse(body).ticket));
    peer.on('error', reject);
  });
}

test('T4 real Chromium accepts session, cleans fragment, rejects replay and restart', async ({ page, context, browser }) => {
  const directory = await mkdtemp(join(tmpdir(), 'rb-probe-'));
  const runtime = join(directory, 'runtime');
  let probe = await start(runtime);
  try {
    const value = await ticket(runtime);
    const requestUrls: string[] = [];
    page.on('request', (request) => requestUrls.push(request.url()));
    await page.goto(`${probe.origin}/#bootstrap=${value}`);
    await expect(page.locator('#status')).toHaveText('Authorized');
    expect(new URL(page.url()).hash).toBe('');
    expect(await page.evaluate(() => document.cookie)).toBe('');
    const cookies = await context.cookies();
    expect(cookies).toHaveLength(1);
    expect(cookies[0]).toMatchObject({ name: 'probe', httpOnly: true, sameSite: 'Strict', path: '/', expires: -1 });
    expect(await page.evaluate(() => localStorage.length)).toBe(0);
    expect(requestUrls.every((url) => !url.includes(value))).toBe(true);
    expect((await page.request.post(`${probe.origin}/bootstrap`, { headers: { Origin: probe.origin }, data: { ticket: value } })).status()).toBe(401);
    await page.reload();
    await expect(page.locator('#status')).toHaveText('Authorized');
    const oldLogs = probe.logs();
    expect(oldLogs.includes(value)).toBe(false);
    expect(oldLogs.includes(cookies[0].value)).toBe(false);
    const port = Number(new URL(probe.origin).port);
    await stop(probe.process);
    probe = await start(runtime, port);
    await page.reload();
    await expect(page.locator('#status')).toHaveText('Unauthorized');
    console.log(`T4 browser ${browser.version()}; Linux Chromium headless; session cookie and restart PASS`);
  } finally {
    await stop(probe.process);
    await rm(directory, { recursive: true });
  }
});
