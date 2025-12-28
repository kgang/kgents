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
import type { GameState } from '@kgents/shared-primitives';
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
import { getEnemyTelegraph, ENEMY_BEHAVIORS } from '../systems/enemies';

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
}

// =============================================================================
// Component
// =============================================================================

export function GameCanvas({ gameState, juiceSystem }: GameCanvasProps) {
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

    // Grid pattern with intensity-based color
    ctx.strokeStyle = intensityColors.grid;
    ctx.lineWidth = 1;
    const gridSize = 40;
    for (let x = 0; x <= ARENA_WIDTH; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, ARENA_HEIGHT);
      ctx.stroke();
    }
    for (let y = 0; y <= ARENA_HEIGHT; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(ARENA_WIDTH, y);
      ctx.stroke();
    }

    // DD-21: Render telegraphs (under enemies for visibility)
    renderTelegraphs(ctx, gameState);

    // Render projectiles (under everything)
    renderProjectiles(ctx, gameState);

    // Render enemies
    renderEnemies(ctx, gameState);

    // Render player
    renderPlayer(ctx, gameState);

    // Render particles (juice system)
    renderParticles(ctx, juiceSystem.particles);

    // DD-20: Health Vignette - render after game content, before HUD
    // (healthFraction already calculated above for intensity)
    renderVignette(ctx, healthFraction);

    ctx.restore();

    // Render HUD (not affected by shake)
    renderHUD(ctx, gameState, juiceSystem);
  }, [gameState, juiceSystem]);

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

function renderPlayer(ctx: CanvasRenderingContext2D, state: GameState) {
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

  // DD-15: Slow Field visual - subtle blue glow around player
  if (activeUpgrades?.slowRadius && activeUpgrades.slowRadius > 0) {
    const slowGradient = ctx.createRadialGradient(
      player.position.x,
      player.position.y,
      0,
      player.position.x,
      player.position.y,
      activeUpgrades.slowRadius
    );
    slowGradient.addColorStop(0, 'rgba(68, 221, 255, 0.05)');
    slowGradient.addColorStop(0.7, 'rgba(68, 221, 255, 0.1)');
    slowGradient.addColorStop(1, 'rgba(68, 221, 255, 0)');
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

  // DD-29-1: Breathing glow effect - radius and alpha pulse with breath
  const baseGlowRadius = player.radius * 2;
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
  gradient.addColorStop(0, `rgba(0, 212, 255, ${breathingGlowAlpha})`);
  gradient.addColorStop(1, 'rgba(0, 212, 255, 0)');
  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(player.position.x, player.position.y, breathingGlowRadius, 0, Math.PI * 2);
  ctx.fill();

  // Main body - slightly pulsing at low health
  const bodyScale = healthFraction < 0.25 ? (1.0 + breathPhase * 0.05) : 1.0;
  ctx.fillStyle = COLORS.player;
  ctx.beginPath();
  ctx.arc(player.position.x, player.position.y, player.radius * bodyScale, 0, Math.PI * 2);
  ctx.fill();

  // Inner highlight
  ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
  ctx.beginPath();
  ctx.arc(
    player.position.x - player.radius * 0.3,
    player.position.y - player.radius * 0.3,
    player.radius * 0.3,
    0,
    Math.PI * 2
  );
  ctx.fill();

  // Health bar above player
  const healthBarWidth = player.radius * 2.5;
  const healthBarHeight = 4;
  // (healthFraction already calculated above for breathing)
  const healthBarX = player.position.x - healthBarWidth / 2;
  const healthBarY = player.position.y - player.radius - 12;

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

    // Enemy glow (danger) with breathing
    const glowRadius = enemy.radius * 1.5 * glowMultiplier;
    const gradient = ctx.createRadialGradient(
      enemy.position.x,
      enemy.position.y,
      0,
      enemy.position.x,
      enemy.position.y,
      glowRadius
    );
    gradient.addColorStop(0, `rgba(255, 51, 102, ${glowAlpha})`);
    gradient.addColorStop(1, 'rgba(255, 51, 102, 0)');
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(enemy.position.x, enemy.position.y, glowRadius, 0, Math.PI * 2);
    ctx.fill();

    // Main body - faded during recovery
    const bodyAlpha = behaviorState === 'recovery' ? 0.6 : 1.0;
    ctx.globalAlpha = bodyAlpha;
    ctx.fillStyle = enemy.color;
    ctx.beginPath();

    // DD-21: Visual feedback for behavior state
    const isAttacking = behaviorState === 'attack';
    const isTelegraphing = behaviorState === 'telegraph';

    // Scale enemy when telegraphing (wind-up visual) - now with breathing too
    let drawRadius = enemy.radius;
    if (isTelegraphing) {
      drawRadius = enemy.radius * 1.2 * glowMultiplier;  // DD-22 + DD-29-1: Breathing during telegraph
    } else if (isAttacking) {
      drawRadius = enemy.radius * (1.0 + breathPhase * 0.1);  // Subtle pulsing during attack
    }

    // Different shapes for different types
    switch (enemy.type) {
      case 'basic':
        ctx.arc(enemy.position.x, enemy.position.y, drawRadius, 0, Math.PI * 2);
        break;
      case 'fast':
        // Triangle for fast enemies (Rusher)
        drawTriangle(ctx, enemy.position.x, enemy.position.y, drawRadius);
        break;
      case 'spitter':
        // DD-24: Diamond shape for ranged Spitter
        drawDiamond(ctx, enemy.position.x, enemy.position.y, drawRadius);
        break;
      case 'tank':
        // Square for tank enemies
        ctx.fillRect(
          enemy.position.x - drawRadius,
          enemy.position.y - drawRadius,
          drawRadius * 2,
          drawRadius * 2
        );
        break;
      case 'boss':
        // Larger octagon for boss
        drawOctagon(ctx, enemy.position.x, enemy.position.y, drawRadius);
        break;
      default:
        ctx.arc(enemy.position.x, enemy.position.y, drawRadius, 0, Math.PI * 2);
    }
    ctx.fill();

    // DD-21: Additional glow during attack
    if (isAttacking) {
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // Health bar for tanks and bosses
    if (enemy.type === 'tank' || enemy.type === 'boss') {
      const healthFraction = enemy.health / enemy.maxHealth;
      const healthBarWidth = enemy.radius * 2;
      const healthBarX = enemy.position.x - healthBarWidth / 2;
      const healthBarY = enemy.position.y - enemy.radius - 8;

      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.fillRect(healthBarX, healthBarY, healthBarWidth, 3);

      ctx.fillStyle = COLORS.enemy;
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
    }
  }

  ctx.globalAlpha = 1;
}

function renderHUD(
  ctx: CanvasRenderingContext2D,
  state: GameState,
  juiceSystem: JuiceSystem
) {
  const padding = 10;

  // Wave indicator (top left)
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 18px sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(`Wave ${state.wave}`, padding, 25);

  // Score (top right)
  ctx.textAlign = 'right';
  ctx.fillStyle = COLORS.xp;
  ctx.fillText(`Score: ${state.score}`, ARENA_WIDTH - padding, 25);

  // XP bar (below wave)
  const xpBarWidth = 150;
  const xpBarHeight = 8;
  const xpFraction = state.player.xp / state.player.xpToNextLevel;

  ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
  ctx.fillRect(padding, 35, xpBarWidth, xpBarHeight);

  ctx.fillStyle = COLORS.xp;
  ctx.fillRect(padding, 35, xpBarWidth * xpFraction, xpBarHeight);

  ctx.fillStyle = '#ffffff';
  ctx.font = '12px sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(`Level ${state.player.level}`, padding, 58);

  // Combo indicator (if active)
  if (juiceSystem.escalation.combo > 1) {
    ctx.fillStyle = COLORS.crisis;
    ctx.font = 'bold 24px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(
      `${juiceSystem.escalation.combo}x COMBO`,
      ARENA_WIDTH / 2,
      30
    );
  }

  // Enemies remaining (bottom)
  ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
  ctx.font = '12px sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(
    `Enemies: ${state.enemies.length} | Killed: ${state.totalEnemiesKilled}`,
    padding,
    ARENA_HEIGHT - padding
  );

  // Game time (bottom right)
  const minutes = Math.floor(state.gameTime / 60000);
  const seconds = Math.floor((state.gameTime % 60000) / 1000);
  ctx.textAlign = 'right';
  ctx.fillText(
    `${minutes}:${seconds.toString().padStart(2, '0')}`,
    ARENA_WIDTH - padding,
    ARENA_HEIGHT - padding
  );
}

// =============================================================================
// Shape Helpers
// =============================================================================

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
// DD-21: Telegraph Rendering
// =============================================================================

/**
 * Render all enemy telegraphs (attack warnings)
 * DD-22: Visual telegraph system
 */
function renderTelegraphs(ctx: CanvasRenderingContext2D, state: GameState) {
  for (const enemy of state.enemies) {
    const telegraph = getEnemyTelegraph(enemy, state.gameTime);
    if (!telegraph) continue;

    const config = ENEMY_BEHAVIORS[enemy.type];
    const { progress, color } = telegraph;

    ctx.save();

    switch (telegraph.type) {
      case 'lunge': {
        // DD-22: Red glow around enemy when lunging
        const glowRadius = enemy.radius * (1.5 + progress * 0.5);
        const gradient = ctx.createRadialGradient(
          enemy.position.x, enemy.position.y, 0,
          enemy.position.x, enemy.position.y, glowRadius
        );
        gradient.addColorStop(0, `${color}88`);
        gradient.addColorStop(0.6, `${color}44`);
        gradient.addColorStop(1, 'transparent');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(enemy.position.x, enemy.position.y, glowRadius, 0, Math.PI * 2);
        ctx.fill();
        break;
      }

      case 'charge': {
        // DD-22: Orange line indicator showing charge direction
        if (telegraph.direction) {
          const chargeDistance = config.attackParams.distance ?? 200;
          const lineLength = chargeDistance * progress;

          const endX = enemy.position.x + telegraph.direction.x * lineLength;
          const endY = enemy.position.y + telegraph.direction.y * lineLength;

          ctx.strokeStyle = color;
          ctx.lineWidth = 4;
          ctx.lineCap = 'round';
          ctx.globalAlpha = 0.6 + progress * 0.4;

          ctx.beginPath();
          ctx.moveTo(enemy.position.x, enemy.position.y);
          ctx.lineTo(endX, endY);
          ctx.stroke();

          // Arrow head
          const headLen = 10;
          const angle = Math.atan2(telegraph.direction.y, telegraph.direction.x);
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

      case 'stomp': {
        // DD-22: Red ground circle showing stomp AOE
        const radius = telegraph.radius ?? config.attackParams.radius ?? 60;
        const pulseRadius = radius * (0.8 + progress * 0.2);

        ctx.globalAlpha = 0.3 + progress * 0.4;
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(enemy.position.x, enemy.position.y, pulseRadius, 0, Math.PI * 2);
        ctx.stroke();

        ctx.fillStyle = `${color}22`;
        ctx.fill();
        break;
      }

      case 'aim': {
        // DD-22: Purple aim laser for Spitter
        if (telegraph.targetPosition) {
          const dx = telegraph.targetPosition.x - enemy.position.x;
          const dy = telegraph.targetPosition.y - enemy.position.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          const laserLength = Math.max(dist * 1.5, 200);
          const laserEndX = enemy.position.x + (dx / dist) * laserLength;
          const laserEndY = enemy.position.y + (dy / dist) * laserLength;

          ctx.globalAlpha = 0.4 + progress * 0.4;
          ctx.strokeStyle = color;
          ctx.lineWidth = 2;
          ctx.setLineDash([8, 4]);

          ctx.beginPath();
          ctx.moveTo(enemy.position.x, enemy.position.y);
          ctx.lineTo(laserEndX, laserEndY);
          ctx.stroke();
          ctx.setLineDash([]);

          // Targeting reticle
          ctx.globalAlpha = progress;
          ctx.beginPath();
          ctx.arc(telegraph.targetPosition.x, telegraph.targetPosition.y, 10, 0, Math.PI * 2);
          ctx.stroke();

          const crossSize = 6;
          ctx.beginPath();
          ctx.moveTo(telegraph.targetPosition.x - crossSize, telegraph.targetPosition.y);
          ctx.lineTo(telegraph.targetPosition.x + crossSize, telegraph.targetPosition.y);
          ctx.moveTo(telegraph.targetPosition.x, telegraph.targetPosition.y - crossSize);
          ctx.lineTo(telegraph.targetPosition.x, telegraph.targetPosition.y + crossSize);
          ctx.stroke();
        }
        break;
      }
    }

    ctx.restore();
  }
}

export default GameCanvas;
