/**
 * Scout Coordination System - Main Logic
 *
 * Handles both solo flanking and coordinated encircling behaviors.
 *
 * Solo Flanking: Scout orbits player, attacks from behind, retreats quickly.
 * Coordinated Attack: 3+ scouts surround player, attack in staggered waves.
 *
 * @see PROTO_SPEC.md S6: Bee Taxonomy
 */

import type { Vector2, Enemy } from '../../types';
import type {
  ScoutCoordinationState,
  ScoutCoordinationManager,
  SoloFlankState,
  SoloFlankPhase as _SoloFlankPhase,
  CoordinatedGroup,
  EncirclePhase as _EncirclePhase,
  ScoutEvent,
  SoloFlankTelegraph,
  CoordinatedTelegraph,
} from './types';
import {
  SCOUT_COORDINATION_CONFIG,
  SOLO_STING_CONFIG,
  COORDINATED_ARC_CONFIG,
  getScaledSoloConfig,
  getScaledCoordinatedConfig,
} from './config';

// =============================================================================
// Factory Functions
// =============================================================================

export function createScoutCoordinationManager(): ScoutCoordinationManager {
  return {
    groups: new Map(),
    scoutStates: new Map(),
    soloStates: new Map(),
    scoutCooldowns: new Map(),
    groupCooldowns: new Map(),
    globalCoordinationCooldown: 0,
    nextGroupId: 1,
  };
}

export function createScoutCoordinationState(): ScoutCoordinationState {
  return {
    mode: 'solo',
    nearbyScouts: [],
    coordinationGroupId: null,
    lastModeCheck: 0,
    modeStable: false,
  };
}

export function createSoloFlankState(gameTime: number): SoloFlankState {
  return {
    phase: 'orbiting',
    phaseStartTime: gameTime,
    orbitAngle: Math.random() * Math.PI * 2,
    orbitDirection: Math.random() > 0.5 ? 1 : -1,
    targetAngle: SOLO_STING_CONFIG.preferredFlankAngle,
    attackDirection: null,
    nextAttackTime: gameTime + SOLO_STING_CONFIG.attackIntervalMin +
      Math.random() * (SOLO_STING_CONFIG.attackIntervalMax - SOLO_STING_CONFIG.attackIntervalMin),
    consecutiveAttacks: 0,
    positionHistory: [],
  };
}

// =============================================================================
// Utility Functions
// =============================================================================

function normalize(v: Vector2): Vector2 {
  const mag = Math.sqrt(v.x * v.x + v.y * v.y);
  if (mag < 0.0001) return { x: 0, y: 0 };
  return { x: v.x / mag, y: v.y / mag };
}

function distance(a: Vector2, b: Vector2): number {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  return Math.sqrt(dx * dx + dy * dy);
}

function subtract(a: Vector2, b: Vector2): Vector2 {
  return { x: a.x - b.x, y: a.y - b.y };
}

function getPlayerFacing(velocity: Vector2): Vector2 {
  const mag = Math.sqrt(velocity.x * velocity.x + velocity.y * velocity.y);
  if (mag < 5) {
    // Player stationary - use default facing
    return { x: 0, y: -1 };
  }
  return { x: velocity.x / mag, y: velocity.y / mag };
}

function angleBetween(v1: Vector2, v2: Vector2): number {
  return Math.acos(Math.max(-1, Math.min(1, v1.x * v2.x + v1.y * v2.y)));
}

function _normalizeAngle(angle: number): number {
  while (angle > Math.PI) angle -= Math.PI * 2;
  while (angle < -Math.PI) angle += Math.PI * 2;
  return angle;
}
void _normalizeAngle;  // Reserved for future use

// =============================================================================
// Mode Detection
// =============================================================================

export function evaluateScoutMode(
  scoutId: string,
  scoutPos: Vector2,
  allEnemies: Enemy[],
  manager: ScoutCoordinationManager,
  gameTime: number
): ScoutCoordinationState {
  const existing = manager.scoutStates.get(scoutId) ?? createScoutCoordinationState();

  // Only re-evaluate periodically
  if (gameTime - existing.lastModeCheck < SCOUT_COORDINATION_CONFIG.modeCheckInterval) {
    return existing;
  }

  // Find nearby scouts
  const nearbyScouts = allEnemies
    .filter(e =>
      e.type === 'scout' &&
      e.id !== scoutId &&
      e.behaviorState !== 'recovery' &&
      !isScoutOnCooldown(e.id, manager, gameTime)
    )
    .filter(e => distance(e.position, scoutPos) <= SCOUT_COORDINATION_CONFIG.coordinationRange)
    .map(e => e.id)
    .slice(0, SCOUT_COORDINATION_CONFIG.maxCoordinatedScouts - 1);

  const shouldCoordinate =
    nearbyScouts.length >= SCOUT_COORDINATION_CONFIG.minScoutsForCoordination - 1 &&
    gameTime >= manager.globalCoordinationCooldown;

  const newMode = shouldCoordinate ? 'coordinated' : 'solo';
  const modeChanged = newMode !== existing.mode;
  const isStable = !modeChanged &&
    (gameTime - existing.lastModeCheck > SCOUT_COORDINATION_CONFIG.modeStabilityTime);

  return {
    mode: newMode,
    nearbyScouts,
    coordinationGroupId: existing.coordinationGroupId,
    lastModeCheck: gameTime,
    modeStable: modeChanged ? false : isStable,
  };
}

function isScoutOnCooldown(
  scoutId: string,
  manager: ScoutCoordinationManager,
  gameTime: number
): boolean {
  const cooldown = manager.scoutCooldowns.get(scoutId);
  return cooldown !== undefined && gameTime < cooldown;
}

// =============================================================================
// Solo Flanking Behavior
// =============================================================================

export function updateSoloFlank(
  scout: Enemy,
  state: SoloFlankState,
  playerPos: Vector2,
  playerVelocity: Vector2,
  gameTime: number,
  deltaTime: number,
  wave: number
): { scout: Enemy; state: SoloFlankState; damage: number; events: ScoutEvent[] } {
  const dt = deltaTime / 1000;
  const events: ScoutEvent[] = [];
  let damage = 0;

  const config = getScaledSoloConfig(wave);
  const newState = { ...state };

  // Update position history for trail
  if (newState.positionHistory.length >= SOLO_STING_CONFIG.trailLength) {
    newState.positionHistory.shift();
  }
  newState.positionHistory.push({ ...scout.position });

  switch (state.phase) {
    case 'orbiting': {
      // Circle player at preferred range
      const idealRange = (SOLO_STING_CONFIG.orbitDistanceMin + SOLO_STING_CONFIG.orbitDistanceMax) / 2;
      const _currentDist = distance(scout.position, playerPos);
      void _currentDist;  // Used for debugging

      // Update orbit angle
      newState.orbitAngle += newState.orbitDirection * SOLO_STING_CONFIG.orbitSpeed * dt;

      // Calculate target position on orbit
      const targetX = playerPos.x + Math.cos(newState.orbitAngle) * idealRange;
      const targetY = playerPos.y + Math.sin(newState.orbitAngle) * idealRange;

      // Move toward orbit position
      const toTarget = normalize(subtract({ x: targetX, y: targetY }, scout.position));
      const moveSpeed = scout.speed * 1.1;

      scout.position.x += toTarget.x * moveSpeed * dt;
      scout.position.y += toTarget.y * moveSpeed * dt;

      // Check if at good flank angle
      const playerFacing = getPlayerFacing(playerVelocity);
      const toScout = normalize(subtract(scout.position, playerPos));
      const currentAngle = angleBetween(playerFacing, toScout);

      const atFlankAngle = currentAngle >= SOLO_STING_CONFIG.preferredFlankAngle -
        SOLO_STING_CONFIG.angleCommitThreshold;

      // Check if should attack
      const orbitTime = gameTime - state.phaseStartTime;
      const canCommit = orbitTime >= SOLO_STING_CONFIG.minFlankingDuration;
      const mustCommit = orbitTime >= SOLO_STING_CONFIG.maxFlankingDuration;

      if ((canCommit && atFlankAngle && gameTime >= state.nextAttackTime) || mustCommit) {
        newState.phase = 'approach';
        newState.phaseStartTime = gameTime;
      }

      // Random direction change for unpredictability
      if (Math.random() < 0.008) {
        newState.orbitDirection *= -1;
      }
      break;
    }

    case 'approach': {
      // Move toward attack range
      const toPlayer = normalize(subtract(playerPos, scout.position));
      const moveSpeed = scout.speed * 1.4; // Faster approach

      scout.position.x += toPlayer.x * moveSpeed * dt;
      scout.position.y += toPlayer.y * moveSpeed * dt;

      const dist = distance(scout.position, playerPos);
      if (dist <= SOLO_STING_CONFIG.attackDistance) {
        newState.phase = 'telegraph';
        newState.phaseStartTime = gameTime + (Math.random() - 0.5) * config.telegraphDuration * 0.3;
        // Lock attack direction
        newState.attackDirection = normalize(subtract(playerPos, scout.position));
      }
      break;
    }

    case 'telegraph': {
      // Brief warning - scout vibrates in place
      const elapsed = gameTime - state.phaseStartTime;

      // Small position jitter for visual effect
      scout.position.x += (Math.random() - 0.5) * 3;
      scout.position.y += (Math.random() - 0.5) * 3;

      if (elapsed >= config.telegraphDuration) {
        newState.phase = 'strike';
        newState.phaseStartTime = gameTime;
      }
      break;
    }

    case 'strike': {
      // Lightning fast dash
      const elapsed = gameTime - state.phaseStartTime;
      const progress = Math.min(1, elapsed / SOLO_STING_CONFIG.attackDuration);

      if (progress < 1 && state.attackDirection) {
        // Ease-out movement (fast start, slowing end)
        const easedSpeed = (1 - Math.pow(progress, 2)) * 20;
        scout.position.x += state.attackDirection.x * SOLO_STING_CONFIG.attackDistance * easedSpeed * dt;
        scout.position.y += state.attackDirection.y * SOLO_STING_CONFIG.attackDistance * easedSpeed * dt;

        // Check hit
        if (distance(scout.position, playerPos) < SOLO_STING_CONFIG.hitRadius + 15) {
          damage = config.damage;
          events.push({
            type: 'solo_attack',
            scoutId: scout.id,
            damage: config.damage,
            position: { ...scout.position },
          });
        }
      }

      if (progress >= 1) {
        newState.phase = 'retreat';
        newState.phaseStartTime = gameTime;
        newState.consecutiveAttacks++;
      }
      break;
    }

    case 'retreat': {
      // Back off quickly
      const elapsed = gameTime - state.phaseStartTime;
      const progress = Math.min(1, elapsed / SOLO_STING_CONFIG.retreatDuration);

      if (progress < 1) {
        const awayDir = normalize(subtract(scout.position, playerPos));
        scout.position.x += awayDir.x * SOLO_STING_CONFIG.retreatSpeed * dt;
        scout.position.y += awayDir.y * SOLO_STING_CONFIG.retreatSpeed * dt;
      } else {
        newState.phase = 'recovery';
        newState.phaseStartTime = gameTime;
        events.push({ type: 'solo_retreat', scoutId: scout.id });
      }
      break;
    }

    case 'recovery': {
      // Vulnerable, slow movement away
      const elapsed = gameTime - state.phaseStartTime;

      if (elapsed < SOLO_STING_CONFIG.recoveryDuration) {
        // Drift away slowly
        const awayDir = normalize(subtract(scout.position, playerPos));
        scout.position.x += awayDir.x * 20 * dt;
        scout.position.y += awayDir.y * 20 * dt;
      } else {
        newState.phase = 'orbiting';
        newState.phaseStartTime = gameTime;
        newState.attackDirection = null;
        // Set next attack time
        newState.nextAttackTime = gameTime +
          config.attackIntervalMin +
          Math.random() * (config.attackIntervalMax - config.attackIntervalMin);
      }
      break;
    }
  }

  return { scout, state: newState, damage, events };
}

// =============================================================================
// Coordinated Encircle Behavior
// =============================================================================

export function createCoordinatedGroup(
  scoutIds: string[],
  playerPos: Vector2,
  gameTime: number,
  manager: ScoutCoordinationManager
): CoordinatedGroup {
  const groupId = `group-${manager.nextGroupId++}`;

  // Assign angles evenly distributed
  const scoutAngles = new Map<string, number>();
  const count = scoutIds.length;
  const baseAngle = Math.random() * Math.PI * 2; // Random starting angle

  scoutIds.forEach((id, i) => {
    const angle = baseAngle + (i / count) * Math.PI * 2 +
      (Math.random() - 0.5) * COORDINATED_ARC_CONFIG.angleJitter;
    scoutAngles.set(id, angle);
  });

  // Determine attack order (alternating for crossing pattern)
  const sorted = [...scoutIds].sort((a, b) =>
    (scoutAngles.get(a) ?? 0) - (scoutAngles.get(b) ?? 0)
  );
  const attackOrder: string[] = [];
  const mid = Math.floor(sorted.length / 2);
  for (let i = 0; i < mid; i++) {
    attackOrder.push(sorted[i]);
    if (sorted[mid + i]) attackOrder.push(sorted[mid + i]);
  }
  if (sorted.length % 2 === 1) attackOrder.push(sorted[sorted.length - 1]);

  return {
    groupId,
    leaderScoutId: scoutIds[0],
    memberIds: scoutIds,
    phase: 'recruiting',
    phaseStartTime: gameTime,
    targetCenter: { ...playerPos },
    formationRadius: COORDINATED_ARC_CONFIG.formationRadius,
    scoutAngles,
    scoutAttackOrder: attackOrder,
    currentAttackIndex: 0,
    lastAttackTime: 0,
  };
}

export function updateCoordinatedGroup(
  group: CoordinatedGroup,
  scouts: Map<string, Enemy>,
  playerPos: Vector2,
  gameTime: number,
  deltaTime: number,
  wave: number
): { group: CoordinatedGroup | null; events: ScoutEvent[]; damage: number } {
  const dt = deltaTime / 1000;
  const events: ScoutEvent[] = [];
  let damage = 0;

  const config = getScaledCoordinatedConfig(wave);
  const elapsed = gameTime - group.phaseStartTime;

  // Filter dead scouts
  const aliveMembers = group.memberIds.filter(id => scouts.has(id));

  // Check if group is still viable
  if (aliveMembers.length < SCOUT_COORDINATION_CONFIG.minScoutsForCoordination) {
    events.push({
      type: 'group_disrupted',
      groupId: group.groupId,
      reason: 'insufficient_scouts',
    });
    return { group: null, events, damage };
  }

  const newGroup = { ...group, memberIds: aliveMembers };

  switch (group.phase) {
    case 'recruiting': {
      // Brief recruitment phase
      if (elapsed >= 300) {
        newGroup.phase = 'positioning';
        newGroup.phaseStartTime = gameTime;
        events.push({
          type: 'group_forming',
          groupId: group.groupId,
          memberCount: aliveMembers.length,
        });
      }
      break;
    }

    case 'positioning': {
      // Move scouts to formation positions
      let allInPosition = true;

      for (const scoutId of aliveMembers) {
        const scout = scouts.get(scoutId);
        if (!scout) continue;

        const angle = group.scoutAngles.get(scoutId) ?? 0;
        const targetX = playerPos.x + Math.cos(angle) * group.formationRadius;
        const targetY = playerPos.y + Math.sin(angle) * group.formationRadius;

        const dx = targetX - scout.position.x;
        const dy = targetY - scout.position.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist > COORDINATED_ARC_CONFIG.positioningTolerance) {
          allInPosition = false;
          // Move toward target
          const speed = COORDINATED_ARC_CONFIG.gatheringSpeed;
          scout.position.x += (dx / dist) * speed * dt;
          scout.position.y += (dy / dist) * speed * dt;
        }
      }

      // Update target center (track player)
      newGroup.targetCenter = { ...playerPos };

      if (allInPosition) {
        newGroup.phase = 'synchronized';
        newGroup.phaseStartTime = gameTime;
        events.push({ type: 'group_positioned', groupId: group.groupId });
      } else if (elapsed >= COORDINATED_ARC_CONFIG.positioningTimeout) {
        events.push({ type: 'group_disrupted', groupId: group.groupId, reason: 'positioning_timeout' });
        return { group: null, events, damage };
      }
      break;
    }

    case 'synchronized': {
      // Hold position, track player
      for (const scoutId of aliveMembers) {
        const scout = scouts.get(scoutId);
        if (!scout) continue;

        const angle = group.scoutAngles.get(scoutId) ?? 0;
        const targetX = playerPos.x + Math.cos(angle) * group.formationRadius;
        const targetY = playerPos.y + Math.sin(angle) * group.formationRadius;

        // Slowly track to maintain formation
        scout.position.x += (targetX - scout.position.x) * 0.1;
        scout.position.y += (targetY - scout.position.y) * 0.1;
      }

      newGroup.targetCenter = { ...playerPos };

      if (elapsed >= COORDINATED_ARC_CONFIG.synchronizedHoldTime) {
        newGroup.phase = 'telegraph';
        newGroup.phaseStartTime = gameTime;
        events.push({
          type: 'group_telegraph',
          groupId: group.groupId,
          targetCenter: { ...playerPos },
        });
      }
      break;
    }

    case 'telegraph': {
      // Visual warning - scouts face player
      for (const scoutId of aliveMembers) {
        const scout = scouts.get(scoutId);
        if (!scout) continue;

        const angle = Math.atan2(
          group.targetCenter.y - scout.position.y,
          group.targetCenter.x - scout.position.x
        );
        scout.attackDirection = { x: Math.cos(angle), y: Math.sin(angle) };
      }

      if (elapsed >= config.telegraphDuration) {
        newGroup.phase = 'attacking';
        newGroup.phaseStartTime = gameTime;
        newGroup.currentAttackIndex = 0;
      }
      break;
    }

    case 'attacking': {
      // Staggered attacks
      const expectedAttackTime = newGroup.currentAttackIndex * config.attackWaveDelay;

      if (elapsed >= expectedAttackTime && newGroup.currentAttackIndex < newGroup.scoutAttackOrder.length) {
        const attackingScoutId = newGroup.scoutAttackOrder[newGroup.currentAttackIndex];
        const scout = scouts.get(attackingScoutId);

        if (scout) {
          const angle = group.scoutAngles.get(attackingScoutId) ?? 0;
          const _startX = group.targetCenter.x + Math.cos(angle) * group.formationRadius;
          const _startY = group.targetCenter.y + Math.sin(angle) * group.formationRadius;
          void _startX; void _startY;  // Reserved for telegraph rendering

          // Target is through the center
          const throughX = group.targetCenter.x - Math.cos(angle) * group.formationRadius * COORDINATED_ARC_CONFIG.attackOvershoot;
          const throughY = group.targetCenter.y - Math.sin(angle) * group.formationRadius * COORDINATED_ARC_CONFIG.attackOvershoot;

          scout.targetPosition = { x: throughX, y: throughY };
          scout.behaviorState = 'attack';
          scout.stateStartTime = gameTime;

          events.push({
            type: 'arc_attack_wave',
            groupId: group.groupId,
            scoutId: attackingScoutId,
            attackIndex: newGroup.currentAttackIndex,
          });
        }

        newGroup.currentAttackIndex++;
      }

      // Update attacking scouts and check hits
      for (let i = 0; i < newGroup.currentAttackIndex; i++) {
        const scoutId = newGroup.scoutAttackOrder[i];
        const scout = scouts.get(scoutId);
        if (!scout || scout.behaviorState !== 'attack') continue;

        const attackElapsed = gameTime - (group.phaseStartTime + i * config.attackWaveDelay);

        if (attackElapsed < COORDINATED_ARC_CONFIG.attackDuration) {
          const progress = attackElapsed / COORDINATED_ARC_CONFIG.attackDuration;
          const easedProgress = 1 - Math.pow(1 - progress, 2);

          const angle = group.scoutAngles.get(scoutId) ?? 0;
          const startX = group.targetCenter.x + Math.cos(angle) * group.formationRadius;
          const startY = group.targetCenter.y + Math.sin(angle) * group.formationRadius;

          scout.position.x = startX + (scout.targetPosition!.x - startX) * easedProgress;
          scout.position.y = startY + (scout.targetPosition!.y - startY) * easedProgress;

          // Check hit (only once per scout)
          const hitDist = distance(scout.position, playerPos);
          if (hitDist < COORDINATED_ARC_CONFIG.hitRadius + 15) {
            damage += config.damagePerScout;

            if (COORDINATED_ARC_CONFIG.appliesMarkingDebuff) {
              events.push({
                type: 'player_marked',
                duration: COORDINATED_ARC_CONFIG.markingDuration,
                damageBonus: COORDINATED_ARC_CONFIG.markingDamageBonus,
              });
            }
          }
        } else if (attackElapsed >= COORDINATED_ARC_CONFIG.attackDuration) {
          scout.behaviorState = 'recovery';
          scout.stateStartTime = gameTime;
        }
      }

      // Check if all attacks complete
      const totalAttackTime = (newGroup.scoutAttackOrder.length) * config.attackWaveDelay +
        COORDINATED_ARC_CONFIG.attackDuration;

      if (elapsed >= totalAttackTime) {
        newGroup.phase = 'dispersing';
        newGroup.phaseStartTime = gameTime;
      }
      break;
    }

    case 'dispersing': {
      // Scatter away
      for (const scoutId of aliveMembers) {
        const scout = scouts.get(scoutId);
        if (!scout) continue;

        const awayDir = normalize(subtract(scout.position, playerPos));
        scout.position.x += awayDir.x * COORDINATED_ARC_CONFIG.scatterSpeed * dt;
        scout.position.y += awayDir.y * COORDINATED_ARC_CONFIG.scatterSpeed * dt;
      }

      if (elapsed >= COORDINATED_ARC_CONFIG.recoveryDuration) {
        events.push({ type: 'group_complete', groupId: group.groupId });
        return { group: null, events, damage };
      }
      break;
    }
  }

  return { group: newGroup, events, damage };
}

// =============================================================================
// Telegraph Generators (for rendering)
// =============================================================================

export function getSoloFlankTelegraph(
  scout: Enemy,
  state: SoloFlankState,
  gameTime: number
): SoloFlankTelegraph | null {
  if (state.phase === 'orbiting' || state.phase === 'approach') {
    return {
      scoutId: scout.id,
      type: state.phase === 'approach' ? 'approaching' : 'orbiting',
      position: scout.position,
      orbitTrail: state.positionHistory,
      attackDirection: null,
      intensityPulse: Math.sin(gameTime / 200) * 0.3 + 0.5,
    };
  }

  if (state.phase === 'telegraph' || state.phase === 'strike') {
    return {
      scoutId: scout.id,
      type: 'striking',
      position: scout.position,
      orbitTrail: state.positionHistory,
      attackDirection: state.attackDirection,
      intensityPulse: Math.sin(gameTime / 80) * 0.5 + 0.5,
    };
  }

  return null;
}

export function getCoordinatedTelegraph(
  group: CoordinatedGroup,
  scouts: Map<string, Enemy>,
  gameTime: number
): CoordinatedTelegraph | null {
  if (group.phase === 'recruiting') return null;

  const scoutPositions: Vector2[] = [];
  const targetPositions: Vector2[] = [];
  const attackArrows: Array<{ from: Vector2; to: Vector2 }> = [];

  for (const scoutId of group.memberIds) {
    const scout = scouts.get(scoutId);
    if (scout) {
      scoutPositions.push({ ...scout.position });

      const angle = group.scoutAngles.get(scoutId) ?? 0;
      targetPositions.push({
        x: group.targetCenter.x + Math.cos(angle) * group.formationRadius,
        y: group.targetCenter.y + Math.sin(angle) * group.formationRadius,
      });

      if (group.phase === 'telegraph' || group.phase === 'attacking') {
        attackArrows.push({
          from: scout.position,
          to: group.targetCenter,
        });
      }
    }
  }

  const elapsed = gameTime - group.phaseStartTime;
  let warningIntensity = 0;

  if (group.phase === 'synchronized') {
    warningIntensity = elapsed / COORDINATED_ARC_CONFIG.synchronizedHoldTime * 0.5;
  } else if (group.phase === 'telegraph') {
    const pulsePhase = (elapsed % COORDINATED_ARC_CONFIG.telegraphPulseRate) /
      COORDINATED_ARC_CONFIG.telegraphPulseRate;
    warningIntensity = Math.sin(pulsePhase * Math.PI * 2) * 0.3 + 0.7;
  } else if (group.phase === 'attacking') {
    warningIntensity = 1;
  }

  return {
    groupId: group.groupId,
    phase: group.phase,
    center: group.targetCenter,
    radius: group.formationRadius,
    scoutPositions,
    targetPositions,
    attackArrows,
    warningIntensity,
  };
}

// =============================================================================
// Main Update Function
// =============================================================================

export interface ScoutSystemUpdateResult {
  manager: ScoutCoordinationManager;
  modifiedScouts: Map<string, Enemy>;
  totalDamage: number;
  events: ScoutEvent[];
  telegraphs: {
    solo: SoloFlankTelegraph[];
    coordinated: CoordinatedTelegraph[];
  };
}

export function updateScoutCoordinationSystem(
  manager: ScoutCoordinationManager,
  enemies: Enemy[],
  playerPos: Vector2,
  playerVelocity: Vector2,
  gameTime: number,
  deltaTime: number,
  wave: number
): ScoutSystemUpdateResult {
  const events: ScoutEvent[] = [];
  const modifiedScouts = new Map<string, Enemy>();
  let totalDamage = 0;

  const soloTelegraphs: SoloFlankTelegraph[] = [];
  const coordinatedTelegraphs: CoordinatedTelegraph[] = [];

  // Get all scouts
  const scouts = enemies.filter(e => e.type === 'scout');
  const scoutMap = new Map(scouts.map(s => [s.id, { ...s }]));

  // Update coordination states
  for (const scout of scouts) {
    const coordState = evaluateScoutMode(scout.id, scout.position, enemies, manager, gameTime);
    manager.scoutStates.set(scout.id, coordState);
  }

  // Try to form new coordinated groups
  const scoutsInGroups = new Set<string>();
  for (const group of manager.groups.values()) {
    group.memberIds.forEach(id => scoutsInGroups.add(id));
  }

  // Find scouts that want to coordinate but aren't in groups
  const coordinatingScouts = scouts.filter(s => {
    const state = manager.scoutStates.get(s.id);
    return state?.mode === 'coordinated' &&
      state.modeStable &&
      !scoutsInGroups.has(s.id) &&
      !isScoutOnCooldown(s.id, manager, gameTime);
  });

  // Form new group if enough scouts
  if (coordinatingScouts.length >= SCOUT_COORDINATION_CONFIG.minScoutsForCoordination &&
      gameTime >= manager.globalCoordinationCooldown) {
    const groupScouts = coordinatingScouts.slice(0, SCOUT_COORDINATION_CONFIG.maxCoordinatedScouts);
    const newGroup = createCoordinatedGroup(
      groupScouts.map(s => s.id),
      playerPos,
      gameTime,
      manager
    );
    manager.groups.set(newGroup.groupId, newGroup);

    // Update coordination states
    for (const scoutId of groupScouts.map(s => s.id)) {
      const state = manager.scoutStates.get(scoutId);
      if (state) {
        state.coordinationGroupId = newGroup.groupId;
      }
      scoutsInGroups.add(scoutId);
    }
  }

  // Update coordinated groups
  for (const [groupId, group] of manager.groups) {
    const result = updateCoordinatedGroup(group, scoutMap, playerPos, gameTime, deltaTime, wave);
    totalDamage += result.damage;
    events.push(...result.events);

    if (result.group) {
      manager.groups.set(groupId, result.group);

      const telegraph = getCoordinatedTelegraph(result.group, scoutMap, gameTime);
      if (telegraph) coordinatedTelegraphs.push(telegraph);
    } else {
      // Group dissolved
      manager.groups.delete(groupId);

      // Apply cooldowns
      for (const scoutId of group.memberIds) {
        manager.scoutCooldowns.set(scoutId, gameTime + SCOUT_COORDINATION_CONFIG.coordinationCooldown);
        const state = manager.scoutStates.get(scoutId);
        if (state) state.coordinationGroupId = null;
      }

      manager.globalCoordinationCooldown = gameTime + SCOUT_COORDINATION_CONFIG.globalCoordinationCooldown;
    }
  }

  // Update solo scouts
  for (const scout of scouts) {
    if (scoutsInGroups.has(scout.id)) continue;

    let soloState = manager.soloStates.get(scout.id);
    if (!soloState) {
      soloState = createSoloFlankState(gameTime);
      manager.soloStates.set(scout.id, soloState);
    }

    const scoutCopy = scoutMap.get(scout.id) ?? { ...scout };
    const result = updateSoloFlank(
      scoutCopy,
      soloState,
      playerPos,
      playerVelocity,
      gameTime,
      deltaTime,
      wave
    );

    manager.soloStates.set(scout.id, result.state);
    modifiedScouts.set(scout.id, result.scout);
    totalDamage += result.damage;
    events.push(...result.events);

    const telegraph = getSoloFlankTelegraph(result.scout, result.state, gameTime);
    if (telegraph) soloTelegraphs.push(telegraph);
  }

  // Add coordinated scouts to modified map
  for (const [id, scout] of scoutMap) {
    if (!modifiedScouts.has(id)) {
      modifiedScouts.set(id, scout);
    }
  }

  return {
    manager,
    modifiedScouts,
    totalDamage,
    events,
    telegraphs: {
      solo: soloTelegraphs,
      coordinated: coordinatedTelegraphs,
    },
  };
}
