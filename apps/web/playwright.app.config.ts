import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests', testMatch: ['diagnostic-app.spec.ts', 'm1-*.spec.ts'], workers: 1, retries: 0,
  use: { browserName: 'chromium', headless: true, trace: 'off', screenshot: 'off', video: 'off' },
  webServer: {
    command: '.venv/bin/python -m tools.web_harness', cwd: '../..',
    url: 'http://127.0.0.1:8031/api/health', timeout: 30000, reuseExistingServer: false,
    stdout: 'ignore', stderr: 'pipe',
  },
});
