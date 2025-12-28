/**
 * Debug API Helpers for Qualia Validation
 *
 * Helpers to interact with the game's DEBUG_* window functions.
 * These match the existing API defined in src/lib/debug-types.ts.
 *
 * Philosophy: The player who cannot see cannot judge. Debug APIs give the PLAYER eyes.
 *
 * @see src/lib/debug-types.ts for type definitions
 * @see src/pilots/wasm-survivors-game/hooks/useDebugAPI.ts for implementation
 */

// =============================================================================
// Types (matching src/lib/debug-types.ts)
// =============================================================================

export interface DebugEnemy {
  id: string;
  type: string;
  position: { x: number; y: number };
  health: number;
  behaviorState: 'chase' | 'telegraph' | 'attack' | 'recovery';
  telegraphProgress?: number;
}

export interface DebugPlayer {
  position: { x: number; y: number };
  health: number;
  maxHealth: number;
  invincible: boolean;
  upgrades: string[];
}

export interface DebugDamageEvent {
  enemyType: string;
  attackType: string;
  damage: number;
  timestamp: number;
}

export interface DebugTelegraph {
  enemyId: string;
  type: 'lunge' | 'charge' | 'stomp' | 'projectile' | 'combo';
  progress: number;
  position: { x: number; y: number };
  radius?: number;
  direction?: { x: number; y: number };
}

export interface DebugGameState {
  wave: number;
  score: number;
  gameTime: number;
  enemies: DebugEnemy[];
  player: DebugPlayer;
  telegraphs: DebugTelegraph[];
  lastDamage: DebugDamageEvent | null;
}

// =============================================================================
// Window API (matches existing implementation)
// =============================================================================

declare global {
  interface Window {
    // State queries
    DEBUG_GET_GAME_STATE?: () => DebugGameState;
    DEBUG_GET_ENEMIES?: () => DebugEnemy[];
    DEBUG_GET_PLAYER?: () => DebugPlayer;
    DEBUG_GET_LAST_DAMAGE?: () => DebugDamageEvent | null;
    DEBUG_GET_TELEGRAPHS?: () => DebugTelegraph[];

    // Control functions
    DEBUG_SPAWN?: (type: string, position: { x: number; y: number }) => void;
    DEBUG_SET_INVINCIBLE?: (invincible: boolean) => void;
    DEBUG_SKIP_WAVE?: () => void;
    DEBUG_KILL_ALL_ENEMIES?: () => void;
    DEBUG_LEVEL_UP?: () => void;
  }
}

// =============================================================================
// Helper Functions for Tests
// =============================================================================

/**
 * Wait for debug API to be available
 */
export async function waitForDebugApi(page: import('@playwright/test').Page, timeout = 5000): Promise<boolean> {
  try {
    await page.waitForFunction(
      () => typeof window.DEBUG_GET_GAME_STATE === 'function',
      { timeout }
    );
    return true;
  } catch {
    return false;
  }
}

/**
 * Get current game state (or null if not available)
 */
export async function getGameState(page: import('@playwright/test').Page): Promise<DebugGameState | null> {
  return page.evaluate(() => window.DEBUG_GET_GAME_STATE?.() ?? null);
}

/**
 * Get all enemies
 */
export async function getEnemies(page: import('@playwright/test').Page): Promise<DebugEnemy[]> {
  return page.evaluate(() => window.DEBUG_GET_ENEMIES?.() ?? []);
}

/**
 * Get player state
 */
export async function getPlayer(page: import('@playwright/test').Page): Promise<DebugPlayer | null> {
  return page.evaluate(() => window.DEBUG_GET_PLAYER?.() ?? null);
}

/**
 * Get active telegraphs
 */
export async function getTelegraphs(page: import('@playwright/test').Page): Promise<DebugTelegraph[]> {
  return page.evaluate(() => window.DEBUG_GET_TELEGRAPHS?.() ?? []);
}

/**
 * Spawn an enemy at position
 */
export async function spawnEnemy(
  page: import('@playwright/test').Page,
  type: string,
  position: { x: number; y: number } = { x: 400, y: 300 }
): Promise<void> {
  await page.evaluate(
    ({ type, position }) => window.DEBUG_SPAWN?.(type, position),
    { type, position }
  );
}

/**
 * Set player invincibility
 */
export async function setInvincible(page: import('@playwright/test').Page, value: boolean): Promise<void> {
  await page.evaluate((v) => window.DEBUG_SET_INVINCIBLE?.(v), value);
}

/**
 * Skip to next wave
 */
export async function skipWave(page: import('@playwright/test').Page): Promise<void> {
  await page.evaluate(() => window.DEBUG_SKIP_WAVE?.());
}

/**
 * Kill all enemies
 */
export async function killAllEnemies(page: import('@playwright/test').Page): Promise<void> {
  await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
}

/**
 * Trigger level up
 */
export async function triggerLevelUp(page: import('@playwright/test').Page): Promise<void> {
  await page.evaluate(() => window.DEBUG_LEVEL_UP?.());
}

/**
 * Get last damage event
 */
export async function getLastDamage(page: import('@playwright/test').Page): Promise<DebugDamageEvent | null> {
  return page.evaluate(() => window.DEBUG_GET_LAST_DAMAGE?.() ?? null);
}

/**
 * Calculate intensity based on game state (helper for tests)
 */
export function calculateIntensity(state: DebugGameState | null): number {
  if (!state) return 0;

  const healthFactor = 1 - (state.player.health / state.player.maxHealth);
  const enemyFactor = Math.min(1, state.enemies.length / 20);
  const waveFactor = Math.min(1, state.wave / 10);

  return healthFactor * 0.4 + enemyFactor * 0.3 + waveFactor * 0.3;
}

// =============================================================================
// State Machine Query Helpers
// =============================================================================

/**
 * Get enemy behavior state for state machine validation
 */
export async function getEnemyBehaviorState(
  page: import('@playwright/test').Page,
  enemyId: string
): Promise<string> {
  const enemies = await getEnemies(page);
  const enemy = enemies.find(e => e.id === enemyId);
  return enemy?.behaviorState ?? 'unknown';
}

/**
 * Wait for any enemy to enter a specific state
 */
export async function waitForEnemyState(
  page: import('@playwright/test').Page,
  targetState: 'chase' | 'telegraph' | 'attack' | 'recovery',
  timeout = 5000
): Promise<DebugEnemy | null> {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    const enemies = await getEnemies(page);
    const match = enemies.find(e => e.behaviorState === targetState);
    if (match) return match;
    await page.waitForTimeout(50);
  }

  return null;
}

/**
 * Wait for a telegraph to appear
 */
export async function waitForTelegraph(
  page: import('@playwright/test').Page,
  timeout = 5000
): Promise<DebugTelegraph | null> {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    const telegraphs = await getTelegraphs(page);
    if (telegraphs.length > 0) return telegraphs[0];
    await page.waitForTimeout(50);
  }

  return null;
}

// =============================================================================
// Evidence Capture Helpers
// =============================================================================

/**
 * Capture a screenshot with metadata
 */
export async function captureEvidence(
  page: import('@playwright/test').Page,
  name: string,
  outputDir: string
): Promise<string> {
  const state = await getGameState(page);
  const timestamp = Date.now();
  const filename = `${name}-${timestamp}.png`;
  const fullPath = `${outputDir}/${filename}`;

  await page.screenshot({ path: fullPath });

  // Also save state metadata
  const metadataPath = `${outputDir}/${name}-${timestamp}.json`;
  const fs = await import('fs');
  fs.writeFileSync(metadataPath, JSON.stringify({ state, timestamp }, null, 2));

  return fullPath;
}

/**
 * Capture a sequence of screenshots over time
 */
export async function captureSequence(
  page: import('@playwright/test').Page,
  name: string,
  outputDir: string,
  count: number,
  intervalMs: number
): Promise<string[]> {
  const paths: string[] = [];

  for (let i = 0; i < count; i++) {
    const path = await captureEvidence(page, `${name}-${i}`, outputDir);
    paths.push(path);
    if (i < count - 1) {
      await page.waitForTimeout(intervalMs);
    }
  }

  return paths;
}
