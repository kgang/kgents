/**
 * WASM Survivors - Core Game Loop Hook
 *
 * 16ms frame budget (60 FPS target):
 * - Input: < 1ms
 * - Physics: < 5ms
 * - Collision: < 3ms
 * - Render: < 7ms (handled by React/Canvas)
 *
 * @see pilots/wasm-survivors-game/.outline.md
 */

import { useRef, useEffect, useCallback } from 'react';
import type { GameState, InputState } from '@kgents/shared-primitives';
import { updatePhysics, checkCollisions } from '../systems/physics';
import { updateSpawner, type SpawnResult } from '../systems/spawn';
import { processJuice, type JuiceSystem, checkClutchMoment, getEffectiveTimeScale } from '../systems/juice';
import { emitWitnessMark, type WitnessContext } from '../systems/witness';
import { generateUpgradeChoices, type UpgradeType, type ActiveUpgrades } from '../systems/upgrades';
import { updateMetamorphosis, type MetamorphosisResult } from '../systems/metamorphosis';
import { updateColossalBehavior } from '../systems/colossal';

// =============================================================================
// Constants
// =============================================================================

const TARGET_FRAME_TIME = 16; // ~60 FPS
const MAX_FRAME_TIME = 100; // Cap delta to prevent spiral of death

// =============================================================================
// Types
// =============================================================================

export interface GameLoopCallbacks {
  onStateUpdate: (state: GameState) => void;
  onGameOver: (finalState: GameState) => void;
  onLevelUp: (state: GameState, choices: string[]) => void;
  onWaveComplete: (wave: number) => void;
  // Sound callbacks (DD-5)
  onEnemyKilled?: (enemyType: 'basic' | 'fast' | 'tank' | 'boss' | 'spitter' | 'colossal_tide') => void;
  onPlayerDamaged?: (damage: number) => void;
  // DD-21: Telegraph callbacks for rendering
  onTelegraphsUpdate?: (telegraphs: import('../systems/enemies').TelegraphData[]) => void;
}

export interface GameLoopControls {
  start: () => void;
  stop: () => void;
  pause: () => void;
  resume: () => void;
  reset: () => void;
  setState: (state: GameState) => void;
  isRunning: boolean;
}

// =============================================================================
// Hook
// =============================================================================

export function useGameLoop(
  initialState: GameState,
  inputRef: React.RefObject<InputState>,
  callbacks: GameLoopCallbacks,
  juiceSystem: JuiceSystem
): GameLoopControls {
  const stateRef = useRef<GameState>(initialState);
  const animationFrameRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(0);
  const isRunningRef = useRef<boolean>(false);
  const isPausedRef = useRef<boolean>(false);
  const witnessContextRef = useRef<WitnessContext>({
    runId: `run-${Date.now()}`,
    marks: [],
    ghosts: [],
    startTime: Date.now(),
    pendingIntents: new Map(),
  });

  // Core game tick - processes one frame
  const tick = useCallback(
    (currentTime: number) => {
      if (!isRunningRef.current || isPausedRef.current) {
        animationFrameRef.current = requestAnimationFrame(tick);
        return;
      }

      // Calculate delta time
      const rawDeltaTime = lastTimeRef.current
        ? Math.min(currentTime - lastTimeRef.current, MAX_FRAME_TIME)
        : TARGET_FRAME_TIME;
      lastTimeRef.current = currentTime;

      // DD-16: Apply clutch moment time scale (slow motion during clutch)
      const timeScale = getEffectiveTimeScale(juiceSystem);
      const deltaTime = rawDeltaTime * timeScale;

      const state = stateRef.current;
      const input = inputRef.current;

      // Skip if in non-playing state
      if (state.status !== 'playing') {
        animationFrameRef.current = requestAnimationFrame(tick);
        return;
      }

      // =======================================================================
      // PHASE 1: Input (< 1ms)
      // =======================================================================
      const playerVelocity = {
        x: 0,
        y: 0,
      };

      if (input) {
        if (input.up) playerVelocity.y -= 1;
        if (input.down) playerVelocity.y += 1;
        if (input.left) playerVelocity.x -= 1;
        if (input.right) playerVelocity.x += 1;

        // Normalize diagonal movement
        const magnitude = Math.sqrt(
          playerVelocity.x * playerVelocity.x + playerVelocity.y * playerVelocity.y
        );
        if (magnitude > 0) {
          playerVelocity.x = (playerVelocity.x / magnitude) * state.player.moveSpeed;
          playerVelocity.y = (playerVelocity.y / magnitude) * state.player.moveSpeed;
        }
      }

      // =======================================================================
      // PHASE 1.5: Dash (DD-10)
      // =======================================================================
      let dashState = state;
      const extendedInput = input as { dashPressed?: boolean; dashConsumed?: boolean } | null;
      const activeUpgradesForDash = state.player.activeUpgrades as ActiveUpgrades | undefined;

      if (
        extendedInput?.dashPressed &&
        !extendedInput?.dashConsumed &&
        activeUpgradesForDash?.dashDistance &&
        activeUpgradesForDash.dashDistance > 0
      ) {
        // Dash in movement direction (or last velocity if not moving)
        const dashDistance = activeUpgradesForDash.dashDistance;
        let dashDirX = playerVelocity.x;
        let dashDirY = playerVelocity.y;

        // Normalize direction
        const magnitude = Math.sqrt(dashDirX * dashDirX + dashDirY * dashDirY);
        if (magnitude > 0) {
          dashDirX = dashDirX / magnitude;
          dashDirY = dashDirY / magnitude;
        } else {
          // If not moving, dash right by default
          dashDirX = 1;
          dashDirY = 0;
        }

        // Calculate new position
        let newX = state.player.position.x + dashDirX * dashDistance;
        let newY = state.player.position.y + dashDirY * dashDistance;

        // Clamp to arena bounds
        newX = Math.max(35, Math.min(765, newX));
        newY = Math.max(35, Math.min(565, newY));

        dashState = {
          ...state,
          player: {
            ...state.player,
            position: { x: newX, y: newY },
          },
        };

        // Mark dash as consumed
        extendedInput.dashConsumed = true;
      }

      // =======================================================================
      // PHASE 2: Physics (< 5ms)
      // =======================================================================
      const physicsResult = updatePhysics(dashState, playerVelocity, deltaTime);

      // DD-21: Emit telegraph updates for rendering
      if (physicsResult.telegraphs && physicsResult.telegraphs.length > 0) {
        callbacks.onTelegraphsUpdate?.(physicsResult.telegraphs);
      }

      // =======================================================================
      // PHASE 3: Collision Detection (< 3ms)
      // =======================================================================
      const collisionResult = checkCollisions(physicsResult.state);

      let newState = collisionResult.state;

      // DD-21: Apply enemy attack damage (separate from contact damage)
      if (physicsResult.enemyDamageDealt > 0) {
        newState = {
          ...newState,
          player: {
            ...newState.player,
            health: Math.max(0, newState.player.health - physicsResult.enemyDamageDealt),
          },
        };

        // Trigger damage juice
        juiceSystem.emitDamage(newState.player.position, physicsResult.enemyDamageDealt);

        // Trigger damage sound callback
        callbacks.onPlayerDamaged?.(physicsResult.enemyDamageDealt);

        // Check for game over from attack damage
        if (newState.player.health <= 0) {
          newState = { ...newState, status: 'gameover' };
          callbacks.onGameOver(newState);

          emitWitnessMark(witnessContextRef.current, {
            type: 'run_ended',
            gameTime: newState.gameTime,
            context: buildWitnessContext(newState),
            deathCause: 'enemy_attack',  // DD-21: More specific death cause
          });
        }
      }

      // Process collision events
      for (const event of collisionResult.events) {
        switch (event.type) {
          case 'enemy_killed': {
            // Add XP
            const xpValue = event.xpValue ?? 10;
            const enemyType = event.enemyType ?? 'basic';

            // DD-12: Vampiric - heal on kill
            const activeUpgrades = newState.player.activeUpgrades as ActiveUpgrades | undefined;
            const vampiricPercent = activeUpgrades?.vampiricPercent ?? 0;
            let newHealth = newState.player.health;

            if (vampiricPercent > 0) {
              const healAmount = Math.floor(
                newState.player.maxHealth * (vampiricPercent / 100)
              );
              newHealth = Math.min(
                newState.player.maxHealth,
                newState.player.health + healAmount
              );

              // TODO: Add emitHeal to juice system for vampiric visual feedback
              // juiceSystem.emitHeal?.(event.position, healAmount);
            }

            newState = {
              ...newState,
              player: {
                ...newState.player,
                xp: newState.player.xp + xpValue,
                health: newHealth,
              },
              totalEnemiesKilled: newState.totalEnemiesKilled + 1,
              score: newState.score + xpValue * 10,
            };

            // Trigger juice (DD-5: Fun Floor - kill = particles + sound + XP)
            juiceSystem.emitKill(event.position, enemyType);

            // Trigger kill sound callback (DD-5)
            callbacks.onEnemyKilled?.(enemyType);

            // DD-14: Burst - AoE damage on kill
            if (activeUpgrades?.burstRadius && activeUpgrades.burstRadius > 0) {
              const burstDamage = activeUpgrades.burstDamage ?? 10;
              const burstRadius = activeUpgrades.burstRadius;

              // Apply damage to enemies within burst radius
              newState = {
                ...newState,
                enemies: newState.enemies.map((enemy) => {
                  const dx = enemy.position.x - event.position.x;
                  const dy = enemy.position.y - event.position.y;
                  const distance = Math.sqrt(dx * dx + dy * dy);

                  if (distance < burstRadius && distance > 0) {
                    return { ...enemy, health: enemy.health - burstDamage };
                  }
                  return enemy;
                }),
              };
            }

            // Async witness mark (non-blocking)
            emitWitnessMark(witnessContextRef.current, {
              type: 'enemy_killed',
              gameTime: newState.gameTime,
              context: buildWitnessContext(newState),
            });
            break;
          }

          case 'player_hit': {
            const damageAmount = event.damage ?? 10;
            newState = {
              ...newState,
              player: {
                ...newState.player,
                health: Math.max(0, newState.player.health - damageAmount),
              },
            };

            // Trigger damage juice
            juiceSystem.emitDamage(newState.player.position, damageAmount);

            // Trigger damage sound callback (DD-5)
            callbacks.onPlayerDamaged?.(damageAmount);

            // DD-16: Check for clutch moment (survived near-death)
            if (newState.player.health > 0) {
              const healthFraction = newState.player.health / newState.player.maxHealth;
              // Count threats within 100 pixels of player
              const threatCount = newState.enemies.filter((enemy) => {
                const dx = enemy.position.x - newState.player.position.x;
                const dy = enemy.position.y - newState.player.position.y;
                return Math.sqrt(dx * dx + dy * dy) < 100;
              }).length;

              const clutchConfig = checkClutchMoment(healthFraction, threatCount);
              if (clutchConfig) {
                // Determine clutch level based on config
                const clutchLevel =
                  clutchConfig.timeScale <= 0.2
                    ? 'full'
                    : clutchConfig.timeScale <= 0.5
                      ? 'medium'
                      : 'critical';
                juiceSystem.triggerClutch(clutchLevel, clutchConfig.durationMs);
              }
            }

            // Check for game over
            if (newState.player.health <= 0) {
              newState = { ...newState, status: 'gameover' };
              callbacks.onGameOver(newState);

              // Seal witness trace
              emitWitnessMark(witnessContextRef.current, {
                type: 'run_ended',
                gameTime: newState.gameTime,
                context: buildWitnessContext(newState),
                deathCause: 'enemy_damage',
              });
            }
            break;
          }
        }
      }

      // =======================================================================
      // PHASE 4: Spawning
      // =======================================================================
      const spawnResult: SpawnResult = updateSpawner(newState, deltaTime);
      newState = spawnResult.state;

      // Wave complete event
      if (spawnResult.waveComplete) {
        juiceSystem.emitWaveComplete(newState.wave);
        callbacks.onWaveComplete(newState.wave);

        emitWitnessMark(witnessContextRef.current, {
          type: 'wave_completed',
          gameTime: newState.gameTime,
          context: buildWitnessContext(newState),
          wave: newState.wave,
        });
      }

      // =======================================================================
      // PHASE 4.5: Metamorphosis (DD-030)
      // =======================================================================
      // Update enemy survival times and pulsing states
      // deltaTime is in ms, but survivalTime and thresholds are in seconds
      const metamorphResult: MetamorphosisResult = updateMetamorphosis(
        newState.enemies,
        deltaTime / 1000, // Convert ms to seconds
        newState.hasWitnessedFirstMetamorphosis ?? false
      );

      // Replace enemies with updated versions
      // Note: metamorphResult.enemies already includes any new colossals
      newState = {
        ...newState,
        enemies: metamorphResult.enemies,
        hasWitnessedFirstMetamorphosis:
          (newState.hasWitnessedFirstMetamorphosis ?? false) ||
          metamorphResult.isFirstMetamorphosis,
      };

      // Handle first metamorphosis revelation (DD-030-3)
      if (metamorphResult.isFirstMetamorphosis) {
        // Emit witness mark for the revelation
        emitWitnessMark(witnessContextRef.current, {
          type: 'first_metamorphosis',
          gameTime: newState.gameTime,
          context: buildWitnessContext(newState),
        });

        // Trigger revelation visual (if juice system supports it)
        // juiceSystem.triggerRevelation?.();
      }

      // =======================================================================
      // PHASE 4.6: Colossal Behavior (DD-030-4)
      // =======================================================================
      // Update THE TIDE colossals with their special behavior
      const colossalEnemies = newState.enemies.filter(e => e.type === 'colossal_tide');
      if (colossalEnemies.length > 0) {
        let nonColossalEnemies = newState.enemies.filter(e => e.type !== 'colossal_tide');

        // Update each colossal
        const updatedColossals = colossalEnemies.map(colossal => {
          const result = updateColossalBehavior(
            colossal,
            nonColossalEnemies,
            newState.player,
            newState.gameTime,
            deltaTime / 1000 // Convert ms to seconds
          );

          // Handle fission (colossal splits into shamblers at 25% HP)
          if (result.fissionedEnemies.length > 0) {
            // Add shamblers to non-colossals
            nonColossalEnemies = [...nonColossalEnemies, ...result.fissionedEnemies];
            return null; // Remove the original colossal (it died)
          }

          // Handle absorbed enemies (remove them from the list)
          if (result.absorbedEnemyIds.length > 0) {
            nonColossalEnemies = nonColossalEnemies.filter(
              e => !result.absorbedEnemyIds.includes(e.id)
            );
          }

          return result.colossal;
        }).filter((c): c is NonNullable<typeof c> => c !== null && c.health > 0);

        newState = {
          ...newState,
          enemies: [...nonColossalEnemies, ...updatedColossals],
        };
      }

      // =======================================================================
      // PHASE 5: Level Up Check
      // =======================================================================
      if (newState.player.xp >= newState.player.xpToNextLevel) {
        // Level up!
        const newLevel = newState.player.level + 1;
        const xpOverflow = newState.player.xp - newState.player.xpToNextLevel;
        const newXpRequired = Math.floor(newState.player.xpToNextLevel * 1.5);

        // Generate upgrade choices (DD-6: verb-based upgrades)
        const choices = generateUpgradeChoicesForState(newState);

        // Only pause for upgrade selection if there are choices available
        // When all upgrades are owned, skip the upgrade UI and continue playing
        const shouldPause = choices.length > 0;

        newState = {
          ...newState,
          status: shouldPause ? 'upgrade' : 'playing',
          player: {
            ...newState.player,
            level: newLevel,
            xp: xpOverflow,
            xpToNextLevel: newXpRequired,
          },
        };

        // Emit level up juice (DD-5: level-up = pause + fanfare)
        juiceSystem.emitLevelUp(newLevel);

        // Record for ghost system
        emitWitnessMark(witnessContextRef.current, {
          type: 'level_up',
          gameTime: newState.gameTime,
          context: buildWitnessContext(newState),
          level: newLevel,
          choices,
        });

        // Only show upgrade UI if there are choices
        if (shouldPause) {
          callbacks.onLevelUp(newState, choices);
        }
      }

      // =======================================================================
      // PHASE 6: Update Game Time
      // =======================================================================
      newState = {
        ...newState,
        gameTime: newState.gameTime + deltaTime,
      };

      // =======================================================================
      // PHASE 7: Process Juice System
      // =======================================================================
      processJuice(juiceSystem, deltaTime, newState);

      // =======================================================================
      // PHASE 8: Emit State Update
      // =======================================================================
      stateRef.current = newState;
      callbacks.onStateUpdate(newState);

      // Schedule next frame
      animationFrameRef.current = requestAnimationFrame(tick);
    },
    [inputRef, callbacks, juiceSystem]
  );

  // Start the game loop
  const start = useCallback(() => {
    if (isRunningRef.current) return;

    isRunningRef.current = true;
    isPausedRef.current = false;
    lastTimeRef.current = 0;

    // Initialize witness context for new run
    witnessContextRef.current = {
      runId: `run-${Date.now()}`,
      marks: [],
      ghosts: [],
      startTime: Date.now(),
      pendingIntents: new Map(),
    };

    animationFrameRef.current = requestAnimationFrame(tick);
  }, [tick]);

  // Stop the game loop completely
  const stop = useCallback(() => {
    isRunningRef.current = false;
    isPausedRef.current = false;
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  }, []);

  // Pause (keep loop running but don't process)
  const pause = useCallback(() => {
    isPausedRef.current = true;
  }, []);

  // Resume from pause
  const resume = useCallback(() => {
    isPausedRef.current = false;
    lastTimeRef.current = 0; // Reset delta to prevent time jump
  }, []);

  // Reset game state
  const reset = useCallback(() => {
    stateRef.current = initialState;
    witnessContextRef.current = {
      runId: `run-${Date.now()}`,
      marks: [],
      ghosts: [],
      startTime: Date.now(),
      pendingIntents: new Map(),
    };
  }, [initialState]);

  // Set game state directly (for starting with specific state)
  const setState = useCallback((state: GameState) => {
    stateRef.current = state;
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return {
    start,
    stop,
    pause,
    resume,
    reset,
    setState,
    isRunning: isRunningRef.current,
  };
}

// =============================================================================
// Helpers
// =============================================================================

function buildWitnessContext(state: GameState): {
  wave: number;
  health: number;
  maxHealth: number;
  upgrades: string[];
  synergies: string[];
  xp: number;
  enemiesKilled: number;
} {
  return {
    wave: state.wave,
    health: state.player.health,
    maxHealth: state.player.maxHealth,
    upgrades: state.player.upgrades,
    synergies: state.player.synergies,
    xp: state.player.xp,
    enemiesKilled: state.totalEnemiesKilled,
  };
}

function generateUpgradeChoicesForState(state: GameState): string[] {
  // Use the new verb-based upgrade system (DD-6)
  const ownedUpgrades = state.player.upgrades as UpgradeType[];
  const choices = generateUpgradeChoices(ownedUpgrades, 3);
  return choices.map((u) => u.id);
}

export default useGameLoop;
