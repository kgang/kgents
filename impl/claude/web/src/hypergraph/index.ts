/**
 * Membrane Editor — Exports
 *
 * "The file is a lie. There is only the graph."
 */

// Types
export type {
  EditorMode,
  EdgeType,
  Edge,
  GraphNode,
  Position,
  Viewport,
  TrailStep,
  Trail,
  KBlockState,
  NavigationState,
  NavigationAction,
  KeyModifiers,
  KeyBinding,
  KeySequence,
  CommandResult,
  Command,
} from './state/types';

export { createInitialState, createTrailStep } from './state/types';

// Hooks
export { useNavigation } from './useNavigation';
export type { UseNavigationResult } from './useNavigation';

export { useKeyHandler } from './useKeyHandler';
export type { UseKeyHandlerOptions, UseKeyHandlerResult } from './useKeyHandler';

// Components
export { HypergraphEditor } from './HypergraphEditor';
export { StatusLine } from './StatusLine';
export { CommandLine } from './CommandLine';
export { FileExplorer } from './FileExplorer';
export type { UploadedFile } from './FileExplorer';
export { PlaceholderNode, PlaceholderNodeCompact } from './PlaceholderNode';
export type { PlaceholderData } from './PlaceholderNode';

// Proof Engine Components
export { ProofPanel } from './ProofPanel';
export type { ProofPanelProps } from './ProofPanel';
export { ProofStatusBadge } from './ProofStatusBadge';
export type { ProofStatusBadgeProps } from './ProofStatusBadge';

// API Bridge
export { useGraphNode, normalizePath, isValidFilePath } from './useGraphNode';
export type { UseGraphNodeResult } from './useGraphNode';

export { useFileUpload } from './useFileUpload';
export type { UseFileUploadOptions, UseFileUploadReturn } from './useFileUpload';

export { useRecentFiles } from './useRecentFiles';
export type { UseRecentFilesReturn } from './useRecentFiles';

// Spec Navigation (AGENTESE concept.specgraph.*)
export {
  useSpecGraph,
  useSpecQuery,
  useSpecEdges,
  useSpecNavigate,
  invokeSpecGraph,
} from './useSpecNavigation';
export type {
  UseSpecGraphResult,
  UseSpecQueryResult,
  UseSpecEdgesResult,
  UseSpecNavigateResult,
  SpecNode,
  SpecEdge,
  SpecToken,
  SpecQueryResult,
  SpecGraphStats,
} from './useSpecNavigation';

// Document Parsing
export { useDocumentParser, createFallbackSceneGraph } from './useDocumentParser';
export type { UseDocumentParserOptions, UseDocumentParserReturn } from './useDocumentParser';

// Document Proxy (AD-015)
export {
  useDocumentProxy,
  getNodesForSection,
  sectionChanged,
  getChangedSections,
} from './useDocumentProxy';
export type {
  UseDocumentProxyOptions,
  UseDocumentProxyReturn,
  DocumentProxyStatus,
} from './useDocumentProxy';

// Navigation Witness (Witness Architecture)
export { useNavigationWitness, createWitnessedReducer } from './useNavigationWitness';
export type { NavigationWitnessOptions, NavigationWitnessResult } from './useNavigationWitness';

// Witnessed Trail (Trail + live marks)
export { WitnessedTrail } from './WitnessedTrail';
export type { WitnessedTrailProps } from './WitnessedTrail';

// Navigation Constitutional Badge
export { NavigationConstitutionalBadge } from './NavigationConstitutionalBadge';
export type { NavigationConstitutionalBadgeProps } from './NavigationConstitutionalBadge';

// =============================================================================
// Composable Hooks (extracted from HypergraphEditor)
// =============================================================================

// Feedback Message Hook
export { useFeedbackMessage } from './useFeedbackMessage';
export type { FeedbackMessage } from './useFeedbackMessage';

// Panel State Management
export { useEditorPanels } from './useEditorPanels';

// Witness Handlers
export { useWitnessHandlers } from './useWitnessHandlers';

// Dialectic Handlers
export { useDialecticHandlers } from './useDialecticHandlers';

// Command Handlers
export { useCommandHandlers } from './useCommandHandlers';

// Navigation Handlers
export { useDerivationNavigation } from './useDerivationNavigation';
export { useLossNavigationHandlers } from './useLossNavigationHandlers';
export { useWitnessNavigationHandlers } from './useWitnessNavigationHandlers';

// Zero Seed Foundation (Post-Genesis)
export { ZeroSeedFoundation } from './ZeroSeedFoundation';
export type { ZeroSeedFoundationProps } from './ZeroSeedFoundation';

// Grounding Dialog (orphan K-Block → Constitutional principle)
export { GroundingDialog } from './GroundingDialog';
export type {
  GroundingDialogProps,
  GroundingSuggestion,
  KBlock as GroundingKBlock,
} from './GroundingDialog';

// Affordance Panel (contextual keyboard shortcuts)
export { AffordancePanel } from './AffordancePanel';
export type { AffordancePanelProps, AffordanceAction } from './AffordancePanel';

// K-Block to GraphNode Conversion (Zero Seed wiring)
export {
  kblockToGraphNode,
  isZeroSeedPath,
  extractKBlockId,
  extractZeroSeedCategory,
  isKBlockPath,
  extractKBlockIdFromPath,
  isGenesisFilePath,
  extractKBlockIdFromGenesisPath,
} from './kblockToGraphNode';

// Constitutional Graph View (files derived from principles)
export { ConstitutionalGraphView } from './ConstitutionalGraphView';
export type {
  ConstitutionalGraphViewProps,
  DerivationEdge,
  DerivationGraph,
  ConstitutionalViewMode,
  DerivationTier,
  NodeStatus,
  ContextMenuAction,
} from './ConstitutionalGraphView';

// Coherence Badge (project-wide coherence metrics)
export { CoherenceBadge } from './CoherenceBadge';
export type { default as CoherenceBadgeProps } from './CoherenceBadge';

// Constitutional Principles Summary (principle grounding overview)
export {
  ConstitutionalPrinciplesSummary,
  PRINCIPLE_COLORS,
} from './ConstitutionalPrinciplesSummary';
export type {
  ConstitutionalPrinciplesSummaryProps,
  ConstitutionalPrinciple,
  ConstitutionalPrincipleId,
} from './ConstitutionalPrinciplesSummary';

// Derivation Inspector (derivation path side panel)
export { DerivationInspector } from './DerivationInspector';
export type {
  DerivationInspectorProps,
  DerivationNode as InspectorDerivationNode,
  Witness,
  WitnessType as InspectorWitnessType,
  DownstreamKBlock,
} from './DerivationInspector';

// Derivation Trail Bar (breadcrumb navigation)
export {
  DerivationTrailBar,
  GaloisLossBadge,
  DepthBadge,
  DerivationNodeChip,
} from './DerivationTrailBar';
export type {
  DerivationTrailBarProps,
  DerivationNode as TrailDerivationNode,
  DerivationPath,
  WitnessType as TrailWitnessType,
} from './DerivationTrailBar';

// Witness Marker (reusable witness indicator)
export { WitnessMarker, WitnessBadge, WITNESS_CONFIG } from './WitnessMarker';
export type { WitnessMarkerProps, WitnessBadgeProps, WitnessType } from './WitnessMarker';
