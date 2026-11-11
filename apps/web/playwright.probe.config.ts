import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: 'bootstrap-probe.spec.ts',
  workers: 1,
  retries: 0,
  use: { browserName: 'chromium', headless: true, trace: 'off', screenshot: 'off', video: 'off' },
});
