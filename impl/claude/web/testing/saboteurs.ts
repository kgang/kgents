/**
 * Type II Saboteurs (Chaos Utilities)
 *
 * Chaos must be **repeatable**: uses seeded RNG.
 * These utilities simulate adverse conditions for resilience testing.
 *
 * @see plans/playwright-witness-protocol.md
 * @see docs/skills/test-patterns.md (T-gent Type II)
 */

import { Page } from '@playwright/test';

// =============================================================================
// Seeded Random Number Generator
// =============================================================================

/**
 * Mulberry32 seeded PRNG for reproducible chaos.
 * Same seed always produces same sequence.
 */
export function createSeededRandom(seed: number): () => number {
  let state = seed;
  return () => {
    state |= 0;
    state = (state + 0x6d2b79f5) | 0;
    let t = Math.imul(state ^ (state >>> 15), 1 | state);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// =============================================================================
// Viewport Chaos
// =============================================================================

/**
 * Rapidly flicker viewport between sizes.
 * Tests resize observer stability.
 */
export async function viewportFlicker(
  page: Page,
  options: {
    seed?: number;
    iterations?: number;
    minWidth?: number;
    maxWidth?: number;
    delayMs?: number;
  } = {}
): Promise<void> {
  const { seed = 42, iterations = 10, minWidth = 320, maxWidth = 1920, delayMs = 50 } = options;

  const random = createSeededRandom(seed);
  const heights = [568, 667, 800, 900, 1024, 1080];

  for (let i = 0; i < iterations; i++) {
    const width = Math.floor(random() * (maxWidth - minWidth)) + minWidth;
    const height = heights[Math.floor(random() * heights.length)];

    await page.setViewportSize({ width, height });
    await page.waitForTimeout(delayMs);
  }
}

// =============================================================================
// Network Chaos
// =============================================================================

/**
 * Add random latency to API routes.
 * Tests loading states and timeout handling.
 */
export async function latencyRoute(
  page: Page,
  pattern: string,
  options: {
    seed?: number;
    minLatencyMs?: number;
    maxLatencyMs?: number;
  } = {}
): Promise<void> {
  const { seed = 42, minLatencyMs = 100, maxLatencyMs = 3000 } = options;

  const random = createSeededRandom(seed);

  await page.route(pattern, async (route) => {
    const latency = Math.floor(random() * (maxLatencyMs - minLatencyMs)) + minLatencyMs;
    await new Promise<void>((resolve) => {
      setTimeout(resolve, latency);
    });
    await route.continue();
  });
}

/**
 * Make routes randomly fail.
 * Tests error handling and retry logic.
 */
export async function flakyRoute(
  page: Page,
  pattern: string,
  options: {
    seed?: number;
    failureProbability?: number;
    errorCodes?: number[];
  } = {}
): Promise<void> {
  const { seed = 42, failureProbability = 0.3, errorCodes = [500, 502, 503, 504] } = options;

  const random = createSeededRandom(seed);

  await page.route(pattern, async (route) => {
    if (random() < failureProbability) {
      const errorCode = errorCodes[Math.floor(random() * errorCodes.length)];
      await route.fulfill({
        status: errorCode,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: `Simulated ${errorCode} error`,
          chaos: true,
        }),
      });
      return;
    }
    await route.continue();
  });
}

/**
 * Simulate complete network disconnection and reconnection.
 * Tests offline handling and reconnection logic.
 */
export async function networkFlap(
  page: Page,
  options: {
    offlineDurationMs?: number;
    onlineDurationMs?: number;
    cycles?: number;
  } = {}
): Promise<void> {
  const { offlineDurationMs = 500, onlineDurationMs = 1000, cycles = 3 } = options;

  for (let i = 0; i < cycles; i++) {
    // Go offline
    await page.context().setOffline(true);
    await page.waitForTimeout(offlineDurationMs);

    // Go online
    await page.context().setOffline(false);
    await page.waitForTimeout(onlineDurationMs);
  }
}

/**
 * Simulate slow network (throttling).
 * Tests graceful degradation.
 */
export async function slowNetwork(
  page: Page,
  options: {
    downloadThroughput?: number; // bytes per second
    uploadThroughput?: number;
    latency?: number; // ms
  } = {}
): Promise<void> {
  const {
    downloadThroughput = 50000, // 50 KB/s (slow 3G)
    uploadThroughput = 20000,
    latency = 400,
  } = options;

  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Network.emulateNetworkConditions', {
    offline: false,
    downloadThroughput,
    uploadThroughput,
    latency,
  });
}

// =============================================================================
// Data Chaos
// =============================================================================

/**
 * Return malformed JSON from routes.
 * Tests JSON parsing error handling.
 */
export async function malformedJsonRoute(page: Page, pattern: string): Promise<void> {
  await page.route(pattern, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: '{"broken": json, missing quotes}',
    });
  });
}

/**
 * Return empty responses from routes.
 * Tests empty state handling.
 */
export async function emptyRoute(page: Page, pattern: string): Promise<void> {
  await page.route(pattern, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({}),
    });
  });
}

/**
 * Return unexpected data shapes.
 * Tests type coercion and validation.
 */
export async function unexpectedShapeRoute(
  page: Page,
  pattern: string,
  options: {
    seed?: number;
  } = {}
): Promise<void> {
  const { seed = 42 } = options;
  const random = createSeededRandom(seed);

  const shapes = [
    null,
    [],
    '',
    0,
    { completely: { different: { shape: true } } },
    [1, 2, 3, 'mixed', null],
    { __proto__: 'evil' },
  ];

  await page.route(pattern, async (route) => {
    const shape = shapes[Math.floor(random() * shapes.length)];
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(shape),
    });
  });
}

// =============================================================================
// Timing Chaos
// =============================================================================

/**
 * SSE stream with random delays between events.
 * Tests streaming UI robustness.
 */
export async function chaosSSEStream(
  page: Page,
  pattern: string,
  options: {
    seed?: number;
    events: Array<{ event: string; data: object }>;
    minDelayMs?: number;
    maxDelayMs?: number;
  }
): Promise<void> {
  const { seed = 42, events, minDelayMs = 10, maxDelayMs = 1000 } = options;
  const random = createSeededRandom(seed);

  await page.route(pattern, async (route) => {
    let body = '';

    for (const { event, data } of events) {
      const delay = Math.floor(random() * (maxDelayMs - minDelayMs)) + minDelayMs;
      // Note: In a real implementation, we'd need chunked streaming
      // For now, we batch with variable data
      body += `event: ${event}\ndata: ${JSON.stringify({ ...data, chaos_delay: delay })}\n\n`;
    }

    await route.fulfill({
      status: 200,
      contentType: 'text/event-stream',
      headers: {
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      },
      body,
    });
  });
}

// =============================================================================
// Composite Chaos
// =============================================================================

/**
 * Apply multiple chaos conditions at once.
 * The "full chaos" experience for resilience testing.
 */
export async function fullChaos(
  page: Page,
  apiPattern: string,
  options: {
    seed?: number;
  } = {}
): Promise<void> {
  const { seed = 42 } = options;

  // Layer chaos utilities with related seeds
  await flakyRoute(page, apiPattern, { seed, failureProbability: 0.2 });
  await latencyRoute(page, apiPattern, { seed: seed + 1, minLatencyMs: 100, maxLatencyMs: 2000 });

  // Viewport chaos runs in background
  // Don't await - let it run during test execution
  viewportFlicker(page, { seed: seed + 2, iterations: 5 });
}

// =============================================================================
// Chaos Report
// =============================================================================

export interface ChaosReport {
  seed: number;
  appliedChaos: string[];
  startTime: number;
  endTime?: number;
  errors: string[];
}

/**
 * Create a chaos session that tracks applied chaos for debugging.
 */
export function createChaosSession(seed: number): ChaosReport {
  return {
    seed,
    appliedChaos: [],
    startTime: Date.now(),
    errors: [],
  };
}
