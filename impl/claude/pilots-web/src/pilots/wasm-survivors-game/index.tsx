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
import { VoiceLineOverlay, ArcPhaseIndicator, ContrastIndicator } from './components/VoiceLineOverlay';
import { ARENA_WIDTH, ARENA_HEIGHT } from './systems/physics';
import { COLORS } from './systems/juice';
import { applyUpgrade as applyVerbUpgrade, type UpgradeType, createInitialActiveUpgrades, type ActiveUpgrades, getGhostSummary, ARCHETYPES } from './systems/upgrades';
import { generateAbilityChoices, type AbilityId } from './systems/abilities';
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

  // Active upgrades tracking (DD-6: verb-based upgrades)
  const activeUpgradesRef = useRef<ActiveUpgrades>(createInitialActiveUpgrades());

  // Juice system (persisted)
  const juiceSystem = useMemo(() => createJuiceSystem(), []);

  // Input handling
  // Note: clearFrameFlags and updateSpaceHoldDuration are available from useInput
  // but currently the game loop clears flags inline. Could be refactored.
  const { inputRef } = useInput();

  // Sound engine (DD-5)
  const soundEngine = useSoundEngine();

  // Debug controls (keyboard shortcuts for debug mode)
  useDebugControls();

  // Check if debug mode is enabled via URL parameter
  const isDebugMode = useMemo(() => {
    if (typeof window === 'undefined') return false;
    return new URLSearchParams(window.location.search).get('debug') === 'true';
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
      upgrades: finalState.player.upgrades as import('./systems/upgrades').UpgradeType[],
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
  }, [soundEngine, gameState.player.position]);

  const handlePlayerDamaged = useCallback(() => {
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
    },
    juiceSystem
  );

  // Start game
  const handleStartGame = useCallback(() => {
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

    // Reset active upgrades (DD-6)
    activeUpgradesRef.current = createInitialActiveUpgrades();

    setGameState(startedState);
    setPhase('playing');
    setCrystal(null);
    // Reset emotional state for new run
    setCurrentVoiceLine(null);
    setArcPhase('POWER');
    setEmotionalState(null);
    gameLoop.setState(startedState);  // Sync game loop state with started state
    gameLoop.start();
  }, [gameLoop]);

  // Handle upgrade selection (DD-6: verb-based upgrades)
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

      // Apply verb upgrade (DD-6) - pass unchosen upgrades for ghost tracking
      const unchosenUpgrades = alternatives as UpgradeType[];
      const { active: newActiveUpgrades, newSynergies } = applyVerbUpgrade(
        activeUpgradesRef.current,
        upgradeId as UpgradeType,
        unchosenUpgrades,
        gameState.gameTime,
        gameState.wave
      );
      activeUpgradesRef.current = newActiveUpgrades;

      // Update game state with verb upgrade effects
      const newState: GameState = {
        ...gameState,
        status: 'playing',
        player: {
          ...gameState.player,
          upgrades: [...gameState.player.upgrades, upgradeId],
          synergies: [...(gameState.player.synergies ?? []), ...newSynergies.map(s => s.id)],
          // DD-6: Store active upgrade effects on player for physics system
          activeUpgrades: newActiveUpgrades as unknown as Record<string, unknown>,
        },
      };

      // TODO: Play synergy sound if new synergy discovered (DD-7)
      if (newSynergies.length > 0) {
        console.log('SYNERGY DISCOVERED:', newSynergies.map(s => s.announcement).join(', '));
        // soundEngine.playSynergy(); // When sound is ready
      }

      setGameState(newState);
      setPhase('playing');
      setUpgradeState(null);
      gameLoop.setState(newState);  // Sync game loop state with upgraded state
      gameLoop.resume();
    },
    [gameState, gameLoop]
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
    const mockAbilities = {
      owned: ownedAbilities,
      levels: {} as Record<AbilityId, number>,
      computed: {} as any, // Not needed for choice generation
    };
    const choices = generateAbilityChoices(mockAbilities, 3);

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
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">*</span>
            <div>
              <h1
                className="text-lg font-bold"
                style={{ color: COLORS.player }}
              >
                WASM Survivors
              </h1>
              <p className="text-gray-500 text-xs">
                Witnessed Run Lab
              </p>
            </div>
          </div>

          {phase === 'playing' && (
            <div className="flex items-center gap-4 text-sm">
              <span className="text-gray-400">
                Wave {gameState.wave}
              </span>
              <span style={{ color: COLORS.xp }}>
                Score: {gameState.score}
              </span>
              {/* DD-7: Show dominant archetype in HUD */}
              {activeUpgradesRef.current.buildIdentity.dominantArchetype && (
                <span
                  className="px-2 py-0.5 rounded text-xs font-medium"
                  style={{
                    backgroundColor: `${ARCHETYPES[activeUpgradesRef.current.buildIdentity.dominantArchetype].color}33`,
                    color: ARCHETYPES[activeUpgradesRef.current.buildIdentity.dominantArchetype].color,
                  }}
                >
                  {ARCHETYPES[activeUpgradesRef.current.buildIdentity.dominantArchetype].name}
                </span>
              )}
            </div>
          )}
        </div>
      </header>

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
              meleeState={meleeState ?? undefined}
              apexState={gameLoop.getApexState()}
              chargePercent={Math.min(1, (inputRef.current?.spaceHoldDuration ?? 0) / 500)}
            />

            {/* Part VI: Voice line overlay */}
            <VoiceLineOverlay
              voiceLine={currentVoiceLine}
              arcPhase={arcPhase}
              onComplete={() => setCurrentVoiceLine(null)}
            />

            {/* Part VI: Arc phase indicator (appears after first phase change) */}
            {emotionalState && (
              <ArcPhaseIndicator
                phase={arcPhase}
                phasesVisited={emotionalState.arc.phasesVisited}
              />
            )}

            {/* Part VI: Contrast progress indicator */}
            {emotionalState && (
              <ContrastIndicator
                contrastsVisited={emotionalState.contrast.contrastsVisited}
              />
            )}

            {phase === 'upgrade' && upgradeState && (
              <UpgradeUI
                level={upgradeState.level}
                choices={upgradeState.choices}
                currentAbilities={gameState.player.upgrades as import('./systems/abilities').AbilityId[]}
                comboState={gameState.comboState}
                recentGhosts={witnessContextRef.current.ghosts.slice(-3)}
                onSelect={handleUpgradeSelect}
              />
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
              meleeState={meleeState ?? undefined}
              apexState={gameLoop.getApexState()}
              chargePercent={0}
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
            ghostSummary={getGhostSummary(activeUpgradesRef.current.buildIdentity)}
            onPlayAgain={handleStartGame}
            onViewCrystal={handleViewCrystal}
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

      {/* Footer */}
      <footer className="border-t border-gray-800 bg-gray-900/50">
        <div className="max-w-4xl mx-auto px-4 py-2 text-center text-gray-600 text-xs">
          WASD to move | Mandible Strike attacks nearest enemy | Level up to choose abilities
        </div>
      </footer>

      {/* Debug Overlay - only visible when ?debug=true */}
      {isDebugMode && <DebugOverlay />}
    </div>
  );
}

// =============================================================================
// Sub-screens
// =============================================================================

function MenuScreen({ onStart }: { onStart: () => void }) {
  // Add keyboard support for Space/Enter to start
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === ' ' || e.key === 'Enter') {
        e.preventDefault();
        onStart();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onStart]);

  return (
    <div className="text-center">
      <div className="text-6xl mb-4">*</div>
      <h1
        className="text-4xl font-bold mb-2"
        style={{ color: COLORS.player }}
      >
        WASM Survivors
      </h1>
      <p className="text-gray-400 mb-8 max-w-md mx-auto">
        Survive endless waves. Every decision is witnessed.
        Your run becomes a crystal - proof of your journey.
      </p>

      <button
        onClick={onStart}
        className="px-8 py-4 rounded-lg text-xl font-bold transition-transform hover:scale-105"
        style={{ backgroundColor: COLORS.player, color: '#000' }}
      >
        Start Run
      </button>

      <div className="mt-8 text-gray-500 text-sm">
        <p>Press SPACE or ENTER to start</p>
        <p className="mt-1 text-gray-600">WASD to move | Mandible Strike enabled</p>
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
      <div className="text-6xl mb-4" style={{ color: COLORS.crisis }}>
        X
      </div>
      <h1 className="text-3xl font-bold mb-2" style={{ color: COLORS.crisis }}>
        Run Ended
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
          <div className="text-gray-500 text-sm">Enemies Killed</div>
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
          className="px-6 py-3 rounded-lg font-medium transition-colors"
          style={{ backgroundColor: COLORS.player, color: '#000' }}
        >
          Play Again
        </button>
      </div>

      <p className="mt-6 text-gray-500 text-sm">
        Your run has been crystallized. View it to see your journey.
      </p>
    </div>
  );
}

export default WASMSurvivors;
