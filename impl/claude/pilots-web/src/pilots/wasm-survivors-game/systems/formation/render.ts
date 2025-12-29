/**
 * THE BALL Formation System - Rendering Helpers
 *
 * Functions for rendering THE BALL formation.
 * Main rendering is in GameCanvas.tsx, these are helpers.
 */

import type { LegacyBallState } from './types';
import { getTemperatureColor, getEscapeGapColor } from './queries';

/**
 * Render THE BALL formation
 * Legacy function for compatibility - main rendering is in GameCanvas.tsx
 */
export function renderBallFormation(
  ctx: CanvasRenderingContext2D,
  state: LegacyBallState,
  gameTime: number
): void {
  if (state.phase === 'inactive') return;

  const { center, currentRadius, gapAngle, gapSize, temperature, phase } = state;

  ctx.save();

  // Draw the sphere outline (dashed during forming, solid during constrict/cooking)
  if (phase === 'forming' || phase === 'silence') {
    ctx.setLineDash([10, 10]);
  } else {
    ctx.setLineDash([]);
  }

  // Draw arc without the gap
  const gapStart = gapAngle - gapSize / 2;
  const gapEnd = gapAngle + gapSize / 2;

  // Draw first arc (before gap)
  ctx.beginPath();
  ctx.arc(center.x, center.y, currentRadius, gapEnd, gapStart + Math.PI * 2);

  // Temperature-based color
  ctx.strokeStyle = phase === 'cooking' ? '#FF3366' : '#FFD700';
  ctx.lineWidth = phase === 'cooking' ? 4 : 2;
  ctx.stroke();

  // Fill with temperature tint
  if (temperature > 40) {
    ctx.beginPath();
    ctx.arc(center.x, center.y, currentRadius, 0, Math.PI * 2);
    ctx.fillStyle = getTemperatureColor(temperature);
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
 */
export function renderLungeIndicator(
  ctx: CanvasRenderingContext2D,
  state: LegacyBallState,
  gameTime: number,
  enemies: Array<{ id: string; position: { x: number; y: number } }>
): void {
  if (!state.activeLunge) return;

  const lunge = state.activeLunge;

  // Phase-aware progress calculation
  let lungeProgress = 0;
  let showTrail = false;

  if (lunge.phase === 'windup') {
    const windupDuration = lunge.lungeStartTime > 0
      ? lunge.lungeStartTime - lunge.windupStartTime
      : 600; // Default windup duration (RUN 037)
    lungeProgress = Math.min(1, (gameTime - lunge.windupStartTime) / windupDuration);
    showTrail = false;
  } else if (lunge.phase === 'lunge') {
    lungeProgress = Math.min(1, (gameTime - lunge.lungeStartTime) / lunge.duration);
    showTrail = true;
  } else if (lunge.phase === 'return') {
    lungeProgress = 1;
    showTrail = true;
  }

  if (showTrail) {
    // Draw lunge trail (red streak from formation to player)
    ctx.globalAlpha = lunge.phase === 'return' ? 0.3 : 0.6;
    ctx.strokeStyle = '#FF0000';
    ctx.lineWidth = 6;
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.moveTo(lunge.startPos.x, lunge.startPos.y);

    // Current lunge position
    const easedProgress = 1 - Math.pow(1 - lungeProgress, 3);
    const currentX = lunge.startPos.x + (lunge.targetPos.x - lunge.startPos.x) * easedProgress;
    const currentY = lunge.startPos.y + (lunge.targetPos.y - lunge.startPos.y) * easedProgress;
    ctx.lineTo(currentX, currentY);
    ctx.stroke();
  }

  // Draw windup indicator (charging ring around bee during windup)
  if (lunge.phase === 'windup') {
    const bee = enemies.find(e => e.id === lunge.beeId);
    if (bee) {
      const chargeProgress = lungeProgress;
      // Pulsing ring that grows
      ctx.globalAlpha = 0.7;
      ctx.strokeStyle = '#FF4400';
      ctx.lineWidth = 3 + chargeProgress * 2;
      ctx.beginPath();
      ctx.arc(bee.position.x, bee.position.y, 15 + chargeProgress * 10, 0, Math.PI * 2 * chargeProgress);
      ctx.stroke();

      // Inner glow
      ctx.globalAlpha = 0.4 * chargeProgress;
      ctx.fillStyle = '#FF6600';
      ctx.beginPath();
      ctx.arc(bee.position.x, bee.position.y, 10 + chargeProgress * 5, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // Draw impact ring at target (pulsing) - only during lunge phase
  if (lunge.phase === 'lunge') {
    const impactPulse = 1 + Math.sin(gameTime * 0.02) * 0.3;
    ctx.globalAlpha = 0.5 + lungeProgress * 0.5;
    ctx.strokeStyle = '#FF4444';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(lunge.targetPos.x, lunge.targetPos.y, 15 * impactPulse, 0, Math.PI * 2);
    ctx.stroke();
  }

  // Draw "!" warning above the lunging bee (during windup and lunge)
  if (lunge.phase === 'windup' || lunge.phase === 'lunge') {
    const bee = enemies.find(e => e.id === lunge.beeId);
    if (bee) {
      ctx.globalAlpha = 1;
      ctx.fillStyle = lunge.phase === 'windup' ? '#FFAA00' : '#FF0000';
      ctx.font = 'bold 20px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('!', bee.position.x, bee.position.y - 20);
    }
  }

  ctx.globalAlpha = 1;
}
