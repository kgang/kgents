/**
 * Membrane — Legacy exports (redirects to new locations)
 *
 * POST-PHASE-1.1 (2025-12-23): Membrane folder simplified.
 * - useWitnessStream → hooks/useWitnessStream
 * - tokens/ → components/tokens/
 * - Container components → _archive/membrane/
 *
 * POST-PHASE-1.2 (2025-12-23): K-Block hooks unified.
 * - useKBlock → hypergraph/useKBlock (unified dialogue + file)
 *
 * This file maintains backward compatibility by re-exporting from new locations.
 */

// =============================================================================
// Hooks (moved to hooks/)
// =============================================================================

export { useWitnessStream } from '../hooks/useWitnessStream';
export type { WitnessEvent, WitnessEventType, UseWitnessStream, SemanticDelta } from '../hooks/useWitnessStream';

export { useKBlock, useFileKBlock, useDialogueKBlock } from '../hypergraph/useKBlock';
export type {
  IsolationState,
  KBlockState,
  KBlockCreateResult,
  KBlockSaveResult,
  ViewEditResult,
  KBlockViewType,
  KBlockReference,
  UseKBlockResult,
  UseKBlockOptions,
} from '../hypergraph/useKBlock';

// Legacy type aliases for backward compatibility
export type {
  KBlockState as ThoughtBlockState,
  KBlockSaveResult as CrystallizeResult,
  UseKBlockResult as UseKBlock,
  UseKBlockResult as UseFileKBlock,
} from '../hypergraph/useKBlock';

// =============================================================================
// Components (moved to components/)
// =============================================================================

export { WitnessEvent as WitnessEventComponent } from '../components/layout/WitnessEvent';

// =============================================================================
// Tokens (moved to components/tokens/)
// =============================================================================

export {
  InteractiveDocument,
  AGENTESEPathToken,
  TaskCheckboxToken,
  PortalToken,
  CodeBlockToken,
  ImageToken,
  PrincipleToken,
  LinkToken,
  TextSpan,
  BlockquoteToken,
  HorizontalRuleToken,
  MarkdownTableToken,
} from '../components/tokens';

export type {
  SceneGraph,
  SceneNode,
  SceneEdge,
  PortalDestination,
  PrincipleCategory,
  AGENTESEPathData,
  TaskCheckboxData,
  PortalData,
  CodeBlockData,
  ImageData,
  PrincipleData,
  LinkData,
  BlockquoteData,
  HorizontalRuleData,
  MarkdownTableData,
} from '../components/tokens';

// =============================================================================
// Archived Components (removed — no longer in use)
// =============================================================================
// Previously exported: Membrane, FocusPane, WitnessStream, DialoguePane,
// DialogueMessage, useMembrane, WelcomeView, FileView, SpecView, ConceptView
//
// These components have been migrated or archived:
// - WelcomeView → pages/WelcomePage.tsx
// - Chart components → components/chart/
// - Ledger components → components/
// - Other components remain in _archive/ for reference only

// =============================================================================
// Spec Navigation (canonical location: hypergraph/)
// =============================================================================

export { useSpecGraph, useSpecQuery, useSpecEdges, useSpecNavigate } from '../hypergraph/useSpecNavigation';
export type {
  EdgeType,
  TokenType,
  SpecNode,
  SpecEdge,
  SpecToken,
  SpecQueryResult,
  SpecGraphStats,
} from '../hypergraph/useSpecNavigation';
