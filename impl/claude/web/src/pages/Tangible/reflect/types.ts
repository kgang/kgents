/**
 * Reflect Mode Types
 *
 * Type definitions for the comprehensive codebase explorer,
 * git history, K-Block inspection, and derivation chain viewing.
 *
 * "The system that watches itself think, and thinks about its watching."
 */

// =============================================================================
// Codebase Explorer Types
// =============================================================================

export type FileType = 'spec' | 'impl' | 'docs' | 'config' | 'test' | 'unknown';

export interface CodebaseFile {
  path: string;
  name: string;
  type: 'file' | 'directory';
  fileType: FileType;
  /** K-Block ID if file has K-Block coverage */
  kblockId?: string;
  /** Whether file has spec/impl drift */
  hasDrift?: boolean;
  /** Last modified timestamp */
  modifiedAt?: string;
  /** Layer in constitutional hierarchy (0-3) */
  layer?: 0 | 1 | 2 | 3;
  /** Galois loss for derivation coherence */
  galoisLoss?: number;
  /** Child files/directories */
  children?: CodebaseFile[];
}

export interface CodebaseFilter {
  type?: 'spec' | 'impl' | 'all';
  hasKBlock?: boolean;
  hasDrift?: boolean;
  searchQuery?: string;
}

// =============================================================================
// Git Types
// =============================================================================

export interface CommitInfo {
  sha: string;
  shortSha: string;
  message: string;
  author: string;
  authorEmail: string;
  date: string;
  filesChanged: number;
  insertions?: number;
  deletions?: number;
}

export interface CommitFile {
  path: string;
  status: 'added' | 'modified' | 'deleted' | 'renamed';
  insertions: number;
  deletions: number;
  previousPath?: string;
}

export interface CommitDetail extends CommitInfo {
  files: CommitFile[];
  parentSha?: string;
  diff?: string;
}

export interface CommitFilter {
  path?: string;
  author?: string;
  dateRange?: {
    start: Date;
    end: Date;
  };
  searchQuery?: string;
}

export interface BlameLine {
  lineNumber: number;
  content: string;
  commitSha: string;
  author: string;
  date: string;
}

// =============================================================================
// Decision Types (Enhanced)
// =============================================================================

export interface Decision {
  id: string;
  timestamp: string;
  topic: string;
  synthesis: string;
  kentView?: string;
  kentReasoning?: string;
  claudeView?: string;
  claudeReasoning?: string;
  relatedFiles?: string[];
  relatedMarks?: string[];
  tags?: string[];
}

// =============================================================================
// K-Block Types
// =============================================================================

export interface KBlockInfo {
  id: string;
  path: string;
  title: string;
  layer: 0 | 1 | 2 | 3;
  layerName: 'AXIOM' | 'VALUE' | 'SPEC' | 'TUNING';
  content?: string;
  derivedFrom?: string[];
  groundedBy?: string[];
  witnesses?: WitnessInfo[];
  galoisLoss?: number;
  createdAt: string;
  modifiedAt?: string;
}

export interface WitnessInfo {
  markId: string;
  action: string;
  author: 'kent' | 'claude' | 'system';
  timestamp: string;
  principles: string[];
}

// =============================================================================
// Derivation Chain Types
// =============================================================================

export interface DerivationStep {
  id: string;
  title: string;
  layer: 0 | 1 | 2 | 3;
  layerName: 'AXIOM' | 'VALUE' | 'SPEC' | 'TUNING';
  galoisLoss: number;
  path?: string;
  description?: string;
}

export interface DerivationChain {
  sourceId: string;
  sourcePath: string;
  steps: DerivationStep[];
  totalLoss: number;
}

// =============================================================================
// Panel State Types
// =============================================================================

export type RightPanelTab = 'git' | 'decisions' | 'witness';

export interface ReflectState {
  selectedFile: string | null;
  selectedCommit: string | null;
  selectedDecision: string | null;
  selectedKBlock: string | null;
  rightPanelTab: RightPanelTab;
  codebaseFilter: CodebaseFilter;
  commitFilter: CommitFilter;
  showDerivationChain: boolean;
  showKBlockInspector: boolean;
  kblockInspectorPosition?: { x: number; y: number };
  leftPanelCollapsed: boolean;
  rightPanelCollapsed: boolean;
}

// =============================================================================
// Layer Colors
// =============================================================================

export const LAYER_COLORS = {
  0: '#c4a77d', // L0: AXIOM (amber/honey glow)
  1: '#6b8b6b', // L1: VALUE (sage green)
  2: '#8b7355', // L2: SPEC (earth brown)
  3: '#a39890', // L3: TUNING (warm steel)
} as const;

export const LAYER_NAMES = {
  0: 'AXIOM',
  1: 'VALUE',
  2: 'SPEC',
  3: 'TUNING',
} as const;
