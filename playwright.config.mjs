import { defineConfig, devices } from '@playwright/test';

// This suite owns a disposable loopback service. Never attach it to a saved scene.
const port = 8765;
const baseURL = `http://127.0.0.1:${port}`;

export default defineConfig({
  testDir: './tests/studio',
  testMatch: 'browser.spec.mjs',
  fullyParallel: false,
  workers: 1, // All pages intentionally share one authoritative scene service.
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  timeout: 45_000,
  // One shared scene requires serial acceptance; 57 workflows include SDK subprocesses.
  globalTimeout: 12 * 60_000,
  expect: { timeout: 10_000 },
  outputDir: 'test-results/browser',
  reporter: [['list'], ['html', { outputFolder: 'playwright-report', open: 'never' }]],
  use: {
    baseURL,
    actionTimeout: 10_000,
    navigationTimeout: 20_000,
    screenshot: 'only-on-failure',
    // Keep successful-run evidence too, rather than implying DOM tests are browser QA.
    trace: 'on',
    video: 'on',
    acceptDownloads: true,
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 1100 } } }],
  webServer: {
    command: `${process.env.STUDIO_PYTHON || 'python'} -m studio.app --ephemeral --port ${port}`,
    url: `${baseURL}/api/health`,
    reuseExistingServer: false,
    timeout: 60_000,
    gracefulShutdown: { signal: 'SIGTERM', timeout: 5_000 },
    stdout: 'pipe',
    stderr: 'pipe',
  },
});
