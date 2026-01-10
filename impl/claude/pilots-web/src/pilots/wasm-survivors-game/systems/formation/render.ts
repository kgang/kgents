/**
 * THE BALL Formation System - Rendering Helpers
 *
 * Functions for rendering THE BALL formation.
 * Main rendering is in GameCanvas.tsx, these are helpers.
 */

import type { LegacyBallState, OutsidePunchState } from './types';
import { getTemperatureColor, getEscapeGapColor } from './queries';
import { BALL_OUTSIDE_PUNCH_CONFIG } from './config';

/**
 * Render THE BALL formation
 * Legacy function for compatibility - main rendering is in GameCanvas.tsx
 *
 * RUN 042: Tier 2 (secondary) balls render with dashed yellow outline only
 * - No solid knockback ring
 * - Visual warning but player can walk through boundary
 */
export function renderBallFormation(
  ctx: CanvasRenderingContext2D,
  state: LegacyBallState,
  gameTime: number
): void {
  if (state.phase === 'inactive') return;

  const { center, currentRadius, gapAngle, gapSize, temperature, phase, phaseProgress, ballTier } = state;
  const isTier2 = ballTier === 2;

  ctx.save();

  // ==========================================================================
  // RUN 039: Gathering Phase - Pre-formation indicator
  // RUN 042: Tier 2 shows "OUTER BALL" label
  // ==========================================================================
  if (phase === 'gathering') {
    // =======================================================================
    // SIMPLIFIED TELEGRAPH (RUN 043): Only 2-3 elements instead of 5-6
    // KEEP: Progress arc (timing) + Warning text (what's happening) + subtle glow
    // REMOVED: Pulsing outer ring, center crosshair, inner target ring
    // =======================================================================
    const pulse = Math.sin(gameTime * 0.008) * 0.3 + 0.7;
    // 20% opacity reduction applied to all elements
    const opacityFactor = 0.8;

    // 1. SUBTLE CENTER GLOW (replaces inner ring + crosshair)
    const glowGradient = ctx.createRadialGradient(
      center.x, center.y, 0,
      center.x, center.y, currentRadius * 0.4
    );
    glowGradient.addColorStop(0, `rgba(255, 51, 102, ${0.3 * opacityFactor})`);  // Pinkish-red danger
    glowGradient.addColorStop(1, 'rgba(255, 51, 102, 0)');
    ctx.fillStyle = glowGradient;
    ctx.beginPath();
    ctx.arc(center.x, center.y, currentRadius * 0.4, 0, Math.PI * 2);
    ctx.fill();

    // 2. PROGRESS ARC (shows timing - fills as gathering progresses)
    ctx.strokeStyle = `rgba(255, 51, 102, ${0.64 * opacityFactor})`; // Pinkish-red danger
    ctx.lineWidth = 4;
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.arc(center.x, center.y, currentRadius * 0.5, -Math.PI / 2, -Math.PI / 2 + (Math.PI * 2 * phaseProgress));
    ctx.stroke();

    // 3. WARNING TEXT (tells what's happening)
    ctx.fillStyle = `rgba(255, 200, 50, ${pulse * opacityFactor})`;
    ctx.font = 'bold 14px sans-serif';
    ctx.textAlign = 'center';
    if (isTier2) {
      ctx.fillText('OUTER BALL FORMING', center.x, center.y - currentRadius - 20);
    } else {
      ctx.fillText('BALL FORMING', center.x, center.y - currentRadius - 20);
    }

    ctx.restore();
    return;  // Don't render normal ball visuals during gathering
  }

  // ==========================================================================
  // RUN 042: Tier 2 balls render with DASHED yellow outline only (no solid ring)
  // This visually indicates "warning" but not "blocking"
  // ==========================================================================

  // Draw arc without the gap
  const gapStart = gapAngle - gapSize / 2;
  const gapEnd = gapAngle + gapSize / 2;

  if (isTier2) {
    // TIER 2 BALL: Dashed yellow warning ring (no knockback)
    // Always dashed to indicate "passable boundary"
    ctx.setLineDash([12, 8]);
    ctx.beginPath();
    ctx.arc(center.x, center.y, currentRadius, gapEnd, gapStart + Math.PI * 2);

    // Yellow/amber color with pulse effect to indicate warning
    const pulse = Math.sin(gameTime * 0.006) * 0.2 + 0.8;
    ctx.strokeStyle = `rgba(255, 200, 50, ${pulse * 0.7})`;
    ctx.lineWidth = 2;
    ctx.stroke();

    // Draw a secondary outer dashed ring for extra visibility
    ctx.beginPath();
    ctx.arc(center.x, center.y, currentRadius + 6, gapEnd, gapStart + Math.PI * 2);
    ctx.strokeStyle = `rgba(255, 150, 0, ${pulse * 0.4})`;
    ctx.lineWidth = 1;
    ctx.stroke();

    // Add "OUTER BALL" indicator
    ctx.setLineDash([]);
    ctx.fillStyle = `rgba(255, 200, 50, ${pulse * 0.6})`;
    ctx.font = 'bold 12px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('OUTER', center.x, center.y - currentRadius - 12);
  } else {
    // TIER 1 BALL: Standard solid/dashed ring with knockback
    // Draw the sphere outline (dashed during forming, solid during constrict/cooking)
    if (phase === 'forming' || phase === 'silence') {
      ctx.setLineDash([10, 10]);
    } else {
      ctx.setLineDash([]);
    }

    // Draw first arc (before gap)
    ctx.beginPath();
    ctx.arc(center.x, center.y, currentRadius, gapEnd, gapStart + Math.PI * 2);

    // Temperature-based color
    ctx.strokeStyle = phase === 'cooking' ? '#FF3366' : '#FFD700';
    ctx.lineWidth = phase === 'cooking' ? 4 : 2;
    ctx.stroke();
  }

  // Fill with temperature tint (both tiers, but tier 2 is more subtle)
  if (temperature > 40) {
    ctx.beginPath();
    ctx.arc(center.x, center.y, currentRadius, 0, Math.PI * 2);
    const tempColor = getTemperatureColor(temperature);
    // Tier 2 has reduced temperature tint opacity
    if (isTier2) {
      ctx.fillStyle = tempColor.replace(/[\d.]+\)$/, match => `${parseFloat(match) * 0.5})`);
    } else {
      ctx.fillStyle = tempColor;
    }
    ctx.fill();
  }

  // Draw escape gap highlight during constrict
  if (phase === 'constrict') {
    ctx.beginPath();
    ctx.arc(center.x, center.y, currentRadius, gapStart, gapEnd);
    ctx.strokeStyle = getEscapeGapColor(phase);
    ctx.lineWidth = 6;
    ctx.setLineDash([]);
    ctx.stroke();

    // Add pulsing glow to gap
    const pulse = Math.sin(gameTime / 200 * Math.PI) * 0.3 + 0.7;
    ctx.beginPath();
    ctx.arc(center.x, center.y, currentRadius + 8, gapStart, gapEnd);
    ctx.strokeStyle = `rgba(0, 212, 255, ${pulse * 0.5})`;
    ctx.lineWidth = 4;
    ctx.stroke();

    // Arrow pointing to gap
    const arrowAngle = gapAngle;
    const arrowRadius = currentRadius + 30;
    const arrowX = center.x + Math.cos(arrowAngle) * arrowRadius;
    const arrowY = center.y + Math.sin(arrowAngle) * arrowRadius;

    ctx.beginPath();
    ctx.moveTo(arrowX, arrowY);
    ctx.lineTo(
      arrowX - Math.cos(arrowAngle - 0.3) * 15,
      arrowY - Math.sin(arrowAngle - 0.3) * 15
    );
    ctx.lineTo(
      arrowX - Math.cos(arrowAngle + 0.3) * 15,
      arrowY - Math.sin(arrowAngle + 0.3) * 15
    );
    ctx.closePath();
    ctx.fillStyle = `rgba(0, 212, 255, ${pulse})`;
    ctx.fill();
  }

  // Draw cooking effect (screen edge burn)
  if (phase === 'cooking') {
    const burnIntensity = (temperature - 80) / 20;
    const gradient = ctx.createRadialGradient(
      center.x, center.y, currentRadius * 0.5,
      center.x, center.y, currentRadius * 2
    );
    gradient.addColorStop(0, 'rgba(255, 0, 0, 0)');
    gradient.addColorStop(1, `rgba(255, 0, 0, ${burnIntensity * 0.4})`);

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  }

  ctx.setLineDash([]);
  ctx.restore();
}

/**
 * Render lunge attack indicator
 *
 * RUN 039: Enhanced to match punch telegraph style with:
 * - Direction line showing lunge path to target
 * - Filling ring indicator during windup
 * - Prominent glow effect
 * - Growing exclamation mark
 * - Impact zone indicator
 */
export function renderLungeIndicator(
  ctx: CanvasRenderingContext2D,
  state: LegacyBallState,
  gameTime: number,
  enemies: Array<{ id: string; position: { x: number; y: number } }>
): void {
  if (!state.activeLunge) return;

  const lunge = state.activeLunge;
  const WINDUP_DURATION = 850; // Match config

  ctx.save();

  if (lunge.phase === 'windup') {
    // =======================================================================
    // SIMPLIFIED TELEGRAPH (RUN 043): Only 2 elements instead of 5-6
    // KEEP: Direction line (where attack goes) + Charging ring (timing)
    // REMOVED: Exclamation mark, inner glow, impact zone indicator
    // SIMPLIFIED: Arrow head to simple triangle
    // =======================================================================
    const elapsed = gameTime - lunge.windupStartTime;
    const progress = Math.min(1, Math.max(0, elapsed / WINDUP_DURATION));
    // 20% opacity reduction
    const opacityFactor = 0.8;

    const bee = enemies.find(e => e.id === lunge.beeId);
    if (bee) {
      const beePos = bee.position;

      // 1. DIRECTION LINE with simple arrow - Shows lunge path to target
      ctx.globalAlpha = (0.4 + progress * 0.32) * opacityFactor; // was 0.5 + 0.4
      ctx.strokeStyle = '#FF3333';  // Pure red danger (distinct from player orange)
      ctx.lineWidth = 2 + progress * 1.5;
      ctx.setLineDash([12, 6]);
      ctx.beginPath();
      ctx.moveTo(beePos.x, beePos.y);
      ctx.lineTo(lunge.targetPos.x, lunge.targetPos.y);
      ctx.stroke();
      ctx.setLineDash([]);

      // Simple triangle arrow head (simplified from complex arrow)
      const dx = lunge.targetPos.x - beePos.x;
      const dy = lunge.targetPos.y - beePos.y;
      const angle = Math.atan2(dy, dx);
      const arrowSize = 8; // fixed size, not growing
      ctx.fillStyle = '#FF3333';  // Pure red danger
      ctx.globalAlpha = 0.6 * opacityFactor;
      ctx.beginPath();
      ctx.moveTo(lunge.targetPos.x, lunge.targetPos.y);
      ctx.lineTo(
        lunge.targetPos.x - Math.cos(angle - 0.5) * arrowSize,
        lunge.targetPos.y - Math.sin(angle - 0.5) * arrowSize
      );
      ctx.lineTo(
        lunge.targetPos.x - Math.cos(angle + 0.5) * arrowSize,
        lunge.targetPos.y - Math.sin(angle + 0.5) * arrowSize
      );
      ctx.closePath();
      ctx.fill();

      // 2. CHARGING RING - Fills clockwise as windup progresses (timing indicator)
      const ringRadius = 20 + progress * 6;
      ctx.globalAlpha = 0.64 * opacityFactor; // was 0.8
      ctx.strokeStyle = '#FF3333';  // Pure red danger (distinct from player orange)
      ctx.lineWidth = 3 + progress * 1.5;
      ctx.beginPath();
      ctx.arc(beePos.x, beePos.y, ringRadius, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * progress);
      ctx.stroke();
    }
  } else if (lunge.phase === 'lunge') {
    // =======================================================================
    // LUNGE PHASE - Simplified: just motion trail (RUN 043)
    // REMOVED: Speed lines, impact ring, exclamation mark
    // =======================================================================
    const progress = Math.min(1, (gameTime - lunge.lungeStartTime) / lunge.duration);
    const easedProgress = 1 - Math.pow(1 - progress, 3);
    const opacityFactor = 0.8; // 20% reduction

    // Current position
    const currentX = lunge.startPos.x + (lunge.targetPos.x - lunge.startPos.x) * easedProgress;
    const currentY = lunge.startPos.y + (lunge.targetPos.y - lunge.startPos.y) * easedProgress;

    // Motion trail only
    ctx.globalAlpha = 0.56 * opacityFactor; // was 0.7
    ctx.strokeStyle = '#FF0000';
    ctx.lineWidth = 6;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(lunge.startPos.x, lunge.startPos.y);
    ctx.lineTo(currentX, currentY);
    ctx.stroke();

  } else if (lunge.phase === 'return') {
    // =======================================================================
    // RETURN PHASE - Fading trail (subtle)
    // =======================================================================
    const progress = Math.min(1, (gameTime - lunge.lungeStartTime) / 200);
    const opacityFactor = 0.8; // 20% reduction

    ctx.globalAlpha = 0.24 * (1 - progress) * opacityFactor; // was 0.3
    ctx.strokeStyle = '#FF0000';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(lunge.startPos.x, lunge.startPos.y);
    ctx.lineTo(lunge.targetPos.x, lunge.targetPos.y);
    ctx.stroke();
  }

  ctx.restore();
}

// =============================================================================
// RUN 039: Outside Punch Telegraph Rendering
// =============================================================================

/**
 * Render outside punch telegraph indicators
 *
 * Visual hierarchy (most to least prominent):
 * 1. Windup: Glowing bee + direction line + "!" + filling ring
 * 2. Punch: Quick flash/impact effect
 * 3. Recovery: Fading indicator
 *
 * This makes punches highly readable and dodgeable.
 */
export function renderOutsidePunchIndicators(
  ctx: CanvasRenderingContext2D,
  activePunches: OutsidePunchState[],
  enemies: Array<{ id: string; position: { x: number; y: number } }>,
  _playerPos: { x: number; y: number },  // Reserved for future use (e.g., dodge indicator)
  gameTime: number
): void {
  if (activePunches.length === 0) return;

  ctx.save();

  for (const punch of activePunches) {
    const enemy = enemies.find(e => e.id === punch.beeId);
    if (!enemy) continue;

    const elapsed = gameTime - punch.phaseStartTime;
    const beePos = enemy.position;

    if (punch.phase === 'windup') {
      // =======================================================================
      // SIMPLIFIED TELEGRAPH (RUN 043): Only 2 elements instead of 5-6
      // KEEP: Direction line (where knockback goes) + Charging ring (timing)
      // REMOVED: Exclamation mark, inner glow, range indicator
      // SIMPLIFIED: Arrow head to simple triangle
      // =======================================================================
      const progress = Math.min(1, elapsed / BALL_OUTSIDE_PUNCH_CONFIG.windupDuration);
      // 20% opacity reduction
      const opacityFactor = 0.8;

      // 1. DIRECTION LINE with simple arrow - Shows knockback direction
      const lineLength = 50;
      const lineEndX = beePos.x + punch.knockbackDir.x * lineLength;
      const lineEndY = beePos.y + punch.knockbackDir.y * lineLength;

      ctx.globalAlpha = (0.32 + progress * 0.32) * opacityFactor; // was 0.4 + 0.4
      ctx.strokeStyle = '#FF6600';
      ctx.lineWidth = 2;
      ctx.setLineDash([8, 4]);
      ctx.beginPath();
      ctx.moveTo(beePos.x, beePos.y);
      ctx.lineTo(lineEndX, lineEndY);
      ctx.stroke();
      ctx.setLineDash([]);

      // Simple triangle arrow head
      const arrowSize = 7; // slightly smaller
      const arrowAngle = Math.atan2(punch.knockbackDir.y, punch.knockbackDir.x);
      ctx.fillStyle = '#FF6600';
      ctx.globalAlpha = 0.5 * opacityFactor;
      ctx.beginPath();
      ctx.moveTo(lineEndX, lineEndY);
      ctx.lineTo(
        lineEndX - Math.cos(arrowAngle - 0.5) * arrowSize,
        lineEndY - Math.sin(arrowAngle - 0.5) * arrowSize
      );
      ctx.lineTo(
        lineEndX - Math.cos(arrowAngle + 0.5) * arrowSize,
        lineEndY - Math.sin(arrowAngle + 0.5) * arrowSize
      );
      ctx.closePath();
      ctx.fill();

      // 2. CHARGING RING - Fills clockwise as windup progresses (timing indicator)
      const ringRadius = 18 + progress * 5;
      ctx.globalAlpha = 0.56 * opacityFactor; // was 0.7
      ctx.strokeStyle = '#FF3333';  // Pure red danger (distinct from player orange)
      ctx.lineWidth = 3 + progress * 1.5;
      ctx.beginPath();
      ctx.arc(beePos.x, beePos.y, ringRadius, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * progress);
      ctx.stroke();

    } else if (punch.phase === 'punch') {
      // =======================================================================
      // PUNCH PHASE - Simplified: just brief flash (RUN 043)
      // REMOVED: Radiating impact lines (too busy)
      // =======================================================================
      const progress = Math.min(1, elapsed / BALL_OUTSIDE_PUNCH_CONFIG.punchDuration);
      const opacityFactor = 0.8; // 20% reduction

      // Simple impact flash only
      ctx.globalAlpha = (1 - progress) * opacityFactor;
      const flashRadius = 25 + progress * 15;
      const flashGradient = ctx.createRadialGradient(
        beePos.x, beePos.y, 0,
        beePos.x, beePos.y, flashRadius
      );
      flashGradient.addColorStop(0, 'rgba(255, 51, 102, 0.6)');  // Pinkish-red danger
      flashGradient.addColorStop(1, 'rgba(255, 51, 51, 0)');
      ctx.fillStyle = flashGradient;
      ctx.beginPath();
      ctx.arc(beePos.x, beePos.y, flashRadius, 0, Math.PI * 2);
      ctx.fill();

    } else if (punch.phase === 'recovery') {
      // =======================================================================
      // RECOVERY PHASE - Fading cooldown indicator (subtle)
      // =======================================================================
      const progress = Math.min(1, elapsed / BALL_OUTSIDE_PUNCH_CONFIG.recoveryDuration);
      const opacityFactor = 0.8; // 20% reduction

      // Fading ring (already subtle, just apply opacity factor)
      ctx.globalAlpha = 0.32 * (1 - progress) * opacityFactor; // was 0.4
      ctx.strokeStyle = '#888888';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(beePos.x, beePos.y, 15 + progress * 5, 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  ctx.globalAlpha = 1;
  ctx.restore();
}

/**
 * Get punch telegraph data for a specific bee
 * Useful for highlighting the bee sprite during windup
 */
export function getPunchingBeeIds(activePunches: OutsidePunchState[]): Set<string> {
  return new Set(
    activePunches
      .filter(p => p.phase === 'windup' || p.phase === 'punch')
      .map(p => p.beeId)
  );
}

/**
 * Get windup progress for a specific bee (for sprite glow effects)
 * Returns 0-1 during windup, 1 during punch, 0 otherwise
 */
export function getBeeWindupProgress(
  beeId: string,
  activePunches: OutsidePunchState[],
  gameTime: number
): number {
  const punch = activePunches.find(p => p.beeId === beeId);
  if (!punch) return 0;

  if (punch.phase === 'windup') {
    const elapsed = gameTime - punch.phaseStartTime;
    return Math.min(1, elapsed / BALL_OUTSIDE_PUNCH_CONFIG.windupDuration);
  } else if (punch.phase === 'punch') {
    return 1;
  }
  return 0;
}
