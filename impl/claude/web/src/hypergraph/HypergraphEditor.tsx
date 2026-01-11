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
import { useNavigationWitness } from './useNavigationWitness';
import { useDerivationNavigation } from '../hooks/useDerivationNavigation';
import { StatusLine } from './StatusLine';
import { CommandLine } from './CommandLine';
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
import { Header, EdgeGutter, EdgeMetadataPanel, ContentPane } from './panes';
import type { ContentPaneRef } from './panes';
import type { GraphNode, Edge } from './state/types';
import { AnalysisQuadrant } from '../components/analysis/AnalysisQuadrant';
import { ProofPanel } from './ProofPanel';
import { ProofStatusBadge } from './ProofStatusBadge';
import { WitnessedTrail } from './WitnessedTrail';
import { AffordancePanel } from './AffordancePanel';
import { DerivationTrailBar } from './DerivationTrailBar';
import type { DerivationPath } from './DerivationTrailBar';
import { DerivationInspector } from './DerivationInspector';
import type {
  DerivationNode as InspectorDerivationNode,
  Witness,
  DownstreamKBlock,
} from './DerivationInspector';
import { CoherenceBadge } from './CoherenceBadge';
import { useDerivationStore, selectAllKBlocks } from '../stores/derivationStore';
import { useShallow } from 'zustand/react/shallow';

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
  onZeroSeed, // Note: Currently unused after CommandPalette removal, kept for potential future use
}: HypergraphEditorProps) {
  // Suppress unused warning for onZeroSeed (kept for API compatibility)
  void onZeroSeed;
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

  // Derivation navigation (Constitutional graph traversal)
  const derivationNav = useDerivationNavigation();

  // Global derivation store (Zustand) for coherence tracking
  // Actions are stable references - use direct access without selector to avoid getSnapshot issues
  const derivationStore = useDerivationStore;
  const computeDerivation = derivationStore.getState().computeDerivation;
  const groundKBlock = derivationStore.getState().groundKBlock;
  const setCurrentDerivationPath = derivationStore.getState().setCurrentDerivationPath;
  const realizeProject = derivationStore.getState().realizeProject;

  // Data selectors - primitives don't need useShallow, arrays/objects do
  const storeDerivationPath = useDerivationStore(
    useShallow((state) => state.currentDerivationPath)
  );
  const coherenceSummary = useDerivationStore(useShallow((state) => state.coherenceSummary));
  const derivationStoreLoading = useDerivationStore((state) => state.isLoading);

  // Get all K-Block IDs for project realization
  // Use useShallow to prevent infinite loop from array reference changes
  const allKBlocks = useDerivationStore(useShallow(selectAllKBlocks));

  // Witness navigation (fire-and-forget marking)
  // Stream 1: Wire navigation actions to create witness marks automatically
  // Every gD/gl/gh navigation creates a mark with principle scoring
  const { witnessNavigation, witnessMode } = useNavigationWitness({
    enabled: true,
    subscribe: false, // Don't subscribe to real-time for now
  });

  // Refs
  const commandLineRef = useRef<HTMLInputElement>(null);
  const contentPaneRef = useRef<ContentPaneRef>(null);

  // UI state
  const [commandLineVisible, setCommandLineVisible] = useState(false);
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

  // Edge metadata panel state
  const [edgePanelOpen, setEdgePanelOpen] = useState(false);

  // Navigation loading state - shows overlay while loading new document
  const [isNavigating, setIsNavigating] = useState(false);

  // Affordance panel state (? key to show)
  const [affordancePanelVisible, setAffordancePanelVisible] = useState(false);

  // Derivation trail bar state
  const [derivationPath, setDerivationPath] = useState<DerivationPath | null>(null);
  const [groundingDialogOpen, setGroundingDialogOpen] = useState(false);
  // Note: groundingDialogOpen is for future grounding dialog feature (TODO)
  void groundingDialogOpen; // Suppress unused warning

  // Derivation Inspector state (gd toggle)
  const [derivationInspectorOpen, setDerivationInspectorOpen] = useState(false);
  const [derivationInspectorLoading, setDerivationInspectorLoading] = useState(false);
  const [derivationInspectorData, setDerivationInspectorData] = useState<{
    derivationNodes: InspectorDerivationNode[];
    witnesses: Witness[];
    downstream: DownstreamKBlock[];
  }>({ derivationNodes: [], witnesses: [], downstream: [] });

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
          // Witness the navigation (fire-and-forget)
          witnessNavigation('derivation', node, parentNode, {
            keySequence: 'gD',
            viaEdge: 'derives_from',
          });
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
          // Witness the navigation (fire-and-forget)
          witnessNavigation('derivation', node, parentNode, {
            keySequence: 'gD',
            viaEdge: 'derives_from',
          });
          focusNode(parentNode);
          onNodeFocus?.(parentNode);
        }
      });
    }
  }, [state.currentNode, loadNode, focusNode, onNavigate, onNodeFocus, witnessNavigation]);

  /**
   * gc - Toggle confidence breakdown panel.
   * Shows derivation confidence details and ancestor chain.
   */
  const handleShowConfidence = useCallback(() => {
    setConfidenceVisible((prev) => !prev);
  }, []);

  // =============================================================================
  // Derivation Navigation Handlers (gh/gl/gj/gk/gG)
  // =============================================================================

  /**
   * gh - Navigate to derivation parent.
   * Uses the useDerivationNavigation hook for Constitutional graph traversal.
   */
  const handleGoDerivationParentNew = useCallback(async () => {
    const node = state.currentNode;
    if (!node) return;

    const parentNode = await derivationNav.goToParent();
    if (parentNode && loadNode) {
      // Witness the navigation
      witnessNavigation('derivation', node, { path: parentNode.path } as any, {
        keySequence: 'gh',
        viaEdge: 'derives_from',
      });

      // Load and navigate
      onNavigate?.(parentNode.path);
      loadNode(parentNode.path).then((graphNode) => {
        if (graphNode) {
          focusNode(graphNode);
          onNodeFocus?.(graphNode);
        }
      });

      setFeedbackMessage({
        type: 'success',
        text: `Navigated to parent: ${parentNode.title}`,
      });
      setTimeout(() => setFeedbackMessage(null), 3000);
    } else {
      setFeedbackMessage({
        type: 'warning',
        text: 'No derivation parent (at axiom)',
      });
      setTimeout(() => setFeedbackMessage(null), 3000);
    }
  }, [
    state.currentNode,
    derivationNav,
    loadNode,
    focusNode,
    onNavigate,
    onNodeFocus,
    witnessNavigation,
  ]);

  /**
   * gl - Navigate to derivation child.
   * Uses the useDerivationNavigation hook to follow derives_from edge down.
   */
  const handleGoDerivationChild = useCallback(async () => {
    const node = state.currentNode;
    if (!node) return;

    const childNode = await derivationNav.goToChild();
    if (childNode && loadNode) {
      // Witness the navigation
      witnessNavigation('derivation', node, { path: childNode.path } as any, {
        keySequence: 'gl',
        viaEdge: 'derives_from',
      });

      // Load and navigate
      onNavigate?.(childNode.path);
      loadNode(childNode.path).then((graphNode) => {
        if (graphNode) {
          focusNode(graphNode);
          onNodeFocus?.(graphNode);
        }
      });

      setFeedbackMessage({
        type: 'success',
        text: `Navigated to child: ${childNode.title}`,
      });
      setTimeout(() => setFeedbackMessage(null), 3000);
    } else {
      setFeedbackMessage({
        type: 'warning',
        text: 'No derivation children',
      });
      setTimeout(() => setFeedbackMessage(null), 3000);
    }
  }, [
    state.currentNode,
    derivationNav,
    loadNode,
    focusNode,
    onNavigate,
    onNodeFocus,
    witnessNavigation,
  ]);

  /**
   * gj - Navigate to next derivation sibling.
   * Same layer, same parent.
   */
  const handleGoDerivationNextSibling = useCallback(async () => {
    const node = state.currentNode;
    if (!node) return;

    const siblingNode = await derivationNav.goToNextSibling();
    if (siblingNode && loadNode) {
      // Witness the navigation
      witnessNavigation('sibling', node, { path: siblingNode.path } as any, {
        keySequence: 'gj',
        direction: 'next',
      });

      // Load and navigate
      onNavigate?.(siblingNode.path);
      loadNode(siblingNode.path).then((graphNode) => {
        if (graphNode) {
          focusNode(graphNode);
          onNodeFocus?.(graphNode);
        }
      });

      const siblingInfo =
        derivationNav.siblingCount > 1
          ? ` (${derivationNav.siblingIndex + 1}/${derivationNav.siblingCount})`
          : '';
      setFeedbackMessage({
        type: 'success',
        text: `Next sibling: ${siblingNode.title}${siblingInfo}`,
      });
      setTimeout(() => setFeedbackMessage(null), 3000);
    } else {
      setFeedbackMessage({
        type: 'warning',
        text: 'No more siblings',
      });
      setTimeout(() => setFeedbackMessage(null), 3000);
    }
  }, [
    state.currentNode,
    derivationNav,
    loadNode,
    focusNode,
    onNavigate,
    onNodeFocus,
    witnessNavigation,
  ]);

  /**
   * gk - Navigate to prev derivation sibling.
   * Same layer, same parent.
   */
  const handleGoDerivationPrevSibling = useCallback(async () => {
    const node = state.currentNode;
    if (!node) return;

    const siblingNode = await derivationNav.goToPrevSibling();
    if (siblingNode && loadNode) {
      // Witness the navigation
      witnessNavigation('sibling', node, { path: siblingNode.path } as any, {
        keySequence: 'gk',
        direction: 'prev',
      });

      // Load and navigate
      onNavigate?.(siblingNode.path);
      loadNode(siblingNode.path).then((graphNode) => {
        if (graphNode) {
          focusNode(graphNode);
          onNodeFocus?.(graphNode);
        }
      });

      const siblingInfo =
        derivationNav.siblingCount > 1
          ? ` (${derivationNav.siblingIndex + 1}/${derivationNav.siblingCount})`
          : '';
      setFeedbackMessage({
        type: 'success',
        text: `Prev sibling: ${siblingNode.title}${siblingInfo}`,
      });
      setTimeout(() => setFeedbackMessage(null), 3000);
    } else {
      setFeedbackMessage({
        type: 'warning',
        text: 'No more siblings',
      });
      setTimeout(() => setFeedbackMessage(null), 3000);
    }
  }, [
    state.currentNode,
    derivationNav,
    loadNode,
    focusNode,
    onNavigate,
    onNodeFocus,
    witnessNavigation,
  ]);

  /**
   * gG - Navigate to genesis (L1 axiom).
   * Traces derivation chain all the way to the root axiom.
   */
  const handleGoToGenesis = useCallback(async () => {
    const node = state.currentNode;
    if (!node) return;

    const genesisNode = await derivationNav.goToGenesis();
    if (genesisNode && loadNode) {
      // Witness the navigation
      witnessNavigation('genesis', node, { path: genesisNode.path } as any, {
        keySequence: 'gG',
        fromDepth: derivationNav.derivationDepth,
      });

      // Load and navigate
      onNavigate?.(genesisNode.path);
      loadNode(genesisNode.path).then((graphNode) => {
        if (graphNode) {
          focusNode(graphNode);
          onNodeFocus?.(graphNode);
        }
      });

      setFeedbackMessage({
        type: 'success',
        text: `Traced to axiom: ${genesisNode.title}`,
      });
      setTimeout(() => setFeedbackMessage(null), 3000);
    } else {
      setFeedbackMessage({
        type: 'warning',
        text: 'Already at genesis (axiom)',
      });
      setTimeout(() => setFeedbackMessage(null), 3000);
    }
  }, [
    state.currentNode,
    derivationNav,
    loadNode,
    focusNode,
    onNavigate,
    onNodeFocus,
    witnessNavigation,
  ]);

  // Track last computed path to prevent infinite loop
  const lastComputedDerivationPathRef = useRef<string | null>(null);

  // Update derivation navigation context when node changes
  // Note: derivationNav is stable across renders (hooks return stable references)
  // so we intentionally omit it from deps to prevent duplicate API calls
  useEffect(() => {
    const path = state.currentNode?.path;
    if (path) {
      // Guard: Don't recompute for the same path (prevents infinite loop)
      if (lastComputedDerivationPathRef.current === path) {
        return;
      }
      lastComputedDerivationPathRef.current = path;

      derivationNav.setCurrentNode(path);
      // Also compute derivation path via global store for coherence tracking
      computeDerivation(path);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.currentNode?.path, computeDerivation]);

  // Track last fetched path to prevent duplicate API calls
  const lastFetchedLineagePathRef = useRef<string | null>(null);

  // Fetch derivation path when current node changes
  // This populates the DerivationTrailBar with the constitutional trace
  useEffect(() => {
    const path = state.currentNode?.path;

    async function fetchDerivationPath() {
      if (!path) {
        setDerivationPath(null);
        return;
      }

      // Guard: Don't refetch for the same path (prevents duplicate calls)
      if (lastFetchedLineagePathRef.current === path) {
        return;
      }
      lastFetchedLineagePathRef.current = path;

      try {
        // Fetch derivation lineage from the API
        const response = await fetch(`/api/zero-seed/lineage?path=${encodeURIComponent(path)}`);

        if (!response.ok) {
          // If endpoint doesn't exist yet or fails, set orphan state
          setDerivationPath({
            nodes: [],
            state: 'orphan',
            totalLoss: 0,
            stateMessage: 'Derivation path not available',
          });
          return;
        }

        const lineage = await response.json();

        // Transform lineage into DerivationPath format
        if (lineage?.nodes && lineage.nodes.length > 0) {
          setDerivationPath({
            nodes: lineage.nodes,
            state: lineage.state || 'grounded',
            totalLoss: lineage.totalLoss || 0,
            stateMessage: lineage.stateMessage,
          });
        } else {
          // No lineage data - orphan state
          setDerivationPath({
            nodes: [],
            state: 'orphan',
            totalLoss: 0,
            stateMessage: 'No derivation path found',
          });
        }
      } catch (error) {
        console.warn('[HypergraphEditor] Failed to fetch derivation path:', error);
        setDerivationPath({
          nodes: [],
          state: 'orphan',
          totalLoss: 0,
          stateMessage: 'Failed to load derivation path',
        });
      }
    }

    fetchDerivationPath();
  }, [state.currentNode?.path]);

  // Fetch derivation inspector data when panel is opened or node changes
  useEffect(() => {
    async function fetchDerivationInspectorData() {
      if (!derivationInspectorOpen || !state.currentNode?.path) {
        return;
      }

      setDerivationInspectorLoading(true);
      try {
        // Fetch derivation trail (converts to InspectorDerivationNode format)
        const trail = await derivationNav.getDerivationTrail(state.currentNode.path);
        const derivationNodes: InspectorDerivationNode[] = trail.map((node, index) => ({
          id: node.id,
          label: node.title,
          layer: node.layer as 1 | 2 | 3 | 4 | 5 | 6 | 7 | undefined,
          kind: mapKindToInspectorKind(node.kind),
          pathLoss: index * 0.05, // Approximate path loss calculation
        }));

        // Fetch witnesses (from API or derive from node metadata)
        let witnesses: Witness[] = [];
        try {
          const witnessResponse = await fetch(
            `/api/zero-seed/witnesses?path=${encodeURIComponent(state.currentNode.path)}`
          );
          if (witnessResponse.ok) {
            const witnessData = await witnessResponse.json();
            witnesses = witnessData.witnesses || [];
          }
        } catch {
          // Witnesses endpoint may not exist yet - use empty array
        }

        // Fetch downstream K-Blocks
        let downstream: DownstreamKBlock[] = [];
        try {
          const children = await derivationNav.getChildren(state.currentNode.path);
          downstream = children.map((child) => ({
            id: child.id,
            label: child.title,
            pathLoss: 0.05, // Approximate
          }));
        } catch {
          // Children fetch may fail - use empty array
        }

        setDerivationInspectorData({ derivationNodes, witnesses, downstream });
      } catch (error) {
        console.warn('[HypergraphEditor] Failed to fetch derivation inspector data:', error);
      } finally {
        setDerivationInspectorLoading(false);
      }
    }

    fetchDerivationInspectorData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [derivationInspectorOpen, state.currentNode?.path]);

  /**
   * Helper to map node kind to DerivationInspector kind.
   */
  function mapKindToInspectorKind(kind: string): InspectorDerivationNode['kind'] {
    switch (kind.toLowerCase()) {
      case 'axiom':
      case 'constitution':
        return 'constitution';
      case 'principle':
        return 'principle';
      case 'spec':
      case 'specification':
        return 'spec';
      case 'impl':
      case 'implementation':
        return 'implementation';
      case 'test':
        return 'test';
      default:
        return 'other';
    }
  }

  /**
   * handleToggleDerivationInspector - Toggle the derivation inspector panel.
   * Triggered by 'gd' keyboard shortcut.
   */
  const handleToggleDerivationInspector = useCallback(() => {
    setDerivationInspectorOpen((prev) => !prev);
  }, []);

  /**
   * handleRederive - Trigger re-derivation of the current K-Block.
   */
  const handleRederive = useCallback(async () => {
    if (!state.currentNode?.path) return;

    setDerivationInspectorLoading(true);
    try {
      const response = await fetch('/api/zero-seed/rederive', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: state.currentNode.path }),
      });

      if (response.ok) {
        setFeedbackMessage({
          type: 'success',
          text: 'Re-derivation triggered',
        });
        // Refetch the derivation path
        setDerivationInspectorOpen(false);
        setTimeout(() => setDerivationInspectorOpen(true), 100);
      } else {
        throw new Error('Re-derivation failed');
      }
    } catch (error) {
      console.error('[HypergraphEditor] Re-derivation failed:', error);
      setFeedbackMessage({
        type: 'error',
        text: 'Re-derivation failed',
      });
    } finally {
      setDerivationInspectorLoading(false);
      setTimeout(() => setFeedbackMessage(null), 3000);
    }
  }, [state.currentNode?.path]);

  /**
   * handleDerivationNavigate - Navigate to a node from the derivation inspector.
   */
  const handleDerivationNavigate = useCallback(
    (kblockId: string) => {
      if (!loadNode) return;

      setIsNavigating(true);
      setDerivationInspectorOpen(false);
      onNavigate?.(kblockId);

      loadNode(kblockId)
        .then((node) => {
          setIsNavigating(false);
          if (node) {
            focusNode(node);
            onNodeFocus?.(node);
          }
        })
        .catch(() => {
          setIsNavigating(false);
        });
    },
    [loadNode, focusNode, onNavigate, onNodeFocus]
  );

  /**
   * handleDerivationNodeClick - Navigate to a node in the derivation trail.
   * Called when user clicks a node chip in the DerivationTrailBar.
   */
  const handleDerivationNodeClick = useCallback(
    (nodeId: string) => {
      if (!loadNode) return;

      // Start navigation
      setIsNavigating(true);
      onNavigate?.(nodeId);

      loadNode(nodeId)
        .then((node) => {
          setIsNavigating(false);
          if (node) {
            focusNode(node);
            onNodeFocus?.(node);
          } else {
            setFeedbackMessage({
              type: 'warning',
              text: `Node not found: ${nodeId}`,
            });
            setTimeout(() => setFeedbackMessage(null), 3000);
          }
        })
        .catch(() => {
          setIsNavigating(false);
        });
    },
    [loadNode, focusNode, onNavigate, onNodeFocus]
  );

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

    // Witness the mode transition
    witnessMode(state.mode, 'INSERT', state.currentNode.path);

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

      console.warn(
        '[HypergraphEditor] K-Block creation failed, using local fallback:',
        kblockResult.error
      );

      // Still create K-Block state so content updates work
      dispatch({ type: 'KBLOCK_CREATED', blockId: fallbackId, content: fallbackContent });
      dispatch({ type: 'ENTER_INSERT' });
    }
  }, [state.currentNode, state.mode, kblockHook, dispatch, witnessMode]);

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

  // Dialectic keyboard shortcuts and affordance panel toggle
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

      // ? key - Toggle affordance panel (only in NORMAL mode, not in INSERT/COMMAND)
      if (e.key === '?' && state.mode !== 'INSERT' && state.mode !== 'COMMAND') {
        e.preventDefault();
        setAffordancePanelVisible((prev) => !prev);
      }
    };

    window.addEventListener('keydown', handleDialecticKeys);
    return () => window.removeEventListener('keydown', handleDialecticKeys);
  }, [state.mode]);

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
        // Witness the navigation (fire-and-forget)
        witnessNavigation('loss_gradient', state.currentNode, node, {
          keySequence: 'gl',
          lossValue: lowest.loss,
        });

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
  }, [state.currentNode, lossNav, loadNode, focusNode, onNavigate, onNodeFocus, witnessNavigation]);

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
        // Witness the navigation (fire-and-forget)
        witnessNavigation('loss_gradient', state.currentNode, node, {
          keySequence: 'gh',
          lossValue: highest.loss,
        });

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
  }, [state.currentNode, lossNav, loadNode, focusNode, onNavigate, onNodeFocus, witnessNavigation]);

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
      const response = await fetch(
        `/api/witness/marks?path=${encodeURIComponent(state.currentNode.path)}`
      );
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
      const response = await fetch(
        `/api/witness/warrant?path=${encodeURIComponent(state.currentNode.path)}`
      );
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
      const response = await fetch(
        `/api/witness/fusion?path=${encodeURIComponent(state.currentNode.path)}`
      );
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
    // Derivation navigation (gh/gl/gj/gk/gG and gD/gc)
    goDerivationParent: handleGoDerivationParentNew, // gh - new derivation parent (via useDerivationNavigation)
    goDerivationChild: handleGoDerivationChild, // gl - derivation child
    goDerivationNextSibling: handleGoDerivationNextSibling, // gj already maps to sibling
    goDerivationPrevSibling: handleGoDerivationPrevSibling, // gk already maps to sibling
    goToGenesis: handleGoToGenesis, // gG - trace to axiom
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
    // Decision stream (witness history)
    onToggleDecisionStream: () => setDecisionStreamOpen((prev) => !prev),
    // Analysis quadrant
    onToggleAnalysisQuadrant: () => setAnalysisQuadrantOpen((prev) => !prev),
    // Edge metadata panel
    onToggleEdgePanel: () => setEdgePanelOpen((prev) => !prev),
    // Derivation inspector panel (gI toggle)
    onToggleDerivationInspector: handleToggleDerivationInspector,
    // Loss-gradient navigation (gL/gH — shifted to uppercase)
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
      !helpVisible &&
      !dialecticModalOpen &&
      !dialogueViewOpen &&
      state.mode !== 'WITNESS',
  });

  // Track if initial load has been performed for this path
  const initialLoadedRef = useRef<string | null>(null);

  // Load initial node - only once per unique path
  useEffect(() => {
    // Guard: Skip if we've already loaded this path or if loadNode is not available
    if (!initialPath || !loadNode) return;
    if (initialLoadedRef.current === initialPath) {
      console.info('[HypergraphEditor] Initial load already performed for:', initialPath);
      return;
    }

    // Mark as loading this path
    initialLoadedRef.current = initialPath;

    loadNode(initialPath).then((node) => {
      if (node) {
        focusNode(node);
        onNodeFocus?.(node);
      }
    });
  }, [initialPath, loadNode, focusNode, onNodeFocus]);

  // Realize project coherence on initial load (if we have K-Blocks)
  // This computes the coherenceSummary for the CoherenceBadge
  const hasInitializedCoherenceRef = useRef(false);
  useEffect(() => {
    // Only run once when we have K-Blocks to analyze
    if (hasInitializedCoherenceRef.current) return;
    if (allKBlocks.length > 0) {
      hasInitializedCoherenceRef.current = true;
      const kblockIds = allKBlocks.map((kb) => kb.id);
      realizeProject(kblockIds).catch((err) => {
        console.warn('[HypergraphEditor] Failed to realize project coherence:', err);
      });
    }
  }, [allKBlocks, realizeProject]);

  // Track last loaded siblings path to prevent duplicate loads
  const lastLoadedSiblingsPathRef = useRef<string | null>(null);

  // Load siblings when node changes
  useEffect(() => {
    const currentNode = state.currentNode;
    const path = currentNode?.path;

    if (currentNode && path && loadSiblings) {
      // Guard: Don't reload siblings for the same path (prevents duplicate calls)
      if (lastLoadedSiblingsPathRef.current === path) {
        return;
      }
      lastLoadedSiblingsPathRef.current = path;

      loadSiblings(currentNode).then((siblings) => {
        const index = siblings.findIndex((s) => s.path === path);
        dispatch({ type: 'SET_SIBLINGS', siblings, index: index >= 0 ? index : 0 });
      });
    }
    // Note: We intentionally only depend on path to prevent loops when currentNode
    // object reference changes but path stays the same. The guard ref prevents
    // duplicate calls for the same path.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.currentNode?.path, loadSiblings, dispatch]);

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

      // Start navigation - show loading state and collapse panels
      setIsNavigating(true);
      setEdgePanelOpen(false);
      setProofPanelOpen(false);

      onNavigate?.(targetPath);

      if (loadNode) {
        loadNode(targetPath)
          .then((node) => {
            setIsNavigating(false);
            if (node) {
              focusNode(node);
              onNodeFocus?.(node);
            }
          })
          .catch(() => {
            setIsNavigating(false);
          });
      } else {
        setIsNavigating(false);
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
        const message = reasoning ? `Saved "${path}" (${reasoning})` : `Saved "${path}"`;
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

      // NOTE: :e/:edit command removed — navigation is graph-first (click nodes, follow edges)
      // "The file is a lie. There is only the graph." Navigate by clicking, not by searching.
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
          console.warn(
            '[HypergraphEditor] :ag requires a path (e.g., :ag self.brain.capture "text")'
          );
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
      } else if (cmd === 'crystallize' || cmd === 'crystal') {
        // :crystallize [notes] - Crystallize current session
        const notes = args.join(' ') || undefined;

        try {
          const response = await fetch('/api/witness/crystallize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              notes,
            }),
          });

          if (response.ok) {
            const result = await response.json();
            console.info('[HypergraphEditor] Crystallization result:', result);
            setFeedbackMessage({
              type: 'success',
              text: `✓ Session crystallized (${result.crystal?.level || 'SESSION'})`,
            });
            setTimeout(() => setFeedbackMessage(null), 3000);
          } else {
            const error = await response.text();
            console.error('[HypergraphEditor] Crystallization error:', error);
            setFeedbackMessage({ type: 'error', text: `Crystallization: ${error}` });
            setTimeout(() => setFeedbackMessage(null), 4000);
          }
        } catch (err) {
          console.error('[HypergraphEditor] Crystallization failed:', err);
          setFeedbackMessage({ type: 'error', text: 'Crystallization failed' });
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

      // Start navigation - show loading state and collapse panels
      setIsNavigating(true);
      setEdgePanelOpen(false);
      setProofPanelOpen(false);

      onNavigate?.(path);

      if (loadNode) {
        try {
          const node = await loadNode(path);
          setIsNavigating(false);
          if (node) {
            focusNode(node);
            onNodeFocus?.(node);
          } else {
            setFeedbackMessage({ type: 'warning', text: `Node not found: ${path}` });
            setTimeout(() => setFeedbackMessage(null), 3000);
          }
        } catch {
          setIsNavigating(false);
        }
      } else {
        setIsNavigating(false);
      }
    },
    [loadNode, focusNode, onNavigate, onNodeFocus]
  );

  // Handle task toggle (from InteractiveDocument)
  // Called when user clicks a checkbox in NORMAL mode
  const handleTaskToggle = useCallback(async (newState: boolean, taskId?: string) => {
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
  }, []);

  // Get breadcrumb
  const breadcrumb = navigation.getTrailBreadcrumb();

  return (
    <div className="hypergraph-editor" data-mode={state.mode}>
      {/* Header */}
      <Header node={state.currentNode} />

      {/* Derivation Trail Bar - Constitutional breadcrumb */}
      <DerivationTrailBar
        currentKBlockId={state.currentNode?.path || null}
        derivationPath={derivationPath}
        onNodeClick={handleDerivationNodeClick}
        onGroundClick={() => setGroundingDialogOpen(true)}
        onTraceToAxiom={handleGoToGenesis}
        derivationDepth={derivationNav.derivationDepth}
        showKeyboardHints={true}
        enablePathAnimation={true}
      />

      {/* Actions toolbar (visible when node focused) */}
      {state.currentNode && (
        <div className="hypergraph-editor__toolbar">
          {/* Coherence Badge - project-wide coherence metrics */}
          <CoherenceBadge
            summary={coherenceSummary}
            size="sm"
            expanded={false}
            loading={derivationStoreLoading}
            showGaloisLoss={true}
            showCounts={false}
          />

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

          <button
            className={`hypergraph-editor__action ${derivationInspectorOpen ? 'hypergraph-editor__action--active' : ''}`}
            onClick={handleToggleDerivationInspector}
            title="Toggle derivation inspector (gI)"
          >
            Derivation
          </button>
        </div>
      )}

      {/* Trail bar with witness marks */}
      <WitnessedTrail
        trail={state.trail}
        currentNode={state.currentNode}
        onNavigate={(_stepIndex, nodePath) => {
          if (loadNode) {
            loadNode(nodePath).then((node) => {
              if (node) {
                focusNode(node);
                onNodeFocus?.(node);
                onNavigate?.(nodePath);
              }
            });
          }
        }}
        showPrinciples={true}
        showCompression={true}
        compact={false}
        maxVisible={7}
      />

      {/* Main content area */}
      <div
        className={`hypergraph-editor__main ${isNavigating ? 'hypergraph-editor__main--loading' : ''}`}
      >
        {/* Loading overlay - shown during navigation */}
        {isNavigating && (
          <div className="hypergraph-editor__loading-overlay">
            <div className="hypergraph-editor__loading-spinner" />
          </div>
        )}

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

        {/* Edge Metadata Panel (collapsible right sidebar - gE toggle) */}
        <EdgeMetadataPanel
          incomingEdges={state.currentNode?.incomingEdges || []}
          outgoingEdges={state.currentNode?.outgoingEdges || []}
          currentNodePath={state.currentNode?.path}
          onEdgeClick={handleEdgeClick}
          isOpen={edgePanelOpen}
          onToggle={() => setEdgePanelOpen((prev) => !prev)}
        />

        {/* Derivation Inspector Panel (collapsible right sidebar - gI toggle) */}
        <DerivationInspector
          kblockId={state.currentNode?.path || ''}
          derivationPath={derivationInspectorData.derivationNodes}
          witnesses={derivationInspectorData.witnesses}
          downstream={derivationInspectorData.downstream}
          onClose={() => setDerivationInspectorOpen(false)}
          onRederive={handleRederive}
          onViewProof={() => {
            setDerivationInspectorOpen(false);
            setProofPanelOpen(true);
          }}
          onNavigate={handleDerivationNavigate}
          isOpen={derivationInspectorOpen}
          loading={derivationInspectorLoading}
        />
      </div>

      {/* Command line (when visible) */}
      {commandLineVisible && (
        <CommandLine ref={commandLineRef} onSubmit={handleCommand} onCancel={handleCommandCancel} />
      )}

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
        <div
          className="hypergraph-editor__modal-overlay"
          onClick={() => setAnalysisQuadrantOpen(false)}
        >
          <div className="hypergraph-editor__modal-content" onClick={(e) => e.stopPropagation()}>
            <AnalysisQuadrant
              nodeId={state.currentNode.path}
              onClose={() => setAnalysisQuadrantOpen(false)}
            />
          </div>
        </div>
      )}

      {/* Affordance Panel (? key or hover) */}
      <AffordancePanel
        node={state.currentNode}
        mode={state.mode}
        isVisible={affordancePanelVisible}
        onClose={() => setAffordancePanelVisible(false)}
        derivationInfo={
          derivationNav.derivationDepth > 0
            ? {
                parentCount: derivationNav.derivationDepth > 0 ? 1 : 0,
                childCount: 0, // Not tracked by hook, could be fetched if needed
                siblingCount: derivationNav.siblingCount,
                layer: derivationNav.derivationDepth,
              }
            : undefined
        }
      />

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
        coherenceSummary={coherenceSummary}
      />
    </div>
  );
});
