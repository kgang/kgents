/**
 * EmergenceDemo - Cymatics Design Sampler
 *
 * A visual exploration of pattern families for cymatics visualization.
 * Shows many variations at once so the eye can find what it likes.
 *
 * Philosophy:
 *   "Don't tune blindly. Show everything. Let the eye choose."
 *
 * @see impl/claude/web/src/components/three/CymaticsSampler.tsx
 */

import { useState, useMemo, useCallback } from 'react';
import { Canvas } from '@react-three/fiber';

import {
  PatternTile,
  PATTERN_PRESETS,
  CURATED_PRESETS,
  type PatternConfig,
  type PatternFamily,
} from '../components/three/CymaticsSampler';

// =============================================================================
// Types
// =============================================================================

interface FamilyInfo {
  name: string;
  description: string;
  param1Label: string;
  param2Label: string;
  param1Range: [number, number];
  param2Range: [number, number];
}

// =============================================================================
// Constants
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

const HUE_PRESETS: { name: string; hue: number; saturation: number }[] = [
  { name: 'Cyan', hue: 0.55, saturation: 0.8 },
  { name: 'Amber', hue: 0.08, saturation: 0.8 },
  { name: 'Purple', hue: 0.75, saturation: 0.7 },
  { name: 'Teal', hue: 0.45, saturation: 0.7 },
  { name: 'Rose', hue: 0.95, saturation: 0.6 },
  { name: 'Gold', hue: 0.12, saturation: 0.9 },
  { name: 'Mono', hue: 0, saturation: 0 },
];

// =============================================================================
// Sub-Components
// =============================================================================

function PatternCanvas({
  config,
  size = 200,
  selected,
  onSelect,
  label,
}: {
  config: PatternConfig;
  size?: number;
  selected?: boolean;
  onSelect?: () => void;
  label?: string;
}) {
  return (
    <div
      className={`relative cursor-pointer transition-all duration-200 ${
        selected ? 'ring-2 ring-cyan-400 ring-offset-2 ring-offset-gray-900' : ''
      }`}
      onClick={onSelect}
      style={{ width: size, height: size }}
    >
      <Canvas
        camera={{ position: [0, 0, 1.2], fov: 45 }}
        style={{ background: '#111' }}
      >
        <PatternTile config={config} size={1.8} animate={true} />
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

// =============================================================================
// Main Page
// =============================================================================

export function EmergenceDemo() {
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

  // Get family info
  const familyInfo = PATTERN_FAMILIES[selectedFamily];

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

  // Update custom config when selecting a variation
  const handleSelectVariation = useCallback((config: PatternConfig, key: string) => {
    setCustomConfig(config);
    setSelectedPreset(key);
    setViewMode('explore');
  }, []);

  // Update config helper
  const updateConfig = useCallback((updates: Partial<PatternConfig>) => {
    setCustomConfig((prev) => ({ ...prev, ...updates }));
    setSelectedPreset(null);
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Cymatics Design Sampler</h1>
            <p className="text-gray-400 text-sm">
              Explore pattern families. Click any tile to customize.
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('gallery')}
              className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                viewMode === 'gallery'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Gallery
            </button>
            <button
              onClick={() => setViewMode('explore')}
              className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                viewMode === 'explore'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Explore
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6">
        {viewMode === 'gallery' ? (
          /* Gallery View - Show all pattern families */
          <div className="space-y-8">
            {/* Family Tabs */}
            <div className="flex flex-wrap gap-2">
              {(Object.keys(PATTERN_FAMILIES) as PatternFamily[]).map((family) => (
                <button
                  key={family}
                  onClick={() => setSelectedFamily(family)}
                  className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                    selectedFamily === family
                      ? 'bg-cyan-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {PATTERN_FAMILIES[family].name}
                </button>
              ))}
            </div>

            {/* Family Description */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h2 className="text-lg font-semibold">{familyInfo.name}</h2>
              <p className="text-gray-400 text-sm mt-1">{familyInfo.description}</p>
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
            </div>

            {/* Color Presets */}
            <div className="flex gap-2">
              <span className="text-sm text-gray-400 self-center mr-2">Color:</span>
              {HUE_PRESETS.map((preset) => (
                <button
                  key={preset.name}
                  onClick={() =>
                    updateConfig({ hue: preset.hue, saturation: preset.saturation })
                  }
                  className={`px-3 py-1 rounded text-xs transition-colors ${
                    customConfig.hue === preset.hue && customConfig.saturation === preset.saturation
                      ? 'bg-gray-600 text-white'
                      : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                  }`}
                  style={{
                    borderLeft: `3px solid hsl(${preset.hue * 360}, ${preset.saturation * 100}%, 50%)`,
                  }}
                >
                  {preset.name}
                </button>
              ))}
            </div>

            {/* 3x3 Variation Grid */}
            <div className="grid grid-cols-3 gap-4 max-w-3xl mx-auto">
              {familyVariations.map(({ key, config }) => (
                <div key={key} className="aspect-square">
                  <PatternCanvas
                    config={config}
                    size={240}
                    selected={selectedPreset === key}
                    onSelect={() => handleSelectVariation(config, key)}
                    label={`${familyInfo.param1Label}: ${config.param1.toFixed(1)} | ${familyInfo.param2Label}: ${config.param2.toFixed(1)}`}
                  />
                </div>
              ))}
            </div>

            {/* Preset Gallery */}
            <div className="mt-8">
              <h3 className="text-lg font-semibold mb-4">Curated Presets</h3>
              <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-3">
                {CURATED_PRESETS.map((key) => {
                  const config = PATTERN_PRESETS[key];
                  return (
                    <div key={key} className="aspect-square">
                      <PatternCanvas
                        config={config}
                        size={120}
                        selected={selectedPreset === key}
                        onSelect={() => handleSelectVariation(config, key)}
                        label={key}
                      />
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          /* Explore View - Detail controls */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Large Preview */}
            <div className="lg:col-span-2">
              <div className="aspect-square bg-gray-800 rounded-lg overflow-hidden">
                <Canvas camera={{ position: [0, 0, 1.2], fov: 45 }}>
                  <PatternTile config={customConfig} size={2.2} animate={true} />
                </Canvas>
              </div>
            </div>

            {/* Controls Panel */}
            <div className="bg-gray-800 rounded-lg p-4 space-y-6">
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
                  }}
                  className="w-full bg-gray-700 text-white rounded px-3 py-2"
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
                      className="w-8 h-8 rounded border-2 border-gray-600 hover:border-white transition-colors"
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
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={customConfig.invert}
                    onChange={(e) => updateConfig({ invert: e.target.checked })}
                    className="rounded"
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
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-800 px-6 py-4 mt-8">
        <div className="max-w-7xl mx-auto text-center text-gray-500 text-sm">
          <p>
            <span className="text-cyan-400 font-medium">KGENTS Design Palette</span>{' '}
            •{' '}
            <span className="text-gray-400">9 families • {CURATED_PRESETS.length} curated presets</span>
          </p>
          <p className="text-xs mt-1">
            See <code className="text-gray-400">docs/skills/cymatics-design-palette.md</code> for usage guidelines
          </p>
        </div>
      </footer>
    </div>
  );
}

export default EmergenceDemo;
