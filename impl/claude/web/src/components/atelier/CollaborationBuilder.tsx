/**
 * CollaborationBuilder: UI for commissioning multiple artisans together.
 *
 * Features:
 * - Select 2+ artisans
 * - Choose collaboration mode (duet, ensemble, refinement, chain)
 * - Quick presets for common collaborations
 * - Enter request
 * - Watch combined creation
 *
 * Theme: Orisinal.com - gentle selection, clear feedback.
 */

import React, { useState } from 'react';
import type { Artisan, Piece } from '@/api/atelier';

interface CollaborationBuilderProps {
  artisans: Artisan[];
  onCollaborate: (artisans: string[], request: string, mode: string) => Promise<Piece | null>;
  isLoading?: boolean;
}

type CollaborationMode = 'duet' | 'ensemble' | 'refinement' | 'chain';

const MODE_INFO: Record<
  CollaborationMode,
  { label: string; description: string; tooltip: string; icon: string }
> = {
  duet: {
    label: 'Duet',
    description: 'First creates, second transforms.',
    tooltip:
      'The first artisan creates a piece, then the second transforms or responds to it. Perfect for creative dialogue.',
    icon: '⟷',
  },
  ensemble: {
    label: 'Ensemble',
    description: 'All create in parallel, results merged.',
    tooltip:
      'All artisans create simultaneously from the same prompt. Their outputs are woven together into a unified piece.',
    icon: '◎',
  },
  refinement: {
    label: 'Refinement',
    description: 'First creates, second refines.',
    tooltip:
      'The first artisan drafts, the second polishes and improves. Use the same artisan twice for self-refinement.',
    icon: '↻',
  },
  chain: {
    label: 'Chain',
    description: 'Sequential pipeline through all.',
    tooltip:
      'Each artisan receives the previous output and transforms it. Creates an evolving piece through multiple perspectives.',
    icon: '→',
  },
};

// Quick preset collaborations
interface CollaborationPreset {
  name: string;
  description: string;
  artisans: string[];
  mode: CollaborationMode;
  sampleRequest: string;
}

const PRESETS: CollaborationPreset[] = [
  {
    name: 'Poetic Journey',
    description: 'Calligrapher writes, Cartographer maps the words',
    artisans: ['calligrapher', 'cartographer'],
    mode: 'duet',
    sampleRequest: 'a meditation on wandering',
  },
  {
    name: 'Self-Refinement',
    description: 'Same artisan refines their own work',
    artisans: ['calligrapher', 'calligrapher'],
    mode: 'refinement',
    sampleRequest: 'a perfect haiku about imperfection',
  },
  {
    name: 'Three Perspectives',
    description: 'Ensemble of three artisans on one theme',
    artisans: ['calligrapher', 'cartographer', 'correspondent'],
    mode: 'ensemble',
    sampleRequest: 'the feeling of coming home',
  },
];

export function CollaborationBuilder({
  artisans,
  onCollaborate,
  isLoading = false,
}: CollaborationBuilderProps) {
  const [selectedArtisans, setSelectedArtisans] = useState<Set<string>>(new Set());
  const [mode, setMode] = useState<CollaborationMode>('duet');
  const [request, setRequest] = useState('');
  const [hoveredMode, setHoveredMode] = useState<CollaborationMode | null>(null);
  const [showPresets, setShowPresets] = useState(true);

  const toggleArtisan = (name: string) => {
    setSelectedArtisans((prev) => {
      const next = new Set(prev);
      if (next.has(name)) {
        next.delete(name);
      } else {
        next.add(name);
      }
      return next;
    });
    // Hide presets once user starts custom selection
    setShowPresets(false);
  };

  const applyPreset = (preset: CollaborationPreset) => {
    setSelectedArtisans(new Set(preset.artisans));
    setMode(preset.mode);
    setRequest(preset.sampleRequest);
    setShowPresets(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedArtisans.size < 2 || !request.trim()) return;
    await onCollaborate(Array.from(selectedArtisans), request.trim(), mode);
  };

  const canSubmit = selectedArtisans.size >= 2 && request.trim() && !isLoading;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Quick Presets */}
      {showPresets && (
        <div>
          <h3 className="text-sm font-medium text-stone-600 mb-3">Quick Start</h3>
          <div className="grid gap-2">
            {PRESETS.map((preset) => (
              <button
                key={preset.name}
                type="button"
                onClick={() => applyPreset(preset)}
                className="
                  p-3 rounded-lg text-left transition-all duration-200
                  border border-stone-200 bg-white hover:border-amber-200
                  hover:bg-amber-50/50
                "
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-stone-700">{preset.name}</span>
                  <span className="text-xs text-stone-400 bg-stone-100 px-2 py-0.5 rounded">
                    {MODE_INFO[preset.mode].label}
                  </span>
                </div>
                <p className="mt-1 text-xs text-stone-400">{preset.description}</p>
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={() => setShowPresets(false)}
            className="mt-3 text-xs text-stone-400 hover:text-stone-600"
          >
            Or build a custom collaboration...
          </button>
        </div>
      )}

      {/* Artisan Selection */}
      {!showPresets && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-stone-600">
              Select Artisans <span className="text-stone-400">(2 or more)</span>
            </h3>
            <button
              type="button"
              onClick={() => setShowPresets(true)}
              className="text-xs text-amber-600 hover:text-amber-700"
            >
              Show presets
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {artisans.map((artisan) => {
              const isSelected = selectedArtisans.has(artisan.name);
              return (
                <button
                  key={artisan.name}
                  type="button"
                  onClick={() => toggleArtisan(artisan.name)}
                  className={`
                    px-3 py-2 rounded-lg text-sm transition-all duration-200
                    border
                    ${
                      isSelected
                        ? 'bg-amber-50 border-amber-300 text-amber-800'
                        : 'bg-white border-stone-200 text-stone-600 hover:border-amber-200'
                    }
                  `}
                >
                  <span className="font-medium">{artisan.name}</span>
                  <span className="ml-1.5 text-xs text-stone-400">{artisan.specialty}</span>
                </button>
              );
            })}
          </div>
          {selectedArtisans.size === 1 && (
            <p className="mt-2 text-xs text-amber-600">
              Select one more artisan for a collaboration.
            </p>
          )}
        </div>
      )}

      {/* Mode Selection */}
      {!showPresets && (
        <div>
          <h3 className="text-sm font-medium text-stone-600 mb-3">Collaboration Mode</h3>
          <div className="grid grid-cols-2 gap-3">
            {(Object.keys(MODE_INFO) as CollaborationMode[]).map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setMode(m)}
                onMouseEnter={() => setHoveredMode(m)}
                onMouseLeave={() => setHoveredMode(null)}
                className={`
                  p-3 rounded-lg text-left transition-all duration-200
                  border relative
                  ${
                    mode === m
                      ? 'bg-amber-50 border-amber-300'
                      : 'bg-white border-stone-200 hover:border-amber-200'
                  }
                `}
                title={MODE_INFO[m].tooltip}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">{MODE_INFO[m].icon}</span>
                  <span
                    className={`
                      text-sm font-medium
                      ${mode === m ? 'text-amber-800' : 'text-stone-700'}
                    `}
                  >
                    {MODE_INFO[m].label}
                  </span>
                </div>
                <p className="mt-1 text-xs text-stone-400">{MODE_INFO[m].description}</p>
              </button>
            ))}
          </div>
          {/* Expanded tooltip on hover */}
          {hoveredMode && (
            <div className="mt-2 p-3 rounded-lg bg-stone-50 border border-stone-100">
              <p className="text-xs text-stone-500">{MODE_INFO[hoveredMode].tooltip}</p>
            </div>
          )}
        </div>
      )}

      {/* Request Input */}
      <div>
        <label htmlFor="collab-request" className="block text-sm font-medium text-stone-600 mb-2">
          What should they create together?
        </label>
        <textarea
          id="collab-request"
          value={request}
          onChange={(e) => setRequest(e.target.value)}
          placeholder="a short story about an API that gained sentience..."
          rows={3}
          className="
            w-full px-4 py-3 rounded-lg border border-stone-200
            text-stone-700 placeholder:text-stone-300
            focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-300
            transition-all
          "
        />
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={!canSubmit}
        className={`
          w-full py-3 rounded-lg font-medium transition-all duration-200
          ${
            canSubmit
              ? 'bg-amber-400 text-amber-900 hover:bg-amber-500'
              : 'bg-stone-100 text-stone-400 cursor-not-allowed'
          }
        `}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="animate-spin">◐</span>
            Creating...
          </span>
        ) : (
          `Commission ${selectedArtisans.size} Artisans`
        )}
      </button>

      {/* Selected Summary */}
      {selectedArtisans.size >= 2 && (
        <p className="text-center text-xs text-stone-400">
          {Array.from(selectedArtisans).join(' + ')} · {MODE_INFO[mode].label}
        </p>
      )}
    </form>
  );
}

export default CollaborationBuilder;
