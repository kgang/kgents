/**
 * AxiomGarden — Procedural visualization of Zero Seed axioms
 *
 * "The seed is not the garden. The seed is the capacity for gardening."
 *
 * A whimsical, animated canvas showing axioms as glowing nodes
 * that connect and form organic patterns. Pure CSS and canvas,
 * no heavy libraries.
 */

import { useEffect, useRef, useState, memo } from 'react';
import './AxiomGarden.css';

// =============================================================================
// Types
// =============================================================================

interface AxiomNode {
  id: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  label: string;
  glyph: string;
  hue: number;
}

// =============================================================================
// Sample Axioms
// =============================================================================

const AXIOMS = [
  { label: 'Entity', glyph: '◇' },
  { label: 'Morphism', glyph: '◈' },
  { label: 'Mirror', glyph: '◉' },
  { label: 'Tasteful', glyph: '✧' },
  { label: 'Composable', glyph: '⊛' },
];

// =============================================================================
// Component
// =============================================================================

function AxiomGardenComponent() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const nodesRef = useRef<AxiomNode[]>([]);
  const animationFrameRef = useRef<number>();
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize nodes ONCE
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const w = canvas.width;
    const h = canvas.height;

    const initialNodes: AxiomNode[] = AXIOMS.map((axiom, i) => ({
      id: `axiom-${i}`,
      x: w * 0.2 + Math.random() * w * 0.6,
      y: h * 0.2 + Math.random() * h * 0.6,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      label: axiom.label,
      glyph: axiom.glyph,
      hue: 40 + i * 15, // Gold to green hues
    }));

    nodesRef.current = initialNodes;
    setIsInitialized(true);
  }, []);

  // Animation loop - NO STATE UPDATES
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !isInitialized) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const w = canvas.width;
    const h = canvas.height;

    const animate = () => {
      // Clear canvas
      ctx.clearRect(0, 0, w, h);

      // Update nodes IN-PLACE (no React state update)
      const nodes = nodesRef.current;

      for (let i = 0; i < nodes.length; i++) {
        const node = nodes[i];

        // Update position
        node.x += node.vx;
        node.y += node.vy;

        // Bounce off edges
        if (node.x < 30 || node.x > w - 30) node.vx *= -1;
        if (node.y < 30 || node.y > h - 30) node.vy *= -1;

        // Keep in bounds
        node.x = Math.max(30, Math.min(w - 30, node.x));
        node.y = Math.max(30, Math.min(h - 30, node.y));
      }

      // Draw connections (edges between close nodes)
      ctx.strokeStyle = 'rgba(196, 167, 125, 0.15)';
      ctx.lineWidth = 1;

      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i];
          const b = nodes[j];
          const dx = b.x - a.x;
          const dy = b.y - a.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          // Draw connection if close enough
          if (dist < 150) {
            const alpha = (1 - dist / 150) * 0.3;
            ctx.strokeStyle = `rgba(196, 167, 125, ${alpha})`;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
      }

      // Draw nodes
      nodes.forEach((node) => {
        // Outer glow
        const gradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, 20);
        gradient.addColorStop(0, `hsla(${node.hue}, 30%, 60%, 0.4)`);
        gradient.addColorStop(1, `hsla(${node.hue}, 30%, 60%, 0)`);
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(node.x, node.y, 20, 0, Math.PI * 2);
        ctx.fill();

        // Node circle
        ctx.fillStyle = `hsl(${node.hue}, 25%, 40%)`;
        ctx.strokeStyle = `hsl(${node.hue}, 30%, 60%)`;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(node.x, node.y, 12, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // Glyph
        ctx.fillStyle = `hsl(${node.hue}, 40%, 75%)`;
        ctx.font = '16px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(node.glyph, node.x, node.y);
      });

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isInitialized]);

  // Handle hover to show labels
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Check if hovering any node (using ref instead of state)
    const hovered = nodesRef.current.find((node) => {
      const dx = node.x - mouseX;
      const dy = node.y - mouseY;
      return Math.sqrt(dx * dx + dy * dy) < 15;
    });

    setHoveredNode(hovered?.id || null);
  };

  return (
    <div className="axiom-garden">
      <div className="axiom-garden__header">
        <span className="axiom-garden__title">Axiom Garden</span>
        <span className="axiom-garden__subtitle">Ground layer • L1-L2</span>
      </div>

      <canvas
        ref={canvasRef}
        className="axiom-garden__canvas"
        width={600}
        height={200}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setHoveredNode(null)}
      />

      {hoveredNode && (
        <div className="axiom-garden__tooltip">
          {nodesRef.current.find((n) => n.id === hoveredNode)?.label}
        </div>
      )}

      <div className="axiom-garden__caption">
        "Everything is a node. Any two nodes can be connected."
      </div>
    </div>
  );
}

// Memoize to prevent re-renders from parent
export const AxiomGarden = memo(AxiomGardenComponent);
