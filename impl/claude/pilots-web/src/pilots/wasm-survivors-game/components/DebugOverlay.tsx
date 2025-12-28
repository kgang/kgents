/**
 * WASM Survivors - Debug Overlay Component
 *
 * Visual overlay that displays game state when ?debug=true is in the URL.
 * Provides real-time debugging information for development and testing.
 *
 * Features:
 * - Game State Panel (wave, enemies, player health, FPS)
 * - Enemy State Labels (CHASE, TELEGRAPH, ATTACK, RECOVERY)
 * - Telegraph Indicators (progress bars, radius circles, direction lines)
 * - Last Damage Indicator (floating text with fade-out)
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 */

import { useEffect, useState, useRef } from 'react';
import type {
  DebugGameState,
  DebugEnemy,
  DebugTelegraph,
  DebugDamageEvent,
} from '../../../lib/debug-types';

// =============================================================================
// Types
// =============================================================================

interface EnemyCount {
  total: number;
  basic: number;
  fast: number;
  tank: number;
  boss: number;
  spitter: number;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get color for enemy behavior state
 */
function getStateColor(state: string): string {
  switch (state) {
    case 'chase':
      return '#22c55e'; // green-500
    case 'telegraph':
      return '#eab308'; // yellow-500
    case 'attack':
      return '#ef4444'; // red-500
    case 'recovery':
      return '#3b82f6'; // blue-500
    default:
      return '#9ca3af'; // gray-400
  }
}

/**
 * Count enemies by type
 */
function countEnemies(enemies: DebugEnemy[]): EnemyCount {
  const counts: EnemyCount = {
    total: enemies.length,
    basic: 0,
    fast: 0,
    tank: 0,
    boss: 0,
    spitter: 0,
  };

  for (const enemy of enemies) {
    const type = enemy.type as keyof Omit<EnemyCount, 'total'>;
    if (type in counts) {
      counts[type]++;
    }
  }

  return counts;
}

// =============================================================================
// Sub-Components
// =============================================================================

/**
 * Game State Panel - Top-left corner info display
 */
function GameStatePanel({
  gameState,
  fps,
}: {
  gameState: DebugGameState;
  fps: number;
}) {
  const counts = countEnemies(gameState.enemies);

  return (
    <div className="absolute top-4 left-4 bg-black/70 text-white p-3 rounded font-mono text-sm select-none">
      <div className="text-yellow-400 font-bold mb-2 border-b border-gray-600 pb-1">
        DEBUG OVERLAY
      </div>
      <div className="space-y-1">
        <div>
          Wave: <span className="text-cyan-400">{gameState.wave}</span>
        </div>
        <div>
          Score: <span className="text-yellow-300">{gameState.score}</span>
        </div>
        <div>
          Time:{' '}
          <span className="text-gray-300">
            {(gameState.gameTime / 1000).toFixed(1)}s
          </span>
        </div>
        <div className="border-t border-gray-600 pt-1 mt-1">
          Enemies: <span className="text-red-400">{counts.total}</span>
          {counts.total > 0 && (
            <div className="ml-2 text-xs text-gray-400">
              {counts.basic > 0 && <span className="mr-2">B:{counts.basic}</span>}
              {counts.fast > 0 && <span className="mr-2">F:{counts.fast}</span>}
              {counts.tank > 0 && <span className="mr-2">T:{counts.tank}</span>}
              {counts.spitter > 0 && (
                <span className="mr-2">S:{counts.spitter}</span>
              )}
              {counts.boss > 0 && <span className="text-red-500">BOSS:{counts.boss}</span>}
            </div>
          )}
        </div>
        <div className="border-t border-gray-600 pt-1 mt-1">
          Health:{' '}
          <span
            className={
              gameState.player.health <= gameState.player.maxHealth * 0.3
                ? 'text-red-400'
                : 'text-green-400'
            }
          >
            {gameState.player.health}/{gameState.player.maxHealth}
          </span>
        </div>
        <div>
          FPS:{' '}
          <span
            className={fps < 30 ? 'text-red-400' : fps < 55 ? 'text-yellow-400' : 'text-green-400'}
          >
            {fps}
          </span>
        </div>
        {gameState.player.invincible && (
          <div className="mt-2 text-yellow-400 font-bold text-lg animate-pulse border-2 border-yellow-400 rounded px-2 py-1 text-center">
            INVINCIBLE
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Enemy Labels - Floating labels above each enemy showing behavior state
 */
function EnemyLabels({ enemies }: { enemies: DebugEnemy[] }) {
  return (
    <>
      {enemies.map((enemy) => (
        <div
          key={enemy.id}
          className="absolute text-xs font-bold pointer-events-none select-none"
          style={{
            left: enemy.position.x,
            top: enemy.position.y - 30,
            transform: 'translateX(-50%)',
            color: getStateColor(enemy.behaviorState),
            textShadow: '0 0 4px rgba(0,0,0,0.8), 0 0 8px rgba(0,0,0,0.6)',
          }}
        >
          {enemy.behaviorState.toUpperCase()}
          {enemy.telegraphProgress !== undefined && (
            <div className="text-center text-[10px] opacity-80">
              {Math.round(enemy.telegraphProgress * 100)}%
            </div>
          )}
        </div>
      ))}
    </>
  );
}

/**
 * Telegraph Indicators - Progress bars and visual indicators for telegraphs
 */
function TelegraphIndicators({ telegraphs }: { telegraphs: DebugTelegraph[] }) {
  return (
    <>
      {telegraphs.map((tel) => (
        <div key={tel.enemyId} className="absolute pointer-events-none">
          {/* Progress bar */}
          <div
            className="absolute"
            style={{
              left: tel.position.x,
              top: tel.position.y - 45,
              transform: 'translateX(-50%)',
            }}
          >
            <div className="w-16 h-1.5 bg-gray-700 rounded overflow-hidden">
              <div
                className="h-full rounded transition-all duration-75"
                style={{
                  width: `${tel.progress * 100}%`,
                  backgroundColor:
                    tel.type === 'stomp'
                      ? '#ef4444'
                      : tel.type === 'charge'
                        ? '#f97316'
                        : tel.type === 'projectile'
                          ? '#a855f7'
                          : '#eab308',
                }}
              />
            </div>
            <div className="text-[8px] text-gray-400 text-center mt-0.5 select-none">
              {tel.type.toUpperCase()}
            </div>
          </div>

          {/* Radius circle for stomp attacks */}
          {tel.type === 'stomp' && tel.radius && (
            <div
              className="absolute rounded-full border-2 border-dashed pointer-events-none"
              style={{
                left: tel.position.x,
                top: tel.position.y,
                width: tel.radius * 2,
                height: tel.radius * 2,
                transform: 'translate(-50%, -50%)',
                borderColor: `rgba(239, 68, 68, ${0.3 + tel.progress * 0.7})`,
                backgroundColor: `rgba(239, 68, 68, ${tel.progress * 0.2})`,
              }}
            />
          )}

          {/* Direction line for charge attacks */}
          {tel.type === 'charge' && tel.direction && (
            <svg
              className="absolute pointer-events-none"
              style={{
                left: 0,
                top: 0,
                width: '100%',
                height: '100%',
                overflow: 'visible',
              }}
            >
              <line
                x1={tel.position.x}
                y1={tel.position.y}
                x2={tel.position.x + tel.direction.x * 150}
                y2={tel.position.y + tel.direction.y * 150}
                stroke={`rgba(249, 115, 22, ${0.4 + tel.progress * 0.6})`}
                strokeWidth={3}
                strokeDasharray="8,4"
              />
              {/* Arrow head */}
              <polygon
                points={getArrowPoints(
                  tel.position.x + tel.direction.x * 150,
                  tel.position.y + tel.direction.y * 150,
                  tel.direction
                )}
                fill={`rgba(249, 115, 22, ${0.4 + tel.progress * 0.6})`}
              />
            </svg>
          )}

          {/* Direction line for projectile (aim) attacks */}
          {tel.type === 'projectile' && tel.direction && (
            <svg
              className="absolute pointer-events-none"
              style={{
                left: 0,
                top: 0,
                width: '100%',
                height: '100%',
                overflow: 'visible',
              }}
            >
              <line
                x1={tel.position.x}
                y1={tel.position.y}
                x2={tel.position.x + tel.direction.x * 100}
                y2={tel.position.y + tel.direction.y * 100}
                stroke={`rgba(168, 85, 247, ${0.4 + tel.progress * 0.6})`}
                strokeWidth={2}
                strokeDasharray="4,4"
              />
            </svg>
          )}
        </div>
      ))}
    </>
  );
}

/**
 * Calculate arrow head points for direction lines
 */
function getArrowPoints(x: number, y: number, dir: { x: number; y: number }): string {
  const size = 8;
  const angle = Math.atan2(dir.y, dir.x);
  const p1x = x;
  const p1y = y;
  const p2x = x - size * Math.cos(angle - Math.PI / 6);
  const p2y = y - size * Math.sin(angle - Math.PI / 6);
  const p3x = x - size * Math.cos(angle + Math.PI / 6);
  const p3y = y - size * Math.sin(angle + Math.PI / 6);
  return `${p1x},${p1y} ${p2x},${p2y} ${p3x},${p3y}`;
}

/**
 * Damage Indicator - Floating text showing last damage taken
 */
function DamageIndicator({ damage }: { damage: DebugDamageEvent }) {
  const [visible, setVisible] = useState(true);
  const [opacity, setOpacity] = useState(1);

  useEffect(() => {
    // Start fade after 1 second
    const fadeTimer = setTimeout(() => {
      setOpacity(0);
    }, 1000);

    // Hide completely after 2 seconds
    const hideTimer = setTimeout(() => {
      setVisible(false);
    }, 2000);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(hideTimer);
    };
  }, [damage.timestamp]);

  if (!visible) return null;

  return (
    <div
      className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 text-red-500 font-bold text-xl pointer-events-none select-none"
      style={{
        opacity,
        transition: 'opacity 1s ease-out',
        textShadow: '0 0 8px rgba(0,0,0,0.8), 0 2px 4px rgba(0,0,0,0.6)',
      }}
    >
      <div className="text-center">
        <span className="text-red-400">{damage.enemyType.toUpperCase()}</span>
        <span className="text-gray-300 mx-2">{damage.attackType}</span>
        <span className="text-red-600">-{damage.damage} HP</span>
      </div>
    </div>
  );
}

/**
 * Debug Controls Help - Bottom-left corner shortcuts reference
 */
function DebugControlsHelp() {
  return (
    <div className="absolute bottom-4 left-4 bg-black/70 text-white p-2 rounded font-mono text-xs select-none">
      <div className="text-yellow-400 mb-1 font-bold">Debug Controls:</div>
      <div className="space-y-0.5 text-gray-300">
        <div>
          <span className="text-cyan-400 w-8 inline-block">1-5</span> Spawn enemies
        </div>
        <div>
          <span className="text-cyan-400 w-8 inline-block">I</span> Toggle invincible
        </div>
        <div>
          <span className="text-cyan-400 w-8 inline-block">N</span> Next wave
        </div>
        <div>
          <span className="text-cyan-400 w-8 inline-block">K</span> Kill all
        </div>
        <div>
          <span className="text-cyan-400 w-8 inline-block">L</span> Level up
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * Debug Overlay - Main overlay component
 *
 * Polls game state every 100ms and displays real-time debug information.
 * Only active when ?debug=true is in the URL.
 */
export function DebugOverlay() {
  const [gameState, setGameState] = useState<DebugGameState | null>(null);
  const [fps, setFps] = useState(60);
  const [lastDamage, setLastDamage] = useState<DebugDamageEvent | null>(null);
  const lastDamageTimestampRef = useRef<number>(0);

  // Poll game state every 100ms
  useEffect(() => {
    const interval = setInterval(() => {
      const state = window.DEBUG_GET_GAME_STATE?.();
      if (state) {
        setGameState(state);

        // Check for new damage
        if (
          state.lastDamage &&
          state.lastDamage.timestamp !== lastDamageTimestampRef.current
        ) {
          lastDamageTimestampRef.current = state.lastDamage.timestamp;
          setLastDamage({ ...state.lastDamage });
        }
      }
    }, 100);

    return () => clearInterval(interval);
  }, []);

  // FPS counter
  useEffect(() => {
    let frames = 0;
    let lastTime = performance.now();
    let animationId: number;

    const countFrame = () => {
      frames++;
      const now = performance.now();
      if (now - lastTime >= 1000) {
        setFps(frames);
        frames = 0;
        lastTime = now;
      }
      animationId = requestAnimationFrame(countFrame);
    };

    animationId = requestAnimationFrame(countFrame);
    return () => cancelAnimationFrame(animationId);
  }, []);

  // Note: Keyboard shortcuts are handled by useDebugControls hook in index.tsx
  // This component is purely visual - no keyboard handling needed here

  if (!gameState) {
    return (
      <div className="fixed inset-0 pointer-events-none z-50">
        <div className="absolute top-4 left-4 bg-black/70 text-yellow-400 p-3 rounded font-mono text-sm">
          DEBUG MODE: Waiting for game state...
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {/* Game State Panel - top left */}
      <GameStatePanel gameState={gameState} fps={fps} />

      {/* Enemy Labels - positioned on canvas */}
      <EnemyLabels enemies={gameState.enemies} />

      {/* Telegraph Indicators */}
      <TelegraphIndicators telegraphs={gameState.telegraphs} />

      {/* Damage Indicator - center screen when damage taken */}
      {lastDamage && <DamageIndicator key={lastDamage.timestamp} damage={lastDamage} />}

      {/* Debug Controls Help - bottom left */}
      <DebugControlsHelp />
    </div>
  );
}

export default DebugOverlay;
