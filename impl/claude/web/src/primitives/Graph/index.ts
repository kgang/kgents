/**
 * Graph Primitive
 *
 * "The file is a lie. There is only the graph."
 *
 * The hypergraph editor is keeper code - excellent modal editing
 * with K-Block isolation. We re-export from the existing location
 * rather than moving, to minimize disruption.
 *
 * Core Capabilities:
 * ==================
 *
 * 1. Modal Editing (6 modes):
 *    - NORMAL: Navigate the graph (vim-like keybindings)
 *    - INSERT: Edit content (K-Block isolation)
 *    - EDGE: Create/modify graph edges
 *    - VISUAL: Select multiple nodes
 *    - COMMAND: Execute AGENTESE commands
 *    - WITNESS: Mark moments
 *
 * 2. Graph Navigation:
 *    - Edge-based traversal (not file paths)
 *    - Trail history (breadcrumbs)
 *    - Sibling navigation (gj/gk)
 *    - Portal operations (fold/unfold subgraphs)
 *
 * 3. K-Block Isolation:
 *    - Edit in isolated workspace
 *    - Crystallize commits to cosmos
 *    - Discard abandons changes
 *    - Supports file and dialogue K-Blocks
 *
 * 4. Declarative Keybindings:
 *    - Registry-based (not scattered event handlers)
 *    - Mode-specific filtering
 *    - Sequence handling (g-prefix, z-prefix)
 *    - Clean separation: NORMAL reads, INSERT writes
 *
 * Architecture:
 * =============
 *
 * HypergraphEditor (Main Component)
 *   ├── useNavigation (state management)
 *   ├── useKeyHandler (vim-like keybindings)
 *   ├── useKBlock (isolation layer)
 *   ├── useCommandRegistry (Cmd+K palette)
 *   └── Panes (Header, Trail, Content, Gutters)
 *
 * Why Re-Export (not move):
 * ==========================
 *
 * The hypergraph code is already well-organized and battle-tested.
 * Moving it would:
 * - Risk breaking existing imports
 * - Lose git history
 * - Disrupt ongoing development
 *
 * Instead, we create a clean entry point that:
 * - Documents the primitive's purpose
 * - Exports the essential APIs
 * - Identifies reusable patterns
 *
 * Reusable Patterns:
 * ==================
 *
 * These patterns could be extracted for use elsewhere:
 *
 * 1. useKeyRegistry:
 *    - Declarative keybinding system
 *    - Mode-specific filtering
 *    - Sequence handling (multi-key)
 *    - Could power any modal interface
 *
 * 2. K-Block Isolation:
 *    - Edit → Crystallize → Commit pattern
 *    - Could be used for any "possible world" editing
 *    - Already supports file and dialogue modes
 *
 * 3. useCommandRegistry:
 *    - Cmd+K command palette
 *    - Recency tracking
 *    - Category-based organization
 *    - Could be app-wide (not just graph)
 *
 * Usage:
 * ======
 *
 * ```typescript
 * import { HypergraphEditor } from '@/primitives/Graph';
 *
 * function MyPage() {
 *   return (
 *     <HypergraphEditor
 *       initialPath="spec/protocols/witness.md"
 *       onNodeFocus={(node) => console.log('Focused:', node)}
 *       onNavigate={(path) => console.log('Navigated to:', path)}
 *       onZeroSeed={(tab) => navigateToZeroSeed(tab)}
 *     />
 *   );
 * }
 * ```
 */

// =============================================================================
// Main Component
// =============================================================================

export { HypergraphEditor } from '../../hypergraph/HypergraphEditor';

// =============================================================================
// Core Hooks
// =============================================================================

export { useNavigation } from '../../hypergraph/useNavigation';
export type { UseNavigationResult } from '../../hypergraph/useNavigation';

export { useKeyHandler } from '../../hypergraph/useKeyHandler';
export type { UseKeyHandlerOptions, UseKeyHandlerResult } from '../../hypergraph/useKeyHandler';

export { useKBlock } from '../../hypergraph/useKBlock';
export type { UseKBlockOptions, UseKBlockResult } from '../../hypergraph/useKBlock';

export { useCommandRegistry } from '../../hypergraph/useCommandRegistry';
export type { Command } from '../../hypergraph/useCommandRegistry';

// Note: useCommandRegistry doesn't export a named return type, so consumers can use:
// ReturnType<typeof useCommandRegistry> or inline the structure:
// { commands: Command[], recentCommands: string[], trackCommand: (id: string) => void }

// =============================================================================
// Graph API Hooks
// =============================================================================

export { useGraphNode, normalizePath, isValidFilePath } from '../../hypergraph/useGraphNode';
export type { UseGraphNodeResult } from '../../hypergraph/useGraphNode';

export { useFileUpload } from '../../hypergraph/useFileUpload';
export type { UseFileUploadOptions, UseFileUploadReturn } from '../../hypergraph/useFileUpload';

export { useRecentFiles } from '../../hypergraph/useRecentFiles';
export type { UseRecentFilesReturn } from '../../hypergraph/useRecentFiles';

// =============================================================================
// Types
// =============================================================================

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
  KeyBinding,
} from '../../hypergraph/state/types';

// Note: Command type is exported from useCommandRegistry above (not state/types)

export { createInitialState, createTrailStep } from '../../hypergraph/state/types';

// =============================================================================
// UI Components (optional, for custom layouts)
// =============================================================================

export { StatusLine } from '../../hypergraph/StatusLine';
export { CommandLine } from '../../hypergraph/CommandLine';
export { CommandPalette } from '../../hypergraph/CommandPalette';
export { FileExplorer } from '../../hypergraph/FileExplorer';
export type { UploadedFile } from '../../hypergraph/FileExplorer';

// =============================================================================
// Proof Engine (Zero Seed integration)
// =============================================================================

export { ProofPanel } from '../../hypergraph/ProofPanel';
export type { ProofPanelProps } from '../../hypergraph/ProofPanel';
export { ProofStatusBadge } from '../../hypergraph/ProofStatusBadge';
export type { ProofStatusBadgeProps } from '../../hypergraph/ProofStatusBadge';
