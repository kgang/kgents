/**
 * CommissionForm: Form for commissioning an artisan.
 *
 * Features:
 * - Artisan selection
 * - Request input
 * - Patron name (optional)
 * - Collaboration mode (optional)
 */

import React, { useState } from 'react';
import { ArtisanGrid } from './ArtisanGrid';

interface CommissionFormProps {
  /** Enable collaboration mode (multiple artisans) */
  collaborationMode?: boolean;
  /** Callback when commission is submitted */
  onSubmit: (data: { artisans: string[]; request: string; patron: string; mode?: string }) => void;
  /** Disable form during submission */
  disabled?: boolean;
}

const COLLABORATION_MODES = [
  { value: 'duet', label: 'Duet', description: 'First creates, second transforms' },
  { value: 'ensemble', label: 'Ensemble', description: 'All create in parallel, merged' },
  { value: 'refinement', label: 'Refinement', description: 'First creates, second refines' },
  { value: 'chain', label: 'Chain', description: 'Sequential pipeline' },
];

export function CommissionForm({
  collaborationMode = false,
  onSubmit,
  disabled = false,
}: CommissionFormProps) {
  const [selectedArtisans, setSelectedArtisans] = useState<string[]>([]);
  const [request, setRequest] = useState('');
  const [patron, setPatron] = useState('wanderer');
  const [mode, setMode] = useState('duet');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedArtisans.length === 0 || !request.trim()) return;

    onSubmit({
      artisans: selectedArtisans,
      request: request.trim(),
      patron: patron.trim() || 'wanderer',
      mode: collaborationMode ? mode : undefined,
    });
  };

  const canSubmit =
    !disabled &&
    selectedArtisans.length > 0 &&
    request.trim().length > 0 &&
    (!collaborationMode || selectedArtisans.length >= 2);

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Artisan Selection */}
      <div>
        <label className="block text-sm font-medium text-stone-600 mb-2">
          {collaborationMode ? 'Select artisans' : 'Choose an artisan'}
        </label>
        <ArtisanGrid
          multiSelect={collaborationMode}
          selected={selectedArtisans}
          onSelect={setSelectedArtisans}
          disabled={disabled}
        />
        {collaborationMode && selectedArtisans.length < 2 && (
          <p className="mt-2 text-xs text-amber-600">
            Select at least 2 artisans for collaboration
          </p>
        )}
      </div>

      {/* Collaboration Mode */}
      {collaborationMode && selectedArtisans.length >= 2 && (
        <div>
          <label className="block text-sm font-medium text-stone-600 mb-2">
            Collaboration mode
          </label>
          <div className="grid grid-cols-2 gap-2">
            {COLLABORATION_MODES.map((m) => (
              <button
                key={m.value}
                type="button"
                onClick={() => setMode(m.value)}
                disabled={disabled}
                className={`
                  p-3 rounded-lg border text-left transition-all
                  ${
                    mode === m.value
                      ? 'border-amber-400 bg-amber-50/50'
                      : 'border-stone-200 hover:border-stone-300'
                  }
                `}
              >
                <div className="font-medium text-sm text-stone-700">{m.label}</div>
                <div className="text-xs text-stone-400 mt-0.5">{m.description}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Request Input */}
      <div>
        <label className="block text-sm font-medium text-stone-600 mb-2">Your request</label>
        <textarea
          value={request}
          onChange={(e) => setRequest(e.target.value)}
          disabled={disabled}
          placeholder="a haiku about persistence..."
          className="
            w-full px-4 py-3 rounded-lg border border-stone-200
            focus:border-amber-400 focus:ring-1 focus:ring-amber-400
            placeholder:text-stone-300 text-stone-700
            resize-none transition-colors
          "
          rows={3}
        />
      </div>

      {/* Patron Name */}
      <div>
        <label className="block text-sm font-medium text-stone-600 mb-2">
          Your name <span className="text-stone-400">(optional)</span>
        </label>
        <input
          type="text"
          value={patron}
          onChange={(e) => setPatron(e.target.value)}
          disabled={disabled}
          placeholder="wanderer"
          className="
            w-full px-4 py-2 rounded-lg border border-stone-200
            focus:border-amber-400 focus:ring-1 focus:ring-amber-400
            placeholder:text-stone-300 text-stone-700
            transition-colors
          "
        />
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={!canSubmit}
        className={`
          w-full py-3 rounded-lg font-medium transition-all
          ${
            canSubmit
              ? 'bg-amber-500 text-white hover:bg-amber-600 active:bg-amber-700'
              : 'bg-stone-100 text-stone-400 cursor-not-allowed'
          }
        `}
      >
        {collaborationMode ? 'Begin Collaboration' : 'Commission'}
      </button>
    </form>
  );
}

export default CommissionForm;
