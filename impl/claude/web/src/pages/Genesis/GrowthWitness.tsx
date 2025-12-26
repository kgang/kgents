/**
 * GrowthWitness - FG: Growth Witness (FTUE Culmination)
 *
 * "From your first seed, the system grew."
 *
 * After F1 (Identity), F2 (Connection), F3 (Judgment), this component shows
 * what EMERGED from the user's seeds. This is the moment of witnessing
 * the system's generative power.
 *
 * Displays:
 * - Mini-graph showing user's axiom connected to Zero Seed foundation
 * - Generated insights about their declaration
 * - Edges that were auto-discovered
 * - Celebration with 4-7-8 breathing animation
 *
 * @see spec/protocols/ftue-axioms.md (FG: Growth Witness)
 * @see plans/zero-seed-genesis-grand-strategy.md (FTUE Journey)
 */

import { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Breathe, GrowingContainer } from '../../components/joy';
import './GrowthWitness.css';

// =============================================================================
// Types
// =============================================================================

interface EdgeConnection {
  edge_id: string;
  source_id: string;
  target_id: string;
  target_title: string;
  edge_type: string;
  context: string;
}

interface LocationState {
  declaration: string;
  kblock_id: string;
  layer: number;
  loss: number;
  justification: string;
  edges?: EdgeConnection[];
}

/** Emergent insight displayed to user */
interface _EmergentInsight {
  id: string;
  title: string;
  description: string;
  confidence: number;
}

interface GraphNode {
  id: string;
  label: string;
  type: 'user' | 'system' | 'axiom';
  x: number;
  y: number;
}

// =============================================================================
// Constants
// =============================================================================

const INSIGHTS_FROM_DECLARATION = [
  {
    id: 'pattern-recognition',
    title: 'Pattern Recognition',
    description: 'Your axiom shares structure with the foundational morphism principle.',
    confidence: 0.82,
  },
  {
    id: 'coherence-potential',
    title: 'Coherence Potential',
    description: 'This seed can branch into multiple connected thoughts.',
    confidence: 0.91,
  },
  {
    id: 'synthesis-opportunity',
    title: 'Synthesis Opportunity',
    description: 'The system sees paths to connect this with future declarations.',
    confidence: 0.77,
  },
];

// =============================================================================
// Graph Visualization
// =============================================================================

function useGraphVisualization(
  canvasRef: React.RefObject<HTMLCanvasElement>,
  nodes: GraphNode[],
  edges: EdgeConnection[],
  animationPhase: 'idle' | 'drawing' | 'complete'
) {
  const [drawnEdges, setDrawnEdges] = useState<Set<string>>(new Set());

  // Helper to add edge to drawn set
  const addDrawnEdge = useCallback((edgeId: string) => {
    setDrawnEdges((prev) => new Set(prev).add(edgeId));
  }, []);

  // Animate edge drawing when phase changes to 'drawing'
  useEffect(() => {
    if (animationPhase !== 'drawing' || edges.length === 0) return;

    const timeouts = edges.map((edge, index) =>
      setTimeout(() => addDrawnEdge(edge.edge_id), 400 + index * 350)
    );

    return () => timeouts.forEach(clearTimeout);
  }, [animationPhase, edges, addDrawnEdge]);

  // Draw edges on canvas
  const drawEdge = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      canvas: HTMLCanvasElement,
      fromNode: GraphNode,
      toNode: GraphNode,
      isComplete: boolean
    ) => {
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;

      const fromX = centerX + fromNode.x;
      const fromY = centerY + fromNode.y;
      const toX = centerX + toNode.x;
      const toY = centerY + toNode.y;

      // Draw curved line with organic feel
      ctx.strokeStyle = isComplete
        ? 'rgba(196, 167, 125, 0.6)' // Amber glow when complete
        : 'rgba(106, 139, 106, 0.5)'; // Life-moss during drawing
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(fromX, fromY);

      // Quadratic curve for organic feel
      const controlX = (fromX + toX) / 2;
      const controlY = Math.min(fromY, toY) - 40;
      ctx.quadraticCurveTo(controlX, controlY, toX, toY);
      ctx.stroke();

      // Draw small circle at connection point
      ctx.fillStyle = isComplete
        ? 'rgba(196, 167, 125, 0.8)'
        : 'rgba(106, 139, 106, 0.6)';
      ctx.beginPath();
      ctx.arc(toX, toY, 4, 0, Math.PI * 2);
      ctx.fill();
    },
    []
  );

  // Canvas rendering
  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth * 2; // Retina
    canvas.height = canvas.offsetHeight * 2;
    ctx.scale(2, 2);

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw all visible edges
    drawnEdges.forEach((edgeId) => {
      const edge = edges.find((e) => e.edge_id === edgeId);
      if (!edge) return;

      const fromNode = nodes.find((n) => n.id === edge.source_id);
      const toNode = nodes.find((n) => n.id === edge.target_id);

      if (fromNode && toNode) {
        drawEdge(ctx, canvas, fromNode, toNode, animationPhase === 'complete');
      }
    });
  }, [canvasRef, nodes, edges, drawnEdges, animationPhase, drawEdge]);

  return { drawnEdges };
}

// =============================================================================
// Component
// =============================================================================

export function GrowthWitness() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Animation state
  const [animationPhase, setAnimationPhase] = useState<
    'intro' | 'drawing' | 'insights' | 'celebration' | 'complete'
  >('intro');
  const [visibleInsights, setVisibleInsights] = useState<number>(0);
  const [isWitnessing, setIsWitnessing] = useState(false);

  // Build graph nodes from state
  const nodes: GraphNode[] = state
    ? [
        // User's axiom at center
        {
          id: state.kblock_id,
          label: state.declaration.slice(0, 30) + '...',
          type: 'user',
          x: 0,
          y: 0,
        },
        // Zero Seed axioms around the user
        ...(state.edges || []).map((edge, index) => {
          const angle = (index * 2 * Math.PI) / (state.edges?.length || 1);
          const radius = 120;
          return {
            id: edge.target_id,
            label: edge.target_title,
            type: 'axiom' as const,
            x: Math.cos(angle) * radius,
            y: Math.sin(angle) * radius,
          };
        }),
      ]
    : [];

  // Use graph visualization hook
  useGraphVisualization(
    canvasRef,
    nodes,
    state?.edges || [],
    animationPhase === 'drawing' || animationPhase === 'insights'
      ? 'drawing'
      : animationPhase === 'celebration' || animationPhase === 'complete'
        ? 'complete'
        : 'idle'
  );

  // Redirect if no state (direct navigation)
  useEffect(() => {
    if (!state) {
      navigate('/genesis/first-question');
    }
  }, [state, navigate]);

  // Animation sequence
  useEffect(() => {
    const timeouts: NodeJS.Timeout[] = [];

    // Phase 1: Start drawing edges after intro
    timeouts.push(
      setTimeout(() => {
        setAnimationPhase('drawing');
      }, 1500)
    );

    // Phase 2: Show insights after edges
    const edgeCount = state?.edges?.length || 0;
    const insightDelay = 1500 + 400 + edgeCount * 350 + 500;
    timeouts.push(
      setTimeout(() => {
        setAnimationPhase('insights');
      }, insightDelay)
    );

    // Phase 3: Stagger insights
    INSIGHTS_FROM_DECLARATION.forEach((_, index) => {
      timeouts.push(
        setTimeout(() => {
          setVisibleInsights(index + 1);
        }, insightDelay + 300 + index * 400)
      );
    });

    // Phase 4: Celebration after all insights
    const celebrationDelay =
      insightDelay + 300 + INSIGHTS_FROM_DECLARATION.length * 400 + 800;
    timeouts.push(
      setTimeout(() => {
        setAnimationPhase('celebration');
      }, celebrationDelay)
    );

    // Phase 5: Complete (enable button)
    timeouts.push(
      setTimeout(() => {
        setAnimationPhase('complete');
      }, celebrationDelay + 1000)
    );

    return () => timeouts.forEach(clearTimeout);
  }, [state?.edges?.length]);

  // Handle entering kgents
  const handleEnterKgents = async () => {
    setIsWitnessing(true);

    try {
      // Call witness-emergence API to record the FG moment
      // Request format: WitnessEmergenceRequest
      await fetch('/api/onboarding/witness-emergence', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          // IDs of artifacts that contributed to emergence
          emerged_from: [
            state?.kblock_id, // F1: Identity seed
            ...(state?.edges?.map((e) => e.edge_id) || []), // F2: Connection edges
          ].filter(Boolean),
          emergence_type: 'pattern_discovered',
          description: `Witnessed ${state?.edges?.length || 0} connections emerge from first axiom`,
        }),
      });
    } catch (err) {
      console.error('Failed to witness emergence:', err);
      // Continue anyway - this is non-critical
    }

    // Mark onboarding as complete
    try {
      await fetch('/api/onboarding/complete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    } catch (err) {
      console.error('Failed to mark onboarding complete:', err);
    }

    // Navigate to main studio with K-Block ID in URL path
    navigate(`/world.document/${state?.kblock_id}`, {
      state: {
        highlightKBlock: state?.kblock_id,
        showZeroSeed: true,
        ftueComplete: true,
        zeroSeedContext: {
          userAxiomId: state?.kblock_id,
          userDeclaration: state?.declaration,
          layer: state?.layer,
          loss: state?.loss,
        },
      },
    });
  };

  if (!state) return null;

  return (
    <div className="growth-witness-page">
      {/* Canvas for edge visualization */}
      <canvas ref={canvasRef} className="growth-witness-canvas" />

      {/* Header */}
      <GrowingContainer autoTrigger duration="deliberate">
        <div className="growth-witness-header">
          <h1 className="growth-witness-title">From your first seed, the system grew</h1>
          <p className="growth-witness-subtitle">
            You are witnessing emergence.
          </p>
        </div>
      </GrowingContainer>

      {/* Graph Nodes */}
      <div className="growth-witness-graph">
        {/* User's axiom (center) */}
        <GrowingContainer autoTrigger delay={500} duration="deliberate">
          <div className="growth-witness-node growth-witness-node--user">
            <Breathe intensity={0.4} speed="slow">
              <div className="growth-witness-node-content">
                <span className="growth-witness-node-label">Your Axiom</span>
                <p className="growth-witness-node-text">
                  {state.declaration.length > 60
                    ? state.declaration.slice(0, 60) + '...'
                    : state.declaration}
                </p>
                <span className="growth-witness-node-layer">L{state.layer}</span>
              </div>
            </Breathe>
          </div>
        </GrowingContainer>

        {/* Connected axioms */}
        <div className="growth-witness-connections">
          {(state.edges || []).map((edge, index) => (
            <GrowingContainer
              key={edge.edge_id}
              autoTrigger
              delay={800 + index * 300}
              duration="normal"
            >
              <div
                className={`growth-witness-node growth-witness-node--axiom growth-witness-node--position-${index}`}
              >
                <div className="growth-witness-node-content">
                  <span className="growth-witness-node-edge-type">
                    {edge.edge_type.replace('_', ' ')}
                  </span>
                  <p className="growth-witness-node-text">{edge.target_title}</p>
                </div>
              </div>
            </GrowingContainer>
          ))}
        </div>
      </div>

      {/* Emergent Insights */}
      {animationPhase !== 'intro' && animationPhase !== 'drawing' && (
        <div className="growth-witness-insights">
          <GrowingContainer autoTrigger duration="normal">
            <h2 className="growth-witness-insights-title">What emerged</h2>
          </GrowingContainer>

          <div className="growth-witness-insights-list">
            {INSIGHTS_FROM_DECLARATION.slice(0, visibleInsights).map(
              (insight, index) => (
                <GrowingContainer
                  key={insight.id}
                  autoTrigger
                  delay={index * 100}
                  duration="quick"
                >
                  <div className="growth-witness-insight">
                    <div className="growth-witness-insight-header">
                      <span className="growth-witness-insight-title">
                        {insight.title}
                      </span>
                      <span className="growth-witness-insight-confidence">
                        {Math.round(insight.confidence * 100)}%
                      </span>
                    </div>
                    <p className="growth-witness-insight-description">
                      {insight.description}
                    </p>
                  </div>
                </GrowingContainer>
              )
            )}
          </div>
        </div>
      )}

      {/* Celebration Moment */}
      {(animationPhase === 'celebration' || animationPhase === 'complete') && (
        <div className="growth-witness-celebration">
          <Breathe intensity={0.6} speed="slow">
            <GrowingContainer autoTrigger duration="deliberate">
              <div className="growth-witness-celebration-content">
                <p className="growth-witness-celebration-emoji">✨</p>
                <p className="growth-witness-celebration-text">
                  The system is ready to grow with you.
                </p>
                <p className="growth-witness-celebration-subtext">
                  Your first axiom is now part of the cosmic graph.
                  Every future thought can connect to this seed.
                </p>
              </div>
            </GrowingContainer>
          </Breathe>
        </div>
      )}

      {/* Enter Button */}
      {animationPhase === 'complete' && (
        <GrowingContainer autoTrigger delay={300} duration="normal">
          <button
            type="button"
            className="growth-witness-enter-btn"
            onClick={handleEnterKgents}
            disabled={isWitnessing}
          >
            {isWitnessing ? 'Entering...' : 'Enter kgents →'}
          </button>
        </GrowingContainer>
      )}
    </div>
  );
}

export default GrowthWitness;
