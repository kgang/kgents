/**
 * EmergencePage — Cymatics Design Experience
 *
 * "Don't tune blindly. Show everything. Let the eye choose."
 *
 * The world.emergence node exposes the Cymatics Design Sampler:
 * - 9 pattern families (chladni, interference, mandala, flow, etc.)
 * - Qualia space coordinates (warmth, weight, tempo, texture, brightness, saturation, complexity)
 * - Circadian phase modulation (dawn, noon, dusk, midnight)
 *
 * This is a Crown Jewel with full categorical stack:
 * - EmergenceSheaf (tile coherence)
 * - EMERGENCE_POLYNOMIAL (phase state machine)
 * - EMERGENCE_OPERAD (composition grammar)
 *
 * AGENTESE Route: /world.emergence
 *
 * @see agents/emergence/
 * @see protocols/agentese/contexts/world_emergence.py
 */

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Waves,
  Sun,
  Moon,
  Sunrise,
  Sunset,
  CircleDot,
  Zap,
  Flower2,
  Wind,
  Sparkles,
  Circle,
  Hexagon,
  Grid3X3,
  ChevronDown,
} from 'lucide-react';
import { useAgentese } from '@/hooks/useAgentesePath';
import { Breathe } from '@/components/joy';

// =============================================================================
// Types
// =============================================================================

interface PatternFamily {
  name: string;
  description: string;
  param1: string;
  param2: string;
}

interface QualiaCoords {
  warmth: number;
  weight: number;
  tempo: number;
  texture: number;
  brightness: number;
  saturation: number;
  complexity: number;
}

interface EmergenceManifest {
  status: string;
  family_count: number;
  families: string[];
  route: string;
}

interface QualiaMetadata {
  circadian: string;
  family: string | null;
  qualia: QualiaCoords;
}

interface CircadianMetadata {
  hour: number;
  phase: string;
  modifier: {
    warmth: number;
    brightness: number;
    tempo: number;
    texture: number;
  };
}

/** BasicRendering envelope from AGENTESE aspects */
interface BasicRendering<T> {
  summary: string;
  content: string;
  metadata: T;
}

type CircadianPhase = 'dawn' | 'noon' | 'dusk' | 'midnight';

// =============================================================================
// Constants
// =============================================================================

const PATTERN_ICONS: Record<string, typeof Waves> = {
  chladni: Waves,
  interference: CircleDot,
  mandala: Flower2,
  flow: Wind,
  reaction: Sparkles,
  spiral: Circle,
  voronoi: Hexagon,
  moire: Grid3X3,
  fractal: Sparkles, // Using Sparkles as Infinity icon shadows global
};

const PATTERN_COLORS: Record<string, { color: string; bg: string }> = {
  chladni: { color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20' },
  interference: { color: 'text-cyan-400', bg: 'bg-cyan-500/10 border-cyan-500/20' },
  mandala: { color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/20' },
  flow: { color: 'text-green-400', bg: 'bg-green-500/10 border-green-500/20' },
  reaction: { color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
  spiral: { color: 'text-pink-400', bg: 'bg-pink-500/10 border-pink-500/20' },
  voronoi: { color: 'text-teal-400', bg: 'bg-teal-500/10 border-teal-500/20' },
  moire: { color: 'text-indigo-400', bg: 'bg-indigo-500/10 border-indigo-500/20' },
  fractal: { color: 'text-rose-400', bg: 'bg-rose-500/10 border-rose-500/20' },
};

const CIRCADIAN_ICONS: Record<CircadianPhase, typeof Sun> = {
  dawn: Sunrise,
  noon: Sun,
  dusk: Sunset,
  midnight: Moon,
};

const CIRCADIAN_COLORS: Record<CircadianPhase, { color: string; bg: string }> = {
  dawn: { color: 'text-orange-400', bg: 'bg-orange-500/10 border-orange-500/20' },
  noon: { color: 'text-yellow-400', bg: 'bg-yellow-500/10 border-yellow-500/20' },
  dusk: { color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/20' },
  midnight: { color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20' },
};

const QUALIA_LABELS: Record<keyof QualiaCoords, { low: string; high: string }> = {
  warmth: { low: 'cool', high: 'warm' },
  weight: { low: 'light', high: 'heavy' },
  tempo: { low: 'slow', high: 'fast' },
  texture: { low: 'smooth', high: 'rough' },
  brightness: { low: 'dark', high: 'bright' },
  saturation: { low: 'muted', high: 'vivid' },
  complexity: { low: 'simple', high: 'complex' },
};

// =============================================================================
// Sub-Components
// =============================================================================

function QualiaBar({
  name,
  value,
  labels,
}: {
  name: string;
  value: number;
  labels: { low: string; high: string };
}) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-500">
        <span>{labels.low}</span>
        <span className="text-gray-400 font-medium">{name}</span>
        <span>{labels.high}</span>
      </div>
      <div className="relative h-2 bg-gray-700/50 rounded-full overflow-hidden">
        {/* Center marker */}
        <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-600" />
        {/* Value bar */}
        <motion.div
          className={`absolute top-0 bottom-0 rounded-full ${
            value >= 0 ? 'left-1/2 bg-cyan-500' : 'right-1/2 bg-amber-500'
          }`}
          initial={{ width: 0 }}
          animate={{
            width: `${Math.abs(value) * 50}%`,
          }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        />
      </div>
      <div className="text-center text-xs text-gray-600">{value.toFixed(2)}</div>
    </div>
  );
}

function PatternCard({
  id,
  family,
  isSelected,
  onClick,
}: {
  id: string;
  family: PatternFamily;
  isSelected: boolean;
  onClick: () => void;
}) {
  const Icon = PATTERN_ICONS[id] ?? Waves;
  const colors = PATTERN_COLORS[id] ?? { color: 'text-gray-400', bg: 'bg-gray-700/50' };

  return (
    <motion.button
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      onClick={onClick}
      className={`
        p-4 rounded-xl border transition-all text-left
        ${isSelected ? `${colors.bg} ${colors.color}` : 'bg-gray-800/40 border-gray-700/50 hover:border-gray-600'}
      `}
    >
      <div className="flex items-center gap-3 mb-2">
        <Icon className={`w-5 h-5 ${isSelected ? colors.color : 'text-gray-500'}`} />
        <span className={`font-medium ${isSelected ? 'text-white' : 'text-gray-300'}`}>
          {family.name}
        </span>
      </div>
      <p className="text-xs text-gray-500 line-clamp-2">{family.description}</p>
    </motion.button>
  );
}

function CircadianBadge({ phase, hour }: { phase: CircadianPhase; hour: number }) {
  const Icon = CIRCADIAN_ICONS[phase] ?? Sun;
  const colors = CIRCADIAN_COLORS[phase] ?? { color: 'text-gray-400', bg: 'bg-gray-700/50' };

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${colors.bg}`}>
      <Icon className={`w-4 h-4 ${colors.color}`} />
      <span className={`text-sm font-medium ${colors.color}`}>
        {phase.charAt(0).toUpperCase() + phase.slice(1)}
      </span>
      <span className="text-xs text-gray-500">{hour}:00</span>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export default function EmergencePage() {
  const [selectedFamily, setSelectedFamily] = useState<string | null>(null);
  const [showAllFamilies, setShowAllFamilies] = useState(false);

  // Fetch manifest
  const { data: manifest, isLoading: manifestLoading } = useAgentese<EmergenceManifest>(
    'world.emergence'
  );

  // Fetch qualia (returns BasicRendering<QualiaMetadata>)
  const { data: qualiaResponse } = useAgentese<BasicRendering<QualiaMetadata>>('world.emergence', {
    aspect: 'qualia',
  });
  const qualia = qualiaResponse?.metadata;

  // Fetch circadian (returns BasicRendering<CircadianMetadata>)
  const { data: circadianResponse } = useAgentese<BasicRendering<CircadianMetadata>>('world.emergence', {
    aspect: 'circadian',
  });
  const circadian = circadianResponse?.metadata;

  // Build pattern families from backend (we'll show a subset initially)
  const patternFamilies: Record<string, PatternFamily> = useMemo(() => ({
    chladni: {
      name: 'Chladni Plates',
      description: 'Classic standing wave patterns from vibrating plates',
      param1: 'N Mode (2-10)',
      param2: 'M Mode (2-10)',
    },
    interference: {
      name: 'Wave Interference',
      description: 'Circular waves from multiple point sources',
      param1: 'Sources (2-8)',
      param2: 'Wavelength (0.15-0.6)',
    },
    mandala: {
      name: 'Mandala',
      description: 'Radial symmetry with angular harmonics',
      param1: 'Symmetry (3-12)',
      param2: 'Complexity (2-8)',
    },
    flow: {
      name: 'Organic Flow',
      description: 'Noise-driven fluid patterns',
      param1: 'Scale (1-6)',
      param2: 'Turbulence (0.3-0.8)',
    },
    reaction: {
      name: 'Reaction-Diffusion',
      description: 'Turing-like patterns (spots and stripes)',
      param1: 'Feature Size (3-8)',
      param2: 'Spot/Stripe Mix (0-1)',
    },
    spiral: {
      name: 'Spiral',
      description: 'Logarithmic spiral patterns',
      param1: 'Arms (2-8)',
      param2: 'Tightness (1-5)',
    },
    voronoi: {
      name: 'Voronoi Cells',
      description: 'Cellular patterns with organic edges',
      param1: 'Cell Count (3-12)',
      param2: 'Edge Sharpness (0.2-1.0)',
    },
    moire: {
      name: 'Moire',
      description: 'Overlapping line gratings',
      param1: 'Line Density (10-30)',
      param2: 'Rotation (0.05-0.3)',
    },
    fractal: {
      name: 'Fractal (Julia)',
      description: 'Self-similar mathematical patterns',
      param1: 'Zoom (1-3)',
      param2: 'Iteration Depth (0.3-1)',
    },
  }), []);

  const displayedFamilies = showAllFamilies
    ? Object.entries(patternFamilies)
    : Object.entries(patternFamilies).slice(0, 6);

  const selectedPatternDetails = selectedFamily ? patternFamilies[selectedFamily] : null;

  return (
    <div className="flex flex-col h-full bg-gray-900 text-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700/50 bg-gray-800/40">
        <div className="flex items-center gap-3">
          <Breathe intensity={0.4} speed="slow">
            <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-cyan-500/30">
              <Waves className="w-6 h-6 text-cyan-400" />
            </div>
          </Breathe>
          <div>
            <h1 className="text-lg font-semibold text-white">Cymatics Design Sampler</h1>
            <p className="text-xs text-gray-500">
              &quot;Show everything. Let the eye choose.&quot;
            </p>
          </div>
        </div>

        {circadian && (
          <CircadianBadge
            phase={circadian.phase as CircadianPhase}
            hour={circadian.hour}
          />
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel: Qualia Space */}
        <div className="w-80 p-4 border-r border-gray-700/50 overflow-y-auto">
          <div className="space-y-6">
            {/* Qualia Visualization */}
            <div className="p-4 rounded-xl bg-gray-800/40 border border-gray-700/50">
              <div className="flex items-center gap-2 mb-4">
                <Zap className="w-4 h-4 text-amber-400" />
                <h3 className="text-sm font-medium text-gray-300">Qualia Space</h3>
              </div>

              {qualia ? (
                <div className="space-y-4">
                  {(Object.keys(QUALIA_LABELS) as Array<keyof QualiaCoords>).map((key) => (
                    <QualiaBar
                      key={key}
                      name={key.charAt(0).toUpperCase() + key.slice(1)}
                      value={qualia.qualia[key]}
                      labels={QUALIA_LABELS[key]}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">Loading qualia...</div>
              )}
            </div>

            {/* Circadian Modifiers */}
            {circadian && (
              <div className="p-4 rounded-xl bg-gray-800/40 border border-gray-700/50">
                <div className="flex items-center gap-2 mb-3">
                  {(() => {
                    const Icon = CIRCADIAN_ICONS[circadian.phase as CircadianPhase] ?? Sun;
                    const colors = CIRCADIAN_COLORS[circadian.phase as CircadianPhase];
                    return <Icon className={`w-4 h-4 ${colors?.color ?? 'text-gray-400'}`} />;
                  })()}
                  <h3 className="text-sm font-medium text-gray-300">Circadian Modifiers</h3>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Warmth</span>
                    <span className="text-gray-300">{circadian.modifier.warmth.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Brightness</span>
                    <span className="text-gray-300">
                      {(circadian.modifier.brightness * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Tempo</span>
                    <span className="text-gray-300">{circadian.modifier.tempo.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Texture</span>
                    <span className="text-gray-300">{circadian.modifier.texture.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel: Pattern Families */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Pattern Grid */}
          <div className="flex-1 overflow-y-auto p-4">
            {manifestLoading ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-gray-500">Loading patterns...</div>
              </div>
            ) : (
              <>
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-sm font-medium text-gray-400">
                    Pattern Families ({manifest?.family_count ?? 9})
                  </h2>
                </div>

                <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                  <AnimatePresence mode="popLayout">
                    {displayedFamilies.map(([id, family]) => (
                      <motion.div
                        key={id}
                        layout
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                      >
                        <PatternCard
                          id={id}
                          family={family}
                          isSelected={selectedFamily === id}
                          onClick={() => setSelectedFamily(selectedFamily === id ? null : id)}
                        />
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>

                {/* Show More */}
                {!showAllFamilies && Object.keys(patternFamilies).length > 6 && (
                  <button
                    onClick={() => setShowAllFamilies(true)}
                    className="w-full mt-4 py-2 flex items-center justify-center gap-2 text-gray-400 hover:text-gray-200 transition-colors"
                  >
                    <span className="text-sm">Show all families</span>
                    <ChevronDown className="w-4 h-4" />
                  </button>
                )}
              </>
            )}
          </div>

          {/* Selected Pattern Details */}
          <AnimatePresence>
            {selectedPatternDetails && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="border-t border-gray-700/50 bg-gray-800/40 overflow-hidden"
              >
                <div className="p-4">
                  <div className="flex items-center gap-3 mb-3">
                    {(() => {
                      if (!selectedFamily) return null;
                      const Icon = PATTERN_ICONS[selectedFamily] ?? Waves;
                      const colors = PATTERN_COLORS[selectedFamily];
                      return (
                        <div className={`p-2 rounded-lg ${colors?.bg ?? 'bg-gray-700'}`}>
                          <Icon className={`w-5 h-5 ${colors?.color ?? 'text-gray-400'}`} />
                        </div>
                      );
                    })()}
                    <div>
                      <h3 className="font-medium text-white">{selectedPatternDetails.name}</h3>
                      <p className="text-xs text-gray-500">{selectedPatternDetails.description}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="p-3 rounded-lg bg-gray-900/50">
                      <div className="text-xs text-gray-600 mb-1">Parameter 1</div>
                      <div className="text-gray-300">{selectedPatternDetails.param1}</div>
                    </div>
                    <div className="p-3 rounded-lg bg-gray-900/50">
                      <div className="text-xs text-gray-600 mb-1">Parameter 2</div>
                      <div className="text-gray-300">{selectedPatternDetails.param2}</div>
                    </div>
                  </div>

                  <p className="mt-4 text-xs text-gray-600 text-center">
                    Cymatics pattern visualization coming in future release
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
