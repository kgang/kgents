/**
 * HypergraphEditor — The main editor component
 *
 * "The file is a lie. There is only the graph."
 * "The buffer is a lie. There is only the node."
 *
 * Layout:
 * ┌────────────────────────────────────────────────────────────────────────┐
 * │ ◀ Parent edges │ Current Node Title │ ▶ Child edges count              │
 * ├────────────────────────────────────────────────────────────────────────┤
 * │ TRAIL: node1 → node2 → current                                   [N]  │
 * ├───────┬────────────────────────────────────────────────────────┬───────┤
 * │       │                                                        │       │
 * │ Left  │              Content Pane                              │ Right │
 * │Gutter │              (Node text)                               │Gutter │
 * │       │                                                        │       │
 * ├───────┴────────────────────────────────────────────────────────┴───────┤
 * │ [MODE] | breadcrumb                                    path | 42,7     │
 * └────────────────────────────────────────────────────────────────────────┘
 */

import { memo, useCallback, useEffect, useRef, useState } from 'react';

import { sovereignApi } from '../api/client';
import { useNavigation } from './useNavigation';
import { useKeyHandler } from './useKeyHandler';
import { useKBlock } from './useKBlock';
import { useDirector } from '../hooks/useDirector';
import { useLossNavigation } from './useLossNavigation';
import { StatusLine } from './StatusLine';
import { CommandLine } from './CommandLine';
import { CommandPalette } from './CommandPalette';
import { EdgePanel } from './EdgePanel';
import { WitnessPanel } from './WitnessPanel';
import { HelpPanel } from './HelpPanel';
import { DialogueView } from './DialogueView';
import { DialecticModal } from './DialecticModal';
import { DecisionFooterWidget } from './DecisionFooterWidget';
import { DecisionStream } from './DecisionStream';
import { VetoPanel } from './VetoPanel';
import { useDialecticDecisions } from './useDialecticDecisions';
import type { DialecticDecision, QuickDecisionInput, FullDialecticInput } from './types/dialectic';
import { Header, TrailBar, EdgeGutter, ContentPane } from './panes';
import type { ContentPaneRef } from './panes';
import type { GraphNode, Edge } from './state/types';
import { AnalysisQuadrant } from '../components/analysis/AnalysisQuadrant';
import { ProofPanel } from './ProofPanel';
import { ProofStatusBadge } from './ProofStatusBadge';

import './HypergraphEditor.css';

// =============================================================================
// Types
// =============================================================================

interface HypergraphEditorProps {
  /** Initial node to focus (path) */
  initialPath?: string;

  /** Callback when node is focused */
  onNodeFocus?: (node: GraphNode) => void;

  /** Callback when navigation occurs */
  onNavigate?: (path: string) => void;

  /** External function to load a node by path */
  loadNode?: (path: string) => Promise<GraphNode | null>;

  /** External function to load siblings */
  loadSiblings?: (node: GraphNode) => Promise<GraphNode[]>;

  /** Callback to navigate to Zero Seed page */
  onZeroSeed?: (tab?: string) => void;
}

// =============================================================================
// Main Component
// =============================================================================

export const HypergraphEditor = memo(function HypergraphEditor({
  initialPath,
  onNodeFocus,
  onNavigate,
  loadNode,
  loadSiblings,
  onZeroSeed,
}: HypergraphEditorProps) {
  const navigation = useNavigation();
  const {
    state,
    dispatch,
    focusNode,
    goDefinition,
    goReferences,
    goTests,
    // Portal operations
    openPortal,
    closePortal,
    togglePortal,
    openAllPortals,
    closeAllPortals,
  } = navigation;

  // K-Block integration
  const kblockHook = useKBlock();

  // Director integration (fetch status for spec files)
  const director = useDirector({
    path: state.currentNode?.path,
    autoFetch: state.currentNode?.kind === 'spec',
  });

  // Loss navigation
  const lossNav = useLossNavigation();

  // Refs
  const commandLineRef = useRef<HTMLInputElement>(null);
  const contentPaneRef = useRef<ContentPaneRef>(null);

  // UI state
  const [commandLineVisible, setCommandLineVisible] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [witnessLoading, setWitnessLoading] = useState(false);
  const [confidenceVisible, setConfidenceVisible] = useState(false);
  const [helpVisible, setHelpVisible] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState<{
    type: 'success' | 'warning' | 'error';
    text: string;
  } | null>(null);

  // Dialectic UI state
  const [dialecticModalOpen, setDialecticModalOpen] = useState(false);
  const [dialogueViewOpen, setDialogueViewOpen] = useState(false);
  const [decisionStreamOpen, setDecisionStreamOpen] = useState(false);
  const [vetoPanelOpen, setVetoPanelOpen] = useState(false);
  const [selectedDecision, setSelectedDecision] = useState<DialecticDecision | null>(null);
  const [dialecticLoading, setDialecticLoading] = useState(false);

  // Analysis UI state
  const [analysisQuadrantOpen, setAnalysisQuadrantOpen] = useState(false);

  // Proof panel state
  const [proofPanelOpen, setProofPanelOpen] = useState(false);

  // Loss navigation state (focal distance for future telescope integration)
  const [focalDistance, setFocalDistance] = useState(1.0);
  // Note: focalDistance is updated by gL/gH but not yet consumed by telescope
  // This is intentional - state is tracked for future telescope feature integration
  void focalDistance; // Suppress unused warning

  // Dialectic decisions hook
  const dialectic = useDialecticDecisions({
    pollInterval: 60000, // Poll every minute
    autoFetch: true,
  });

  // =============================================================================
  // Derivation Navigation (gD/gc)
  // =============================================================================

  /**
   * gD - Navigate to derivation parent.
   * Follows the derives_from edge to the parent in the derivation DAG.
   */
  const handleGoDerivationParent = useCallback(() => {
    const node = state.currentNode;
    if (!node) return;

    // First, try explicit derivationParent field
    if (node.derivationParent && loadNode) {
      onNavigate?.(node.derivationParent);
      loadNode(node.derivationParent).then((parentNode) => {
        if (parentNode) {
          focusNode(parentNode);
          onNodeFocus?.(parentNode);
        }
      });
      return;
    }

    // Fall back to derives_from edge
    const derivesFromEdge = node.incomingEdges.find((e) => e.type === 'derives_from');
    if (derivesFromEdge && loadNode) {
      const parentPath = derivesFromEdge.source;
      onNavigate?.(parentPath);
      loadNode(parentPath).then((parentNode) => {
        if (parentNode) {
          focusNode(parentNode);
          onNodeFocus?.(parentNode);
        }
      });
    }
  }, [state.currentNode, loadNode, focusNode, onNavigate, onNodeFocus]);

  /**
   * gc - Toggle confidence breakdown panel.
   * Shows derivation confidence details and ancestor chain.
   */
  const handleShowConfidence = useCallback(() => {
    setConfidenceVisible((prev) => !prev);
  }, []);

  /**
   * Handle re-analyze action.
   * Triggers fresh LLM analysis of the current document via concept.document.analyze.
   */
  const handleReanalyze = useCallback(async () => {
    const currentPath = state.currentNode?.path;
    if (!currentPath || isAnalyzing) return;

    setIsAnalyzing(true);
    try {
      const result = await sovereignApi.analyze(currentPath, { force: true });

      if (result.error) {
        setFeedbackMessage({
          type: 'error',
          text: `Analysis failed: ${result.error}`,
        });
      } else {
        const claims = result.claim_count ?? 0;
        const refs = result.ref_count ?? 0;
        const placeholders = result.placeholder_count ?? 0;
        setFeedbackMessage({
          type: 'success',
          text: `Analysis complete: ${claims} claims, ${refs} refs, ${placeholders} placeholders`,
        });
      }
      setTimeout(() => setFeedbackMessage(null), 4000);
      console.info('[HypergraphEditor] Analysis complete:', result);
    } catch (error) {
      console.error('[HypergraphEditor] Analysis failed:', error);
      setFeedbackMessage({
        type: 'error',
        text: 'Analysis failed. Check console for details.',
      });
      setTimeout(() => setFeedbackMessage(null), 4000);
    } finally {
      setIsAnalyzing(false);
    }
  }, [state.currentNode?.path, isAnalyzing]);

  // Handle INSERT mode entry - create K-Block
  const handleEnterInsert = useCallback(async () => {
    if (!state.currentNode) return;

    // Create K-Block for the current node's path
    const kblockResult = await kblockHook.create(state.currentNode.path);

    // Check for success and blockId - content can be empty string (valid for new/empty files)
    if (kblockResult.success && kblockResult.blockId) {
      // Use content from result, falling back to empty string for empty files
      const content = kblockResult.content ?? '';

      // Update reducer state with K-Block info
      dispatch({ type: 'KBLOCK_CREATED', blockId: kblockResult.blockId, content });
      dispatch({ type: 'ENTER_INSERT' });
      console.info('[HypergraphEditor] Entering INSERT with K-Block:', kblockResult.blockId);
    } else {
      // K-Block creation failed - use fallback content from node
      const fallbackContent = state.currentNode.content ?? '';
      const fallbackId = `local-${Date.now()}`;

      console.warn('[HypergraphEditor] K-Block creation failed, using local fallback:', kblockResult.error);

      // Still create K-Block state so content updates work
      dispatch({ type: 'KBLOCK_CREATED', blockId: fallbackId, content: fallbackContent });
      dispatch({ type: 'ENTER_INSERT' });
    }
  }, [state.currentNode, kblockHook, dispatch]);

  // Handle witness mark save
  const handleWitnessSave = useCallback(
    async (action: string, reasoning?: string, tags?: string[]) => {
      setWitnessLoading(true);
      try {
        await fetch('/api/witness/marks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action,
            reasoning: reasoning || null,
            principles: tags || [],
            author: 'kent',
          }),
        });
        dispatch({ type: 'EXIT_WITNESS' });
        console.info('[HypergraphEditor] Witness mark saved:', action);
      } catch (error) {
        console.error('[HypergraphEditor] Failed to save mark:', error);
      } finally {
        setWitnessLoading(false);
      }
    },
    [dispatch]
  );


  // Handle quick mark (immediate save with tag)
  const handleQuickMark = useCallback(
    async (tag: string) => {
      setWitnessLoading(true);
      try {
        // Quick marks use tag as action template
        const actionTemplates: Record<string, string> = {
          eureka: 'Eureka moment',
          gotcha: 'Gotcha',
          taste: 'Taste decision',
          friction: 'Friction point',
          joy: 'Joy moment',
          veto: 'Veto',
        };

        const action = actionTemplates[tag] || tag;

        await fetch('/api/witness/marks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action,
            reasoning: null,
            principles: [tag],
            author: 'kent',
          }),
        });

        dispatch({ type: 'EXIT_WITNESS' });
        console.info('[HypergraphEditor] Quick mark saved:', tag);
      } catch (error) {
        console.error('[HypergraphEditor] Failed to save quick mark:', error);
      } finally {
        setWitnessLoading(false);
      }
    },
    [dispatch]
  );

  // =============================================================================
  // Dialectic Decision Handlers
  // =============================================================================

  // Handle decision save (quick or full)
  const handleDecisionSave = useCallback(
    async (input: QuickDecisionInput | FullDialecticInput) => {
      setDialecticLoading(true);
      try {
        const response = await fetch('/api/witness/fusion', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(input),
        });

        if (!response.ok) {
          throw new Error(`Failed to save decision: ${response.statusText}`);
        }

        const decision = await response.json();
        console.info('[HypergraphEditor] Decision saved:', decision);

        // Refresh decision list
        await dialectic.refresh();

        // Close modal
        setDialecticModalOpen(false);

        // Show success feedback
        setFeedbackMessage({
          type: 'success',
          text: 'Decision saved',
        });
        setTimeout(() => setFeedbackMessage(null), 3000);
      } catch (error) {
        console.error('[HypergraphEditor] Failed to save decision:', error);
        setFeedbackMessage({
          type: 'error',
          text: 'Failed to save decision',
        });
        setTimeout(() => setFeedbackMessage(null), 4000);
      } finally {
        setDialecticLoading(false);
      }
    },
    [dialectic]
  );

  // Handle veto
  const handleVeto = useCallback(
    async (reason?: string) => {
      if (!selectedDecision) return;

      setDialecticLoading(true);
      try {
        const response = await fetch(`/api/witness/fusion/${selectedDecision.id}/veto`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ reason }),
        });

        if (!response.ok) {
          throw new Error(`Failed to veto decision: ${response.statusText}`);
        }

        console.info('[HypergraphEditor] Decision vetoed:', selectedDecision.id);

        // Refresh decision list
        await dialectic.refresh();

        // Close panels
        setVetoPanelOpen(false);
        setDialogueViewOpen(false);

        // Show success feedback
        setFeedbackMessage({
          type: 'success',
          text: 'Decision vetoed',
        });
        setTimeout(() => setFeedbackMessage(null), 3000);
      } catch (error) {
        console.error('[HypergraphEditor] Failed to veto decision:', error);
        setFeedbackMessage({
          type: 'error',
          text: 'Failed to veto decision',
        });
        setTimeout(() => setFeedbackMessage(null), 4000);
      } finally {
        setDialecticLoading(false);
      }
    },
    [selectedDecision, dialectic]
  );

  // Handle decision click (open DialogueView)
  const handleDecisionClick = useCallback((decision: DialecticDecision) => {
    setSelectedDecision(decision);
    setDialogueViewOpen(true);
    setDecisionStreamOpen(false);
  }, []);

  // Get last decision for footer widget
  const lastDecision = dialectic.decisions.length > 0 ? dialectic.decisions[0] : null;

  // Dialectic keyboard shortcuts
  useEffect(() => {
    const handleDialecticKeys = (e: KeyboardEvent) => {
      // Cmd+Shift+D - Open dialectic modal (quick decision)
      if (e.metaKey && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        setDialecticModalOpen(true);
      }

      // Cmd+Shift+L - Open decision stream (list)
      if (e.metaKey && e.shiftKey && e.key === 'L') {
        e.preventDefault();
        setDecisionStreamOpen(true);
      }
    };

    window.addEventListener('keydown', handleDialecticKeys);
    return () => window.removeEventListener('keydown', handleDialecticKeys);
  }, []);

  // Handle EDGE mode confirmation - create witness mark
  const handleEdgeConfirm = useCallback(async () => {
    if (!state.edgePending) return;

    const { sourceId, edgeType, targetId } = state.edgePending;

    try {
      await fetch('/api/witness/marks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: `Created ${edgeType} edge: ${sourceId} → ${targetId}`,
          reasoning: null,
          principles: ['composable'],
          author: 'hypergraph-editor',
        }),
      });

      dispatch({ type: 'EDGE_CONFIRMED' });
    } catch (error) {
      console.error('[EdgeConfirm] Failed to create edge mark:', error);
      // Still exit edge mode on failure (user can retry)
      dispatch({ type: 'EDGE_CONFIRMED' });
    }
  }, [state.edgePending, dispatch]);

  // =============================================================================
  // Loss-Gradient Navigation (gl/gh/gL/gH)
  // =============================================================================

  /**
   * gl - Navigate to lowest-loss neighbor.
   * Follows the gradient toward stability (min loss).
   */
  const handleGoLowestLoss = useCallback(async () => {
    if (!state.currentNode) return;

    const neighbors = await lossNav.getNeighborLosses(state.currentNode);
    if (neighbors.length === 0) {
      setFeedbackMessage({
        type: 'warning',
        text: 'No neighbors found',
      });
      setTimeout(() => setFeedbackMessage(null), 3000);
      return;
    }

    const lowest = neighbors[0]; // Already sorted ascending
    const targetId = lowest.nodeId;

    if (!loadNode) return;

    onNavigate?.(targetId);
    loadNode(targetId).then((node) => {
      if (node) {
        focusNode(node);
        onNodeFocus?.(node);

        // Show feedback with loss value
        const lossValue = (lowest.loss * 100).toFixed(1);
        setFeedbackMessage({
          type: 'success',
          text: `Navigated to lowest-loss neighbor (loss: ${lossValue}%)`,
        });
        setTimeout(() => setFeedbackMessage(null), 3000);
        console.info('[LossNav] Navigated to lowest-loss neighbor:', targetId, lowest.loss);
      }
    });
  }, [state.currentNode, lossNav, loadNode, focusNode, onNavigate, onNodeFocus]);

  /**
   * gh - Navigate to highest-loss neighbor.
   * Investigates instability (max loss).
   */
  const handleGoHighestLoss = useCallback(async () => {
    if (!state.currentNode) return;

    const neighbors = await lossNav.getNeighborLosses(state.currentNode);
    if (neighbors.length === 0) {
      setFeedbackMessage({
        type: 'warning',
        text: 'No neighbors found',
      });
      setTimeout(() => setFeedbackMessage(null), 3000);
      return;
    }

    const highest = neighbors[neighbors.length - 1]; // Already sorted ascending, so last is highest
    const targetId = highest.nodeId;

    if (!loadNode) return;

    onNavigate?.(targetId);
    loadNode(targetId).then((node) => {
      if (node) {
        focusNode(node);
        onNodeFocus?.(node);

        // Show feedback with loss value
        const lossValue = (highest.loss * 100).toFixed(1);
        setFeedbackMessage({
          type: 'warning',
          text: `Navigated to highest-loss neighbor (loss: ${lossValue}%)`,
        });
        setTimeout(() => setFeedbackMessage(null), 3000);
        console.info('[LossNav] Navigated to highest-loss neighbor:', targetId, highest.loss);
      }
    });
  }, [state.currentNode, lossNav, loadNode, focusNode, onNavigate, onNodeFocus]);

  /**
   * gL - Zoom out (increase focal distance).
   */
  const handleZoomOut = useCallback(() => {
    setFocalDistance((prev) => {
      const newDistance = prev * 10;
      setFeedbackMessage({
        type: 'success',
        text: `Zoomed out (focal distance: ${newDistance.toFixed(2)})`,
      });
      setTimeout(() => setFeedbackMessage(null), 2000);
      console.info('[LossNav] Zoomed out, focal distance:', newDistance);
      return newDistance;
    });
  }, []);

  /**
   * gH - Zoom in (decrease focal distance).
   */
  const handleZoomIn = useCallback(() => {
    setFocalDistance((prev) => {
      const newDistance = Math.max(0.01, prev / 10);
      setFeedbackMessage({
        type: 'success',
        text: `Zoomed in (focal distance: ${newDistance.toFixed(2)})`,
      });
      setTimeout(() => setFeedbackMessage(null), 2000);
      console.info('[LossNav] Zoomed in, focal distance:', newDistance);
      return newDistance;
    });
  }, []);

  // =============================================================================
  // Witness Navigation (gm/gW/gf)
  // =============================================================================

  /**
   * gm - Navigate to witness marks for current node.
   * Opens a panel showing the witness trail (marks related to this node).
   */
  const handleGoToMarks = useCallback(async () => {
    if (!state.currentNode) return;

    try {
      // Fetch marks related to the current node
      const response = await fetch(`/api/witness/marks?path=${encodeURIComponent(state.currentNode.path)}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch marks: ${response.statusText}`);
      }

      const marks = await response.json();
      console.info('[WitnessNav] Marks for node:', state.currentNode.path, marks);

      // TODO: Open a panel to display marks (could reuse WitnessPanel or create new MarkPanel)
      // For now, just open the decision stream and filter by current node
      setDecisionStreamOpen(true);
      setFeedbackMessage({
        type: 'success',
        text: `Found ${marks.length || 0} marks for this node`,
      });
      setTimeout(() => setFeedbackMessage(null), 3000);
    } catch (error) {
      console.error('[WitnessNav] Failed to fetch marks:', error);
      setFeedbackMessage({
        type: 'error',
        text: 'Failed to fetch witness marks',
      });
      setTimeout(() => setFeedbackMessage(null), 4000);
    }
  }, [state.currentNode]);

  /**
   * gW - Navigate to warrant for current node.
   * Shows the justification/reasoning for the current node's existence.
   */
  const handleGoToWarrant = useCallback(async () => {
    if (!state.currentNode) return;

    try {
      // Fetch warrant/justification for the current node
      const response = await fetch(`/api/witness/warrant?path=${encodeURIComponent(state.currentNode.path)}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch warrant: ${response.statusText}`);
      }

      const warrant = await response.json();
      console.info('[WitnessNav] Warrant for node:', state.currentNode.path, warrant);

      // TODO: Open a panel to display warrant
      // For now, show a feedback message
      setFeedbackMessage({
        type: 'success',
        text: warrant.reasoning || 'Warrant found',
      });
      setTimeout(() => setFeedbackMessage(null), 5000);
    } catch (error) {
      console.error('[WitnessNav] Failed to fetch warrant:', error);
      setFeedbackMessage({
        type: 'error',
        text: 'Failed to fetch warrant',
      });
      setTimeout(() => setFeedbackMessage(null), 4000);
    }
  }, [state.currentNode]);

  /**
   * gf - Navigate to decision (fusion) for current node.
   * Shows the dialectical synthesis related to this node.
   */
  const handleGoToDecision = useCallback(async () => {
    if (!state.currentNode) return;

    try {
      // Fetch decision/fusion related to the current node
      const response = await fetch(`/api/witness/fusion?path=${encodeURIComponent(state.currentNode.path)}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch decision: ${response.statusText}`);
      }

      const decisions = await response.json();
      console.info('[WitnessNav] Decisions for node:', state.currentNode.path, decisions);

      if (decisions.length > 0) {
        // Show the most recent decision
        setSelectedDecision(decisions[0]);
        setDialogueViewOpen(true);
      } else {
        setFeedbackMessage({
          type: 'warning',
          text: 'No decisions found for this node',
        });
        setTimeout(() => setFeedbackMessage(null), 3000);
      }
    } catch (error) {
      console.error('[WitnessNav] Failed to fetch decision:', error);
      setFeedbackMessage({
        type: 'error',
        text: 'Failed to fetch decision',
      });
      setTimeout(() => setFeedbackMessage(null), 4000);
    }
  }, [state.currentNode]);

  // Key handler
  const { pendingSequence } = useKeyHandler({
    state,
    dispatch,
    goDefinition,
    goReferences,
    goTests,
    // Derivation navigation (gD/gc)
    goDerivationParent: handleGoDerivationParent,
    showConfidence: handleShowConfidence,
    // Portal operations (zo/zc — vim fold-style)
    openPortal,
    closePortal,
    togglePortal,
    openAllPortals,
    closeAllPortals,
    // Scroll navigation (j/k/{/}/gg/G in NORMAL mode)
    scrollDown: () => contentPaneRef.current?.scrollLines(1),
    scrollUp: () => contentPaneRef.current?.scrollLines(-1),
    scrollParagraphDown: () => contentPaneRef.current?.scrollParagraph(1),
    scrollParagraphUp: () => contentPaneRef.current?.scrollParagraph(-1),
    scrollToTop: () => contentPaneRef.current?.scrollToTop(),
    scrollToBottom: () => contentPaneRef.current?.scrollToBottom(),
    // Mode callbacks
    onEnterCommand: () => {
      setCommandLineVisible(true);
      // Focus command line after state updates
      setTimeout(() => commandLineRef.current?.focus(), 0);
    },
    onEnterInsert: handleEnterInsert,
    onEdgeConfirm: handleEdgeConfirm,
    onShowHelp: () => setHelpVisible(true),
    onOpenCommandPalette: () => setCommandPaletteOpen(true),
    // Decision stream (witness history)
    onToggleDecisionStream: () => setDecisionStreamOpen((prev) => !prev),
    // Analysis quadrant
    onToggleAnalysisQuadrant: () => setAnalysisQuadrantOpen((prev) => !prev),
    // Loss-gradient navigation (gl/gh/gL/gH)
    goLowestLoss: handleGoLowestLoss,
    goHighestLoss: handleGoHighestLoss,
    zoomOut: handleZoomOut,
    zoomIn: handleZoomIn,
    // Witness navigation (gm/gW/gf)
    goToMarks: handleGoToMarks,
    goToWarrant: handleGoToWarrant,
    goToDecision: handleGoToDecision,
    enabled:
      !commandLineVisible &&
      !commandPaletteOpen &&
      !helpVisible &&
      !dialecticModalOpen &&
      !dialogueViewOpen &&
      state.mode !== 'WITNESS',
  });

  // Load initial node
  useEffect(() => {
    if (initialPath && loadNode) {
      loadNode(initialPath).then((node) => {
        if (node) {
          focusNode(node);
          onNodeFocus?.(node);
        }
      });
    }
  }, [initialPath, loadNode, focusNode, onNodeFocus]);

  // Load siblings when node changes
  useEffect(() => {
    if (state.currentNode && loadSiblings) {
      loadSiblings(state.currentNode).then((siblings) => {
        const index = siblings.findIndex((s) => s.path === state.currentNode?.path);
        dispatch({ type: 'SET_SIBLINGS', siblings, index: index >= 0 ? index : 0 });
      });
    }
  }, [state.currentNode, loadSiblings, dispatch]);

  // Load portal content when portals are opened (zo)
  useEffect(() => {
    if (!loadNode) return;

    // Find portals that are loading (no targetNode yet)
    const loadingPortals = Array.from(state.portals.values()).filter(
      (portal) => portal.loading && !portal.targetNode
    );

    // Load each portal's target node
    loadingPortals.forEach((portal) => {
      // Extract target path from the edge
      const edge = state.currentNode?.outgoingEdges.find((e) => e.id === portal.edgeId);
      if (!edge) {
        console.warn('[HypergraphEditor] Portal edge not found:', portal.edgeId);
        return;
      }

      loadNode(edge.target).then((node) => {
        if (node) {
          dispatch({ type: 'PORTAL_LOADED', edgeId: portal.edgeId, node });
        } else {
          console.warn('[HypergraphEditor] Portal target not found:', edge.target);
          // Still mark as loaded (with null) to stop infinite loading
          dispatch({
            type: 'PORTAL_LOADED',
            edgeId: portal.edgeId,
            node: {
              path: edge.target,
              title: 'Not Found',
              kind: 'unknown',
              outgoingEdges: [],
              incomingEdges: [],
              content: `Node not found: ${edge.target}`,
            },
          });
        }
      });
    });
  }, [state.portals, state.currentNode, loadNode, dispatch]);

  // Handle edge click (navigate to connected node)
  const handleEdgeClick = useCallback(
    (edge: Edge) => {
      const targetPath = edge.target === state.currentNode?.path ? edge.source : edge.target;
      onNavigate?.(targetPath);

      if (loadNode) {
        loadNode(targetPath).then((node) => {
          if (node) {
            focusNode(node);
            onNodeFocus?.(node);
          }
        });
      }
    },
    [state.currentNode, onNavigate, loadNode, focusNode, onNodeFocus]
  );

  // Handle witnessed :w save
  const handleWrite = useCallback(
    async (reasoning?: string) => {
      if (!kblockHook.kblock) {
        console.warn('[HypergraphEditor] :w - No K-Block to save');
        setFeedbackMessage({ type: 'warning', text: 'No K-Block to save' });
        setTimeout(() => setFeedbackMessage(null), 3000);
        return false;
      }

      // Sync current content to hook before save
      if (state.kblock?.workingContent) {
        kblockHook.updateContent(state.kblock.workingContent);
      }

      const result = await kblockHook.save(reasoning || undefined);

      if (result.success) {
        // Clear reducer K-Block state
        dispatch({ type: 'KBLOCK_COMMITTED' });
        // Exit INSERT if we were in it
        if (state.mode === 'INSERT') {
          dispatch({ type: 'EXIT_INSERT' });
        }
        console.info('[HypergraphEditor] :w saved K-Block', reasoning ? `(${reasoning})` : '');

        // Show success feedback
        const path = state.currentNode?.path?.split('/').pop() || 'K-Block';
        const message = reasoning
          ? `Saved "${path}" (${reasoning})`
          : `Saved "${path}"`;
        setFeedbackMessage({ type: 'success', text: message });
        setTimeout(() => setFeedbackMessage(null), 3000);
      } else {
        // Show error feedback
        setFeedbackMessage({
          type: 'error',
          text: result.error || 'Failed to save K-Block',
        });
        setTimeout(() => setFeedbackMessage(null), 4000);
      }

      return result.success;
    },
    [kblockHook, state.kblock, state.mode, state.currentNode, dispatch]
  );

  // Handle :q! discard
  const handleQuit = useCallback(
    async (force: boolean) => {
      if (kblockHook.kblock) {
        if (kblockHook.kblock.isDirty && !force) {
          console.warn('[HypergraphEditor] :q - K-Block has unsaved changes. Use :q! to force.');
          setFeedbackMessage({
            type: 'warning',
            text: 'No write since last change (use :q! to force quit)',
          });
          setTimeout(() => setFeedbackMessage(null), 4000);
          return false;
        }

        if (force) {
          await kblockHook.discard();
          dispatch({ type: 'KBLOCK_DISCARDED' });
          console.info('[HypergraphEditor] :q! - Discarded K-Block');

          // Show discard confirmation
          setFeedbackMessage({ type: 'success', text: 'K-Block discarded without saving' });
          setTimeout(() => setFeedbackMessage(null), 3000);
        }
      }

      // Exit INSERT mode if we were in it
      if (state.mode === 'INSERT') {
        dispatch({ type: 'EXIT_INSERT' });
      }

      return true;
    },
    [kblockHook, state.mode, dispatch]
  );

  // Handle command submission
  const handleCommand = useCallback(
    async (command: string) => {
      setCommandLineVisible(false);
      dispatch({ type: 'EXIT_COMMAND' });

      // Parse and execute command
      const rawCmd = command.trim();
      const [cmd, ...args] = rawCmd.split(/\s+/);

      // NOTE: :e/:edit command removed — navigation is via URL or CommandPalette (Cmd+K)
      // "The file is a lie. There is only the graph." Navigate by path, not by command.
      if (cmd === 'w' || cmd === 'write') {
        // :w [message] - Save with optional witness message
        const message = args.join(' ') || undefined;
        await handleWrite(message);
      } else if (cmd === 'wq') {
        // :wq - Save and quit
        const success = await handleWrite();
        if (success) {
          await handleQuit(false);
        }
      } else if (cmd === 'q!' || rawCmd === 'q!') {
        // :q! - Force quit without saving
        await handleQuit(true);
      } else if (cmd === 'q' || cmd === 'quit') {
        // :q - Quit (warns if dirty)
        await handleQuit(false);
      } else if (cmd === 'checkpoint' || cmd === 'cp') {
        // :checkpoint [name] - Create named checkpoint
        const name = args.join(' ') || `checkpoint-${Date.now()}`;
        const cpId = await kblockHook.checkpoint(name);
        if (cpId) {
          dispatch({ type: 'KBLOCK_CHECKPOINT', id: cpId, message: name });
          console.info('[HypergraphEditor] Created checkpoint:', cpId, name);
        }
      } else if (cmd === 'rewind') {
        // :rewind <checkpoint_id> - Rewind to checkpoint
        const checkpointId = args[0];
        if (!checkpointId) {
          console.warn('[HypergraphEditor] :rewind requires checkpoint ID');
          return;
        }
        await kblockHook.rewind(checkpointId);
        console.info('[HypergraphEditor] Rewound to checkpoint:', checkpointId);
      } else if (cmd === 'ag') {
        // :ag <agentese-path> [args...] - Invoke AGENTESE endpoint
        const agentesePath = args[0];
        const agentArgs = args.slice(1).join(' ');

        if (!agentesePath) {
          console.warn('[HypergraphEditor] :ag requires a path (e.g., :ag self.brain.capture "text")');
          setFeedbackMessage({ type: 'warning', text: ':ag requires a path' });
          setTimeout(() => setFeedbackMessage(null), 3000);
          return;
        }

        try {
          // Call AGENTESE invoke API
          const response = await fetch('/api/agentese/invoke', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              path: agentesePath,
              args: agentArgs || undefined,
              observer: 'kent', // Default observer
            }),
          });

          if (response.ok) {
            const result = await response.json();
            console.info('[HypergraphEditor] AGENTESE result:', result);
            setFeedbackMessage({ type: 'success', text: `✓ ${agentesePath}` });
            setTimeout(() => setFeedbackMessage(null), 3000);
          } else {
            const error = await response.text();
            console.error('[HypergraphEditor] AGENTESE error:', error);
            setFeedbackMessage({ type: 'error', text: `AGENTESE: ${error}` });
            setTimeout(() => setFeedbackMessage(null), 4000);
          }
        } catch (err) {
          console.error('[HypergraphEditor] AGENTESE invoke failed:', err);
          setFeedbackMessage({ type: 'error', text: 'AGENTESE invoke failed' });
          setTimeout(() => setFeedbackMessage(null), 4000);
        }
      }
    },
    [dispatch, loadNode, focusNode, onNavigate, onNodeFocus, handleWrite, handleQuit, kblockHook]
  );

  // Handle command cancel
  const handleCommandCancel = useCallback(() => {
    setCommandLineVisible(false);
    dispatch({ type: 'EXIT_COMMAND' });
  }, [dispatch]);

  // Handle token navigation (from InteractiveDocument)
  // Called when user clicks an AGENTESE path or link in NORMAL mode
  const handleTokenNavigate = useCallback(
    async (path: string) => {
      console.info('[HypergraphEditor] Token navigate:', path);
      onNavigate?.(path);

      if (loadNode) {
        const node = await loadNode(path);
        if (node) {
          focusNode(node);
          onNodeFocus?.(node);
        } else {
          setFeedbackMessage({ type: 'warning', text: `Node not found: ${path}` });
          setTimeout(() => setFeedbackMessage(null), 3000);
        }
      }
    },
    [loadNode, focusNode, onNavigate, onNodeFocus]
  );

  // Handle task toggle (from InteractiveDocument)
  // Called when user clicks a checkbox in NORMAL mode
  const handleTaskToggle = useCallback(
    async (newState: boolean, taskId?: string) => {
      console.info('[HypergraphEditor] Task toggle:', { newState, taskId });

      // TODO: Integrate with K-Block to update content and persist
      // For now, just log the toggle - full implementation would:
      // 1. Parse the current content to find the task
      // 2. Update the checkbox state in the markdown
      // 3. Update K-Block working content
      // 4. Create a witness mark for the toggle
      setFeedbackMessage({
        type: 'success',
        text: `Task ${newState ? 'completed' : 'uncompleted'}`,
      });
      setTimeout(() => setFeedbackMessage(null), 2000);
    },
    []
  );

  // Get breadcrumb
  const breadcrumb = navigation.getTrailBreadcrumb();

  return (
    <div className="hypergraph-editor" data-mode={state.mode}>
      {/* Header */}
      <Header node={state.currentNode} />

      {/* Actions toolbar (visible when node focused) */}
      {state.currentNode && (
        <div className="hypergraph-editor__toolbar">
          {/* Proof Engine status badge */}
          <ProofStatusBadge
            layer={kblockHook.state?.zeroSeedLayer}
            kind={kblockHook.state?.zeroSeedKind}
            confidence={kblockHook.state?.confidence ?? 1.0}
            hasProof={kblockHook.state?.hasProof ?? false}
            isPanelOpen={proofPanelOpen}
            onTogglePanel={() => setProofPanelOpen((prev) => !prev)}
          />

          <button
            className="hypergraph-editor__action"
            onClick={handleReanalyze}
            disabled={!state.currentNode || isAnalyzing}
            title="Re-analyze document with Claude"
          >
            {isAnalyzing ? 'Analyzing...' : 'Re-analyze'}
          </button>
        </div>
      )}

      {/* Trail bar */}
      <TrailBar trail={breadcrumb} mode={state.mode} />

      {/* Main content area */}
      <div className="hypergraph-editor__main">
        {/* Left gutter (incoming edges) */}
        <EdgeGutter
          edges={state.currentNode?.incomingEdges || []}
          side="left"
          onEdgeClick={handleEdgeClick}
        />

        {/* Content pane */}
        <ContentPane
          ref={contentPaneRef}
          node={state.currentNode}
          mode={state.mode}
          cursor={state.cursor}
          workingContent={state.kblock?.workingContent}
          portals={state.portals}
          onContentChange={(content) => {
            // Update both reducer state and K-Block hook
            dispatch({ type: 'KBLOCK_UPDATED', content });
            kblockHook.updateContent(content);
          }}
          onCursorChange={(line, column) => {
            dispatch({ type: 'MOVE_CURSOR', position: { line, column } });
          }}
          onNavigate={handleTokenNavigate}
          onToggle={handleTaskToggle}
        />

        {/* Right gutter (outgoing edges) */}
        <EdgeGutter
          edges={state.currentNode?.outgoingEdges || []}
          side="right"
          onEdgeClick={handleEdgeClick}
        />

        {/* Proof Panel (collapsible side panel) */}
        <ProofPanel
          layer={kblockHook.state?.zeroSeedLayer}
          kind={kblockHook.state?.zeroSeedKind}
          confidence={kblockHook.state?.confidence ?? 1.0}
          hasProof={kblockHook.state?.hasProof ?? false}
          proof={kblockHook.state?.toulminProof}
          lineage={kblockHook.state?.lineage ?? []}
          parentBlocks={kblockHook.state?.parentBlocks ?? []}
          childBlocks={kblockHook.state?.childBlocks ?? []}
          onNavigate={(blockId) => {
            // Navigate to the block
            if (loadNode) {
              loadNode(blockId).then((node) => {
                if (node) {
                  focusNode(node);
                  onNodeFocus?.(node);
                  onNavigate?.(blockId);
                }
              });
            }
          }}
          isOpen={proofPanelOpen}
          onToggle={() => setProofPanelOpen((prev) => !prev)}
        />
      </div>

      {/* Command line (when visible) */}
      {commandLineVisible && (
        <CommandLine ref={commandLineRef} onSubmit={handleCommand} onCancel={handleCommandCancel} />
      )}

      {/* Command palette (Cmd+K) */}
      <CommandPalette
        open={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        onNavigate={(path) => {
          onNavigate?.(path);
          if (loadNode) {
            loadNode(path).then((node) => {
              if (node) {
                focusNode(node);
                onNodeFocus?.(node);
              }
            });
          }
        }}
        onWitnessMode={() => dispatch({ type: 'ENTER_WITNESS' })}
        onSave={handleWrite}
        onReanalyze={handleReanalyze}
        onAnalysisQuadrant={() => setAnalysisQuadrantOpen(true)}
        onAgentese={(path) => {
          console.info('[HypergraphEditor] AGENTESE invoked:', path);
          // TODO: Implement AGENTESE navigation/invocation
        }}
        onZeroSeed={onZeroSeed}
      />

      {/* Edge panel (when in EDGE mode) */}
      {state.mode === 'EDGE' && state.edgePending && <EdgePanel edgePending={state.edgePending} />}

      {/* Witness panel (when in WITNESS mode) */}
      {state.mode === 'WITNESS' && (
        <WitnessPanel
          onSave={handleWitnessSave}
          onCancel={() => dispatch({ type: 'EXIT_WITNESS' })}
          onQuickMark={handleQuickMark}
          loading={witnessLoading}
        />
      )}

      {/* Feedback message overlay */}
      {feedbackMessage && (
        <div
          className={`hypergraph-editor__feedback hypergraph-editor__feedback--${feedbackMessage.type}`}
        >
          {feedbackMessage.text}
        </div>
      )}

      {/* Help panel (? key) */}
      {helpVisible && <HelpPanel onClose={() => setHelpVisible(false)} />}

      {/* Confidence breakdown panel (gc toggle) */}
      {confidenceVisible && state.currentNode && (
        <div className="confidence-panel">
          <div className="confidence-panel__header">
            <span>Derivation Confidence</span>
            <button onClick={() => setConfidenceVisible(false)} className="confidence-panel__close">
              ×
            </button>
          </div>
          <div className="confidence-panel__content">
            <div className="confidence-panel__row">
              <span className="confidence-panel__label">Confidence:</span>
              <span className="confidence-panel__value">
                {state.currentNode.confidence !== undefined
                  ? `${Math.round(state.currentNode.confidence * 100)}%`
                  : 'Unknown'}
              </span>
            </div>
            <div className="confidence-panel__row">
              <span className="confidence-panel__label">Tier:</span>
              <span className="confidence-panel__value">
                {state.currentNode.derivationTier || state.currentNode.tier || 'Unknown'}
              </span>
            </div>
            {state.currentNode.derivationParent && (
              <div className="confidence-panel__row">
                <span className="confidence-panel__label">Parent:</span>
                <button
                  className="confidence-panel__link"
                  onClick={handleGoDerivationParent}
                  title="gD: Go to derivation parent"
                >
                  {state.currentNode.derivationParent.split('/').pop()}
                </button>
              </div>
            )}
            <div className="confidence-panel__hint">
              <kbd>gD</kbd> Navigate to parent • <kbd>Esc</kbd> Close
            </div>
          </div>
        </div>
      )}

      {/* Dialectic Modal (quick decision capture - Cmd+Shift+D) */}
      {dialecticModalOpen && (
        <DialecticModal
          onSave={handleDecisionSave}
          onClose={() => setDialecticModalOpen(false)}
          loading={dialecticLoading}
        />
      )}

      {/* DialogueView (full dialectic display) */}
      {dialogueViewOpen && selectedDecision && (
        <DialogueView
          decision={selectedDecision}
          onSave={handleDecisionSave}
          onClose={() => {
            setDialogueViewOpen(false);
            setSelectedDecision(null);
          }}
          onVeto={async () => {
            setVetoPanelOpen(true);
          }}
          loading={dialecticLoading}
          editable={false}
        />
      )}

      {/* DecisionStream (list of all decisions) */}
      {decisionStreamOpen && (
        <DecisionStream
          onDecisionClick={handleDecisionClick}
          onClose={() => setDecisionStreamOpen(false)}
        />
      )}

      {/* VetoPanel (disgust veto) */}
      {vetoPanelOpen && (
        <VetoPanel
          onVeto={handleVeto}
          onCancel={() => setVetoPanelOpen(false)}
          loading={dialecticLoading}
        />
      )}

      {/* DecisionFooterWidget (last decision in status area) */}
      {lastDecision && !decisionStreamOpen && (
        <DecisionFooterWidget
          lastDecision={lastDecision}
          onClick={handleDecisionClick}
          onClose={() => {
            // Hide footer by clearing decision (or add a flag)
          }}
        />
      )}

      {/* AnalysisQuadrant Modal (<leader>a) */}
      {analysisQuadrantOpen && state.currentNode && (
        <div className="hypergraph-editor__modal-overlay" onClick={() => setAnalysisQuadrantOpen(false)}>
          <div className="hypergraph-editor__modal-content" onClick={(e) => e.stopPropagation()}>
            <AnalysisQuadrant
              nodeId={state.currentNode.path}
              onClose={() => setAnalysisQuadrantOpen(false)}
            />
          </div>
        </div>
      )}

      {/* Status line */}
      <StatusLine
        mode={state.mode}
        cursor={state.cursor}
        breadcrumb={breadcrumb}
        pendingSequence={pendingSequence}
        kblockStatus={state.kblock?.isolation}
        nodePath={state.currentNode?.path}
        confidence={state.currentNode?.confidence}
        derivationTier={state.currentNode?.derivationTier}
        directorStatus={director.status ?? undefined}
      />
    </div>
  );
});
