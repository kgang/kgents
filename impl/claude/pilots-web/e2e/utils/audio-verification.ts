/**
 * Audio Verification Test Utilities
 *
 * Helper functions for PLAYER to verify audio behavior in wasm-survivors-game.
 * Uses the DEBUG_AUDIO_* API exposed on window when ?debug=true.
 *
 * V1 Focus: noise_silence pole (is there audio contrast between loud and silent moments?)
 *
 * @see src/pilots/wasm-survivors-game/systems/audio.ts
 */

import { Page, expect } from '@playwright/test';

// =============================================================================
// Types
// =============================================================================

/**
 * Audio state snapshot from DEBUG API
 */
export interface AudioState {
  /** Whether audio is enabled and initialized */
  isEnabled: boolean;
  /** Master volume (0-1) */
  masterVolume: number;
  /** Current buzz volume from coordination (0-1) */
  buzzVolume: number;
  /** Current mood ambient setting */
  currentMood: string | null;
  /** Whether audio context is running (vs suspended) */
  contextState: 'running' | 'suspended' | 'closed' | 'unavailable';
}

/**
 * Audio event logged by the DEBUG API
 */
export interface AudioEvent {
  /** Event type (kill, damage, dash, xp, levelup, ball-phase, death, buzz, ambient) */
  type: string;
  /** Timestamp relative to session start (ms) */
  timestamp: number;
  /** Additional data depending on event type */
  data?: Record<string, unknown>;
}

/**
 * Audio level measurement
 */
export interface AudioLevel {
  /** Current level (0-255 scale) */
  level: number;
  /** Peak level in recent window */
  peak: number;
  /** Whether any audio is currently playing */
  isPlaying: boolean;
}

// =============================================================================
// Initialization
// =============================================================================

/**
 * Check if audio DEBUG API is available
 */
export async function hasAudioDebugAPI(page: Page): Promise<boolean> {
  return page.evaluate(() => {
    return typeof (window as any).DEBUG_GET_AUDIO_STATE === 'function';
  });
}

/**
 * Initialize audio for testing (requires user gesture simulation).
 * Returns true if audio was successfully initialized.
 */
export async function initAudioForTest(page: Page): Promise<boolean> {
  // First check if API is available
  const hasAPI = await hasAudioDebugAPI(page);
  if (!hasAPI) {
    console.warn('Audio DEBUG API not available');
    return false;
  }

  // Simulate user gesture by clicking
  await page.click('body', { force: true });

  // Initialize audio via game's initAudio (triggered by user gesture click above)
  // The audio system auto-initializes on first sound trigger after user gesture
  const result = await page.evaluate(() => {
    // Check if audio is already enabled
    const state = (window as any).DEBUG_GET_AUDIO_STATE?.();
    return state?.isEnabled === true;
  });

  return result === true;
}

// =============================================================================
// State Queries
// =============================================================================

/**
 * Get current audio state snapshot
 */
export async function getAudioState(page: Page): Promise<AudioState> {
  const hasAPI = await hasAudioDebugAPI(page);
  if (!hasAPI) {
    return {
      isEnabled: false,
      masterVolume: 0,
      buzzVolume: 0,
      currentMood: null,
      contextState: 'unavailable',
    };
  }

  return page.evaluate(() => {
    const state = (window as any).DEBUG_GET_AUDIO_STATE?.();
    return state || {
      isEnabled: false,
      masterVolume: 0,
      buzzVolume: 0,
      currentMood: null,
      contextState: 'unavailable',
    };
  });
}

/**
 * Get current audio output level (0-255 scale).
 * Uses AnalyserNode if available, otherwise estimates from recent events.
 */
export async function getAudioLevel(page: Page): Promise<number> {
  const hasAPI = await hasAudioDebugAPI(page);
  if (!hasAPI) return 0;

  return page.evaluate(() => {
    const level = (window as any).DEBUG_GET_AUDIO_LEVEL?.();
    return typeof level === 'number' ? level : 0;
  });
}

/**
 * Get recent audio events from the log
 */
export async function getAudioLog(page: Page): Promise<AudioEvent[]> {
  const hasAPI = await hasAudioDebugAPI(page);
  if (!hasAPI) return [];

  return page.evaluate(() => {
    const log = (window as any).DEBUG_GET_AUDIO_LOG?.();
    return Array.isArray(log) ? log : [];
  });
}

/**
 * Clear the audio event log
 */
export async function clearAudioLog(page: Page): Promise<void> {
  const hasAPI = await hasAudioDebugAPI(page);
  if (!hasAPI) return;

  await page.evaluate(() => {
    (window as any).DEBUG_CLEAR_AUDIO_LOG?.();
  });
}

// =============================================================================
// Waiting & Polling
// =============================================================================

/**
 * Wait for audio to play (level exceeds threshold).
 * Polls until audio level is above threshold or timeout.
 */
export async function waitForAudio(
  page: Page,
  options: { timeout?: number; threshold?: number } = {}
): Promise<void> {
  const { timeout = 5000, threshold = 10 } = options;

  const hasAPI = await hasAudioDebugAPI(page);
  if (!hasAPI) {
    throw new Error('Audio DEBUG API not available - cannot wait for audio');
  }

  const startTime = Date.now();
  while (Date.now() - startTime < timeout) {
    const level = await getAudioLevel(page);
    if (level >= threshold) {
      return;
    }
    await page.waitForTimeout(50);
  }

  throw new Error(`Audio level did not exceed ${threshold} within ${timeout}ms`);
}

/**
 * Wait for a specific audio event type to appear in log.
 */
export async function waitForAudioEvent(
  page: Page,
  eventType: string,
  options: { timeout?: number; since?: number } = {}
): Promise<AudioEvent> {
  const { timeout = 5000, since = 0 } = options;

  const hasAPI = await hasAudioDebugAPI(page);
  if (!hasAPI) {
    throw new Error('Audio DEBUG API not available - cannot wait for audio event');
  }

  const startTime = Date.now();
  while (Date.now() - startTime < timeout) {
    const log = await getAudioLog(page);
    const event = log.find(
      (e) => e.type === eventType && e.timestamp > since
    );
    if (event) {
      return event;
    }
    await page.waitForTimeout(50);
  }

  throw new Error(`Audio event "${eventType}" did not occur within ${timeout}ms`);
}

// =============================================================================
// Assertions
// =============================================================================

/**
 * Assert that audio is silent (level below threshold).
 */
export async function assertSilence(
  page: Page,
  threshold: number = 5
): Promise<void> {
  const level = await getAudioLevel(page);
  expect(
    level,
    `Expected silence (level < ${threshold}) but got level ${level}`
  ).toBeLessThan(threshold);
}

/**
 * Assert that audio is playing (level above threshold).
 */
export async function assertAudioPlaying(
  page: Page,
  threshold: number = 10
): Promise<void> {
  const level = await getAudioLevel(page);
  expect(
    level,
    `Expected audio playing (level >= ${threshold}) but got level ${level}`
  ).toBeGreaterThanOrEqual(threshold);
}

/**
 * Assert audio contrast between two phases (V1 verification).
 *
 * This is the core V1 verification for the noise_silence pole:
 * loud moments should be detectably louder than silent moments.
 *
 * @param page - Playwright page
 * @param loudPhase - Async function that triggers the loud phase
 * @param silentPhase - Async function that triggers the silent phase
 * @param minContrast - Minimum level difference required (default 20)
 * @returns Contrast data for logging/evidence
 */
export async function assertAudioContrast(
  page: Page,
  loudPhase: () => Promise<void>,
  silentPhase: () => Promise<void>,
  minContrast: number = 20
): Promise<{ loudLevel: number; silentLevel: number; contrast: number }> {
  // Measure loud phase
  await loudPhase();
  await page.waitForTimeout(100); // Allow audio to stabilize
  const loudLevel = await getAudioLevel(page);

  // Measure silent phase
  await silentPhase();
  await page.waitForTimeout(100);
  const silentLevel = await getAudioLevel(page);

  const contrast = loudLevel - silentLevel;

  expect(
    contrast,
    `Expected audio contrast >= ${minContrast}, got ${contrast} (loud: ${loudLevel}, silent: ${silentLevel})`
  ).toBeGreaterThanOrEqual(minContrast);

  return { loudLevel, silentLevel, contrast };
}

// =============================================================================
// High-Level Test Helpers
// =============================================================================

/**
 * Capture audio evidence during a gameplay action.
 * Returns level samples and events logged during the action.
 */
export async function captureAudioEvidence(
  page: Page,
  action: () => Promise<void>,
  options: { duration?: number; sampleRate?: number } = {}
): Promise<{
  samples: { time: number; level: number }[];
  events: AudioEvent[];
  peakLevel: number;
  avgLevel: number;
}> {
  const { duration = 2000, sampleRate = 50 } = options;

  await clearAudioLog(page);
  const samples: { time: number; level: number }[] = [];
  const startTime = Date.now();

  // Start the action
  const actionPromise = action();

  // Sample audio levels
  while (Date.now() - startTime < duration) {
    const level = await getAudioLevel(page);
    samples.push({ time: Date.now() - startTime, level });
    await page.waitForTimeout(sampleRate);
  }

  await actionPromise;

  const events = await getAudioLog(page);
  const levels = samples.map((s) => s.level);
  const peakLevel = Math.max(...levels);
  const avgLevel = levels.reduce((a, b) => a + b, 0) / levels.length;

  return { samples, events, peakLevel, avgLevel };
}

/**
 * Test helper to skip test if audio API unavailable (graceful degradation).
 */
export async function skipIfNoAudioAPI(
  page: Page,
  test: { skip: () => void }
): Promise<boolean> {
  const hasAPI = await hasAudioDebugAPI(page);
  if (!hasAPI) {
    console.log('Skipping test: Audio DEBUG API not available');
    test.skip();
    return true;
  }
  return false;
}

/**
 * Get audio state summary for logging.
 */
export async function getAudioSummary(page: Page): Promise<string> {
  const state = await getAudioState(page);
  const level = await getAudioLevel(page);
  const log = await getAudioLog(page);

  return [
    `Audio State:`,
    `  Enabled: ${state.isEnabled}`,
    `  Context: ${state.contextState}`,
    `  Master Volume: ${state.masterVolume}`,
    `  Buzz Volume: ${state.buzzVolume}`,
    `  Current Level: ${level}`,
    `  Recent Events: ${log.length}`,
    `  Event Types: ${[...new Set(log.map((e) => e.type))].join(', ')}`,
  ].join('\n');
}
