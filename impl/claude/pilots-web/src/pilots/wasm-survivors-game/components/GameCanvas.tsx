/**
 * WASM Survivors - Game Canvas
 *
 * Canvas-based rendering for the game.
 * Budget: < 8ms for full render (within 16ms frame)
 *
 * Color Palette:
 * - Player: #00D4FF (Electric Blue)
 * - Enemy: #FF3366 (Corrupted Red)
 * - XP: #FFD700 (Golden)
 * - Health: #00FF88 (Vitality Green)
 * - Ghost: #A0A0B0 (Warm Gray)
 * - Crisis: #FF8800 (Warning Orange)
 *
 * Run 027 Additions:
 * - DD-17: Combo Crescendo (brightness/saturation filters)
 * - DD-20: Health Vignette (edge darkening at low HP)
 *
 * @see pilots/wasm-survivors-game/.outline.md
 */

import { useRef, useEffect, useCallback, useMemo } from 'react';
import type { GameState, Enemy } from '../types';
import type { JuiceSystem, Particle } from '../systems/juice';
import { ARENA_WIDTH, ARENA_HEIGHT } from '../systems/physics';
import {
  COLORS,
  getBreathPhase,
  getBreathGlowMultiplier,
  getBreathAlphaMultiplier,
  getEntityPhaseOffset,
  getIntensityColors,
  BREATHING_CONFIGS,
} from '../systems/juice';
import type { ActiveUpgrades } from '../systems/upgrades';
import { getBeeTelegraph, BEE_BEHAVIORS } from '../systems/enemies';
import type { BallState } from '../systems/formation';
import type { MeleeAttackState } from '../systems/melee';
import { getArcRenderPoints, getAttackProgress, MANDIBLE_REAVER_CONFIG } from '../systems/melee';
import type { ApexStrikeState } from '../systems/apex-strike';
import { APEX_CONFIG, isLocking } from '../systems/apex-strike';

// =============================================================================
// DD-17: Combo Crescendo Tiers
// =============================================================================

interface CrescendoState {
  tier: 0 | 5 | 10 | 20 | 50;
  brightness: number;
  saturation: number;
  particleMultiplier: number;
}

function getCrescendoState(combo: number): CrescendoState {
  if (combo >= 50) return { tier: 50, brightness: 1.2, saturation: 1.5, particleMultiplier: 3.0 };
  if (combo >= 20) return { tier: 20, brightness: 1.15, saturation: 1.3, particleMultiplier: 2.0 };
  if (combo >= 10) return { tier: 10, brightness: 1.1, saturation: 1.2, particleMultiplier: 1.5 };
  if (combo >= 5) return { tier: 5, brightness: 1.05, saturation: 1.1, particleMultiplier: 1.2 };
  return { tier: 0, brightness: 1.0, saturation: 1.0, particleMultiplier: 1.0 };
}

// =============================================================================
// Types
// =============================================================================

interface GameCanvasProps {
  gameState: GameState;
  juiceSystem: JuiceSystem;
  ballState?: BallState;  // Run 036: THE BALL formation state for rendering
  meleeState?: MeleeAttackState;  // Run 036: Player melee attack state
  apexState?: ApexStrikeState;  // Run 036: Apex Strike state for crosshair rendering
  chargePercent?: number;  // 0-1: How charged the current apex strike is
}

// =============================================================================
// Component
// =============================================================================

export function GameCanvas({ gameState, juiceSystem, ballState, meleeState, apexState, chargePercent = 0 }: GameCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Main render function
  const render = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Apply screen shake
    const shakeOffset = juiceSystem.shake.offset;

    // DD-16: Clutch moment zoom
    const clutch = juiceSystem.clutch;
    const isClutchActive = clutch.active && clutch.zoom > 1;

    // Clear canvas
    ctx.save();

    // Apply clutch zoom centered on player
    if (isClutchActive) {
      const playerX = gameState.player.position.x;
      const playerY = gameState.player.position.y;
      const zoom = clutch.zoom;

      // Translate to player, scale, translate back
      ctx.translate(playerX, playerY);
      ctx.scale(zoom, zoom);
      ctx.translate(-playerX, -playerY);
    }

    ctx.translate(shakeOffset.x, shakeOffset.y);

    // DD-29-2: Screen intensity colors based on wave and health
    const healthFraction = gameState.player.health / gameState.player.maxHealth;
    const intensityColors = getIntensityColors(gameState.wave, healthFraction);

    // Background with intensity-based color
    ctx.fillStyle = intensityColors.background;
    ctx.fillRect(-10, -10, ARENA_WIDTH + 20, ARENA_HEIGHT + 20);

    // Arena border with intensity-based color
    ctx.strokeStyle = intensityColors.border;
    ctx.lineWidth = 2;
    ctx.strokeRect(0, 0, ARENA_WIDTH, ARENA_HEIGHT);

    // Honeycomb hexagonal grid pattern (bee-themed!)
    drawHoneycombGrid(ctx, ARENA_WIDTH, ARENA_HEIGHT, 25, intensityColors.grid);

    // DD-21: Render telegraphs (under enemies for visibility)
    renderTelegraphs(ctx, gameState);

    // Render projectiles (under everything)
    renderProjectiles(ctx, gameState);

    // Render enemies
    renderEnemies(ctx, gameState);

    // DD-36: Attack phase visual effects (on top of enemies)
    renderAttackEffects(ctx, gameState);

    // Run 036: Render THE BALL formation (on top of enemies)
    if (ballState && ballState.phase !== 'inactive') {
      renderBall(ctx, ballState, gameState.gameTime, gameState.enemies);
    }

    // Render player (enhanced with visual upgrades)
    renderPlayer(ctx, gameState, meleeState);

    // Run 036: Render Apex Strike crosshair/sightline during lock phase
    if (apexState && isLocking(apexState)) {
      renderApexCrosshair(ctx, gameState.player.position, apexState, chargePercent);
    }

    // Run 036: Render player melee attack arc
    if (meleeState) {
      renderMeleeAttack(ctx, gameState.player.position, meleeState, gameState.gameTime);
    }

    // Render particles (juice system)
    renderParticles(ctx, juiceSystem.particles);

    // DD-20: Health Vignette - render after game content, before HUD
    // (healthFraction already calculated above for intensity)
    renderVignette(ctx, healthFraction);

    ctx.restore();

    // Render HUD (not affected by shake)
    renderHUD(ctx, gameState, juiceSystem);
  }, [gameState, juiceSystem, ballState, meleeState, apexState, chargePercent]);

  // DD-17: Calculate crescendo state from combo
  const crescendo = useMemo(
    () => getCrescendoState(juiceSystem.escalation.combo),
    [juiceSystem.escalation.combo]
  );

  // DD-17: Build CSS filter string
  const filterStyle = useMemo(() => {
    if (crescendo.tier === 0) return undefined;
    return `brightness(${crescendo.brightness}) saturate(${crescendo.saturation})`;
  }, [crescendo]);

  // Animation loop for rendering
  useEffect(() => {
    const animate = () => {
      render();
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [render]);

  return (
    <canvas
      ref={canvasRef}
      width={ARENA_WIDTH}
      height={ARENA_HEIGHT}
      className="block bg-gray-900 rounded-lg shadow-2xl"
      style={{
        imageRendering: 'pixelated',
        filter: filterStyle, // DD-17: Combo Crescendo visual effect
        transition: 'filter 0.3s ease-out', // Smooth transitions between tiers
      }}
    />
  );
}

// =============================================================================
// Render Functions
// =============================================================================

/**
 * DD-20: Health Vignette
 *
 * Creates tunnel vision effect as health decreases:
 * - HP > 50%: No vignette
 * - HP 25-50%: Subtle red edge darkening
 * - HP 10-25%: Strong vignette
 * - HP < 10%: Pulsing vignette (synced to ~5Hz)
 */
function renderVignette(ctx: CanvasRenderingContext2D, healthFraction: number) {
  // No vignette above 50% HP
  if (healthFraction > 0.5) return;

  // Intensity increases as health decreases (0 at 50%, 1 at 0%)
  const intensity = 1 - healthFraction / 0.5;

  // Pulsing at critical health (< 10%)
  let pulse = 1.0;
  if (healthFraction < 0.1) {
    pulse = 0.7 + 0.3 * Math.sin(Date.now() / 200); // ~5Hz pulse
  }

  // Radial gradient from center (clear) to edges (red)
  const centerX = ARENA_WIDTH / 2;
  const centerY = ARENA_HEIGHT / 2;
  const innerRadius = Math.max(ARENA_WIDTH, ARENA_HEIGHT) * 0.25;
  const outerRadius = Math.max(ARENA_WIDTH, ARENA_HEIGHT) * 0.75;

  const gradient = ctx.createRadialGradient(
    centerX,
    centerY,
    innerRadius,
    centerX,
    centerY,
    outerRadius
  );

  // Red vignette that intensifies with low health
  const alpha = intensity * 0.5 * pulse;
  gradient.addColorStop(0, 'transparent');
  gradient.addColorStop(0.5, `rgba(80, 0, 0, ${alpha * 0.3})`);
  gradient.addColorStop(1, `rgba(120, 0, 0, ${alpha})`);

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, ARENA_WIDTH, ARENA_HEIGHT);

  // Extra edge darkening at critical health
  if (healthFraction < 0.25) {
    const edgeAlpha = (0.25 - healthFraction) / 0.25 * 0.3 * pulse;
    ctx.fillStyle = `rgba(0, 0, 0, ${edgeAlpha})`;

    // Top edge
    const edgeGradientTop = ctx.createLinearGradient(0, 0, 0, ARENA_HEIGHT * 0.15);
    edgeGradientTop.addColorStop(0, `rgba(0, 0, 0, ${edgeAlpha})`);
    edgeGradientTop.addColorStop(1, 'transparent');
    ctx.fillStyle = edgeGradientTop;
    ctx.fillRect(0, 0, ARENA_WIDTH, ARENA_HEIGHT * 0.15);

    // Bottom edge
    const edgeGradientBottom = ctx.createLinearGradient(0, ARENA_HEIGHT * 0.85, 0, ARENA_HEIGHT);
    edgeGradientBottom.addColorStop(0, 'transparent');
    edgeGradientBottom.addColorStop(1, `rgba(0, 0, 0, ${edgeAlpha})`);
    ctx.fillStyle = edgeGradientBottom;
    ctx.fillRect(0, ARENA_HEIGHT * 0.85, ARENA_WIDTH, ARENA_HEIGHT * 0.15);
  }
}

/**
 * Render Apex Strike crosshair/sightline during lock phase.
 *
 * Shows:
 * - Aim line from player to target direction
 * - Crosshair at the end point showing where strike will land
 * - Charge indicator showing dash distance (based on hold time)
 *
 * "The hornet doesn't dash - it HUNTS. Call your shot."
 */
function renderApexCrosshair(
  ctx: CanvasRenderingContext2D,
  playerPos: { x: number; y: number },
  apexState: ApexStrikeState,
  chargePercent: number
) {
  if (!apexState.lockDirection) return;

  // Calculate dash distance based on charge (min 60px, max 360px)
  const minDistance = 60;
  const maxDistance = APEX_CONFIG.strikeDistance;
  const dashDistance = minDistance + (maxDistance - minDistance) * chargePercent;

  // Calculate end point
  const endX = playerPos.x + apexState.lockDirection.x * dashDistance;
  const endY = playerPos.y + apexState.lockDirection.y * dashDistance;

  // Draw sightline - dashed line from player to target
  ctx.save();

  // Outer glow for visibility
  ctx.strokeStyle = 'rgba(255, 140, 0, 0.3)';  // Strike Orange glow
  ctx.lineWidth = 8;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(playerPos.x, playerPos.y);
  ctx.lineTo(endX, endY);
  ctx.stroke();

  // Inner line - pulsing based on charge
  const pulseAlpha = 0.5 + chargePercent * 0.5;
  ctx.strokeStyle = `rgba(255, 140, 0, ${pulseAlpha})`;  // Strike Orange
  ctx.lineWidth = 3;
  ctx.setLineDash([10, 5]);  // Dashed line for "aim" feel
  ctx.beginPath();
  ctx.moveTo(playerPos.x, playerPos.y);
  ctx.lineTo(endX, endY);
  ctx.stroke();

  // Reset line dash
  ctx.setLineDash([]);

  // Draw crosshair at end point
  const crosshairSize = 12 + chargePercent * 8;  // Grows with charge
  const crosshairAlpha = 0.6 + chargePercent * 0.4;

  // Outer ring
  ctx.strokeStyle = `rgba(255, 140, 0, ${crosshairAlpha})`;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(endX, endY, crosshairSize, 0, Math.PI * 2);
  ctx.stroke();

  // Inner dot
  ctx.fillStyle = `rgba(255, 140, 0, ${crosshairAlpha})`;
  ctx.beginPath();
  ctx.arc(endX, endY, 3, 0, Math.PI * 2);
  ctx.fill();

  // Crosshair lines
  ctx.lineWidth = 2;
  ctx.beginPath();
  // Horizontal
  ctx.moveTo(endX - crosshairSize - 4, endY);
  ctx.lineTo(endX - crosshairSize + 4, endY);
  ctx.moveTo(endX + crosshairSize - 4, endY);
  ctx.lineTo(endX + crosshairSize + 4, endY);
  // Vertical
  ctx.moveTo(endX, endY - crosshairSize - 4);
  ctx.lineTo(endX, endY - crosshairSize + 4);
  ctx.moveTo(endX, endY + crosshairSize - 4);
  ctx.lineTo(endX, endY + crosshairSize + 4);
  ctx.stroke();

  // Charge bar indicator next to player
  const barWidth = 40;
  const barHeight = 6;
  const barX = playerPos.x - barWidth / 2;
  const barY = playerPos.y + 25;  // Below player

  // Bar background
  ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
  ctx.fillRect(barX - 1, barY - 1, barWidth + 2, barHeight + 2);

  // Charge fill - color shifts from yellow to orange to red at max
  let chargeColor: string;
  if (chargePercent < 0.5) {
    chargeColor = `rgba(255, ${200 - chargePercent * 120}, 0, 0.9)`;
  } else if (chargePercent < 1) {
    chargeColor = `rgba(255, ${140 - (chargePercent - 0.5) * 140}, 0, 0.9)`;
  } else {
    // Max charge - pulsing red
    const pulse = 0.7 + 0.3 * Math.sin(Date.now() / 100);
    chargeColor = `rgba(255, ${50 * pulse}, 0, 1)`;
  }
  ctx.fillStyle = chargeColor;
  ctx.fillRect(barX, barY, barWidth * chargePercent, barHeight);

  // Bar border
  ctx.strokeStyle = 'rgba(255, 140, 0, 0.8)';
  ctx.lineWidth = 1;
  ctx.strokeRect(barX, barY, barWidth, barHeight);

  ctx.restore();
}

/**
 * Render the player (hornet) with full visual upgrades.
 * "Ukiyo-e meets arcade brutalism" - The hornet emerges from shadow.
 *
 * @see pilots/wasm-survivors-game/HORNET_SPRITE_SPEC.md
 * @see pilots/wasm-survivors-game/ART_STYLE_GUIDE.md
 */
function renderPlayer(
  ctx: CanvasRenderingContext2D,
  state: GameState,
  meleeState?: MeleeAttackState
) {
  const { player } = state;
  const activeUpgrades = player.activeUpgrades as ActiveUpgrades | undefined;
  const healthFraction = player.health / player.maxHealth;

  // DD-29-1: Player breathing - faster at low health
  const breathConfig = healthFraction < 0.25
    ? BREATHING_CONFIGS.playerLowHealth
    : BREATHING_CONFIGS.playerCalm;
  const breathPhase = getBreathPhase(state.gameTime, breathConfig);
  const glowMultiplier = getBreathGlowMultiplier(breathPhase, breathConfig.intensity);
  const alphaMultiplier = getBreathAlphaMultiplier(breathPhase, breathConfig.intensity);

  // DD-15: Slow Field visual - subtle amber glow around player (was blue)
  if (activeUpgrades?.slowRadius && activeUpgrades.slowRadius > 0) {
    const slowGradient = ctx.createRadialGradient(
      player.position.x,
      player.position.y,
      0,
      player.position.x,
      player.position.y,
      activeUpgrades.slowRadius
    );
    // Use Burnt Amber for slow field (hornet's domain)
    slowGradient.addColorStop(0, 'rgba(204, 85, 0, 0.05)');
    slowGradient.addColorStop(0.7, 'rgba(204, 85, 0, 0.1)');
    slowGradient.addColorStop(1, 'rgba(204, 85, 0, 0)');
    ctx.fillStyle = slowGradient;
    ctx.beginPath();
    ctx.arc(player.position.x, player.position.y, activeUpgrades.slowRadius, 0, Math.PI * 2);
    ctx.fill();
  }

  // DD-9: Orbit visual - golden ring around player
  if (activeUpgrades?.orbitActive && activeUpgrades.orbitRadius > 0) {
    const time = Date.now() / 1000;
    const pulseAlpha = 0.3 + 0.2 * Math.sin(time * 4);

    ctx.strokeStyle = `rgba(255, 215, 0, ${pulseAlpha})`;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(player.position.x, player.position.y, activeUpgrades.orbitRadius, 0, Math.PI * 2);
    ctx.stroke();

    // Inner glow for orbit zone
    const orbitGradient = ctx.createRadialGradient(
      player.position.x,
      player.position.y,
      activeUpgrades.orbitRadius - 10,
      player.position.x,
      player.position.y,
      activeUpgrades.orbitRadius
    );
    orbitGradient.addColorStop(0, 'rgba(255, 215, 0, 0)');
    orbitGradient.addColorStop(1, `rgba(255, 215, 0, ${pulseAlpha * 0.3})`);
    ctx.fillStyle = orbitGradient;
    ctx.beginPath();
    ctx.arc(player.position.x, player.position.y, activeUpgrades.orbitRadius, 0, Math.PI * 2);
    ctx.fill();
  }

  // DD-29-1: Breathing glow effect - Burnt Amber glow (was cyan)
  const playerRadius = player.radius ?? 15;
  const baseGlowRadius = playerRadius * 2;
  const breathingGlowRadius = baseGlowRadius * glowMultiplier;
  const baseGlowAlpha = 0.3;
  const breathingGlowAlpha = baseGlowAlpha * alphaMultiplier;

  const gradient = ctx.createRadialGradient(
    player.position.x,
    player.position.y,
    0,
    player.position.x,
    player.position.y,
    breathingGlowRadius
  );
  // Burnt Amber glow (#CC5500)
  gradient.addColorStop(0, `rgba(204, 85, 0, ${breathingGlowAlpha})`);
  gradient.addColorStop(1, 'rgba(204, 85, 0, 0)');
  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(player.position.x, player.position.y, breathingGlowRadius, 0, Math.PI * 2);
  ctx.fill();

  // ==========================================================================
  // VISUAL UPGRADE: Wing Blur (render BEFORE body - semi-transparent behind)
  // "Wing Blur Circles - overlapping ellipses pulsing at 60hz"
  // ==========================================================================
  drawHornetWings(
    ctx,
    player.position.x,
    player.position.y,
    playerRadius,
    state.gameTime,
    COLORS.playerWing
  );

  // ==========================================================================
  // VISUAL UPGRADE: Main body with stripes
  // "The hornet emerges from shadow. Orange breaks through darkness."
  // ==========================================================================
  const bodyScale = healthFraction < 0.25 ? (1.0 + breathPhase * 0.05) : 1.0;
  const scaledRadius = playerRadius * bodyScale;

  // Main body - Burnt Amber (#CC5500)
  ctx.fillStyle = COLORS.player;
  ctx.beginPath();
  ctx.arc(player.position.x, player.position.y, scaledRadius, 0, Math.PI * 2);
  ctx.fill();

  // Body stripes - Venom Black (#1A1A1A)
  drawHornetStripes(
    ctx,
    player.position.x,
    player.position.y,
    scaledRadius,
    COLORS.playerStripe
  );

  // Body shadow (underside depth) - Dried Blood (#662200)
  ctx.fillStyle = COLORS.playerShadow;
  ctx.beginPath();
  ctx.ellipse(
    player.position.x,
    player.position.y + scaledRadius * 0.3,
    scaledRadius * 0.6,
    scaledRadius * 0.25,
    0,
    0,
    Math.PI * 2
  );
  ctx.fill();

  // Body highlight (top) - Strike Orange (#FF8C00)
  ctx.fillStyle = COLORS.playerHighlight;
  ctx.beginPath();
  ctx.ellipse(
    player.position.x,
    player.position.y - scaledRadius * 0.4,
    scaledRadius * 0.5,
    scaledRadius * 0.2,
    0,
    0,
    Math.PI * 2
  );
  ctx.fill();

  // ==========================================================================
  // VISUAL UPGRADE: Mandibles
  // "Mandibles should NEVER fully close during idle. Always a gap."
  // ==========================================================================
  const isAttacking = meleeState && (meleeState.isActive || meleeState.isInWindup);
  const mandibleOpen = isAttacking ? 1.0 : 0.0;
  const mandibleColor = isAttacking ? COLORS.playerMandible : COLORS.playerStripe;
  const mandibleDirection = meleeState?.direction ?? player.velocity;

  drawMandibles(
    ctx,
    player.position.x,
    player.position.y,
    scaledRadius,
    mandibleOpen,
    mandibleColor,
    mandibleDirection
  );

  // ==========================================================================
  // VISUAL UPGRADE: Eyes with gleam
  // "Eyes: Large, kidney-shaped, not circular. PREDATOR eyes."
  // ==========================================================================
  drawHornetEyes(
    ctx,
    player.position.x,
    player.position.y,
    scaledRadius,
    COLORS.playerEyes
  );

  // Inner highlight (kept but smaller - on thorax area)
  ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
  ctx.beginPath();
  ctx.arc(
    player.position.x - scaledRadius * 0.25,
    player.position.y - scaledRadius * 0.35,
    scaledRadius * 0.15,
    0,
    Math.PI * 2
  );
  ctx.fill();

  // ==========================================================================
  // Health bar above player (pushed up to accommodate mandibles)
  // ==========================================================================
  const healthBarWidth = playerRadius * 2.5;
  const healthBarHeight = 4;
  const healthBarX = player.position.x - healthBarWidth / 2;
  const healthBarY = player.position.y - playerRadius - 18; // Pushed up

  // Background
  ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
  ctx.fillRect(healthBarX, healthBarY, healthBarWidth, healthBarHeight);

  // Health fill
  const healthColor =
    healthFraction > 0.5
      ? COLORS.health
      : healthFraction > 0.25
        ? COLORS.xp
        : COLORS.crisis;
  ctx.fillStyle = healthColor;
  ctx.fillRect(healthBarX, healthBarY, healthBarWidth * healthFraction, healthBarHeight);
}

// =============================================================================
// Bee Type Colors (Run 036+: Enhanced Readability)
// =============================================================================

// =============================================================================
// Bee Type Colors - "Ukiyo-e meets arcade brutalism"
// Workers blur into swarm; elites get hierarchy colors
// See: pilots/wasm-survivors-game/ART_STYLE_GUIDE.md, BEE_SPRITES_SPEC.md
// =============================================================================

const BEE_TYPE_COLORS = {
  // Worker Bee: Expendable, swarm density (circle shape)
  worker: '#D4920A',    // Worker Amber - sympathetic but not precious
  basic: '#D4920A',     // Alias for worker

  // Scout Bee: Leaner, paler - flies too long (triangle shape)
  scout: '#E5B84A',     // Faded Honey - lighter = faster visual weight
  fast: '#E5B84A',      // Alias for scout

  // Guard Bee: Darker, denser - armor plating (square shape)
  guard: '#B87A0A',     // Hardened Amber - earthy, solid
  tank: '#B87A0A',      // Alias for guard

  // Propolis Bee: Sticky, resinous - slight green undertone (diamond shape)
  propolis: '#A08020',  // Resin Gold - chemical payload
  spitter: '#A08020',   // Alias for propolis

  // Royal Guard: SACRED purple - edge only, 2-4 pixels (octagon shape)
  royal: '#6B2D5B',     // Royal Purple - hierarchy, not decoration
  boss: '#6B2D5B',      // Alias for royal
} as const;

function renderEnemies(ctx: CanvasRenderingContext2D, state: GameState) {
  for (const enemy of state.enemies) {
    // DD-29-1: Enemy breathing based on behavior state
    const behaviorState = enemy.behaviorState ?? 'chase';
    let breathConfig = BREATHING_CONFIGS.enemyChase;
    if (behaviorState === 'telegraph') {
      breathConfig = BREATHING_CONFIGS.enemyTelegraph;
    } else if (behaviorState === 'attack') {
      breathConfig = BREATHING_CONFIGS.enemyAttack;
    } else if (behaviorState === 'recovery') {
      breathConfig = BREATHING_CONFIGS.enemyRecovery;
    }

    // Each enemy breathes at a different phase
    const phaseOffset = getEntityPhaseOffset(enemy.id);
    const breathPhase = getBreathPhase(state.gameTime, { ...breathConfig, phaseOffset });
    const glowMultiplier = getBreathGlowMultiplier(breathPhase, breathConfig.intensity);
    const alphaMultiplier = getBreathAlphaMultiplier(breathPhase, breathConfig.intensity);

    // Base glow alpha varies by state
    const baseGlowAlpha = behaviorState === 'recovery' ? 0.1 : 0.2;
    const glowAlpha = baseGlowAlpha * alphaMultiplier;

    // Run 036: Recovery state vulnerability visualization
    const isRecovering = behaviorState === 'recovery';

    // Run 036+: Get bee-type specific color
    const beeColor = BEE_TYPE_COLORS[enemy.type as keyof typeof BEE_TYPE_COLORS] ?? enemy.color ?? '#F4D03F';

    // Enemy glow - golden opportunity glow during recovery
    const glowRadius = enemy.radius * 1.5 * glowMultiplier;
    const gradient = ctx.createRadialGradient(
      enemy.position.x,
      enemy.position.y,
      0,
      enemy.position.x,
      enemy.position.y,
      glowRadius
    );

    if (isRecovering) {
      // Golden glow = opportunity (not red = danger)
      gradient.addColorStop(0, `rgba(255, 215, 0, ${glowAlpha * 2})`);
      gradient.addColorStop(0.5, `rgba(255, 255, 255, ${glowAlpha * 1.5})`);
      gradient.addColorStop(1, 'rgba(255, 215, 0, 0)');
    } else {
      // Red glow = danger
      gradient.addColorStop(0, `rgba(255, 51, 102, ${glowAlpha})`);
      gradient.addColorStop(1, 'rgba(255, 51, 102, 0)');
    }
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(enemy.position.x, enemy.position.y, glowRadius, 0, Math.PI * 2);
    ctx.fill();

    // DD-21: Visual feedback for behavior state
    const isAttacking = behaviorState === 'attack';
    const isTelegraphing = behaviorState === 'telegraph';

    // Run 036: Wobble animation during recovery (staggered enemy)
    let wobbleOffsetX = 0;
    let wobbleOffsetY = 0;
    if (isRecovering) {
      const wobbleSpeed = 0.01;
      const wobbleAmplitude = enemy.radius * 0.15;
      wobbleOffsetX = Math.sin(state.gameTime * wobbleSpeed) * wobbleAmplitude;
      wobbleOffsetY = Math.cos(state.gameTime * wobbleSpeed * 1.3) * wobbleAmplitude * 0.5;
    }

    const enemyX = enemy.position.x + wobbleOffsetX;
    const enemyY = enemy.position.y + wobbleOffsetY;

    // Scale enemy when telegraphing (wind-up visual) - now with breathing too
    let drawRadius = enemy.radius;
    if (isTelegraphing) {
      drawRadius = enemy.radius * 1.2 * glowMultiplier;  // DD-22 + DD-29-1: Breathing during telegraph
    } else if (isAttacking) {
      drawRadius = enemy.radius * (1.0 + breathPhase * 0.1);  // Subtle pulsing during attack
    }

    // ==========================================================================
    // Run 036+: WING ANIMATION (all bee types)
    // Semi-transparent oscillating wing blur effect
    // ==========================================================================

    const wingPhase = Math.sin(state.gameTime * 0.02 + (enemy.id.charCodeAt(0) ?? 0));
    const wingAlpha = 0.3 + wingPhase * 0.1;
    const wingColor = `rgba(200, 200, 255, ${wingAlpha})`;

    ctx.save();
    ctx.fillStyle = wingColor;
    ctx.globalAlpha = wingAlpha;

    // Left wing
    ctx.beginPath();
    ctx.ellipse(
      enemyX - drawRadius * 0.8,
      enemyY - drawRadius * 0.3,
      drawRadius * 0.6,
      drawRadius * 0.25,
      -Math.PI * 0.25 + wingPhase * 0.1,
      0,
      Math.PI * 2
    );
    ctx.fill();

    // Right wing (mirror)
    ctx.beginPath();
    ctx.ellipse(
      enemyX + drawRadius * 0.8,
      enemyY - drawRadius * 0.3,
      drawRadius * 0.6,
      drawRadius * 0.25,
      Math.PI * 0.25 - wingPhase * 0.1,
      0,
      Math.PI * 2
    );
    ctx.fill();

    ctx.restore();

    // ==========================================================================
    // Main body rendering with type-specific colors
    // ==========================================================================

    // Main body - faded during recovery
    const bodyAlpha = behaviorState === 'recovery' ? 0.6 : 1.0;
    ctx.globalAlpha = bodyAlpha;
    ctx.fillStyle = beeColor;
    ctx.beginPath();

    // Different shapes for different types (Run 036: Added bee type mappings)
    switch (enemy.type) {
      case 'basic':
      case 'worker':  // Bee type: circle (swarm)
        ctx.arc(enemyX, enemyY, drawRadius, 0, Math.PI * 2);
        ctx.fill();

        // Run 036+: Add stripes to worker bees
        ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
        const stripeWidth = drawRadius * 0.25;
        for (let i = -1; i <= 1; i++) {
          ctx.fillRect(
            enemyX - drawRadius * 0.7,
            enemyY + i * stripeWidth * 1.5 - stripeWidth * 0.4,
            drawRadius * 1.4,
            stripeWidth * 0.8
          );
        }
        break;

      case 'fast':
      case 'scout':  // Bee type: triangle (fast alert)
        // =================================================================
        // VISUAL UPGRADE: Scout with antennae + speed trails
        // "The colony's eyes. They see you. They tell the others."
        // =================================================================

        // Triangle for fast enemies (Rusher)
        drawTriangle(ctx, enemyX, enemyY, drawRadius);
        ctx.fill();

        // VISUAL UPGRADE: Wiggling antennae (alert mode)
        const antennaPhase = state.gameTime * 0.015 + (enemy.id.charCodeAt(0) ?? 0);
        drawAntennae(ctx, enemyX, enemyY, drawRadius, antennaPhase, '#1F1A14');

        // Speed lines - Enhanced cyan (#00D4FF) instead of orange
        ctx.strokeStyle = 'rgba(0, 212, 255, 0.5)';  // Cyan speed trails
        ctx.lineWidth = 2;
        const speedPhase = (state.gameTime * 0.005) % 1;
        for (let i = 0; i < 3; i++) {
          const lineOffset = (i - 1) * drawRadius * 0.35;
          const lineAlpha = 0.3 + (1 - speedPhase) * 0.3;
          ctx.globalAlpha = lineAlpha;
          ctx.beginPath();
          ctx.moveTo(enemyX + lineOffset, enemyY + drawRadius * 0.5);
          ctx.lineTo(enemyX + lineOffset, enemyY + drawRadius * (1.0 + speedPhase * 0.5));
          ctx.stroke();
        }
        ctx.globalAlpha = 1;
        break;

      case 'spitter':
      case 'propolis':  // Bee type: diamond (ranged)
        // =================================================================
        // VISUAL UPGRADE: Propolis with animated drip
        // "The colony's alchemist. Sticky death from a distance."
        // =================================================================

        // DD-24: Diamond shape for ranged Spitter
        drawDiamond(ctx, enemyX, enemyY, drawRadius);
        ctx.fill();

        // VISUAL UPGRADE: Animated drip falling from bottom vertex
        const dripPhase = ((state.gameTime * 0.002) + (enemy.id.charCodeAt(0) ?? 0) * 0.1) % 1;
        const dripY = enemyY + drawRadius + dripPhase * drawRadius * 0.8;
        const dripSize = drawRadius * 0.15 * (1 - dripPhase * 0.5);
        const dripAlpha = 1 - dripPhase * 0.7;

        // Drip trail
        ctx.fillStyle = `rgba(160, 128, 32, ${dripAlpha * 0.4})`;
        ctx.beginPath();
        ctx.moveTo(enemyX, enemyY + drawRadius);
        ctx.lineTo(enemyX - dripSize * 0.5, dripY);
        ctx.lineTo(enemyX + dripSize * 0.5, dripY);
        ctx.closePath();
        ctx.fill();

        // Drip droplet
        ctx.fillStyle = `rgba(160, 128, 32, ${dripAlpha})`;  // Resin Gold
        ctx.beginPath();
        ctx.arc(enemyX, dripY, dripSize, 0, Math.PI * 2);
        ctx.fill();

        // Purple core (projectile organ)
        ctx.fillStyle = 'rgba(107, 45, 91, 0.7)';  // Royal Purple
        ctx.beginPath();
        ctx.arc(enemyX, enemyY, drawRadius * 0.35, 0, Math.PI * 2);
        ctx.fill();
        break;

      case 'tank':
      case 'guard':  // Bee type: square (blocker)
        // =================================================================
        // VISUAL UPGRADE: Guard with full armor plating
        // "The colony's shield. They don't chase. They hold the line."
        // =================================================================

        // Square for tank enemies
        ctx.fillRect(
          enemyX - drawRadius,
          enemyY - drawRadius,
          drawRadius * 2,
          drawRadius * 2
        );

        // VISUAL UPGRADE: Armor plating - vertical lines
        ctx.strokeStyle = 'rgba(74, 48, 0, 0.5)';  // Dark Umber
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(enemyX - drawRadius * 0.6, enemyY - drawRadius);
        ctx.lineTo(enemyX - drawRadius * 0.6, enemyY + drawRadius);
        ctx.moveTo(enemyX + drawRadius * 0.6, enemyY - drawRadius);
        ctx.lineTo(enemyX + drawRadius * 0.6, enemyY + drawRadius);
        ctx.stroke();

        // VISUAL UPGRADE: Armor plating - horizontal bands
        ctx.strokeStyle = 'rgba(74, 48, 0, 0.4)';  // Dark Umber
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(enemyX - drawRadius, enemyY - drawRadius * 0.4);
        ctx.lineTo(enemyX + drawRadius, enemyY - drawRadius * 0.4);
        ctx.moveTo(enemyX - drawRadius, enemyY + drawRadius * 0.4);
        ctx.lineTo(enemyX + drawRadius, enemyY + drawRadius * 0.4);
        ctx.stroke();

        // VISUAL UPGRADE: Gold trim highlight on armor edges
        ctx.strokeStyle = 'rgba(196, 160, 0, 0.3)';  // Armor Gold
        ctx.lineWidth = 1;
        ctx.strokeRect(
          enemyX - drawRadius + 1,
          enemyY - drawRadius + 1,
          drawRadius * 2 - 2,
          drawRadius * 2 - 2
        );

        // Heavy outline for "blocky tank" feel
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.4)';
        ctx.lineWidth = 2;
        ctx.strokeRect(
          enemyX - drawRadius,
          enemyY - drawRadius,
          drawRadius * 2,
          drawRadius * 2
        );
        break;

      case 'boss':
      case 'royal':  // Bee type: octagon (elite)
        // =================================================================
        // VISUAL UPGRADE: Royal Guard with crown, jewel, red eyes, aura
        // "The Queen's chosen. They anchor THE BALL. They end the siege."
        // =================================================================

        // Pulsing royal aura
        const royalPulse = Math.sin(state.gameTime * 0.003) * 0.5 + 0.5;
        const auraAlpha = 0.15 + royalPulse * 0.1;
        const royalAura = ctx.createRadialGradient(
          enemyX, enemyY, drawRadius * 0.5,
          enemyX, enemyY, drawRadius * 1.8
        );
        royalAura.addColorStop(0, `rgba(107, 45, 91, ${auraAlpha})`);  // Royal Purple
        royalAura.addColorStop(1, 'rgba(107, 45, 91, 0)');
        ctx.fillStyle = royalAura;
        ctx.beginPath();
        ctx.arc(enemyX, enemyY, drawRadius * 1.8, 0, Math.PI * 2);
        ctx.fill();

        // Larger octagon for boss
        ctx.fillStyle = beeColor;
        drawOctagon(ctx, enemyX, enemyY, drawRadius);
        ctx.fill();

        // Cross-hatch pattern on body
        ctx.strokeStyle = 'rgba(74, 26, 74, 0.4)';  // Darker purple
        ctx.lineWidth = 1;
        for (let i = -2; i <= 2; i++) {
          ctx.beginPath();
          ctx.moveTo(enemyX + i * drawRadius * 0.3, enemyY - drawRadius * 0.7);
          ctx.lineTo(enemyX + i * drawRadius * 0.3, enemyY + drawRadius * 0.7);
          ctx.stroke();
        }

        // Gold trim edge
        ctx.strokeStyle = 'rgba(255, 215, 0, 0.5)';
        ctx.lineWidth = 2;
        drawOctagon(ctx, enemyX, enemyY, drawRadius);
        ctx.stroke();

        // Crown with 3 points
        ctx.fillStyle = '#FFD700';  // Gold Leaf
        ctx.beginPath();
        const crownY = enemyY - drawRadius * 0.55;
        ctx.moveTo(enemyX - drawRadius * 0.45, crownY);
        ctx.lineTo(enemyX - drawRadius * 0.25, crownY - drawRadius * 0.35);
        ctx.lineTo(enemyX, crownY - drawRadius * 0.15);
        ctx.lineTo(enemyX + drawRadius * 0.25, crownY - drawRadius * 0.35);
        ctx.lineTo(enemyX + drawRadius * 0.45, crownY);
        ctx.closePath();
        ctx.fill();

        // Crown jewel (center gem)
        ctx.fillStyle = '#FF0000';  // Ruby red
        ctx.beginPath();
        ctx.arc(enemyX, crownY - drawRadius * 0.15, drawRadius * 0.08, 0, Math.PI * 2);
        ctx.fill();
        // Jewel gleam
        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        ctx.arc(enemyX - drawRadius * 0.02, crownY - drawRadius * 0.18, 1.5, 0, Math.PI * 2);
        ctx.fill();

        // MENACING RED EYES
        ctx.fillStyle = '#FF0000';
        const eyeOffsetX = drawRadius * 0.25;
        const eyeOffsetY = drawRadius * 0.1;
        // Left eye
        ctx.beginPath();
        ctx.ellipse(
          enemyX - eyeOffsetX,
          enemyY - eyeOffsetY,
          drawRadius * 0.12,
          drawRadius * 0.08,
          -0.2,
          0,
          Math.PI * 2
        );
        ctx.fill();
        // Right eye
        ctx.beginPath();
        ctx.ellipse(
          enemyX + eyeOffsetX,
          enemyY - eyeOffsetY,
          drawRadius * 0.12,
          drawRadius * 0.08,
          0.2,
          0,
          Math.PI * 2
        );
        ctx.fill();
        // Eye gleam
        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        ctx.arc(enemyX - eyeOffsetX - 1, enemyY - eyeOffsetY - 1, 1, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(enemyX + eyeOffsetX - 1, enemyY - eyeOffsetY - 1, 1, 0, Math.PI * 2);
        ctx.fill();
        break;

      default:
        ctx.arc(enemyX, enemyY, drawRadius, 0, Math.PI * 2);
        ctx.fill();
    }

    // DD-21: Additional glow during attack
    if (isAttacking) {
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 2;
      ctx.beginPath();
      // Re-draw shape outline for stroke
      switch (enemy.type) {
        case 'basic':
        case 'worker':
          ctx.arc(enemyX, enemyY, drawRadius, 0, Math.PI * 2);
          break;
        case 'fast':
        case 'scout':
          drawTriangle(ctx, enemyX, enemyY, drawRadius);
          break;
        case 'spitter':
        case 'propolis':
          drawDiamond(ctx, enemyX, enemyY, drawRadius);
          break;
        case 'tank':
        case 'guard':
          ctx.rect(enemyX - drawRadius, enemyY - drawRadius, drawRadius * 2, drawRadius * 2);
          break;
        case 'boss':
        case 'royal':
          drawOctagon(ctx, enemyX, enemyY, drawRadius);
          break;
        default:
          ctx.arc(enemyX, enemyY, drawRadius, 0, Math.PI * 2);
      }
      ctx.stroke();
    }

    // Run 036: Golden shimmer outline during recovery + stars/dizziness
    if (isRecovering) {
      const shimmerPhase = (state.gameTime % 1000) / 1000; // 0-1 cycle per second
      const shimmerAlpha = 0.4 + Math.sin(shimmerPhase * Math.PI * 2) * 0.3;

      ctx.globalAlpha = shimmerAlpha;
      ctx.strokeStyle = '#FFD700'; // Golden outline
      ctx.lineWidth = 3;

      // Re-draw shape for shimmer stroke
      ctx.beginPath();
      switch (enemy.type) {
        case 'basic':
        case 'worker':
          ctx.arc(enemyX, enemyY, drawRadius, 0, Math.PI * 2);
          break;
        case 'fast':
        case 'scout':
          drawTriangle(ctx, enemyX, enemyY, drawRadius);
          break;
        case 'spitter':
        case 'propolis':
          drawDiamond(ctx, enemyX, enemyY, drawRadius);
          break;
        case 'tank':
        case 'guard':
          ctx.rect(enemyX - drawRadius, enemyY - drawRadius, drawRadius * 2, drawRadius * 2);
          break;
        case 'boss':
        case 'royal':
          drawOctagon(ctx, enemyX, enemyY, drawRadius);
          break;
        default:
          ctx.arc(enemyX, enemyY, drawRadius, 0, Math.PI * 2);
      }
      ctx.stroke();

      // Inner white highlight for extra pop
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 1.5;
      ctx.globalAlpha = shimmerAlpha * 0.6;
      ctx.stroke();

      // Run 036+: Stars/dizziness indicator during recovery
      ctx.globalAlpha = 0.8;
      ctx.fillStyle = '#FFD700';
      const starCount = 3;
      const starOrbitRadius = drawRadius + 8;
      const starRotation = (state.gameTime * 0.005) % (Math.PI * 2);

      for (let i = 0; i < starCount; i++) {
        const starAngle = starRotation + (i * Math.PI * 2) / starCount;
        const starX = enemyX + Math.cos(starAngle) * starOrbitRadius;
        const starY = enemyY - drawRadius * 0.5 + Math.sin(starAngle) * (starOrbitRadius * 0.3);

        // Draw small 4-pointed star
        ctx.beginPath();
        const starSize = 4;
        ctx.moveTo(starX, starY - starSize);
        ctx.lineTo(starX + starSize * 0.3, starY - starSize * 0.3);
        ctx.lineTo(starX + starSize, starY);
        ctx.lineTo(starX + starSize * 0.3, starY + starSize * 0.3);
        ctx.lineTo(starX, starY + starSize);
        ctx.lineTo(starX - starSize * 0.3, starY + starSize * 0.3);
        ctx.lineTo(starX - starSize, starY);
        ctx.lineTo(starX - starSize * 0.3, starY - starSize * 0.3);
        ctx.closePath();
        ctx.fill();
      }
    }

    // Health bar for tanks, guards, bosses, and royals
    if (enemy.type === 'tank' || enemy.type === 'boss' || enemy.type === 'guard' || enemy.type === 'royal') {
      ctx.globalAlpha = 1.0;
      const healthFraction = enemy.health / enemy.maxHealth;
      const healthBarWidth = enemy.radius * 2;
      const healthBarX = enemy.position.x - healthBarWidth / 2;
      const healthBarY = enemy.position.y - enemy.radius - 8;

      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.fillRect(healthBarX, healthBarY, healthBarWidth, 3);

      // Health color based on bee type
      ctx.fillStyle = beeColor;
      ctx.fillRect(healthBarX, healthBarY, healthBarWidth * healthFraction, 3);
    }

    // DD-29-1: Reset globalAlpha after each enemy
    ctx.globalAlpha = 1.0;
  }
}

function renderProjectiles(ctx: CanvasRenderingContext2D, state: GameState) {
  for (const projectile of state.projectiles) {
    // Trail effect
    const gradient = ctx.createRadialGradient(
      projectile.position.x,
      projectile.position.y,
      0,
      projectile.position.x,
      projectile.position.y,
      projectile.radius * 2
    );
    gradient.addColorStop(0, 'rgba(0, 212, 255, 0.6)');
    gradient.addColorStop(1, 'rgba(0, 212, 255, 0)');
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(
      projectile.position.x,
      projectile.position.y,
      projectile.radius * 2,
      0,
      Math.PI * 2
    );
    ctx.fill();

    // Main body
    ctx.fillStyle = projectile.color;
    ctx.beginPath();
    ctx.arc(
      projectile.position.x,
      projectile.position.y,
      projectile.radius,
      0,
      Math.PI * 2
    );
    ctx.fill();
  }
}

function renderParticles(ctx: CanvasRenderingContext2D, particles: Particle[]) {
  for (const particle of particles) {
    ctx.globalAlpha = particle.alpha;

    switch (particle.type) {
      case 'burst':
        ctx.fillStyle = particle.color;
        ctx.beginPath();
        ctx.arc(
          particle.position.x,
          particle.position.y,
          particle.size,
          0,
          Math.PI * 2
        );
        ctx.fill();
        break;

      case 'trail':
        const trailGradient = ctx.createRadialGradient(
          particle.position.x,
          particle.position.y,
          0,
          particle.position.x,
          particle.position.y,
          particle.size
        );
        trailGradient.addColorStop(0, particle.color);
        trailGradient.addColorStop(1, 'transparent');
        ctx.fillStyle = trailGradient;
        ctx.beginPath();
        ctx.arc(
          particle.position.x,
          particle.position.y,
          particle.size,
          0,
          Math.PI * 2
        );
        ctx.fill();
        break;

      case 'text':
        ctx.fillStyle = particle.color;
        ctx.font = `bold ${particle.size}px sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText(
          particle.text || '',
          particle.position.x,
          particle.position.y
        );
        break;

      case 'ring':
        ctx.strokeStyle = particle.color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(
          particle.position.x,
          particle.position.y,
          particle.size,
          0,
          Math.PI * 2
        );
        ctx.stroke();
        break;

      case 'spiral':
        // Death spiral with rotation - star shape
        ctx.save();
        ctx.translate(particle.position.x, particle.position.y);
        ctx.rotate(particle.rotation ?? 0);
        ctx.fillStyle = particle.color;
        ctx.beginPath();
        const points = 4;
        const innerRadius = particle.size * 0.5;
        const outerRadius = particle.size;
        for (let i = 0; i < points * 2; i++) {
          const angle = (Math.PI * i) / points;
          const radius = i % 2 === 0 ? outerRadius : innerRadius;
          const x = Math.cos(angle) * radius;
          const y = Math.sin(angle) * radius;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.fill();
        ctx.restore();
        break;

      case 'drip':
        // Honey drip - teardrop shape
        ctx.fillStyle = particle.color;
        ctx.beginPath();
        ctx.arc(
          particle.position.x,
          particle.position.y,
          particle.size,
          0,
          Math.PI * 2
        );
        ctx.fill();
        break;

      case 'pool':
        // Honey pool - ellipse on ground
        ctx.save();
        ctx.fillStyle = particle.color;
        ctx.beginPath();
        const poolWidth = particle.size * 1.3;
        const poolHeight = particle.size * 0.6;
        ctx.ellipse(
          particle.position.x,
          particle.position.y,
          poolWidth,
          poolHeight,
          0, 0, Math.PI * 2
        );
        ctx.fill();
        ctx.restore();
        break;

      case 'fragment':
        // Damage flash fragments - sharp angular shapes
        ctx.fillStyle = particle.color;
        ctx.beginPath();
        ctx.arc(
          particle.position.x,
          particle.position.y,
          particle.size,
          0,
          Math.PI * 2
        );
        ctx.fill();
        break;

      case 'graze_spark':
        // Graze sparks - cyan flash with glow
        ctx.save();
        // Outer glow
        const sparkGradient = ctx.createRadialGradient(
          particle.position.x,
          particle.position.y,
          0,
          particle.position.x,
          particle.position.y,
          particle.size * 2
        );
        sparkGradient.addColorStop(0, particle.color);
        sparkGradient.addColorStop(0.5, `${particle.color}88`);
        sparkGradient.addColorStop(1, 'transparent');
        ctx.fillStyle = sparkGradient;
        ctx.beginPath();
        ctx.arc(
          particle.position.x,
          particle.position.y,
          particle.size * 2,
          0,
          Math.PI * 2
        );
        ctx.fill();
        // Inner core
        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        ctx.arc(
          particle.position.x,
          particle.position.y,
          particle.size * 0.5,
          0,
          Math.PI * 2
        );
        ctx.fill();
        ctx.restore();
        break;
    }
  }

  ctx.globalAlpha = 1;
}

/**
 * Draw a semi-transparent HUD panel with honey amber border
 */
function drawHUDPanel(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  options?: { glow?: boolean; glowColor?: string }
) {
  ctx.save();

  // Panel background
  ctx.fillStyle = 'rgba(0, 0, 0, 0.65)';
  ctx.beginPath();
  ctx.roundRect(x, y, width, height, 6);
  ctx.fill();

  // Honey amber border
  ctx.strokeStyle = 'rgba(244, 163, 0, 0.4)';
  ctx.lineWidth = 1.5;
  ctx.stroke();

  // Optional glow effect
  if (options?.glow) {
    ctx.shadowColor = options.glowColor ?? '#F4A300';
    ctx.shadowBlur = 8;
    ctx.strokeStyle = options.glowColor ?? 'rgba(244, 163, 0, 0.6)';
    ctx.stroke();
    ctx.shadowBlur = 0;
  }

  ctx.restore();
}

/**
 * Draw text with shadow for better readability
 */
function drawTextWithShadow(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  options?: { shadowBlur?: number; shadowColor?: string }
) {
  ctx.save();
  ctx.shadowColor = options?.shadowColor ?? 'rgba(0, 0, 0, 0.9)';
  ctx.shadowBlur = options?.shadowBlur ?? 4;
  ctx.shadowOffsetX = 1;
  ctx.shadowOffsetY = 1;
  ctx.fillText(text, x, y);
  ctx.restore();
}

/**
 * Draw a hexagonal badge shape
 */
function drawHexBadge(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number
) {
  const inset = height * 0.25;
  ctx.beginPath();
  ctx.moveTo(x + inset, y);
  ctx.lineTo(x + width - inset, y);
  ctx.lineTo(x + width, y + height / 2);
  ctx.lineTo(x + width - inset, y + height);
  ctx.lineTo(x + inset, y + height);
  ctx.lineTo(x, y + height / 2);
  ctx.closePath();
}

function renderHUD(
  ctx: CanvasRenderingContext2D,
  state: GameState,
  juiceSystem: JuiceSystem
) {
  const padding = 12;
  const combo = juiceSystem.escalation.combo;

  // ==========================================================================
  // TOP LEFT: Wave indicator with hexagonal badge
  // ==========================================================================

  const waveText = `Wave ${state.wave}`;
  ctx.font = 'bold 20px sans-serif';
  const waveTextWidth = ctx.measureText(waveText).width;
  const waveBadgeWidth = waveTextWidth + 50;
  const waveBadgeHeight = 32;

  // Hexagonal badge background
  ctx.save();
  drawHexBadge(ctx, padding - 5, 8, waveBadgeWidth, waveBadgeHeight);

  // Gradient fill for the badge
  const waveGradient = ctx.createLinearGradient(padding, 8, padding, 8 + waveBadgeHeight);
  waveGradient.addColorStop(0, 'rgba(244, 163, 0, 0.3)');
  waveGradient.addColorStop(0.5, 'rgba(180, 100, 0, 0.4)');
  waveGradient.addColorStop(1, 'rgba(244, 163, 0, 0.3)');
  ctx.fillStyle = waveGradient;
  ctx.fill();

  // Badge border with glow
  ctx.strokeStyle = '#F4A300';
  ctx.lineWidth = 2;
  ctx.shadowColor = '#F4A300';
  ctx.shadowBlur = 6;
  ctx.stroke();
  ctx.shadowBlur = 0;
  ctx.restore();

  // Wave text with bee icon
  ctx.fillStyle = '#FFFFFF';
  ctx.font = 'bold 20px sans-serif';
  ctx.textAlign = 'left';
  drawTextWithShadow(ctx, `Wave ${state.wave}`, padding + 8, 30);

  // ==========================================================================
  // TOP RIGHT: Score with panel
  // ==========================================================================

  const scoreText = `${state.score.toLocaleString()}`;
  ctx.font = 'bold 18px sans-serif';
  const scoreTextWidth = ctx.measureText(scoreText).width;
  const scorePanelWidth = scoreTextWidth + 60;

  drawHUDPanel(ctx, ARENA_WIDTH - padding - scorePanelWidth, 6, scorePanelWidth, 30);

  ctx.fillStyle = COLORS.xp;
  ctx.font = 'bold 18px sans-serif';
  ctx.textAlign = 'right';
  drawTextWithShadow(ctx, `Score: ${scoreText}`, ARENA_WIDTH - padding - 10, 27);

  // ==========================================================================
  // XP Bar with hexagonal styling and gradient fill
  // ==========================================================================

  const xpBarWidth = 160;
  const xpBarHeight = 12;
  const xpBarX = padding;
  const xpBarY = 48;
  const xpFraction = state.player.xp / state.player.xpToNextLevel;

  // XP bar background panel
  drawHUDPanel(ctx, xpBarX - 5, xpBarY - 4, xpBarWidth + 10, xpBarHeight + 8);

  // XP bar background track
  ctx.fillStyle = 'rgba(40, 30, 10, 0.8)';
  ctx.beginPath();
  ctx.roundRect(xpBarX, xpBarY, xpBarWidth, xpBarHeight, 3);
  ctx.fill();

  // XP bar fill with gradient (dark gold to bright gold)
  if (xpFraction > 0) {
    const xpGradient = ctx.createLinearGradient(xpBarX, xpBarY, xpBarX + xpBarWidth * xpFraction, xpBarY);
    xpGradient.addColorStop(0, '#B8860B'); // Dark gold
    xpGradient.addColorStop(0.5, '#FFD700'); // Bright gold
    xpGradient.addColorStop(1, '#FFF8DC'); // Cornsilk (shimmer)

    ctx.fillStyle = xpGradient;
    ctx.beginPath();
    ctx.roundRect(xpBarX, xpBarY, xpBarWidth * xpFraction, xpBarHeight, 3);
    ctx.fill();

    // Shimmer effect (animated highlight)
    const shimmerTime = Date.now() * 0.002;
    const shimmerPos = (Math.sin(shimmerTime) * 0.5 + 0.5) * xpFraction;
    const shimmerX = xpBarX + xpBarWidth * shimmerPos;

    if (xpFraction > 0.1) {
      const shimmerGradient = ctx.createLinearGradient(shimmerX - 20, xpBarY, shimmerX + 20, xpBarY);
      shimmerGradient.addColorStop(0, 'rgba(255, 255, 255, 0)');
      shimmerGradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.4)');
      shimmerGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

      ctx.fillStyle = shimmerGradient;
      ctx.beginPath();
      ctx.roundRect(xpBarX, xpBarY, xpBarWidth * xpFraction, xpBarHeight, 3);
      ctx.fill();
    }
  }

  // XP bar border
  ctx.strokeStyle = 'rgba(244, 163, 0, 0.5)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.roundRect(xpBarX, xpBarY, xpBarWidth, xpBarHeight, 3);
  ctx.stroke();

  // Level indicator
  ctx.fillStyle = '#FFFFFF';
  ctx.font = 'bold 13px sans-serif';
  ctx.textAlign = 'left';
  drawTextWithShadow(ctx, `Lv.${state.player.level}`, xpBarX + xpBarWidth + 10, xpBarY + 10);

  // ==========================================================================
  // CENTER TOP: Combo indicator (scales with combo count)
  // ==========================================================================

  if (combo > 1) {
    // Combo panel with glow effect
    const comboText = `${combo}x COMBO`;

    // Scale font size with combo (max at 50+)
    const comboScale = Math.min(1 + (combo - 1) * 0.02, 1.5);
    const comboFontSize = Math.floor(24 * comboScale);
    ctx.font = `bold ${comboFontSize}px sans-serif`;

    const comboTextWidth = ctx.measureText(comboText).width;
    const comboPanelWidth = comboTextWidth + 30;
    const comboPanelHeight = comboFontSize + 16;
    const comboPanelX = (ARENA_WIDTH - comboPanelWidth) / 2;
    const comboPanelY = 5;

    // Determine glow color based on combo tier
    let comboColor = '#FF8800'; // Orange
    let glowColor = '#FF8800';
    if (combo >= 50) {
      comboColor = '#FFD700'; // Gold
      glowColor = '#FFD700';
    } else if (combo >= 20) {
      comboColor = '#FF4444'; // Red
      glowColor = '#FF4444';
    } else if (combo >= 10) {
      comboColor = '#FF6600'; // Deep orange
      glowColor = '#FF6600';
    }

    // Pulsing glow effect
    const pulseTime = Date.now() * 0.006;
    const pulseIntensity = 0.5 + Math.sin(pulseTime) * 0.3;

    drawHUDPanel(ctx, comboPanelX, comboPanelY, comboPanelWidth, comboPanelHeight, {
      glow: true,
      glowColor: glowColor
    });

    // Combo text with glow
    ctx.save();
    ctx.fillStyle = comboColor;
    ctx.textAlign = 'center';
    ctx.shadowColor = comboColor;
    ctx.shadowBlur = 10 * pulseIntensity;
    ctx.fillText(comboText, ARENA_WIDTH / 2, comboPanelY + comboPanelHeight - 8);
    ctx.shadowBlur = 0;
    ctx.restore();

    // Combo timer bar (if combo is decaying)
    const comboDecayMax = 2000; // 2 seconds
    const comboTimeLeft = Math.max(0, comboDecayMax - (Date.now() - (juiceSystem.killTracker.lastKillTime ?? Date.now())));
    const comboTimeRatio = comboTimeLeft / comboDecayMax;

    if (comboTimeRatio < 1) {
      const timerBarWidth = comboPanelWidth - 10;
      const timerBarHeight = 3;
      const timerBarX = comboPanelX + 5;
      const timerBarY = comboPanelY + comboPanelHeight - 5;

      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.fillRect(timerBarX, timerBarY, timerBarWidth, timerBarHeight);

      ctx.fillStyle = comboColor;
      ctx.fillRect(timerBarX, timerBarY, timerBarWidth * comboTimeRatio, timerBarHeight);
    }
  }

  // ==========================================================================
  // BOTTOM LEFT: Enemies remaining with panel
  // ==========================================================================

  const enemyText = `${state.enemies.length}`;
  const killText = `${state.totalEnemiesKilled}`;

  drawHUDPanel(ctx, padding - 5, ARENA_HEIGHT - 38, 140, 30);

  ctx.fillStyle = '#FFFFFF';
  ctx.font = '13px sans-serif';
  ctx.textAlign = 'left';
  drawTextWithShadow(ctx, `Enemies: ${enemyText}`, padding + 5, ARENA_HEIGHT - 18);
  drawTextWithShadow(ctx, `Kills: ${killText}`, padding + 75, ARENA_HEIGHT - 18);

  // ==========================================================================
  // BOTTOM RIGHT: Game time with panel
  // ==========================================================================

  const minutes = Math.floor(state.gameTime / 60000);
  const seconds = Math.floor((state.gameTime % 60000) / 1000);
  const timeText = `${minutes}:${seconds.toString().padStart(2, '0')}`;

  ctx.font = 'bold 16px sans-serif';
  const timeTextWidth = ctx.measureText(timeText).width;

  drawHUDPanel(ctx, ARENA_WIDTH - padding - timeTextWidth - 25, ARENA_HEIGHT - 38, timeTextWidth + 30, 30);

  ctx.fillStyle = '#FFFFFF';
  ctx.font = 'bold 16px sans-serif';
  ctx.textAlign = 'right';
  drawTextWithShadow(ctx, timeText, ARENA_WIDTH - padding - 5, ARENA_HEIGHT - 17);
}

// =============================================================================
// Run 036: Melee Attack Rendering
// =============================================================================

/**
 * Render the Mandible Reaver melee attack arc
 * Visual: Amber/gold arc sweep with mandible trail effect
 */
function renderMeleeAttack(
  ctx: CanvasRenderingContext2D,
  playerPos: { x: number; y: number },
  meleeState: MeleeAttackState,
  gameTime: number
) {
  // Only render during active phases
  if (!meleeState.isActive && !meleeState.isInWindup && !meleeState.isInRecovery) {
    return;
  }

  const { phase, progress } = getAttackProgress(meleeState, gameTime);

  ctx.save();

  // Get arc points for rendering
  const arcPoints = getArcRenderPoints(playerPos, meleeState.direction, MANDIBLE_REAVER_CONFIG, 16);

  // Phase-specific rendering
  if (phase === 'windup') {
    // Windup: Faint preview of arc
    ctx.globalAlpha = 0.3 * progress;
    ctx.strokeStyle = '#FFB000';
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i < arcPoints.length; i++) {
      if (i === 0) {
        ctx.moveTo(arcPoints[i].x, arcPoints[i].y);
      } else {
        ctx.lineTo(arcPoints[i].x, arcPoints[i].y);
      }
    }
    ctx.stroke();
  } else if (phase === 'active') {
    // Active: Full arc with amber fill and golden edge
    const attackAlpha = 1 - progress * 0.5; // Fade as attack completes

    // Fill the arc
    ctx.globalAlpha = attackAlpha * 0.4;
    ctx.fillStyle = '#FFB000';
    ctx.beginPath();
    for (let i = 0; i < arcPoints.length; i++) {
      if (i === 0) {
        ctx.moveTo(arcPoints[i].x, arcPoints[i].y);
      } else {
        ctx.lineTo(arcPoints[i].x, arcPoints[i].y);
      }
    }
    ctx.closePath();
    ctx.fill();

    // Edge glow
    ctx.globalAlpha = attackAlpha;
    ctx.strokeStyle = '#FFD700';
    ctx.lineWidth = 3;
    ctx.shadowColor = '#FFD700';
    ctx.shadowBlur = 10;
    ctx.beginPath();
    // Only draw the arc edge (skip the lines back to center)
    for (let i = 1; i < arcPoints.length - 1; i++) {
      if (i === 1) {
        ctx.moveTo(arcPoints[i].x, arcPoints[i].y);
      } else {
        ctx.lineTo(arcPoints[i].x, arcPoints[i].y);
      }
    }
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Mandible "teeth" at the arc edge (for that bee theme)
    const teethCount = 5;
    ctx.fillStyle = '#FFD700';
    ctx.globalAlpha = attackAlpha * 0.8;
    for (let i = 0; i < teethCount; i++) {
      const t = (i + 0.5) / teethCount;
      const idx = Math.floor(1 + t * (arcPoints.length - 3));
      if (idx < arcPoints.length - 1) {
        const toothPos = arcPoints[idx];
        const nextPos = arcPoints[idx + 1] || toothPos;

        // Tooth direction (outward from arc)
        const dx = toothPos.x - playerPos.x;
        const dy = toothPos.y - playerPos.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist > 0) {
          const nx = dx / dist;
          const ny = dy / dist;
          const toothLength = 8;

          ctx.beginPath();
          ctx.moveTo(toothPos.x, toothPos.y);
          ctx.lineTo(toothPos.x + nx * toothLength, toothPos.y + ny * toothLength);
          ctx.lineTo(nextPos.x, nextPos.y);
          ctx.fill();
        }
      }
    }
  } else if (phase === 'recovery') {
    // Recovery: Fading afterglow
    ctx.globalAlpha = 0.2 * (1 - progress);
    ctx.strokeStyle = '#FFB000';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i < arcPoints.length; i++) {
      if (i === 0) {
        ctx.moveTo(arcPoints[i].x, arcPoints[i].y);
      } else {
        ctx.lineTo(arcPoints[i].x, arcPoints[i].y);
      }
    }
    ctx.stroke();
  }

  ctx.restore();
}

// =============================================================================
// Shape Helpers
// =============================================================================

/**
 * Draw a honeycomb hexagonal grid pattern.
 * Creates a subtle, bee-themed background that tiles seamlessly.
 */
function drawHoneycombGrid(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  hexSize: number,
  color: string
) {
  // Hexagon dimensions for pointy-top orientation
  const hexWidth = hexSize * 2;
  const hexHeight = Math.sqrt(3) * hexSize;

  ctx.strokeStyle = color;
  ctx.lineWidth = 1;

  // Draw honeycomb pattern - offset every other column
  const cols = Math.ceil(width / (hexWidth * 0.75)) + 2;
  const rows = Math.ceil(height / hexHeight) + 2;

  for (let col = -1; col < cols; col++) {
    for (let row = -1; row < rows; row++) {
      // Horizontal offset for honeycomb stagger
      const x = col * hexWidth * 0.75;
      // Vertical offset - alternate columns shifted by half hex height
      const y = row * hexHeight + (col % 2 ? hexHeight / 2 : 0);

      drawHexagon(ctx, x, y, hexSize);
    }
  }
}

/**
 * Draw a single hexagon (pointy-top orientation).
 */
function drawHexagon(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  size: number
) {
  ctx.beginPath();
  for (let i = 0; i < 6; i++) {
    // Pointy-top hexagon: start at top (offset by -PI/2)
    const angle = (Math.PI / 3) * i - Math.PI / 2;
    const px = x + size * Math.cos(angle);
    const py = y + size * Math.sin(angle);
    if (i === 0) {
      ctx.moveTo(px, py);
    } else {
      ctx.lineTo(px, py);
    }
  }
  ctx.closePath();
  ctx.stroke();
}

function drawTriangle(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  radius: number
) {
  ctx.beginPath();
  ctx.moveTo(x, y - radius);
  ctx.lineTo(x - radius * 0.866, y + radius * 0.5);
  ctx.lineTo(x + radius * 0.866, y + radius * 0.5);
  ctx.closePath();
}

function drawOctagon(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  radius: number
) {
  ctx.beginPath();
  for (let i = 0; i < 8; i++) {
    const angle = (Math.PI * 2 * i) / 8 - Math.PI / 8;
    const px = x + Math.cos(angle) * radius;
    const py = y + Math.sin(angle) * radius;
    if (i === 0) {
      ctx.moveTo(px, py);
    } else {
      ctx.lineTo(px, py);
    }
  }
  ctx.closePath();
}

/**
 * DD-24: Diamond shape for Spitter (ranged enemy)
 */
function drawDiamond(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  radius: number
) {
  ctx.beginPath();
  ctx.moveTo(x, y - radius);       // Top
  ctx.lineTo(x + radius, y);        // Right
  ctx.lineTo(x, y + radius);        // Bottom
  ctx.lineTo(x - radius, y);        // Left
  ctx.closePath();
}

// =============================================================================
// Visual Upgrade: Hornet Player Drawing Helpers
// "Ukiyo-e meets arcade brutalism" - HORNET_SPRITE_SPEC.md
// =============================================================================

/**
 * Draw hornet mandibles - the signature feature.
 * "Mandibles should NEVER fully close during idle. Always a gap."
 *
 * @param openAmount - 0 = idle (slightly parted), 1 = attack (wide open)
 */
function drawMandibles(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  radius: number,
  openAmount: number,
  color: string,
  direction: { x: number; y: number } | null = null
) {
  ctx.save();

  // Calculate facing direction (default: down/forward)
  let angle = Math.PI / 2; // Default facing down
  if (direction && (direction.x !== 0 || direction.y !== 0)) {
    angle = Math.atan2(direction.y, direction.x);
  }

  ctx.translate(x, y);
  ctx.rotate(angle - Math.PI / 2); // Rotate so mandibles face movement direction

  // Mandible parameters
  const mandibleLength = radius * 0.7;
  const mandibleWidth = radius * 0.25;
  const baseSpread = 0.15; // Idle spread (never fully closed)
  const maxSpread = 0.6;   // Attack spread (wide open)
  const spread = baseSpread + (maxSpread - baseSpread) * openAmount;

  ctx.fillStyle = color;

  // Left mandible (pincer shape)
  ctx.save();
  ctx.rotate(-spread);
  ctx.beginPath();
  ctx.moveTo(0, radius * 0.3);
  ctx.lineTo(-mandibleWidth * 0.5, radius * 0.3 + mandibleLength * 0.3);
  ctx.lineTo(-mandibleWidth * 0.3, radius * 0.3 + mandibleLength);
  ctx.lineTo(mandibleWidth * 0.2, radius * 0.3 + mandibleLength * 0.8);
  ctx.lineTo(mandibleWidth * 0.3, radius * 0.3);
  ctx.closePath();
  ctx.fill();
  ctx.restore();

  // Right mandible (mirrored)
  ctx.save();
  ctx.rotate(spread);
  ctx.beginPath();
  ctx.moveTo(0, radius * 0.3);
  ctx.lineTo(mandibleWidth * 0.5, radius * 0.3 + mandibleLength * 0.3);
  ctx.lineTo(mandibleWidth * 0.3, radius * 0.3 + mandibleLength);
  ctx.lineTo(-mandibleWidth * 0.2, radius * 0.3 + mandibleLength * 0.8);
  ctx.lineTo(-mandibleWidth * 0.3, radius * 0.3);
  ctx.closePath();
  ctx.fill();
  ctx.restore();

  // Mandible gleam (only during attack)
  if (openAmount > 0.5) {
    ctx.fillStyle = '#FFE55C'; // Pale yellow gleam
    ctx.save();
    ctx.rotate(-spread);
    ctx.beginPath();
    ctx.arc(-mandibleWidth * 0.2, radius * 0.3 + mandibleLength * 0.5, 1.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    ctx.save();
    ctx.rotate(spread);
    ctx.beginPath();
    ctx.arc(mandibleWidth * 0.2, radius * 0.3 + mandibleLength * 0.5, 1.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  ctx.restore();
}

/**
 * Draw antenna pair for scout bees.
 * "Antennae visibly alert (wiggling)"
 */
function drawAntennae(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  radius: number,
  phase: number,
  color: string
) {
  ctx.save();
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.5;
  ctx.lineCap = 'round';

  const antennaLength = radius * 0.8;
  const wiggle = Math.sin(phase) * 0.15;

  // Left antenna
  ctx.beginPath();
  ctx.moveTo(x - radius * 0.25, y - radius * 0.7);
  ctx.quadraticCurveTo(
    x - radius * 0.5 + wiggle * radius,
    y - radius * 1.2,
    x - radius * 0.4 + wiggle * radius * 2,
    y - radius * 0.7 - antennaLength
  );
  ctx.stroke();

  // Left antenna tip (ball)
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(
    x - radius * 0.4 + wiggle * radius * 2,
    y - radius * 0.7 - antennaLength,
    2,
    0,
    Math.PI * 2
  );
  ctx.fill();

  // Right antenna
  ctx.beginPath();
  ctx.moveTo(x + radius * 0.25, y - radius * 0.7);
  ctx.quadraticCurveTo(
    x + radius * 0.5 - wiggle * radius,
    y - radius * 1.2,
    x + radius * 0.4 - wiggle * radius * 2,
    y - radius * 0.7 - antennaLength
  );
  ctx.stroke();

  // Right antenna tip (ball)
  ctx.beginPath();
  ctx.arc(
    x + radius * 0.4 - wiggle * radius * 2,
    y - radius * 0.7 - antennaLength,
    2,
    0,
    Math.PI * 2
  );
  ctx.fill();

  ctx.restore();
}

/**
 * Draw hornet wing blur effect.
 * "Wing Blur Circles - Semi-transparent overlapping ellipses pulsing at 60hz"
 */
function drawHornetWings(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  radius: number,
  gameTime: number,
  wingColor: string
) {
  ctx.save();

  // Wing animation phase (faster than bee wings - hornet is POWER)
  const wingPhase = Math.sin(gameTime * 0.04); // Faster oscillation
  const wingAlpha = 0.35 + wingPhase * 0.15;

  // Parse wing color and create rgba
  const r = parseInt(wingColor.slice(1, 3), 16);
  const g = parseInt(wingColor.slice(3, 5), 16);
  const b = parseInt(wingColor.slice(5, 7), 16);

  ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${wingAlpha})`;
  ctx.globalAlpha = wingAlpha;

  // Left wing - larger, more prominent than bee wings
  ctx.beginPath();
  ctx.ellipse(
    x - radius * 1.0,
    y - radius * 0.2,
    radius * 0.9,
    radius * 0.35,
    -Math.PI * 0.2 + wingPhase * 0.12,
    0,
    Math.PI * 2
  );
  ctx.fill();

  // Right wing - mirrored
  ctx.beginPath();
  ctx.ellipse(
    x + radius * 1.0,
    y - radius * 0.2,
    radius * 0.9,
    radius * 0.35,
    Math.PI * 0.2 - wingPhase * 0.12,
    0,
    Math.PI * 2
  );
  ctx.fill();

  // Wing highlight (blur edge)
  ctx.globalAlpha = wingAlpha * 0.3;
  ctx.strokeStyle = `rgba(255, 255, 255, 0.3)`;
  ctx.lineWidth = 1;

  ctx.beginPath();
  ctx.ellipse(
    x - radius * 1.0,
    y - radius * 0.2,
    radius * 0.9,
    radius * 0.35,
    -Math.PI * 0.2 + wingPhase * 0.12,
    0,
    Math.PI * 2
  );
  ctx.stroke();

  ctx.beginPath();
  ctx.ellipse(
    x + radius * 1.0,
    y - radius * 0.2,
    radius * 0.9,
    radius * 0.35,
    Math.PI * 0.2 - wingPhase * 0.12,
    0,
    Math.PI * 2
  );
  ctx.stroke();

  ctx.restore();
}

/**
 * Draw hornet eyes with gleam.
 * "Eyes: Large, kidney-shaped, not circular. PREDATOR eyes."
 */
function drawHornetEyes(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  radius: number,
  eyeColor: string
) {
  ctx.save();

  const eyeRadius = radius * 0.18;
  const eyeOffsetX = radius * 0.35;
  const eyeOffsetY = radius * 0.15;

  // Left eye (kidney-shaped via ellipse + rotation)
  ctx.fillStyle = eyeColor;
  ctx.beginPath();
  ctx.ellipse(
    x - eyeOffsetX,
    y - eyeOffsetY,
    eyeRadius * 1.2,
    eyeRadius * 0.8,
    -0.3,
    0,
    Math.PI * 2
  );
  ctx.fill();

  // Right eye (mirrored)
  ctx.beginPath();
  ctx.ellipse(
    x + eyeOffsetX,
    y - eyeOffsetY,
    eyeRadius * 1.2,
    eyeRadius * 0.8,
    0.3,
    0,
    Math.PI * 2
  );
  ctx.fill();

  // Eye gleam (single pixel of white on each eye)
  ctx.fillStyle = '#FFFFFF';
  ctx.beginPath();
  ctx.arc(x - eyeOffsetX - eyeRadius * 0.3, y - eyeOffsetY - eyeRadius * 0.2, 1.5, 0, Math.PI * 2);
  ctx.fill();

  ctx.beginPath();
  ctx.arc(x + eyeOffsetX - eyeRadius * 0.3, y - eyeOffsetY - eyeRadius * 0.2, 1.5, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
}

/**
 * Draw hornet body stripes.
 * "3 bands minimum - distinct orange/black BANDS on abdomen"
 */
function drawHornetStripes(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  radius: number,
  stripeColor: string
) {
  ctx.save();
  ctx.fillStyle = stripeColor;

  const stripeWidth = radius * 0.22;
  const stripeSpacing = radius * 0.35;

  // 3 horizontal stripes on lower body (abdomen area)
  for (let i = 0; i < 3; i++) {
    const stripeY = y + radius * 0.1 + i * stripeSpacing;
    ctx.fillRect(
      x - radius * 0.65,
      stripeY - stripeWidth * 0.4,
      radius * 1.3,
      stripeWidth * 0.7
    );
  }

  ctx.restore();
}

// =============================================================================
// DD-21: Telegraph Rendering
// =============================================================================

/**
 * Render all enemy telegraphs (attack warnings)
 * DD-22: Visual telegraph system
 * RUN 036: Enhanced telegraphs - MORE READABLE, MORE SPECTACULAR
 */
function renderTelegraphs(ctx: CanvasRenderingContext2D, state: GameState) {
  for (const enemy of state.enemies) {
    // Cast to extended enemy type with behavior state
    const telegraph = getBeeTelegraph(enemy as Parameters<typeof getBeeTelegraph>[0], state.gameTime);
    if (!telegraph) continue;

    const config = BEE_BEHAVIORS[enemy.type];
    const { progress, color } = telegraph;

    // RUN 036: Shake during final 20% of telegraph
    const isFinalPhase = progress > 0.8;
    const shakeAmount = isFinalPhase ? 2 * (progress - 0.8) / 0.2 : 0;
    const shakeX = (Math.random() - 0.5) * shakeAmount;
    const shakeY = (Math.random() - 0.5) * shakeAmount;

    ctx.save();
    ctx.translate(shakeX, shakeY);

    switch (telegraph.type) {
      case 'swarm': {
        // RUN 036: Worker swarm - pulsing rings that expand outward
        const baseRadius = enemy.radius * 1.5;
        const maxRadius = enemy.radius * 3;

        // Multiple expanding rings
        for (let i = 0; i < 3; i++) {
          const ringProgress = (progress + i * 0.33) % 1;
          const ringRadius = baseRadius + (maxRadius - baseRadius) * ringProgress;
          const ringAlpha = (1 - ringProgress) * 0.4;

          ctx.globalAlpha = ringAlpha;
          ctx.strokeStyle = color;
          ctx.lineWidth = 2 + (1 - ringProgress) * 2;
          ctx.beginPath();
          ctx.arc(enemy.position.x, enemy.position.y, ringRadius, 0, Math.PI * 2);
          ctx.stroke();
        }

        // Core glow (enhanced)
        const glowRadius = enemy.radius * (1.5 + progress * 0.5);
        const gradient = ctx.createRadialGradient(
          enemy.position.x, enemy.position.y, 0,
          enemy.position.x, enemy.position.y, glowRadius
        );
        gradient.addColorStop(0, `${color}CC`);
        gradient.addColorStop(0.4, `${color}88`);
        gradient.addColorStop(0.8, `${color}44`);
        gradient.addColorStop(1, 'transparent');
        ctx.globalAlpha = 0.8 + progress * 0.2;
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(enemy.position.x, enemy.position.y, glowRadius, 0, Math.PI * 2);
        ctx.fill();
        break;
      }

      case 'sting': {
        // RUN 036: Scout sting - motion lines + speed anticipation
        if (telegraph.direction) {
          const stingDistance = config.attackParams.distance ?? 80;
          const lineLength = stingDistance * progress;

          const endX = enemy.position.x + telegraph.direction.x * lineLength;
          const endY = enemy.position.y + telegraph.direction.y * lineLength;

          // Motion blur lines (3 parallel lines with offset)
          for (let i = -1; i <= 1; i++) {
            const perpX = -telegraph.direction.y * i * 3;
            const perpY = telegraph.direction.x * i * 3;
            const lineAlpha = i === 0 ? 0.8 : 0.3;

            ctx.globalAlpha = (0.6 + progress * 0.4) * lineAlpha;
            ctx.strokeStyle = color;
            ctx.lineWidth = i === 0 ? 5 : 2;
            ctx.lineCap = 'round';

            ctx.beginPath();
            ctx.moveTo(enemy.position.x + perpX, enemy.position.y + perpY);
            ctx.lineTo(endX + perpX, endY + perpY);
            ctx.stroke();
          }

          // Speed streaks behind the line
          const numStreaks = 4;
          for (let i = 0; i < numStreaks; i++) {
            const streakProgress = (progress * 2 + i * 0.15) % 1;
            const streakLength = lineLength * 0.3;
            const streakStart = lineLength * streakProgress;

            const streakStartX = enemy.position.x + telegraph.direction.x * streakStart;
            const streakStartY = enemy.position.y + telegraph.direction.y * streakStart;
            const streakEndX = streakStartX - telegraph.direction.x * streakLength;
            const streakEndY = streakStartY - telegraph.direction.y * streakLength;

            ctx.globalAlpha = (1 - streakProgress) * 0.5;
            ctx.strokeStyle = '#FFFFFF';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(streakStartX, streakStartY);
            ctx.lineTo(streakEndX, streakEndY);
            ctx.stroke();
          }

          // Enhanced arrow head with glow
          const headLen = 15;
          const angle = Math.atan2(telegraph.direction.y, telegraph.direction.x);

          ctx.globalAlpha = 1;
          ctx.strokeStyle = '#FFFFFF';
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.moveTo(endX, endY);
          ctx.lineTo(
            endX - headLen * Math.cos(angle - Math.PI / 6),
            endY - headLen * Math.sin(angle - Math.PI / 6)
          );
          ctx.moveTo(endX, endY);
          ctx.lineTo(
            endX - headLen * Math.cos(angle + Math.PI / 6),
            endY - headLen * Math.sin(angle + Math.PI / 6)
          );
          ctx.stroke();
        }
        break;
      }

      case 'block': {
        // RUN 036: Guard block - fill from center outward
        const radius = telegraph.radius ?? config.attackParams.radius ?? 50;
        const pulseRadius = radius * (0.8 + progress * 0.2);
        const fillRadius = radius * progress; // Fill grows with progress

        // Filled center (grows from 0 to full radius)
        const fillGradient = ctx.createRadialGradient(
          enemy.position.x, enemy.position.y, 0,
          enemy.position.x, enemy.position.y, fillRadius
        );
        fillGradient.addColorStop(0, `${color}66`);
        fillGradient.addColorStop(0.7, `${color}33`);
        fillGradient.addColorStop(1, `${color}11`);
        ctx.globalAlpha = 0.6 + progress * 0.4;
        ctx.fillStyle = fillGradient;
        ctx.beginPath();
        ctx.arc(enemy.position.x, enemy.position.y, fillRadius, 0, Math.PI * 2);
        ctx.fill();

        // Outer ring (pulsing)
        ctx.globalAlpha = 0.5 + progress * 0.5;
        ctx.strokeStyle = color;
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(enemy.position.x, enemy.position.y, pulseRadius, 0, Math.PI * 2);
        ctx.stroke();

        // Warning ring (white flash at high progress)
        if (progress > 0.7) {
          ctx.globalAlpha = (progress - 0.7) / 0.3;
          ctx.strokeStyle = '#FFFFFF';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(enemy.position.x, enemy.position.y, pulseRadius + 3, 0, Math.PI * 2);
          ctx.stroke();
        }
        break;
      }

      case 'sticky': {
        // RUN 036: Enhanced laser with glow and rotating reticle
        if (telegraph.targetPosition) {
          const dx = telegraph.targetPosition.x - enemy.position.x;
          const dy = telegraph.targetPosition.y - enemy.position.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          const laserLength = Math.max(dist * 1.5, 200);
          const laserEndX = enemy.position.x + (dx / dist) * laserLength;
          const laserEndY = enemy.position.y + (dy / dist) * laserLength;

          // Laser glow (Run 036 fix: reset setLineDash immediately after stroke)
          ctx.globalAlpha = 0.2 + progress * 0.3;
          ctx.strokeStyle = color;
          ctx.lineWidth = 8;
          ctx.setLineDash([8, 4]);
          ctx.beginPath();
          ctx.moveTo(enemy.position.x, enemy.position.y);
          ctx.lineTo(laserEndX, laserEndY);
          ctx.stroke();
          ctx.setLineDash([]);  // Reset immediately to prevent leak

          // Main laser (solid, no dash)
          ctx.globalAlpha = 0.5 + progress * 0.5;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(enemy.position.x, enemy.position.y);
          ctx.lineTo(laserEndX, laserEndY);
          ctx.stroke();

          // Enhanced targeting reticle with rotation
          const reticleRotation = state.gameTime * 0.003;
          ctx.globalAlpha = 0.8 + progress * 0.2;

          // Outer ring
          ctx.beginPath();
          ctx.arc(telegraph.targetPosition.x, telegraph.targetPosition.y, 12, 0, Math.PI * 2);
          ctx.stroke();

          // Rotating cross
          ctx.save();
          ctx.translate(telegraph.targetPosition.x, telegraph.targetPosition.y);
          ctx.rotate(reticleRotation);
          const crossSize = 8;
          ctx.beginPath();
          ctx.moveTo(-crossSize, 0);
          ctx.lineTo(crossSize, 0);
          ctx.moveTo(0, -crossSize);
          ctx.lineTo(0, crossSize);
          ctx.stroke();
          ctx.restore();

          // Corner brackets
          const bracketSize = 16;
          const bracketThick = 3;
          ctx.lineWidth = 2;
          for (let i = 0; i < 4; i++) {
            const angle = (Math.PI / 2) * i + Math.PI / 4;
            const bx = telegraph.targetPosition.x + Math.cos(angle) * bracketSize;
            const by = telegraph.targetPosition.y + Math.sin(angle) * bracketSize;
            const ex1 = bx - Math.cos(angle - Math.PI / 4) * bracketThick;
            const ey1 = by - Math.sin(angle - Math.PI / 4) * bracketThick;
            const ex2 = bx - Math.cos(angle + Math.PI / 4) * bracketThick;
            const ey2 = by - Math.sin(angle + Math.PI / 4) * bracketThick;

            ctx.beginPath();
            ctx.moveTo(ex1, ey1);
            ctx.lineTo(bx, by);
            ctx.lineTo(ex2, ey2);
            ctx.stroke();
          }
        }
        break;
      }

      case 'elite': {
        // RUN 036: Royal elite - 3-phase indicator (charge → AOE → projectile)
        const phase = progress < 0.33 ? 'charge' : progress < 0.66 ? 'aoe' : 'projectile';

        // Phase colors
        const chargeColor = '#4488FF';  // Blue
        const aoeColor = '#FF8844';     // Orange
        const projectileColor = '#FF4444'; // Red

        // Phase 1: Charge glow
        if (progress < 0.33) {
          const phaseProgress = progress / 0.33;
          const glowRadius = enemy.radius * (1.5 + phaseProgress * 1);
          const gradient = ctx.createRadialGradient(
            enemy.position.x, enemy.position.y, 0,
            enemy.position.x, enemy.position.y, glowRadius
          );
          gradient.addColorStop(0, `${chargeColor}FF`);
          gradient.addColorStop(0.5, `${chargeColor}88`);
          gradient.addColorStop(1, 'transparent');
          ctx.globalAlpha = 0.6 + phaseProgress * 0.4;
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(enemy.position.x, enemy.position.y, glowRadius, 0, Math.PI * 2);
          ctx.fill();
        }

        // Phase 2: AOE expansion
        if (progress >= 0.33 && progress < 0.66) {
          const phaseProgress = (progress - 0.33) / 0.33;
          const aoeRadius = (telegraph.radius ?? 60) * phaseProgress;

          const gradient = ctx.createRadialGradient(
            enemy.position.x, enemy.position.y, 0,
            enemy.position.x, enemy.position.y, aoeRadius
          );
          gradient.addColorStop(0, `${aoeColor}44`);
          gradient.addColorStop(0.7, `${aoeColor}22`);
          gradient.addColorStop(1, 'transparent');
          ctx.globalAlpha = 0.7;
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(enemy.position.x, enemy.position.y, aoeRadius, 0, Math.PI * 2);
          ctx.fill();

          // AOE ring
          ctx.strokeStyle = aoeColor;
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.arc(enemy.position.x, enemy.position.y, aoeRadius, 0, Math.PI * 2);
          ctx.stroke();
        }

        // Phase 3: Projectile preparation
        if (progress >= 0.66) {
          const phaseProgress = (progress - 0.66) / 0.34;
          const maxRadius = telegraph.radius ?? 60;

          // Full AOE with projectile color
          const gradient = ctx.createRadialGradient(
            enemy.position.x, enemy.position.y, 0,
            enemy.position.x, enemy.position.y, maxRadius
          );
          gradient.addColorStop(0, `${projectileColor}88`);
          gradient.addColorStop(0.5, `${projectileColor}44`);
          gradient.addColorStop(1, 'transparent');
          ctx.globalAlpha = 0.8 + phaseProgress * 0.2;
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(enemy.position.x, enemy.position.y, maxRadius, 0, Math.PI * 2);
          ctx.fill();

          // Intense ring
          ctx.strokeStyle = projectileColor;
          ctx.lineWidth = 4;
          ctx.setLineDash([10, 5]);
          ctx.beginPath();
          ctx.arc(enemy.position.x, enemy.position.y, maxRadius, 0, Math.PI * 2);
          ctx.stroke();
          ctx.setLineDash([]);

          // Warning flash
          if (phaseProgress > 0.7) {
            ctx.globalAlpha = (phaseProgress - 0.7) / 0.3;
            ctx.strokeStyle = '#FFFFFF';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(enemy.position.x, enemy.position.y, maxRadius + 4, 0, Math.PI * 2);
            ctx.stroke();
          }
        }

        // Phase indicator ring segments
        ctx.globalAlpha = 0.9;
        const segmentRadius = enemy.radius + 25;
        const segmentStart = -Math.PI / 2;
        const segmentLength = (Math.PI * 2) / 3;

        for (let i = 0; i < 3; i++) {
          const segmentColor = i === 0 ? chargeColor : i === 1 ? aoeColor : projectileColor;
          const isActive = (i === 0 && phase === 'charge') ||
                          (i === 1 && phase === 'aoe') ||
                          (i === 2 && phase === 'projectile');

          ctx.strokeStyle = segmentColor;
          ctx.lineWidth = isActive ? 4 : 2;
          ctx.globalAlpha = isActive ? 1 : 0.3;
          ctx.beginPath();
          ctx.arc(
            enemy.position.x,
            enemy.position.y,
            segmentRadius,
            segmentStart + i * segmentLength,
            segmentStart + (i + 1) * segmentLength
          );
          ctx.stroke();
        }
        break;
      }
    }

    ctx.restore();
  }
}

// =============================================================================
// DD-36: Attack Phase Visual Effects (Run 036)
// =============================================================================

/**
 * Render spectacular attack phase animations.
 *
 * Attack types:
 * - Worker swarm: Speed lines behind the bee as it lunges
 * - Scout sting: Afterimage trail (3-4 fading copies behind)
 * - Guard block: Shockwave ring expanding from center
 * - Propolis sticky: Glow pulse when projectile fires
 * - Royal combo: Phase-colored aura (yellow → red → blue)
 *
 * Performance: Quick and punchy effects, < 2ms total budget
 */
function renderAttackEffects(ctx: CanvasRenderingContext2D, state: GameState) {
  for (const enemy of state.enemies) {
    const behaviorState = enemy.behaviorState ?? 'chase';
    if (behaviorState !== 'attack') continue;

    const config = BEE_BEHAVIORS[enemy.type];
    const stateStartTime = enemy.stateStartTime ?? state.gameTime;
    const timeInState = state.gameTime - stateStartTime;
    const attackProgress = Math.min(1, timeInState / config.attackDuration);

    ctx.save();

    switch (config.attackType) {
      case 'swarm': {
        // Worker swarm: Speed lines behind the bee during lunge
        if (enemy.attackDirection && attackProgress < 0.8) {
          const lineCount = 5;
          const lineLength = 20 + attackProgress * 40;
          const lineSpacing = enemy.radius * 0.4;

          ctx.strokeStyle = config.colors.attack;
          ctx.lineCap = 'round';

          for (let i = 0; i < lineCount; i++) {
            const offset = (i - lineCount / 2) * lineSpacing;
            const alpha = (1 - attackProgress) * (1 - i / lineCount) * 0.6;
            const lengthMultiplier = 1 - i / lineCount;

            // Perpendicular offset for spread
            const perpX = -enemy.attackDirection.y * offset;
            const perpY = enemy.attackDirection.x * offset;

            const startX = enemy.position.x + perpX - enemy.attackDirection.x * (i * 8);
            const startY = enemy.position.y + perpY - enemy.attackDirection.y * (i * 8);
            const endX = startX - enemy.attackDirection.x * lineLength * lengthMultiplier;
            const endY = startY - enemy.attackDirection.y * lineLength * lengthMultiplier;

            ctx.globalAlpha = alpha;
            ctx.lineWidth = 2 + (lineCount - i) * 0.5;
            ctx.beginPath();
            ctx.moveTo(startX, startY);
            ctx.lineTo(endX, endY);
            ctx.stroke();
          }
        }
        break;
      }

      case 'sting': {
        // Scout sting: Afterimage trail (4 fading copies)
        if (enemy.attackDirection && attackProgress < 0.9) {
          const afterimageCount = 4;
          const maxTrailDistance = 60;

          for (let i = 1; i <= afterimageCount; i++) {
            const trailProgress = i / afterimageCount;
            const trailDistance = maxTrailDistance * trailProgress * attackProgress;

            const imageX = enemy.position.x - enemy.attackDirection.x * trailDistance;
            const imageY = enemy.position.y - enemy.attackDirection.y * trailDistance;

            const alpha = (1 - trailProgress) * (1 - attackProgress * 0.5) * 0.5;
            const scale = 1 - trailProgress * 0.3;

            ctx.globalAlpha = alpha;
            ctx.fillStyle = enemy.color ?? config.colors.attack;
            ctx.beginPath();

            // Triangle shape for fast enemies
            const r = enemy.radius * scale;
            ctx.moveTo(imageX, imageY - r);
            ctx.lineTo(imageX - r * 0.866, imageY + r * 0.5);
            ctx.lineTo(imageX + r * 0.866, imageY + r * 0.5);
            ctx.closePath();
            ctx.fill();
          }
        }
        break;
      }

      case 'block': {
        // Guard block: Expanding shockwave ring at attack peak
        if (attackProgress >= 0.7) {
          const shockwaveProgress = (attackProgress - 0.7) / 0.3;
          const maxRadius = config.attackParams.radius ?? 50;
          const currentRadius = maxRadius * shockwaveProgress;
          const alpha = (1 - shockwaveProgress) * 0.8;

          // Primary shockwave
          ctx.globalAlpha = alpha;
          ctx.strokeStyle = config.colors.attack;
          ctx.lineWidth = 4 * (1 - shockwaveProgress * 0.5);
          ctx.beginPath();
          ctx.arc(enemy.position.x, enemy.position.y, currentRadius, 0, Math.PI * 2);
          ctx.stroke();

          // Secondary shockwave (delayed)
          if (shockwaveProgress > 0.3) {
            const secondaryProgress = (shockwaveProgress - 0.3) / 0.7;
            const secondaryRadius = maxRadius * secondaryProgress * 0.8;
            const secondaryAlpha = (1 - secondaryProgress) * 0.5;

            ctx.globalAlpha = secondaryAlpha;
            ctx.lineWidth = 3 * (1 - secondaryProgress * 0.5);
            ctx.beginPath();
            ctx.arc(enemy.position.x, enemy.position.y, secondaryRadius, 0, Math.PI * 2);
            ctx.stroke();
          }
        }
        break;
      }

      case 'sticky': {
        // Propolis: Glow pulse when firing projectile (early in attack phase)
        if (attackProgress < 0.3) {
          const pulseProgress = attackProgress / 0.3;
          const pulseIntensity = Math.sin(pulseProgress * Math.PI);

          // Charging glow
          const glowRadius = enemy.radius * (2 + pulseIntensity * 1.5);
          const gradient = ctx.createRadialGradient(
            enemy.position.x, enemy.position.y, 0,
            enemy.position.x, enemy.position.y, glowRadius
          );
          gradient.addColorStop(0, `${config.colors.attack}${Math.floor(pulseIntensity * 100).toString(16).padStart(2, '0')}`);
          gradient.addColorStop(0.5, `${config.colors.attack}${Math.floor(pulseIntensity * 50).toString(16).padStart(2, '0')}`);
          gradient.addColorStop(1, 'transparent');

          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(enemy.position.x, enemy.position.y, glowRadius, 0, Math.PI * 2);
          ctx.fill();

          // Energy particles spiraling around
          const particleCount = 6;
          for (let i = 0; i < particleCount; i++) {
            const angle = (i / particleCount) * Math.PI * 2 + pulseProgress * Math.PI * 4;
            const distance = enemy.radius * (1.5 - pulseProgress);
            const px = enemy.position.x + Math.cos(angle) * distance;
            const py = enemy.position.y + Math.sin(angle) * distance;

            ctx.globalAlpha = pulseIntensity * 0.8;
            ctx.fillStyle = config.colors.telegraph;
            ctx.beginPath();
            ctx.arc(px, py, 3, 0, Math.PI * 2);
            ctx.fill();
          }
        }
        break;
      }

      case 'combo': {
        // Royal combo: Phase-colored aura based on attack phase
        // Phase 1 (0-0.3): Yellow charge aura
        // Phase 2 (0.3-0.6): Red AOE aura
        // Phase 3 (0.6-1.0): Blue projectile aura

        let phaseColor: string;
        let auraPulse: number;

        if (attackProgress < 0.3) {
          // Yellow charging phase
          phaseColor = '#F4D03F';
          auraPulse = (attackProgress / 0.3);

          // Growing spiral aura
          const spiralRadius = enemy.radius * (1.5 + auraPulse * 1.5);
          const spiralCount = 3;

          for (let i = 0; i < spiralCount; i++) {
            const spiralOffset = (i / spiralCount) * Math.PI * 2;
            const angle = auraPulse * Math.PI * 4 + spiralOffset;

            ctx.globalAlpha = (1 - auraPulse) * 0.3;
            ctx.strokeStyle = phaseColor;
            ctx.lineWidth = 3;
            ctx.beginPath();

            for (let a = 0; a < Math.PI * 2; a += 0.2) {
              const r = spiralRadius * (0.5 + (a / (Math.PI * 2)) * 0.5);
              const x = enemy.position.x + Math.cos(angle + a) * r;
              const y = enemy.position.y + Math.sin(angle + a) * r;
              if (a === 0) ctx.moveTo(x, y);
              else ctx.lineTo(x, y);
            }
            ctx.stroke();
          }
        } else if (attackProgress < 0.6) {
          // Red AOE phase
          phaseColor = '#E74C3C';
          auraPulse = (attackProgress - 0.3) / 0.3;

          // Expanding red burst
          const burstRadius = (config.attackParams.radius ?? 60) * auraPulse;
          const gradient = ctx.createRadialGradient(
            enemy.position.x, enemy.position.y, 0,
            enemy.position.x, enemy.position.y, burstRadius
          );
          gradient.addColorStop(0, `${phaseColor}AA`);
          gradient.addColorStop(0.7, `${phaseColor}44`);
          gradient.addColorStop(1, 'transparent');

          ctx.globalAlpha = 1 - auraPulse * 0.5;
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(enemy.position.x, enemy.position.y, burstRadius, 0, Math.PI * 2);
          ctx.fill();
        } else {
          // Blue projectile phase
          phaseColor = '#3498DB';
          auraPulse = (attackProgress - 0.6) / 0.4;

          // Rotating energy orbs
          const orbCount = 4;
          const orbitRadius = enemy.radius * 2;

          for (let i = 0; i < orbCount; i++) {
            const angle = (i / orbCount) * Math.PI * 2 + auraPulse * Math.PI * 6;
            const orbX = enemy.position.x + Math.cos(angle) * orbitRadius;
            const orbY = enemy.position.y + Math.sin(angle) * orbitRadius;

            // Orb glow
            const orbGlow = ctx.createRadialGradient(orbX, orbY, 0, orbX, orbY, 8);
            orbGlow.addColorStop(0, phaseColor);
            orbGlow.addColorStop(0.5, `${phaseColor}88`);
            orbGlow.addColorStop(1, 'transparent');

            ctx.globalAlpha = 0.8;
            ctx.fillStyle = orbGlow;
            ctx.beginPath();
            ctx.arc(orbX, orbY, 8, 0, Math.PI * 2);
            ctx.fill();
          }
        }
        break;
      }
    }

    ctx.restore();
  }

  ctx.globalAlpha = 1.0;
}

// =============================================================================
// Run 036: THE BALL Formation Rendering
// =============================================================================

/**
 * Render THE BALL formation - the colony's coordinated sphere attack.
 *
 * Visual phases:
 * - FORMING: Orange ring growing, gap visible, warning pulses
 * - SILENCE: Ring turns ominous red, gap shrinking, tension builds
 * - CONSTRICTING: Ring tightens, heat waves appear, gap closing fast
 * - COOKING: Full heat, damage ticks visible, screen edge heat
 *
 * The gap is always visible as a green "escape route" indicator.
 */
function renderBall(ctx: CanvasRenderingContext2D, ballState: BallState, gameTime: number, enemies: Enemy[]) {
  const { phase, center, currentRadius, gapAngle, gapSize, phaseProgress, formationBeeIds, isFading, fadeProgress } = ballState;

  ctx.save();

  // ==========================================================================
  // RUN 039: Fade/Linger Opacity
  // When player escapes, ball fades but can revive if they return
  // ==========================================================================

  // Calculate base opacity based on fade state
  let baseOpacity = 1.0;
  if (isFading) {
    // Fade from 100% to 30% during linger period
    baseOpacity = 1.0 - fadeProgress * 0.7;
  } else if (ballState.isDissipating) {
    // Final dissipation: fade from 30% to 0%
    const dissipProgress = Math.min(1, (gameTime - ballState.dissipationStartTime) / 800);
    baseOpacity = 0.3 * (1 - dissipProgress);
  }

  // Store base opacity for use in all rendering
  const applyOpacity = (alpha: number) => baseOpacity * alpha;

  // Phase-based colors
  const phaseColors = {
    forming: { ring: '#FF8800', glow: '#FF8800', gap: '#00FF88' },
    silence: { ring: '#FF4444', glow: '#FF2222', gap: '#00FF88' },
    constrict: { ring: '#FF2222', glow: '#FF0000', gap: '#88FF88' },
    cooking: { ring: '#FF0000', glow: '#FF0000', gap: '#FFFFFF' },
  } as const;

  const colors = phaseColors[phase as keyof typeof phaseColors] ?? phaseColors.forming;

  // ==========================================================================
  // 1. OUTER GLOW (threat indicator)
  // ==========================================================================

  const glowIntensity = phase === 'cooking' ? 0.6 : phase === 'constrict' ? 0.4 : 0.25;
  const glowRadius = currentRadius + 30 + Math.sin(gameTime * 0.005) * 5;

  const outerGlow = ctx.createRadialGradient(
    center.x, center.y, currentRadius - 10,
    center.x, center.y, glowRadius
  );
  outerGlow.addColorStop(0, `${colors.glow}00`);
  outerGlow.addColorStop(0.5, `${colors.glow}${Math.floor(glowIntensity * 255).toString(16).padStart(2, '0')}`);
  outerGlow.addColorStop(1, `${colors.glow}00`);

  ctx.fillStyle = outerGlow;
  ctx.beginPath();
  ctx.arc(center.x, center.y, glowRadius, 0, Math.PI * 2);
  ctx.fill();

  // ==========================================================================
  // 2. THE RING (with gap)
  // ==========================================================================

  // Ring thickness based on phase
  const ringThickness = phase === 'cooking' ? 12 : phase === 'constrict' ? 8 : 6;

  // Draw the ring arc (excluding the gap)
  const gapStart = gapAngle - gapSize / 2;
  const gapEnd = gapAngle + gapSize / 2;

  // Ring pulse (with fade opacity)
  const pulseAlpha = 0.7 + Math.sin(gameTime * 0.008) * 0.2;

  ctx.strokeStyle = colors.ring;
  ctx.lineWidth = ringThickness;
  ctx.globalAlpha = applyOpacity(pulseAlpha);

  // Draw the ring in two arcs (before and after the gap)
  ctx.beginPath();
  ctx.arc(center.x, center.y, currentRadius, gapEnd, gapStart + Math.PI * 2);
  ctx.stroke();

  // ==========================================================================
  // 3. THE GAP (escape route indicator)
  // ==========================================================================

  if (gapSize > 0.05) { // Only show gap if it's meaningful
    // Gap highlight - green "exit" marker
    const gapMidAngle = gapAngle;
    const gapIndicatorRadius = currentRadius;

    // Draw gap arc in green
    ctx.strokeStyle = colors.gap;
    ctx.lineWidth = ringThickness + 4;
    ctx.globalAlpha = applyOpacity(0.4 + Math.sin(gameTime * 0.01) * 0.2);
    ctx.beginPath();
    ctx.arc(center.x, center.y, gapIndicatorRadius, gapStart, gapEnd);
    ctx.stroke();

    // Arrow pointing outward through the gap
    const arrowDist = currentRadius + 25;
    const arrowX = center.x + Math.cos(gapMidAngle) * arrowDist;
    const arrowY = center.y + Math.sin(gapMidAngle) * arrowDist;

    ctx.globalAlpha = applyOpacity(0.8);
    ctx.fillStyle = colors.gap;
    ctx.beginPath();
    const arrowLen = 12;
    const arrowWidth = 8;
    // Arrow pointing outward
    ctx.moveTo(
      arrowX + Math.cos(gapMidAngle) * arrowLen,
      arrowY + Math.sin(gapMidAngle) * arrowLen
    );
    ctx.lineTo(
      arrowX + Math.cos(gapMidAngle + Math.PI / 2) * arrowWidth,
      arrowY + Math.sin(gapMidAngle + Math.PI / 2) * arrowWidth
    );
    ctx.lineTo(
      arrowX + Math.cos(gapMidAngle - Math.PI / 2) * arrowWidth,
      arrowY + Math.sin(gapMidAngle - Math.PI / 2) * arrowWidth
    );
    ctx.closePath();
    ctx.fill();
  }

  // ==========================================================================
  // 4. HEAT WAVES (during constricting/cooking)
  // ==========================================================================

  if (phase === 'constrict' || phase === 'cooking') {
    const waveCount = phase === 'cooking' ? 4 : 2;
    const waveSpeed = phase === 'cooking' ? 0.006 : 0.004;

    for (let i = 0; i < waveCount; i++) {
      const waveProgress = ((gameTime * waveSpeed) + i / waveCount) % 1;
      const waveRadius = currentRadius * (0.3 + waveProgress * 0.7);
      const waveAlpha = (1 - waveProgress) * 0.4;

      ctx.strokeStyle = '#FF4400';
      ctx.lineWidth = 2;
      ctx.globalAlpha = waveAlpha;
      ctx.beginPath();
      ctx.arc(center.x, center.y, waveRadius, 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  // ==========================================================================
  // 5. COOKING DAMAGE INDICATOR (pulsing inner zone)
  // ==========================================================================

  if (phase === 'cooking') {
    const damageZoneRadius = currentRadius * 0.8;
    const damageAlpha = 0.2 + Math.sin(gameTime * 0.015) * 0.15;

    const damageGradient = ctx.createRadialGradient(
      center.x, center.y, 0,
      center.x, center.y, damageZoneRadius
    );
    damageGradient.addColorStop(0, `rgba(255, 0, 0, ${damageAlpha})`);
    damageGradient.addColorStop(0.7, `rgba(255, 100, 0, ${damageAlpha * 0.5})`);
    damageGradient.addColorStop(1, 'transparent');

    ctx.globalAlpha = 1;
    ctx.fillStyle = damageGradient;
    ctx.beginPath();
    ctx.arc(center.x, center.y, damageZoneRadius, 0, Math.PI * 2);
    ctx.fill();

    // Damage tick indicators (sparks around the inner edge)
    const sparkCount = 8;
    for (let i = 0; i < sparkCount; i++) {
      const sparkAngle = (i / sparkCount) * Math.PI * 2 + gameTime * 0.003;
      const sparkRadius = damageZoneRadius * (0.6 + Math.random() * 0.3);
      const sparkX = center.x + Math.cos(sparkAngle) * sparkRadius;
      const sparkY = center.y + Math.sin(sparkAngle) * sparkRadius;

      ctx.fillStyle = '#FFFF00';
      ctx.globalAlpha = 0.5 + Math.random() * 0.5;
      ctx.beginPath();
      ctx.arc(sparkX, sparkY, 2 + Math.random() * 2, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // ==========================================================================
  // 6. PHASE INDICATOR TEXT
  // ==========================================================================

  ctx.globalAlpha = 0.9;
  ctx.fillStyle = colors.ring;
  ctx.font = 'bold 14px sans-serif';
  ctx.textAlign = 'center';

  const phaseText = {
    forming: '⚠ THE BALL FORMING',
    silence: '⚠ SILENCE BEFORE STORM',
    constrict: '🔥 CONSTRICTING!',
    cooking: '💀 COOKING!',
  } as const;

  ctx.fillText(
    phaseText[phase as keyof typeof phaseText] ?? 'THE BALL',
    center.x,
    center.y - currentRadius - 20
  );

  // Progress bar
  const barWidth = 80;
  const barHeight = 6;
  const barX = center.x - barWidth / 2;
  const barY = center.y - currentRadius - 10;

  ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
  ctx.fillRect(barX, barY, barWidth, barHeight);

  ctx.fillStyle = colors.ring;
  ctx.fillRect(barX, barY, barWidth * phaseProgress, barHeight);

  // Bee count indicator
  ctx.font = '12px sans-serif';
  ctx.fillStyle = '#FFFFFF';
  ctx.globalAlpha = 0.7;
  ctx.fillText(
    `${formationBeeIds.length} bees`,
    center.x,
    center.y + currentRadius + 25
  );

  // ==========================================================================
  // 7. ACTIVE LUNGE INDICATOR (Run 036, updated Run 040 for pullback/charge)
  // ==========================================================================

  if (ballState.activeLunge) {
    const lunge = ballState.activeLunge;

    // Phase-aware progress calculation (RUN 040: expanded phases)
    let phaseProgress = 0;
    let showTrail = false;
    const isPullback = lunge.phase === 'pullback';
    const isCharge = lunge.phase === 'charge';
    const isWindup = lunge.phase === 'windup' || isPullback || isCharge;

    if (isPullback) {
      // Pullback: bee moves backward at normal speed
      phaseProgress = Math.min(1, (gameTime - lunge.windupStartTime) / 500);
      showTrail = false;
    } else if (isCharge) {
      // Charge: bee holds position, accelerating
      const chargeStart = lunge.windupStartTime + 500; // After pullback
      phaseProgress = Math.min(1, (gameTime - chargeStart) / 350);
      showTrail = false;
    } else if (lunge.phase === 'windup') {
      // Legacy windup support
      const windupDuration = lunge.lungeStartTime > 0
        ? lunge.lungeStartTime - lunge.windupStartTime
        : 850;
      phaseProgress = Math.min(1, (gameTime - lunge.windupStartTime) / windupDuration);
      showTrail = false;
    } else if (lunge.phase === 'lunge') {
      // Lunge: bee is attacking - show trail
      phaseProgress = Math.min(1, (gameTime - lunge.lungeStartTime) / lunge.duration);
      showTrail = true;
    } else if (lunge.phase === 'return') {
      // Return: bee is going back - trail fades
      phaseProgress = 1;
      showTrail = true;
    }

    // Calculate pullback position for rendering
    const dx = lunge.targetPos.x - lunge.startPos.x;
    const dy = lunge.targetPos.y - lunge.startPos.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const pullbackDist = 40; // BALL_LUNGE_CONFIG.pullbackDistance
    const pullbackPos = dist > 0 ? {
      x: lunge.startPos.x - (dx / dist) * pullbackDist,
      y: lunge.startPos.y - (dy / dist) * pullbackDist,
    } : lunge.startPos;

    if (showTrail) {
      // Draw lunge trail (red streak from pullback position to target)
      ctx.globalAlpha = lunge.phase === 'return' ? 0.3 : 0.6;
      ctx.strokeStyle = '#FF0000';
      ctx.lineWidth = 6;
      ctx.setLineDash([]);
      ctx.beginPath();
      ctx.moveTo(pullbackPos.x, pullbackPos.y);

      // Current lunge position
      const easedProgress = 1 - Math.pow(1 - phaseProgress, 3);
      const currentX = pullbackPos.x + (lunge.targetPos.x - pullbackPos.x) * easedProgress;
      const currentY = pullbackPos.y + (lunge.targetPos.y - pullbackPos.y) * easedProgress;
      ctx.lineTo(currentX, currentY);
      ctx.stroke();
    }

    // Draw pullback indicator (arrow showing bee moving backward)
    if (isPullback) {
      const bee = enemies.find(e => e.id === lunge.beeId);
      if (bee && dist > 0) {
        // Draw arrow showing pullback direction
        ctx.globalAlpha = 0.6;
        ctx.strokeStyle = '#FFAA00';
        ctx.lineWidth = 3;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(lunge.startPos.x, lunge.startPos.y);
        ctx.lineTo(pullbackPos.x, pullbackPos.y);
        ctx.stroke();
        ctx.setLineDash([]);

        // Small "retreating" indicator
        ctx.globalAlpha = 0.7;
        ctx.fillStyle = '#FFAA00';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('←', bee.position.x, bee.position.y - 25);
      }
    }

    // Draw charge indicator (intensifying glow at pullback position)
    if (isCharge) {
      const bee = enemies.find(e => e.id === lunge.beeId);
      if (bee) {
        // Vibrating charging effect
        const vibration = Math.sin(gameTime * 0.05) * 3 * phaseProgress;

        // Growing ring that fills as charge completes
        ctx.globalAlpha = 0.8;
        ctx.strokeStyle = '#FF4400';
        ctx.lineWidth = 3 + phaseProgress * 3;
        ctx.beginPath();
        ctx.arc(bee.position.x + vibration, bee.position.y, 15 + phaseProgress * 12, 0, Math.PI * 2);
        ctx.stroke();

        // Inner glow intensifies
        ctx.globalAlpha = 0.3 + phaseProgress * 0.5;
        ctx.fillStyle = '#FF6600';
        ctx.beginPath();
        ctx.arc(bee.position.x + vibration, bee.position.y, 12 + phaseProgress * 8, 0, Math.PI * 2);
        ctx.fill();

        // Charge percentage indicator
        ctx.globalAlpha = 1;
        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`${Math.floor(phaseProgress * 100)}%`, bee.position.x, bee.position.y + 4);
      }
    }

    // Draw legacy windup indicator
    if (lunge.phase === 'windup') {
      const bee = enemies.find(e => e.id === lunge.beeId);
      if (bee) {
        ctx.globalAlpha = 0.7;
        ctx.strokeStyle = '#FF4400';
        ctx.lineWidth = 3 + phaseProgress * 2;
        ctx.beginPath();
        ctx.arc(bee.position.x, bee.position.y, 15 + phaseProgress * 10, 0, Math.PI * 2 * phaseProgress);
        ctx.stroke();

        ctx.globalAlpha = 0.4 * phaseProgress;
        ctx.fillStyle = '#FF6600';
        ctx.beginPath();
        ctx.arc(bee.position.x, bee.position.y, 10 + phaseProgress * 5, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Draw impact ring at target (pulsing) - only during lunge phase
    if (lunge.phase === 'lunge') {
      const impactPulse = 1 + Math.sin(gameTime * 0.02) * 0.3;
      ctx.globalAlpha = 0.5 + phaseProgress * 0.5;
      ctx.strokeStyle = '#FF4444';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(lunge.targetPos.x, lunge.targetPos.y, 15 * impactPulse, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Draw "!" warning above the lunging bee (during all telegraph and lunge phases)
    if (isWindup || lunge.phase === 'lunge') {
      const bee = enemies.find(e => e.id === lunge.beeId);
      if (bee) {
        ctx.globalAlpha = 1;
        // Color progression: yellow (pullback) → orange (charge) → red (lunge)
        if (isPullback) {
          ctx.fillStyle = '#FFDD00';
        } else if (isCharge) {
          ctx.fillStyle = '#FF8800';
        } else if (lunge.phase === 'lunge') {
          ctx.fillStyle = '#FF0000';
        } else {
          ctx.fillStyle = '#FFAA00';
        }
        ctx.font = 'bold 20px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('!', bee.position.x, bee.position.y - 20);
      }
    }
  }

  // ==========================================================================
  // 8. FADE/LINGER INDICATOR (RUN 039)
  // Shows when ball is fading and can revive
  // ==========================================================================

  if (isFading) {
    // Ghost-like pulsing ring during fade
    const fadePulse = 0.3 + Math.sin(gameTime * 0.004) * 0.2;
    ctx.globalAlpha = fadePulse * (1 - fadeProgress);
    ctx.strokeStyle = '#AAAAFF';
    ctx.lineWidth = 3;
    ctx.setLineDash([8, 8]);
    ctx.beginPath();
    ctx.arc(center.x, center.y, currentRadius + 15, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);

    // "ESCAPING..." text with fade progress bar
    ctx.globalAlpha = 0.8 * (1 - fadeProgress * 0.5);
    ctx.fillStyle = '#88AAFF';
    ctx.font = 'bold 12px sans-serif';
    ctx.textAlign = 'center';

    // Show different text based on whether reviving or fading
    const fadePercent = Math.floor(fadeProgress * 100);
    ctx.fillText(
      fadePercent < 50 ? `THE BALL FADING... ${fadePercent}%` : `DISPERSING... ${fadePercent}%`,
      center.x,
      center.y + currentRadius + 45
    );

    // Fade progress bar (shows how close to full dispersal)
    const fadeBarWidth = 60;
    const fadeBarHeight = 4;
    const fadeBarX = center.x - fadeBarWidth / 2;
    const fadeBarY = center.y + currentRadius + 50;

    ctx.fillStyle = 'rgba(100, 150, 255, 0.3)';
    ctx.fillRect(fadeBarX, fadeBarY, fadeBarWidth, fadeBarHeight);

    ctx.fillStyle = '#88AAFF';
    ctx.fillRect(fadeBarX, fadeBarY, fadeBarWidth * fadeProgress, fadeBarHeight);
  }

  // Revive indicator (when player returns during fade)
  if (isFading && fadeProgress > 0 && fadeProgress < 0.5) {
    // Only show revive hint if they're close to saving it
    const revivePulse = 0.5 + Math.sin(gameTime * 0.01) * 0.3;
    ctx.globalAlpha = revivePulse;
    ctx.fillStyle = '#FFAA00';
    ctx.font = 'bold 10px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('⚠ BALL CAN REVIVE!', center.x, center.y - currentRadius - 35);
  }

  ctx.restore();
}

export default GameCanvas;
