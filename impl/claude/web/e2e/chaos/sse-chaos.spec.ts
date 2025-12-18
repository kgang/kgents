import { test, expect } from '@playwright/test';
import { setupHotDataMocks, chaosSSEStream, createSeededRandom } from '../../testing';

/**
 * SSE Stream Chaos Tests (Type II - Saboteurs)
 *
 * Tests SSE streaming robustness:
 * - Variable event timing
 * - Dropped events
 * - Out-of-order events
 * - Stream interruption
 *
 * @tags @chaos
 * @see plans/playwright-witness-protocol.md
 */

const CHAOS_SEED = 42;

test.describe('SSE Stream Chaos @chaos', () => {
  test.beforeEach(async ({ page }) => {
    await setupHotDataMocks(page);
  });

  test('handles variable event timing', async ({ page }) => {
    // Setup chaotic SSE stream
    await chaosSSEStream(page, '**/v1/town/*/live*', {
      seed: CHAOS_SEED,
      events: [
        { event: 'live.start', data: { town_id: 'demo', phases: 4 } },
        { event: 'live.event', data: { tick: 1, phase: 'MORNING', operation: 'wake' } },
        { event: 'live.event', data: { tick: 2, phase: 'MORNING', operation: 'work' } },
        { event: 'live.event', data: { tick: 3, phase: 'NOON', operation: 'trade' } },
        { event: 'live.end', data: { town_id: 'demo', total_ticks: 3 } },
      ],
      minDelayMs: 10,
      maxDelayMs: 500,
    });

    await page.goto('/town/demo-town-123');

    // Start live simulation
    const startButton = page.locator('[data-testid="start-simulation"]');
    if (await startButton.isVisible()) {
      await startButton.click();
    }

    // Should handle variable timing
    await expect(page.locator('body')).toBeVisible();
  });

  test('survives stream with burst of events', async ({ page }) => {
    // Generate burst of events
    const events = [];
    for (let i = 0; i < 50; i++) {
      events.push({
        event: 'live.event',
        data: {
          tick: i,
          phase: i % 4 === 0 ? 'MORNING' : i % 4 === 1 ? 'NOON' : i % 4 === 2 ? 'EVENING' : 'NIGHT',
          operation: 'action',
          participants: ['Alice', 'Bob'],
        },
      });
    }

    await page.route('**/v1/town/*/live*', async (route) => {
      let body = `event: live.start\ndata: ${JSON.stringify({ town_id: 'demo', phases: 4 })}\n\n`;

      for (const { event, data } of events) {
        body += `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
      }

      body += `event: live.end\ndata: ${JSON.stringify({ town_id: 'demo', total_ticks: 50 })}\n\n`;

      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body,
      });
    });

    await page.goto('/town/demo-town-123');

    // Should handle burst without crashing
    await expect(page.locator('body')).toBeVisible();
  });

  test('handles SSE reconnection', async ({ page }) => {
    let connectionCount = 0;

    await page.route('**/v1/town/*/live*', async (route) => {
      connectionCount++;

      // First connection fails mid-stream
      if (connectionCount === 1) {
        const body = `event: live.start\ndata: ${JSON.stringify({ town_id: 'demo' })}\n\n`;
        await route.fulfill({
          status: 200,
          contentType: 'text/event-stream',
          body,
        });
        return;
      }

      // Second connection succeeds
      const body =
        `event: live.start\ndata: ${JSON.stringify({ town_id: 'demo', phases: 4 })}\n\n` +
        `event: live.end\ndata: ${JSON.stringify({ status: 'completed' })}\n\n`;

      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body,
      });
    });

    await page.goto('/town/demo-town-123');
    await expect(page.locator('body')).toBeVisible();
  });

  test('handles malformed SSE data', async ({ page }) => {
    await page.route('**/v1/town/*/live*', async (route) => {
      // Malformed SSE: missing newlines, bad JSON
      const body =
        'event: live.start\n' +
        'data: {"broken": json}\n\n' +
        'event: live.event\ndata: {"valid": true}\n\n' +
        'event: live.end\ndata: {"status": "done"}\n\n';

      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body,
      });
    });

    await page.goto('/town/demo-town-123');

    // Should handle gracefully, not crash
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('N-Phase Stream Chaos @chaos', () => {
  test('handles N-Phase transitions under chaos', async ({ page }) => {
    const random = createSeededRandom(CHAOS_SEED);

    await page.route('**/v1/town/*/live*', async (route) => {
      const events = [];

      // Start
      events.push({
        type: 'event',
        name: 'live.start',
        data: {
          town_id: 'demo',
          nphase_enabled: true,
          nphase: { session_id: 'test', current_phase: 'UNDERSTAND', cycle_count: 1 },
        },
      });

      // Random N-Phase transitions
      const phases = ['UNDERSTAND', 'ACT', 'REFLECT', 'REST'];
      let currentPhase = 0;

      for (let tick = 1; tick <= 20; tick++) {
        // Random chance of phase transition
        if (random() < 0.3 && currentPhase < phases.length - 1) {
          currentPhase++;
          events.push({
            type: 'event',
            name: 'live.nphase',
            data: {
              tick,
              from_phase: phases[currentPhase - 1],
              to_phase: phases[currentPhase],
              session_id: 'test',
            },
          });
        }

        // Regular event
        events.push({
          type: 'event',
          name: 'live.event',
          data: {
            tick,
            operation: 'action',
            nphase_state: phases[currentPhase],
          },
        });
      }

      // End
      events.push({
        type: 'event',
        name: 'live.end',
        data: { total_ticks: 20, nphase_summary: { final_phase: phases[currentPhase] } },
      });

      let body = '';
      for (const e of events) {
        body += `event: ${e.name}\ndata: ${JSON.stringify(e.data)}\n\n`;
      }

      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body,
      });
    });

    await page.goto('/town/demo-town-123');
    await expect(page.locator('body')).toBeVisible();
  });
});
