/**
 * Portal Page - Source file exploration via portal tokens
 *
 * "You don't go to the document. The document comes to you."
 *
 * Provides a dedicated view for exploring source file connections
 * through the portal token system.
 *
 * Phase 5C: Adds collaborative editing with agent proposals.
 *
 * @see spec/protocols/portal-token.md Phase 5.3
 * @see spec/protocols/context-perception.md §6
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileCode,
  FolderOpen,
  RefreshCw,
  Expand,
  ChevronRight,
  Loader2,
  AlertCircle,
  TreePine,
  Sparkles,
  PanelRightOpen,
  PanelRightClose,
} from 'lucide-react';
import {
  PortalTree,
  ProposalList,
  ProposalBadge,
  TrailPanel,
  TrailIndicator,
} from '@/components/portal';
import type { CollaborationEvent } from '@/components/portal';
import { usePortalTree, PORTAL_EDGE_CONFIG } from '@/api/portal';
import { useCollaboration, type Proposal } from '@/api/collaboration';
import { createTrail, computeEvidenceStrength, type Trail, type TrailStep, type TrailEvidence } from '@/api/trail';
import { Breathe } from '@/components/joy';

// =============================================================================
// Constants
// =============================================================================

/**
 * Example file paths for quick exploration.
 */
const EXAMPLE_PATHS = [
  'impl/claude/services/brain/persistence.py',
  'impl/claude/services/witness/bus.py',
  'impl/claude/protocols/agentese/gateway.py',
  'impl/claude/protocols/context/collaboration.py',
];

// =============================================================================
// Page Component
// =============================================================================

export default function PortalPage() {
  const navigate = useNavigate();

  // State for file path input
  const [inputPath, setInputPath] = useState('');
  const [currentPath, setCurrentPath] = useState<string | null>(null);
  const [showProposals, setShowProposals] = useState(true);
  const [showTrailPanel, setShowTrailPanel] = useState(true);
  const [witnessError, setWitnessError] = useState<string | null>(null);

  // Portal tree state
  const { tree, loading, error, loadTree, expand, collapse, isExpanding } = usePortalTree();

  // Trail breadcrumbs (expansion history)
  const [trail, setTrail] = useState<string[]>([]);

  // Session trail state (for TrailPanel)
  const [sessionTrail, setSessionTrail] = useState<Trail | null>(null);
  const [sessionEvidence, setSessionEvidence] = useState<TrailEvidence | null>(null);
  const [selectedStep, setSelectedStep] = useState<number | null>(null);
  const [collaborationEvents, setCollaborationEvents] = useState<CollaborationEvent[]>([]);
  const [isWitnessing, setIsWitnessing] = useState(false);

  // Track collaboration events for TrailPanel
  const handleProposalAccepted = useCallback((proposal: Proposal) => {
    const event: CollaborationEvent = {
      type: 'proposal_accepted',
      proposalId: proposal.id,
      agentName: proposal.agent_name,
      description: proposal.description,
      timestamp: new Date().toISOString(),
      stepIndex: sessionTrail?.steps.length ? sessionTrail.steps.length - 1 : undefined,
    };
    setCollaborationEvents((prev) => [...prev, event]);
  }, [sessionTrail]);

  const handleProposalRejected = useCallback((proposal: Proposal) => {
    const event: CollaborationEvent = {
      type: 'proposal_rejected',
      proposalId: proposal.id,
      agentName: proposal.agent_name,
      description: proposal.description,
      timestamp: new Date().toISOString(),
      stepIndex: sessionTrail?.steps.length ? sessionTrail.steps.length - 1 : undefined,
    };
    setCollaborationEvents((prev) => [...prev, event]);
  }, [sessionTrail]);

  const handleAutoAccept = useCallback((proposal: Proposal) => {
    console.log('[Portal] Proposal auto-accepted:', proposal.id);
    const event: CollaborationEvent = {
      type: 'auto_accepted',
      proposalId: proposal.id,
      agentName: proposal.agent_name,
      description: proposal.description,
      timestamp: new Date().toISOString(),
      stepIndex: sessionTrail?.steps.length ? sessionTrail.steps.length - 1 : undefined,
    };
    setCollaborationEvents((prev) => [...prev, event]);
  }, [sessionTrail]);

  // Collaboration state (Phase 5C)
  const {
    proposals,
    isHumanTyping,
    isConnected: collaborationConnected,
    accept: baseAcceptProposal,
    reject: baseRejectProposal,
    recordKeystroke,
  } = useCollaboration({
    autoConnect: true,
    location: currentPath || undefined,
    onAutoAccept: handleAutoAccept,
  });

  // Wrap accept/reject to track events
  const acceptProposal = useCallback(async (proposalId: string) => {
    const proposal = proposals.find((p) => p.id === proposalId);
    await baseAcceptProposal(proposalId);
    if (proposal) handleProposalAccepted(proposal);
  }, [baseAcceptProposal, proposals, handleProposalAccepted]);

  const rejectProposal = useCallback(async (proposalId: string) => {
    const proposal = proposals.find((p) => p.id === proposalId);
    await baseRejectProposal(proposalId);
    if (proposal) handleProposalRejected(proposal);
  }, [baseRejectProposal, proposals, handleProposalRejected]);

  // Keystroke tracking - debounced
  const keystrokeTimeoutRef = useRef<number | null>(null);
  const lastKeystrokeLocationRef = useRef<string | null>(null);

  // Build session trail step
  const addTrailStep = useCallback((sourcePath: string, edge: string | null, destinations: string[]) => {
    setSessionTrail((prev) => {
      const newStep: TrailStep = {
        index: prev?.steps.length ?? 0,
        source_path: sourcePath,
        edge,
        destination_paths: destinations,
        reasoning: null,
        loop_status: 'none',
        created_at: new Date().toISOString(),
      };

      if (!prev) {
        // Create new trail
        const trail: Trail = {
          trail_id: `session-${Date.now()}`,
          name: `Portal Session ${new Date().toLocaleTimeString()}`,
          steps: [newStep],
          annotations: {},
          version: 1,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          forked_from_id: null,
          topics: [],
        };
        return trail;
      }

      // Add to existing trail
      return {
        ...prev,
        steps: [...prev.steps, newStep],
        updated_at: new Date().toISOString(),
      };
    });

    // Update evidence
    setSessionEvidence((prev) => {
      const stepCount = (prev?.step_count ?? 0) + 1;
      const uniquePaths = new Set([
        ...(prev ? Array(prev.unique_paths).fill(0).map((_, i) => `path-${i}`) : []),
        sourcePath,
        ...destinations,
      ]).size;
      const uniqueEdges = new Set([
        ...(prev ? Array(prev.unique_edges).fill(0).map((_, i) => `edge-${i}`) : []),
        ...(edge ? [edge] : []),
      ]).size;

      return {
        step_count: stepCount,
        unique_paths: uniquePaths,
        unique_edges: uniqueEdges,
        evidence_strength: computeEvidenceStrength(stepCount, uniquePaths),
      };
    });
  }, []);

  // Load a file's portals
  const handleLoad = useCallback(
    async (path: string) => {
      setCurrentPath(path);
      setTrail([path.split('/').pop() || path]);

      // Start new session trail
      setSessionTrail(null);
      setSessionEvidence(null);
      setCollaborationEvents([]);
      addTrailStep(path, null, []);

      await loadTree(path);
    },
    [loadTree, addTrailStep]
  );

  // Handle form submission
  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (inputPath.trim()) {
        handleLoad(inputPath.trim());
      }
    },
    [inputPath, handleLoad]
  );

  // Handle expansion with trail tracking
  const handleExpand = useCallback(
    async (path: string[], edgeType?: string) => {
      await expand(path, edgeType);
      // Add to breadcrumb trail
      const label = edgeType || path[path.length - 1] || 'expand';
      setTrail((prev) => [...prev, label]);

      // Add to session trail
      const sourcePath = path.join('/');
      addTrailStep(sourcePath, edgeType || 'expand', []);
    },
    [expand, addTrailStep]
  );

  // Handle collapse
  const handleCollapse = useCallback(
    async (path: string[]) => {
      await collapse(path);
      // Remove from trail (simplistic - removes last entry)
      setTrail((prev) => prev.slice(0, -1));
    },
    [collapse]
  );

  // Handle step selection in TrailPanel
  const handleSelectStep = useCallback((stepIndex: number) => {
    setSelectedStep(stepIndex);
    // TODO: Could highlight the corresponding node in the portal tree
  }, []);

  // Handle witness action - persist trail and navigate to Trail view
  const handleWitness = useCallback(async () => {
    if (!sessionTrail || sessionTrail.steps.length < 3) return;

    setIsWitnessing(true);
    setWitnessError(null);

    try {
      // Convert session trail steps to API format
      const apiSteps = sessionTrail.steps.map((step) => ({
        path: step.source_path,
        edge: step.edge || undefined,
        reasoning: step.reasoning || undefined,
      }));

      // Create the trail via AGENTESE API
      const result = await createTrail(sessionTrail.name, apiSteps, sessionTrail.topics);

      // Add a collaboration event to note the witness
      setCollaborationEvents((prev) => [
        ...prev,
        {
          type: 'proposal_accepted',
          proposalId: `witness-${Date.now()}`,
          agentName: 'Witness',
          description: `Trail witnessed (${result.step_count} steps)`,
          timestamp: new Date().toISOString(),
        },
      ]);

      // Navigate to the trail graph view
      navigate(`/_/trail/${result.trail_id}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to witness trail';
      setWitnessError(message);
      console.error('[Portal] Witness error:', err);
    } finally {
      setIsWitnessing(false);
    }
  }, [sessionTrail, navigate]);

  // Handle fork action
  const handleFork = useCallback(async (name: string, forkPoint?: number) => {
    if (!sessionTrail) return;
    // TODO: Call API to fork the trail
    console.log('[Portal] Forking trail:', name, 'at step:', forkPoint);
  }, [sessionTrail]);

  // Expand all portals
  const handleExpandAll = useCallback(async () => {
    if (currentPath) {
      await loadTree(currentPath, true);
    }
  }, [currentPath, loadTree]);

  // Handle input change with keystroke tracking
  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setInputPath(value);

      // Debounced keystroke recording
      if (keystrokeTimeoutRef.current) {
        window.clearTimeout(keystrokeTimeoutRef.current);
      }

      const location = value || 'portal.input';
      if (location !== lastKeystrokeLocationRef.current) {
        lastKeystrokeLocationRef.current = location;
        keystrokeTimeoutRef.current = window.setTimeout(() => {
          recordKeystroke(location);
        }, 100);
      }
    },
    [recordKeystroke]
  );

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (keystrokeTimeoutRef.current) {
        window.clearTimeout(keystrokeTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-surface-canvas p-6">
      {/* Header */}
      <div className="max-w-6xl mx-auto mb-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <TreePine className="w-6 h-6 text-emerald-500" />
            <h1 className="text-2xl font-bold text-white">Portal Explorer</h1>
          </div>
          {/* Status bar */}
          <div className="flex items-center gap-3">
            {/* Trail indicator */}
            {sessionTrail && sessionTrail.steps.length > 0 && (
              <TrailIndicator
                stepCount={sessionTrail.steps.length}
                strength={sessionEvidence?.evidence_strength}
                onClick={() => setShowTrailPanel(!showTrailPanel)}
              />
            )}
            {/* Proposals */}
            {proposals.length > 0 && (
              <ProposalBadge
                count={proposals.length}
                onClick={() => setShowProposals(!showProposals)}
              />
            )}
            {/* Collaboration status */}
            {collaborationConnected && (
              <span className="flex items-center gap-1.5 text-xs text-green-400">
                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                Collaborative
              </span>
            )}
            {isHumanTyping && (
              <span className="text-xs text-yellow-400">Typing...</span>
            )}
            {/* Trail panel toggle */}
            <button
              onClick={() => setShowTrailPanel(!showTrailPanel)}
              className={`p-1.5 rounded transition-colors ${
                showTrailPanel ? 'bg-blue-600/30 text-blue-400' : 'text-gray-400 hover:bg-gray-700'
              }`}
              title={showTrailPanel ? 'Hide trail panel' : 'Show trail panel'}
            >
              {showTrailPanel ? (
                <PanelRightClose className="w-4 h-4" />
              ) : (
                <PanelRightOpen className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
        <p className="text-gray-400 text-sm">
          Navigate source file connections. Expand portals to explore imports, tests, and more.
        </p>
      </div>

      {/* Agent Proposals Panel (Phase 5C) */}
      {showProposals && proposals.length > 0 && (
        <div className="max-w-6xl mx-auto mb-6">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-medium text-purple-200">Agent Proposals</span>
            <button
              onClick={() => setShowProposals(false)}
              className="ml-auto text-xs text-gray-500 hover:text-gray-300"
            >
              Hide
            </button>
          </div>
          <ProposalList
            proposals={proposals}
            onAccept={acceptProposal}
            onReject={rejectProposal}
          />
        </div>
      )}

      {/* Main content area with optional trail panel */}
      <div className="max-w-6xl mx-auto flex gap-6">
        {/* Left side: Main content */}
        <div className={showTrailPanel ? 'flex-1 min-w-0' : 'w-full'}>
          {/* File Picker */}
          <div className="mb-6">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <div className="flex-1 relative">
                <FolderOpen className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  type="text"
                  value={inputPath}
                  onChange={handleInputChange}
                  placeholder="Enter file path (e.g., impl/claude/services/brain/core.py)"
                  className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg
                    text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <button
                type="submit"
                disabled={loading || !inputPath.trim()}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700
                  disabled:cursor-not-allowed text-white rounded-lg transition-colors
                  flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  <>
                    <FileCode className="w-4 h-4" />
                    Explore
                  </>
                )}
              </button>
            </form>

            {/* Quick picks */}
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="text-gray-500 text-xs">Quick picks:</span>
              {EXAMPLE_PATHS.map((path) => (
                <button
                  key={path}
                  onClick={() => {
                    setInputPath(path);
                    handleLoad(path);
                  }}
                  className="px-2 py-0.5 text-xs bg-gray-800 hover:bg-gray-700 text-gray-400
                    hover:text-white rounded transition-colors"
                >
                  {path.split('/').pop()}
                </button>
              ))}
            </div>
          </div>

          {/* Trail Breadcrumbs */}
          {trail.length > 0 && (
            <div className="mb-4">
              <div className="flex items-center gap-1 text-sm text-gray-500 overflow-x-auto">
                {trail.map((crumb, index) => (
                  <span key={index} className="flex items-center">
                    {index > 0 && <ChevronRight className="w-4 h-4 mx-1" />}
                    <span
                      className={`px-1.5 py-0.5 rounded ${
                        index === trail.length - 1
                          ? 'bg-gray-700 text-white'
                          : 'hover:bg-gray-800 cursor-pointer'
                      }`}
                    >
                      {crumb}
                    </span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Error Display */}
          {(error || witnessError) && (
            <div className="mb-4">
              <div className="flex items-center gap-2 p-3 bg-red-950/30 border border-red-900 rounded-lg text-red-400">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <span>{error || witnessError}</span>
              </div>
            </div>
          )}

          {/* Portal Tree - grows naturally with content, page scrolls */}
          <div>
            {tree ? (
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg">
                {/* Tree Header */}
                <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800">
                  <div className="flex items-center gap-2 text-gray-400 text-sm">
                    <FileCode className="w-4 h-4" />
                    <span>{currentPath}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleExpandAll}
                      disabled={loading}
                      className="p-1.5 hover:bg-gray-700 rounded transition-colors"
                      title="Expand All"
                    >
                      <Expand className="w-4 h-4 text-gray-400" />
                    </button>
                    <button
                      onClick={() => currentPath && handleLoad(currentPath)}
                      disabled={loading}
                      className="p-1.5 hover:bg-gray-700 rounded transition-colors"
                      title="Refresh"
                    >
                      <Breathe intensity={loading ? 0.3 : 0} speed="fast">
                        <RefreshCw
                          className={`w-4 h-4 text-gray-400 ${loading ? 'animate-spin' : ''}`}
                        />
                      </Breathe>
                    </button>
                  </div>
                </div>

                {/* Tree Content - grows naturally, no max-height constraint */}
                <div className="p-4">
                  <PortalTree
                    root={tree.root}
                    onExpand={handleExpand}
                    onCollapse={handleCollapse}
                    isExpanding={isExpanding}
                  />
                </div>
              </div>
            ) : !loading ? (
              <div className="bg-gray-900/30 border border-gray-800 rounded-lg p-12">
                <div className="flex flex-col items-center text-center">
                  <TreePine className="w-16 h-16 text-gray-700 mb-4" />
                  <h2 className="text-xl text-gray-400 mb-2">No file selected</h2>
                  <p className="text-gray-500 text-sm max-w-md">
                    Enter a file path above or select a quick pick to explore its connections.
                    Portals reveal imports, tests, specs, and more.
                  </p>
                </div>
              </div>
            ) : null}
          </div>

          {/* Edge Type Legend */}
          <div className="mt-6">
            <div className="flex flex-wrap gap-4 text-xs text-gray-500">
              <span className="font-medium">Edge types:</span>
              {Object.entries(PORTAL_EDGE_CONFIG)
                .filter(([key]) => key !== 'default')
                .map(([type, config]) => (
                  <span key={type} className="flex items-center gap-1">
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: config.color }}
                    />
                    {type}
                  </span>
                ))}
            </div>
          </div>
        </div>

        {/* Right side: Trail Panel (Phase 5D) */}
        {showTrailPanel && (
          <div className="w-80 flex-shrink-0">
            <div className="sticky top-6">
              <TrailPanel
                trail={sessionTrail}
                evidence={sessionEvidence}
                collaborationEvents={collaborationEvents}
                selectedStep={selectedStep}
                onSelectStep={handleSelectStep}
                onWitness={handleWitness}
                onFork={handleFork}
                isWitnessing={isWitnessing}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
