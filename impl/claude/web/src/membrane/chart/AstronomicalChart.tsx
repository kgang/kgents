/**
 * AstronomicalChart — Canvas-based spec graph visualization
 *
 * Renders specs as celestial bodies in a force-directed layout.
 * GPU-accelerated via Pixi.js for millions of nodes.
 *
 * Visual metaphor:
 * - Specs as stars (size = evidence, color = tier)
 * - Connections as gravitational threads (visible on hover)
 * - Orphans dim and peripheral
 *
 * "The file is a lie. There is only the graph."
 */

import { useEffect, useRef, useState } from 'react';
import * as PIXI from 'pixi.js';
import { useAstronomicalData } from './useAstronomicalData';
import { useViewport } from './useViewport';
import { useForceLayout } from './useForceLayout';
import { useChartInteraction } from './useChartInteraction';
import { ChartControls } from './ChartControls';
import {
  BACKGROUND,
  TIER_COLORS,
  createStarGraphic,
  createGlowRing,
  drawConnection,
  createStarField,
  getTierLabel,
  hexToString,
  TrailSystem,
} from './StarRenderer';

import './AstronomicalChart.css';

// =============================================================================
// Types
// =============================================================================

interface AstronomicalChartProps {
  /** Filter by status */
  statusFilter?: string;
  /** Maximum specs to show */
  limit?: number;
  /** Callback when node is clicked */
  onNodeClick?: (path: string) => void;
  /** Show controls panel */
  showControls?: boolean;
  /** Show legend */
  showLegend?: boolean;
}

// =============================================================================
// Component
// =============================================================================

export function AstronomicalChart({
  statusFilter,
  limit = 100,
  onNodeClick,
  showControls = true,
  showLegend = true,
}: AstronomicalChartProps) {
  // Refs
  const containerRef = useRef<HTMLDivElement>(null);
  const appRef = useRef<PIXI.Application | null>(null);
  const viewportContainerRef = useRef<PIXI.Container | null>(null);
  const starsContainerRef = useRef<PIXI.Container | null>(null);
  const connectionsGraphicsRef = useRef<PIXI.Graphics | null>(null);
  const starGraphicsRef = useRef<Map<string, PIXI.Graphics>>(new Map());
  const trailSystemRef = useRef<TrailSystem | null>(null);
  const previousPositionsRef = useRef<Map<string, { x: number; y: number }>>(new Map());

  // State
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [internalStatusFilter, setInternalStatusFilter] = useState(statusFilter || '');
  const [tierFilter, setTierFilter] = useState<number[] | null>(null);

  // Data (AD-015: now includes needsScan and scan)
  const { stars, connections, isLoading, error, needsScan, scan, refetch } = useAstronomicalData({
    statusFilter: internalStatusFilter || undefined,
    limit,
  });

  // Filter stars by tier
  const filteredStars = tierFilter ? stars.filter((s) => tierFilter.includes(s.tier)) : stars;

  // Interaction state (hover, selection, search, keyboard)
  const {
    state: interactionState,
    actions: interactionActions,
    keyboardHandler,
  } = useChartInteraction({
    stars: filteredStars,
    onSelectionChange: (star) => {
      if (star) onNodeClick?.(star.path);
    },
  });

  const {
    hovered: hoveredStar,
    selected: selectedStar,
    searchQuery,
    searchResults,
    focusedResultIndex,
    searchFocused,
  } = interactionState;
  const { setHovered: setHoveredStar, setSelected: setSelectedStar } = interactionActions;

  // Viewport
  const {
    state: viewport,
    actions: viewportActions,
    bind: viewportBind,
  } = useViewport({
    minScale: 0.05,
    maxScale: 5.0,
    initial: { scale: 1.0 },
  });

  // Force-directed layout
  const {
    nodes: positionedStars,
    isSimulating,
    restart: restartSimulation,
  } = useForceLayout(stars, connections, {
    width: dimensions.width,
    height: dimensions.height,
    autoStart: true,
  });

  // Track if we've initialized Pixi (to avoid re-init on every render)
  const pixiInitializedRef = useRef(false);

  // Initialize Pixi application when container becomes available
  // This runs when stars.length changes from 0 (loading/needsScan) to > 0 (data loaded)
  useEffect(() => {
    // Skip if already initialized or container doesn't exist
    if (pixiInitializedRef.current || !containerRef.current) return;
    // Skip if we're in loading/needsScan/error state (stars will be empty)
    if (stars.length === 0) return;

    pixiInitializedRef.current = true;

    // Get container dimensions
    const rect = containerRef.current.getBoundingClientRect();
    setDimensions({ width: rect.width, height: rect.height });

    // Create Pixi application
    const app = new PIXI.Application({
      width: rect.width,
      height: rect.height,
      backgroundColor: BACKGROUND.obsidian,
      antialias: true,
      resolution: window.devicePixelRatio || 1,
      autoDensity: true,
    });

    containerRef.current.appendChild(app.view as HTMLCanvasElement);
    appRef.current = app;

    // Create viewport container (for pan/zoom transforms)
    const viewportContainer = new PIXI.Container();
    viewportContainer.position.set(rect.width / 2, rect.height / 2);
    app.stage.addChild(viewportContainer);
    viewportContainerRef.current = viewportContainer;

    // Create star field background
    const starField = createStarField(rect.width * 2, rect.height * 2, 200);
    viewportContainer.addChild(starField);

    // Create connections layer
    const connectionsGraphics = new PIXI.Graphics();
    viewportContainer.addChild(connectionsGraphics);
    connectionsGraphicsRef.current = connectionsGraphics;

    // Create stars container
    const starsContainer = new PIXI.Container();
    viewportContainer.addChild(starsContainer);
    starsContainerRef.current = starsContainer;

    // Create trail system for simulation particles
    const trailSystem = new TrailSystem(viewportContainer, 100);
    trailSystemRef.current = trailSystem;

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current || !app) return;
      const newRect = containerRef.current.getBoundingClientRect();
      app.renderer.resize(newRect.width, newRect.height);
      viewportContainer.position.set(newRect.width / 2, newRect.height / 2);
      setDimensions({ width: newRect.width, height: newRect.height });
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      trailSystem.destroy();
      trailSystemRef.current = null;
      app.destroy(true, { children: true });
      appRef.current = null;
      pixiInitializedRef.current = false;
    };
  }, [stars.length]); // Re-run when stars become available

  // Update viewport transform
  useEffect(() => {
    if (!viewportContainerRef.current) return;

    viewportContainerRef.current.scale.set(viewport.scale);
    viewportContainerRef.current.position.set(
      dimensions.width / 2 + viewport.x * viewport.scale,
      dimensions.height / 2 + viewport.y * viewport.scale
    );
  }, [viewport, dimensions]);

  // Render stars
  useEffect(() => {
    if (!starsContainerRef.current) return;

    const container = starsContainerRef.current;
    const trailSystem = trailSystemRef.current;
    const prevPositions = previousPositionsRef.current;

    // Update existing graphics or create new ones
    positionedStars.forEach((star) => {
      let graphic = starGraphicsRef.current.get(star.id);

      if (!graphic) {
        // Create new graphic
        graphic = createStarGraphic(star);
        graphic.eventMode = 'static';
        graphic.cursor = 'pointer';

        // Store position data for hit detection
        (graphic as any).starData = star;

        // Event handlers
        graphic.on('pointerover', () => setHoveredStar(star));
        graphic.on('pointerout', () => setHoveredStar(null));
        graphic.on('pointertap', () => {
          setSelectedStar(star);
          onNodeClick?.(star.path);
        });

        container.addChild(graphic);
        starGraphicsRef.current.set(star.id, graphic);
      }

      // Emit trail particles if star moved during simulation
      if (isSimulating && trailSystem) {
        const prev = prevPositions.get(star.id);
        if (prev) {
          const dx = star.x - prev.x;
          const dy = star.y - prev.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          // Only emit if moved significantly
          if (dist > 2) {
            const color = TIER_COLORS[star.tier] ?? TIER_COLORS[2];
            trailSystem.emit(prev.x, prev.y, color, star.radius * 0.5);
          }
        }
        prevPositions.set(star.id, { x: star.x, y: star.y });
      }

      // Update position
      graphic.position.set(star.x, star.y);
      (graphic as any).starData = star;
    });

    // Update trail system each frame
    trailSystem?.update();

    // Remove graphics for stars that no longer exist
    const currentIds = new Set(positionedStars.map((s) => s.id));
    starGraphicsRef.current.forEach((graphic, id) => {
      if (!currentIds.has(id)) {
        container.removeChild(graphic);
        starGraphicsRef.current.delete(id);
        prevPositions.delete(id);
      }
    });
  }, [positionedStars, onNodeClick, isSimulating]);

  // Render connections (only for hovered/selected star)
  useEffect(() => {
    if (!connectionsGraphicsRef.current) return;

    const graphics = connectionsGraphicsRef.current;
    graphics.clear();

    const activeStar = selectedStar || hoveredStar;
    if (!activeStar) return;

    const starLookup = new Map(positionedStars.map((s) => [s.id, s]));

    // Draw connections for active star
    connections.forEach((conn) => {
      if (conn.source !== activeStar.id && conn.target !== activeStar.id) return;

      const source = starLookup.get(conn.source);
      const target = starLookup.get(conn.target);

      if (source && target) {
        drawConnection(
          graphics,
          source,
          target,
          conn.relationship,
          conn.strength,
          selectedStar ? 0.6 : 0.4
        );
      }
    });
  }, [connections, hoveredStar, selectedStar, positionedStars]);

  // Add glow ring for selection/hover
  useEffect(() => {
    if (!starsContainerRef.current) return;

    // Remove existing glow rings
    starsContainerRef.current.children.forEach((child) => {
      if ((child as any).isGlowRing) {
        starsContainerRef.current?.removeChild(child);
      }
    });

    // Add glow for selected star
    if (selectedStar) {
      const starGraphic = starGraphicsRef.current.get(selectedStar.id);
      if (starGraphic) {
        const glow = createGlowRing(selectedStar.radius, 'selection');
        glow.position.copyFrom(starGraphic.position);
        (glow as any).isGlowRing = true;
        starsContainerRef.current.addChildAt(glow, 0);
      }
    }

    // Add glow for hovered star (if different from selected)
    if (hoveredStar && hoveredStar.id !== selectedStar?.id) {
      const starGraphic = starGraphicsRef.current.get(hoveredStar.id);
      if (starGraphic) {
        const glow = createGlowRing(hoveredStar.radius, 'hover');
        glow.position.copyFrom(starGraphic.position);
        (glow as any).isGlowRing = true;
        starsContainerRef.current.addChildAt(glow, 0);
      }
    }
  }, [hoveredStar, selectedStar]);

  // Bind viewport events
  useEffect(() => {
    if (!containerRef.current) return;

    const el = containerRef.current;

    el.addEventListener('wheel', viewportBind.onWheel as any, { passive: false });
    el.addEventListener('mousedown', viewportBind.onMouseDown as any);
    el.addEventListener('mousemove', viewportBind.onMouseMove as any);
    el.addEventListener('mouseup', viewportBind.onMouseUp as any);
    el.addEventListener('mouseleave', viewportBind.onMouseLeave as any);

    return () => {
      el.removeEventListener('wheel', viewportBind.onWheel as any);
      el.removeEventListener('mousedown', viewportBind.onMouseDown as any);
      el.removeEventListener('mousemove', viewportBind.onMouseMove as any);
      el.removeEventListener('mouseup', viewportBind.onMouseUp as any);
      el.removeEventListener('mouseleave', viewportBind.onMouseLeave as any);
    };
  }, [viewportBind]);

  // Bind keyboard events (vim-style navigation)
  useEffect(() => {
    window.addEventListener('keydown', keyboardHandler);
    return () => window.removeEventListener('keydown', keyboardHandler);
  }, [keyboardHandler]);

  // Loading state
  if (isLoading) {
    return (
      <div className="astronomical-chart astronomical-chart--loading">
        <div className="astronomical-chart__loading">
          <div className="astronomical-chart__spinner" />
          <span>Mapping the cosmos...</span>
        </div>
      </div>
    );
  }

  // AD-015: Needs scan state
  if (needsScan) {
    return (
      <div className="astronomical-chart astronomical-chart--needs-scan">
        <div className="astronomical-chart__needs-scan">
          <div className="astronomical-chart__needs-scan-icon">🔭</div>
          <h2>Analysis Required</h2>
          <p>
            No proxy handle data available.
            <br />
            <span className="astronomical-chart__hint">
              AD-015: Analysis is explicit, not automatic.
            </span>
          </p>
          <button onClick={scan} className="astronomical-chart__scan-button">
            Scan Spec Corpus
          </button>
          <p className="astronomical-chart__scan-note">
            This will analyze ~200 specs and generate a proxy handle.
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="astronomical-chart astronomical-chart--error">
        <div className="astronomical-chart__error">
          <span>Error loading graph: {error.message}</span>
          <button onClick={refetch}>Retry</button>
        </div>
      </div>
    );
  }

  // Empty state
  if (stars.length === 0) {
    return (
      <div className="astronomical-chart astronomical-chart--empty">
        <div className="astronomical-chart__empty">
          <span>No specs to display</span>
          <button onClick={refetch}>Refresh</button>
        </div>
      </div>
    );
  }

  return (
    <div className="astronomical-chart">
      {/* Canvas container */}
      <div ref={containerRef} className="astronomical-chart__canvas" style={{ cursor: 'grab' }} />

      {/* Controls Panel */}
      {showControls && (
        <ChartControls
          searchQuery={searchQuery}
          resultCount={searchResults.length}
          focusedIndex={focusedResultIndex}
          searchFocused={searchFocused}
          zoomLevel={viewport.scale}
          statusFilter={internalStatusFilter}
          tierFilter={tierFilter}
          isSimulating={isSimulating}
          onSearchChange={interactionActions.search}
          onSearchFocus={interactionActions.setSearchFocused}
          onZoomIn={() => viewportActions.zoom(0.2)}
          onZoomOut={() => viewportActions.zoom(-0.2)}
          onZoomReset={() => viewportActions.reset()}
          onStatusFilterChange={setInternalStatusFilter}
          onTierFilterChange={setTierFilter}
          onReheat={() => restartSimulation(0.5)}
        />
      )}

      {/* Legend */}
      {showLegend && (
        <div className="astronomical-chart__legend">
          <div className="astronomical-chart__legend-title">Tiers</div>
          <div className="astronomical-chart__legend-items">
            {[0, 1, 2, 3, 4].map((tier) => (
              <div key={tier} className="astronomical-chart__legend-item">
                <span
                  className="astronomical-chart__legend-color"
                  style={{ backgroundColor: hexToString(TIER_COLORS[tier]) }}
                />
                <span>{getTierLabel(tier)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tooltip */}
      {hoveredStar && (
        <div className="astronomical-chart__tooltip">
          <div className="astronomical-chart__tooltip-title">{hoveredStar.label}</div>
          <div className="astronomical-chart__tooltip-tier">
            {getTierLabel(hoveredStar.tier)} &middot; {hoveredStar.status.toLowerCase()}
          </div>
          <div className="astronomical-chart__tooltip-stats">
            {hoveredStar.claimCount > 0 && <span>{hoveredStar.claimCount} claims</span>}
            {hoveredStar.implCount > 0 && <span>{hoveredStar.implCount} impl</span>}
            {hoveredStar.testCount > 0 && <span>{hoveredStar.testCount} tests</span>}
          </div>
          <div className="astronomical-chart__tooltip-hint">Click to focus</div>
        </div>
      )}

      {/* Stats */}
      <div className="astronomical-chart__stats">
        {stars.length} specs &middot; {connections.length} connections
        {isSimulating && (
          <span className="astronomical-chart__simulating"> &middot; simulating...</span>
        )}
      </div>
    </div>
  );
}

export default AstronomicalChart;
