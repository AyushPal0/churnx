import { defineConfig, devices } from '@playwright/test';
import process from 'node:process';

const python = process.platform === 'win32' ? '.venv\\Scripts\\python.exe' : '.venv/bin/python';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  workers: 1,
  timeout: 30000,
  use: { baseURL: 'http://127.0.0.1:15173', trace: 'retain-on-failure' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    { command: `${python} -m uvicorn backend.main:app --host 127.0.0.1 --port 18080`, url: 'http://127.0.0.1:18080/health', reuseExistingServer: false, timeout: 30000, env: { DATABASE_PATH: 'runtime/e2e-predictions.db' } },
    { command: 'node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 15173 --strictPort', url: 'http://127.0.0.1:15173', reuseExistingServer: false, timeout: 30000, env: { CHURNX_API_PROXY: 'http://127.0.0.1:18080', VITE_API_URL: '/api' } },
  ],
});
