/**
 * CollaborationBuilder: UI for commissioning multiple artisans together.
 *
 * Features:
 * - Select 2+ artisans
 * - Choose collaboration mode (duet, relay, chorus)
 * - Enter request
 * - Watch combined creation
 *
 * Theme: Orisinal.com - gentle selection, clear feedback.
 */

import React, { useState } from 'react';
import type { Artisan, Piece } from '@/api/atelier';

interface CollaborationBuilderProps {
  artisans: Artisan[];
  onCollaborate: (
    artisans: string[],
    request: string,
    mode: string
  ) => Promise<Piece | null>;
  isLoading?: boolean;
}

type CollaborationMode = 'duet' | 'relay' | 'chorus';

const MODE_INFO: Record<CollaborationMode, { label: string; description: string }> = {
  duet: {
    label: 'Duet',
    description: 'Artisans take turns, building on each other.',
  },
  relay: {
    label: 'Relay',
    description: 'Each artisan hands off to the next.',
  },
  chorus: {
    label: 'Chorus',
    description: 'All artisans contribute simultaneously.',
  },
};

export function CollaborationBuilder({
  artisans,
  onCollaborate,
  isLoading = false,
}: CollaborationBuilderProps) {
  const [selectedArtisans, setSelectedArtisans] = useState<Set<string>>(new Set());
  const [mode, setMode] = useState<CollaborationMode>('duet');
  const [request, setRequest] = useState('');

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
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedArtisans.size < 2 || !request.trim()) return;
    await onCollaborate(Array.from(selectedArtisans), request.trim(), mode);
  };

  const canSubmit = selectedArtisans.size >= 2 && request.trim() && !isLoading;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Artisan Selection */}
      <div>
        <h3 className="text-sm font-medium text-stone-600 mb-3">
          Select Artisans <span className="text-stone-400">(2 or more)</span>
        </h3>
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
                <span className="ml-1.5 text-xs text-stone-400">
                  {artisan.specialty}
                </span>
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

      {/* Mode Selection */}
      <div>
        <h3 className="text-sm font-medium text-stone-600 mb-3">
          Collaboration Mode
        </h3>
        <div className="grid grid-cols-3 gap-3">
          {(Object.keys(MODE_INFO) as CollaborationMode[]).map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => setMode(m)}
              className={`
                p-3 rounded-lg text-left transition-all duration-200
                border
                ${
                  mode === m
                    ? 'bg-amber-50 border-amber-300'
                    : 'bg-white border-stone-200 hover:border-amber-200'
                }
              `}
            >
              <span
                className={`
                  text-sm font-medium
                  ${mode === m ? 'text-amber-800' : 'text-stone-700'}
                `}
              >
                {MODE_INFO[m].label}
              </span>
              <p className="mt-1 text-xs text-stone-400">
                {MODE_INFO[m].description}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Request Input */}
      <div>
        <label
          htmlFor="collab-request"
          className="block text-sm font-medium text-stone-600 mb-2"
        >
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
