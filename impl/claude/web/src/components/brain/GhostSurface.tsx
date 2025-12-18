/**
 * GhostSurface - LLM-Powered Serendipitous Memory Recall
 *
 * Surfaces relevant memories based on context with optional LLM explanation.
 * Uses AGENTESE self.memory.surface endpoint (will be enhanced to self.memory.ghost).
 *
 * "Memories float up from the void when the context calls them."
 *
 * Living Earth aesthetic: bark tones for ghost state, honey glow for surfaced.
 *
 * @see spec/protocols/2d-renaissance.md - Phase 4: Brain2D
 */

import { useState, useCallback } from 'react';
import { Sparkles, Loader2, AlertCircle, ExternalLink } from 'lucide-react';
import { Breathe, PopOnMount } from '@/components/joy';
import { brainApi } from '@/api/client';

// =============================================================================
// Types
// =============================================================================

export interface GhostSurfaceProps {
  /** Callback when a surfaced crystal is selected */
  onSurface?: (crystalId: string) => void;
  /** Compact mode for mobile/drawer */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

type SurfaceState = 'idle' | 'loading' | 'surfaced' | 'empty' | 'error';

interface SurfaceResult {
  crystal_id: string;
  content: string;
  summary: string;
  similarity: number;
}

// =============================================================================
// Component
// =============================================================================

export function GhostSurface({ onSurface, compact = false, className = '' }: GhostSurfaceProps) {
  const [context, setContext] = useState('');
  const [entropy, setEntropy] = useState(0.5);
  const [state, setState] = useState<SurfaceState>('idle');
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SurfaceResult | null>(null);

  const handleSurface = useCallback(async () => {
    setState('loading');
    setError(null);
    setResult(null);

    try {
      // Call AGENTESE ghost endpoint (wraps surface with optional LLM explanation)
      // BrainGhostResponse has { surfaced: GhostMemory[], context, status, count }
      const response = await brainApi.ghost({
        context: context.trim() || 'recent thoughts',
        limit: 1,
      });

      if (response.surfaced && response.surfaced.length > 0) {
        const firstGhost = response.surfaced[0];
        setState('surfaced');
        setResult({
          crystal_id: firstGhost.concept_id,
          content: firstGhost.content || '',
          summary: firstGhost.content?.slice(0, 100) || 'Ghost memory surfaced',
          similarity: firstGhost.relevance || 0.5,
        });
      } else {
        setState('empty');
      }
    } catch (err) {
      setState('error');
      setError(err instanceof Error ? err.message : 'Failed to surface memories');
    }
  }, [context, entropy]);

  const handleSelectCrystal = useCallback(() => {
    if (result) {
      onSurface?.(result.crystal_id);
    }
  }, [result, onSurface]);

  const handleReset = useCallback(() => {
    setState('idle');
    setResult(null);
    setError(null);
  }, []);

  const isLoading = state === 'loading';

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Context Input */}
      <div>
        <label
          htmlFor="ghost-context"
          className={`block text-gray-400 mb-1 ${compact ? 'text-xs' : 'text-sm'}`}
        >
          Context
          <span className="text-gray-600 ml-1">(optional)</span>
        </label>
        <input
          id="ghost-context"
          type="text"
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder="What are you thinking about?"
          disabled={isLoading}
          className={`
            w-full px-3 py-2 bg-[#1a1a1a] border border-gray-700 rounded-lg
            text-white placeholder-gray-500
            focus:outline-none focus:border-[#4A3728] transition-colors
            disabled:opacity-50 disabled:cursor-not-allowed
            ${compact ? 'text-sm' : 'text-base'}
          `}
        />
      </div>

      {/* Entropy Slider */}
      {!compact && (
        <div>
          <div className="flex justify-between items-center mb-1">
            <label htmlFor="ghost-entropy" className="text-sm text-gray-400">
              Entropy
            </label>
            <span className="text-xs text-gray-500">
              {entropy < 0.3 ? 'Precise' : entropy < 0.7 ? 'Balanced' : 'Serendipitous'}
            </span>
          </div>
          <input
            id="ghost-entropy"
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={entropy}
            onChange={(e) => setEntropy(parseFloat(e.target.value))}
            disabled={isLoading}
            className="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-[#D4A574]"
          />
        </div>
      )}

      {/* Surface Button */}
      <button
        onClick={handleSurface}
        disabled={isLoading}
        className={`
          w-full flex items-center justify-center gap-2 rounded-lg font-medium
          bg-[#4A3728] hover:bg-[#5A4738] text-[#E8C4A0]
          transition-all duration-200
          disabled:opacity-50 disabled:cursor-not-allowed
          ${compact ? 'py-2 text-sm' : 'py-2.5 text-base'}
        `}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Surfacing...
          </>
        ) : (
          <>
            <Sparkles className="w-4 h-4" />
            Surface Memory
          </>
        )}
      </button>

      {/* Error State */}
      {state === 'error' && error && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-900/20 px-3 py-2 rounded-lg">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Empty State */}
      {state === 'empty' && (
        <div className="text-center py-4 text-gray-500">
          <Sparkles className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No memories surfaced</p>
          <p className="text-xs mt-1">Try a different context or increase entropy</p>
        </div>
      )}

      {/* Surfaced Result */}
      {state === 'surfaced' && result && (
        <PopOnMount scale={1.02} duration={300}>
          <div className="bg-[#2a2a2a] border border-[#4A3728] rounded-lg p-4 space-y-3">
            {/* Header */}
            <div className="flex items-start justify-between gap-2">
              <Breathe intensity={0.3} speed="slow">
                <Sparkles className="w-5 h-5 text-[#E8C4A0]" />
              </Breathe>
              <div className="flex-1">
                <h4 className="font-medium text-[#E8C4A0] text-sm">Memory Surfaced</h4>
                <p className="text-xs text-gray-500 font-mono">
                  {result.crystal_id.slice(0, 12)}...
                </p>
              </div>
              <SimilarityBadge similarity={result.similarity} />
            </div>

            {/* Summary */}
            <p className={`text-gray-300 ${compact ? 'text-sm' : 'text-base'}`}>
              {result.summary || result.content.slice(0, 150)}
              {result.content.length > 150 && '...'}
            </p>

            {/* Actions */}
            <div className="flex gap-2">
              <button
                onClick={handleSelectCrystal}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-[#4A6B4A] hover:bg-[#5A7B5A] rounded text-white text-sm transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                View Crystal
              </button>
              <button
                onClick={handleReset}
                className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-gray-300 text-sm transition-colors"
              >
                Surface Again
              </button>
            </div>
          </div>
        </PopOnMount>
      )}
    </div>
  );
}

// =============================================================================
// Sub-Components
// =============================================================================

interface SimilarityBadgeProps {
  similarity: number;
}

function SimilarityBadge({ similarity }: SimilarityBadgeProps) {
  const percentage = Math.round(similarity * 100);
  const color =
    similarity > 0.7
      ? 'text-green-400 bg-green-900/30'
      : similarity > 0.4
        ? 'text-[#D4A574] bg-[#D4A574]/20'
        : 'text-gray-400 bg-gray-700/50';

  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${color}`}>{percentage}% match</span>
  );
}

export default GhostSurface;
