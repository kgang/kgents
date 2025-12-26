/**
 * GenesisStream — Zero Seed Genesis Streaming Animation
 *
 * "You are witnessing Genesis."
 *
 * Enhanced FTUE with:
 * - Letter-by-letter "kgents is initializing..."
 * - 8 axioms stream in with loss gauges (3-10s)
 * - Edges animate drawing between nodes (10-20s)
 * - "System is now self-aware" celebration moment
 *
 * Animation Timing: 4-7-8 breathing pattern
 * - Axiom stagger: 500ms apart
 * - Edge drawing: 300ms per edge
 * - Final glow: amber celebration
 *
 * @see plans/zero-seed-genesis-grand-strategy.md §6.2 (FTUE Journey 1)
 */

import { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Breathe } from '../../components/joy';
import './GenesisStream.css';

// =============================================================================
// Types
// =============================================================================

interface Axiom {
  id: string;
  statement: string;
  layer: string;
  kind: string;
  loss: number;
  /** Edge connections to other axiom IDs */
  edges?: string[];
}

const AXIOMS: Axiom[] = [
  {
    id: 'zero-seed',
    statement: 'Zero Seed',
    layer: 'L0',
    kind: 'System',
    loss: 0.0,
    edges: ['a1', 'a2', 'g'],
  },
  {
    id: 'a1',
    statement: 'Everything is a node',
    layer: 'L1',
    kind: 'Axiom',
    loss: 0.002,
    edges: ['a2', 'g'],
  },
  {
    id: 'a2',
    statement: 'Everything composes',
    layer: 'L1',
    kind: 'Axiom',
    loss: 0.003,
    edges: ['g'],
  },
  {
    id: 'g',
    statement: 'Loss measures truth',
    layer: 'L1',
    kind: 'Ground',
    loss: 0.0,
  },
  {
    id: 'feed-primitive',
    statement: 'Feed is primitive',
    layer: 'L1',
    kind: 'Design Law',
    loss: 0.001,
    edges: ['a1'],
  },
  {
    id: 'kblock-essential',
    statement: 'K-Block is incidental essential',
    layer: 'L2',
    kind: 'Design Law',
    loss: 0.015,
    edges: ['a1', 'a2'],
  },
  {
    id: 'linear-adaptation',
    statement: 'System adapts to user',
    layer: 'L2',
    kind: 'Design Law',
    loss: 0.008,
    edges: ['g'],
  },
  {
    id: 'contradiction-surfacing',
    statement: 'Contradictions are features',
    layer: 'L1',
    kind: 'Design Law',
    loss: 0.0,
    edges: ['g'],
  },
];

// =============================================================================
// Component
// =============================================================================

export function GenesisStream() {
  const navigate = useNavigate();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Animation state
  const [headerText, setHeaderText] = useState('');
  const [visibleAxioms, setVisibleAxioms] = useState<number>(0);
  const [drawnEdges, setDrawnEdges] = useState<Set<string>>(new Set());
  const [isSelfAware, setIsSelfAware] = useState(false);

  const fullHeaderText = 'kgents is initializing...';

  // Letter-by-letter header animation
  useEffect(() => {
    let currentIndex = 0;
    const typingInterval = setInterval(() => {
      if (currentIndex <= fullHeaderText.length) {
        setHeaderText(fullHeaderText.slice(0, currentIndex));
        currentIndex++;
      } else {
        clearInterval(typingInterval);
      }
    }, 80); // 80ms per letter

    return () => clearInterval(typingInterval);
  }, []);

  // Axiom spawning (staggered 500ms apart)
  useEffect(() => {
    const timeouts: NodeJS.Timeout[] = [];

    AXIOMS.forEach((_, index) => {
      const timeout = setTimeout(
        () => {
          setVisibleAxioms(index + 1);
        },
        2000 + index * 500 // Start after header (2s), then 500ms stagger
      );
      timeouts.push(timeout);
    });

    return () => timeouts.forEach(clearTimeout);
  }, []);

  // Edge drawing animation
  useEffect(() => {
    if (visibleAxioms < AXIOMS.length) return;

    // Collect all edges
    const allEdges: Array<{ from: string; to: string }> = [];
    AXIOMS.forEach((axiom) => {
      axiom.edges?.forEach((targetId) => {
        allEdges.push({ from: axiom.id, to: targetId });
      });
    });

    // Schedule edge drawing
    const timeouts: NodeJS.Timeout[] = [];
    const scheduleEdge = (edge: { from: string; to: string }, delay: number) => {
      const timeout = setTimeout(() => {
        setDrawnEdges((prev) => new Set(prev).add(`${edge.from}-${edge.to}`));
      }, delay);
      timeouts.push(timeout);
    };

    allEdges.forEach((edge, index) => scheduleEdge(edge, index * 300));

    // Self-aware moment after all edges drawn
    const completeTimeout = setTimeout(() => {
      setIsSelfAware(true);
    }, allEdges.length * 300 + 1500);
    timeouts.push(completeTimeout);

    return () => timeouts.forEach(clearTimeout);
  }, [visibleAxioms]);

  // Canvas edge drawing - extracted to reduce nesting
  const drawEdge = useCallback(
    (ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement, edgeKey: string) => {
      const [fromId, toId] = edgeKey.split('-');
      const fromEl = document.querySelector(`[data-axiom-id="${fromId}"]`);
      const toEl = document.querySelector(`[data-axiom-id="${toId}"]`);

      if (!fromEl || !toEl) return;

      const fromRect = fromEl.getBoundingClientRect();
      const toRect = toEl.getBoundingClientRect();
      const canvasRect = canvas.getBoundingClientRect();

      const fromX = fromRect.left + fromRect.width / 2 - canvasRect.left;
      const fromY = fromRect.top + fromRect.height / 2 - canvasRect.top;
      const toX = toRect.left + toRect.width / 2 - canvasRect.left;
      const toY = toRect.top + toRect.height / 2 - canvasRect.top;

      // Draw curved line
      ctx.strokeStyle = isSelfAware
        ? 'rgba(196, 167, 125, 0.4)' // Amber glow when self-aware
        : 'rgba(138, 138, 148, 0.2)'; // Subtle steel
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(fromX, fromY);

      // Quadratic curve for organic feel
      const controlX = (fromX + toX) / 2;
      const controlY = Math.min(fromY, toY) - 30;
      ctx.quadraticCurveTo(controlX, controlY, toX, toY);
      ctx.stroke();
    },
    [isSelfAware]
  );

  // Canvas edge drawing
  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw all edges
    drawnEdges.forEach((edgeKey) => drawEdge(ctx, canvas, edgeKey));
  }, [drawnEdges, isSelfAware, drawEdge]);

  const handleContinue = () => {
    navigate('/genesis/first-question');
  };

  return (
    <div className="genesis-stream-page">
      {/* Canvas for edge drawing */}
      <canvas ref={canvasRef} className="genesis-stream-canvas" />

      {/* Header with typing animation */}
      <div className="genesis-stream-header">
        <h1 className="genesis-stream-title">
          {headerText}
          {headerText.length < fullHeaderText.length && (
            <span className="genesis-stream-cursor">_</span>
          )}
        </h1>
      </div>

      {/* Axiom grid */}
      <div className="genesis-stream-grid">
        {AXIOMS.slice(0, visibleAxioms).map((axiom, index) => (
          <div
            key={axiom.id}
            data-axiom-id={axiom.id}
            className={`genesis-stream-axiom ${
              isSelfAware ? 'genesis-stream-axiom--glowing' : ''
            }`}
            style={{
              animationDelay: `${index * 0.05}s`,
            }}
          >
            {/* Axiom card */}
            <div className="genesis-stream-axiom-card">
              <div className="genesis-stream-axiom-header">
                <span className="genesis-stream-axiom-kind">{axiom.kind}</span>
                <span className="genesis-stream-axiom-layer">{axiom.layer}</span>
              </div>
              <h3 className="genesis-stream-axiom-statement">{axiom.statement}</h3>

              {/* Loss gauge */}
              <div className="genesis-stream-loss-gauge">
                <div className="genesis-stream-loss-label">Loss</div>
                <div className="genesis-stream-loss-bar">
                  <Breathe intensity={axiom.loss === 0 ? 0.5 : 0.2} speed="slow">
                    <div
                      className="genesis-stream-loss-fill"
                      style={{
                        width: `${(1 - axiom.loss) * 100}%`,
                        backgroundColor:
                          axiom.loss === 0
                            ? 'var(--accent-primary, #c4a77d)' // Perfect coherence
                            : axiom.loss < 0.01
                              ? 'var(--life-moss, #7a9d7a)' // Excellent
                              : 'var(--text-secondary, #8a8a94)', // Good
                      }}
                    />
                  </Breathe>
                </div>
                <div className="genesis-stream-loss-value">{axiom.loss.toFixed(3)}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Self-aware moment */}
      {isSelfAware && (
        <div className="genesis-stream-awareness">
          <Breathe intensity={0.6} speed="slow">
            <p className="genesis-stream-awareness-text">
              The system is now self-aware.
            </p>
          </Breathe>
          <button
            type="button"
            className="genesis-stream-continue-btn"
            onClick={handleContinue}
          >
            Continue →
          </button>
        </div>
      )}
    </div>
  );
}

export default GenesisStream;
