/**
 * ConstitutionalExplorer — Navigate the Constitutional Graph
 *
 * "The user explores what already exists."
 *
 * Four layers, 22 K-Blocks. Navigate by layer or by node.
 */

import { useMemo } from 'react';
import type { GenesisLayer, GenesisKBlock } from '../../types';
import { GENESIS_LAYERS, getLayerColor } from '../../types';
import {
  CONSTITUTIONAL_GRAPH,
  getLayerKBlocks,
  getKBlock,
  getAncestors,
} from '../../data/genesis-seed';
import { LayerPanel } from './LayerPanel';
import { KBlockDetail } from './KBlockDetail';
import { DerivationTrail } from './DerivationTrail';

interface ConstitutionalExplorerProps {
  currentLayer: GenesisLayer;
  selectedNodeId: string | null;
  visitedNodes: readonly string[];
  onLayerChange: (layer: GenesisLayer) => void;
  onSelectNode: (nodeId: string | null) => void;
  onReadyToExtend: () => void;
}

/**
 * The main exploration interface
 */
export function ConstitutionalExplorer({
  currentLayer,
  selectedNodeId,
  visitedNodes,
  onLayerChange,
  onSelectNode,
  onReadyToExtend,
}: ConstitutionalExplorerProps) {
  // Get K-Blocks for current layer
  const layerKBlocks = useMemo(() => getLayerKBlocks(currentLayer), [currentLayer]);

  // Get selected K-Block
  const selectedKBlock = useMemo(
    () => (selectedNodeId ? getKBlock(selectedNodeId) : null),
    [selectedNodeId]
  );

  // Get derivation path for selected node
  const derivationPath = useMemo(() => {
    if (!selectedNodeId) return [];
    const ancestors = getAncestors(selectedNodeId);
    const current = getKBlock(selectedNodeId);
    if (current) {
      return [...ancestors.reverse(), current];
    }
    return ancestors.reverse();
  }, [selectedNodeId]);

  // Check if user has explored enough to extend
  const hasExploredEnough = visitedNodes.length >= 4;

  return (
    <div className="constitutional-explorer">
      {/* Header */}
      <header className="constitutional-explorer__header">
        <h1 className="constitutional-explorer__title">Constitutional Graph</h1>
        <p className="constitutional-explorer__subtitle">
          22 K-Blocks across 4 layers. Every principle derives from the axioms.
        </p>
      </header>

      {/* Layer navigation */}
      <nav className="constitutional-explorer__layers">
        {GENESIS_LAYERS.map((layer) => (
          <button
            key={layer.level}
            className={`constitutional-explorer__layer-btn ${
              currentLayer === layer.level ? 'constitutional-explorer__layer-btn--active' : ''
            }`}
            onClick={() => onLayerChange(layer.level as GenesisLayer)}
            style={
              {
                '--layer-color': getLayerColor(layer.level as GenesisLayer),
              } as React.CSSProperties
            }
          >
            <span className="constitutional-explorer__layer-level">L{layer.level}</span>
            <span className="constitutional-explorer__layer-name">{layer.name}</span>
            <span className="constitutional-explorer__layer-count">{layer.count}</span>
          </button>
        ))}
      </nav>

      {/* Layer bar indicator */}
      <div className="constitutional-explorer__layer-bar">
        {GENESIS_LAYERS.map((layer) => (
          <div
            key={layer.level}
            className={`constitutional-explorer__layer-segment ${
              currentLayer === layer.level ? 'constitutional-explorer__layer-segment--active' : ''
            } ${
              currentLayer > layer.level ? 'constitutional-explorer__layer-segment--visited' : ''
            }`}
            style={
              {
                '--layer-color': getLayerColor(layer.level as GenesisLayer),
              } as React.CSSProperties
            }
          />
        ))}
      </div>

      {/* Main content area */}
      <main className="constitutional-explorer__main">
        {/* Left: Layer panel with K-Block list */}
        <div className="constitutional-explorer__list">
          <LayerPanel
            layer={currentLayer}
            kblocks={layerKBlocks}
            selectedNodeId={selectedNodeId}
            visitedNodes={visitedNodes}
            onSelectNode={onSelectNode}
          />
        </div>

        {/* Right: Selected K-Block detail */}
        <div className="constitutional-explorer__detail">
          {selectedKBlock ? (
            <>
              {/* Derivation trail */}
              {derivationPath.length > 1 && (
                <DerivationTrail path={derivationPath} onSelectNode={onSelectNode} />
              )}

              {/* K-Block detail */}
              <KBlockDetail
                kblock={selectedKBlock}
                onNavigateToDerivation={(id) => {
                  const node = getKBlock(id);
                  if (node) {
                    onLayerChange(node.layer);
                    onSelectNode(id);
                  }
                }}
              />
            </>
          ) : (
            <div className="constitutional-explorer__empty">
              <p>Select a K-Block to explore its content and derivations.</p>
              <p className="constitutional-explorer__empty-hint">
                Layer {currentLayer}: {GENESIS_LAYERS[currentLayer].description}
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Footer with navigation */}
      <footer className="constitutional-explorer__footer">
        <div className="constitutional-explorer__progress">
          <span className="constitutional-explorer__visited-count">
            {visitedNodes.length} / 22 explored
          </span>
          {hasExploredEnough && (
            <span className="constitutional-explorer__ready-hint">Ready to extend the graph</span>
          )}
        </div>

        <div className="constitutional-explorer__nav-buttons">
          {currentLayer > 0 && (
            <button
              className="constitutional-explorer__nav-btn"
              onClick={() => onLayerChange((currentLayer - 1) as GenesisLayer)}
            >
              ↑ L{currentLayer - 1}: {GENESIS_LAYERS[currentLayer - 1].name}
            </button>
          )}

          {currentLayer < 3 && (
            <button
              className="constitutional-explorer__nav-btn"
              onClick={() => onLayerChange((currentLayer + 1) as GenesisLayer)}
            >
              ↓ L{currentLayer + 1}: {GENESIS_LAYERS[currentLayer + 1].name}
            </button>
          )}

          {hasExploredEnough && (
            <button className="constitutional-explorer__extend-btn" onClick={onReadyToExtend}>
              Create Your First Declaration →
            </button>
          )}
        </div>
      </footer>
    </div>
  );
}
