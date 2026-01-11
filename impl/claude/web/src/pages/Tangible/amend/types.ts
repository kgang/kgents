/**
 * Amendment Mode Types
 *
 * Type definitions for proposing and reviewing constitutional changes
 * to K-Blocks in the Self-Reflective OS.
 *
 * "The constitution that cannot be amended is already dead."
 */

// =============================================================================
// Amendment Status & Type
// =============================================================================

export type AmendmentStatus =
  | 'draft'
  | 'proposed'
  | 'under_review'
  | 'approved'
  | 'rejected'
  | 'applied'
  | 'reverted';

export type AmendmentType =
  | 'principle_addition'
  | 'principle_modification'
  | 'principle_removal'
  | 'axiom_refinement'
  | 'derivation_correction'
  | 'layer_restructure';

// =============================================================================
// Review & Witness Types
// =============================================================================

export interface ReviewNote {
  id: string;
  reviewer: string;
  note: string;
  timestamp: string;
  sentiment?: 'support' | 'concern' | 'question' | 'neutral';
}

export interface AmendmentWitness {
  markId: string;
  action: string;
  author: 'kent' | 'claude' | 'system';
  timestamp: string;
  reasoning?: string;
}

// =============================================================================
// Amendment Core Types
// =============================================================================

export interface Amendment {
  id: string;
  title: string;
  description: string;
  amendmentType: AmendmentType;
  status: AmendmentStatus;
  targetKblock: string;
  targetKblockTitle?: string;
  targetLayer: 0 | 1 | 2 | 3 | 4;
  originalContent: string;
  proposedContent: string;
  diff: string;
  proposer: string;
  reasoning: string;
  principlesAffected: string[];
  reviewNotes: ReviewNote[];
  witnesses?: AmendmentWitness[];
  approvalReasoning?: string;
  rejectionReasoning?: string;
  createdAt: string;
  proposedAt?: string;
  reviewedAt?: string;
  appliedAt?: string;
  revertedAt?: string;
  preCommitSha?: string;
  postCommitSha?: string;
}

// =============================================================================
// Amendment Form Types
// =============================================================================

export interface AmendmentDraft {
  title: string;
  description: string;
  amendmentType: AmendmentType;
  targetKblock: string;
  targetLayer: 0 | 1 | 2 | 3 | 4;
  proposedContent: string;
  reasoning: string;
  principlesAffected: string[];
}

export interface AmendmentProposalInput {
  title: string;
  description: string;
  amendmentType: AmendmentType;
  targetKblock: string;
  targetLayer: 0 | 1 | 2 | 3 | 4;
  proposedContent: string;
  reasoning: string;
  principlesAffected: string[];
  submitForReview: boolean;
}

// =============================================================================
// UI State Types
// =============================================================================

export type AmendmentFilterStatus = AmendmentStatus | 'all';

export interface AmendmentFilters {
  status: AmendmentFilterStatus;
  searchQuery: string;
  layer?: 0 | 1 | 2 | 3 | 4;
  amendmentType?: AmendmentType;
}

export interface AmendmentModeState {
  selectedAmendmentId: string | null;
  filters: AmendmentFilters;
  isProposalModalOpen: boolean;
  isEditing: boolean;
  leftPanelCollapsed: boolean;
  rightPanelCollapsed: boolean;
  viewMode: 'split' | 'diff' | 'original' | 'proposed';
}

// =============================================================================
// Constants
// =============================================================================

export const AMENDMENT_TYPE_LABELS: Record<AmendmentType, string> = {
  principle_addition: 'Add Principle',
  principle_modification: 'Modify Principle',
  principle_removal: 'Remove Principle',
  axiom_refinement: 'Refine Axiom',
  derivation_correction: 'Correct Derivation',
  layer_restructure: 'Restructure Layer',
};

export const AMENDMENT_STATUS_LABELS: Record<AmendmentStatus, string> = {
  draft: 'Draft',
  proposed: 'Proposed',
  under_review: 'Under Review',
  approved: 'Approved',
  rejected: 'Rejected',
  applied: 'Applied',
  reverted: 'Reverted',
};

export const AMENDMENT_STATUS_COLORS: Record<AmendmentStatus, string> = {
  draft: '#71717a', // steel-500
  proposed: '#c4a77d', // amber (glow)
  under_review: '#6b8b6b', // sage green
  approved: '#6b8b6b', // sage green
  rejected: '#e57373', // red
  applied: '#6b8b6b', // sage green
  reverted: '#e57373', // red
};

export const LAYER_COLORS = {
  0: '#c4a77d', // L0: AXIOM (amber/honey)
  1: '#6b8b6b', // L1: VALUE (sage green)
  2: '#8b7355', // L2: SPEC (earth brown)
  3: '#a39890', // L3: TUNING (warm steel)
  4: '#52525b', // L4: IMPL (dark steel)
} as const;

export const LAYER_NAMES = {
  0: 'AXIOM',
  1: 'VALUE',
  2: 'SPEC',
  3: 'TUNING',
  4: 'IMPL',
} as const;

// =============================================================================
// Mock Data (for initial development)
// =============================================================================

export const MOCK_AMENDMENTS: Amendment[] = [
  {
    id: 'amend-1',
    title: 'Add HETERARCHICAL principle',
    description: 'Introduce the concept of non-hierarchical agent relationships',
    amendmentType: 'principle_addition',
    status: 'under_review',
    targetKblock: 'spec/principles/core.md',
    targetKblockTitle: 'Core Principles',
    targetLayer: 1,
    originalContent: `## Core Principles

1. COMPOSABLE - Agents are morphisms in a category
2. ETHICAL - Augment human capability, never replace judgment
3. TASTEFUL - Each agent serves a clear, justified purpose
4. JOY_INDUCING - Delight in interaction`,
    proposedContent: `## Core Principles

1. COMPOSABLE - Agents are morphisms in a category
2. ETHICAL - Augment human capability, never replace judgment
3. TASTEFUL - Each agent serves a clear, justified purpose
4. JOY_INDUCING - Delight in interaction
5. HETERARCHICAL - Agents exist in flux, not fixed hierarchy`,
    diff: `@@ -4,4 +4,5 @@
 2. ETHICAL - Augment human capability, never replace judgment
 3. TASTEFUL - Each agent serves a clear, justified purpose
 4. JOY_INDUCING - Delight in interaction
+5. HETERARCHICAL - Agents exist in flux, not fixed hierarchy`,
    proposer: 'kent',
    reasoning:
      'The kgents architecture is inherently non-hierarchical. Agents can compose freely without fixed parent-child relationships. This principle makes that explicit.',
    principlesAffected: ['composable', 'joy_inducing'],
    reviewNotes: [
      {
        id: 'note-1',
        reviewer: 'claude',
        note: 'This aligns well with the categorical foundation. Should we also consider implications for the operad composition?',
        timestamp: '2025-12-22T10:30:00Z',
        sentiment: 'support',
      },
    ],
    createdAt: '2025-12-22T09:00:00Z',
    proposedAt: '2025-12-22T09:30:00Z',
  },
  {
    id: 'amend-2',
    title: 'Refine COMPOSABLE axiom definition',
    description: 'Clarify the categorical semantics of agent composition',
    amendmentType: 'axiom_refinement',
    status: 'draft',
    targetKblock: 'spec/principles/axioms.md',
    targetKblockTitle: 'Axioms',
    targetLayer: 0,
    originalContent: `## COMPOSABLE

Agents are morphisms in a category. Composition is associative.`,
    proposedContent: `## COMPOSABLE

Agents are morphisms in a category. Composition is:
- Associative: (f >> g) >> h = f >> (g >> h)
- Unital: id >> f = f = f >> id
- Typed: Agents have input/output types that must match at composition boundaries`,
    diff: `@@ -1,3 +1,7 @@
 ## COMPOSABLE

-Agents are morphisms in a category. Composition is associative.
+Agents are morphisms in a category. Composition is:
+- Associative: (f >> g) >> h = f >> (g >> h)
+- Unital: id >> f = f = f >> id
+- Typed: Agents have input/output types that must match at composition boundaries`,
    proposer: 'kent',
    reasoning:
      'The original definition is too vague. Explicit categorical laws make the composability guarantees clear.',
    principlesAffected: ['composable'],
    reviewNotes: [],
    createdAt: '2025-12-22T14:00:00Z',
  },
  {
    id: 'amend-3',
    title: 'Remove deprecated EMERGENCE concept',
    description: 'Remove the EMERGENCE section that was superseded by HETERARCHICAL',
    amendmentType: 'principle_removal',
    status: 'approved',
    targetKblock: 'spec/principles/deprecated.md',
    targetKblockTitle: 'Deprecated Concepts',
    targetLayer: 1,
    originalContent: `## EMERGENCE

Emergent behavior arises from simple rules applied recursively.
This concept has been found to be too vague for practical application.`,
    proposedContent: `<!-- EMERGENCE removed: superseded by HETERARCHICAL principle -->`,
    diff: `@@ -1,4 +1 @@
-## EMERGENCE
-
-Emergent behavior arises from simple rules applied recursively.
-This concept has been found to be too vague for practical application.
+<!-- EMERGENCE removed: superseded by HETERARCHICAL principle -->`,
    proposer: 'kent',
    reasoning:
      'The EMERGENCE concept was always vague. Post-extinction cleanup means removing concepts that do not carry their weight.',
    principlesAffected: [],
    reviewNotes: [
      {
        id: 'note-2',
        reviewer: 'claude',
        note: 'Agreed. This was a philosophical placeholder without operational value.',
        timestamp: '2025-12-21T16:00:00Z',
        sentiment: 'support',
      },
    ],
    approvalReasoning: 'Clean removal of dead concept. No dependencies found in codebase.',
    createdAt: '2025-12-21T15:00:00Z',
    proposedAt: '2025-12-21T15:30:00Z',
    reviewedAt: '2025-12-21T16:30:00Z',
  },
];
