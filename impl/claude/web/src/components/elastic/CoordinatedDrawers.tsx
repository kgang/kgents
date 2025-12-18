/**
 * CoordinatedDrawers: Demo of temporal coherence between top and left drawers.
 *
 * When the top drawer collapses, the left drawer slides up to fill the space.
 * This uses the DesignSheaf's temporal coherence framework:
 * - Top drawer = LEADER (its progress drives the animation)
 * - Left drawer = FOLLOWER (reads leader's progress to position itself)
 *
 * The categorical insight: this is a LEADER_FOLLOWER sync strategy where
 * the left drawer's top offset is a function of the top drawer's progress.
 *
 * @see impl/claude/agents/design/sheaf.py (temporal coherence)
 */

import { useState, useCallback, type CSSProperties } from 'react';
import {
  useAnimationCoordination,
  type AnimationPhase,
} from '../../hooks/useDesignPolynomial';

// =============================================================================
// Constants
// =============================================================================

const TOP_DRAWER_HEIGHT = 120; // px when expanded (fits within 400px container)
const ANIMATION_DURATION = 0.3; // seconds
const LEFT_DRAWER_WIDTH = 280; // px

// =============================================================================
// Component Props
// =============================================================================

export interface CoordinatedDrawersProps {
  /** Content for the top drawer */
  topContent?: React.ReactNode;
  /** Content for the left drawer */
  leftContent?: React.ReactNode;
  /** Content for the main area */
  mainContent?: React.ReactNode;
  /** Initial state of top drawer */
  topOpen?: boolean;
  /** Initial state of left drawer */
  leftOpen?: boolean;
}

// =============================================================================
// Component
// =============================================================================

export function CoordinatedDrawers({
  topContent = <DefaultTopContent />,
  leftContent = <DefaultLeftContent />,
  mainContent = <DefaultMainContent />,
  topOpen: initialTopOpen = true,
  leftOpen: initialLeftOpen = true,
}: CoordinatedDrawersProps) {
  // Drawer open states
  const [topOpen, setTopOpen] = useState(initialTopOpen);
  const [leftOpen, setLeftOpen] = useState(initialLeftOpen);

  // Animation coordination
  // Note: unregisterAnimation and getNeighborProgress available for cleanup/sync
  const { registerAnimation, constraints } = useAnimationCoordination();

  // Track animation progress for smooth transitions
  const [topProgress, setTopProgress] = useState(topOpen ? 1 : 0);
  const [isAnimating, setIsAnimating] = useState(false);

  // Handle top drawer toggle with animation tracking
  const handleTopToggle = useCallback(() => {
    const newOpen = !topOpen;
    setTopOpen(newOpen);
    setIsAnimating(true);

    // Register the animation
    const phase: AnimationPhase = {
      phase: newOpen ? 'entering' : 'exiting',
      progress: 0,
      startedAt: Date.now() / 1000,
      duration: ANIMATION_DURATION,
    };
    registerAnimation('top-drawer', phase);

    // Animate progress
    const startTime = Date.now();
    const startProgress = topProgress;
    const targetProgress = newOpen ? 1 : 0;

    const animate = () => {
      const elapsed = (Date.now() - startTime) / 1000;
      const t = Math.min(elapsed / ANIMATION_DURATION, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - t, 3);
      const current = startProgress + (targetProgress - startProgress) * eased;

      setTopProgress(current);

      // Update animation phase progress
      registerAnimation('top-drawer', {
        ...phase,
        progress: t,
      });

      if (t < 1) {
        requestAnimationFrame(animate);
      } else {
        setIsAnimating(false);
        registerAnimation('top-drawer', {
          phase: newOpen ? 'active' : 'idle',
          progress: 1,
          startedAt: phase.startedAt,
          duration: ANIMATION_DURATION,
        });
      }
    };

    requestAnimationFrame(animate);
  }, [topOpen, topProgress, registerAnimation]);

  // Handle left drawer toggle
  const handleLeftToggle = useCallback(() => {
    setLeftOpen((prev) => !prev);
  }, []);

  // Calculate left drawer's top offset based on top drawer's progress
  // This is the LEADER_FOLLOWER coordination:
  // - When top is fully open (progress=1), left starts at TOP_DRAWER_HEIGHT
  // - When top is collapsed (progress=0), left starts at 0
  const leftDrawerTop = topProgress * TOP_DRAWER_HEIGHT;

  // Styles
  const containerStyle: CSSProperties = {
    position: 'relative',
    width: '100%',
    height: '100%', // Use 100% to respect parent container constraints
    minHeight: '400px', // Ensure minimum usable height
    overflow: 'hidden',
    background: '#1a1a2e',
  };

  const topDrawerStyle: CSSProperties = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: `${topProgress * TOP_DRAWER_HEIGHT}px`,
    background: '#16213e',
    borderBottom: '1px solid #0f3460',
    overflow: 'hidden',
    transition: isAnimating ? 'none' : `height ${ANIMATION_DURATION}s ease-out`,
  };

  const leftDrawerStyle: CSSProperties = {
    position: 'absolute',
    top: `${leftDrawerTop}px`, // <-- KEY: follows top drawer's progress
    left: 0,
    width: leftOpen ? `${LEFT_DRAWER_WIDTH}px` : '0px',
    bottom: 0,
    background: '#1a1a2e',
    borderRight: '1px solid #0f3460',
    overflow: 'hidden',
    transition: `width ${ANIMATION_DURATION}s ease-out`,
    // Height adjusts automatically via bottom: 0
  };

  const mainAreaStyle: CSSProperties = {
    position: 'absolute',
    top: `${leftDrawerTop}px`, // Also follows top drawer
    left: leftOpen ? `${LEFT_DRAWER_WIDTH}px` : '0px',
    right: 0,
    bottom: 0,
    background: '#0f0f23',
    transition: `left ${ANIMATION_DURATION}s ease-out`,
    overflow: 'auto',
  };

  // Debug info showing constraint state
  const debugInfo = constraints.length > 0 ? (
    <div className="absolute top-2 right-2 bg-black/50 text-xs text-gray-400 p-2 rounded font-mono">
      Constraints: {constraints.map(c => `${c.source}↔${c.target}:${c.strategy}`).join(', ')}
    </div>
  ) : null;

  return (
    <div style={containerStyle}>
      {/* Top Drawer */}
      <div style={topDrawerStyle}>
        <div className="p-4 h-full">
          {topContent}
        </div>
      </div>

      {/* Left Drawer - slides up as top collapses */}
      <div style={leftDrawerStyle}>
        <div className="p-4 h-full overflow-auto">
          {leftContent}
        </div>
      </div>

      {/* Main Content Area */}
      <div style={mainAreaStyle}>
        <div className="p-4">
          {mainContent}
        </div>
      </div>

      {/* Controls */}
      <div className="absolute bottom-4 right-4 flex gap-2">
        <button
          onClick={handleTopToggle}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          {topOpen ? 'Collapse Top' : 'Expand Top'}
        </button>
        <button
          onClick={handleLeftToggle}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          {leftOpen ? 'Hide Left' : 'Show Left'}
        </button>
      </div>

      {/* Progress indicator */}
      <div className="absolute bottom-4 left-4 bg-black/50 text-xs text-gray-400 p-2 rounded font-mono">
        Top Progress: {(topProgress * 100).toFixed(0)}%
        <br />
        Left Top: {leftDrawerTop.toFixed(0)}px
      </div>

      {debugInfo}
    </div>
  );
}

// =============================================================================
// Default Content Components
// =============================================================================

function DefaultTopContent() {
  return (
    <div className="text-white">
      <h3 className="text-lg font-semibold mb-2">Top Drawer</h3>
      <p className="text-gray-400 text-sm">
        This drawer collapses. Watch the left drawer slide up to fill the space.
      </p>
    </div>
  );
}

function DefaultLeftContent() {
  return (
    <div className="text-white">
      <h3 className="text-lg font-semibold mb-2">Left Drawer</h3>
      <p className="text-gray-400 text-sm mb-4">
        I follow the top drawer's collapse progress.
      </p>
      <ul className="space-y-2 text-sm text-gray-300">
        <li>• Navigation Item 1</li>
        <li>• Navigation Item 2</li>
        <li>• Navigation Item 3</li>
        <li>• Navigation Item 4</li>
      </ul>
    </div>
  );
}

function DefaultMainContent() {
  return (
    <div className="text-white">
      <h2 className="text-2xl font-bold mb-4">Main Content</h2>
      <p className="text-gray-400 mb-4">
        Click the buttons in the bottom-right to see the coordinated animation.
      </p>
      <div className="bg-gray-800/50 p-4 rounded-lg">
        <h4 className="font-semibold mb-2">How it works:</h4>
        <ol className="list-decimal list-inside space-y-1 text-sm text-gray-300">
          <li>Top drawer registers its animation phase</li>
          <li>Animation progress is tracked (0% → 100%)</li>
          <li>Left drawer's top offset = progress × TOP_DRAWER_HEIGHT</li>
          <li>This creates the "slide up to fill space" effect</li>
        </ol>
      </div>
      <div className="mt-4 bg-blue-900/30 p-4 rounded-lg border border-blue-700">
        <h4 className="font-semibold mb-2 text-blue-300">Categorical Insight</h4>
        <p className="text-sm text-blue-200">
          This is <code className="bg-black/30 px-1 rounded">LEADER_FOLLOWER</code> sync strategy:
          the left drawer's position is a <em>function</em> of the top drawer's progress.
          The sheaf ensures both animations stay coherent.
        </p>
      </div>
    </div>
  );
}

export default CoordinatedDrawers;
