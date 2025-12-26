/**
 * GenesisPage - The Self-Aware Awakening
 *
 * First-Time User Experience (FTUE) - System initialization as narrative.
 * K-Blocks emerge from the void, earning their light through the axiom cascade.
 *
 * STARK BIOME aesthetic:
 * - 90% Steel, 10% Earned Glow
 * - 4-7-8 breathing animation (6.75s, asymmetric slow exhale)
 * - Bioluminescence: K-Blocks glow as they materialize
 *
 * Layout: Centered cascade with axiom emergence
 * L0 AXIOM -> L1 GROUND -> L2 PRINCIPLE
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { LossIndicator } from '../primitives/Loss';
import './GenesisPage.css';

// =============================================================================
// Types
// =============================================================================

interface GenesisKBlock {
  id: string;
  layer: number;
  title: string;
  content: string;
  loss: number;
}

// =============================================================================
// Genesis K-Blocks - The Foundation
// =============================================================================

const GENESIS_BLOCKS: GenesisKBlock[] = [
  {
    id: 'axiom-truth',
    layer: 0,
    title: 'Truth is correspondence',
    content: 'A statement is true if it corresponds to reality.',
    loss: 0.0,
  },
  {
    id: 'ground-types',
    layer: 1,
    title: 'Types encode invariants',
    content: 'Type systems capture logical constraints in code.',
    loss: 0.08,
  },
  {
    id: 'principle-compose',
    layer: 2,
    title: 'Composability is fundamental',
    content: 'Every component composes via >> operator.',
    loss: 0.15,
  },
];

// =============================================================================
// Layer Names
// =============================================================================

const LAYER_NAMES: Record<number, string> = {
  0: 'AXIOM',
  1: 'GROUND',
  2: 'PRINCIPLE',
};

// =============================================================================
// Component
// =============================================================================

export function GenesisPage() {
  const navigate = useNavigate();
  const [visibleBlocks, setVisibleBlocks] = useState<number>(0);
  const [coherence, setCoherence] = useState(0);
  const [isReady, setIsReady] = useState(false);

  // Staggered block emergence - 1.2s between blocks
  useEffect(() => {
    if (visibleBlocks < GENESIS_BLOCKS.length) {
      const timer = setTimeout(
        () => {
          setVisibleBlocks((prev) => prev + 1);
        },
        1200 // 1.2s between blocks
      );
      return () => clearTimeout(timer);
    } else {
      // All blocks visible - animate coherence to 0.92
      const coherenceTimer = setInterval(() => {
        setCoherence((prev) => {
          const next = prev + 0.02;
          if (next >= 0.92) {
            clearInterval(coherenceTimer);
            setIsReady(true);
            return 0.92;
          }
          return next;
        });
      }, 50);
      return () => clearInterval(coherenceTimer);
    }
  }, [visibleBlocks]);

  const handleEnter = useCallback(() => {
    navigate('/studio');
  }, [navigate]);

  return (
    <div className="genesis-page">
      <div className="genesis-page__container">
        <h1 className="genesis-page__title">K-gents Genesis</h1>
        <p className="genesis-page__subtitle">The system is awakening...</p>

        <div className="genesis-page__cascade">
          {GENESIS_BLOCKS.map((block, index) => (
            <div key={block.id}>
              <div
                className={`genesis-block ${index < visibleBlocks ? 'genesis-block--visible' : ''}`}
                style={{ animationDelay: `${index * 0.3}s` }}
              >
                <div className="genesis-block__header">
                  <span className="genesis-block__layer">[L{block.layer}]</span>
                  <span className="genesis-block__layer-name">
                    {LAYER_NAMES[block.layer]}
                  </span>
                </div>
                <h3 className="genesis-block__title">{block.title}</h3>
                <p className="genesis-block__content">{block.content}</p>
                <div className="genesis-block__meta">
                  <LossIndicator loss={block.loss} size="sm" />
                  <span className="genesis-block__foundation">
                    {block.layer === 0
                      ? 'Foundation'
                      : `Grounded in L${block.layer - 1}`}
                  </span>
                </div>
              </div>
              {/* Derivation arrow - show when both this block and next are visible */}
              {index < GENESIS_BLOCKS.length - 1 && index < visibleBlocks - 1 && (
                <div className="genesis-block__arrow">
                  <span className="genesis-block__arrow-symbol">&#8595;</span>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="genesis-page__coherence">
          <span className="genesis-page__coherence-label">System coherence:</span>
          <div className="genesis-page__coherence-bar">
            <div
              className="genesis-page__coherence-fill"
              style={{ width: `${coherence * 100}%` }}
            />
          </div>
          <span className="genesis-page__coherence-value">
            {(coherence * 100).toFixed(0)}%
          </span>
        </div>

        <button
          className={`genesis-page__enter ${isReady ? 'genesis-page__enter--ready' : ''}`}
          onClick={handleEnter}
          disabled={!isReady}
        >
          {isReady ? 'Enter Studio' : 'Initializing...'}
        </button>
      </div>
    </div>
  );
}

export default GenesisPage;
