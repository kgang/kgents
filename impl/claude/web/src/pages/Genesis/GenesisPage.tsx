/**
 * GenesisPage — First Time User Experience Phase 1
 *
 * "You are witnessing Genesis."
 *
 * The Zero Seed spawns in real-time, grounded in the minimal kernel:
 *
 * | Component | Statement                                        | Loss   |
 * |-----------|--------------------------------------------------|--------|
 * | A1        | Everything is a node                             | 0.002  |
 * | A2        | Everything composes                              | 0.003  |
 * | G         | L measures structure loss; axioms are Fix(L)     | 0.000  |
 *
 * After witnessing, user proceeds to FirstQuestion.
 *
 * Design: STARK BIOME aesthetic with 4-7-8 breathing, earned glow.
 * @see spec/protocols/zero-seed.md (canonical axioms)
 * @see plans/zero-seed-creative-strategy-v2.md (journey design)
 */

import { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Breathe } from '../../components/joy';
import { genesisApi, type GenesisAxiomResponse } from '../../api/client';
import './GenesisStream.css';

// =============================================================================
// Types
// =============================================================================

type GenesisState = 'loading' | 'seeding' | 'animating' | 'complete' | 'error';

interface Axiom {
  id: string;
  statement: string;
  layer: string;
  kind: string;
  loss: number;
  description: string;
  kblock_id: string;
  /** Edge connections to other axiom IDs */
  edges?: string[];
}

/**
 * Map API response to display format.
 */
function mapAxiomFromApi(apiAxiom: GenesisAxiomResponse): Axiom {
  // Create human-readable descriptions based on axiom ID
  const descriptions: Record<string, string> = {
    A1: 'A1: Entity — The first truth. All things are nodes in the graph.',
    A2: 'A2: Morphism — The second truth. Composition is the fundamental operation.',
    G: 'G: Galois Ground — L measures how much structure is lost in abstraction. Axioms are Fix(L).',
  };

  // Determine layer based on kind
  const layer = apiAxiom.kind === 'ground' ? 'L0' : 'L1';

  // Determine edges based on axiom relationships
  const edges: Record<string, string[]> = {
    A1: ['A2', 'G'],
    A2: ['G'],
    G: [],
  };

  return {
    id: apiAxiom.id.toLowerCase(),
    statement: apiAxiom.statement,
    layer,
    kind: apiAxiom.kind === 'ground' ? 'Ground' : 'Axiom',
    loss: apiAxiom.loss,
    description: descriptions[apiAxiom.id] || `${apiAxiom.id}: ${apiAxiom.statement}`,
    kblock_id: apiAxiom.kblock_id,
    edges: edges[apiAxiom.id] || [],
  };
}

/**
 * Fallback axioms if API fails (matches canonical spec).
 */
const FALLBACK_AXIOMS: Axiom[] = [
  {
    id: 'a1',
    statement: 'Everything is a node',
    description: 'A1: Entity — The first truth. All things are nodes in the graph.',
    layer: 'L1',
    kind: 'Axiom',
    loss: 0.002,
    kblock_id: '',
    edges: ['a2', 'g'],
  },
  {
    id: 'a2',
    statement: 'Everything composes',
    description: 'A2: Morphism — The second truth. Composition is the fundamental operation.',
    layer: 'L1',
    kind: 'Axiom',
    loss: 0.003,
    kblock_id: '',
    edges: ['g'],
  },
  {
    id: 'g',
    statement: 'Loss measures structure loss',
    description: 'G: Galois Ground — L measures how much structure is lost in abstraction. Axioms are Fix(L).',
    layer: 'L0',
    kind: 'Ground',
    loss: 0.000,
    kblock_id: '',
  },
];

// =============================================================================
// Component
// =============================================================================

export function GenesisPage() {
  const navigate = useNavigate();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Genesis state machine
  const [genesisState, setGenesisState] = useState<GenesisState>('loading');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [axioms, setAxioms] = useState<Axiom[]>([]);

  // Animation state
  const [headerText, setHeaderText] = useState('');
  const [visibleAxioms, setVisibleAxioms] = useState<number>(0);
  const [drawnEdges, setDrawnEdges] = useState<Set<string>>(new Set());
  const [isSelfAware, setIsSelfAware] = useState(false);

  const fullHeaderText = 'kgents is initializing...';

  // =============================================================================
  // API Integration
  // =============================================================================

  /**
   * Check genesis status and seed if needed.
   */
  const initializeGenesis = useCallback(async () => {
    try {
      setGenesisState('loading');
      setErrorMessage(null);

      // Step 1: Check if already seeded
      const status = await genesisApi.getStatus();

      if (status.is_seeded) {
        // Already seeded - fetch existing axioms from Zero Seed
        const zeroSeed = await genesisApi.getZeroSeed();
        const mappedAxioms = zeroSeed.axioms.map(mapAxiomFromApi);

        // Sort: A1, A2, G (Entity, Morphism, Ground)
        mappedAxioms.sort((a, b) => {
          const order = ['a1', 'a2', 'g'];
          return order.indexOf(a.id) - order.indexOf(b.id);
        });

        setAxioms(mappedAxioms.length > 0 ? mappedAxioms : FALLBACK_AXIOMS);
        setGenesisState('animating');
      } else {
        // Not seeded - perform seeding
        setGenesisState('seeding');

        const seedResult = await genesisApi.seed(false);

        if (seedResult.success) {
          const mappedAxioms = seedResult.axioms.map(mapAxiomFromApi);

          // Sort: A1, A2, G
          mappedAxioms.sort((a, b) => {
            const order = ['a1', 'a2', 'g'];
            return order.indexOf(a.id) - order.indexOf(b.id);
          });

          setAxioms(mappedAxioms.length > 0 ? mappedAxioms : FALLBACK_AXIOMS);
          setGenesisState('animating');
        } else {
          throw new Error(seedResult.message || 'Seeding failed');
        }
      }
    } catch (error) {
      console.error('Genesis initialization failed:', error);
      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'Failed to initialize genesis. Please try again.'
      );
      setGenesisState('error');
      // Fall back to hardcoded axioms so user can still proceed
      setAxioms(FALLBACK_AXIOMS);
    }
  }, []);

  // Initialize on mount
  useEffect(() => {
    initializeGenesis();
  }, [initializeGenesis]);

  // =============================================================================
  // Animation Effects
  // =============================================================================

  // Letter-by-letter header animation (80ms per letter)
  useEffect(() => {
    if (genesisState !== 'animating') return;

    let currentIndex = 0;
    const typingInterval = setInterval(() => {
      if (currentIndex <= fullHeaderText.length) {
        setHeaderText(fullHeaderText.slice(0, currentIndex));
        currentIndex++;
      } else {
        clearInterval(typingInterval);
      }
    }, 80);

    return () => clearInterval(typingInterval);
  }, [genesisState]);

  // Axiom spawning (staggered 800ms apart, starts after header)
  useEffect(() => {
    if (genesisState !== 'animating' || axioms.length === 0) return;

    const timeouts: NodeJS.Timeout[] = [];

    axioms.forEach((_, index) => {
      const timeout = setTimeout(
        () => {
          setVisibleAxioms(index + 1);
        },
        2500 + index * 800 // Start after header (2.5s), then 800ms stagger
      );
      timeouts.push(timeout);
    });

    return () => timeouts.forEach(clearTimeout);
  }, [genesisState, axioms]);

  // Edge drawing animation (after all axioms visible)
  useEffect(() => {
    if (visibleAxioms < axioms.length || axioms.length === 0) return;

    // Collect all edges
    const allEdges: Array<{ from: string; to: string }> = [];
    axioms.forEach((axiom) => {
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

    allEdges.forEach((edge, index) => scheduleEdge(edge, index * 400));

    // Self-aware moment after all edges drawn
    const completeTimeout = setTimeout(() => {
      setIsSelfAware(true);
      setGenesisState('complete');
    }, allEdges.length * 400 + 1500);
    timeouts.push(completeTimeout);

    return () => timeouts.forEach(clearTimeout);
  }, [visibleAxioms, axioms]);

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
        ? 'rgba(196, 167, 125, 0.5)' // Amber glow when self-aware
        : 'rgba(106, 139, 106, 0.4)'; // Life-moss during formation
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(fromX, fromY);

      // Quadratic curve for organic feel
      const controlX = (fromX + toX) / 2;
      const controlY = Math.min(fromY, toY) - 40;
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

  // =============================================================================
  // Handlers
  // =============================================================================

  const handleContinue = () => {
    navigate('/genesis/first-question');
  };

  const handleRetry = () => {
    setErrorMessage(null);
    setHeaderText('');
    setVisibleAxioms(0);
    setDrawnEdges(new Set());
    setIsSelfAware(false);
    initializeGenesis();
  };

  // Helper: get color for loss gauge
  const getLossColor = (loss: number): string => {
    if (loss === 0) return 'var(--accent-primary, #c4a77d)'; // Perfect coherence
    if (loss < 0.003) return 'var(--life-sage, #6b8b6b)'; // Excellent
    return 'var(--life-moss, #4a6b4a)'; // Good
  };

  // =============================================================================
  // Render States
  // =============================================================================

  // Loading state
  if (genesisState === 'loading') {
    return (
      <div className="genesis-stream-page">
        <div className="genesis-stream-header">
          <h1 className="genesis-stream-title">
            Checking genesis status...
            <span className="genesis-stream-cursor">_</span>
          </h1>
        </div>
      </div>
    );
  }

  // Seeding state
  if (genesisState === 'seeding') {
    return (
      <div className="genesis-stream-page">
        <div className="genesis-stream-header">
          <h1 className="genesis-stream-title">
            Spawning Zero Seed...
            <span className="genesis-stream-cursor">_</span>
          </h1>
          <p className="genesis-stream-awareness-subtext">
            Creating foundational K-Blocks in the database
          </p>
        </div>
      </div>
    );
  }

  // Error state with retry
  if (genesisState === 'error') {
    return (
      <div className="genesis-stream-page">
        <div className="genesis-stream-header">
          <h1 className="genesis-stream-title genesis-stream-title--error">
            Genesis encountered an issue
          </h1>
          {errorMessage && (
            <p className="genesis-stream-error-message">{errorMessage}</p>
          )}
          <div className="genesis-stream-error-actions">
            <button
              type="button"
              className="genesis-stream-retry-btn"
              onClick={handleRetry}
            >
              Retry Genesis
            </button>
            <button
              type="button"
              className="genesis-stream-continue-btn genesis-stream-continue-btn--fallback"
              onClick={() => {
                // Use fallback axioms and proceed
                setGenesisState('animating');
              }}
            >
              Continue with defaults
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Main animation/complete state
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

      {/* Zero Seed Axiom Grid */}
      <div className="genesis-stream-grid">
        {axioms.slice(0, visibleAxioms).map((axiom, index) => (
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
              <p className="genesis-stream-axiom-description">{axiom.description}</p>

              {/* K-Block ID indicator (only if real) */}
              {axiom.kblock_id && (
                <div className="genesis-stream-axiom-kblock">
                  <span className="genesis-stream-kblock-label">K-Block:</span>
                  <span className="genesis-stream-kblock-id">
                    {axiom.kblock_id.slice(0, 8)}...
                  </span>
                </div>
              )}

              {/* Loss gauge with 4-7-8 breathing */}
              <div className="genesis-stream-loss-gauge">
                <div className="genesis-stream-loss-label">Loss</div>
                <div className="genesis-stream-loss-bar">
                  <Breathe intensity={axiom.loss === 0 ? 0.5 : 0.2} speed="slow">
                    <div
                      className="genesis-stream-loss-fill"
                      style={{
                        width: `${(1 - axiom.loss * 100) * 100}%`,
                        backgroundColor: getLossColor(axiom.loss),
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
          <p className="genesis-stream-awareness-subtext">
            From two axioms and a ground, everything emerges.
          </p>
          <button
            type="button"
            className="genesis-stream-continue-btn"
            onClick={handleContinue}
          >
            Continue
          </button>
        </div>
      )}
    </div>
  );
}

export default GenesisPage;
