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
 * @see pilots/wasm-survivors-witnessed-run-lab/PROTO_SPEC.md
 * @see pilots/wasm-survivors-witnessed-run-lab/.outline.md
 */

import { useState, useCallback, useRef, useMemo, useEffect } from 'react';
import type { GameState, Ghost, GameCrystal } from '@kgents/shared-primitives';
import { useGameLoop } from './hooks/useGameLoop';
import { useInput } from './hooks/useInput';
import { useSoundEngine } from './hooks/useSoundEngine';
import { createInitialGameState } from './systems/physics';
import { startWave, resetSpawner } from './systems/spawn';
import { createJuiceSystem } from './systems/juice';
import { crystallize, type WitnessContext } from './systems/witness';
import { GameCanvas } from './components/GameCanvas';
import { UpgradeUI } from './components/UpgradeUI';
import { CrystalView } from './components/CrystalView';
import { DeathOverlay, type DeathInfo } from './components/DeathOverlay';
import { COLORS } from './systems/juice';
import { applyUpgrade as applyVerbUpgrade, type UpgradeType, createInitialActiveUpgrades, type ActiveUpgrades } from './systems/upgrades';

// =============================================================================
// Types
// =============================================================================

type GamePhase = 'menu' | 'playing' | 'upgrade' | 'gameover' | 'crystal';

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
  const inputRef = useInput();

  // Sound engine (DD-5)
  const soundEngine = useSoundEngine();

  // Game loop callbacks
  const handleStateUpdate = useCallback((state: GameState) => {
    setGameState(state);
  }, []);

  const handleGameOver = useCallback((finalState: GameState) => {
    setPhase('gameover');

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

    setDeathInfo({
      killerType: nearestEnemy?.type ?? 'basic',
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
    const trace = {
      runId: ctx.runId,
      startTime: ctx.startTime,
      endTime: Date.now(),
      marks: ctx.marks,
      finalContext: {
        wave: finalState.wave,
        health: finalState.player.health,
        maxHealth: finalState.player.maxHealth,
        upgrades: finalState.player.upgrades,
        synergies: finalState.player.synergies,
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

  // Sound callbacks (DD-5)
  const handleEnemyKilled = useCallback((enemyType: 'basic' | 'fast' | 'tank' | 'boss') => {
    soundEngine.playKill(enemyType);
  }, [soundEngine]);

  const handlePlayerDamaged = useCallback(() => {
    soundEngine.playDamage();
  }, [soundEngine]);

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
    },
    juiceSystem
  );

  // Start game
  const handleStartGame = useCallback(() => {
    // Reset everything
    resetSpawner();
    const freshState = createInitialGameState();
    const startedState = startWave({ ...freshState, status: 'playing', wave: 1 });

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
          synergies: gameState.player.synergies,
          xp: gameState.player.xp,
          enemiesKilled: gameState.totalEnemiesKilled,
        },
        projectedDrift: 0.1, // Simplified
      };
      witnessContextRef.current.ghosts.push(ghost);

      // Apply verb upgrade (DD-6)
      const { active: newActiveUpgrades, newSynergies } = applyVerbUpgrade(
        activeUpgradesRef.current,
        upgradeId as UpgradeType
      );
      activeUpgradesRef.current = newActiveUpgrades;

      // Update game state with verb upgrade effects
      const newState: GameState = {
        ...gameState,
        status: 'playing',
        player: {
          ...gameState.player,
          upgrades: [...gameState.player.upgrades, upgradeId],
          synergies: [...gameState.player.synergies, ...newSynergies.map(s => s.id)],
          // DD-6: Store active upgrade effects on player for physics system
          activeUpgrades: newActiveUpgrades,
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

  // View crystal
  const handleViewCrystal = useCallback(() => {
    setPhase('crystal');
  }, []);

  // Close crystal
  const handleCloseCrystal = useCallback(() => {
    setPhase('menu');
  }, []);

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
            />

            {phase === 'upgrade' && upgradeState && (
              <UpgradeUI
                level={upgradeState.level}
                choices={upgradeState.choices}
                currentUpgrades={gameState.player.upgrades}
                recentGhosts={witnessContextRef.current.ghosts.slice(-3)}
                onSelect={handleUpgradeSelect}
              />
            )}
          </div>
        )}

        {phase === 'gameover' && deathInfo && (
          <DeathOverlay
            death={deathInfo}
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
          WASD to move | Auto-attack nearest enemy | Level up to choose upgrades
        </div>
      </footer>
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
        <p className="mt-1 text-gray-600">WASD to move | Auto-attack enabled</p>
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
