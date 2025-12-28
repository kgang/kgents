/**
 * WASM Survivors - Death Crystallization Overlay
 *
 * DD-29-3: When the player dies, the final frame crystallizes.
 *
 * Effect Sequence:
 * 1. Time slows (handled by game loop)
 * 2. Screen develops fracture lines radiating from death position
 * 3. Colors shift to monochrome with golden accents
 * 4. "Your run crystallized" text appears
 * 5. Pulses gently until dismissed
 *
 * @see pilots/wasm-survivors-game/runs/run-029/coordination/.outline.md
 */

import { useEffect, useState, useMemo } from 'react';
import { COLORS } from '../systems/juice';

interface CrystallizationOverlayProps {
  deathPosition: { x: number; y: number };
  arenaWidth: number;
  arenaHeight: number;
  onComplete: () => void;
  durationMs?: number;
}

interface FractureLine {
  angle: number;
  length: number;
  thickness: number;
  delay: number;
}

/**
 * Generates fracture lines radiating from a point
 */
function generateFractureLines(count: number): FractureLine[] {
  const lines: FractureLine[] = [];
  const baseAngle = Math.random() * Math.PI * 2;

  for (let i = 0; i < count; i++) {
    // Distribute angles around the circle with some randomness
    const angle = baseAngle + (i / count) * Math.PI * 2 + (Math.random() - 0.5) * 0.3;

    lines.push({
      angle,
      length: 0.3 + Math.random() * 0.7, // 30-100% of max distance
      thickness: 1 + Math.random() * 2,
      delay: Math.random() * 200, // Staggered appearance
    });
  }

  return lines;
}

export function CrystallizationOverlay({
  deathPosition,
  arenaWidth,
  arenaHeight,
  onComplete,
  durationMs = 2000,
}: CrystallizationOverlayProps) {
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState<'fracturing' | 'crystallizing' | 'complete'>('fracturing');

  // Generate fracture lines once
  const fractureLines = useMemo(() => generateFractureLines(12), []);

  // Animation progress
  useEffect(() => {
    const startTime = Date.now();
    let animationFrame: number;

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const newProgress = Math.min(1, elapsed / durationMs);
      setProgress(newProgress);

      // Phase transitions
      if (newProgress < 0.3) {
        setPhase('fracturing');
      } else if (newProgress < 0.8) {
        setPhase('crystallizing');
      } else {
        setPhase('complete');
      }

      if (newProgress < 1) {
        animationFrame = requestAnimationFrame(animate);
      } else {
        onComplete();
      }
    };

    animationFrame = requestAnimationFrame(animate);

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [durationMs, onComplete]);

  // Calculate normalized death position (0-1)
  const deathX = deathPosition.x / arenaWidth;
  const deathY = deathPosition.y / arenaHeight;

  // Fracture progress (0-1 during fracturing phase)
  const fractureProgress = phase === 'fracturing' ? progress / 0.3 : 1;

  // Crystal pulse (subtle breathing after complete)
  const crystalPulse = phase === 'complete' ? 0.9 + 0.1 * Math.sin(Date.now() / 200) : 1;

  // Monochrome/golden shift intensity
  const monochromeIntensity = phase === 'fracturing' ? 0 : Math.min(1, (progress - 0.3) / 0.5);

  return (
    <div
      className="absolute inset-0 pointer-events-none overflow-hidden"
      style={{
        // Apply monochrome + golden filter
        filter: `saturate(${1 - monochromeIntensity * 0.8}) sepia(${monochromeIntensity * 0.3})`,
        transition: 'filter 0.3s ease-out',
      }}
    >
      {/* Fracture lines SVG overlay */}
      <svg
        className="absolute inset-0 w-full h-full"
        viewBox={`0 0 ${arenaWidth} ${arenaHeight}`}
        preserveAspectRatio="none"
      >
        <defs>
          {/* Golden gradient for fractures */}
          <linearGradient id="fracture-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={COLORS.xp} stopOpacity="0.8" />
            <stop offset="50%" stopColor="#FFFFFF" stopOpacity="1" />
            <stop offset="100%" stopColor={COLORS.xp} stopOpacity="0.4" />
          </linearGradient>

          {/* Glow filter */}
          <filter id="fracture-glow">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Fracture lines */}
        {fractureLines.map((line, i) => {
          // Calculate line endpoint
          const maxLength = Math.sqrt(arenaWidth * arenaWidth + arenaHeight * arenaHeight);
          const lineLength = maxLength * line.length * fractureProgress;

          const startX = deathPosition.x;
          const startY = deathPosition.y;
          const endX = startX + Math.cos(line.angle) * lineLength;
          const endY = startY + Math.sin(line.angle) * lineLength;

          // Staggered appearance
          const lineProgress = Math.max(0, (fractureProgress * 300 - line.delay) / (300 - line.delay));
          const lineOpacity = lineProgress * crystalPulse;

          return (
            <line
              key={i}
              x1={startX}
              y1={startY}
              x2={startX + (endX - startX) * lineProgress}
              y2={startY + (endY - startY) * lineProgress}
              stroke="url(#fracture-gradient)"
              strokeWidth={line.thickness}
              opacity={lineOpacity}
              filter="url(#fracture-glow)"
              strokeLinecap="round"
            />
          );
        })}

        {/* Central crystal burst at death point */}
        {phase !== 'fracturing' && (
          <g opacity={monochromeIntensity * crystalPulse}>
            {/* Inner glow */}
            <circle
              cx={deathPosition.x}
              cy={deathPosition.y}
              r={20 + monochromeIntensity * 10}
              fill="none"
              stroke={COLORS.xp}
              strokeWidth="3"
              filter="url(#fracture-glow)"
            />
            {/* Outer ring */}
            <circle
              cx={deathPosition.x}
              cy={deathPosition.y}
              r={40 + monochromeIntensity * 20}
              fill="none"
              stroke={COLORS.xp}
              strokeWidth="1"
              opacity="0.5"
            />
          </g>
        )}
      </svg>

      {/* "Your run crystallized" text */}
      {phase === 'complete' && (
        <div
          className="absolute inset-0 flex items-center justify-center"
          style={{
            opacity: crystalPulse,
            transform: `scale(${0.95 + crystalPulse * 0.05})`,
          }}
        >
          <div className="text-center">
            <h2
              className="text-3xl font-bold mb-2"
              style={{ color: COLORS.xp, textShadow: `0 0 20px ${COLORS.xp}` }}
            >
              Your run crystallized
            </h2>
            <p className="text-gray-400 text-sm">
              Every decision witnessed. Every moment preserved.
            </p>
          </div>
        </div>
      )}

      {/* Vignette overlay during crystallization */}
      <div
        className="absolute inset-0"
        style={{
          background: `radial-gradient(circle at ${deathX * 100}% ${deathY * 100}%, transparent 0%, transparent 30%, rgba(0,0,0,${monochromeIntensity * 0.3}) 100%)`,
          pointerEvents: 'none',
        }}
      />
    </div>
  );
}

export default CrystallizationOverlay;
