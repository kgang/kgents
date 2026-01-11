/**
 * WASM Survivors Witnessed Run Lab
 *
 * A Vampire Survivors-style game with witness layer integration.
 * Every run generates a crystallized proof of the player's journey.
 *
 * Key Design Decisions:
 * - DD-1: Invisible Witness - Zero witness HUD during play
 * - DD-2: Ghost as Honor - Unchosen alternatives shown with neutral language
 * - DD-3: Crystal as Proof - Compressed, shareable run summary
 * - DD-5: Fun Floor - Input < 16ms, kill = particles + sound + XP
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 * @see pilots/wasm-survivors-game/.outline.md
 */

import { useState, useCallback, useRef, useMemo, useEffect } from 'react';
import type { GameState, EnemyType, Vector2, Ghost, GameCrystal, Trace } from './types';
import { useGameLoop } from './hooks/useGameLoop';
import { useInput } from './hooks/useInput';
import { useSoundEngine } from './hooks/useSoundEngine';
// UNIFIED AUDIO: KENT Fugue is THE music system. SoundEngine handles SFX.
// EmergentAudio and ProceduralMusic disabled to eliminate conflicts.
// import { useEmergentAudio, gameStateToAudioState } from './hooks/useEmergentAudio';
// import { useProceduralMusic } from './hooks/useProceduralMusic';
import { useKentFugue } from './hooks/useKentFugue';
import { useHornetSound } from './hooks/useHornetSound';
import { useDebugAPI } from './hooks/useDebugAPI';
import { useDebugControls } from './hooks/useDebugControls';
import { createInitialGameState } from './systems/physics';
import { startWave, resetSpawner } from './systems/spawn';
import { createJuiceSystem } from './systems/juice';
import { crystallize, type WitnessContext } from './systems/witness';
import { GameCanvas } from './components/GameCanvas';
import { UpgradeUI } from './components/UpgradeUI';
import { CrystalView } from './components/CrystalView';
import { DeathOverlay, type DeathInfo } from './components/DeathOverlay';
import { CrystallizationOverlay } from './components/CrystallizationOverlay';
import { DebugOverlay } from './components/DebugOverlay';
import { AudioDebugOverlay } from './components/AudioDebugOverlay';
import { VoiceLineOverlay } from './components/VoiceLineOverlay';
import { HornetIcon, SkullIcon, LightningIcon, ArrowUpIcon, GamepadIcon } from './components/Icons';
import { ARENA_WIDTH, ARENA_HEIGHT } from './systems/physics';
import { COLORS, SHAKE } from './systems/juice';
import { generateAbilityChoices, type AbilityId, type ActiveAbilities, type ComputedEffects } from './systems/abilities';
import {
  type WildUpgradeType,
  type WildUpgradeState,
  createInitialWildUpgradeState,
  getWildUpgrade,
} from './systems/wild-upgrades';
import { BEE_BEHAVIORS, type TelegraphData } from './systems/enemies';
import type { AttackType } from './components/DeathOverlay';
import type { VoiceLine, ArcPhase, EmotionalState } from './systems/contrast';

// =============================================================================
// Types
// =============================================================================

type GamePhase = 'menu' | 'playing' | 'upgrade' | 'crystallizing' | 'gameover' | 'crystal';

interface UpgradeState {
  choices: string[];
  level: number;
}

// =============================================================================
// Main Component
// =============================================================================

export function WASMSurvivors() {
  // Game state
  const [gameState, setGameState] = useState<GameState>(createInitialGameState());
  const [phase, setPhase] = useState<GamePhase>('menu');
  const [upgradeState, setUpgradeState] = useState<UpgradeState | null>(null);
  const [crystal, setCrystal] = useState<GameCrystal | null>(null);
  const [deathInfo, setDeathInfo] = useState<DeathInfo | null>(null);

  // Debug API: Telegraph state for debug visualization
  const [telegraphs, setTelegraphs] = useState<TelegraphData[]>([]);

  // Part VI: Emotional state (arc, contrasts, voice lines)
  const [currentVoiceLine, setCurrentVoiceLine] = useState<VoiceLine | null>(null);
  const [arcPhase, setArcPhase] = useState<ArcPhase>('POWER');
  const [emotionalState, setEmotionalState] = useState<EmotionalState | null>(null);

  // Run 036: Melee attack state for visual rendering
  const [meleeState, setMeleeState] = useState<import('./systems/melee').MeleeAttackState | null>(null);

  // Pause state
  const [isPaused, setIsPaused] = useState(false);

  // Debug API: Invincibility state (managed separately from game state)
  const invincibleRef = useRef<boolean>(false);

  // Witness context (persisted across game loop)
  const witnessContextRef = useRef<WitnessContext>({
    runId: `run-${Date.now()}`,
    marks: [],
    ghosts: [],
    startTime: Date.now(),
    pendingIntents: new Map(),
  });

  // Wild upgrades tracking (new wild upgrades system)
  const wildUpgradeStateRef = useRef<WildUpgradeState>(createInitialWildUpgradeState());
  const wildUpgradesRef = useRef<WildUpgradeType[]>([]);

  // Juice system (persisted)
  const juiceSystem = useMemo(() => createJuiceSystem(), []);

  // Memoize upgrade UI props to prevent re-renders during upgrade phase
  // Only recalculate when entering upgrade phase (upgradeState changes)
  const upgradeUIProps = useMemo(() => {
    if (!upgradeState) return null;
    return {
      recentGhosts: witnessContextRef.current.ghosts.slice(-3),
      currentAbilities: wildUpgradesRef.current,
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [upgradeState]); // Only recalc when upgrade state changes, not on every gameState update

  // Input handling
  // Note: clearFrameFlags and updateSpaceHoldDuration are available from useInput
  // but currently the game loop clears flags inline. Could be refactored.
  const { inputRef, resetInput } = useInput();

  // Sound engine (DD-5) - handles SFX (kills, damage, dash, XP, etc.)
  const soundEngine = useSoundEngine();

  // Track recent kills and combo for intensity calculations
  const recentKillsRef = useRef(0);
  const comboCountRef = useRef(0);

  // KENT Fugue System - THE UNIFIED MUSIC SYSTEM
  // K-E-N-T cryptogram: B#-F#-D#-A (two tritones = maximum tension!)
  // 4-voice fugue with percussion in C# minor
  const kentFugue = useKentFugue();
  const lastFrameTimeRef = useRef(performance.now());

  // Hornet Sound Identity - Unique bee/swarm synthesis layer
  // Works alongside KENT Fugue: swarm texture + horror drone + heartbeat + ambience
  const hornetSound = useHornetSound();
  const hornetSoundRef = useRef(hornetSound);
  hornetSoundRef.current = hornetSound;

  // Refs to track KENT fugue state (avoids stale closure in interval)
  const kentFugueRunningRef = useRef(false);
  kentFugueRunningRef.current = kentFugue.isRunning;
  const kentFugueUpdateRef = useRef(kentFugue.update);
  kentFugueUpdateRef.current = kentFugue.update;

  // Performance: Store game state in refs for music systems to avoid per-frame useEffect triggers
  const gameStateRef = useRef(gameState);
  gameStateRef.current = gameState;
  const phaseRef = useRef(phase);
  phaseRef.current = phase;

  // Low health heartbeat management
  // Plays heartbeat loop when player health drops below 30% and stops when above or on death/game end
  const LOW_HEALTH_THRESHOLD = 0.3;
  useEffect(() => {
    // Only manage heartbeat during active gameplay
    if (phase !== 'playing') {
      // Stop heartbeat when not playing (menu, upgrade screen, game over, etc.)
      soundEngine.stopHeartbeatLoop();
      return;
    }

    const healthFraction = gameState.player.health / gameState.player.maxHealth;
    const isLowHealth = healthFraction > 0 && healthFraction < LOW_HEALTH_THRESHOLD;

    if (isLowHealth) {
      soundEngine.startHeartbeatLoop();
    } else {
      soundEngine.stopHeartbeatLoop();
    }
  }, [gameState.player.health, gameState.player.maxHealth, phase, soundEngine]);

  // ============================================================================
  // KENT FUGUE: Interval-based music update (PERFORMANCE FIX)
  // ============================================================================
  // UNIFIED AUDIO ARCHITECTURE:
  // - KENT Fugue: THE music system (4-voice fugue + percussion in C# minor)
  // - SoundEngine: SFX only (kills, damage, dash, XP, etc.)
  //
  // Music doesn't need 60Hz updates. 10Hz (100ms) is plenty for:
  // - Beat transitions at up to 600 BPM
  // - Smooth parameter interpolation
  // - Phase/mood changes
  // ============================================================================
  useEffect(() => {
    const MUSIC_UPDATE_INTERVAL_MS = 100; // 10 updates/sec is plenty for music

    const musicUpdateLoop = () => {
      const currentPhase = phaseRef.current;
      const currentGameState = gameStateRef.current;

      // ---- KENT Fugue Update (THE music system) ----
      // Use ref to avoid stale closure - kentFugue.isRunning won't update in interval
      if (currentPhase === 'playing' && kentFugueRunningRef.current) {
        // Calculate delta time since last music update
        const now = performance.now();
        let deltaTime = (now - lastFrameTimeRef.current) / 1000;
        lastFrameTimeRef.current = now;

        // TIMING FIX: Cap delta time to prevent huge jumps when tab is backgrounded
        // or when there's a frame hiccup. Max 200ms prevents audio from going haywire.
        const MAX_DELTA_TIME = 0.2; // 200ms max
        deltaTime = Math.min(deltaTime, MAX_DELTA_TIME);

        // Determine game phase for music
        const healthFraction = currentGameState.player.health / currentGameState.player.maxHealth;
        const hasBall = currentGameState.ballPhase !== null;

        let musicGamePhase: 'exploration' | 'combat' | 'crisis' | 'death';
        if (currentGameState.player.health <= 0) {
          musicGamePhase = 'death';
        } else if (hasBall || healthFraction < 0.25) {
          musicGamePhase = 'crisis';
        } else if (currentGameState.enemies.length > 15 || recentKillsRef.current > 3) {
          musicGamePhase = 'combat';
        } else {
          musicGamePhase = 'exploration';
        }

        // Calculate intensity (0-1)
        const intensity = Math.min(1, Math.max(0,
          (currentGameState.enemies.length / 30) * 0.4 +
          (1 - healthFraction) * 0.3 +
          (currentGameState.wave / 15) * 0.2 +
          (recentKillsRef.current / 10) * 0.1
        ));

        // Update the KENT fugue (pass wave number for voice progression)
        kentFugueUpdateRef.current(deltaTime, intensity, musicGamePhase, currentGameState.wave);

        // Update Hornet Sound Identity (swarm synthesis + horror layers)
        // Uses coordination to balance with KENT Fugue
        if (hornetSoundRef.current.isPlaying) {
          hornetSoundRef.current.update(currentGameState);
        }
      }
    };

    // Start the interval
    const intervalId = setInterval(musicUpdateLoop, MUSIC_UPDATE_INTERVAL_MS);

    return () => clearInterval(intervalId);
  }, []); // All state accessed via refs - no dependencies needed

  // Debug controls (keyboard shortcuts for debug mode)
  useDebugControls();

  // Check if debug mode is enabled via URL parameter
  const isDebugMode = useMemo(() => {
    if (typeof window === 'undefined') return false;
    return new URLSearchParams(window.location.search).get('debug') === 'true';
  }, []);

  // Check if audio debug mode is enabled via URL parameter (?debug=audio)
  const isAudioDebugMode = useMemo(() => {
    if (typeof window === 'undefined') return false;
    return new URLSearchParams(window.location.search).get('debug') === 'audio';
  }, []);

  // Game loop callbacks
  const handleStateUpdate = useCallback((state: GameState) => {
    setGameState(state);
  }, []);

  const handleGameOver = useCallback((finalState: GameState) => {
    // DD-29-3: Start with crystallization phase before game over
    setPhase('crystallizing');

    // Play damage sound on death
    soundEngine.playDamage();

    // DD-8: Capture death info for DeathOverlay
    // Find the likely killer (nearest enemy to player)
    const playerPos = finalState.player.position;
    let nearestEnemy = finalState.enemies[0];
    let nearestDist = Infinity;
    for (const enemy of finalState.enemies) {
      const dx = enemy.position.x - playerPos.x;
      const dy = enemy.position.y - playerPos.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < nearestDist) {
        nearestDist = dist;
        nearestEnemy = enemy;
      }
    }

    // DD-21: Determine attack type based on enemy behavior state
    // Map old types to bee types for display
    const rawType = nearestEnemy?.type ?? 'worker';
    const killerType = rawType as EnemyType;
    let attackType: AttackType = 'contact'; // Default to contact damage

    if (nearestEnemy?.behaviorState === 'attack') {
      // Enemy was in attack state - use their specific attack type
      const behavior = BEE_BEHAVIORS[killerType];
      if (behavior) {
        // DD-21: Map bee behavior attack types to DeathOverlay AttackType
        // AttackType is: 'swarm' | 'sting' | 'block' | 'sticky' | 'combo' | 'contact'
        const attackMap: Record<string, AttackType> = {
          swarm: 'swarm',
          sting: 'sting',
          block: 'block',
          sticky: 'sticky',
          combo: 'combo',
          elite: 'combo', // Royal bees use combo attacks
        };
        attackType = attackMap[behavior.attackType] ?? 'contact';
      }
    }

    setDeathInfo({
      killerType,
      attackType, // DD-21: Now includes specific attack attribution
      killerPosition: nearestEnemy?.position ?? { x: 0, y: 0 },
      damageDealt: 1, // Most enemies deal 1 damage
      healthBefore: 1, // Player was at 1 HP before dying
      wave: finalState.wave,
      gameTime: finalState.gameTime,
      // DD-18: Additional fields for death narrative
      totalKills: finalState.totalEnemiesKilled,
      upgrades: wildUpgradesRef.current,
      score: finalState.score,
    });

    // Create crystal from witness context
    const ctx = witnessContextRef.current;
    const trace: Trace = {
      runId: ctx.runId,
      startTime: ctx.startTime,
      endTime: Date.now(),
      marks: ctx.marks,
      finalContext: {
        wave: finalState.wave,
        health: finalState.player.health,
        maxHealth: finalState.player.maxHealth,
        upgrades: finalState.player.upgrades,
        synergies: finalState.player.synergies ?? [],
        xp: finalState.player.xp,
        enemiesKilled: finalState.totalEnemiesKilled,
      },
      deathCause: 'enemy_damage',
      sealed: true,
    };

    const newCrystal = crystallize(ctx, trace);
    setCrystal(newCrystal);
  }, []);

  const handleLevelUp = useCallback((state: GameState, choices: string[]) => {
    setPhase('upgrade');
    setUpgradeState({
      choices,
      level: state.player.level,
    });

    // Play level up fanfare (DD-5)
    soundEngine.playLevelUp();
  }, [soundEngine]);

  const handleWaveComplete = useCallback((wave: number) => {
    console.log(`Wave ${wave} complete!`);
    // Play wave complete sound (DD-5)
    soundEngine.playWave();
  }, [soundEngine]);

  // Run 036: ASMR Audio - Sound callbacks with layered kill sounds
  // THREE layers: CRUNCH + SNAP + DECAY with spatial audio and multi-kill escalation
  const handleEnemyKilled = useCallback((
    enemyType: import('./types').EnemyType,
    tier: import('./types').KillTier,
    comboCount: number,
    position: import('./types').Vector2
  ) => {
    // Update spatial config with player position for stereo panning
    soundEngine.updateSpatialConfig(gameState.player.position);
    // Play layered ASMR kill sound
    soundEngine.playKill(enemyType, tier, comboCount, position);

    // Update kill tracking for KENT Fugue intensity calculation
    recentKillsRef.current = comboCount;
    comboCountRef.current = tier === 'massacre' ? 10 : tier === 'multi' ? 3 : 1;
  }, [soundEngine, gameState.player.position]);

  const handlePlayerDamaged = useCallback((_damage: number = 1) => {
    soundEngine.playDamage();
  }, [soundEngine]);

  // Debug API: Telegraph update callback
  const handleTelegraphsUpdate = useCallback((newTelegraphs: TelegraphData[]) => {
    setTelegraphs(newTelegraphs);
  }, []);

  // Part VI: Voice line callback
  const handleVoiceLine = useCallback((line: VoiceLine) => {
    setCurrentVoiceLine(line);
  }, []);

  // Part VI: Phase transition callback
  const handlePhaseTransition = useCallback((phase: ArcPhase) => {
    setArcPhase(phase);
  }, []);

  // Part VI: Emotional state update callback
  const handleEmotionalStateUpdate = useCallback((state: EmotionalState) => {
    setEmotionalState(state);
    // Also update arc phase from state
    setArcPhase(state.arc.currentPhase);
  }, []);

  // Run 036: Melee state update callback
  const handleMeleeStateUpdate = useCallback((state: import('./systems/melee').MeleeAttackState) => {
    setMeleeState(state);
  }, []);

  // Run 038: Melee event callback - triggers sounds for mandible strikes
  const handleMeleeEvent = useCallback((event: import('./systems/melee').MeleeEvent) => {
    if (event.type === 'attack_hit') {
      // Play satisfying hit sound for mandible strike connecting
      // Use the ASMR audio system for proper layered crunch
      soundEngine.playEnemyHit(15, gameState.player.position);
    } else if (event.type === 'attack_massacre') {
      // 5+ kills in one swing! Play massacre sound
      soundEngine.play('massacre', { volume: 0.9 });
    }
  }, [soundEngine, gameState.player.position]);

  // THE BALL Formation event callback (Appendix E JUICE: Audio cue for scout coordination)
  // RUN 039: Alarm pheromone plays on GATHERING start (earliest warning)
  // RUN 049: Full audio sequencing for THE BALL phases
  const handleBallEvent = useCallback((event: import('./systems/formation').FormationEvent) => {
    // =========================================================================
    // THE BALL Audio Sequencing (Run 049)
    // "THE BALL should have 3s complete silence then bass drop"
    // =========================================================================
    switch (event.type) {
      case 'ball_gathering_started':
        // Play alarm pheromone sound - signals scouts coordinating for THE BALL
        // This is the "oh no" audio warning that gives players a chance to react
        soundEngine.play('alarmPheromone');

        // Hornet Sound Identity: Play warning clicks for THE BALL formation
        hornetSound.playWarningClick();
        setTimeout(() => hornetSound.playWarningClick(), 300);
        setTimeout(() => hornetSound.playWarningClick(), 600);
        break;

      case 'ball_forming_started':
        // Transition to forming: Quick fade out (500ms)
        // Creates anticipation before the terrifying silence
        soundEngine.fadeOutAudio(500);
        break;

      case 'ball_silence_started':
        // TRUE SILENCE phase: Stop ALL audio for maximum dread
        // The setTrueSilence is already called by fadeOutAudio
        // No additional action needed - silence IS the action
        break;

      case 'ball_constrict_started':
        // After 3s of silence: BASS DROP + intense music
        // "THOOM" - the signature sound of THE BALL constricting
        soundEngine.playBassDrop();
        soundEngine.startIntense();
        break;

      case 'ball_escaped':
      case 'ball_dispersed':
      case 'ball_dissipating':
        // Dissipation: Fade back to normal music (1000ms)
        // Tension release - they survived or escaped
        soundEngine.fadeToNormal(1000);
        break;

      // RUN 039: Outside punch telegraph sounds
      case 'punch_hit':
        // Punch connected - use ASMR audio for proper layered impact
        soundEngine.playEnemyHit(25, event.position);
        break;

      case 'punch_whiff':
        // Player dodged! - GRAZE SOUND DISABLED
        break;
    }
  }, [soundEngine, hornetSound]);

  // Game loop
  const gameLoop = useGameLoop(
    gameState,
    inputRef,
    {
      onStateUpdate: handleStateUpdate,
      onGameOver: handleGameOver,
      onLevelUp: handleLevelUp,
      onWaveComplete: handleWaveComplete,
      onEnemyKilled: handleEnemyKilled,
      onPlayerDamaged: handlePlayerDamaged,
      onTelegraphsUpdate: handleTelegraphsUpdate,
      onVoiceLine: handleVoiceLine,
      onPhaseTransition: handlePhaseTransition,
      onEmotionalStateUpdate: handleEmotionalStateUpdate,
      onMeleeStateUpdate: handleMeleeStateUpdate,
      onMeleeEvent: handleMeleeEvent,  // Run 038: Mandible strike hit sounds
      onBallEvent: handleBallEvent,  // Appendix E JUICE: Alarm pheromone on BALL formation
    },
    juiceSystem
  );

  // Pause toggle handler (P key)
  const togglePause = useCallback(() => {
    if (phase !== 'playing') return; // Only pause during gameplay

    setIsPaused(prev => {
      const newPaused = !prev;
      if (newPaused) {
        gameLoop.pause();
      } else {
        gameLoop.resume();
      }
      return newPaused;
    });
  }, [phase, gameLoop]);

  // Pause keyboard handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key.toLowerCase() === 'p' && phase === 'playing') {
        e.preventDefault();
        togglePause();
      }
      // Also allow Escape to unpause
      if (e.key === 'Escape' && isPaused) {
        e.preventDefault();
        togglePause();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [phase, isPaused, togglePause]);

  // Reset pause state when game ends or restarts
  useEffect(() => {
    if (phase !== 'playing') {
      setIsPaused(false);
    }
  }, [phase]);

  // Start game
  const handleStartGame = useCallback(async () => {
    // CRITICAL: Stop the existing game loop first!
    // This ensures all refs get reset when start() is called.
    // Without this, start() returns early if isRunningRef is true,
    // leaving apex strike, combat state, etc. in stale state.
    gameLoop.stop();

    // RESET AUDIO FIRST - prevents buzz/ambient carry-over between runs
    // Fixes the "ambient bee buzzing carry-over" bug
    soundEngine.resetAudio();

    // Start KENT Fugue music system (requires user interaction for Web Audio API)
    // UNIFIED: Only KENT fugue runs - no competing systems
    // MUST await to ensure isRunning is set before game loop starts
    await kentFugue.start();

    // Start Hornet Sound Identity (swarm synthesis + horror layers)
    // Works alongside KENT Fugue for complete audio experience
    await hornetSound.initialize();
    hornetSound.start();

    // Reset input state to clear any held keys (e.g., space held during death)
    resetInput();

    // Reset juice system to clear particles and effects from previous run
    // This prevents visual artifacts from accumulating between games
    juiceSystem.reset();

    // Reset everything
    resetSpawner();
    const freshState = createInitialGameState();
    // Note: startWave uses a local stub GameState type, so we cast back to full GameState
    const startedState = startWave({ ...freshState, status: 'playing', wave: 1 }) as unknown as GameState;

    // Reset witness context
    witnessContextRef.current = {
      runId: `run-${Date.now()}`,
      marks: [],
      ghosts: [],
      startTime: Date.now(),
      pendingIntents: new Map(),
    };

    // Reset wild upgrades state
    wildUpgradeStateRef.current = createInitialWildUpgradeState();
    wildUpgradesRef.current = [];

    // Reset death info
    setDeathInfo(null);

    setGameState(startedState);
    setPhase('playing');
    setCrystal(null);
    // Reset emotional state for new run
    setCurrentVoiceLine(null);
    setArcPhase('POWER');
    setEmotionalState(null);
    gameLoop.setState(startedState);  // Sync game loop state with started state
    gameLoop.start();
  }, [gameLoop, resetInput, juiceSystem, kentFugue, hornetSound, soundEngine]);

  // Handle upgrade selection (WILD UPGRADES)
  const handleUpgradeSelect = useCallback(
    (upgradeId: string, alternatives: string[]) => {
      // Record ghost (DD-2: Ghost as Honor)
      const ghost: Ghost = {
        decisionPoint: gameState.gameTime,
        chosen: upgradeId,
        unchosen: alternatives,
        context: {
          wave: gameState.wave,
          health: gameState.player.health,
          maxHealth: gameState.player.maxHealth,
          upgrades: gameState.player.upgrades,
          synergies: gameState.player.synergies ?? [],
          xp: gameState.player.xp,
          enemiesKilled: gameState.totalEnemiesKilled,
        },
        projectedDrift: 0.1, // Simplified
      };
      witnessContextRef.current.ghosts.push(ghost);

      // Activate wild upgrade
      const wildUpgradeId = upgradeId as WildUpgradeType;
      const wildUpgrade = getWildUpgrade(wildUpgradeId);

      // Add to owned wild upgrades
      wildUpgradesRef.current = [...wildUpgradesRef.current, wildUpgradeId];

      // Activate the upgrade in state
      const newWildState = { ...wildUpgradeStateRef.current };
      switch (wildUpgradeId) {
        case 'echo':
          newWildState.echo = { ...newWildState.echo, active: true };
          break;
        case 'gravity_well':
          newWildState.gravityWell = { ...newWildState.gravityWell, active: true };
          break;
        case 'metamorphosis':
          newWildState.metamorphosis = { ...newWildState.metamorphosis, active: true };
          break;
        case 'blood_price':
          newWildState.bloodPrice = { ...newWildState.bloodPrice, active: true };
          break;
        case 'temporal_debt':
          newWildState.temporalDebt = { ...newWildState.temporalDebt, active: true };
          break;
        case 'swarm_mind':
          newWildState.swarmMind = { ...newWildState.swarmMind, active: true };
          break;
        case 'honey_trap':
          newWildState.honeyTrap = { ...newWildState.honeyTrap, active: true };
          break;
        case 'royal_decree':
          newWildState.royalDecree = { ...newWildState.royalDecree, active: true };
          break;
      }
      wildUpgradeStateRef.current = newWildState;

      // Check for synergies with previously owned upgrades
      const newSynergies: string[] = [];
      for (const ownedUpgrade of wildUpgradesRef.current.slice(0, -1)) {
        if (wildUpgrade) {
          const synergy = wildUpgrade.synergies[ownedUpgrade as WildUpgradeType];
          if (synergy && synergy.name !== 'Self') {
            newSynergies.push(synergy.name);
          }
        }
      }

      // Update game state with wild upgrade
      const newState: GameState = {
        ...gameState,
        status: 'playing',
        player: {
          ...gameState.player,
          upgrades: [...gameState.player.upgrades, upgradeId],
          synergies: [...(gameState.player.synergies ?? []), ...newSynergies],
        },
      };

      // Play synergy effect if new synergy discovered
      if (newSynergies.length > 0) {
        console.log('WILD SYNERGY DISCOVERED:', newSynergies.join(', '));
        // Wire shake: Synergy discovery - 10px + flash celebration (biggest moment!)
        juiceSystem.triggerShake(SHAKE.synergyDiscovery.amplitude, SHAKE.synergyDiscovery.duration);
      }

      setGameState(newState);
      setPhase('playing');
      setUpgradeState(null);
      gameLoop.setState(newState);  // Sync game loop state with upgraded state
      gameLoop.activateWildUpgrade(upgradeId as WildUpgradeType);  // WILD UPGRADES: Activate the upgrade mechanics
      gameLoop.resume();
    },
    [gameState, gameLoop, juiceSystem]
  );

  // DD-29-3: Handle crystallization completion
  const handleCrystallizationComplete = useCallback(() => {
    setPhase('gameover');
  }, []);

  // View crystal
  const handleViewCrystal = useCallback(() => {
    setPhase('crystal');
  }, []);

  // Close crystal
  const handleCloseCrystal = useCallback(() => {
    setPhase('menu');
  }, []);

  // =============================================================================
  // Debug API Callbacks
  // =============================================================================

  // Debug: Spawn an enemy at a position
  // Bee-themed types: worker, scout, guard, propolis, royal
  const handleDebugSpawn = useCallback((type: EnemyType, position: Vector2) => {
    // Enemy stats based on bee type
    type EnemyStats = { radius: number; health: number; damage: number; xpValue: number; color: string };
    const enemyStats: Partial<Record<EnemyType, EnemyStats>> = {
      worker: { radius: 12, health: 20, damage: 10, xpValue: 10, color: '#F4D03F' },
      scout: { radius: 8, health: 10, damage: 8, xpValue: 15, color: '#F39C12' },
      guard: { radius: 20, health: 80, damage: 20, xpValue: 30, color: '#E74C3C' },
      propolis: { radius: 10, health: 15, damage: 15, xpValue: 20, color: '#9B59B6' },
      royal: { radius: 35, health: 300, damage: 30, xpValue: 100, color: '#3498DB' },
    };
    const defaultStats: EnemyStats = { radius: 12, health: 20, damage: 10, xpValue: 10, color: '#F4D03F' };
    const stats = enemyStats[type] ?? defaultStats;
    const enemy = {
      id: `debug-enemy-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      type,
      position: { x: position.x, y: position.y },
      velocity: { x: 0, y: 0 },
      radius: stats.radius,
      health: stats.health,
      maxHealth: stats.health,
      damage: stats.damage,
      speed: type === 'scout' ? 120 : type === 'guard' ? 60 : 80, // Bee speeds
      xpValue: stats.xpValue,
      color: stats.color,
      behaviorState: 'chase' as const,
      survivalTime: 0,
      coordinationState: 'idle' as const,
      pulsingState: 'normal' as const,
    };

    const newState: GameState = {
      ...gameState,
      enemies: [...gameState.enemies, enemy],
    };
    setGameState(newState);
    gameLoop.setState(newState);
  }, [gameState, gameLoop]);

  // Debug: Set invincibility
  const handleDebugSetInvincible = useCallback((invincible: boolean) => {
    invincibleRef.current = invincible;
    // Note: Actual invincibility is handled by modifying damage in the game loop
    // For now, we just set max health very high when invincible
    if (invincible) {
      const newState: GameState = {
        ...gameState,
        player: {
          ...gameState.player,
          health: 999999,
          maxHealth: 999999,
        },
      };
      setGameState(newState);
      gameLoop.setState(newState);
    }
  }, [gameState, gameLoop]);

  // Debug: Skip to next wave
  const handleDebugSkipWave = useCallback(() => {
    const newState: GameState = {
      ...gameState,
      wave: gameState.wave + 1,
      waveTimer: 0,
      enemies: [], // Clear current enemies
    };
    setGameState(newState);
    gameLoop.setState(newState);
  }, [gameState, gameLoop]);

  // Debug: Kill all enemies
  const handleDebugKillAllEnemies = useCallback(() => {
    const killedCount = gameState.enemies.length;
    const xpGained = gameState.enemies.reduce((sum, e) => sum + e.xpValue, 0);

    const newState: GameState = {
      ...gameState,
      enemies: [],
      totalEnemiesKilled: gameState.totalEnemiesKilled + killedCount,
      score: gameState.score + xpGained * 10,
      player: {
        ...gameState.player,
        xp: gameState.player.xp + xpGained,
      },
    };
    setGameState(newState);
    gameLoop.setState(newState);
  }, [gameState, gameLoop]);

  // Debug: Trigger level up (uses same ability system as normal level up)
  const handleDebugLevelUp = useCallback(() => {
    const newLevel = gameState.player.level + 1;
    // Use the new abilities system - same as normal level up
    const ownedAbilities = gameState.player.upgrades as AbilityId[];
    const mockAbilities: ActiveAbilities = {
      owned: ownedAbilities,
      levels: {} as Record<AbilityId, number>,
      computed: {} as ComputedEffects,
      runtime: {
        sawtoothCounter: 0,
        trophyScentKills: 0,
        updraftSpeedBonus: 0,
        updraftExpiry: 0,
        aggroPulseLastTime: 0,
        moltingBurstUsed: false,
        ablativeShellUsed: false,
        confusionClouds: [],
        deathMarkers: [],
        bitterTasteDebuffs: new Map(),
        heatRetentionActive: false,
      },
    };
    const choices = generateAbilityChoices(mockAbilities, 4);  // Run 040: 4 choices

    const newState: GameState = {
      ...gameState,
      status: 'upgrade',
      player: {
        ...gameState.player,
        level: newLevel,
        xpToNextLevel: Math.floor(gameState.player.xpToNextLevel * 1.5),
      },
    };

    setGameState(newState);
    setPhase('upgrade');
    setUpgradeState({
      choices,
      level: newLevel,
    });
    gameLoop.pause();
  }, [gameState, gameLoop]);

  // Initialize Debug API
  useDebugAPI({
    gameState,
    telegraphs,
    emotionalState,  // Part VI: Emotional state for debug
    ballState: gameLoop.getBallState(),  // Run 036: THE BALL state
    onSpawnEnemy: handleDebugSpawn,
    onSetInvincible: handleDebugSetInvincible,
    onSkipWave: handleDebugSkipWave,
    onKillAllEnemies: handleDebugKillAllEnemies,
    onLevelUp: handleDebugLevelUp,
    onForceBall: gameLoop.forceBall,  // Run 036: Force THE BALL
  });

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-4">
        {phase === 'menu' && (
          <MenuScreen onStart={handleStartGame} />
        )}

        {(phase === 'playing' || phase === 'upgrade') && (
          <div className="relative">
            <GameCanvas
              gameState={gameState}
              juiceSystem={juiceSystem}
              ballState={gameLoop.getBallState()}
              allBalls={gameLoop.getAllBalls()}
              meleeState={meleeState ?? undefined}
              apexState={gameLoop.getApexState()}
              chargePercent={gameLoop.getApexState().chargeLevel}
              attackCooldownPercent={gameLoop.getAttackCooldownPercent()}
              killStreak={gameLoop.getKillStreak()}
              hasFullArc={false}  // TODO: Implement via new ability system
              isDoubleStrikeReady={gameLoop.isDoubleStrikeReady()}
              territorialMarks={gameLoop.getTerritorialMarks()}
              deathMarkers={gameLoop.getDeathMarkers()}
              wildUpgradeState={gameLoop.getWildUpgradeState()}
              metamorphosisAbilities={gameLoop.getMetamorphosisAbilities()}
            />

            {/* Part VI: Voice line overlay */}
            <VoiceLineOverlay
              voiceLine={currentVoiceLine}
              arcPhase={arcPhase}
              onComplete={() => setCurrentVoiceLine(null)}
            />


            {phase === 'upgrade' && upgradeState && upgradeUIProps && (
              <UpgradeUI
                level={upgradeState.level}
                choices={upgradeState.choices}
                currentAbilities={upgradeUIProps.currentAbilities}
                recentGhosts={upgradeUIProps.recentGhosts}
                onSelect={handleUpgradeSelect}
              />
            )}

            {/* Pause overlay */}
            {isPaused && (
              <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-50 backdrop-blur-sm">
                <div className="text-center">
                  <div
                    className="text-4xl font-bold mb-4"
                    style={{ color: COLORS.player }}
                  >
                    PAUSED
                  </div>
                  <p className="text-gray-400 mb-6">
                    Press P or ESC to resume
                  </p>
                  <button
                    onClick={togglePause}
                    className="px-6 py-2 rounded-lg font-bold text-sm transition-all duration-200 hover:scale-105 border border-amber-500/50"
                    style={{ backgroundColor: COLORS.player, color: '#000' }}
                  >
                    RESUME
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* DD-29-3: Crystallization overlay shows during crystallizing phase */}
        {phase === 'crystallizing' && (
          <div className="relative">
            <GameCanvas
              gameState={gameState}
              juiceSystem={juiceSystem}
              ballState={gameLoop.getBallState()}
              allBalls={gameLoop.getAllBalls()}
              meleeState={meleeState ?? undefined}
              apexState={gameLoop.getApexState()}
              chargePercent={0}
              attackCooldownPercent={1}
              killStreak={0}
              wildUpgradeState={gameLoop.getWildUpgradeState()}
            />
            <CrystallizationOverlay
              deathPosition={gameState.player.position}
              arenaWidth={ARENA_WIDTH}
              arenaHeight={ARENA_HEIGHT}
              onComplete={handleCrystallizationComplete}
              durationMs={2000}
            />
          </div>
        )}

        {phase === 'gameover' && deathInfo && (
          <DeathOverlay
            death={deathInfo}
            ghostSummary={{
              ghostUpgrades: witnessContextRef.current.ghosts
                .flatMap(g => g.unchosen)
                .filter((id): id is WildUpgradeType =>
                  ['echo', 'gravity_well', 'metamorphosis', 'blood_price', 'temporal_debt', 'swarm_mind', 'honey_trap', 'royal_decree'].includes(id)
                ),
              pivotMoments: witnessContextRef.current.ghosts.length,
              alternateBuilds: [],
            }}
            onPlayAgain={handleStartGame}
          />
        )}

        {phase === 'gameover' && !deathInfo && (
          <GameOverScreen
            gameState={gameState}
            onPlayAgain={handleStartGame}
            onViewCrystal={handleViewCrystal}
          />
        )}

        {phase === 'crystal' && crystal && (
          <CrystalView
            crystal={crystal}
            ghosts={witnessContextRef.current.ghosts}
            onClose={handleCloseCrystal}
            onPlayAgain={handleStartGame}
          />
        )}
      </main>

      {/* Debug Overlay - only visible when ?debug=true */}
      {isDebugMode && <DebugOverlay />}

      {/* Audio Debug Overlay - only visible when ?debug=audio */}
      {isAudioDebugMode && <AudioDebugOverlay />}
    </div>
  );
}

// =============================================================================
// Sub-screens
// =============================================================================

// =============================================================================
// Lore Modal - The Japanese Hornet Story (One-time cinematic intro)
// =============================================================================

const LORE_STORAGE_KEY = 'bee-survivors-lore-seen';

// Hornet sprite colors (matching GameCanvas)
const HORNET_COLORS = {
  body: '#CC5500',      // Burnt Amber
  stripe: '#1A1A1A',    // Venom Black
  eyes: '#FFE066',      // Pollen Gold
  wing: '#4A6B8C',      // Wing Blue
  highlight: '#FF8C00', // Strike Orange
  shadow: '#662200',    // Dried Blood
};

/**
 * Animated hornet sprite for the lore modal
 * Matches the in-game player sprite style
 */
function HornetSprite({ size = 120 }: { size?: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const radius = size * 0.35;
    const cx = size / 2;
    const cy = size / 2;
    let animFrame: number;
    let startTime = Date.now();

    const draw = () => {
      const time = Date.now() - startTime;
      ctx.clearRect(0, 0, size, size);

      // Wing blur (animated)
      const wingPhase = (time / 16) % (Math.PI * 2); // 60hz flutter
      const wingAlpha = 0.3 + 0.1 * Math.sin(wingPhase * 8);
      ctx.fillStyle = `rgba(74, 107, 140, ${wingAlpha})`;

      // Left wing
      ctx.beginPath();
      ctx.ellipse(cx - radius * 0.8, cy - radius * 0.2, radius * 0.7, radius * 0.4, -0.3, 0, Math.PI * 2);
      ctx.fill();

      // Right wing
      ctx.beginPath();
      ctx.ellipse(cx + radius * 0.8, cy - radius * 0.2, radius * 0.7, radius * 0.4, 0.3, 0, Math.PI * 2);
      ctx.fill();

      // Main body
      ctx.fillStyle = HORNET_COLORS.body;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fill();

      // Stripes
      ctx.fillStyle = HORNET_COLORS.stripe;
      for (let i = 0; i < 3; i++) {
        const stripeY = cy + (i - 1) * radius * 0.4;
        ctx.beginPath();
        ctx.ellipse(cx, stripeY, radius * 0.9, radius * 0.12, 0, 0, Math.PI * 2);
        ctx.fill();
      }

      // Shadow (underside)
      ctx.fillStyle = HORNET_COLORS.shadow;
      ctx.beginPath();
      ctx.ellipse(cx, cy + radius * 0.3, radius * 0.6, radius * 0.25, 0, 0, Math.PI * 2);
      ctx.fill();

      // Highlight (top)
      ctx.fillStyle = HORNET_COLORS.highlight;
      ctx.beginPath();
      ctx.ellipse(cx, cy - radius * 0.4, radius * 0.5, radius * 0.2, 0, 0, Math.PI * 2);
      ctx.fill();

      // Mandibles (slightly open, menacing)
      ctx.fillStyle = HORNET_COLORS.stripe;
      ctx.beginPath();
      ctx.moveTo(cx - radius * 0.3, cy + radius * 0.8);
      ctx.lineTo(cx - radius * 0.15, cy + radius * 1.3);
      ctx.lineTo(cx - radius * 0.05, cy + radius * 0.85);
      ctx.closePath();
      ctx.fill();

      ctx.beginPath();
      ctx.moveTo(cx + radius * 0.3, cy + radius * 0.8);
      ctx.lineTo(cx + radius * 0.15, cy + radius * 1.3);
      ctx.lineTo(cx + radius * 0.05, cy + radius * 0.85);
      ctx.closePath();
      ctx.fill();

      // Eyes (predator eyes - large, kidney-shaped)
      ctx.fillStyle = HORNET_COLORS.eyes;
      // Left eye
      ctx.beginPath();
      ctx.ellipse(cx - radius * 0.35, cy - radius * 0.15, radius * 0.25, radius * 0.35, -0.2, 0, Math.PI * 2);
      ctx.fill();
      // Right eye
      ctx.beginPath();
      ctx.ellipse(cx + radius * 0.35, cy - radius * 0.15, radius * 0.25, radius * 0.35, 0.2, 0, Math.PI * 2);
      ctx.fill();

      // Eye gleam
      ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
      ctx.beginPath();
      ctx.arc(cx - radius * 0.4, cy - radius * 0.25, radius * 0.08, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(cx + radius * 0.3, cy - radius * 0.25, radius * 0.08, 0, Math.PI * 2);
      ctx.fill();

      animFrame = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(animFrame);
  }, [size]);

  return (
    <canvas
      ref={canvasRef}
      width={size}
      height={size}
      style={{ width: size, height: size }}
    />
  );
}

function LoreModal({ onDismiss }: { onDismiss: () => void }) {
  const [stage, setStage] = useState(0);

  // Progress through stages on click or key press, ESC to skip
  useEffect(() => {
    const handleAdvance = (e: KeyboardEvent | MouseEvent) => {
      if (e instanceof KeyboardEvent) {
        if (e.key === 'Escape') {
          e.preventDefault();
          sessionStorage.setItem(LORE_STORAGE_KEY, 'true');
          onDismiss();
          return;
        }
        if (e.key !== ' ' && e.key !== 'Enter') return;
      }
      e.preventDefault();
      if (stage < 2) {
        setStage(s => s + 1);
      } else {
        sessionStorage.setItem(LORE_STORAGE_KEY, 'true');
        onDismiss();
      }
    };
    window.addEventListener('keydown', handleAdvance);
    window.addEventListener('click', handleAdvance);
    return () => {
      window.removeEventListener('keydown', handleAdvance);
      window.removeEventListener('click', handleAdvance);
    };
  }, [stage, onDismiss]);

  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center p-8 z-50">
      <div className="max-w-xl text-center">
        {/* Stage 0: You Are Death */}
        {stage === 0 && (
          <div className="animate-fade-in">
            <div className="flex justify-center mb-6">
              <HornetSprite size={140} />
            </div>
            <p className="text-amber-500 text-3xl font-bold mb-3">You are the Giant Hornet.</p>
            <p className="text-gray-400 text-lg">
              <span className="text-red-500">40 kills per minute.</span> Mandibles that decapitate.
            </p>
            <p className="text-white mt-2">The apex predator.</p>
          </div>
        )}

        {/* Stage 1: But... */}
        {stage === 1 && (
          <div className="animate-fade-in">
            <p className="text-gray-500 text-lg mb-4">
              But these bees evolved <span className="text-amber-400">a countermeasure</span>.
            </p>
            <p className="text-white text-xl">
              They will surround you. Cook you alive.
            </p>
            <p className="text-red-400 text-2xl font-bold mt-4">
              THE BALL.
            </p>
          </div>
        )}

        {/* Stage 2: Hunt */}
        {stage === 2 && (
          <div className="animate-fade-in">
            <p className="text-gray-600 text-sm uppercase tracking-widest mb-2">The hive awaits</p>
            <p className="text-3xl font-bold" style={{ color: COLORS.player }}>
              Hunt or be hunted.
            </p>
          </div>
        )}

        {/* Continue prompt */}
        <div className="mt-10 text-gray-600 text-xs animate-pulse">
          {stage < 2 ? 'SPACE to continue' : 'SPACE to begin'}
        </div>
      </div>
    </div>
  );
}

function MenuScreen({ onStart }: { onStart: () => void }) {
  // Check if lore has been seen this session
  const [showLore, setShowLore] = useState(() => {
    if (typeof window === 'undefined') return false;
    return sessionStorage.getItem(LORE_STORAGE_KEY) !== 'true';
  });

  // Add keyboard support for Space/Enter to start (only when lore is dismissed)
  useEffect(() => {
    if (showLore) return; // Don't handle start keys while lore is showing

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === ' ' || e.key === 'Enter') {
        e.preventDefault();
        onStart();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onStart, showLore]);

  // Show lore modal first
  if (showLore) {
    return <LoreModal onDismiss={() => setShowLore(false)} />;
  }

  return (
    <div className="text-center max-w-lg mx-auto">
      {/* Hornet title art */}
      <div className="mb-2 flex justify-center">
        <HornetIcon size={64} color={COLORS.player} />
      </div>
      <h1
        className="text-4xl font-bold mb-1"
        style={{ color: COLORS.player }}
      >
        Bee Survivors
      </h1>
      <p className="text-amber-500 text-sm mb-6 italic">
        You are the hornet. The hive fights back.
      </p>

      {/* Three instruction cards with icon illustrations */}
      <div className="space-y-4 mb-8 text-left">
        {/* Instruction 1: Movement */}
        <div className="bg-gray-800/50 rounded-lg p-4 flex items-center gap-4">
          <GamepadIcon size={32} color="#FFFFFF" />
          <div>
            <div className="text-white font-medium">Move with WASD</div>
            <div className="text-gray-400 text-sm">
              Dodge the swarm and hunt worker bees.
            </div>
          </div>
        </div>

        {/* Instruction 2: Apex Strike (the dash) */}
        <div className="bg-gray-800/50 rounded-lg p-4 flex items-center gap-4">
          <LightningIcon size={32} color="#FFD700" />
          <div>
            <div className="text-white font-medium">Hold SPACE to charge Apex Strike</div>
            <div className="text-gray-400 text-sm">
              <span className="text-amber-400">Phase 1:</span> Teleport in your aimed direction.{' '}
              <span className="text-orange-400">Phase 2:</span> Speed boost—change direction mid-dash!
            </div>
          </div>
        </div>

        {/* Instruction 3: Kill to level up */}
        <div className="bg-gray-800/50 rounded-lg p-4 flex items-center gap-4">
          <ArrowUpIcon size={32} color="#00FF88" />
          <div>
            <div className="text-white font-medium">Kill bees to level up</div>
            <div className="text-gray-400 text-sm">
              Choose upgrades that shape your playstyle. Watch for THE BALL formation!
            </div>
          </div>
        </div>
      </div>

      <button
        onClick={onStart}
        className="px-8 py-4 rounded-lg text-xl font-bold transition-transform hover:scale-105 flex items-center gap-2 mx-auto"
        style={{ backgroundColor: COLORS.player, color: '#000' }}
      >
        <HornetIcon size={24} color="#000" />
        Start Hunting
      </button>

      <div className="mt-6 text-gray-500 text-xs">
        <p>Press SPACE or ENTER to start</p>
      </div>
    </div>
  );
}

function GameOverScreen({
  gameState,
  onPlayAgain,
  onViewCrystal,
}: {
  gameState: GameState;
  onPlayAgain: () => void;
  onViewCrystal: () => void;
}) {
  return (
    <div className="text-center">
      <div className="mb-4 flex justify-center">
        <SkullIcon size={64} color={COLORS.crisis} />
      </div>
      <h1 className="text-3xl font-bold mb-2" style={{ color: COLORS.crisis }}>
        The Hive Won
      </h1>

      <div className="grid grid-cols-3 gap-8 my-8">
        <div>
          <div className="text-3xl font-bold" style={{ color: COLORS.player }}>
            {gameState.wave}
          </div>
          <div className="text-gray-500 text-sm">Waves Survived</div>
        </div>
        <div>
          <div className="text-3xl font-bold" style={{ color: COLORS.xp }}>
            {gameState.score}
          </div>
          <div className="text-gray-500 text-sm">Score</div>
        </div>
        <div>
          <div className="text-3xl font-bold" style={{ color: COLORS.health }}>
            {gameState.totalEnemiesKilled}
          </div>
          <div className="text-gray-500 text-sm">Bees Killed</div>
        </div>
      </div>

      <div className="flex gap-4 justify-center">
        <button
          onClick={onViewCrystal}
          className="px-6 py-3 rounded-lg font-medium transition-colors"
          style={{ backgroundColor: COLORS.xp, color: '#000' }}
        >
          View Crystal
        </button>
        <button
          onClick={onPlayAgain}
          className="px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2"
          style={{ backgroundColor: COLORS.player, color: '#000' }}
        >
          <HornetIcon size={20} color="#000" />
          Hunt Again
        </button>
      </div>

      <p className="mt-6 text-gray-500 text-sm">
        Your hunt has been crystallized. View it to see your journey.
      </p>
    </div>
  );
}

export default WASMSurvivors;
