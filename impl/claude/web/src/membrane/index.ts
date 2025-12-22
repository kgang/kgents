/**
 * Membrane — The single morphing co-thinking surface
 *
 * "Stop documenting agents. Become the agent."
 */

// Main component
export { Membrane } from './Membrane';

// Hooks
export { useMembrane } from './useMembrane';
export type {
  MembraneMode,
  FocusType,
  Focus,
  DialogueMessage,
  MembraneState,
  UseMembrane,
} from './useMembrane';

export { useWitnessStream } from './useWitnessStream';
export type { WitnessEvent, WitnessEventType, UseWitnessStream } from './useWitnessStream';

export { useSpecGraph, useSpecQuery, useSpecEdges, useSpecNavigate } from './useSpecNavigation';
export type {
  EdgeType,
  TokenType,
  SpecNode,
  SpecEdge,
  SpecToken,
  SpecQueryResult,
  SpecGraphStats,
} from './useSpecNavigation';

// Sub-components (for advanced use)
export { FocusPane } from './FocusPane';
export { WitnessStream } from './WitnessStream';
export { WitnessEvent as WitnessEventComponent } from './WitnessEvent';
export { DialoguePane } from './DialoguePane';
export { DialogueMessage as DialogueMessageComponent } from './DialogueMessage';

// Views
export { WelcomeView, FileView, SpecView, ConceptView } from './views';
