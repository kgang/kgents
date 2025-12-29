/**
 * THE BALL Formation System - Telegraph Data Extraction
 *
 * Extracts telegraph data from state for rendering.
 * Follows the pattern from enemies.ts getBeeTelegraph().
 */

import type { LegacyBallState, BallTelegraphData, LungePhase } from './types';
import { BALL_LUNGE_CONFIG } from './config';

/**
 * Extract telegraph data from ball state for rendering
 * Returns null if ball is inactive
 */
export function getBallTelegraph(
  state: LegacyBallState,
  gameTime: number
): BallTelegraphData | null {
  if (state.phase === 'inactive') {
    return null;
  }

  // Determine telegraph type based on phase, lunge state, and fade state
  let type: BallTelegraphData['type'];
  if (state.activeLunge) {
    if (state.activeLunge.phase === 'windup') {
      type = 'lunge_windup';
    } else if (state.activeLunge.phase === 'lunge') {
      type = 'lunge_attack';
    } else {
      type = state.phase as BallTelegraphData['type'];
    }
  } else if (state.isDissipating) {
    type = 'dissipating';
  } else if (state.isFading) {
    type = 'fading';
  } else {
    type = state.phase as BallTelegraphData['type'];
  }

  // Check if player is inside the ball during fading (reviving)
  // Note: We set this true during fading when fadeProgress is decreasing
  // The actual "is player inside" check happens in dissipation.ts
  const isReviving = state.isFading && state.fadeProgress > 0;

  const telegraph: BallTelegraphData = {
    type,
    center: state.center,
    radius: state.currentRadius,
    gapAngle: state.gapAngle,
    gapSize: state.gapSize,
    progress: state.phaseProgress,
    temperature: state.temperature,
    isDissipating: state.isDissipating,
    // Fade/linger state (RUN 039)
    isFading: state.isFading,
    fadeProgress: state.fadeProgress,
    isReviving: isReviving,
  };

  // Add lunge-specific data if lunging
  if (state.activeLunge) {
    telegraph.lungeBeeId = state.activeLunge.beeId;
    telegraph.lungePhase = state.activeLunge.phase;

    // Calculate lunge progress based on phase
    const lungeProgress = getLungeProgressFromState(state.activeLunge, gameTime);
    telegraph.lungeProgress = lungeProgress.progress;

    // Calculate current bee position
    const beePos = getLungingBeePositionFromState(state.activeLunge, gameTime);
    if (beePos) {
      telegraph.lungeBeePos = beePos;
    }

    telegraph.lungeTargetPos = state.activeLunge.targetPos;
  }

  return telegraph;
}

/**
 * Get lunge progress from legacy activeLunge state
 * RUN 040: Handles new pullback/charge phases
 */
function getLungeProgressFromState(
  activeLunge: NonNullable<LegacyBallState['activeLunge']>,
  gameTime: number
): { phase: LungePhase; progress: number } {
  let duration: number;
  let startTime: number;

  switch (activeLunge.phase) {
    case 'pullback':
      duration = BALL_LUNGE_CONFIG.pullbackDuration;
      startTime = activeLunge.windupStartTime;
      break;
    case 'charge':
      duration = BALL_LUNGE_CONFIG.chargeDuration;
      startTime = activeLunge.windupStartTime;
      break;
    case 'windup':
      // Legacy compatibility - treat as pullback
      duration = BALL_LUNGE_CONFIG.windupDuration;
      startTime = activeLunge.windupStartTime;
      break;
    case 'lunge':
      duration = activeLunge.duration;
      startTime = activeLunge.lungeStartTime;
      break;
    case 'return':
      duration = BALL_LUNGE_CONFIG.returnDuration;
      startTime = activeLunge.lungeStartTime;
      break;
    default:
      return { phase: 'idle', progress: 0 };
  }

  const elapsed = gameTime - startTime;
  return {
    phase: activeLunge.phase,
    progress: Math.min(1, elapsed / duration),
  };
}

/**
 * Calculate current position of lunging bee from legacy state
 * RUN 040: Handles new pullback/charge phases
 */
function getLungingBeePositionFromState(
  activeLunge: NonNullable<LegacyBallState['activeLunge']>,
  gameTime: number
): { x: number; y: number } | null {
  const { phase, progress } = getLungeProgressFromState(activeLunge, gameTime);

  // Calculate pullback position (used by multiple phases)
  const dx = activeLunge.targetPos.x - activeLunge.startPos.x;
  const dy = activeLunge.targetPos.y - activeLunge.startPos.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  if (dist === 0) return activeLunge.startPos;

  // Pullback position is 40px behind start position
  const pullbackDist = BALL_LUNGE_CONFIG.pullbackDistance;
  const pullbackPos = {
    x: activeLunge.startPos.x - (dx / dist) * pullbackDist,
    y: activeLunge.startPos.y - (dy / dist) * pullbackDist,
  };

  switch (phase) {
    case 'pullback': {
      // Move backward from startPos to pullbackPos
      return {
        x: activeLunge.startPos.x + (pullbackPos.x - activeLunge.startPos.x) * progress,
        y: activeLunge.startPos.y + (pullbackPos.y - activeLunge.startPos.y) * progress,
      };
    }

    case 'charge': {
      // Hold at pullback position with vibration
      const vibration = Math.sin(gameTime * 0.05) * 2 * progress;
      return {
        x: pullbackPos.x + (-dy / dist) * vibration,
        y: pullbackPos.y + (dx / dist) * vibration,
      };
    }

    case 'windup': {
      // Legacy: simple pullback (15px)
      const legacyPullbackDist = 15 * progress;
      return {
        x: activeLunge.startPos.x - (dx / dist) * legacyPullbackDist,
        y: activeLunge.startPos.y - (dy / dist) * legacyPullbackDist,
      };
    }

    case 'lunge': {
      // Ease-out dash from pullbackPos toward target
      const easedProgress = 1 - Math.pow(1 - progress, 3);
      return {
        x: pullbackPos.x + (activeLunge.targetPos.x - pullbackPos.x) * easedProgress,
        y: pullbackPos.y + (activeLunge.targetPos.y - pullbackPos.y) * easedProgress,
      };
    }

    case 'return': {
      // Ease-in return from targetPos to startPos (original formation position)
      const easedProgress = Math.pow(progress, 2);
      return {
        x: activeLunge.targetPos.x + (activeLunge.startPos.x - activeLunge.targetPos.x) * easedProgress,
        y: activeLunge.targetPos.y + (activeLunge.startPos.y - activeLunge.targetPos.y) * easedProgress,
      };
    }

    default:
      return null;
  }
}

/**
 * Get audio parameters for current ball state
 */
export function getBallAudioParams(state: LegacyBallState): {
  buzzVolume: number;
  buzzFreq: number;
  shouldPlayHeartbeat: boolean;
  shouldPlayBass: boolean;
} {
  switch (state.phase) {
    case 'inactive':
      return {
        buzzVolume: 0,
        buzzFreq: 0,
        shouldPlayHeartbeat: false,
        shouldPlayBass: false,
      };

    case 'forming':
      // Crescendo from 0.3 to 1.0
      return {
        buzzVolume: 0.3 + (1.0 - 0.3) * state.phaseProgress,
        buzzFreq: 150 + state.phaseProgress * 650, // 150Hz -> 800Hz
        shouldPlayHeartbeat: false,
        shouldPlayBass: false,
      };

    case 'silence':
      // SILENCE - the dread
      return {
        buzzVolume: 0,
        buzzFreq: 0,
        shouldPlayHeartbeat: true,
        shouldPlayBass: false,
      };

    case 'constrict':
      // Bass note rises
      return {
        buzzVolume: 0.2, // Subtle buzz
        buzzFreq: 200,
        shouldPlayHeartbeat: true,
        shouldPlayBass: true,
      };

    case 'cooking':
      // Maximum intensity
      return {
        buzzVolume: 1.0,
        buzzFreq: 1000, // High frequency panic
        shouldPlayHeartbeat: false,
        shouldPlayBass: true,
      };

    case 'dissipating':
      // Fading out
      return {
        buzzVolume: 0.2,
        buzzFreq: 100,
        shouldPlayHeartbeat: false,
        shouldPlayBass: false,
      };

    default:
      return {
        buzzVolume: 0,
        buzzFreq: 0,
        shouldPlayHeartbeat: false,
        shouldPlayBass: false,
      };
  }
}

/**
 * Get camera state for ball phase
 */
export function getBallCameraState(state: LegacyBallState): {
  targetZoom: number;
  focusPoint: { x: number; y: number };
  transitionSpeed: number;
} {
  switch (state.phase) {
    case 'inactive':
      return {
        targetZoom: 1.0,
        focusPoint: { x: 0, y: 0 },
        transitionSpeed: 0.1,
      };

    case 'forming':
      // Pull back to show full sphere
      const formingZoom = 1.0 - state.phaseProgress * 0.3;
      return {
        targetZoom: formingZoom,
        focusPoint: state.center,
        transitionSpeed: 0.02,
      };

    case 'silence':
      // Hold wide shot
      return {
        targetZoom: 0.7,
        focusPoint: state.center,
        transitionSpeed: 0.02,
      };

    case 'constrict':
      // Zoom back in slightly to show gap
      return {
        targetZoom: 0.85,
        focusPoint: {
          x: state.center.x + Math.cos(state.gapAngle) * state.currentRadius * 0.3,
          y: state.center.y + Math.sin(state.gapAngle) * state.currentRadius * 0.3,
        },
        transitionSpeed: 0.05,
      };

    case 'cooking':
      // Tight on player
      return {
        targetZoom: 1.1,
        focusPoint: state.center,
        transitionSpeed: 0.05,
      };

    case 'dissipating':
      // Pull back as ball breaks up
      return {
        targetZoom: 0.9,
        focusPoint: state.center,
        transitionSpeed: 0.03,
      };

    default:
      return {
        targetZoom: 1.0,
        focusPoint: { x: 0, y: 0 },
        transitionSpeed: 0.1,
      };
  }
}
