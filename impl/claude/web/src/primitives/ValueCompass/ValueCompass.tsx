/**
 * ValueCompass: Constitutional principle visualization
 *
 * Displays the 7 kgents principles as a radar chart with:
 * - Current scores (0-1 for each principle)
 * - Decision trajectory over time (optional)
 * - Personality attractor basin (optional)
 *
 * Pure CSS implementation - no D3 dependency.
 */

import { memo, useMemo } from 'react';
import type { ConstitutionScores, PersonalityAttractor } from '@/types/theory';
import { PRINCIPLES } from '@/types/theory';
import './ValueCompass.css';

export interface ValueCompassProps {
  scores: ConstitutionScores;
  trajectory?: ConstitutionScores[];
  attractor?: PersonalityAttractor;
  compact?: boolean;
  className?: string;
}

interface Point {
  x: number;
  y: number;
}

// Convert polar (angle, radius) to cartesian (x, y)
// Center is at (150, 150) for 300x300 viewport
function polarToCartesian(angleDeg: number, radius: number, center = 150): Point {
  const angleRad = (angleDeg - 90) * (Math.PI / 180);
  return {
    x: center + radius * Math.cos(angleRad),
    y: center + radius * Math.sin(angleRad),
  };
}

// Generate SVG path for polygon from scores
function scoreToPath(scores: ConstitutionScores, maxRadius = 120): string {
  const points = PRINCIPLES.map(({ key, angle }) => {
    const score = scores[key as keyof ConstitutionScores];
    const radius = score * maxRadius;
    return polarToCartesian(angle, radius);
  });

  if (points.length === 0) return '';

  const pathCommands = points.map((p, i) =>
    `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(2)} ${p.y.toFixed(2)}`
  );
  pathCommands.push('Z'); // Close path

  return pathCommands.join(' ');
}

export const ValueCompass = memo(function ValueCompass({
  scores,
  trajectory = [],
  attractor,
  compact = false,
  className = '',
}: ValueCompassProps) {
  // Compute paths
  const currentPath = useMemo(() => scoreToPath(scores), [scores]);
  const trajectoryPaths = useMemo(
    () => trajectory.map(t => scoreToPath(t)),
    [trajectory]
  );
  const attractorPath = useMemo(
    () => attractor ? scoreToPath(attractor.coordinates) : null,
    [attractor]
  );
  const attractorBasinPaths = useMemo(
    () => attractor?.basin.map(b => scoreToPath(b)) || [],
    [attractor]
  );

  const size = compact ? 200 : 300;
  const maxRadius = compact ? 80 : 120;
  const center = size / 2;

  // Grid circles for reference
  const gridLevels = [0.25, 0.5, 0.75, 1.0];

  return (
    <div className={`value-compass ${compact ? 'compact' : ''} ${className}`}>
      <svg
        viewBox={`0 0 ${size} ${size}`}
        className="compass-svg"
        aria-label="Constitutional Principles Radar"
      >
        {/* Grid circles */}
        <g className="grid-layer">
          {gridLevels.map(level => (
            <circle
              key={level}
              cx={center}
              cy={center}
              r={level * maxRadius}
              className="grid-circle"
              opacity={level === 1 ? 0.3 : 0.15}
            />
          ))}
        </g>

        {/* Axes for each principle */}
        <g className="axis-layer">
          {PRINCIPLES.map(({ key, angle }) => {
            const end = polarToCartesian(angle, maxRadius, center);
            return (
              <line
                key={key}
                x1={center}
                y1={center}
                x2={end.x}
                y2={end.y}
                className="axis-line"
              />
            );
          })}
        </g>

        {/* Attractor basin (if provided) */}
        {attractorBasinPaths.length > 0 && (
          <g className="attractor-basin-layer">
            {attractorBasinPaths.map((path, i) => (
              <path
                key={i}
                d={path}
                className="attractor-basin-path"
              />
            ))}
          </g>
        )}

        {/* Attractor coordinates (if provided) */}
        {attractorPath && (
          <g className="attractor-layer">
            <path
              d={attractorPath}
              className="attractor-path"
            />
          </g>
        )}

        {/* Historical trajectory (if provided) */}
        {trajectoryPaths.length > 0 && (
          <g className="trajectory-layer">
            {trajectoryPaths.map((path, i) => (
              <path
                key={i}
                d={path}
                className="trajectory-path"
                opacity={0.2 + (i / trajectoryPaths.length) * 0.3}
              />
            ))}
          </g>
        )}

        {/* Current scores */}
        <g className="score-layer">
          <path
            d={currentPath}
            className="score-path"
          />
          {/* Vertices for current scores */}
          {PRINCIPLES.map(({ key, angle }) => {
            const score = scores[key as keyof ConstitutionScores];
            const point = polarToCartesian(angle, score * maxRadius, center);
            return (
              <circle
                key={key}
                cx={point.x}
                cy={point.y}
                r={compact ? 3 : 4}
                className="score-vertex"
                data-principle={key}
              />
            );
          })}
        </g>

        {/* Principle labels */}
        <g className="label-layer">
          {PRINCIPLES.map(({ key, label, angle }) => {
            const labelRadius = maxRadius + (compact ? 20 : 30);
            const point = polarToCartesian(angle, labelRadius, center);

            // Adjust text anchor based on angle
            let textAnchor: 'start' | 'middle' | 'end' = 'middle';
            if (angle > 30 && angle < 150) textAnchor = 'start';
            if (angle > 210 && angle < 330) textAnchor = 'end';

            return (
              <text
                key={key}
                x={point.x}
                y={point.y}
                className="principle-label"
                textAnchor={textAnchor}
                dominantBaseline="middle"
                data-principle={key}
              >
                {compact ? label.slice(0, 3) : label}
              </text>
            );
          })}
        </g>
      </svg>

      {/* Attractor stability indicator */}
      {attractor && !compact && (
        <div className="attractor-info">
          <div className="stability-bar">
            <div
              className="stability-fill"
              style={{ width: `${attractor.stability * 100}%` }}
            />
          </div>
          <span className="stability-label">
            Stability: {(attractor.stability * 100).toFixed(0)}%
          </span>
        </div>
      )}
    </div>
  );
});

export default ValueCompass;
