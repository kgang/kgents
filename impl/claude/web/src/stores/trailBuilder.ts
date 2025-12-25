/**
 * Trail Builder Store - Zustand state for trail creation UI.
 *
 * "The trail creation UI should feel like curating a museum exhibit."
 *
 * Features:
 * - Progressive step building
 * - Undo/redo support
 * - Topic tagging
 * - Save to backend
 *
 * @see brainstorming/visual-trail-graph-r&d.md Section 2
 * @see spec/protocols/trail-protocol.md
 */

import { create } from 'zustand';
import { nanoid } from 'nanoid';

// =============================================================================
// Types
// =============================================================================

/**
 * Edge types for trail steps.
 * From R&D doc - structured edges and semantic edges.
 */
export const EDGE_TYPES = [
  // Structural edges
  { value: 'contains', label: 'Contains', icon: '▣', semantic: false },
  { value: 'implements', label: 'Implements', icon: '◎', semantic: false },
  { value: 'imports', label: 'Imports', icon: '→', semantic: false },
  { value: 'uses', label: 'Uses', icon: '◇', semantic: false },
  { value: 'tests', label: 'Tests', icon: '✓', semantic: false },
  { value: 'extends', label: 'Extends', icon: '◆', semantic: false },
  { value: 'specifies', label: 'Specifies', icon: '▤', semantic: false },
  { value: 'projects', label: 'Projects', icon: '◉', semantic: false },
  // Semantic edges (dashed, animated)
  { value: 'semantic:similar_to', label: 'Similar To', icon: '≈', semantic: true },
  { value: 'semantic:grounds', label: 'Grounds', icon: '●', semantic: true },
  { value: 'semantic:contradicts', label: 'Contradicts', icon: '×', semantic: true },
  { value: 'semantic:evolves', label: 'Evolves Into', icon: '→', semantic: true },
  { value: 'semantic:encodes', label: 'Encodes', icon: '◎', semantic: true },
] as const;

export type EdgeType = (typeof EDGE_TYPES)[number]['value'];

/**
 * A step in the trail being built.
 * Supports branching via parentId/children relationships.
 */
export interface TrailBuilderStep {
  /** Unique ID for this step */
  id: string;
  /** Path to the file/concept */
  path: string;
  /** Edge type from parent step (null for root step) */
  edge: EdgeType | null;
  /** Reasoning for this step */
  reasoning: string;
  /** Parent step ID for branching (null = root step) */
  parentId: string | null;
  /** Child step IDs (computed, for UI convenience) */
  children: string[];
}

/**
 * History entry for undo/redo.
 */
interface HistoryEntry {
  name: string;
  steps: TrailBuilderStep[];
  topics: string[];
}

/**
 * Trail builder state.
 */
export interface TrailBuilderState {
  /** Trail name */
  name: string;
  /** Steps in the trail */
  steps: TrailBuilderStep[];
  /** Topic tags */
  topics: string[];
  /** Is the builder open? */
  isOpen: boolean;
  /** Is saving in progress? */
  isSaving: boolean;
  /** Error message */
  error: string | null;

  // Branching state
  /** ID of the current branch tip (where new steps are added) */
  currentBranchId: string | null;

  // History for undo/redo
  history: HistoryEntry[];
  historyIndex: number;

  // Actions
  open: () => void;
  close: () => void;
  setName: (name: string) => void;
  addStep: (path: string) => void;
  updateStep: (id: string, updates: Partial<Omit<TrailBuilderStep, 'id' | 'children'>>) => void;
  removeStep: (id: string) => void;
  reorderSteps: (fromIndex: number, toIndex: number) => void;
  addTopic: (topic: string) => void;
  removeTopic: (topic: string) => void;
  undo: () => void;
  redo: () => void;
  reset: () => void;
  save: () => Promise<string | null>;

  // Branching actions
  /** Create a branch from an existing step */
  branchFrom: (stepId: string, path: string) => void;
  /** Switch to a different branch for adding new steps */
  switchBranch: (stepId: string) => void;
}

// =============================================================================
// Store
// =============================================================================

const MAX_HISTORY = 50;

const initialState = {
  name: '',
  steps: [] as TrailBuilderStep[],
  topics: [] as string[],
  isOpen: false,
  isSaving: false,
  error: null,
  currentBranchId: null as string | null,
  history: [] as HistoryEntry[],
  historyIndex: -1,
};

export const useTrailBuilder = create<TrailBuilderState>((set, get) => ({
  ...initialState,

  open: () => set({ isOpen: true }),

  close: () => set({ isOpen: false }),

  setName: (name) => set({ name }),

  addStep: (path) => {
    const { steps, pushHistory } = getHelpers(get, set);
    const { currentBranchId } = get();
    pushHistory();

    const newStepId = nanoid(8);

    // Determine parent: use currentBranchId if set, otherwise last step
    const parentId = currentBranchId ?? (steps.length > 0 ? steps[steps.length - 1].id : null);

    const newStep: TrailBuilderStep = {
      id: newStepId,
      path,
      edge: parentId ? 'imports' : null, // Default edge for non-root steps
      reasoning: '',
      parentId,
      children: [],
    };

    // Update parent's children array if parent exists
    let updatedSteps = [...steps];
    if (parentId) {
      updatedSteps = updatedSteps.map((step) =>
        step.id === parentId
          ? { ...step, children: [...step.children, newStepId] }
          : step
      );
    }

    set({
      steps: [...updatedSteps, newStep],
      currentBranchId: newStepId, // New step becomes the current branch tip
    });
  },

  updateStep: (id, updates) => {
    const { steps, pushHistory } = getHelpers(get, set);
    pushHistory();

    set({
      steps: steps.map((step) =>
        step.id === id ? { ...step, ...updates } : step
      ),
    });
  },

  removeStep: (id) => {
    const { steps, pushHistory } = getHelpers(get, set);
    const { currentBranchId } = get();
    pushHistory();

    const stepToRemove = steps.find((s) => s.id === id);
    if (!stepToRemove) return;

    // Remove step and update parent's children array
    let newSteps = steps.filter((s) => s.id !== id);

    // Update parent's children array
    if (stepToRemove.parentId) {
      newSteps = newSteps.map((step) =>
        step.id === stepToRemove.parentId
          ? { ...step, children: step.children.filter((c) => c !== id) }
          : step
      );
    }

    // Re-parent orphaned children to the removed step's parent
    const orphanedChildren = stepToRemove.children;
    if (orphanedChildren.length > 0) {
      newSteps = newSteps.map((step) =>
        orphanedChildren.includes(step.id)
          ? { ...step, parentId: stepToRemove.parentId }
          : step
      );
      // Update new parent's children array
      if (stepToRemove.parentId) {
        newSteps = newSteps.map((step) =>
          step.id === stepToRemove.parentId
            ? { ...step, children: [...step.children, ...orphanedChildren] }
            : step
        );
      }
    }

    // If removed step was current branch, switch to parent or last step
    let newCurrentBranchId = currentBranchId;
    if (currentBranchId === id) {
      newCurrentBranchId = stepToRemove.parentId ?? (newSteps.length > 0 ? newSteps[newSteps.length - 1].id : null);
    }

    set({ steps: newSteps, currentBranchId: newCurrentBranchId });
  },

  reorderSteps: (fromIndex, toIndex) => {
    const { steps, pushHistory } = getHelpers(get, set);
    if (fromIndex === toIndex) return;
    pushHistory();

    const newSteps = [...steps];
    const [removed] = newSteps.splice(fromIndex, 1);
    newSteps.splice(toIndex, 0, removed);

    // Ensure first step has no edge
    if (newSteps.length > 0) {
      newSteps[0] = { ...newSteps[0], edge: null };
    }

    // Ensure non-first steps have an edge (default to 'imports' if none)
    for (let i = 1; i < newSteps.length; i++) {
      if (!newSteps[i].edge) {
        newSteps[i] = { ...newSteps[i], edge: 'imports' };
      }
    }

    set({ steps: newSteps });
  },

  addTopic: (topic) => {
    const { topics } = get();
    const normalized = topic.toLowerCase().trim();
    if (normalized && !topics.includes(normalized)) {
      set({ topics: [...topics, normalized] });
    }
  },

  removeTopic: (topic) => {
    const { topics } = get();
    set({ topics: topics.filter((t) => t !== topic) });
  },

  undo: () => {
    const { history, historyIndex } = get();
    if (historyIndex < 0) return;

    const entry = history[historyIndex];
    set({
      name: entry.name,
      steps: entry.steps,
      topics: entry.topics,
      historyIndex: historyIndex - 1,
    });
  },

  redo: () => {
    const { history, historyIndex } = get();
    if (historyIndex >= history.length - 1) return;

    const entry = history[historyIndex + 1];
    set({
      name: entry.name,
      steps: entry.steps,
      topics: entry.topics,
      historyIndex: historyIndex + 1,
    });
  },

  reset: () => set(initialState),

  save: async () => {
    const { name, steps, topics } = get();

    if (!name.trim()) {
      set({ error: 'Trail name is required' });
      return null;
    }

    if (steps.length === 0) {
      set({ error: 'At least one step is required' });
      return null;
    }

    set({ isSaving: true, error: null });

    try {
      // Build step ID to index map for parent_index conversion
      const idToIndex = new Map(steps.map((step, i) => [step.id, i]));

      // Convert to API format with parent_index for branching
      const apiSteps = steps.map((step) => ({
        path: step.path,
        edge: step.edge || undefined,
        reasoning: step.reasoning || undefined,
        parent_index: step.parentId ? idToIndex.get(step.parentId) ?? null : null,
      }));

      // Call the backend API
      const response = await fetch('/agentese/self/trail/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(),
          steps: apiSteps,
          topics,
          response_format: 'json',
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create trail: ${response.statusText}`);
      }

      const data = await response.json();
      const trailId = data.result?.metadata?.trail_id;

      if (!trailId) {
        throw new Error('No trail_id in response');
      }

      // Success - reset and close
      set({ ...initialState });
      return trailId;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to save trail';
      set({ error: message, isSaving: false });
      return null;
    }
  },

  // Branching actions
  branchFrom: (stepId, path) => {
    const { steps, pushHistory } = getHelpers(get, set);
    pushHistory();

    const parentStep = steps.find((s) => s.id === stepId);
    if (!parentStep) return;

    const newStepId = nanoid(8);

    const newStep: TrailBuilderStep = {
      id: newStepId,
      path,
      edge: 'imports', // Default edge for branch
      reasoning: '',
      parentId: stepId,
      children: [],
    };

    // Update parent's children array
    const updatedSteps = steps.map((step) =>
      step.id === stepId
        ? { ...step, children: [...step.children, newStepId] }
        : step
    );

    set({
      steps: [...updatedSteps, newStep],
      currentBranchId: newStepId, // Switch to new branch
    });
  },

  switchBranch: (stepId) => {
    const { steps } = get();
    const step = steps.find((s) => s.id === stepId);
    if (step) {
      set({ currentBranchId: stepId });
    }
  },
}));

// =============================================================================
// Helpers
// =============================================================================

function getHelpers(
  get: () => TrailBuilderState,
  set: (state: Partial<TrailBuilderState>) => void
) {
  const { name, steps, topics, history, historyIndex } = get();

  const pushHistory = () => {
    // Save current state to history
    const entry: HistoryEntry = { name, steps, topics };
    const newHistory = [...history.slice(0, historyIndex + 1), entry];

    // Limit history size
    if (newHistory.length > MAX_HISTORY) {
      newHistory.shift();
    }

    set({
      history: newHistory,
      historyIndex: newHistory.length - 1,
    });
  };

  return { steps, pushHistory };
}

// =============================================================================
// Selectors
// =============================================================================

export const selectCanUndo = (state: TrailBuilderState) => state.historyIndex >= 0;
export const selectCanRedo = (state: TrailBuilderState) =>
  state.historyIndex < state.history.length - 1;
export const selectStepCount = (state: TrailBuilderState) => state.steps.length;
export const selectIsValid = (state: TrailBuilderState) =>
  state.name.trim().length > 0 && state.steps.length > 0;

// =============================================================================
// Reasoning Validation (Session 2)
// =============================================================================

/**
 * Reasoning level for hierarchical requirements.
 * From spec/protocols/trail-protocol.md Section 3.3
 */
export type ReasoningLevel = 'trail' | 'branch' | 'semantic' | 'structural';

/**
 * Get the reasoning level for a step.
 *
 * Hierarchy:
 * - Trail (Sheaf): Root step representing the overall exploration
 * - Branch Point: Step with multiple children (decision point)
 * - Semantic Edge: Step using semantic edge types (similar_to, grounds, etc.)
 * - Structural Edge: Step using structural edge types (imports, contains, etc.)
 */
export function getReasoningLevel(step: TrailBuilderStep, steps: TrailBuilderStep[]): ReasoningLevel {
  // Check if this is a branch point (has multiple children)
  const children = steps.filter((s) => s.parentId === step.id);
  if (children.length > 1) {
    return 'branch';
  }

  // Check if this is a semantic edge
  if (step.edge?.startsWith('semantic:')) {
    return 'semantic';
  }

  // Check if this is a root step with no children (trail-level reasoning)
  if (step.parentId === null && children.length === 0) {
    return 'trail';
  }

  return 'structural';
}

/**
 * Validation result for reasoning requirements.
 */
export interface ReasoningValidationResult {
  /** Is the trail valid for saving? */
  valid: boolean;
  /** Blocking errors (must fix before save) */
  errors: string[];
  /** Non-blocking warnings (can save with warnings) */
  warnings: string[];
  /** Can the trail be saved? (errors.length === 0) */
  canSave: boolean;
}

/**
 * Validate reasoning requirements for all steps.
 *
 * Requirements (from spec Section 3.3):
 * - Trail (Sheaf): Required (name field serves this purpose)
 * - Branch Point: Required (decision points need explanation)
 * - Semantic Edge: Encouraged (not blocking)
 * - Structural Edge: Optional
 */
export function validateReasoning(state: TrailBuilderState): ReasoningValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Trail name is required (trail-level reasoning proxy)
  if (!state.name.trim()) {
    errors.push('Trail name is required');
  }

  // Check branch points - require reasoning
  for (const step of state.steps) {
    const children = state.steps.filter((s) => s.parentId === step.id);
    const isBranchPoint = children.length > 1;

    if (isBranchPoint && !step.reasoning.trim()) {
      // Extract filename for clearer error message
      const filename = step.path.split('/').pop() || step.path;
      errors.push(`Branch at "${filename}" needs reasoning`);
    }

    // Check semantic edges - encouraged but not required
    if (step.edge?.startsWith('semantic:') && !step.reasoning.trim()) {
      const filename = step.path.split('/').pop() || step.path;
      warnings.push(`Semantic edge at "${filename}" should have reasoning`);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    canSave: errors.length === 0,
  };
}

/**
 * Get reasoning prompt placeholder based on level.
 */
export function getReasoningPlaceholder(level: ReasoningLevel): string {
  switch (level) {
    case 'trail':
      return 'This trail documents how...';
    case 'branch':
      return 'Branching here to explore...';
    case 'semantic':
      return 'Similar pattern to...';
    case 'structural':
      return 'Following the connection...';
  }
}
