/**
 * OverrideControls: Controls for entropy, seed, and phase overrides.
 */

import type { GalleryOverrides } from '@/api/types';

interface OverrideControlsProps {
  overrides: GalleryOverrides;
  onChange: (overrides: GalleryOverrides) => void;
}

const PHASES = ['idle', 'active', 'waiting', 'error', 'complete', 'working'];

export function OverrideControls({ overrides, onChange }: OverrideControlsProps) {
  const handleEntropyChange = (value: number) => {
    onChange({ ...overrides, entropy: value });
  };

  const handleSeedChange = (value: string) => {
    const seed = value ? parseInt(value, 10) : undefined;
    onChange({ ...overrides, seed: isNaN(seed!) ? undefined : seed });
  };

  const handlePhaseChange = (value: string) => {
    onChange({ ...overrides, phase: value || undefined });
  };

  return (
    <div className="flex flex-wrap items-center gap-4 text-sm">
      {/* Entropy slider */}
      <div className="flex items-center gap-2">
        <label className="text-gray-400 whitespace-nowrap">Entropy:</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={overrides.entropy ?? 0}
          onChange={(e) => handleEntropyChange(parseFloat(e.target.value))}
          className="w-24 h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-town-highlight"
        />
        <span className="text-gray-300 font-mono w-10 text-right">
          {(overrides.entropy ?? 0).toFixed(2)}
        </span>
      </div>

      {/* Seed input */}
      <div className="flex items-center gap-2">
        <label className="text-gray-400 whitespace-nowrap">Seed:</label>
        <input
          type="number"
          min="0"
          max="9999"
          placeholder="42"
          value={overrides.seed ?? ''}
          onChange={(e) => handleSeedChange(e.target.value)}
          className="w-20 px-2 py-1 bg-town-surface border border-town-accent/30 rounded text-gray-300 text-sm"
        />
      </div>

      {/* Phase dropdown */}
      <div className="flex items-center gap-2">
        <label className="text-gray-400 whitespace-nowrap">Phase:</label>
        <select
          value={overrides.phase ?? ''}
          onChange={(e) => handlePhaseChange(e.target.value)}
          className="px-2 py-1 bg-town-surface border border-town-accent/30 rounded text-gray-300 text-sm"
        >
          <option value="">Default</option>
          {PHASES.map((phase) => (
            <option key={phase} value={phase}>
              {phase}
            </option>
          ))}
        </select>
      </div>

      {/* Reset button */}
      <button
        onClick={() => onChange({})}
        className="px-2 py-1 text-xs text-gray-500 hover:text-gray-300 transition-colors"
        title="Reset all overrides"
      >
        Reset
      </button>
    </div>
  );
}

export default OverrideControls;
