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
