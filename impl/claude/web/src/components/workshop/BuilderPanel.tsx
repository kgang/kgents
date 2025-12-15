import { useState } from 'react';
import { useWorkshopStore, selectSelectedBuilderData } from '@/stores/workshopStore';
import { useUserStore, selectCanInhabit } from '@/stores/userStore';
import { workshopApi } from '@/api/client';
import { BUILDER_COLORS, BUILDER_ICONS } from '@/api/types';
import type { BuilderArchetype } from '@/api/types';
import { cn } from '@/lib/utils';

/**
 * BuilderPanel displays detailed builder information in the workshop sidebar.
 */
export function BuilderPanel() {
  const { selectedBuilder, selectBuilder, builders } = useWorkshopStore();
  const selectedBuilderData = useWorkshopStore(selectSelectedBuilderData());
  const { tier: _tier } = useUserStore(); // Reserved for future tier-specific UI
  const canInhabit = useUserStore(selectCanInhabit());

  const [whisperInput, setWhisperInput] = useState('');
  const [isWhispering, setIsWhispering] = useState(false);
  const [whisperResponse, setWhisperResponse] = useState<string | null>(null);

  const handleWhisper = async () => {
    if (!selectedBuilder || !whisperInput.trim() || isWhispering) return;

    setIsWhispering(true);
    try {
      const response = await workshopApi.whisper(selectedBuilder, whisperInput.trim());
      setWhisperResponse(response.data.response);
      setWhisperInput('');
      // Clear response after 3 seconds
      setTimeout(() => setWhisperResponse(null), 3000);
    } catch (err) {
      console.error('Failed to whisper:', err);
    } finally {
      setIsWhispering(false);
    }
  };

  if (!selectedBuilder || !selectedBuilderData) {
    return (
      <div className="p-6 text-center text-gray-500">
        <div className="text-4xl mb-4">👆</div>
        <p>Click a builder on the canvas to see their details</p>
        <div className="mt-6 space-y-2">
          <p className="text-sm text-gray-600">Available Builders:</p>
          <div className="flex flex-wrap gap-2 justify-center">
            {builders.map((b) => (
              <button
                key={b.archetype}
                onClick={() => selectBuilder(b.archetype)}
                className={cn(
                  'px-3 py-1 rounded-full text-sm transition-colors',
                  b.is_active
                    ? 'bg-green-600/30 text-green-300'
                    : 'bg-town-surface/50 text-gray-400 hover:bg-town-surface'
                )}
              >
                {BUILDER_ICONS[b.archetype as BuilderArchetype]} {b.archetype}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const color = BUILDER_COLORS[selectedBuilderData.archetype as BuilderArchetype];
  const icon = BUILDER_ICONS[selectedBuilderData.archetype as BuilderArchetype];

  return (
    <div className="p-4 space-y-4 overflow-y-auto h-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{icon}</span>
          <div>
            <h2 className="text-xl font-bold">{selectedBuilderData.name}</h2>
            <p className="text-sm font-medium" style={{ color }}>
              {selectedBuilderData.archetype}
            </p>
          </div>
        </div>
        <button onClick={() => selectBuilder(null)} className="text-gray-400 hover:text-white">
          ✕
        </button>
      </div>

      {/* Status Section */}
      <div className="bg-town-surface/30 rounded-lg p-4 border border-town-accent/20">
        <h3 className="font-medium mb-3 flex items-center gap-2">
          <span>📊</span> Status
        </h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">Phase</span>
            <span className={getPhaseTextColor(selectedBuilderData.phase)}>
              {selectedBuilderData.phase}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Active</span>
            <span className={selectedBuilderData.is_active ? 'text-green-400' : 'text-gray-500'}>
              {selectedBuilderData.is_active ? 'Yes' : 'No'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">In Specialty</span>
            <span
              className={selectedBuilderData.is_in_specialty ? 'text-purple-400' : 'text-gray-500'}
            >
              {selectedBuilderData.is_in_specialty ? 'Yes' : 'No'}
            </span>
          </div>
        </div>
      </div>

      {/* Specialty Section */}
      <div className="bg-town-surface/30 rounded-lg p-4 border border-town-accent/20">
        <h3 className="font-medium mb-3 flex items-center gap-2">
          <span>⭐</span> Specialty
        </h3>
        <p className="text-sm text-gray-300">
          {getBuilderSpecialty(selectedBuilderData.archetype as BuilderArchetype)}
        </p>
      </div>

      {/* Whisper Response */}
      {whisperResponse && (
        <div className="bg-purple-900/30 rounded-lg p-4 border border-purple-500/20">
          <p className="text-sm text-purple-300 italic">{whisperResponse}</p>
        </div>
      )}

      {/* Whisper Input */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-400">
          Whisper to {selectedBuilderData.name}
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={whisperInput}
            onChange={(e) => setWhisperInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleWhisper()}
            placeholder="Say something..."
            className="flex-1 bg-town-surface border border-town-accent/30 rounded px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
          />
          <button
            onClick={handleWhisper}
            disabled={!whisperInput.trim() || isWhispering}
            className="px-3 py-2 bg-purple-600/30 text-purple-300 rounded text-sm hover:bg-purple-600/50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isWhispering ? '...' : '💬'}
          </button>
        </div>
      </div>

      {/* INHABIT Button (Future) */}
      <div className="pt-4 border-t border-town-accent/30">
        {canInhabit ? (
          <button
            disabled
            className="w-full py-2 px-4 bg-town-highlight/50 rounded-lg text-center font-medium opacity-50 cursor-not-allowed"
          >
            🎭 INHABIT (Coming Soon)
          </button>
        ) : (
          <p className="text-xs text-center text-gray-500">
            Upgrade to RESIDENT to unlock INHABIT mode
          </p>
        )}
      </div>
    </div>
  );
}

function getPhaseTextColor(phase: string): string {
  switch (phase) {
    case 'EXPLORING':
      return 'text-green-400';
    case 'DESIGNING':
      return 'text-purple-400';
    case 'PROTOTYPING':
      return 'text-amber-400';
    case 'REFINING':
      return 'text-blue-400';
    case 'INTEGRATING':
      return 'text-pink-400';
    default:
      return 'text-gray-400';
  }
}

function getBuilderSpecialty(archetype: BuilderArchetype): string {
  switch (archetype) {
    case 'Scout':
      return 'Exploration & Research — Discovers possibilities, maps the landscape, finds the path forward.';
    case 'Sage':
      return 'Architecture & Design — Thinks through structure, considers patterns, creates blueprints.';
    case 'Spark':
      return 'Prototyping & Experimentation — Tries new ideas, builds rough cuts, embraces iteration.';
    case 'Steady':
      return 'Refinement & Quality — Polishes work, adds tests, ensures reliability.';
    case 'Sync':
      return 'Integration & Coordination — Connects pieces, merges components, ships the final product.';
    default:
      return 'Unknown specialty';
  }
}

export default BuilderPanel;
