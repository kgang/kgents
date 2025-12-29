/**
 * WASM Survivors - Camera System
 *
 * Handles camera zoom, pan, and focus for spectacle moments.
 * The camera is a key tool for making THE BALL clip-worthy.
 *
 * Modes:
 * - normal: Follow player, zoom 1.0
 * - spectacle: Pull back for THE BALL, focus on formation
 * - death: Zoom in on player, dramatic focus
 * - transition: Smooth blend between modes
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md (Phase 1: THE BALL Perfection)
 */

import type { Vector2 } from '../types';
import type { BallState, BallPhase } from './formation';
import type { ArcPhase } from './contrast';

// =============================================================================
// Types
// =============================================================================

/**
 * Camera operating modes
 */
export type CameraMode =
  | 'normal'      // Standard gameplay
  | 'spectacle'   // THE BALL or other major events
  | 'death'       // Death sequence
  | 'levelup';    // Level up pause

/**
 * Camera state
 */
export interface CameraState {
  // Current values
  zoom: number;           // 1.0 = normal view
  position: Vector2;      // Camera center in world coords
  rotation: number;       // Camera rotation (radians) - for death spiral

  // Target values for interpolation
  targetZoom: number;
  targetPosition: Vector2;
  targetRotation: number;

  // Mode
  mode: CameraMode;
  modeStartTime: number;

  // Shake (from juice system)
  shakeOffset: Vector2;

  // Constraints
  bounds: { minX: number; maxX: number; minY: number; maxY: number };
}

/**
 * Configuration for camera modes
 */
export const CAMERA_CONFIGS = {
  normal: {
    zoom: 1.0,
    followSpeed: 0.1,      // How fast camera follows player
    zoomSpeed: 0.05,       // How fast zoom transitions
  },

  spectacle: {
    zoom: 0.7,             // Pull back to show THE BALL
    followSpeed: 0.03,     // Slower, more cinematic
    zoomSpeed: 0.02,       // Slow zoom for drama
  },

  death: {
    zoom: 1.2,             // Zoom in for intimate moment
    followSpeed: 0.15,     // Quick snap
    zoomSpeed: 0.08,       // Faster zoom
    rotationSpeed: 0.1,    // For death spiral effect
  },

  levelup: {
    zoom: 1.0,             // No zoom change
    followSpeed: 0,        // Camera stops
    zoomSpeed: 0,
  },
} as const;

// =============================================================================
// Factory
// =============================================================================

/**
 * Create initial camera state
 */
export function createCameraState(
  arenaWidth: number,
  arenaHeight: number
): CameraState {
  const center = { x: arenaWidth / 2, y: arenaHeight / 2 };

  return {
    zoom: 1.0,
    position: { ...center },
    rotation: 0,

    targetZoom: 1.0,
    targetPosition: { ...center },
    targetRotation: 0,

    mode: 'normal',
    modeStartTime: 0,

    shakeOffset: { x: 0, y: 0 },

    bounds: {
      minX: 0,
      maxX: arenaWidth,
      minY: 0,
      maxY: arenaHeight,
    },
  };
}

// =============================================================================
// Core Logic
// =============================================================================

/**
 * Determine camera mode based on game state
 */
export function determineCameraMode(
  _currentMode: CameraMode,
  ballPhase: BallPhase,
  arcPhase: ArcPhase,
  gameStatus: string,
  isUpgrading: boolean
): CameraMode {
  // Death takes priority
  if (gameStatus === 'gameover') {
    return 'death';
  }

  // Level up pause
  if (isUpgrading) {
    return 'levelup';
  }

  // THE BALL spectacle
  if (ballPhase !== 'inactive') {
    return 'spectacle';
  }

  // Crisis phase might warrant slight pull-back
  if (arcPhase === 'TRAGEDY') {
    // Could be spectacle, but only if something dramatic is happening
    return 'normal'; // Default to normal during TRAGEDY unless BALL is active
  }

  return 'normal';
}

/**
 * Calculate target camera position based on mode and focus
 */
export function calculateCameraTarget(
  mode: CameraMode,
  playerPos: Vector2,
  ballState: BallState | null,
  arenaWidth: number,
  arenaHeight: number
): { targetZoom: number; targetPosition: Vector2; targetRotation: number } {
  const config = CAMERA_CONFIGS[mode];

  switch (mode) {
    case 'normal':
      return {
        targetZoom: config.zoom,
        targetPosition: { ...playerPos },
        targetRotation: 0,
      };

    case 'spectacle':
      if (ballState && ballState.phase !== 'inactive') {
        // Focus on ball formation, pulled back
        let zoom: number = config.zoom;
        let focusPoint = ballState.center;

        // Adjust based on ball phase
        if (ballState.phase === 'forming') {
          // Gradual pull-back during forming
          zoom = 1.0 - ballState.phaseProgress * 0.3;
        } else if (ballState.phase === 'constrict') {
          // Zoom back in slightly, focus toward gap
          zoom = 0.85;
          const gapOffset = 50;
          focusPoint = {
            x: ballState.center.x + Math.cos(ballState.gapAngle) * gapOffset,
            y: ballState.center.y + Math.sin(ballState.gapAngle) * gapOffset,
          };
        } else if (ballState.phase === 'cooking') {
          // Tight on the trapped player
          zoom = 1.1;
        }

        return {
          targetZoom: zoom,
          targetPosition: focusPoint,
          targetRotation: 0,
        };
      }

      // Default spectacle (no ball)
      return {
        targetZoom: config.zoom,
        targetPosition: { x: arenaWidth / 2, y: arenaHeight / 2 },
        targetRotation: 0,
      };

    case 'death':
      return {
        targetZoom: config.zoom,
        targetPosition: { ...playerPos },
        targetRotation: Math.PI * 0.1, // Slight tilt for drama
      };

    case 'levelup':
      return {
        targetZoom: config.zoom,
        targetPosition: { ...playerPos },
        targetRotation: 0,
      };

    default:
      return {
        targetZoom: 1.0,
        targetPosition: { ...playerPos },
        targetRotation: 0,
      };
  }
}

/**
 * Linear interpolation
 */
function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

/**
 * Vector linear interpolation
 */
function lerpVec(a: Vector2, b: Vector2, t: number): Vector2 {
  return {
    x: lerp(a.x, b.x, t),
    y: lerp(a.y, b.y, t),
  };
}

/**
 * Update camera state
 */
export function updateCamera(
  camera: CameraState,
  playerPos: Vector2,
  ballState: BallState | null,
  arcPhase: ArcPhase,
  gameStatus: string,
  isUpgrading: boolean,
  shakeOffset: Vector2,
  _deltaTime: number
): CameraState {
  // Determine mode
  const newMode = determineCameraMode(
    camera.mode,
    ballState?.phase ?? 'inactive',
    arcPhase,
    gameStatus,
    isUpgrading
  );

  // Get config for current mode
  const config = CAMERA_CONFIGS[newMode];

  // Calculate targets
  const { targetZoom, targetPosition, targetRotation } = calculateCameraTarget(
    newMode,
    playerPos,
    ballState,
    camera.bounds.maxX,
    camera.bounds.maxY
  );

  // Interpolate current values toward targets
  const newZoom = lerp(camera.zoom, targetZoom, config.zoomSpeed);
  const newPosition = lerpVec(camera.position, targetPosition, config.followSpeed);
  const rotationSpeed = 'rotationSpeed' in config ? (config as { rotationSpeed: number }).rotationSpeed : 0.05;
  const newRotation = lerp(camera.rotation, targetRotation, rotationSpeed);

  // Clamp position to bounds (accounting for zoom)
  const viewWidth = camera.bounds.maxX / newZoom;
  const viewHeight = camera.bounds.maxY / newZoom;
  const halfViewWidth = viewWidth / 2;
  const halfViewHeight = viewHeight / 2;

  const clampedPosition = {
    x: Math.max(halfViewWidth, Math.min(camera.bounds.maxX - halfViewWidth, newPosition.x)),
    y: Math.max(halfViewHeight, Math.min(camera.bounds.maxY - halfViewHeight, newPosition.y)),
  };

  return {
    ...camera,
    zoom: newZoom,
    position: clampedPosition,
    rotation: newRotation,
    targetZoom,
    targetPosition,
    targetRotation,
    mode: newMode,
    modeStartTime: newMode !== camera.mode ? Date.now() : camera.modeStartTime,
    shakeOffset,
  };
}

// =============================================================================
// Rendering Helpers
// =============================================================================

/**
 * Apply camera transform to canvas context
 *
 * Call at the start of render, before drawing anything.
 * Call resetCameraTransform() at the end.
 */
export function applyCameraTransform(
  ctx: CanvasRenderingContext2D,
  camera: CameraState,
  arenaWidth: number,
  arenaHeight: number
): void {
  ctx.save();

  // Move to center of canvas
  const centerX = arenaWidth / 2;
  const centerY = arenaHeight / 2;
  ctx.translate(centerX, centerY);

  // Apply rotation
  if (camera.rotation !== 0) {
    ctx.rotate(camera.rotation);
  }

  // Apply zoom
  ctx.scale(camera.zoom, camera.zoom);

  // Apply shake offset
  ctx.translate(camera.shakeOffset.x, camera.shakeOffset.y);

  // Offset by camera position (inverted because we're moving the world)
  ctx.translate(-camera.position.x + centerX / camera.zoom, -camera.position.y + centerY / camera.zoom);

  // Move back from center
  ctx.translate(-centerX / camera.zoom, -centerY / camera.zoom);
}

/**
 * Reset camera transform
 *
 * Call at the end of render.
 */
export function resetCameraTransform(ctx: CanvasRenderingContext2D): void {
  ctx.restore();
}

/**
 * Convert screen coordinates to world coordinates
 */
export function screenToWorld(
  screenPos: Vector2,
  camera: CameraState,
  arenaWidth: number,
  arenaHeight: number
): Vector2 {
  const centerX = arenaWidth / 2;
  const centerY = arenaHeight / 2;

  // Reverse the transform
  // 1. Translate from center
  let x = screenPos.x - centerX;
  let y = screenPos.y - centerY;

  // 2. Reverse rotation
  if (camera.rotation !== 0) {
    const cos = Math.cos(-camera.rotation);
    const sin = Math.sin(-camera.rotation);
    const rx = x * cos - y * sin;
    const ry = x * sin + y * cos;
    x = rx;
    y = ry;
  }

  // 3. Reverse zoom
  x /= camera.zoom;
  y /= camera.zoom;

  // 4. Reverse shake
  x -= camera.shakeOffset.x;
  y -= camera.shakeOffset.y;

  // 5. Add camera position offset
  x += camera.position.x;
  y += camera.position.y;

  return { x, y };
}

/**
 * Convert world coordinates to screen coordinates
 */
export function worldToScreen(
  worldPos: Vector2,
  camera: CameraState,
  arenaWidth: number,
  arenaHeight: number
): Vector2 {
  const centerX = arenaWidth / 2;
  const centerY = arenaHeight / 2;

  // Apply the transform
  // 1. Subtract camera position
  let x = worldPos.x - camera.position.x;
  let y = worldPos.y - camera.position.y;

  // 2. Add shake
  x += camera.shakeOffset.x;
  y += camera.shakeOffset.y;

  // 3. Apply zoom
  x *= camera.zoom;
  y *= camera.zoom;

  // 4. Apply rotation
  if (camera.rotation !== 0) {
    const cos = Math.cos(camera.rotation);
    const sin = Math.sin(camera.rotation);
    const rx = x * cos - y * sin;
    const ry = x * sin + y * cos;
    x = rx;
    y = ry;
  }

  // 5. Translate to center
  x += centerX;
  y += centerY;

  return { x, y };
}

// =============================================================================
// Debug Helpers
// =============================================================================

/**
 * Render camera debug overlay
 */
export function renderCameraDebug(
  ctx: CanvasRenderingContext2D,
  camera: CameraState,
  _arenaWidth: number,
  arenaHeight: number
): void {
  ctx.save();

  // Draw camera info
  ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
  ctx.fillRect(10, arenaHeight - 80, 200, 70);

  ctx.fillStyle = '#FFFFFF';
  ctx.font = '12px monospace';
  ctx.fillText(`Camera Mode: ${camera.mode}`, 15, arenaHeight - 60);
  ctx.fillText(`Zoom: ${camera.zoom.toFixed(2)}`, 15, arenaHeight - 45);
  ctx.fillText(`Pos: (${camera.position.x.toFixed(0)}, ${camera.position.y.toFixed(0)})`, 15, arenaHeight - 30);
  ctx.fillText(`Rotation: ${(camera.rotation * 180 / Math.PI).toFixed(1)}°`, 15, arenaHeight - 15);

  ctx.restore();
}

// =============================================================================
// Spectacle Presets
// =============================================================================

/**
 * Get dramatic camera settings for specific moments
 */
export function getSpectacleCameraSettings(
  momentType: 'ball_forming' | 'ball_silence' | 'ball_constrict' | 'ball_cooking' | 'death_spiral' | 'massacre'
): { zoom: number; transitionSpeed: number; rotation: number } {
  switch (momentType) {
    case 'ball_forming':
      return { zoom: 0.75, transitionSpeed: 0.015, rotation: 0 };

    case 'ball_silence':
      return { zoom: 0.7, transitionSpeed: 0.01, rotation: 0 };

    case 'ball_constrict':
      return { zoom: 0.85, transitionSpeed: 0.03, rotation: 0 };

    case 'ball_cooking':
      return { zoom: 1.1, transitionSpeed: 0.04, rotation: 0 };

    case 'death_spiral':
      return { zoom: 1.15, transitionSpeed: 0.06, rotation: Math.PI * 0.15 };

    case 'massacre':
      // Brief zoom-out to show carnage
      return { zoom: 0.9, transitionSpeed: 0.08, rotation: 0 };

    default:
      return { zoom: 1.0, transitionSpeed: 0.05, rotation: 0 };
  }
}
