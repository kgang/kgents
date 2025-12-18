/**
 * CaptureForm - Memory Capture with Tags
 *
 * Allows users to capture new memories to the Brain with optional tags.
 * Calls AGENTESE self.memory.capture endpoint.
 *
 * Living Earth aesthetic: sage success state, amber loading, organic animations.
 *
 * @see spec/protocols/2d-renaissance.md - Phase 4: Brain2D
 */

import { useState, useCallback } from 'react';
import { Sparkles, Tag, Loader2, Check, AlertCircle } from 'lucide-react';
import { celebrate } from '@/components/joy';
import { brainApi } from '@/api/client';
import type { SelfMemoryCaptureResponse } from '@/api/types';

// =============================================================================
// Types
// =============================================================================

export interface CaptureFormProps {
  /** Callback after successful capture */
  onCapture?: (result: SelfMemoryCaptureResponse) => void;
  /** Default tags to include */
  defaultTags?: string[];
  /** Compact mode for mobile/drawer */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

type CaptureState = 'idle' | 'loading' | 'success' | 'error';

// =============================================================================
// Component
// =============================================================================

export function CaptureForm({
  onCapture,
  defaultTags = [],
  compact = false,
  className = '',
}: CaptureFormProps) {
  const [content, setContent] = useState('');
  const [tagsInput, setTagsInput] = useState(defaultTags.join(', '));
  const [state, setState] = useState<CaptureState>('idle');
  const [error, setError] = useState<string | null>(null);
  const [lastCapture, setLastCapture] = useState<SelfMemoryCaptureResponse | null>(null);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      if (!content.trim()) {
        setError('Content is required');
        return;
      }

      setState('loading');
      setError(null);

      try {
        // Parse tags from comma-separated input
        const tags = tagsInput
          .split(',')
          .map((t) => t.trim().toLowerCase())
          .filter((t) => t.length > 0);

        // Call AGENTESE capture endpoint via brainApi
        const result = (await brainApi.capture({
          content: content.trim(),
          tags,
          source_type: 'web-capture',
        })) as SelfMemoryCaptureResponse;

        // Success!
        setState('success');
        setLastCapture(result);

        // Celebrate with joy animation
        celebrate({ intensity: 'normal' });

        // Clear form after short delay
        setTimeout(() => {
          setContent('');
          setTagsInput('');
          setState('idle');
          onCapture?.(result);
        }, 1500);
      } catch (err) {
        setState('error');
        setError(err instanceof Error ? err.message : 'Failed to capture memory');
      }
    },
    [content, tagsInput, onCapture]
  );

  const isDisabled = state === 'loading' || state === 'success';

  return (
    <form onSubmit={handleSubmit} className={`space-y-3 ${className}`}>
      {/* Content Input */}
      <div>
        <label
          htmlFor="capture-content"
          className={`block text-gray-400 mb-1 ${compact ? 'text-xs' : 'text-sm'}`}
        >
          Memory Content
        </label>
        <textarea
          id="capture-content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="What would you like to remember?"
          disabled={isDisabled}
          rows={compact ? 2 : 3}
          className={`
            w-full px-3 py-2 bg-[#1a1a1a] border border-gray-700 rounded-lg
            text-white placeholder-gray-500 resize-none
            focus:outline-none focus:border-[#4A6B4A] transition-colors
            disabled:opacity-50 disabled:cursor-not-allowed
            ${compact ? 'text-sm' : 'text-base'}
          `}
        />
      </div>

      {/* Tags Input */}
      <div>
        <label
          htmlFor="capture-tags"
          className={`flex items-center gap-1 text-gray-400 mb-1 ${compact ? 'text-xs' : 'text-sm'}`}
        >
          <Tag className="w-3 h-3" />
          Tags
          <span className="text-gray-600">(comma-separated)</span>
        </label>
        <input
          id="capture-tags"
          type="text"
          value={tagsInput}
          onChange={(e) => setTagsInput(e.target.value)}
          placeholder="category, project, idea"
          disabled={isDisabled}
          className={`
            w-full px-3 py-2 bg-[#1a1a1a] border border-gray-700 rounded-lg
            text-white placeholder-gray-500
            focus:outline-none focus:border-[#4A6B4A] transition-colors
            disabled:opacity-50 disabled:cursor-not-allowed
            ${compact ? 'text-sm' : 'text-base'}
          `}
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {/* Success Message */}
      {state === 'success' && lastCapture && (
        <div className="flex items-center gap-2 text-green-400 text-sm bg-green-900/20 px-3 py-2 rounded-lg">
          <Check className="w-4 h-4" />
          <span>Captured: {lastCapture.summary || lastCapture.crystal_id.slice(0, 8)}</span>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isDisabled || !content.trim()}
        className={`
          w-full flex items-center justify-center gap-2 rounded-lg font-medium
          transition-all duration-200
          ${
            state === 'success'
              ? 'bg-green-600 text-white'
              : state === 'loading'
                ? 'bg-[#D4A574] text-white'
                : 'bg-[#4A6B4A] hover:bg-[#5A7B5A] text-white'
          }
          disabled:opacity-50 disabled:cursor-not-allowed
          ${compact ? 'py-2 text-sm' : 'py-2.5 text-base'}
        `}
      >
        {state === 'loading' ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Crystallizing...
          </>
        ) : state === 'success' ? (
          <>
            <Check className="w-4 h-4" />
            Captured!
          </>
        ) : (
          <>
            <Sparkles className="w-4 h-4" />
            Capture Memory
          </>
        )}
      </button>
    </form>
  );
}

export default CaptureForm;
