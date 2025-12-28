/**
 * PLAYER Iteration 9: Deep Qualia Testing
 * Uses debug API to test enemy variety, upgrades, and higher waves
 */
import { test, expect } from '@playwright/test';
import * as fs from 'fs';

const PILOT_URL = process.env.PILOT_URL || 'http://localhost:3006/pilots/wasm-survivors-game?debug=true';
const EVIDENCE_DIR = '/Users/kentgang/git/kgents/impl/claude/pilots-web/test-results/iteration9';

// Ensure evidence directory exists
if (!fs.existsSync(EVIDENCE_DIR)) {
  fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
}

test.describe('PLAYER Iteration 9: Deep Qualia Testing', () => {

  test('E3: Verify enemy types are visually distinct', async ({ page }) => {
    await page.goto(PILOT_URL);
    await page.waitForLoadState('networkidle');
    
    // Start game
    await page.keyboard.press('Space');
    await page.waitForTimeout(1000);
    
    // Enable invincibility
    await page.keyboard.press('i');
    await page.waitForTimeout(200);
    
    // Kill all current enemies
    await page.keyboard.press('k');
    await page.waitForTimeout(500);
    
    // Spawn each enemy type one by one and screenshot
    const enemyTypes = ['1', '2', '3', '4', '5']; // basic, fast, tank, spitter, boss
    const typeNames = ['basic', 'fast', 'tank', 'spitter', 'boss'];
    
    for (let i = 0; i < enemyTypes.length; i++) {
      await page.keyboard.press('k'); // Clear
      await page.waitForTimeout(300);
      await page.keyboard.press(enemyTypes[i]); // Spawn
      await page.waitForTimeout(500);
      await page.screenshot({ path: `${EVIDENCE_DIR}/enemy-type-${typeNames[i]}.png` });
      console.log(`Captured enemy type: ${typeNames[i]}`);
    }
    
    // Spawn all types together for comparison
    await page.keyboard.press('k');
    await page.waitForTimeout(300);
    for (const key of enemyTypes) {
      await page.keyboard.press(key);
      await page.waitForTimeout(100);
    }
    await page.waitForTimeout(500);
    await page.screenshot({ path: `${EVIDENCE_DIR}/enemy-types-all.png` });
    console.log('Captured all enemy types together');
  });

  test('U2: Verify upgrade system and build identity', async ({ page }) => {
    await page.goto(PILOT_URL);
    await page.waitForLoadState('networkidle');
    
    // Start game
    await page.keyboard.press('Space');
    await page.waitForTimeout(1000);
    
    // Enable invincibility
    await page.keyboard.press('i');
    await page.waitForTimeout(200);
    
    // Screenshot before any upgrades
    await page.screenshot({ path: `${EVIDENCE_DIR}/upgrades-0-before.png` });
    
    // Level up multiple times to see upgrade choices
    for (let level = 1; level <= 5; level++) {
      await page.keyboard.press('l'); // Level up
      await page.waitForTimeout(500);
      await page.screenshot({ path: `${EVIDENCE_DIR}/upgrade-choice-${level}.png` });
      
      // Select first upgrade
      await page.keyboard.press('1');
      await page.waitForTimeout(300);
    }
    
    // Screenshot after 5 upgrades
    await page.screenshot({ path: `${EVIDENCE_DIR}/upgrades-5-after.png` });
    console.log('Captured upgrade progression');
  });

  test('Wave progression and intensity', async ({ page }) => {
    await page.goto(PILOT_URL);
    await page.waitForLoadState('networkidle');
    
    // Start game
    await page.keyboard.press('Space');
    await page.waitForTimeout(1000);
    
    // Enable invincibility
    await page.keyboard.press('i');
    await page.waitForTimeout(200);
    
    // Progress through waves
    for (let wave = 1; wave <= 10; wave++) {
      await page.screenshot({ path: `${EVIDENCE_DIR}/wave-${wave}.png` });
      console.log(`Captured wave ${wave}`);
      
      // Get game state if debug API available
      const state = await page.evaluate(() => {
        const gs = (window as any).DEBUG_GET_GAME_STATE?.();
        return gs ? { wave: gs.wave, enemies: gs.enemies?.length } : null;
      });
      console.log(`  State: wave=${state?.wave}, enemies=${state?.enemies}`);
      
      // Skip to next wave
      await page.keyboard.press('n');
      await page.waitForTimeout(1000);
    }
  });

  test('E1: Verify telegraph visibility', async ({ page }) => {
    await page.goto(PILOT_URL);
    await page.waitForLoadState('networkidle');
    
    // Start game
    await page.keyboard.press('Space');
    await page.waitForTimeout(1000);
    
    // Enable invincibility
    await page.keyboard.press('i');
    await page.waitForTimeout(200);
    
    // Kill all and spawn a single enemy close to player
    await page.keyboard.press('k');
    await page.waitForTimeout(300);
    await page.keyboard.press('1'); // Spawn basic enemy
    
    // Wait and capture screenshots rapidly to catch telegraph state
    console.log('Watching for telegraph state...');
    for (let i = 0; i < 20; i++) {
      const enemies = await page.evaluate(() => {
        return (window as any).DEBUG_GET_ENEMIES?.() || [];
      });
      
      const telegraphs = await page.evaluate(() => {
        return (window as any).DEBUG_GET_TELEGRAPHS?.() || [];
      });
      
      if (enemies.length > 0) {
        const enemy = enemies[0];
        console.log(`  Frame ${i}: state=${enemy.behaviorState}, telegraphs=${telegraphs.length}`);
        
        if (enemy.behaviorState === 'telegraph' || telegraphs.length > 0) {
          await page.screenshot({ path: `${EVIDENCE_DIR}/telegraph-visible-${i}.png` });
          console.log('  CAPTURED TELEGRAPH!');
        }
      }
      
      await page.waitForTimeout(100);
    }
    
    // Final screenshot
    await page.screenshot({ path: `${EVIDENCE_DIR}/telegraph-final.png` });
  });

});
