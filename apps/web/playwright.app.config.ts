import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests', testMatch: ['diagnostic-app.spec.ts', 'm1-*.spec.ts'], workers: 1, retries: 0,
  use: { browserName: 'chromium', headless: true, trace: 'off', screenshot: 'off', video: 'off' },
  webServer: [{
    command: '.venv/bin/python -m tools.web_harness', cwd: '../..',
    url: 'http://127.0.0.1:8031/api/health', timeout: 30000, reuseExistingServer: false,
    stdout: 'ignore', stderr: 'pipe',
  }, {
    command: 'node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 4179 --strictPort', cwd: '.',
    url: 'http://127.0.0.1:4179/tests/fixtures/m1-t6/', timeout: 30000, reuseExistingServer: false,
    stdout: 'ignore', stderr: 'pipe',
  }],
});
