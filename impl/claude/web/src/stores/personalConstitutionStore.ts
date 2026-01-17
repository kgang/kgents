/**
 * Personal Constitution Store - Zustand state for axiom discovery and constitution building.
 *
 * Manages state for the Personal Constitution Builder, including:
 * - Axiom discovery pipeline execution
 * - Discovered candidate management
 * - Constitution building (accept/reject/edit)
 * - Local persistence via localStorage
 * - Amendment history tracking
 *
 * Philosophy:
 *   "The persona is a garden, not a museum."
 *   Axioms should feel discovered, not imposed. Evidence-based UI.
 *
 * @see services/zero_seed/axiom_discovery_pipeline.py
 * @see components/constitution/PersonalConstitutionBuilder.tsx
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  AxiomCandidate,
  ConstitutionalAxiom,
  PersonalConstitution,
  DiscoveryProgress,
  AxiomDiscoveryResult,
  Amendment,
  AxiomLayer,
} from '../components/constitution/types';
import { getAxiomLayer, candidateToConstitutional } from '../components/constitution/types';

// =============================================================================
// State Types
// =============================================================================

interface PersonalConstitutionState {
  // Discovery State
  /** Whether discovery is in progress */
  isDiscovering: boolean;

  /** Current discovery progress */
  discoveryProgress: DiscoveryProgress | null;

  /** Latest discovery result */
  discoveryResult: AxiomDiscoveryResult | null;

  /** Error from latest discovery attempt */
  discoveryError: string | null;

  // Candidates State
  /** Candidates currently being reviewed */
  pendingCandidates: AxiomCandidate[];

  /** Currently selected candidate for detail view */
  selectedCandidateIndex: number | null;

  // Constitution State
  /** The user's personal constitution */
  constitution: PersonalConstitution;

  // UI State
  /** Active section in the builder */
  activeSection: 'discover' | 'review' | 'constitution' | 'contradictions';

  /** Whether to show accepted axioms only in constitution view */
  showAcceptedOnly: boolean;

  /** Filter by layer in constitution view */
  filterLayer: AxiomLayer | 'all';
}

// =============================================================================
// Actions
// =============================================================================

interface PersonalConstitutionActions {
  // Discovery Actions
  /** Start axiom discovery */
  startDiscovery: (days?: number, maxCandidates?: number) => Promise<void>;

  /** Update discovery progress */
  setDiscoveryProgress: (progress: DiscoveryProgress) => void;

  /** Set discovery result */
  setDiscoveryResult: (result: AxiomDiscoveryResult) => void;

  /** Set discovery error */
  setDiscoveryError: (error: string | null) => void;

  /** Clear discovery state */
  clearDiscovery: () => void;

  // Candidate Actions
  /** Select a candidate for detail view */
  selectCandidate: (index: number | null) => void;

  /** Accept a candidate into the constitution */
  acceptCandidate: (candidate: AxiomCandidate, notes?: string) => void;

  /** Reject a candidate */
  rejectCandidate: (candidate: AxiomCandidate, notes?: string) => void;

  /** Edit a candidate before accepting */
  editAndAccept: (candidate: AxiomCandidate, editedContent: string, notes?: string) => void;

  /** Remove a candidate from pending review */
  dismissCandidate: (index: number) => void;

  // Constitution Actions
  /** Remove an axiom from the constitution */
  removeAxiom: (axiomId: string) => void;

  /** Update an existing axiom */
  updateAxiom: (axiomId: string, updates: Partial<ConstitutionalAxiom>) => void;

  /** Reorder axioms within a layer */
  reorderAxioms: (layer: AxiomLayer, fromIndex: number, toIndex: number) => void;

  /** Check for contradictions in the constitution */
  checkContradictions: () => Promise<void>;

  // UI Actions
  /** Set active section */
  setActiveSection: (section: PersonalConstitutionState['activeSection']) => void;

  /** Toggle accepted-only filter */
  toggleShowAcceptedOnly: () => void;

  /** Set layer filter */
  setFilterLayer: (layer: AxiomLayer | 'all') => void;

  // Utility Actions
  /** Export constitution */
  exportConstitution: (format: 'markdown' | 'json' | 'spec') => string;

  /** Reset to initial state */
  reset: () => void;

  /** Get axioms by layer */
  getAxiomsByLayer: (layer: AxiomLayer) => ConstitutionalAxiom[];

  /** Get total axiom count */
  getTotalAxiomCount: () => number;
}

// =============================================================================
// Store Type
// =============================================================================

export type PersonalConstitutionStore = PersonalConstitutionState & PersonalConstitutionActions;

// =============================================================================
// Initial State
// =============================================================================

const initialConstitution: PersonalConstitution = {
  axioms: [],
  values: [],
  goals: [],
  contradictions: [],
  lastUpdated: new Date().toISOString(),
  discoveryCount: 0,
  amendments: [],
};

const initialState: PersonalConstitutionState = {
  isDiscovering: false,
  discoveryProgress: null,
  discoveryResult: null,
  discoveryError: null,
  pendingCandidates: [],
  selectedCandidateIndex: null,
  constitution: initialConstitution,
  activeSection: 'discover',
  showAcceptedOnly: true,
  filterLayer: 'all',
};

// =============================================================================
// Store Implementation
// =============================================================================

export const usePersonalConstitutionStore = create<PersonalConstitutionStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      // =========================================================================
      // Discovery Actions
      // =========================================================================

      startDiscovery: async (days = 30, maxCandidates = 10) => {
        set({
          isDiscovering: true,
          discoveryProgress: {
            stage: 'surfacing',
            message: 'Surfacing your decisions...',
            percent: 0,
            decisionsAnalyzed: 0,
            patternsFound: 0,
          },
          discoveryError: null,
        });

        try {
          // Import API client dynamically to avoid circular deps
          const { discoverAxioms } = await import('../api/axiomDiscovery');
          const result = await discoverAxioms({ days, maxCandidates });

          set({
            isDiscovering: false,
            discoveryProgress: {
              stage: 'complete',
              message: `Discovered ${result.axiomsDiscovered} axioms from ${result.totalDecisionsAnalyzed} decisions`,
              percent: 100,
              decisionsAnalyzed: result.totalDecisionsAnalyzed,
              patternsFound: result.patternsFound,
            },
            discoveryResult: result,
            pendingCandidates: result.candidates,
            constitution: {
              ...get().constitution,
              discoveryCount: get().constitution.discoveryCount + 1,
            },
            activeSection: 'review',
          });
        } catch (error) {
          set({
            isDiscovering: false,
            discoveryError: error instanceof Error ? error.message : 'Discovery failed',
            discoveryProgress: null,
          });
        }
      },

      setDiscoveryProgress: (progress) => {
        set({ discoveryProgress: progress });
      },

      setDiscoveryResult: (result) => {
        set({
          discoveryResult: result,
          pendingCandidates: result.candidates,
          isDiscovering: false,
        });
      },

      setDiscoveryError: (error) => {
        set({ discoveryError: error, isDiscovering: false });
      },

      clearDiscovery: () => {
        set({
          discoveryResult: null,
          discoveryProgress: null,
          discoveryError: null,
          pendingCandidates: [],
          selectedCandidateIndex: null,
        });
      },

      // =========================================================================
      // Candidate Actions
      // =========================================================================

      selectCandidate: (index) => {
        set({ selectedCandidateIndex: index });
      },

      acceptCandidate: (candidate, notes) => {
        const constitutional = candidateToConstitutional(candidate, 'accepted');
        constitutional.notes = notes;

        const layer = getAxiomLayer(candidate.loss);
        const constitution = { ...get().constitution };

        // Add to appropriate layer
        switch (layer) {
          case 'L0':
            constitution.axioms = [...constitution.axioms, constitutional];
            break;
          case 'L1':
            constitution.values = [...constitution.values, constitutional];
            break;
          case 'L2':
            constitution.goals = [...constitution.goals, constitutional];
            break;
        }

        // Record amendment
        const amendment: Amendment = {
          id: `amend_${Date.now()}`,
          type: 'add',
          axiomId: constitutional.id,
          description: `Accepted "${candidate.content}" as ${layer}`,
          timestamp: new Date().toISOString(),
        };
        constitution.amendments = [...constitution.amendments, amendment];
        constitution.lastUpdated = new Date().toISOString();

        // Remove from pending
        const pending = get().pendingCandidates.filter((c) => c.content !== candidate.content);

        set({
          constitution,
          pendingCandidates: pending,
          selectedCandidateIndex: null,
        });
      },

      rejectCandidate: (candidate, notes) => {
        const constitutional = candidateToConstitutional(candidate, 'rejected');
        constitutional.notes = notes;

        // Remove from pending but track rejection
        const pending = get().pendingCandidates.filter((c) => c.content !== candidate.content);

        set({
          pendingCandidates: pending,
          selectedCandidateIndex: null,
        });
      },

      editAndAccept: (candidate, editedContent, notes) => {
        const constitutional = candidateToConstitutional(candidate, 'edited');
        constitutional.editedContent = editedContent;
        constitutional.notes = notes;

        const layer = getAxiomLayer(candidate.loss);
        const constitution = { ...get().constitution };

        // Add to appropriate layer
        switch (layer) {
          case 'L0':
            constitution.axioms = [...constitution.axioms, constitutional];
            break;
          case 'L1':
            constitution.values = [...constitution.values, constitutional];
            break;
          case 'L2':
            constitution.goals = [...constitution.goals, constitutional];
            break;
        }

        // Record amendment
        const amendment: Amendment = {
          id: `amend_${Date.now()}`,
          type: 'add',
          axiomId: constitutional.id,
          description: `Accepted edited "${editedContent}" (was: "${candidate.content}") as ${layer}`,
          timestamp: new Date().toISOString(),
        };
        constitution.amendments = [...constitution.amendments, amendment];
        constitution.lastUpdated = new Date().toISOString();

        // Remove from pending
        const pending = get().pendingCandidates.filter((c) => c.content !== candidate.content);

        set({
          constitution,
          pendingCandidates: pending,
          selectedCandidateIndex: null,
        });
      },

      dismissCandidate: (index) => {
        const pending = [...get().pendingCandidates];
        pending.splice(index, 1);
        set({ pendingCandidates: pending, selectedCandidateIndex: null });
      },

      // =========================================================================
      // Constitution Actions
      // =========================================================================

      removeAxiom: (axiomId) => {
        const constitution = { ...get().constitution };
        let removed: ConstitutionalAxiom | undefined;

        // Find and remove from the appropriate layer
        constitution.axioms = constitution.axioms.filter((a) => {
          if (a.id === axiomId) {
            removed = a;
            return false;
          }
          return true;
        });

        if (!removed) {
          constitution.values = constitution.values.filter((a) => {
            if (a.id === axiomId) {
              removed = a;
              return false;
            }
            return true;
          });
        }

        if (!removed) {
          constitution.goals = constitution.goals.filter((a) => {
            if (a.id === axiomId) {
              removed = a;
              return false;
            }
            return true;
          });
        }

        if (removed) {
          // Record amendment
          const amendment: Amendment = {
            id: `amend_${Date.now()}`,
            type: 'remove',
            axiomId,
            description: `Removed "${removed.editedContent || removed.content}"`,
            timestamp: new Date().toISOString(),
            previousState: removed,
          };
          constitution.amendments = [...constitution.amendments, amendment];
          constitution.lastUpdated = new Date().toISOString();
        }

        set({ constitution });
      },

      updateAxiom: (axiomId, updates) => {
        const constitution = { ...get().constitution };

        const updateInList = (list: ConstitutionalAxiom[]) =>
          list.map((a) => (a.id === axiomId ? { ...a, ...updates } : a));

        constitution.axioms = updateInList(constitution.axioms);
        constitution.values = updateInList(constitution.values);
        constitution.goals = updateInList(constitution.goals);

        // Record amendment
        const amendment: Amendment = {
          id: `amend_${Date.now()}`,
          type: 'edit',
          axiomId,
          description: `Updated axiom`,
          timestamp: new Date().toISOString(),
        };
        constitution.amendments = [...constitution.amendments, amendment];
        constitution.lastUpdated = new Date().toISOString();

        set({ constitution });
      },

      reorderAxioms: (layer, fromIndex, toIndex) => {
        const constitution = { ...get().constitution };

        const reorder = (list: ConstitutionalAxiom[]) => {
          const result = [...list];
          const [removed] = result.splice(fromIndex, 1);
          result.splice(toIndex, 0, removed);
          return result;
        };

        switch (layer) {
          case 'L0':
            constitution.axioms = reorder(constitution.axioms);
            break;
          case 'L1':
            constitution.values = reorder(constitution.values);
            break;
          case 'L2':
            constitution.goals = reorder(constitution.goals);
            break;
        }

        constitution.lastUpdated = new Date().toISOString();
        set({ constitution });
      },

      checkContradictions: async () => {
        try {
          const { detectContradictions } = await import('../api/axiomDiscovery');
          const constitution = get().constitution;

          // Get all accepted axioms
          const allAxioms = [
            ...constitution.axioms,
            ...constitution.values,
            ...constitution.goals,
          ].filter((a) => a.status === 'accepted' || a.status === 'edited');

          if (allAxioms.length < 2) {
            set({
              constitution: {
                ...constitution,
                contradictions: [],
              },
            });
            return;
          }

          const contents = allAxioms.map((a) => a.editedContent || a.content);
          const contradictions = await detectContradictions(contents);

          set({
            constitution: {
              ...constitution,
              contradictions,
            },
          });
        } catch (error) {
          console.error('Failed to check contradictions:', error);
        }
      },

      // =========================================================================
      // UI Actions
      // =========================================================================

      setActiveSection: (section) => {
        set({ activeSection: section });
      },

      toggleShowAcceptedOnly: () => {
        set({ showAcceptedOnly: !get().showAcceptedOnly });
      },

      setFilterLayer: (layer) => {
        set({ filterLayer: layer });
      },

      // =========================================================================
      // Utility Actions
      // =========================================================================

      exportConstitution: (format) => {
        const constitution = get().constitution;
        const now = new Date().toISOString();

        if (format === 'json') {
          return JSON.stringify(constitution, null, 2);
        }

        if (format === 'spec') {
          // Export as kgents spec file format
          let spec = `---
title: Personal Constitution
type: constitution
created: ${now}
last_updated: ${constitution.lastUpdated}
discovery_count: ${constitution.discoveryCount}
---

# Personal Constitution

> "The persona is a garden, not a museum."

`;

          if (constitution.axioms.length > 0) {
            spec += `## L0 Axioms (Fixed Points)\n\n`;
            spec += `These are the principles you never violate.\n\n`;
            constitution.axioms.forEach((a, i) => {
              const content = a.editedContent || a.content;
              spec += `### ${i + 1}. ${content}\n\n`;
              spec += `- **Loss**: ${a.loss.toFixed(4)}\n`;
              spec += `- **Confidence**: ${(a.confidence * 100).toFixed(1)}%\n`;
              spec += `- **Evidence**: ${a.evidence.length} decisions\n\n`;
            });
          }

          if (constitution.values.length > 0) {
            spec += `## L1 Values (Strong Preferences)\n\n`;
            spec += `These are values you rarely trade off.\n\n`;
            constitution.values.forEach((a, i) => {
              const content = a.editedContent || a.content;
              spec += `### ${i + 1}. ${content}\n\n`;
              spec += `- **Loss**: ${a.loss.toFixed(4)}\n`;
              spec += `- **Confidence**: ${(a.confidence * 100).toFixed(1)}%\n`;
              spec += `- **Evidence**: ${a.evidence.length} decisions\n\n`;
            });
          }

          if (constitution.goals.length > 0) {
            spec += `## L2 Goals (Guiding Principles)\n\n`;
            spec += `These are goals you sometimes adjust.\n\n`;
            constitution.goals.forEach((a, i) => {
              const content = a.editedContent || a.content;
              spec += `### ${i + 1}. ${content}\n\n`;
              spec += `- **Loss**: ${a.loss.toFixed(4)}\n`;
              spec += `- **Confidence**: ${(a.confidence * 100).toFixed(1)}%\n`;
              spec += `- **Evidence**: ${a.evidence.length} decisions\n\n`;
            });
          }

          return spec;
        }

        // Default: markdown
        let md = `# My Personal Constitution\n\n`;
        md += `*Last updated: ${new Date(constitution.lastUpdated).toLocaleDateString()}*\n\n`;

        if (constitution.axioms.length > 0) {
          md += `## Axioms (L0)\n\n`;
          md += `*Principles I never violate*\n\n`;
          constitution.axioms.forEach((a, i) => {
            const content = a.editedContent || a.content;
            md += `${i + 1}. **${content}** *(${(a.confidence * 100).toFixed(0)}% confident)*\n`;
          });
          md += `\n`;
        }

        if (constitution.values.length > 0) {
          md += `## Values (L1)\n\n`;
          md += `*Strong preferences I rarely trade off*\n\n`;
          constitution.values.forEach((a, i) => {
            const content = a.editedContent || a.content;
            md += `${i + 1}. **${content}** *(${(a.confidence * 100).toFixed(0)}% confident)*\n`;
          });
          md += `\n`;
        }

        if (constitution.goals.length > 0) {
          md += `## Goals (L2)\n\n`;
          md += `*Guiding principles I sometimes adjust*\n\n`;
          constitution.goals.forEach((a, i) => {
            const content = a.editedContent || a.content;
            md += `${i + 1}. **${content}** *(${(a.confidence * 100).toFixed(0)}% confident)*\n`;
          });
          md += `\n`;
        }

        return md;
      },

      reset: () => {
        set(initialState);
      },

      getAxiomsByLayer: (layer) => {
        const constitution = get().constitution;
        switch (layer) {
          case 'L0':
            return constitution.axioms;
          case 'L1':
            return constitution.values;
          case 'L2':
            return constitution.goals;
        }
      },

      getTotalAxiomCount: () => {
        const constitution = get().constitution;
        return constitution.axioms.length + constitution.values.length + constitution.goals.length;
      },
    }),
    {
      name: 'kgents-personal-constitution',
      partialize: (state) => ({
        constitution: state.constitution,
        showAcceptedOnly: state.showAcceptedOnly,
        filterLayer: state.filterLayer,
      }),
    }
  )
);

// =============================================================================
// Selectors
// =============================================================================

export const selectConstitution = (state: PersonalConstitutionStore) => state.constitution;
export const selectPendingCandidates = (state: PersonalConstitutionStore) =>
  state.pendingCandidates;
export const selectIsDiscovering = (state: PersonalConstitutionStore) => state.isDiscovering;
export const selectDiscoveryProgress = (state: PersonalConstitutionStore) =>
  state.discoveryProgress;
export const selectDiscoveryResult = (state: PersonalConstitutionStore) => state.discoveryResult;
export const selectActiveSection = (state: PersonalConstitutionStore) => state.activeSection;

export const selectHasContradictions = (state: PersonalConstitutionStore) =>
  state.constitution.contradictions.length > 0;

export const selectTotalAxiomCount = (state: PersonalConstitutionStore) =>
  state.constitution.axioms.length +
  state.constitution.values.length +
  state.constitution.goals.length;

export const selectStrongContradictions = (state: PersonalConstitutionStore) =>
  state.constitution.contradictions.filter(
    (c) => c.type === 'strong' || c.type === 'irreconcilable'
  );
