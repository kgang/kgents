/**
 * TokenBalanceWidget - Animated token balance display
 *
 * Shows current token balance with animated counting on changes.
 * Flash green on earn, red on spend. Particles flow using LIVING_EARTH.honey.
 *
 * Features:
 * - Animated counter (counts up/down to new value)
 * - Direction-aware flash (green=earn, red=spend)
 * - Particle burst on significant changes
 * - Compact and full display modes
 *
 * @see plans/crown-jewels-genesis-phase2-chunks3-5.md - Chunk 3: Token Economy Visualization
 * @see docs/skills/crown-jewel-patterns.md - Pattern 3: Optimistic Updates
 */

import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { Zap, TrendingUp, TrendingDown } from 'lucide-react';
import { LIVING_EARTH } from '@/constants/colors';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

export interface TokenBalanceWidgetProps {
  /** Current token balance */
  balance: number;
  /** Recent change (for animation direction) */
  recentChange?: {
    amount: number;
    direction: 'in' | 'out';
  };
  /** Display mode */
  variant?: 'compact' | 'full';
  /** Whether to show the "tokens" label */
  showLabel?: boolean;
  /** Whether SSE is connected */
  isConnected?: boolean;
  /** Optional class name */
  className?: string;
  /** Click handler (e.g., to open spend history) */
  onClick?: () => void;
}

interface Particle {
  id: string;
  x: number;
  y: number;
  dx: number;
  dy: number;
  life: number;
  color: string;
}

// =============================================================================
// Constants
// =============================================================================

const ANIMATION_DURATION = 600; // ms for count animation
const FLASH_DURATION = 400; // ms for color flash
const PARTICLE_COUNT = 8;
const PARTICLE_LIFETIME = 800; // ms

// =============================================================================
// Component
// =============================================================================

export function TokenBalanceWidget({
  balance,
  recentChange,
  variant = 'compact',
  showLabel = true,
  isConnected = true,
  className,
  onClick,
}: TokenBalanceWidgetProps) {
  // Animated display value
  const [displayValue, setDisplayValue] = useState(balance);
  const [flashState, setFlashState] = useState<'none' | 'earn' | 'spend'>('none');
  const [particles, setParticles] = useState<Particle[]>([]);

  // Refs for animation
  const prevBalanceRef = useRef(balance);
  const animationFrameRef = useRef<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Animate count to new value
  const animateCount = useCallback((from: number, to: number, startTime: number) => {
    const animate = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / ANIMATION_DURATION, 1);

      // Easing: ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(from + (to - from) * eased);

      setDisplayValue(current);

      if (progress < 1) {
        animationFrameRef.current = requestAnimationFrame((t) => animate(t));
      }
    };

    animationFrameRef.current = requestAnimationFrame((t) => animate(t));
  }, []);

  // Spawn particles on change
  const spawnParticles = useCallback((direction: 'in' | 'out') => {
    const newParticles: Particle[] = [];
    const color = direction === 'in' ? LIVING_EARTH.sage : LIVING_EARTH.copper;

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const angle = (Math.PI * 2 * i) / PARTICLE_COUNT + Math.random() * 0.5;
      const speed = 2 + Math.random() * 2;

      newParticles.push({
        id: `particle-${Date.now()}-${i}`,
        x: 50, // Center
        y: 50,
        dx: Math.cos(angle) * speed,
        dy: Math.sin(angle) * speed,
        life: 1,
        color,
      });
    }

    setParticles(newParticles);
  }, []);

  // Animate particles
  useEffect(() => {
    if (particles.length === 0) return;

    const startTime = performance.now();

    const animate = (now: number) => {
      const elapsed = now - startTime;
      const progress = elapsed / PARTICLE_LIFETIME;

      if (progress >= 1) {
        setParticles([]);
        return;
      }

      setParticles((prev) =>
        prev.map((p) => ({
          ...p,
          x: p.x + p.dx,
          y: p.y + p.dy,
          dy: p.dy + 0.1, // Gravity
          life: 1 - progress,
        }))
      );

      requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  }, [particles.length > 0]); // Only re-run when particles appear

  // Handle balance changes
  useEffect(() => {
    const prevBalance = prevBalanceRef.current;

    if (prevBalance !== balance) {
      // Cancel any existing animation
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }

      // Determine direction
      const direction = balance > prevBalance ? 'in' : 'out';

      // Flash color
      setFlashState(direction === 'in' ? 'earn' : 'spend');
      setTimeout(() => setFlashState('none'), FLASH_DURATION);

      // Spawn particles for significant changes (>= 5 tokens)
      if (Math.abs(balance - prevBalance) >= 5) {
        spawnParticles(direction);
      }

      // Animate the count
      animateCount(prevBalance, balance, performance.now());

      prevBalanceRef.current = balance;
    }
  }, [balance, animateCount, spawnParticles]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  // Flash color styles
  const flashStyles = useMemo(() => {
    switch (flashState) {
      case 'earn':
        return {
          backgroundColor: `${LIVING_EARTH.mint}30`,
          borderColor: LIVING_EARTH.sage,
        };
      case 'spend':
        return {
          backgroundColor: `${LIVING_EARTH.copper}30`,
          borderColor: LIVING_EARTH.copper,
        };
      default:
        return {};
    }
  }, [flashState]);

  // Recent change indicator
  const changeIndicator = recentChange && (
    <div
      className={cn(
        'flex items-center gap-0.5 text-xs font-medium animate-fade-in',
        recentChange.direction === 'in' ? 'text-green-600' : 'text-red-500'
      )}
    >
      {recentChange.direction === 'in' ? (
        <TrendingUp className="w-3 h-3" />
      ) : (
        <TrendingDown className="w-3 h-3" />
      )}
      <span>{recentChange.direction === 'in' ? '+' : '-'}{recentChange.amount}</span>
    </div>
  );

  if (variant === 'compact') {
    return (
      <button
        ref={containerRef}
        onClick={onClick}
        className={cn(
          'relative flex items-center gap-1.5 px-3 py-1.5 rounded-full',
          'border transition-all duration-200',
          'bg-amber-50 border-amber-200 hover:bg-amber-100',
          onClick && 'cursor-pointer',
          className
        )}
        style={flashStyles}
      >
        {/* Connection indicator */}
        {!isConnected && (
          <span
            className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-amber-400"
            title="Reconnecting..."
          />
        )}

        {/* Icon */}
        <Zap
          className="w-4 h-4"
          style={{ color: LIVING_EARTH.amber }}
        />

        {/* Value */}
        <span className="font-semibold text-stone-800 tabular-nums">
          {displayValue}
        </span>

        {/* Particles */}
        {particles.length > 0 && (
          <svg
            className="absolute inset-0 pointer-events-none overflow-visible"
            style={{ width: '100%', height: '100%' }}
          >
            {particles.map((p) => (
              <circle
                key={p.id}
                cx={`${p.x}%`}
                cy={`${p.y}%`}
                r={3 * p.life}
                fill={p.color}
                opacity={p.life * 0.8}
              />
            ))}
          </svg>
        )}
      </button>
    );
  }

  // Full variant
  return (
    <div
      ref={containerRef}
      onClick={onClick}
      className={cn(
        'relative p-4 rounded-lg border transition-all duration-200',
        'bg-white border-stone-200',
        onClick && 'cursor-pointer hover:border-amber-300',
        className
      )}
      style={flashStyles}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div
            className="p-2 rounded-lg"
            style={{ backgroundColor: `${LIVING_EARTH.honey}30` }}
          >
            <Zap
              className="w-5 h-5"
              style={{ color: LIVING_EARTH.amber }}
            />
          </div>
          {showLabel && (
            <span className="text-sm font-medium text-stone-600">Token Balance</span>
          )}
        </div>

        {/* Connection status */}
        <div className="flex items-center gap-1">
          <span
            className={cn(
              'w-2 h-2 rounded-full',
              isConnected ? 'bg-green-400' : 'bg-amber-400 animate-pulse'
            )}
          />
          <span className="text-xs text-stone-400">
            {isConnected ? 'Live' : 'Syncing...'}
          </span>
        </div>
      </div>

      {/* Balance */}
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold text-stone-900 tabular-nums">
          {displayValue}
        </span>
        {showLabel && (
          <span className="text-sm text-stone-400">tokens</span>
        )}
      </div>

      {/* Recent change */}
      {changeIndicator && (
        <div className="mt-2">
          {changeIndicator}
        </div>
      )}

      {/* Particles overlay */}
      {particles.length > 0 && (
        <svg
          className="absolute inset-0 pointer-events-none overflow-visible"
          style={{ width: '100%', height: '100%' }}
        >
          {particles.map((p) => (
            <circle
              key={p.id}
              cx={`${p.x}%`}
              cy={`${p.y}%`}
              r={4 * p.life}
              fill={p.color}
              opacity={p.life * 0.8}
            />
          ))}
        </svg>
      )}
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default TokenBalanceWidget;
