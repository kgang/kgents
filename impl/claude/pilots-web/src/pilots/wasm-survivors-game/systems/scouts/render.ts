/**
 * Scout Coordination System - Visual Rendering
 *
 * Renders telegraph effects for scout behaviors:
 * - Solo Flanking: Orange orbit trails, quick sting warnings
 * - Coordinated Arc: Formation lines, synchronized attack arrows
 *
 * @see PROTO_SPEC.md A2: Attributable Outcomes (telegraphs enable dodging)
 */

import type { SoloFlankTelegraph, CoordinatedTelegraph } from './types';
import { SOLO_STING_CONFIG, COORDINATED_ARC_CONFIG } from './config';

// =============================================================================
// Solo Flanking Telegraphs
// =============================================================================

/**
 * Render solo scout orbit trail and attack warning
 */
export function renderSoloFlankTelegraph(
  ctx: CanvasRenderingContext2D,
  telegraph: SoloFlankTelegraph,
  _gameTime: number  // Reserved for animation timing
): void {
  const { position, orbitTrail, attackDirection, intensityPulse, type } = telegraph;

  ctx.save();

  // ORBIT TRAIL: Fading orange positions
  if (orbitTrail.length > 1) {
    for (let i = 0; i < orbitTrail.length - 1; i++) {
      const alpha = (i / orbitTrail.length) * 0.4;
      const p = orbitTrail[i];

      ctx.globalAlpha = alpha;
      ctx.fillStyle = SOLO_STING_CONFIG.colors.orbit;
      ctx.beginPath();
      ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // APPROACHING indicator: Pulsing glow
  if (type === 'approaching') {
    const glowRadius = 20 + intensityPulse * 10;
    const gradient = ctx.createRadialGradient(
      position.x, position.y, 5,
      position.x, position.y, glowRadius
    );
    gradient.addColorStop(0, `${SOLO_STING_CONFIG.colors.telegraph}88`);
    gradient.addColorStop(1, `${SOLO_STING_CONFIG.colors.telegraph}00`);

    ctx.globalAlpha = 0.6 + intensityPulse * 0.4;
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(position.x, position.y, glowRadius, 0, Math.PI * 2);
    ctx.fill();
  }

  // STRIKING indicator: Attack direction arrow + flash
  if (type === 'striking' && attackDirection) {
    // Intense flash
    ctx.globalAlpha = 0.8 * intensityPulse;
    ctx.fillStyle = SOLO_STING_CONFIG.colors.strike;
    ctx.beginPath();
    ctx.arc(position.x, position.y, 12, 0, Math.PI * 2);
    ctx.fill();

    // Attack direction arrow
    const arrowLen = 50;
    const endX = position.x + attackDirection.x * arrowLen;
    const endY = position.y + attackDirection.y * arrowLen;

    // Motion lines (3 parallel)
    for (let i = -1; i <= 1; i++) {
      const perpX = -attackDirection.y * i * 4;
      const perpY = attackDirection.x * i * 4;

      ctx.globalAlpha = i === 0 ? 0.9 : 0.4;
      ctx.strokeStyle = SOLO_STING_CONFIG.colors.strike;
      ctx.lineWidth = i === 0 ? 3 : 1.5;

      ctx.beginPath();
      ctx.moveTo(position.x + perpX, position.y + perpY);
      ctx.lineTo(endX + perpX, endY + perpY);
      ctx.stroke();
    }

    // Arrow head
    const headLen = 12;
    const angle = Math.atan2(attackDirection.y, attackDirection.x);

    ctx.globalAlpha = 1;
    ctx.fillStyle = '#FFFFFF';
    ctx.beginPath();
    ctx.moveTo(endX, endY);
    ctx.lineTo(
      endX - headLen * Math.cos(angle - Math.PI / 6),
      endY - headLen * Math.sin(angle - Math.PI / 6)
    );
    ctx.lineTo(
      endX - headLen * Math.cos(angle + Math.PI / 6),
      endY - headLen * Math.sin(angle + Math.PI / 6)
    );
    ctx.closePath();
    ctx.fill();

    // "!" Warning above scout (shake during strike)
    const shake = (Math.random() - 0.5) * 4;
    ctx.font = 'bold 16px Arial';
    ctx.fillStyle = '#FF4400';
    ctx.textAlign = 'center';
    ctx.fillText('!', position.x + shake, position.y - 20);
  }

  ctx.restore();
}

// =============================================================================
// Coordinated Arc Telegraphs
// =============================================================================

/**
 * Render coordinated group formation and attack warnings
 */
export function renderCoordinatedTelegraph(
  ctx: CanvasRenderingContext2D,
  telegraph: CoordinatedTelegraph,
  gameTime: number
): void {
  const {
    phase,
    center,
    radius,
    scoutPositions,
    targetPositions,
    attackArrows,
    warningIntensity,
  } = telegraph;

  ctx.save();

  // Draw connection lines between scouts (shows coordination)
  if (scoutPositions.length > 1 && phase !== 'dispersing') {
    ctx.globalAlpha = 0.3 + warningIntensity * 0.3;
    ctx.strokeStyle = COORDINATED_ARC_CONFIG.colors.connection;
    ctx.lineWidth = 1;

    for (let i = 0; i < scoutPositions.length; i++) {
      const next = scoutPositions[(i + 1) % scoutPositions.length];
      ctx.beginPath();
      ctx.moveTo(scoutPositions[i].x, scoutPositions[i].y);
      ctx.lineTo(next.x, next.y);
      ctx.stroke();
    }
  }

  // POSITIONING: Show target formation positions
  if (phase === 'positioning' || phase === 'synchronized') {
    for (const target of targetPositions) {
      ctx.globalAlpha = 0.4;
      ctx.strokeStyle = COORDINATED_ARC_CONFIG.colors.gathering;
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);

      ctx.beginPath();
      ctx.arc(target.x, target.y, 10, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  }

  // SYNCHRONIZED: Pulsing formation ring
  if (phase === 'synchronized') {
    const pulse = Math.sin(gameTime / 100) * 0.2 + 0.8;
    const ringRadius = radius + 5;

    ctx.globalAlpha = warningIntensity * pulse;
    ctx.strokeStyle = COORDINATED_ARC_CONFIG.colors.synchronized;
    ctx.lineWidth = 2;
    ctx.setLineDash([8, 4]);

    ctx.beginPath();
    ctx.arc(center.x, center.y, ringRadius, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // TELEGRAPH: Attack warning arrows
  if (phase === 'telegraph' || phase === 'attacking') {
    const pulsePhase = Math.sin(gameTime / COORDINATED_ARC_CONFIG.telegraphPulseRate * Math.PI * 2);
    const intensity = phase === 'attacking' ? 1 : 0.6 + pulsePhase * 0.4;

    // Warning zone fill
    ctx.globalAlpha = warningIntensity * 0.15;
    const gradient = ctx.createRadialGradient(
      center.x, center.y, 0,
      center.x, center.y, radius
    );
    gradient.addColorStop(0, COORDINATED_ARC_CONFIG.colors.telegraph);
    gradient.addColorStop(1, 'transparent');
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(center.x, center.y, radius, 0, Math.PI * 2);
    ctx.fill();

    // Attack arrows
    for (const arrow of attackArrows) {
      const dx = arrow.to.x - arrow.from.x;
      const dy = arrow.to.y - arrow.from.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const dirX = dx / dist;
      const dirY = dy / dist;

      // Arrow line
      ctx.globalAlpha = intensity;
      ctx.strokeStyle = COORDINATED_ARC_CONFIG.colors.attackLine;
      ctx.lineWidth = 2;

      ctx.beginPath();
      ctx.moveTo(arrow.from.x, arrow.from.y);
      ctx.lineTo(arrow.to.x, arrow.to.y);
      ctx.stroke();

      // Arrow head
      const headLen = 10;
      const angle = Math.atan2(dirY, dirX);

      ctx.fillStyle = COORDINATED_ARC_CONFIG.colors.attackLine;
      ctx.beginPath();
      ctx.moveTo(arrow.to.x, arrow.to.y);
      ctx.lineTo(
        arrow.to.x - headLen * Math.cos(angle - Math.PI / 6),
        arrow.to.y - headLen * Math.sin(angle - Math.PI / 6)
      );
      ctx.lineTo(
        arrow.to.x - headLen * Math.cos(angle + Math.PI / 6),
        arrow.to.y - headLen * Math.sin(angle + Math.PI / 6)
      );
      ctx.closePath();
      ctx.fill();
    }

    // "!!!" Warning at center during telegraph
    if (phase === 'telegraph') {
      const shakeX = (Math.random() - 0.5) * warningIntensity * 4;
      const shakeY = (Math.random() - 0.5) * warningIntensity * 4;

      ctx.font = 'bold 24px Arial';
      ctx.fillStyle = COORDINATED_ARC_CONFIG.colors.telegraph;
      ctx.textAlign = 'center';
      ctx.globalAlpha = warningIntensity;
      ctx.fillText('!!!', center.x + shakeX, center.y - 30 + shakeY);
    }
  }

  // ATTACKING: Flash on each scout as they attack
  if (phase === 'attacking') {
    for (const pos of scoutPositions) {
      const flash = Math.random() > 0.7; // Random flash effect

      if (flash) {
        ctx.globalAlpha = 0.6;
        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 15, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }

  ctx.restore();
}

// =============================================================================
// Combined Render Function
// =============================================================================

/**
 * Render all scout coordination telegraphs
 *
 * Call this from GameCanvas after regular telegraphs, before enemies
 */
export function renderScoutTelegraphs(
  ctx: CanvasRenderingContext2D,
  soloTelegraphs: SoloFlankTelegraph[],
  coordinatedTelegraphs: CoordinatedTelegraph[],
  gameTime: number
): void {
  // Render solo telegraphs first (less visually important)
  for (const telegraph of soloTelegraphs) {
    renderSoloFlankTelegraph(ctx, telegraph, gameTime);
  }

  // Render coordinated telegraphs (more visually important)
  for (const telegraph of coordinatedTelegraphs) {
    renderCoordinatedTelegraph(ctx, telegraph, gameTime);
  }
}
