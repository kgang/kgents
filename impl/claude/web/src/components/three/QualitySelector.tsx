/**
 * QualitySelector - UI for illumination quality override
 *
 * Allows users to manually select quality level if auto-detection is incorrect,
 * or if they want to experience cinematic quality on a capable device.
 *
 * Usage:
 * ```tsx
 * const { quality, override, isAutoDetected } = useIlluminationQuality();
 *
 * <QualitySelector
 *   currentQuality={quality}
 *   isAutoDetected={isAutoDetected}
 *   onQualityChange={override}
 * />
 * ```
 */

import {
  type IlluminationQuality,
  QUALITY_DESCRIPTIONS,
  ssaoEnabled,
} from '../../constants/lighting';

// =============================================================================
// Types
// =============================================================================

export interface QualitySelectorProps {
  /** Current quality level */
  currentQuality: IlluminationQuality;
  /** Whether current quality was auto-detected */
  isAutoDetected: boolean;
  /** Callback when user changes quality */
  onQualityChange: (quality: IlluminationQuality | null) => void;
  /** Compact mode for mobile/overlay */
  compact?: boolean;
  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

const QUALITY_LEVELS: IlluminationQuality[] = ['minimal', 'standard', 'high', 'cinematic'];

const QUALITY_ICONS: Record<IlluminationQuality, string> = {
  minimal: '🔋',
  standard: '⚡',
  high: '✨',
  cinematic: '🎬',
};

// =============================================================================
// Component
// =============================================================================

export function QualitySelector({
  currentQuality,
  isAutoDetected,
  onQualityChange,
  compact = false,
  className = '',
}: QualitySelectorProps) {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    if (value === 'auto') {
      onQualityChange(null);
    } else {
      onQualityChange(value as IlluminationQuality);
    }
  };

  if (compact) {
    return (
      <div className={`flex items-center gap-1.5 ${className}`}>
        <select
          value={isAutoDetected ? 'auto' : currentQuality}
          onChange={handleChange}
          className="bg-gray-700 text-gray-200 text-xs rounded px-1.5 py-1 border border-gray-600 focus:outline-none focus:border-cyan-500 cursor-pointer"
          aria-label="Quality level"
        >
          <option value="auto">Auto</option>
          {QUALITY_LEVELS.map((level) => (
            <option key={level} value={level}>
              {QUALITY_ICONS[level]} {level.charAt(0).toUpperCase() + level.slice(1)}
            </option>
          ))}
        </select>
        {ssaoEnabled(currentQuality) && (
          <span className="text-[10px] text-purple-400 font-medium" title="SSAO enabled">
            SSAO
          </span>
        )}
      </div>
    );
  }

  return (
    <div className={`bg-gray-800/90 backdrop-blur-sm rounded-lg p-3 ${className}`}>
      <label className="block text-xs text-gray-400 mb-1.5">
        Render Quality
        {isAutoDetected && <span className="text-green-400 ml-1">(auto)</span>}
      </label>
      <select
        value={isAutoDetected ? 'auto' : currentQuality}
        onChange={handleChange}
        className="w-full bg-gray-700 text-gray-200 text-sm rounded px-2 py-1.5 border border-gray-600 focus:outline-none focus:border-cyan-500 cursor-pointer"
        aria-label="Quality level"
      >
        <option value="auto">Auto ({currentQuality})</option>
        {QUALITY_LEVELS.map((level) => (
          <option key={level} value={level}>
            {QUALITY_ICONS[level]} {level.charAt(0).toUpperCase() + level.slice(1)}
          </option>
        ))}
      </select>
      <p className="text-[10px] text-gray-500 mt-1.5">
        {QUALITY_DESCRIPTIONS[currentQuality]}
      </p>
    </div>
  );
}

export default QualitySelector;
