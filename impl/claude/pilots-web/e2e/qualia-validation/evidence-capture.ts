/**
 * Evidence Capture Utilities — Run 038
 *
 * Comprehensive evidence capture for WITNESS phase qualia verification.
 * Captures screenshots, metrics, and state snapshots for post-run analysis.
 *
 * Philosophy: "The player is the proof. The joy is the witness."
 *
 * @see coordination/.player.session.md for qualia verification matrix
 */

import type { Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// =============================================================================
// Types
// =============================================================================

export interface EvidenceMetadata {
  timestamp: number;
  iteration: number;
  qualia: string;
  description: string;
  gameState?: Record<string, unknown>;
  apexState?: Record<string, unknown>;
  passed?: boolean;
}

export interface EvidenceBundle {
  id: string;
  qualia: string;
  files: string[];
  metadata: EvidenceMetadata;
}

// =============================================================================
// Configuration
// =============================================================================

const EVIDENCE_BASE = 'test-results/run038-evidence';

export const EVIDENCE_DIRS = {
  screenshots: `${EVIDENCE_BASE}/screenshots`,
  sequences: `${EVIDENCE_BASE}/sequences`,
  metrics: `${EVIDENCE_BASE}/metrics`,
};

// =============================================================================
// Directory Management
// =============================================================================

/**
 * Ensure all evidence directories exist
 */
export function ensureEvidenceDirs(): void {
  Object.values(EVIDENCE_DIRS).forEach((dir) => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

/**
 * Get timestamped filename
 */
function getTimestampedFilename(prefix: string, ext: string): string {
  const timestamp = Date.now();
  return `${prefix}-${timestamp}.${ext}`;
}

// =============================================================================
// Screenshot Capture
// =============================================================================

/**
 * Capture a single screenshot with metadata
 */
export async function captureScreenshot(
  page: Page,
  qualia: string,
  description: string
): Promise<EvidenceBundle> {
  ensureEvidenceDirs();

  const id = `${qualia}-${Date.now()}`;
  const screenshotPath = path.join(EVIDENCE_DIRS.screenshots, `${id}.png`);
  const metadataPath = path.join(EVIDENCE_DIRS.screenshots, `${id}.json`);

  // Capture screenshot
  await page.screenshot({ path: screenshotPath, fullPage: false });

  // Capture game state if available
  const gameState = await page.evaluate(() => {
    return window.DEBUG_GET_GAME_STATE?.() ?? null;
  });

  const apexState = await page.evaluate(() => {
    return (window as any).DEBUG_GET_APEX_STATE?.() ?? null;
  });

  const metadata: EvidenceMetadata = {
    timestamp: Date.now(),
    iteration: 6, // Current iteration
    qualia,
    description,
    gameState: gameState as Record<string, unknown> ?? undefined,
    apexState: apexState as Record<string, unknown> ?? undefined,
  };

  // Save metadata
  fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));

  return {
    id,
    qualia,
    files: [screenshotPath, metadataPath],
    metadata,
  };
}

/**
 * Capture a sequence of screenshots over time
 */
export async function captureSequence(
  page: Page,
  qualia: string,
  count: number,
  intervalMs: number,
  description: string
): Promise<EvidenceBundle> {
  ensureEvidenceDirs();

  const id = `${qualia}-seq-${Date.now()}`;
  const seqDir = path.join(EVIDENCE_DIRS.sequences, id);
  fs.mkdirSync(seqDir, { recursive: true });

  const files: string[] = [];

  for (let i = 0; i < count; i++) {
    const framePath = path.join(seqDir, `frame-${i.toString().padStart(3, '0')}.png`);
    await page.screenshot({ path: framePath });
    files.push(framePath);

    if (i < count - 1) {
      await page.waitForTimeout(intervalMs);
    }
  }

  const metadata: EvidenceMetadata = {
    timestamp: Date.now(),
    iteration: 6,
    qualia,
    description,
  };

  const metadataPath = path.join(seqDir, 'metadata.json');
  fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
  files.push(metadataPath);

  return {
    id,
    qualia,
    files,
    metadata,
  };
}

// =============================================================================
// Metrics Capture
// =============================================================================

export interface MetricsSnapshot {
  timestamp: number;
  inputLatency?: number;
  frameTime?: number;
  enemyCount?: number;
  playerHealth?: number;
  wave?: number;
  chargeLevel?: number;
  missPenaltyPhase?: string | null;
}

/**
 * Capture performance metrics
 */
export async function captureMetrics(page: Page, qualia: string): Promise<EvidenceBundle> {
  ensureEvidenceDirs();

  const id = `${qualia}-metrics-${Date.now()}`;
  const metricsPath = path.join(EVIDENCE_DIRS.metrics, `${id}.json`);

  // Gather metrics
  const metrics = await page.evaluate(() => {
    const gameState = window.DEBUG_GET_GAME_STATE?.();
    const apexState = (window as any).DEBUG_GET_APEX_STATE?.();

    return {
      timestamp: Date.now(),
      enemyCount: gameState?.enemies?.length ?? 0,
      playerHealth: gameState?.player?.health ?? 0,
      wave: gameState?.wave ?? 0,
      chargeLevel: apexState?.chargeLevel ?? 0,
      missPenaltyPhase: apexState?.missPenaltyPhase ?? null,
    };
  });

  const metadata: EvidenceMetadata = {
    timestamp: Date.now(),
    iteration: 6,
    qualia,
    description: 'Metrics snapshot',
    gameState: metrics as Record<string, unknown>,
  };

  fs.writeFileSync(metricsPath, JSON.stringify({ metrics, metadata }, null, 2));

  return {
    id,
    qualia,
    files: [metricsPath],
    metadata,
  };
}

// =============================================================================
// Qualia-Specific Evidence
// =============================================================================

/**
 * Capture evidence for D1: Cursor-aim clarity
 */
export async function captureAimEvidence(page: Page): Promise<EvidenceBundle> {
  // Move mouse to specific position
  await page.mouse.move(500, 300);

  // Start charging
  await page.keyboard.down('Space');
  await page.waitForTimeout(300);

  const bundle = await captureScreenshot(page, 'D1-aim', 'Direction indicator during charge');

  await page.keyboard.up('Space');
  return bundle;
}

/**
 * Capture evidence for D2: Charge scaling
 */
export async function captureChargeEvidence(page: Page): Promise<EvidenceBundle[]> {
  const bundles: EvidenceBundle[] = [];

  // Capture at different charge levels
  const levels = [0.2, 0.5, 0.8, 1.0];

  for (const level of levels) {
    await page.keyboard.down('Space');
    await page.waitForTimeout(level * 800); // Scale to max charge time

    bundles.push(await captureScreenshot(page, `D2-charge-${Math.round(level * 100)}`, `Charge at ${Math.round(level * 100)}%`));

    await page.keyboard.up('Space');
    await page.waitForTimeout(500); // Wait for cooldown
  }

  return bundles;
}

/**
 * Capture evidence for D4: Miss penalty phases
 */
export async function captureMissPenaltyEvidence(page: Page): Promise<EvidenceBundle> {
  // Force a miss (dash into empty space)
  await page.keyboard.down('Space');
  await page.waitForTimeout(800);
  await page.keyboard.up('Space');

  // Capture sequence during penalty phases
  return captureSequence(page, 'D4-penalty', 10, 150, 'Miss penalty phase progression');
}

/**
 * Capture evidence for DD-038-3: Afterimages
 */
export async function captureAfterimageEvidence(page: Page): Promise<EvidenceBundle> {
  // Spawn enemy and charge dash
  await page.evaluate(() => {
    (window as any).DEBUG_SET_INVINCIBLE?.(true);
    window.DEBUG_SPAWN?.('worker', { x: 400, y: 300 });
  });

  await page.waitForTimeout(200);

  // Capture sequence during strike
  await page.keyboard.down('Space');
  await page.waitForTimeout(600);

  const bundle = await captureSequence(page, 'D3-afterimage', 8, 30, 'Afterimage trail during strike');

  await page.keyboard.up('Space');
  return bundle;
}

// =============================================================================
// Evidence Summary
// =============================================================================

export interface EvidenceSummary {
  runId: string;
  timestamp: number;
  bundles: EvidenceBundle[];
  qualiaVerified: string[];
  qualiaFailed: string[];
}

/**
 * Generate evidence summary for a run
 */
export function generateSummary(bundles: EvidenceBundle[]): EvidenceSummary {
  const qualiaSet = new Set<string>();
  bundles.forEach((b) => qualiaSet.add(b.qualia));

  return {
    runId: 'run-038',
    timestamp: Date.now(),
    bundles,
    qualiaVerified: Array.from(qualiaSet),
    qualiaFailed: [], // Will be populated during WITNESS
  };
}

/**
 * Save evidence summary
 */
export function saveSummary(summary: EvidenceSummary): string {
  ensureEvidenceDirs();
  const summaryPath = path.join(EVIDENCE_BASE, `summary-${Date.now()}.json`);
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
  return summaryPath;
}
