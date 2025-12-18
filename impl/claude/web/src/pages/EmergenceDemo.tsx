/**
 * EmergenceDemo - Cymatics Design Experience (Crown Jewel)
 *
 * A visual exploration of pattern families with full vertical slice compliance:
 * - Layer 1: EmergenceSheaf (tile coherence)
 * - Layer 2: EMERGENCE_POLYNOMIAL (5 phases)
 * - Layer 3: EMERGENCE_OPERAD (composition grammar)
 * - Layer 4: agents/emergence/ (service module)
 * - Layer 5: @node decorator (world.emergence.*)
 * - Layer 6: Gateway discovery
 * - Layer 7: Web projection (this file)
 * - Layer 8: REST API via AGENTESE gateway
 *
 * Philosophy:
 *   "Don't tune blindly. Show everything. Let the eye choose."
 *
 * Design System Integration:
 * - ElasticSplit for responsive gallery/controls
 * - BottomDrawer for mobile controls
 * - FloatingActions for quick preset access
 * - useDesignPolynomial for density-aware behavior
 * - Full circadian modulation (dawn/noon/dusk/midnight)
 *
 * @see impl/claude/agents/emergence/ (categorical foundation)
 * @see impl/claude/protocols/agentese/contexts/world_emergence.py (AGENTESE node)
 * @see plans/structured-greeting-boot.md (enhancement plan)
 */

import { useState, useMemo, useCallback, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';

import {
  PatternTile,
  PATTERN_PRESETS,
  CURATED_PRESETS,
  type PatternConfig,
  type PatternFamily,
} from '../components/three/CymaticsSampler';

// Elastic UI primitives
import {
  ElasticSplit,
  BottomDrawer,
  FloatingActions,
} from '../components/elastic';

// Design polynomial for density-aware behavior
import { useDesignPolynomial, type Density } from '../hooks/useDesignPolynomial';

// =============================================================================
// Types (aligned with agents/emergence/types.py)
// =============================================================================

interface FamilyInfo {
  name: string;
  description: string;
  param1Label: string;
  param2Label: string;
  param1Range: [number, number];
  param2Range: [number, number];
}

/** Circadian phase (mirroring Python CircadianPhase) */
type CircadianPhase = 'dawn' | 'noon' | 'dusk' | 'midnight';

/** Qualia coordinates (subset for frontend - reserved for future use) */
// interface QualiaCoords {
//   warmth: number;   // -1 to 1 (cyan to amber)
//   weight: number;   // -1 to 1 (light to heavy)
//   tempo: number;    // -1 to 1 (slow to fast)
//   brightness: number; // 0 to 1
// }

// =============================================================================
// Constants (aligned with agents/emergence/types.py)
// =============================================================================

const PATTERN_FAMILIES: Record<PatternFamily, FamilyInfo> = {
  chladni: {
    name: 'Chladni Plates',
    description: 'Classic standing wave patterns from vibrating plates',
    param1Label: 'N Mode',
    param2Label: 'M Mode',
    param1Range: [2, 10],
    param2Range: [2, 10],
  },
  interference: {
    name: 'Wave Interference',
    description: 'Circular waves from multiple point sources',
    param1Label: 'Sources',
    param2Label: 'Wavelength',
    param1Range: [2, 8],
    param2Range: [0.15, 0.6],
  },
  mandala: {
    name: 'Mandala',
    description: 'Radial symmetry with angular harmonics',
    param1Label: 'Symmetry',
    param2Label: 'Complexity',
    param1Range: [3, 12],
    param2Range: [2, 8],
  },
  flow: {
    name: 'Organic Flow',
    description: 'Noise-driven fluid patterns',
    param1Label: 'Scale',
    param2Label: 'Turbulence',
    param1Range: [1, 6],
    param2Range: [0.3, 0.8],
  },
  reaction: {
    name: 'Reaction-Diffusion',
    description: 'Turing-like patterns (spots and stripes)',
    param1Label: 'Feature Size',
    param2Label: 'Spot/Stripe Mix',
    param1Range: [3, 8],
    param2Range: [0, 1],
  },
  spiral: {
    name: 'Spiral',
    description: 'Logarithmic spiral patterns',
    param1Label: 'Arms',
    param2Label: 'Tightness',
    param1Range: [2, 8],
    param2Range: [1, 5],
  },
  voronoi: {
    name: 'Voronoi Cells',
    description: 'Cellular patterns with organic edges',
    param1Label: 'Cell Count',
    param2Label: 'Edge Sharpness',
    param1Range: [3, 12],
    param2Range: [0.2, 1.0],
  },
  moiré: {
    name: 'Moiré',
    description: 'Overlapping line gratings',
    param1Label: 'Line Density',
    param2Label: 'Rotation',
    param1Range: [10, 30],
    param2Range: [0.05, 0.3],
  },
  fractal: {
    name: 'Fractal (Julia)',
    description: 'Self-similar mathematical patterns',
    param1Label: 'Zoom',
    param2Label: 'Iteration Depth',
    param1Range: [1, 3],
    param2Range: [0.3, 1],
  },
};

/** Family qualia mappings (from agents/emergence/types.py FAMILY_QUALIA)
 * Reserved for future qualia-based sorting/filtering
 */
// const FAMILY_QUALIA: Record<PatternFamily, QualiaCoords> = {
//   chladni: { warmth: -0.3, weight: 0.2, tempo: 0.3, brightness: 0.7 },
//   interference: { warmth: -0.2, weight: -0.3, tempo: 0.4, brightness: 0.8 },
//   mandala: { warmth: 0.2, weight: 0.5, tempo: -0.3, brightness: 0.6 },
//   flow: { warmth: 0.4, weight: -0.2, tempo: -0.1, brightness: 0.5 },
//   reaction: { warmth: 0.1, weight: 0.3, tempo: 0.5, brightness: 0.6 },
//   spiral: { warmth: 0.3, weight: 0.1, tempo: 0.2, brightness: 0.7 },
//   voronoi: { warmth: -0.1, weight: 0.4, tempo: -0.2, brightness: 0.5 },
//   moiré: { warmth: -0.4, weight: -0.1, tempo: 0.1, brightness: 0.9 },
//   fractal: { warmth: 0.0, weight: 0.6, tempo: -0.4, brightness: 0.4 },
// };

/** Circadian modifiers (from agents/emergence/types.py CIRCADIAN_MODIFIERS) */
const CIRCADIAN_MODIFIERS: Record<CircadianPhase, { warmth: number; brightness: number; tempo: number }> = {
  dawn: { warmth: -0.2, brightness: 0.8, tempo: 0.2 },
  noon: { warmth: 0.0, brightness: 1.0, tempo: 0.0 },
  dusk: { warmth: 0.3, brightness: 0.6, tempo: -0.2 },
  midnight: { warmth: -0.1, brightness: 0.3, tempo: -0.4 },
};

const HUE_PRESETS: { name: string; hue: number; saturation: number }[] = [
  { name: 'Cyan', hue: 0.55, saturation: 0.8 },
  { name: 'Amber', hue: 0.08, saturation: 0.8 },
  { name: 'Purple', hue: 0.75, saturation: 0.7 },
  { name: 'Teal', hue: 0.45, saturation: 0.7 },
  { name: 'Rose', hue: 0.95, saturation: 0.6 },
  { name: 'Gold', hue: 0.12, saturation: 0.9 },
  { name: 'Mono', hue: 0, saturation: 0 },
];

/** Density-parameterized constants */
const GRID_COLUMNS: Record<Density, number> = { compact: 2, comfortable: 3, spacious: 3 };
const TILE_SIZE: Record<Density, number> = { compact: 140, comfortable: 180, spacious: 220 };
const PRESET_COLUMNS: Record<Density, number> = { compact: 3, comfortable: 6, spacious: 8 };

// =============================================================================
// Circadian Hook
// =============================================================================

/** Get circadian phase from hour (0-23) */
function getCircadianPhase(hour: number): CircadianPhase {
  if (hour >= 6 && hour < 10) return 'dawn';
  if (hour >= 10 && hour < 16) return 'noon';
  if (hour >= 16 && hour < 20) return 'dusk';
  return 'midnight';
}

/** Hook for circadian phase tracking */
function useCircadian() {
  const [phase, setPhase] = useState<CircadianPhase>(() =>
    getCircadianPhase(new Date().getHours())
  );
  const [overridePhase, setOverridePhase] = useState<CircadianPhase | null>(null);

  // Update phase every minute
  useEffect(() => {
    const interval = setInterval(() => {
      setPhase(getCircadianPhase(new Date().getHours()));
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  const effectivePhase = overridePhase ?? phase;
  const modifier = CIRCADIAN_MODIFIERS[effectivePhase];

  return {
    phase: effectivePhase,
    naturalPhase: phase,
    modifier,
    setOverride: setOverridePhase,
    clearOverride: () => setOverridePhase(null),
    isOverridden: overridePhase !== null,
  };
}

// =============================================================================
// Apply circadian modulation to hue
// =============================================================================

function applyCircadianToHue(baseHue: number, modifier: { warmth: number }): number {
  // Warmth shifts hue towards amber (0.08) or cyan (0.55)
  const warmthShift = modifier.warmth * 0.05;
  return Math.max(0, Math.min(1, baseHue + warmthShift));
}

// =============================================================================
// Sub-Components
// =============================================================================

function PatternCanvas({
  config,
  size = 200,
  selected,
  onSelect,
  label,
  circadianModifier,
}: {
  config: PatternConfig;
  size?: number;
  selected?: boolean;
  onSelect?: () => void;
  label?: string;
  circadianModifier?: { warmth: number; brightness: number };
}) {
  // Apply circadian modulation
  const adjustedConfig = useMemo(() => {
    if (!circadianModifier) return config;
    return {
      ...config,
      hue: applyCircadianToHue(config.hue, circadianModifier),
    };
  }, [config, circadianModifier]);

  return (
    <div
      className={`relative cursor-pointer transition-all duration-200 hover:scale-105 ${
        selected ? 'ring-2 ring-cyan-400 ring-offset-2 ring-offset-gray-900 scale-105' : ''
      }`}
      onClick={onSelect}
      style={{ width: size, height: size }}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect?.();
        }
      }}
    >
      <Canvas
        camera={{ position: [0, 0, 1.2], fov: 45 }}
        style={{ background: '#111' }}
      >
        <PatternTile config={adjustedConfig} size={1.8} animate={true} />
      </Canvas>
      {label && (
        <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-xs py-1 px-2 truncate">
          {label}
        </div>
      )}
    </div>
  );
}

function Slider({
  label,
  value,
  min,
  max,
  step = 0.01,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between text-xs text-gray-400">
        <span>{label}</span>
        <span className="font-mono">{value.toFixed(2)}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
      />
    </div>
  );
}

/** Circadian indicator showing current phase */
function CircadianIndicator({
  phase,
  isOverridden,
  onOverride,
}: {
  phase: CircadianPhase;
  isOverridden: boolean;
  onOverride: (phase: CircadianPhase | null) => void;
}) {
  const phaseEmoji: Record<CircadianPhase, string> = {
    dawn: '🌅',
    noon: '☀️',
    dusk: '🌇',
    midnight: '🌙',
  };

  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="text-gray-400">Circadian:</span>
      <div className="flex gap-1">
        {(['dawn', 'noon', 'dusk', 'midnight'] as CircadianPhase[]).map((p) => (
          <button
            key={p}
            onClick={() => onOverride(phase === p && isOverridden ? null : p)}
            className={`px-2 py-1 rounded text-xs transition-colors ${
              phase === p
                ? 'bg-cyan-600 text-white'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
            }`}
            title={`${p} ${isOverridden && phase === p ? '(override active)' : ''}`}
          >
            {phaseEmoji[p]}
          </button>
        ))}
      </div>
      {isOverridden && (
        <button
          onClick={() => onOverride(null)}
          className="text-xs text-gray-500 hover:text-gray-300"
        >
          (reset)
        </button>
      )}
    </div>
  );
}

/** Controls panel - used in both sidebar and drawer */
function ControlsPanel({
  customConfig,
  updateConfig,
  onFamilyChange,
}: {
  customConfig: PatternConfig;
  updateConfig: (updates: Partial<PatternConfig>) => void;
  onFamilyChange: (family: PatternFamily) => void;
}) {
  return (
    <div className="space-y-6 p-4">
      <div>
        <h3 className="text-lg font-semibold mb-2">Pattern Family</h3>
        <select
          value={customConfig.family}
          onChange={(e) => {
            const family = e.target.value as PatternFamily;
            const info = PATTERN_FAMILIES[family];
            updateConfig({
              family,
              param1: (info.param1Range[0] + info.param1Range[1]) / 2,
              param2: (info.param2Range[0] + info.param2Range[1]) / 2,
            });
            onFamilyChange(family);
          }}
          className="w-full bg-gray-700 text-white rounded px-3 py-2 min-h-[48px]"
        >
          {(Object.keys(PATTERN_FAMILIES) as PatternFamily[]).map((f) => (
            <option key={f} value={f}>
              {PATTERN_FAMILIES[f].name}
            </option>
          ))}
        </select>
        <p className="text-xs text-gray-400 mt-1">
          {PATTERN_FAMILIES[customConfig.family].description}
        </p>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Parameters</h3>
        <Slider
          label={PATTERN_FAMILIES[customConfig.family].param1Label}
          value={customConfig.param1}
          min={PATTERN_FAMILIES[customConfig.family].param1Range[0]}
          max={PATTERN_FAMILIES[customConfig.family].param1Range[1]}
          step={0.1}
          onChange={(v) => updateConfig({ param1: v })}
        />
        <Slider
          label={PATTERN_FAMILIES[customConfig.family].param2Label}
          value={customConfig.param2}
          min={PATTERN_FAMILIES[customConfig.family].param2Range[0]}
          max={PATTERN_FAMILIES[customConfig.family].param2Range[1]}
          step={0.01}
          onChange={(v) => updateConfig({ param2: v })}
        />
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Color</h3>
        <Slider
          label="Hue"
          value={customConfig.hue}
          min={0}
          max={1}
          onChange={(v) => updateConfig({ hue: v })}
        />
        <Slider
          label="Saturation"
          value={customConfig.saturation}
          min={0}
          max={1}
          onChange={(v) => updateConfig({ saturation: v })}
        />
        <div className="flex gap-2 flex-wrap">
          {HUE_PRESETS.map((preset) => (
            <button
              key={preset.name}
              onClick={() =>
                updateConfig({ hue: preset.hue, saturation: preset.saturation })
              }
              className="w-10 h-10 rounded border-2 border-gray-600 hover:border-white transition-colors min-w-[40px] min-h-[40px]"
              style={{
                background: `hsl(${preset.hue * 360}, ${preset.saturation * 100}%, 40%)`,
              }}
              title={preset.name}
            />
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Animation</h3>
        <Slider
          label="Speed"
          value={customConfig.speed}
          min={0}
          max={2}
          onChange={(v) => updateConfig({ speed: v })}
        />
        <label className="flex items-center gap-2 text-sm min-h-[48px]">
          <input
            type="checkbox"
            checked={customConfig.invert}
            onChange={(e) => updateConfig({ invert: e.target.checked })}
            className="rounded w-5 h-5"
          />
          Invert colors
        </label>
      </div>

      <div className="pt-4 border-t border-gray-700">
        <h4 className="text-sm font-medium text-gray-400 mb-2">Config (copy to use)</h4>
        <pre className="bg-gray-900 rounded p-2 text-xs overflow-x-auto">
          {JSON.stringify(customConfig, null, 2)}
        </pre>
      </div>
    </div>
  );
}

// =============================================================================
// Gallery View Component
// =============================================================================

function GalleryView({
  selectedFamily,
  setSelectedFamily,
  customConfig,
  handleSelectVariation,
  selectedPreset,
  circadianModifier,
  density,
}: {
  selectedFamily: PatternFamily;
  setSelectedFamily: (f: PatternFamily) => void;
  customConfig: PatternConfig;
  handleSelectVariation: (config: PatternConfig, key: string) => void;
  selectedPreset: string | null;
  circadianModifier: { warmth: number; brightness: number };
  density: Density;
}) {
  const familyInfo = PATTERN_FAMILIES[selectedFamily];
  const tileSize = TILE_SIZE[density];
  const gridCols = GRID_COLUMNS[density];
  const presetCols = PRESET_COLUMNS[density];

  // Generate variations for current family
  const familyVariations = useMemo(() => {
    const info = PATTERN_FAMILIES[selectedFamily];
    const variations: { key: string; config: PatternConfig }[] = [];

    // Generate 9 variations (3x3 grid)
    const param1Steps = [
      info.param1Range[0],
      (info.param1Range[0] + info.param1Range[1]) / 2,
      info.param1Range[1],
    ];
    const param2Steps = [
      info.param2Range[0],
      (info.param2Range[0] + info.param2Range[1]) / 2,
      info.param2Range[1],
    ];

    param1Steps.forEach((p1, i) => {
      param2Steps.forEach((p2, j) => {
        variations.push({
          key: `${selectedFamily}-${i}-${j}`,
          config: {
            family: selectedFamily,
            param1: p1,
            param2: p2,
            hue: customConfig.hue,
            saturation: customConfig.saturation,
            speed: 0.5,
            invert: false,
          },
        });
      });
    });

    return variations;
  }, [selectedFamily, customConfig.hue, customConfig.saturation]);

  return (
    <div className="space-y-6 p-4">
      {/* Family Tabs */}
      <div className="flex flex-wrap gap-2">
        {(Object.keys(PATTERN_FAMILIES) as PatternFamily[]).map((family) => (
          <button
            key={family}
            onClick={() => setSelectedFamily(family)}
            className={`px-3 py-2 rounded text-sm font-medium transition-colors min-h-[44px] ${
              selectedFamily === family
                ? 'bg-cyan-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {density === 'compact'
              ? PATTERN_FAMILIES[family].name.split(' ')[0]
              : PATTERN_FAMILIES[family].name}
          </button>
        ))}
      </div>

      {/* Family Description */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h2 className="text-lg font-semibold">{familyInfo.name}</h2>
        <p className="text-gray-400 text-sm mt-1">{familyInfo.description}</p>
        {density !== 'compact' && (
          <div className="mt-2 flex gap-4 text-xs text-gray-500">
            <span>
              <strong className="text-gray-400">{familyInfo.param1Label}:</strong>{' '}
              {familyInfo.param1Range[0]} – {familyInfo.param1Range[1]}
            </span>
            <span>
              <strong className="text-gray-400">{familyInfo.param2Label}:</strong>{' '}
              {familyInfo.param2Range[0]} – {familyInfo.param2Range[1]}
            </span>
          </div>
        )}
      </div>

      {/* Color Presets */}
      <div className="flex gap-2 flex-wrap items-center">
        <span className="text-sm text-gray-400 mr-2">Color:</span>
        {HUE_PRESETS.map((preset) => (
          <button
            key={preset.name}
            onClick={() =>
              handleSelectVariation(
                { ...customConfig, hue: preset.hue, saturation: preset.saturation },
                selectedPreset ?? ''
              )
            }
            className={`px-3 py-2 rounded text-xs transition-colors min-h-[44px] ${
              customConfig.hue === preset.hue && customConfig.saturation === preset.saturation
                ? 'bg-gray-600 text-white'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
            }`}
            style={{
              borderLeft: `3px solid hsl(${preset.hue * 360}, ${preset.saturation * 100}%, 50%)`,
            }}
          >
            {density === 'compact' ? preset.name.charAt(0) : preset.name}
          </button>
        ))}
      </div>

      {/* Variation Grid */}
      <div
        className="grid gap-4 justify-center"
        style={{ gridTemplateColumns: `repeat(${gridCols}, ${tileSize}px)` }}
      >
        {familyVariations.map(({ key, config }) => (
          <div key={key} className="aspect-square">
            <PatternCanvas
              config={config}
              size={tileSize}
              selected={selectedPreset === key}
              onSelect={() => handleSelectVariation(config, key)}
              label={
                density === 'compact'
                  ? `${config.param1.toFixed(0)}/${config.param2.toFixed(1)}`
                  : `${familyInfo.param1Label}: ${config.param1.toFixed(1)} | ${familyInfo.param2Label}: ${config.param2.toFixed(1)}`
              }
              circadianModifier={circadianModifier}
            />
          </div>
        ))}
      </div>

      {/* Preset Gallery */}
      <div className="mt-8">
        <h3 className="text-lg font-semibold mb-4">Curated Presets</h3>
        <div
          className="grid gap-3"
          style={{ gridTemplateColumns: `repeat(${presetCols}, 1fr)` }}
        >
          {CURATED_PRESETS.map((key) => {
            const config = PATTERN_PRESETS[key];
            return (
              <div key={key} className="aspect-square">
                <PatternCanvas
                  config={config}
                  size={density === 'compact' ? 100 : 120}
                  selected={selectedPreset === key}
                  onSelect={() => handleSelectVariation(config, key)}
                  label={density === 'compact' ? key.split('-')[0] : key}
                  circadianModifier={circadianModifier}
                />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Explore View Component
// =============================================================================

function ExploreView({
  customConfig,
  updateConfig,
  circadianModifier,
  onFamilyChange,
}: {
  customConfig: PatternConfig;
  updateConfig: (updates: Partial<PatternConfig>) => void;
  circadianModifier: { warmth: number; brightness: number };
  onFamilyChange: (family: PatternFamily) => void;
}) {
  // Apply circadian modulation
  const adjustedConfig = useMemo(() => ({
    ...customConfig,
    hue: applyCircadianToHue(customConfig.hue, circadianModifier),
  }), [customConfig, circadianModifier]);

  return (
    <ElasticSplit
      direction="horizontal"
      defaultRatio={0.65}
      collapseAtDensity="compact"
      collapsePriority="secondary"
      minPaneSize={300}
      primary={
        <div className="h-full bg-gray-800 rounded-lg overflow-hidden">
          <Canvas camera={{ position: [0, 0, 1.2], fov: 45 }}>
            <PatternTile config={adjustedConfig} size={2.2} animate={true} />
          </Canvas>
        </div>
      }
      secondary={
        <div className="h-full bg-gray-800 rounded-lg overflow-y-auto">
          <ControlsPanel
            customConfig={customConfig}
            updateConfig={updateConfig}
            onFamilyChange={onFamilyChange}
          />
        </div>
      }
    />
  );
}

// =============================================================================
// Main Page
// =============================================================================

export function EmergenceDemo() {
  // Design polynomial for density-aware behavior
  const { state: designState } = useDesignPolynomial();
  const density = designState.density;

  // Circadian phase
  const circadian = useCircadian();

  // Selected family for exploration
  const [selectedFamily, setSelectedFamily] = useState<PatternFamily>('chladni');

  // Custom config for the detail view
  const [customConfig, setCustomConfig] = useState<PatternConfig>({
    family: 'chladni',
    param1: 4,
    param2: 5,
    hue: 0.55,
    saturation: 0.7,
    speed: 0.5,
    invert: false,
  });

  // Selected preset key (if any)
  const [selectedPreset, setSelectedPreset] = useState<string | null>('chladni-4-5');

  // View mode
  const [viewMode, setViewMode] = useState<'gallery' | 'explore'>('gallery');

  // Mobile drawer state
  const [controlsDrawerOpen, setControlsDrawerOpen] = useState(false);

  // Update custom config when selecting a variation
  const handleSelectVariation = useCallback((config: PatternConfig, key: string) => {
    setCustomConfig(config);
    setSelectedPreset(key);
    setSelectedFamily(config.family);
    setViewMode('explore');
  }, []);

  // Update config helper
  const updateConfig = useCallback((updates: Partial<PatternConfig>) => {
    setCustomConfig((prev) => ({ ...prev, ...updates }));
    setSelectedPreset(null);
  }, []);

  // Handle family change
  const handleFamilyChange = useCallback((family: PatternFamily) => {
    setSelectedFamily(family);
  }, []);

  // Floating actions for mobile
  const floatingActions = useMemo(() => [
    {
      id: 'gallery',
      icon: '🎨',
      label: 'Gallery',
      onClick: () => setViewMode('gallery'),
      isActive: viewMode === 'gallery',
    },
    {
      id: 'explore',
      icon: '🔍',
      label: 'Explore',
      onClick: () => setViewMode('explore'),
      isActive: viewMode === 'explore',
    },
    {
      id: 'controls',
      icon: '⚙️',
      label: 'Controls',
      onClick: () => setControlsDrawerOpen(true),
      variant: 'primary' as const,
    },
  ], [viewMode]);

  return (
    <div className="h-screen bg-gray-900 text-white flex flex-col overflow-hidden">
      {/* Header */}
      <header className="border-b border-gray-800 px-4 py-3 flex-shrink-0">
        <div className="max-w-7xl mx-auto flex items-center justify-between flex-wrap gap-2">
          <div>
            <h1 className="text-xl font-bold">Cymatics Design Experience</h1>
            {density !== 'compact' && (
              <p className="text-gray-400 text-sm">
                Explore pattern families. Click any tile to customize.
              </p>
            )}
          </div>
          <div className="flex items-center gap-4">
            {/* Circadian indicator - hidden on compact */}
            {density !== 'compact' && (
              <CircadianIndicator
                phase={circadian.phase}
                isOverridden={circadian.isOverridden}
                onOverride={(p) => p ? circadian.setOverride(p) : circadian.clearOverride()}
              />
            )}
            {/* View mode buttons - hidden on compact (use FABs instead) */}
            {density !== 'compact' && (
              <div className="flex gap-2">
                <button
                  onClick={() => setViewMode('gallery')}
                  className={`px-4 py-2 rounded text-sm font-medium transition-colors min-h-[44px] ${
                    viewMode === 'gallery'
                      ? 'bg-cyan-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Gallery
                </button>
                <button
                  onClick={() => setViewMode('explore')}
                  className={`px-4 py-2 rounded text-sm font-medium transition-colors min-h-[44px] ${
                    viewMode === 'explore'
                      ? 'bg-cyan-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Explore
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-auto relative">
        <div className="max-w-7xl mx-auto h-full">
          {viewMode === 'gallery' ? (
            <GalleryView
              selectedFamily={selectedFamily}
              setSelectedFamily={setSelectedFamily}
              customConfig={customConfig}
              handleSelectVariation={handleSelectVariation}
              selectedPreset={selectedPreset}
              circadianModifier={circadian.modifier}
              density={density}
            />
          ) : (
            <div className="h-full p-4">
              <ExploreView
                customConfig={customConfig}
                updateConfig={updateConfig}
                circadianModifier={circadian.modifier}
                onFamilyChange={handleFamilyChange}
              />
            </div>
          )}
        </div>

        {/* Floating Actions (compact mode only) */}
        {density === 'compact' && (
          <FloatingActions
            actions={floatingActions}
            position="bottom-right"
          />
        )}
      </main>

      {/* Footer - hidden on compact */}
      {density !== 'compact' && (
        <footer className="border-t border-gray-800 px-4 py-3 flex-shrink-0">
          <div className="max-w-7xl mx-auto text-center text-gray-500 text-sm">
            <p>
              <span className="text-cyan-400 font-medium">KGENTS Design Experience</span>
              {' • '}
              <span className="text-gray-400">
                9 families • {CURATED_PRESETS.length} presets • Circadian: {circadian.phase}
              </span>
            </p>
          </div>
        </footer>
      )}

      {/* Controls Drawer (compact mode) */}
      <BottomDrawer
        isOpen={controlsDrawerOpen}
        onClose={() => setControlsDrawerOpen(false)}
        title="Pattern Controls"
        maxHeightPercent={80}
      >
        <ControlsPanel
          customConfig={customConfig}
          updateConfig={updateConfig}
          onFamilyChange={handleFamilyChange}
        />
        <div className="p-4 border-t border-gray-700">
          <CircadianIndicator
            phase={circadian.phase}
            isOverridden={circadian.isOverridden}
            onOverride={(p) => p ? circadian.setOverride(p) : circadian.clearOverride()}
          />
        </div>
      </BottomDrawer>
    </div>
  );
}

export default EmergenceDemo;
