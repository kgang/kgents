/**
 * useCircadian - Hook for circadian phase and warmth data.
 *
 * CLI v7 Phase 5: Collaborative Canvas.
 *
 * Pattern #11: Circadian Modulation
 * Adjusts UI warmth and tempo based on time of day.
 *
 * Evening/night sessions are warmer (amber tones).
 * Morning sessions are cooler and more energetic.
 *
 * Voice Anchor:
 * "The persona is a garden, not a museum."
 */

import { useState, useEffect, useCallback } from 'react';
import { useAgentese } from './useAgentesePath';

// =============================================================================
// Types
// =============================================================================

export interface CircadianData {
  /** Current circadian phase name */
  phase: string;
  /** Animation tempo modifier (0.3-1.0) */
  tempo_modifier: number;
  /** Color warmth (0.0-1.0, higher = warmer) */
  warmth: number;
  /** Current hour (0-23) */
  hour: number;
}

export interface UseCircadianReturn {
  /** Circadian phase data */
  data: CircadianData | null;
  /** Whether data is loading */
  isLoading: boolean;
  /** Error if any */
  error: Error | null;
  /** CSS custom properties for circadian styling */
  cssVars: Record<string, string>;
  /** Background gradient with warmth applied */
  backgroundStyle: React.CSSProperties;
  /** Refetch circadian data */
  refetch: () => Promise<void>;
}

// =============================================================================
// Constants
// =============================================================================

// Warmth to color mapping (amber overlay intensity)
const WARMTH_COLORS = {
  cold: 'rgba(59, 130, 246, 0.05)', // blue tint
  neutral: 'rgba(0, 0, 0, 0)',
  warm: 'rgba(251, 191, 36, 0.08)', // amber tint
  hot: 'rgba(251, 146, 60, 0.12)', // orange tint
};

// =============================================================================
// Helper Functions
// =============================================================================

function getWarmthColor(warmth: number): string {
  if (warmth < 0.3) return WARMTH_COLORS.cold;
  if (warmth < 0.5) return WARMTH_COLORS.neutral;
  if (warmth < 0.7) return WARMTH_COLORS.warm;
  return WARMTH_COLORS.hot;
}

function generateCssVars(data: CircadianData): Record<string, string> {
  return {
    '--circadian-warmth': String(data.warmth),
    '--circadian-tempo': String(data.tempo_modifier),
    '--circadian-warmth-color': getWarmthColor(data.warmth),
    '--circadian-animation-speed': `${1 / data.tempo_modifier}s`,
  };
}

function generateBackgroundStyle(data: CircadianData): React.CSSProperties {
  const warmthColor = getWarmthColor(data.warmth);

  // Create a gradient overlay based on warmth
  // Evening: warm amber overlay
  // Morning: cool blue tint
  // Night: deep purple-blue
  return {
    background: `
      linear-gradient(
        to bottom,
        ${warmthColor},
        transparent 30%
      ),
      linear-gradient(
        135deg,
        rgb(17, 24, 39) 0%,
        rgb(31, 41, 55) 100%
      )
    `,
    transition: 'background 2s ease-out',
  };
}

// Client-side circadian calculation (fallback when API unavailable)
function calculateClientCircadian(): CircadianData {
  const hour = new Date().getHours();

  // Phase determination
  let phase: string;
  let tempo_modifier: number;
  let warmth: number;

  if (hour >= 5 && hour < 9) {
    phase = 'DAWN';
    tempo_modifier = 0.6;
    warmth = 0.8;
  } else if (hour >= 9 && hour < 12) {
    phase = 'MORNING';
    tempo_modifier = 1.0;
    warmth = 0.4;
  } else if (hour >= 12 && hour < 14) {
    phase = 'NOON';
    tempo_modifier = 0.9;
    warmth = 0.3;
  } else if (hour >= 14 && hour < 17) {
    phase = 'AFTERNOON';
    tempo_modifier = 0.8;
    warmth = 0.4;
  } else if (hour >= 17 && hour < 20) {
    phase = 'DUSK';
    tempo_modifier = 0.6;
    warmth = 0.9;
  } else if (hour >= 20 && hour < 23) {
    phase = 'EVENING';
    tempo_modifier = 0.4;
    warmth = 0.7;
  } else {
    phase = 'NIGHT';
    tempo_modifier = 0.3;
    warmth = 0.5;
  }

  return { phase, tempo_modifier, warmth, hour };
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useCircadian(): UseCircadianReturn {
  // Try to fetch from backend
  const { data: apiData, isLoading, error, refetch } = useAgentese<CircadianData>(
    'self.presence',
    {
      aspect: 'circadian',
      pollInterval: 60000, // Refresh every minute
    }
  );

  // Fallback to client-side calculation
  const [clientData, setClientData] = useState<CircadianData>(calculateClientCircadian);

  // Update client data every minute
  useEffect(() => {
    const interval = setInterval(() => {
      setClientData(calculateClientCircadian());
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  // Use API data if available, otherwise client-side
  const data = apiData ?? clientData;

  // Generate CSS variables
  const cssVars = generateCssVars(data);

  // Generate background style
  const backgroundStyle = generateBackgroundStyle(data);

  // Wrap refetch to handle void return
  const handleRefetch = useCallback(async () => {
    await refetch();
  }, [refetch]);

  return {
    data,
    isLoading,
    error,
    cssVars,
    backgroundStyle,
    refetch: handleRefetch,
  };
}

// =============================================================================
// Exports
// =============================================================================

export default useCircadian;
