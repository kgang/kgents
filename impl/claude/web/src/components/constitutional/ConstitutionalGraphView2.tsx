/**
 * ConstitutionalGraphView2 - Visualize K-Block derivation graph.
 *
 * "Simplistic, brutalistic, dense, intelligent design."
 * "Kent should see his constitution at a glance."
 *
 * Displays the L0->L1->L2->L3 derivation chains with:
 * - Layers as horizontal bands (L0 at bottom, L3 at top)
 * - Nodes showing block name, Galois loss, evidence tier
 * - Edges showing derivation relationships
 * - Click node to see full derivation path + downstream impact
 * - Orphan blocks highlighted in warning color
 * - Three density modes (compact/comfortable/spacious)
 *
 * Philosophy:
 *   "The proof IS the decision. The mark IS the witness."
 *
 * @see services/zero_seed/ashc_self_awareness.py
 * @see docs/skills/elastic-ui-patterns.md
 */

import { memo, useEffect, useRef, useCallback, useMemo } from 'react';
import { useWindowLayout } from '@/hooks/useLayoutContext';
import { useConstitutionalGraphStore } from '@/stores/constitutionalGraphStore';
import { ConstitutionalNode } from './ConstitutionalNode';
import { DerivationEdge } from './DerivationEdge';
import { LayerBand } from './LayerBand';
import type { EpistemicLayer, DensityMode, GroundingResult } from './graphTypes';
import { DENSITY_SIZES, LAYER_NAMES, LAYER_COLORS, EVIDENCE_TIER_COLORS } from './graphTypes';
import './ConstitutionalGraphView2.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionalGraphView2Props {
  /** Optional initial selected block */
  initialSelectedBlock?: string;
  /** Callback when a block is selected */
  onBlockSelect?: (blockId: string | null, groundingResult: GroundingResult | null) => void;
  /** Whether to show the detail panel */
  showDetailPanel?: boolean;
  /** Optional class name */
  className?: string;
}

// =============================================================================
// Detail Panel Component
// =============================================================================

interface DetailPanelProps {
  blockId: string | null;
  groundingResult: GroundingResult | null;
  density: DensityMode;
  onClose: () => void;
}

const DetailPanel = memo(function DetailPanel({
  blockId,
  groundingResult,
  density: _density,
  onClose,
}: DetailPanelProps) {
  // Note: density param reserved for future density-aware styling
  const blocks = useConstitutionalGraphStore((s) => s.blocks);
  const block = blockId ? blocks.get(blockId) : null;

  if (!block || !groundingResult) return null;

  return (
    <div className="cgv2-detail">
      <div className="cgv2-detail__header">
        <h4 className="cgv2-detail__title">{block.id}</h4>
        <button className="cgv2-detail__close" onClick={onClose} aria-label="Close detail panel">
          x
        </button>
      </div>

      <div className="cgv2-detail__content">
        {/* Grounding status */}
        <div className="cgv2-detail__row">
          <span className="cgv2-detail__label">Grounded:</span>
          <span
            className={`cgv2-detail__value ${groundingResult.isGrounded ? 'cgv2-detail__value--success' : 'cgv2-detail__value--warning'}`}
          >
            {groundingResult.isGrounded ? 'Yes' : 'No'}
          </span>
        </div>

        {/* Evidence tier */}
        <div className="cgv2-detail__row">
          <span className="cgv2-detail__label">Tier:</span>
          <span
            className="cgv2-detail__value"
            style={{ color: EVIDENCE_TIER_COLORS[groundingResult.evidenceTier] }}
          >
            {groundingResult.evidenceTier.toUpperCase()}
          </span>
        </div>

        {/* Total loss */}
        <div className="cgv2-detail__row">
          <span className="cgv2-detail__label">Total Loss:</span>
          <span className="cgv2-detail__value cgv2-detail__value--mono">
            {groundingResult.totalLoss.toFixed(3)}
          </span>
        </div>

        {/* Layer */}
        <div className="cgv2-detail__row">
          <span className="cgv2-detail__label">Layer:</span>
          <span className="cgv2-detail__value" style={{ color: LAYER_COLORS[block.layer] }}>
            L{block.layer} ({LAYER_NAMES[block.layer]})
          </span>
        </div>

        {/* Derivation path */}
        <div className="cgv2-detail__section">
          <span className="cgv2-detail__section-label">Derivation Path:</span>
          <div className="cgv2-detail__path">
            {groundingResult.derivationPath.map((id, i) => (
              <span key={id} className="cgv2-detail__path-item">
                {id}
                {i < groundingResult.derivationPath.length - 1 && (
                  <span className="cgv2-detail__path-arrow">{' -> '}</span>
                )}
              </span>
            ))}
          </div>
        </div>

        {/* Derives from */}
        {block.derivesFrom.length > 0 && (
          <div className="cgv2-detail__section">
            <span className="cgv2-detail__section-label">Derives From:</span>
            <div className="cgv2-detail__tags">
              {block.derivesFrom.map((id) => (
                <span key={id} className="cgv2-detail__tag">
                  {id}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Dependents */}
        {block.dependents.length > 0 && (
          <div className="cgv2-detail__section">
            <span className="cgv2-detail__section-label">Dependents:</span>
            <div className="cgv2-detail__tags">
              {block.dependents.map((id) => (
                <span key={id} className="cgv2-detail__tag">
                  {id}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const ConstitutionalGraphView2 = memo(function ConstitutionalGraphView2({
  initialSelectedBlock,
  onBlockSelect,
  showDetailPanel = true,
  className = '',
}: ConstitutionalGraphView2Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { density: windowDensity } = useWindowLayout();

  // Store state
  const {
    blocks,
    edges,
    blocksByLayer,
    positions,
    selectedBlockId,
    highlightedBlockIds,
    groundingResult,
    orphanBlockIds,
    density,
    isLoading,
    error,
    initializeGraph,
    selectBlock,
    clearSelection,
    setDensity,
    setContainerSize,
    checkConsistency,
  } = useConstitutionalGraphStore();

  // Sync density with window layout
  useEffect(() => {
    setDensity(windowDensity);
  }, [windowDensity, setDensity]);

  // Initialize graph on mount
  useEffect(() => {
    initializeGraph();
    checkConsistency();
  }, [initializeGraph, checkConsistency]);

  // Handle initial selection
  useEffect(() => {
    if (initialSelectedBlock) {
      selectBlock(initialSelectedBlock);
    }
  }, [initialSelectedBlock, selectBlock]);

  // Update container size on resize
  useEffect(() => {
    if (!containerRef.current) return;

    const updateSize = () => {
      const rect = containerRef.current?.getBoundingClientRect();
      if (rect) {
        setContainerSize(rect.width, rect.height);
      }
    };

    updateSize();

    const observer = new ResizeObserver(updateSize);
    observer.observe(containerRef.current);

    return () => observer.disconnect();
  }, [setContainerSize]);

  // Handle block click
  const handleBlockClick = useCallback(
    async (blockId: string) => {
      if (selectedBlockId === blockId) {
        clearSelection();
        onBlockSelect?.(null, null);
      } else {
        await selectBlock(blockId);
        // Get updated grounding result from store
        const store = useConstitutionalGraphStore.getState();
        onBlockSelect?.(blockId, store.groundingResult);
      }
    },
    [selectedBlockId, selectBlock, clearSelection, onBlockSelect]
  );

  // Handle close detail panel
  const handleCloseDetail = useCallback(() => {
    clearSelection();
    onBlockSelect?.(null, null);
  }, [clearSelection, onBlockSelect]);

  // Calculate SVG dimensions and layout
  const sizes = DENSITY_SIZES[density];
  const svgHeight = 4 * sizes.layerGap + sizes.padding * 2; // 4 layers

  // Memoize layers array (constant, but memoized to avoid recreation)
  const layers = useMemo<EpistemicLayer[]>(() => [3, 2, 1, 0], []); // Top to bottom

  // Memoize layer band data
  const layerBandData = useMemo(() => {
    return layers.map((layer, index) => ({
      layer,
      y: index * sizes.layerGap + sizes.padding,
      height: sizes.layerGap,
      blockCount: blocksByLayer.get(layer)?.length || 0,
    }));
  }, [layers, sizes.layerGap, sizes.padding, blocksByLayer]);

  // Memoize edge data
  const edgeData = useMemo(() => {
    return edges
      .map((edge) => {
        const sourcePos = positions.get(edge.sourceId);
        const targetPos = positions.get(edge.targetId);
        const sourceBlock = blocks.get(edge.sourceId);
        const targetBlock = blocks.get(edge.targetId);

        if (!sourcePos || !targetPos || !sourceBlock || !targetBlock) return null;

        return {
          ...edge,
          sourcePos,
          targetPos,
          sourceLayer: sourceBlock.layer,
          targetLayer: targetBlock.layer,
          isHighlighted:
            highlightedBlockIds.has(edge.sourceId) && highlightedBlockIds.has(edge.targetId),
        };
      })
      .filter(Boolean);
  }, [edges, positions, blocks, highlightedBlockIds]);

  // Memoize node data
  const nodeData = useMemo(() => {
    return Array.from(blocks.values())
      .map((block) => {
        const position = positions.get(block.id);
        if (!position) return null;

        return {
          block,
          position,
          isSelected: selectedBlockId === block.id,
          isHighlighted: highlightedBlockIds.has(block.id),
          isOrphan: orphanBlockIds.has(block.id),
        };
      })
      .filter(Boolean);
  }, [blocks, positions, selectedBlockId, highlightedBlockIds, orphanBlockIds]);

  // Loading state
  if (isLoading) {
    return (
      <div className={`cgv2 cgv2--loading ${className}`}>
        <div className="cgv2__loading">Loading constitution...</div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={`cgv2 cgv2--error ${className}`}>
        <div className="cgv2__error">
          <span className="cgv2__error-icon">!</span>
          <span className="cgv2__error-text">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`cgv2 cgv2--${density} ${className}`} ref={containerRef}>
      {/* Header */}
      <header className="cgv2__header">
        <h3 className="cgv2__title">Constitutional Derivation Graph</h3>
        <div className="cgv2__meta">
          <span className="cgv2__block-count">{blocks.size} blocks</span>
          <span className="cgv2__layer-count">4 layers</span>
        </div>
      </header>

      {/* Graph SVG */}
      <div className="cgv2__canvas">
        <svg
          className="cgv2__svg"
          width="100%"
          height={svgHeight}
          viewBox={`0 0 ${containerRef.current?.clientWidth || 800} ${svgHeight}`}
          preserveAspectRatio="xMidYMid meet"
        >
          {/* Layer bands */}
          <g className="cgv2__layers">
            {layerBandData.map(({ layer, y, height, blockCount }) => (
              <LayerBand
                key={layer}
                layer={layer}
                y={y}
                width={containerRef.current?.clientWidth || 800}
                height={height}
                blockCount={blockCount}
                density={density}
              />
            ))}
          </g>

          {/* Edges (render before nodes so nodes appear on top) */}
          <g className="cgv2__edges">
            {edgeData.map((edge) =>
              edge ? (
                <DerivationEdge
                  key={`${edge.sourceId}-${edge.targetId}`}
                  sourceId={edge.sourceId}
                  targetId={edge.targetId}
                  sourcePos={edge.sourcePos}
                  targetPos={edge.targetPos}
                  sourceLayer={edge.sourceLayer}
                  targetLayer={edge.targetLayer}
                  loss={edge.loss}
                  isHighlighted={edge.isHighlighted}
                  nodeHeight={sizes.nodeHeight}
                />
              ) : null
            )}
          </g>

          {/* Nodes */}
          <g className="cgv2__nodes">
            {nodeData.map((data) =>
              data ? (
                <ConstitutionalNode
                  key={data.block.id}
                  block={data.block}
                  isSelected={data.isSelected}
                  isHighlighted={data.isHighlighted}
                  isOrphan={data.isOrphan}
                  x={data.position.x}
                  y={data.position.y}
                  density={density}
                  onClick={handleBlockClick}
                />
              ) : null
            )}
          </g>
        </svg>
      </div>

      {/* Detail panel */}
      {showDetailPanel && selectedBlockId && (
        <DetailPanel
          blockId={selectedBlockId}
          groundingResult={groundingResult}
          density={density}
          onClose={handleCloseDetail}
        />
      )}
    </div>
  );
});

export default ConstitutionalGraphView2;
