/**
 * EigenvectorSliders: 7D slider controls for personality tuning.
 *
 * Eigenvectors: warmth, curiosity, trust, creativity, patience, resilience, ambition
 */

import { useState } from 'react';
import { cn } from '@/lib/utils';
import type { Eigenvectors, Archetype } from '@/api/types';

export interface EigenvectorSlidersProps {
  values: Eigenvectors;
  onChange: (values: Eigenvectors) => void;
  archetype?: Archetype | null;
  showPresets?: boolean;
  className?: string;
}

interface VectorConfig {
  key: keyof Eigenvectors;
  label: string;
  icon: string;
  color: string;
  description: string;
  lowLabel: string;
  highLabel: string;
}

const VECTOR_CONFIG: VectorConfig[] = [
  {
    key: 'warmth',
    label: 'Warmth',
    icon: '❤️',
    color: 'bg-red-500',
    description: 'Emotional expressiveness and approachability',
    lowLabel: 'Reserved',
    highLabel: 'Affectionate',
  },
  {
    key: 'curiosity',
    label: 'Curiosity',
    icon: '🔍',
    color: 'bg-yellow-500',
    description: 'Drive to explore and learn new things',
    lowLabel: 'Content',
    highLabel: 'Inquisitive',
  },
  {
    key: 'trust',
    label: 'Trust',
    icon: '🤝',
    color: 'bg-green-500',
    description: 'Openness to others and collaborative spirit',
    lowLabel: 'Cautious',
    highLabel: 'Trusting',
  },
  {
    key: 'creativity',
    label: 'Creativity',
    icon: '✨',
    color: 'bg-purple-500',
    description: 'Imaginative thinking and novel approaches',
    lowLabel: 'Practical',
    highLabel: 'Imaginative',
  },
  {
    key: 'patience',
    label: 'Patience',
    icon: '⏳',
    color: 'bg-blue-500',
    description: 'Tolerance for slow progress and delayed rewards',
    lowLabel: 'Impulsive',
    highLabel: 'Patient',
  },
  {
    key: 'resilience',
    label: 'Resilience',
    icon: '💪',
    color: 'bg-orange-500',
    description: 'Ability to recover from setbacks',
    lowLabel: 'Sensitive',
    highLabel: 'Resilient',
  },
  {
    key: 'ambition',
    label: 'Ambition',
    icon: '🚀',
    color: 'bg-pink-500',
    description: 'Drive to achieve and excel',
    lowLabel: 'Relaxed',
    highLabel: 'Driven',
  },
];

const PRESETS: { name: string; values: Eigenvectors }[] = [
  {
    name: 'Balanced',
    values: { warmth: 0.5, curiosity: 0.5, trust: 0.5, creativity: 0.5, patience: 0.5, resilience: 0.5, ambition: 0.5 },
  },
  {
    name: 'Explorer',
    values: { warmth: 0.4, curiosity: 0.9, trust: 0.5, creativity: 0.7, patience: 0.3, resilience: 0.6, ambition: 0.7 },
  },
  {
    name: 'Diplomat',
    values: { warmth: 0.8, curiosity: 0.5, trust: 0.8, creativity: 0.4, patience: 0.7, resilience: 0.5, ambition: 0.4 },
  },
  {
    name: 'Innovator',
    values: { warmth: 0.4, curiosity: 0.7, trust: 0.4, creativity: 0.9, patience: 0.3, resilience: 0.7, ambition: 0.8 },
  },
  {
    name: 'Guardian',
    values: { warmth: 0.6, curiosity: 0.4, trust: 0.6, creativity: 0.3, patience: 0.8, resilience: 0.9, ambition: 0.4 },
  },
];

export function EigenvectorSliders({
  values,
  onChange,
  archetype: _archetype,
  showPresets = true,
  className,
}: EigenvectorSlidersProps) {
  const [hoveredVector, setHoveredVector] = useState<keyof Eigenvectors | null>(null);

  const handleChange = (key: keyof Eigenvectors, value: number) => {
    onChange({ ...values, [key]: value });
  };

  const handlePreset = (preset: Eigenvectors) => {
    onChange(preset);
  };

  const handleRandomize = () => {
    const randomized: Eigenvectors = {
      warmth: Math.random(),
      curiosity: Math.random(),
      trust: Math.random(),
      creativity: Math.random(),
      patience: Math.random(),
      resilience: Math.random(),
      ambition: Math.random(),
    };
    onChange(randomized);
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* Presets */}
      {showPresets && (
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((preset) => (
            <button
              key={preset.name}
              onClick={() => handlePreset(preset.values)}
              className="px-3 py-1 text-xs bg-town-surface/50 hover:bg-town-accent/30 rounded-full transition-colors"
            >
              {preset.name}
            </button>
          ))}
          <button
            onClick={handleRandomize}
            className="px-3 py-1 text-xs bg-town-surface/50 hover:bg-town-accent/30 rounded-full transition-colors"
            title="Randomize all values"
          >
            🎲 Random
          </button>
        </div>
      )}

      {/* Sliders */}
      <div className="space-y-4">
        {VECTOR_CONFIG.map((config) => (
          <VectorSlider
            key={config.key}
            config={config}
            value={values[config.key]}
            onChange={(v) => handleChange(config.key, v)}
            isHovered={hoveredVector === config.key}
            onHover={(hovered) => setHoveredVector(hovered ? config.key : null)}
          />
        ))}
      </div>

      {/* Description tooltip */}
      {hoveredVector && (
        <div className="text-sm text-gray-400 bg-town-surface/30 rounded-lg p-3">
          {VECTOR_CONFIG.find((c) => c.key === hoveredVector)?.description}
        </div>
      )}

      {/* Summary visualization */}
      <EigenvectorRadarMini values={values} />
    </div>
  );
}

// =============================================================================
// Slider Component
// =============================================================================

interface VectorSliderProps {
  config: VectorConfig;
  value: number;
  onChange: (value: number) => void;
  isHovered: boolean;
  onHover: (hovered: boolean) => void;
}

function VectorSlider({ config, value, onChange, isHovered, onHover }: VectorSliderProps) {
  return (
    <div
      className={cn(
        'p-3 rounded-lg transition-colors',
        isHovered ? 'bg-town-surface/30' : ''
      )}
      onMouseEnter={() => onHover(true)}
      onMouseLeave={() => onHover(false)}
    >
      <div className="flex items-center gap-3 mb-2">
        <span className="text-lg">{config.icon}</span>
        <span className="font-medium flex-1">{config.label}</span>
        <span className="text-sm font-mono text-gray-400 w-12 text-right">
          {value.toFixed(2)}
        </span>
      </div>

      <div className="flex items-center gap-3">
        <span className="text-xs text-gray-500 w-20 text-right">{config.lowLabel}</span>

        <div className="flex-1 relative">
          {/* Track background */}
          <div className="h-2 bg-town-surface rounded-full overflow-hidden">
            {/* Filled portion */}
            <div
              className={cn('h-full transition-all', config.color)}
              style={{ width: `${value * 100}%` }}
            />
          </div>

          {/* Input range (invisible but captures interaction) */}
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={value}
            onChange={(e) => onChange(parseFloat(e.target.value))}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />

          {/* Thumb indicator */}
          <div
            className={cn(
              'absolute top-1/2 -translate-y-1/2 w-4 h-4 rounded-full shadow-lg transition-all',
              config.color,
              'ring-2 ring-white/30'
            )}
            style={{ left: `calc(${value * 100}% - 8px)` }}
          />
        </div>

        <span className="text-xs text-gray-500 w-20">{config.highLabel}</span>
      </div>
    </div>
  );
}

// =============================================================================
// Mini Radar Chart
// =============================================================================

function EigenvectorRadarMini({ values }: { values: Eigenvectors }) {
  const size = 120;
  const center = size / 2;
  const radius = size / 2 - 15;

  const vectors = VECTOR_CONFIG.map((c) => ({
    key: c.key,
    icon: c.icon,
    value: values[c.key],
  }));

  const angleStep = (Math.PI * 2) / vectors.length;

  // Generate polygon points
  const points = vectors
    .map(({ value }, i) => {
      const angle = i * angleStep - Math.PI / 2;
      const r = value * radius;
      const x = center + Math.cos(angle) * r;
      const y = center + Math.sin(angle) * r;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <div className="flex justify-center">
      <svg width={size} height={size} className="opacity-70">
        {/* Background ring */}
        <polygon
          points={vectors
            .map((_, i) => {
              const angle = i * angleStep - Math.PI / 2;
              const x = center + Math.cos(angle) * radius;
              const y = center + Math.sin(angle) * radius;
              return `${x},${y}`;
            })
            .join(' ')}
          fill="none"
          stroke="currentColor"
          strokeOpacity="0.2"
        />

        {/* Data polygon */}
        <polygon
          points={points}
          fill="var(--town-highlight, #60a5fa)"
          fillOpacity="0.3"
          stroke="var(--town-highlight, #60a5fa)"
          strokeWidth="2"
        />

        {/* Labels */}
        {vectors.map(({ icon }, i) => {
          const angle = i * angleStep - Math.PI / 2;
          const x = center + Math.cos(angle) * (radius + 12);
          const y = center + Math.sin(angle) * (radius + 12);
          return (
            <text
              key={i}
              x={x}
              y={y + 4}
              fontSize="12"
              textAnchor="middle"
              dominantBaseline="middle"
            >
              {icon}
            </text>
          );
        })}
      </svg>
    </div>
  );
}

export default EigenvectorSliders;
