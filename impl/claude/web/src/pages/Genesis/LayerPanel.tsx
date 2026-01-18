/**
 * LayerPanel — K-Block List for a Layer
 *
 * Shows all K-Blocks in a layer with selection state.
 */

import type { GenesisLayer, GenesisKBlock } from '../../types';
import { GENESIS_LAYERS, getLayerColor, isAxiom } from '../../types';

interface LayerPanelProps {
  layer: GenesisLayer;
  kblocks: GenesisKBlock[];
  selectedNodeId: string | null;
  visitedNodes: readonly string[];
  onSelectNode: (nodeId: string | null) => void;
}

/**
 * Panel showing K-Blocks for a layer
 */
export function LayerPanel({
  layer,
  kblocks,
  selectedNodeId,
  visitedNodes,
  onSelectNode,
}: LayerPanelProps) {
  const layerInfo = GENESIS_LAYERS[layer];

  return (
    <div className="layer-panel">
      <header className="layer-panel__header">
        <div
          className="layer-panel__layer-badge"
          style={
            {
              '--layer-color': getLayerColor(layer),
            } as React.CSSProperties
          }
        >
          L{layer}
        </div>
        <div className="layer-panel__layer-info">
          <h2 className="layer-panel__title">{layerInfo.name}</h2>
          <p className="layer-panel__description">{layerInfo.description}</p>
        </div>
      </header>

      <ul className="layer-panel__list">
        {kblocks.map((kblock) => {
          const isSelected = selectedNodeId === kblock.id;
          const isVisited = visitedNodes.includes(kblock.id);
          const isL0 = isAxiom(kblock);

          return (
            <li key={kblock.id} className="layer-panel__item">
              <button
                className={`layer-panel__kblock ${
                  isSelected ? 'layer-panel__kblock--selected' : ''
                } ${isVisited ? 'layer-panel__kblock--visited' : ''}`}
                onClick={() => onSelectNode(isSelected ? null : kblock.id)}
                style={
                  {
                    '--kblock-color': kblock.color,
                  } as React.CSSProperties
                }
              >
                {/* Icon based on type */}
                <span className="layer-panel__icon">{isL0 ? '⚡' : layer === 2 ? '◉' : '○'}</span>

                {/* Title and summary */}
                <div className="layer-panel__content">
                  <span className="layer-panel__kblock-title">{kblock.title}</span>
                  <span className="layer-panel__kblock-summary">{kblock.summary}</span>
                </div>

                {/* Confidence/Loss indicator */}
                <span className="layer-panel__confidence">
                  {isL0 ? (
                    <span className="layer-panel__axiom-badge">AXIOM</span>
                  ) : (
                    <span className="layer-panel__loss">
                      L={kblock.proof?.galoisLoss.toFixed(2)}
                    </span>
                  )}
                </span>

                {/* Selection indicator */}
                <span className="layer-panel__arrow">{isSelected ? '◀' : '→'}</span>
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
