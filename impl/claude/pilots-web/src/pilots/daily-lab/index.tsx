/**
 * Daily Lab Pilot - Trail to Crystal
 *
 * "Turn your day into proof of intention."
 *
 * This pilot implements the Daily Lab experience:
 * - Quick mark capture (< 5 seconds)
 * - Trail visualization with neutral gap handling
 * - Crystallization ritual at day's end
 *
 * Design Philosophy (from PROTO_SPEC):
 * - QA-1: Lighter than a to-do list
 * - QA-2: Reward honest gaps
 * - QA-3: Witnessed, not surveilled
 * - QA-4: Crystal = memory artifact
 * - QA-5/6/7: Contract coherence (all types from shared-primitives)
 *
 * Anti-Patterns Avoided:
 * - NO streak counters
 * - NO productivity scores
 * - NO "untracked time" shaming
 * - NO gamification
 * - NO hustle language
 *
 * @see pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md
 */

import { useState, useEffect, useCallback } from 'react';
import type {
  CaptureRequest,
  CaptureResponse,
  TrailMark,
  TimeGap,
  Crystal,
  CompressionHonesty,
} from '@kgents/shared-primitives';
import { DayView } from './components/DayView';
import {
  getTrail,
  captureMark,
  crystallizeDay,
  exportDay,
  WitnessApiError,
} from '@/api/witness';

// =============================================================================
// Types
// =============================================================================

interface DailyLabState {
  marks: TrailMark[];
  gaps: TimeGap[];
  crystal?: Crystal;
  crystalHonesty?: CompressionHonesty;
  reviewPrompt?: string;
  isLoading: boolean;
  error?: string;
}

// =============================================================================
// Component
// =============================================================================

/**
 * DailyLabPilot
 *
 * Main pilot page for Daily Lab. Manages state and API interactions.
 *
 * @example
 * // In router:
 * <Route path="/pilots/daily-lab" element={<DailyLabPilot />} />
 */
export function DailyLabPilot() {
  const [date] = useState(() => new Date());
  const [state, setState] = useState<DailyLabState>({
    marks: [],
    gaps: [],
    isLoading: true,
  });

  // Fetch trail on mount
  useEffect(() => {
    const fetchTrail = async () => {
      setState((prev) => ({ ...prev, isLoading: true, error: undefined }));

      try {
        const trail = await getTrail();

        setState((prev) => ({
          ...prev,
          marks: trail.marks,
          gaps: trail.gaps,
          reviewPrompt: trail.review_prompt,
          isLoading: false,
        }));
      } catch (error) {
        const message =
          error instanceof WitnessApiError
            ? error.detail
            : error instanceof Error
              ? error.message
              : 'Failed to load trail';

        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: message,
        }));
      }
    };

    fetchTrail();
  }, []);

  // Handle mark capture
  const handleCapture = useCallback(
    async (request: CaptureRequest): Promise<CaptureResponse | void> => {
      try {
        const response = await captureMark(request);

        // Add the new mark to the trail immediately (optimistic update)
        const newMark: TrailMark = {
          mark_id: response.mark_id,
          content: response.content,
          tags: response.tag ? [response.tag] : [],
          timestamp: response.timestamp,
        };

        setState((prev) => ({
          ...prev,
          marks: [...prev.marks, newMark],
          // Recalculate gaps would happen on next fetch
        }));

        return response;
      } catch (error) {
        const message =
          error instanceof WitnessApiError
            ? error.detail
            : error instanceof Error
              ? error.message
              : 'Failed to capture mark';

        // Show error briefly, then clear
        setState((prev) => ({ ...prev, error: message }));
        setTimeout(() => {
          setState((prev) => ({ ...prev, error: undefined }));
        }, 5000);

        throw error;
      }
    },
    []
  );

  // Handle crystallization
  const handleCrystallize = useCallback(async () => {
    setState((prev) => ({ ...prev, error: undefined }));

    try {
      const result = await crystallizeDay();

      if (result.success && result.crystal_id) {
        // Create crystal object from response
        const crystal: Crystal = {
          crystal_id: result.crystal_id,
          insight: result.insight ?? result.summary ?? 'No insight generated',
          significance: result.significance ?? '',
          disclosure: result.disclosure,
          level: 'day',
          timestamp: new Date().toISOString(),
          confidence: 0.8, // Default confidence
        };

        const honesty: CompressionHonesty | undefined = result.compression_honesty
          ? {
              dropped_count: result.compression_honesty.dropped_count,
              dropped_tags: result.compression_honesty.dropped_tags,
              dropped_summaries: result.compression_honesty.dropped_summaries,
              galois_loss: result.compression_honesty.galois_loss,
            }
          : undefined;

        setState((prev) => ({
          ...prev,
          crystal,
          crystalHonesty: honesty,
        }));
      } else {
        setState((prev) => ({
          ...prev,
          error: result.disclosure || 'Not enough marks to crystallize yet.',
        }));
      }
    } catch (error) {
      const message =
        error instanceof WitnessApiError
          ? error.detail
          : error instanceof Error
            ? error.message
            : 'Crystallization failed';

      setState((prev) => ({ ...prev, error: message }));
    }
  }, []);

  // Handle export
  const handleExport = useCallback(async (format: 'markdown' | 'json') => {
    try {
      const result = await exportDay({ format });

      // Create a download
      const blob = new Blob([result.content], {
        type: format === 'json' ? 'application/json' : 'text/markdown',
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `daily-lab-${result.date}.${format === 'json' ? 'json' : 'md'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      const message =
        error instanceof WitnessApiError
          ? error.detail
          : error instanceof Error
            ? error.message
            : 'Export failed';

      setState((prev) => ({ ...prev, error: message }));
    }
  }, []);

  // Handle crystal share (copy to clipboard)
  const handleShareCrystal = useCallback(async (crystal: Crystal) => {
    try {
      const text = `Daily Crystal (${new Date(crystal.timestamp).toLocaleDateString()})

${crystal.insight}

Why this matters: ${crystal.significance}

---
Generated by Daily Lab`;

      await navigator.clipboard.writeText(text);

      // Could add a toast notification here
      console.log('Crystal copied to clipboard');
    } catch (error) {
      console.error('Failed to copy crystal:', error);
    }
  }, []);

  return (
    <DayView
      date={date}
      marks={state.marks}
      gaps={state.gaps}
      crystal={state.crystal}
      crystalHonesty={state.crystalHonesty}
      isLoading={state.isLoading}
      error={state.error}
      onCapture={handleCapture}
      onCrystallize={handleCrystallize}
      onExport={handleExport}
      onShareCrystal={handleShareCrystal}
      reviewPrompt={state.reviewPrompt}
    />
  );
}

export default DailyLabPilot;
