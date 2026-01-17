/**
 * FusionCeremony Types
 *
 * Type definitions for the Dialectical Fusion UI components.
 */

import type { Position, Synthesis, FusionResult } from '@/api/dialectic';

// =============================================================================
// Component States
// =============================================================================

/**
 * The current phase of the fusion ceremony.
 */
export type CeremonyPhase =
  | 'input' // Entering positions
  | 'processing' // Synthesizing
  | 'complete' // Fusion complete
  | 'error'; // Something went wrong

/**
 * State for the fusion ceremony.
 */
export interface CeremonyState {
  phase: CeremonyPhase;
  topic: string;
  thesis: Position | null;
  antithesis: Position | null;
  synthesis: Synthesis | null;
  result: FusionResult | null;
  reasoning: string | null;
  trustDelta: number | null;
  fusionId: string | null;
  markId: string | null;
  error: string | null;
}

/**
 * Initial ceremony state.
 */
export const INITIAL_CEREMONY_STATE: CeremonyState = {
  phase: 'input',
  topic: '',
  thesis: null,
  antithesis: null,
  synthesis: null,
  result: null,
  reasoning: null,
  trustDelta: null,
  fusionId: null,
  markId: null,
  error: null,
};

// =============================================================================
// Component Props
// =============================================================================

/**
 * Props for ThesisPanel.
 */
export interface ThesisPanelProps {
  topic: string;
  onTopicChange: (topic: string) => void;
  content: string;
  onContentChange: (content: string) => void;
  reasoning: string;
  onReasoningChange: (reasoning: string) => void;
  disabled?: boolean;
  className?: string;
}

/**
 * Props for AntithesisPanel.
 */
export interface AntithesisPanelProps {
  content: string;
  onContentChange: (content: string) => void;
  reasoning: string;
  onReasoningChange: (reasoning: string) => void;
  thesisContent?: string;
  disabled?: boolean;
  className?: string;
}

/**
 * Props for SynthesisPanel.
 */
export interface SynthesisPanelProps {
  synthesis: Synthesis | null;
  result: FusionResult | null;
  reasoning: string | null;
  trustDelta: number | null;
  loading?: boolean;
  className?: string;
}

/**
 * Props for CoconeVisualization.
 */
export interface CoconeVisualizationProps {
  thesis: Position | null;
  antithesis: Position | null;
  synthesis: Synthesis | null;
  phase: CeremonyPhase;
  className?: string;
}

/**
 * Props for the main FusionCeremony.
 */
export interface FusionCeremonyProps {
  /** Initial topic (optional) */
  initialTopic?: string;
  /** Initial Kent's view (optional) */
  initialKentView?: string;
  /** Initial Claude's view (optional) */
  initialClaudeView?: string;
  /** Callback when fusion completes */
  onFusionComplete?: (state: CeremonyState) => void;
  /** Custom CSS class */
  className?: string;
}

// =============================================================================
// Animation States
// =============================================================================

/**
 * Animation state for the cocone visualization.
 */
export type CoconeAnimationState =
  | 'idle' // Nothing happening
  | 'thesis-pulse' // Highlighting Kent's position
  | 'antithesis-pulse' // Highlighting Claude's position
  | 'converging' // Both positions moving toward synthesis
  | 'sublating' // The Aufhebung moment
  | 'complete'; // Final state

// =============================================================================
// Export Types
// =============================================================================

/**
 * Export format options.
 */
export type ExportFormat = 'markdown' | 'json' | 'image' | 'link';

/**
 * Export data structure.
 */
export interface ExportData {
  topic: string;
  kentPosition: {
    content: string;
    reasoning: string;
  };
  claudePosition: {
    content: string;
    reasoning: string;
  };
  synthesis: {
    content: string;
    reasoning: string;
    preservedFromKent: string;
    preservedFromClaude: string;
    transcends: string;
  } | null;
  result: FusionResult;
  trustDelta: number;
  fusionId: string;
  timestamp: string;
}
