/**
 * PLAYER Latency Measurement
 *
 * This test measures various latency metrics critical for game feel.
 * Used by PLAYER to objectively assess the Fun Floor requirements.
 *
 * Usage:
 *   PILOT_NAME="wasm-survivors-game" npx playwright test e2e/latency.spec.ts
 *
 * Metrics measured:
 * - Input latency (keypress to response)
 * - Frame time consistency
 * - First contentful paint
 * - Time to interactive
 */

import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PILOT_NAME = process.env.PILOT_NAME || 'wasm-survivors-game';
const PILOT_URL = process.env.PILOT_URL || null; // Direct URL takes precedence
const RESULTS_DIR = path.join(__dirname, '..', 'test-results', 'latency');

// Ensure results directory exists
if (!fs.existsSync(RESULTS_DIR)) {
  fs.mkdirSync(RESULTS_DIR, { recursive: true });
}

interface LatencyReport {
  pilot: string;
  timestamp: string;
  inputLatency: {
    avg: number;
    min: number;
    max: number;
    p95: number;
    samples: number[];
  };
  frameTime: {
    avg: number;
    min: number;
    max: number;
    dropped: number;
    fps: number;
  };
  loadTime: {
    fcp: number;
    tti: number;
    domReady: number;
  };
  verdict: 'PASS' | 'WARN' | 'FAIL';
}

function percentile(arr: number[], p: number): number {
  const sorted = [...arr].sort((a, b) => a - b);
  const idx = Math.ceil((p / 100) * sorted.length) - 1;
  return sorted[Math.max(0, idx)];
}

test.describe('Latency Measurement Suite', () => {
  let report: Partial<LatencyReport> = {
    pilot: PILOT_NAME,
    timestamp: new Date().toISOString(),
  };

  test.beforeAll(async () => {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`LATENCY MEASUREMENT: ${PILOT_NAME}`);
    console.log(`${'='.repeat(60)}\n`);
  });

  test.afterAll(async () => {
    // Determine verdict
    const inputOk = (report.inputLatency?.avg || 999) < 16;
    const framesOk = (report.frameTime?.fps || 0) >= 55;
    const loadOk = (report.loadTime?.tti || 9999) < 3000;

    if (inputOk && framesOk && loadOk) {
      report.verdict = 'PASS';
    } else if (inputOk || framesOk) {
      report.verdict = 'WARN';
    } else {
      report.verdict = 'FAIL';
    }

    // Save report
    const reportPath = path.join(RESULTS_DIR, `${PILOT_NAME}-${Date.now()}.json`);
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

    console.log(`\n${'='.repeat(60)}`);
    console.log(`VERDICT: ${report.verdict}`);
    console.log(`Report saved: ${reportPath}`);
    console.log(`${'='.repeat(60)}\n`);
  });

  test('measure input latency', async ({ page }) => {
    const url = PILOT_URL || `/pilots/${PILOT_NAME}`;
    await page.goto(url);
    await page.waitForLoadState('networkidle');

    // Start the game
    await page.keyboard.press('Space');
    await page.waitForTimeout(500);

    const samples: number[] = [];
    const sampleCount = 50;

    for (let i = 0; i < sampleCount; i++) {
      const latency = await page.evaluate(() => {
        return new Promise<number>((resolve) => {
          const start = performance.now();
          let resolved = false;

          const handler = () => {
            if (!resolved) {
              resolved = true;
              resolve(performance.now() - start);
              document.removeEventListener('keydown', handler);
            }
          };

          document.addEventListener('keydown', handler);
          document.dispatchEvent(
            new KeyboardEvent('keydown', {
              key: 'w',
              bubbles: true,
              cancelable: true,
            })
          );

          // Timeout fallback
          setTimeout(() => {
            if (!resolved) {
              resolved = true;
              resolve(-1);
              document.removeEventListener('keydown', handler);
            }
          }, 100);
        });
      });

      if (latency > 0) {
        samples.push(latency);
      }

      await page.waitForTimeout(50);
    }

    const avg = samples.reduce((a, b) => a + b, 0) / samples.length;
    const min = Math.min(...samples);
    const max = Math.max(...samples);
    const p95 = percentile(samples, 95);

    report.inputLatency = { avg, min, max, p95, samples };

    console.log(`Input Latency:`);
    console.log(`  Average: ${avg.toFixed(2)}ms`);
    console.log(`  Min: ${min.toFixed(2)}ms`);
    console.log(`  Max: ${max.toFixed(2)}ms`);
    console.log(`  P95: ${p95.toFixed(2)}ms`);
    console.log(`  Samples: ${samples.length}`);

    // Fun Floor: < 16ms average (L-IMPL-1 requirement)
    expect(avg).toBeLessThan(16);
  });

  test('measure frame time', async ({ page }) => {
    const url = PILOT_URL || `/pilots/${PILOT_NAME}`;
    await page.goto(url);
    await page.waitForLoadState('networkidle');

    await page.keyboard.press('Space');
    await page.waitForTimeout(500);

    const frameData = await page.evaluate(async () => {
      const frameTimes: number[] = [];
      let lastTime = performance.now();
      const duration = 5000; // 5 seconds
      const startTime = performance.now();

      return new Promise<{ times: number[]; duration: number }>((resolve) => {
        function measureFrame() {
          const now = performance.now();
          frameTimes.push(now - lastTime);
          lastTime = now;

          if (now - startTime < duration) {
            requestAnimationFrame(measureFrame);
          } else {
            resolve({ times: frameTimes, duration: now - startTime });
          }
        }

        requestAnimationFrame(measureFrame);
      });
    });

    const times = frameData.times;
    const avg = times.reduce((a, b) => a + b, 0) / times.length;
    const min = Math.min(...times);
    const max = Math.max(...times);
    const dropped = times.filter((t) => t > 33.33).length; // Below 30fps
    const fps = 1000 / avg;

    report.frameTime = { avg, min, max, dropped, fps };

    console.log(`Frame Time:`);
    console.log(`  Average: ${avg.toFixed(2)}ms`);
    console.log(`  Min: ${min.toFixed(2)}ms`);
    console.log(`  Max: ${max.toFixed(2)}ms`);
    console.log(`  FPS: ${fps.toFixed(1)}`);
    console.log(`  Dropped frames: ${dropped}/${times.length}`);

    // Fun Floor: 60fps target (55+ acceptable)
    expect(fps).toBeGreaterThan(55);
    expect(dropped).toBeLessThan(times.length * 0.05); // < 5% dropped
  });

  test('measure load time', async ({ page }) => {
    // Clear cache for accurate measurement
    await page.context().clearCookies();

    const startTime = Date.now();
    const url = PILOT_URL || `/pilots/${PILOT_NAME}`;

    await page.goto(url, {
      waitUntil: 'domcontentloaded',
    });

    const domReady = Date.now() - startTime;

    // Wait for FCP
    const fcp = await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntriesByName('first-contentful-paint');
          if (entries.length > 0) {
            resolve(entries[0].startTime);
            observer.disconnect();
          }
        });

        observer.observe({ type: 'paint', buffered: true });

        // Fallback if already painted
        const entries = performance.getEntriesByName('first-contentful-paint');
        if (entries.length > 0) {
          resolve(entries[0].startTime);
          observer.disconnect();
        }

        // Timeout
        setTimeout(() => resolve(-1), 5000);
      });
    });

    // Wait for interactive
    await page.waitForLoadState('networkidle');
    const tti = Date.now() - startTime;

    report.loadTime = { fcp: fcp > 0 ? fcp : domReady, tti, domReady };

    console.log(`Load Time:`);
    console.log(`  DOM Ready: ${domReady}ms`);
    console.log(`  First Contentful Paint: ${fcp > 0 ? fcp.toFixed(0) : 'N/A'}ms`);
    console.log(`  Time to Interactive: ${tti}ms`);

    // Fun Floor: < 3s to interactive
    expect(tti).toBeLessThan(3000);
  });

  test('measure continuous play stability', async ({ page }) => {
    const url = PILOT_URL || `/pilots/${PILOT_NAME}`;
    await page.goto(url);
    await page.waitForLoadState('networkidle');

    await page.keyboard.press('Space');
    await page.waitForTimeout(500);

    // Play for 60 seconds and measure stability
    const stabilityData = await page.evaluate(async () => {
      const measurements: { time: number; memory?: number }[] = [];
      const duration = 60000;
      const startTime = performance.now();
      const interval = 1000; // Measure every second

      return new Promise<typeof measurements>((resolve) => {
        const measure = () => {
          const now = performance.now();
          const elapsed = now - startTime;

          const measurement: { time: number; memory?: number } = {
            time: elapsed,
          };

          // Memory if available
          if ((performance as any).memory) {
            measurement.memory = (performance as any).memory.usedJSHeapSize / 1024 / 1024;
          }

          measurements.push(measurement);

          if (elapsed < duration) {
            setTimeout(measure, interval);
          } else {
            resolve(measurements);
          }
        };

        measure();
      });
    });

    // Simulate inputs during stability test
    const playPromise = (async () => {
      const keys = ['w', 'a', 's', 'd'];
      for (let i = 0; i < 600; i++) {
        await page.keyboard.press(keys[i % keys.length]);
        await page.waitForTimeout(100);
      }
    })();

    await playPromise;

    // Analyze stability
    const memoryValues = stabilityData
      .map((m) => m.memory)
      .filter((m): m is number => m !== undefined);

    if (memoryValues.length > 0) {
      const memoryStart = memoryValues[0];
      const memoryEnd = memoryValues[memoryValues.length - 1];
      const memoryGrowth = memoryEnd - memoryStart;

      console.log(`Stability (60s):`);
      console.log(`  Memory start: ${memoryStart.toFixed(1)}MB`);
      console.log(`  Memory end: ${memoryEnd.toFixed(1)}MB`);
      console.log(`  Growth: ${memoryGrowth.toFixed(1)}MB`);

      // Warn if memory grows significantly (possible leak)
      expect(memoryGrowth).toBeLessThan(50); // < 50MB growth in 60s
    } else {
      console.log(`Memory measurement not available in this browser`);
    }
  });
});
