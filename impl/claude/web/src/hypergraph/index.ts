/**
 * Hypergraph Emacs — Exports
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
} from './types';

export { createInitialState, createTrailStep } from './types';

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

// API Bridge
export { useGraphNode, normalizePath } from './useGraphNode';
export type { UseGraphNodeResult } from './useGraphNode';
