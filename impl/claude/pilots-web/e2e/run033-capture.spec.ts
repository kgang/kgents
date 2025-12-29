/**
 * Run 033 Evidence Capture
 *
 * Captures gameplay screenshots to verify visual enhancements.
 */

import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const EVIDENCE_DIR = path.join(__dirname, '..', 'evidence');

// Ensure evidence directory exists
if (!fs.existsSync(EVIDENCE_DIR)) {
  fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
}

test('capture Run 033 gameplay evidence', async ({ page }) => {
  test.setTimeout(60000);

  // Navigate to game
  await page.goto('/pilots/wasm-survivors-game');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(500);

  // Screenshot 1: Menu
  await page.screenshot({
    path: path.join(EVIDENCE_DIR, 'run033-1-menu.png'),
    fullPage: true
  });
  console.log('✓ Captured menu');

  // Click BEGIN RAID
  const button = page.locator('button:has-text("BEGIN RAID")');
  await expect(button).toBeVisible();
  await button.click();
  console.log('✓ Clicked BEGIN RAID');

  // Wait for game to start (enemies should spawn)
  await page.waitForTimeout(2000);
  await page.screenshot({
    path: path.join(EVIDENCE_DIR, 'run033-2-early.png'),
    fullPage: true
  });
  console.log('✓ Captured early gameplay');

  // Play for a bit with movement
  for (let i = 0; i < 50; i++) {
    await page.keyboard.press(['w', 'a', 's', 'd'][i % 4]);
    await page.waitForTimeout(80);
  }

  await page.screenshot({
    path: path.join(EVIDENCE_DIR, 'run033-3-mid.png'),
    fullPage: true
  });
  console.log('✓ Captured mid gameplay');

  // Continue playing
  for (let i = 0; i < 100; i++) {
    await page.keyboard.press(['w', 'a', 's', 'd'][i % 4]);
    await page.waitForTimeout(50);
  }

  await page.screenshot({
    path: path.join(EVIDENCE_DIR, 'run033-4-late.png'),
    fullPage: true
  });
  console.log('✓ Captured late gameplay');

  // Check for death screen or upgrade screen
  const hasDeathScreen = await page.locator('text=KILLED BY').isVisible().catch(() => false);
  const hasUpgradeScreen = await page.locator('text=Choose an upgrade').isVisible().catch(() => false);

  if (hasDeathScreen) {
    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'run033-5-death.png'),
      fullPage: true
    });
    console.log('✓ Captured death screen');
  }

  if (hasUpgradeScreen) {
    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'run033-5-upgrade.png'),
      fullPage: true
    });
    console.log('✓ Captured upgrade screen');
  }

  console.log('\n✓ Evidence capture complete! Check evidence/ directory');
});
