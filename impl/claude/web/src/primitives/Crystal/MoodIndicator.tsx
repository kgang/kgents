/**
 * MoodIndicator — 7D Affective Signature Visualization
 *
 * Displays a MoodVector as a compact, subtle visual.
 * STARK BIOME aesthetic: steel base, subtle glow.
 */

import { memo } from 'react';
import type { MoodVector } from '../../types/crystal';
import './MoodIndicator.css';

// =============================================================================
// Types
// =============================================================================

interface MoodIndicatorProps {
  mood: MoodVector;
  size?: 'small' | 'medium' | 'large';
  variant?: 'dots' | 'bars';
}

// =============================================================================
// Dimension Labels
// =============================================================================

const DIMENSION_LABELS: Record<keyof MoodVector, string> = {
  warmth: 'Warmth',
  weight: 'Weight',
  tempo: 'Tempo',
  texture: 'Texture',
  brightness: 'Brightness',
  saturation: 'Saturation',
  complexity: 'Complexity',
};

// =============================================================================
// Component
// =============================================================================

export const MoodIndicator = memo(function MoodIndicator({
  mood,
  size = 'medium',
  variant = 'dots',
}: MoodIndicatorProps) {
  const dimensions: (keyof MoodVector)[] = [
    'warmth',
    'weight',
    'tempo',
    'texture',
    'brightness',
    'saturation',
    'complexity',
  ];

  if (variant === 'bars') {
    return (
      <div className={`mood-indicator mood-indicator--bars mood-indicator--${size}`}>
        {dimensions.map((dim) => (
          <div key={dim} className="mood-indicator__bar-container">
            <div
              className="mood-indicator__bar"
              style={{ width: `${mood[dim] * 100}%` }}
              title={`${DIMENSION_LABELS[dim]}: ${(mood[dim] * 100).toFixed(0)}%`}
            />
          </div>
        ))}
      </div>
    );
  }

  // Dots variant (default)
  return (
    <div className={`mood-indicator mood-indicator--dots mood-indicator--${size}`}>
      {dimensions.map((dim) => {
        const value = mood[dim];
        const intensity = Math.round(value * 3); // 0-3 scale

        return (
          <div
            key={dim}
            className={`mood-indicator__dot mood-indicator__dot--intensity-${intensity}`}
            title={`${DIMENSION_LABELS[dim]}: ${(value * 100).toFixed(0)}%`}
          />
        );
      })}
    </div>
  );
});
