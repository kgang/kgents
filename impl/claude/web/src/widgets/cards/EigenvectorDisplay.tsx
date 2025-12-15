/**
 * EigenvectorDisplay: Visualizes citizen personality vectors.
 *
 * Renders warmth, curiosity, and trust as labeled bars.
 * Uses the eigenvector values (0.0-1.0) to show personality dimensions.
 */

import { memo } from 'react';
import type { CitizenEigenvectors } from '@/reactive/types';

export interface EigenvectorDisplayProps {
  eigenvectors: CitizenEigenvectors;
  className?: string;
  compact?: boolean;
}

const EIGEN_LABELS: Record<keyof CitizenEigenvectors, { label: string; color: string }> = {
  warmth: { label: 'W', color: 'text-red-500' },
  curiosity: { label: 'C', color: 'text-blue-500' },
  trust: { label: 'T', color: 'text-green-500' },
};

export const EigenvectorDisplay = memo(function EigenvectorDisplay({
  eigenvectors,
  className,
  compact = false,
}: EigenvectorDisplayProps) {
  const width = compact ? 5 : 8;

  const renderBar = (key: keyof CitizenEigenvectors) => {
    const value = eigenvectors[key];
    const { label, color } = EIGEN_LABELS[key];
    const filled = Math.round(value * width);

    return (
      <div key={key} className={`flex items-center gap-1 ${color}`}>
        <span className="font-bold text-xs w-4">{label}:</span>
        <span className="font-mono text-xs">
          {'█'.repeat(filled)}
          {'░'.repeat(width - filled)}
        </span>
        {!compact && <span className="text-xs text-gray-500">{value.toFixed(2)}</span>}
      </div>
    );
  };

  return (
    <div className={`kgents-eigenvector-display flex flex-col gap-0.5 ${className || ''}`}>
      {renderBar('warmth')}
      {renderBar('curiosity')}
      {renderBar('trust')}
    </div>
  );
});

export default EigenvectorDisplay;
