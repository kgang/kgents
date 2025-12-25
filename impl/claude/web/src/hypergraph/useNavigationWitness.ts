/**
 * Navigation Witness Hook
 *
 * Integrates useWitness with HypergraphEditor navigation.
 * Every significant navigation creates a witnessed mark.
 *
 * "Every navigation leaves a trail. The trail IS the evidence."
 *
 * @see spec/synthesis/RADICAL_TRANSFORMATION.md
 */

import { useCallback, useRef } from 'react';
import { useWitness, NavigationAction, DomainMark } from '../hooks/useWitness';
import { GraphNode, NavigationState, EditorMode } from './state/types';

// =============================================================================
// Types
// =============================================================================

export interface NavigationWitnessOptions {
  /** Enable witnessing (default: true) */
  enabled?: boolean;

  /** Debounce rapid navigations (ms, default: 300) */
  debounceMs?: number;

  /** Subscribe to real-time marks */
  subscribe?: boolean;
}

export interface NavigationWitnessResult {
  /** Witness a navigation event */
  witnessNavigation: (
    actionType: NavigationAction,
    fromNode: GraphNode | null,
    toNode: GraphNode,
    extra?: {
      keySequence?: string;
      viaEdge?: string;
      lossValue?: number;
      confidence?: number;
    }
  ) => void;

  /** Witness a mode transition */
  witnessMode: (
    fromMode: EditorMode,
    toMode: EditorMode,
    nodePath: string | null
  ) => void;

  /** Recent navigation marks */
  recentMarks: DomainMark[];

  /** Whether SSE is connected */
  isConnected: boolean;

  /** Number of pending fire-and-forget marks */
  pendingCount: number;
}

// =============================================================================
// Action Type Mappings
// =============================================================================

/**
 * Map key sequences to navigation action types.
 */
const KEY_TO_ACTION: Record<string, NavigationAction> = {
  gD: 'derivation',
  gl: 'loss_gradient',
  gh: 'loss_gradient',
  gL: 'loss_gradient',
  gH: 'loss_gradient',
  gj: 'sibling',
  gk: 'sibling',
  gd: 'definition',
  gr: 'references',
  gt: 'tests',
  'Ctrl-o': 'back',
  'Ctrl-i': 'forward',
};

/**
 * Infer action type from key sequence or fall back to direct.
 */
function inferActionType(keySequence?: string, viaEdge?: string): NavigationAction {
  if (keySequence && KEY_TO_ACTION[keySequence]) {
    return KEY_TO_ACTION[keySequence];
  }
  if (viaEdge === 'derives_from') return 'derivation';
  if (viaEdge === 'implements') return 'definition';
  if (viaEdge === 'tests') return 'tests';
  if (viaEdge === 'references') return 'references';
  return 'direct';
}

/**
 * Generate human-readable reasoning for navigation.
 */
function generateReasoning(
  actionType: NavigationAction,
  extra?: {
    keySequence?: string;
    viaEdge?: string;
    lossValue?: number;
    confidence?: number;
  }
): string {
  switch (actionType) {
    case 'derivation':
      return 'Following derivation chain to understand justification';
    case 'loss_gradient':
      if (extra?.lossValue !== undefined) {
        return `Following loss gradient (loss: ${(extra.lossValue * 100).toFixed(1)}%)`;
      }
      return 'Following loss gradient toward stability';
    case 'sibling':
      return 'Exploring related nodes at the same level';
    case 'definition':
      return 'Navigating to definition/implementation';
    case 'references':
      return 'Exploring references and usages';
    case 'tests':
      return 'Navigating to tests for verification';
    case 'back':
      return 'Returning to previous position in trail';
    case 'forward':
      return 'Moving forward in navigation history';
    case 'direct':
      return extra?.keySequence
        ? `Direct navigation via ${extra.keySequence}`
        : 'Direct navigation to node';
  }
}

// =============================================================================
// Hook Implementation
// =============================================================================

/**
 * Hook that wraps navigation with witness marks.
 *
 * @example
 * const { witnessNavigation, witnessMode } = useNavigationWitness();
 *
 * // In navigation handler:
 * function handleNavigate(toNode: GraphNode) {
 *   witnessNavigation('derivation', currentNode, toNode, { keySequence: 'gD' });
 *   dispatch({ type: 'FOCUS_NODE', node: toNode });
 * }
 *
 * // In mode handler:
 * function handleModeChange(newMode: EditorMode) {
 *   witnessMode(currentMode, newMode, currentNode?.path);
 *   dispatch({ type: 'SET_MODE', mode: newMode });
 * }
 */
export function useNavigationWitness(
  options: NavigationWitnessOptions = {}
): NavigationWitnessResult {
  const { enabled = true, debounceMs = 300, subscribe = false } = options;

  const { witness, recentMarks, isConnected, pendingCount } =
    useWitness({
      subscribe,
      filterDomain: 'navigation',
      maxRecent: 30,
    });

  // Debounce tracking
  const lastNavRef = useRef<{ path: string; time: number } | null>(null);

  /**
   * Witness a navigation event with full context.
   */
  const witnessNavigation = useCallback(
    (
      actionType: NavigationAction,
      fromNode: GraphNode | null,
      toNode: GraphNode,
      extra?: {
        keySequence?: string;
        viaEdge?: string;
        lossValue?: number;
        confidence?: number;
      }
    ) => {
      if (!enabled) return;

      // Debounce rapid navigations to same node
      const now = Date.now();
      if (
        lastNavRef.current &&
        lastNavRef.current.path === toNode.path &&
        now - lastNavRef.current.time < debounceMs
      ) {
        return;
      }
      lastNavRef.current = { path: toNode.path, time: now };

      // Infer action type if not explicitly provided
      const inferredType = extra?.keySequence
        ? inferActionType(extra.keySequence, extra.viaEdge)
        : actionType;

      // Build descriptive action string
      const fromPath = fromNode?.path ?? '(root)';
      const toPath = toNode.path;
      const viaString = extra?.viaEdge ? ` via [${extra.viaEdge}]` : '';
      const action = `${fromPath} -> ${toPath}${viaString}`;

      // Generate reasoning
      const reasoning = generateReasoning(inferredType, extra);

      // Build metadata
      const metadata: Record<string, unknown> = {
        fromPath: fromNode?.path,
        toPath: toNode.path,
        nodeKind: toNode.kind,
        nodeTier: toNode.tier,
      };
      if (extra?.keySequence) metadata.keySequence = extra.keySequence;
      if (extra?.viaEdge) metadata.viaEdge = extra.viaEdge;
      if (extra?.lossValue !== undefined) metadata.lossValue = extra.lossValue;
      if (extra?.confidence !== undefined) metadata.confidence = extra.confidence;
      if (toNode.derivationTier) metadata.derivationTier = toNode.derivationTier;

      // Fire the witness mark (fire-and-forget)
      witness({
        domain: 'navigation',
        actionType: inferredType,
        action,
        reasoning,
        metadata,
        fireAndForget: true,
      });
    },
    [enabled, debounceMs, witness]
  );

  /**
   * Witness a mode transition.
   */
  const witnessMode = useCallback(
    (fromMode: EditorMode, toMode: EditorMode, nodePath: string | null) => {
      if (!enabled) return;

      // Only witness significant mode changes
      if (fromMode === toMode) return;

      // Skip temporary modes like COMMAND
      const significantModes: EditorMode[] = ['INSERT', 'EDGE', 'WITNESS'];
      if (!significantModes.includes(toMode) && !significantModes.includes(fromMode)) {
        return;
      }

      const action = `Mode: ${fromMode} -> ${toMode}${nodePath ? ` at ${nodePath}` : ''}`;
      const reasoning =
        toMode === 'INSERT'
          ? 'Entering edit mode to modify content'
          : toMode === 'EDGE'
            ? 'Entering edge mode to create/modify relationships'
            : toMode === 'WITNESS'
              ? 'Entering witness mode to mark significant moment'
              : `Exiting ${fromMode} mode`;

      witness({
        domain: 'navigation',
        action,
        reasoning,
        principles: ['ethical'], // Mode changes affect behavior
        metadata: { fromMode, toMode, nodePath },
        fireAndForget: true,
      });
    },
    [enabled, witness]
  );

  return {
    witnessNavigation,
    witnessMode,
    recentMarks,
    isConnected,
    pendingCount,
  };
}

// =============================================================================
// Reducer Wrapper Factory
// =============================================================================

/**
 * Create a wrapped reducer that witnesses navigation state changes.
 *
 * @example
 * const witnessedReducer = createWitnessedReducer(
 *   navigationReducer,
 *   witnessNavigation
 * );
 */
export function createWitnessedReducer(
  baseReducer: (state: NavigationState, action: unknown) => NavigationState,
  witnessNavigation: NavigationWitnessResult['witnessNavigation']
): (state: NavigationState, action: unknown) => NavigationState {
  return (state: NavigationState, action: unknown): NavigationState => {
    const prevNode = state.currentNode;
    const nextState = baseReducer(state, action);
    const nextNode = nextState.currentNode;

    // Detect navigation (node changed)
    if (nextNode && (!prevNode || prevNode.path !== nextNode.path)) {
      // Extract action type from action object if present
      const actionObj = action as { type?: string; direction?: number };
      let navAction: NavigationAction = 'direct';
      let viaEdge: string | undefined;

      switch (actionObj.type) {
        case 'FOCUS_NODE':
          navAction = 'direct';
          break;
        case 'GO_SIBLING':
          navAction = 'sibling';
          break;
        case 'GO_BACK':
          navAction = 'back';
          break;
        case 'GO_DEFINITION':
          navAction = 'definition';
          viaEdge = 'implements';
          break;
        case 'GO_TESTS':
          navAction = 'tests';
          viaEdge = 'tests';
          break;
        case 'GO_REFERENCES':
          navAction = 'references';
          viaEdge = 'references';
          break;
        case 'GO_DERIVATION':
          navAction = 'derivation';
          viaEdge = 'derives_from';
          break;
      }

      witnessNavigation(navAction, prevNode, nextNode, { viaEdge });
    }

    return nextState;
  };
}

// =============================================================================
// Export
// =============================================================================

export default useNavigationWitness;
