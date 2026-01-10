/**
 * Scout Coordination System - Type Definitions
 *
 * Scouts have two behavior modes:
 * 1. Solo Mode: Single scout flanks and performs quick hit-and-run stings
 * 2. Coordinated Mode: 3+ scouts encircle and perform synchronized arc attacks
 *
 * @see PROTO_SPEC.md S6: Bee Taxonomy
 */

import type { Vector2 } from '../../types';

// =============================================================================
// Scout Behavior Mode
// =============================================================================

export type ScoutMode = 'solo' | 'coordinated';

export interface ScoutCoordinationState {
  mode: ScoutMode;
  nearbyScouts: string[];           // IDs of scouts within coordination range
  coordinationGroupId: string | null;
  lastModeCheck: number;
  modeStable: boolean;              // Has mode been stable long enough to act?
}

// =============================================================================
// Solo Flanking State
// =============================================================================

export type SoloFlankPhase =
  | 'orbiting'      // Circling player at range
  | 'approach'      // Moving into attack range
  | 'telegraph'     // Brief twitch warning
  | 'strike'        // Lightning fast dash
  | 'retreat'       // Backing off after attack
  | 'recovery';     // Brief vulnerable window

export interface SoloFlankState {
  phase: SoloFlankPhase;
  phaseStartTime: number;

  // Orbit tracking
  orbitAngle: number;               // Current angle around player
  orbitDirection: 1 | -1;           // Clockwise or counter-clockwise
  targetAngle: number;              // Ideal flank angle (behind player)

  // Attack state
  attackDirection: Vector2 | null;
  nextAttackTime: number;
  consecutiveAttacks: number;

  // Position history for trail rendering
  positionHistory: Vector2[];
}

// =============================================================================
// Coordinated Encircle State
// =============================================================================

export type EncirclePhase =
  | 'recruiting'      // Finding nearby scouts to join
  | 'positioning'     // Moving to surround positions
  | 'synchronized'    // All in position, building tension
  | 'telegraph'       // Visual warning before attack
  | 'attacking'       // Staggered arc attacks
  | 'dispersing';     // Recovery and scatter

export interface CoordinatedGroup {
  groupId: string;
  leaderScoutId: string;
  memberIds: string[];
  phase: EncirclePhase;
  phaseStartTime: number;

  // Geometry
  targetCenter: Vector2;            // Player position snapshot
  formationRadius: number;

  // Per-scout assignments
  scoutAngles: Map<string, number>; // Assigned attack angle per scout
  scoutAttackOrder: string[];       // Order scouts attack in
  currentAttackIndex: number;

  // Timing
  lastAttackTime: number;
}

// =============================================================================
// Manager State (tracks all active groups)
// =============================================================================

export interface ScoutCoordinationManager {
  // Active coordinated groups
  groups: Map<string, CoordinatedGroup>;

  // Per-scout state
  scoutStates: Map<string, ScoutCoordinationState>;
  soloStates: Map<string, SoloFlankState>;

  // Cooldowns
  scoutCooldowns: Map<string, number>;      // scoutId -> canAttackAfter
  groupCooldowns: Map<string, number>;      // groupId -> canReformAfter
  globalCoordinationCooldown: number;       // When any group can form

  // Next group ID
  nextGroupId: number;
}

// =============================================================================
// Events
// =============================================================================

export type ScoutEvent =
  | { type: 'solo_attack'; scoutId: string; damage: number; position: Vector2 }
  | { type: 'solo_retreat'; scoutId: string }
  | { type: 'group_forming'; groupId: string; memberCount: number }
  | { type: 'group_positioned'; groupId: string }
  | { type: 'group_telegraph'; groupId: string; targetCenter: Vector2 }
  | { type: 'arc_attack_wave'; groupId: string; scoutId: string; attackIndex: number }
  | { type: 'group_complete'; groupId: string }
  | { type: 'group_disrupted'; groupId: string; reason: string }
  | { type: 'player_marked'; duration: number; damageBonus: number };

// =============================================================================
// Telegraph Data (for rendering)
// =============================================================================

export interface SoloFlankTelegraph {
  scoutId: string;
  type: 'orbiting' | 'approaching' | 'striking';
  position: Vector2;
  orbitTrail: Vector2[];
  attackDirection: Vector2 | null;
  intensityPulse: number;           // 0-1 for glow effect
}

export interface CoordinatedTelegraph {
  groupId: string;
  phase: EncirclePhase;
  center: Vector2;
  radius: number;
  scoutPositions: Vector2[];
  targetPositions: Vector2[];
  attackArrows: Array<{ from: Vector2; to: Vector2 }>;
  warningIntensity: number;         // 0-1 for pulse effect
}
