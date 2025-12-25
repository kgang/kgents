/**
 * HypergraphStudio: Graph + Trail
 *
 * "The file is a lie. There is only the graph."
 *
 * UX TRANSFORMATION (2025-12-25): ValueCompass removed per Kent's decision.
 *
 * A construction composing two primitives for the hypergraph editing experience:
 * - Graph (HypergraphEditor): Modal editing with K-Block isolation
 * - Trail: Derivation breadcrumb showing navigation path
 *
 * Layout:
 * ┌─────────────────────────────────────────────────────────┐
 * │ Trail (derivation chain)                                 │
 * ├─────────────────────────────────────────────────────────┤
 * │                                                          │
 * │  HypergraphEditor (from Graph primitive)                 │
 * │  (main editing area)                                     │
 * │                                                          │
 * └─────────────────────────────────────────────────────────┘
 *
 * @see docs/skills/hypergraph-editor.md
 */

import { memo, useState, useCallback, useMemo } from 'react';
import { HypergraphEditor } from '@/primitives/Graph';
import { Trail } from '@/primitives/Trail';
import type { GraphNode } from '@/primitives/Graph';
import type { PolicyTrace } from '@/types/theory';
import './HypergraphStudio.css';

// =============================================================================
// Types
// =============================================================================

export interface HypergraphStudioProps {
  /** Initial file path to open */
  initialPath?: string;

  /** Policy trace for session */
  policyTrace?: PolicyTrace;

  /** File save handler */
  onSave?: (path: string, content: string) => void;

  /** Navigation callback */
  onNavigate?: (path: string) => void;

  /** Zero Seed navigation callback (legacy, kept for API compat) */
  onZeroSeed?: (tab?: string) => void;

  /** External node loader (for custom data sources) */
  loadNode?: (path: string) => Promise<GraphNode | null>;

  /** External sibling loader (for custom data sources) */
  loadSiblings?: (node: GraphNode) => Promise<GraphNode[]>;
}

// =============================================================================
// Component
// =============================================================================

export const HypergraphStudio = memo(function HypergraphStudio({
  initialPath,
  policyTrace,
  onSave: _onSave, // Reserved for future K-Block save integration
  onNavigate,
  onZeroSeed,
  loadNode,
  loadSiblings,
}: HypergraphStudioProps) {
  // UI state
  const [currentNode, setCurrentNode] = useState<GraphNode | null>(null);
  const [navigationPath, setNavigationPath] = useState<string[]>([]);

  // =============================================================================
  // Trail Management
  // =============================================================================

  /**
   * Build trail path from current node's navigation history.
   * The trail shows the derivation/navigation chain leading to current node.
   */
  const trailPath = useMemo(() => {
    if (!currentNode) return [];

    // If we have explicit navigation path, use it
    if (navigationPath.length > 0) {
      return navigationPath;
    }

    // Otherwise, build from node metadata
    const path: string[] = [];

    // Add derivation parent chain (if available)
    if (currentNode.derivationParent) {
      path.push(currentNode.derivationParent);
    }

    // Add current node
    path.push(currentNode.path);

    return path;
  }, [currentNode, navigationPath]);

  /**
   * Handle trail step click - navigate back to that point.
   */
  const handleTrailStepClick = useCallback(
    (stepIndex: number, stepId: string) => {
      // Truncate navigation path at this point
      setNavigationPath((prev) => prev.slice(0, stepIndex + 1));

      // Trigger navigation
      onNavigate?.(stepId);
    },
    [onNavigate]
  );

  // =============================================================================
  // Graph Event Handlers
  // =============================================================================

  /**
   * Handle node focus - update current node and trail.
   */
  const handleNodeFocus = useCallback((node: GraphNode) => {
    setCurrentNode(node);

    // Add to navigation path if not already present
    setNavigationPath((prev) => {
      // Avoid duplicates
      if (prev[prev.length - 1] === node.path) {
        return prev;
      }
      return [...prev, node.path];
    });
  }, []);

  /**
   * Handle navigation - update trail and notify parent.
   */
  const handleNavigate = useCallback(
    (path: string) => {
      onNavigate?.(path);
    },
    [onNavigate]
  );

  // =============================================================================
  // Trail Metadata
  // =============================================================================

  /**
   * Get compression ratio from policy trace.
   */
  const compressionRatio = useMemo(() => {
    return policyTrace?.compressionRatio;
  }, [policyTrace]);

  // =============================================================================
  // Render
  // =============================================================================

  return (
    <div className="hypergraph-studio">
      {/* Trail - shows navigation/derivation path */}
      <div className="hypergraph-studio__trail">
        <Trail
          path={trailPath}
          compressionRatio={compressionRatio}
          onStepClick={handleTrailStepClick}
          currentIndex={trailPath.length - 1}
          maxVisible={7}
        />
      </div>

      {/* Main editor area */}
      <div className="hypergraph-studio__main">
        <HypergraphEditor
          initialPath={initialPath}
          onNodeFocus={handleNodeFocus}
          onNavigate={handleNavigate}
          onZeroSeed={onZeroSeed}
          loadNode={loadNode}
          loadSiblings={loadSiblings}
        />
      </div>

      {/* ValueCompass panel removed per UX transformation (2025-12-25) */}
    </div>
  );
});

export default HypergraphStudio;
