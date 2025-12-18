/**
 * Mesa: Props-based Mesa canvas for Agent Town visualization.
 *
 * Receives citizens as props for rendering with PixiJS.
 *
 * Performance Optimizations (Phase 5.2):
 * - Mobile mode reduces draw calls and complexity
 * - Conditional grid rendering based on density
 * - Reduced event lines on mobile
 * - Device pixel ratio awareness for crisp rendering without overdraw
 *
 * @see plans/park-town-design-overhaul.md - Phase 5.2 Performance
 */

import { Stage, Container, Graphics, Text } from '@pixi/react';
import { useCallback, useMemo, useState } from 'react';
import * as PIXI from 'pixi.js';
import { gridToScreen, REGION_GRID_POSITIONS } from '@/lib/regionGrid';
import type { CitizenCardJSON } from '@/reactive/types';
import type { TownEvent } from '@/api/types';

// =============================================================================
// Constants
// =============================================================================

const GRID_SIZE = 20;

/** Cell size varies by density for better mobile rendering */
const CELL_SIZE_BY_DENSITY = {
  default: 24,
  mobile: 18, // Smaller cells on mobile for better fit
} as const;

const ARCHETYPE_COLORS: Record<string, number> = {
  // Lowercase (from widget JSON)
  builder: 0x3b82f6,
  trader: 0xf59e0b,
  healer: 0x22c55e,
  scholar: 0x8b5cf6,
  watcher: 0x6b7280,
  // PascalCase (from API)
  Builder: 0x3b82f6,
  Trader: 0xf59e0b,
  Healer: 0x22c55e,
  Scholar: 0x8b5cf6,
  Watcher: 0x6b7280,
};

const PHASE_ALPHA: Record<string, number> = {
  IDLE: 1.0,
  WORKING: 0.9,
  SOCIALIZING: 1.0,
  REFLECTING: 0.8,
  RESTING: 0.5,
};

const EVENT_LINE_COLORS: Record<string, number> = {
  greet: 0x22c55e,    // green
  gossip: 0xeab308,   // yellow
  trade: 0x3b82f6,    // blue
  solo: 0x8b5cf6,     // purple
  work: 0x06b6d4,     // cyan
  reflect: 0xa855f7,  // violet
  default: 0x6b7280,  // gray
};

/** Max event lines varies by density - fewer on mobile for performance */
const MAX_EVENT_LINES_BY_DENSITY = {
  default: 5,
  mobile: 3, // Fewer event lines on mobile
} as const;

// =============================================================================
// Types
// =============================================================================

interface MesaProps {
  width?: number;
  height?: number;
  citizens: CitizenCardJSON[];
  events?: TownEvent[];
  selectedCitizenId: string | null;
  onSelectCitizen?: (id: string) => void;
  onHoverCitizen?: (id: string | null) => void;
  /**
   * Enable mobile optimizations:
   * - Smaller cell size
   * - Fewer event lines
   * - Simplified grid (skip every other line)
   * - Lower resolution text
   */
  mobile?: boolean;
  /**
   * Skip grid rendering entirely (extreme mobile perf mode)
   */
  hideGrid?: boolean;
  /**
   * Observer-dependent overlay rendering (Phase 3)
   */
  overlay?: 'none' | 'relationships' | 'coalitions' | 'economy';
  /**
   * Observer umwelt (for future extensions)
   */
  observer?: string;
}

interface CitizenPosition {
  citizen: CitizenCardJSON;
  screenX: number;
  screenY: number;
}

// =============================================================================
// Component
// =============================================================================

export function Mesa({
  width = 800,
  height = 600,
  citizens,
  events = [],
  selectedCitizenId,
  onSelectCitizen,
  onHoverCitizen,
  mobile = false,
  hideGrid = false,
  overlay = 'none',
  observer,
}: MesaProps) {
  // Note: observer reserved for future extensions
  void observer;
  const [hoveredCitizenId, setHoveredCitizenId] = useState<string | null>(null);

  // Mobile-aware constants
  const cellSize = mobile ? CELL_SIZE_BY_DENSITY.mobile : CELL_SIZE_BY_DENSITY.default;
  const maxEventLines = mobile ? MAX_EVENT_LINES_BY_DENSITY.mobile : MAX_EVENT_LINES_BY_DENSITY.default;
  const citizenRadius = mobile ? 9 : 12;
  const fontSize = mobile ? 10 : 14;

  const offsetX = width / 2;
  const offsetY = height / 4;

  // Calculate citizen screen positions
  const citizenPositions = useMemo<CitizenPosition[]>(() => {
    const byRegion = new Map<string, CitizenCardJSON[]>();
    citizens.forEach((c) => {
      const list = byRegion.get(c.region) || [];
      list.push(c);
      byRegion.set(c.region, list);
    });

    const positions: CitizenPosition[] = [];
    byRegion.forEach((regionCitizens, region) => {
      const basePos = REGION_GRID_POSITIONS[region] || { x: 10, y: 10 };

      regionCitizens.forEach((citizen, index) => {
        let gridX = basePos.x;
        let gridY = basePos.y;

        if (regionCitizens.length > 1) {
          const angleStep = (2 * Math.PI) / regionCitizens.length;
          const angle = angleStep * index;
          const radius = 1.5;
          gridX += Math.cos(angle) * radius;
          gridY += Math.sin(angle) * radius;
        }

        const screen = gridToScreen(gridX, gridY, cellSize, offsetX, offsetY);
        positions.push({
          citizen,
          screenX: screen.x,
          screenY: screen.y,
        });
      });
    });

    return positions;
  }, [citizens, cellSize, offsetX, offsetY]);

  // Build a map of citizen name -> position for event line lookup
  const citizenPositionByName = useMemo(() => {
    const map = new Map<string, CitizenPosition>();
    citizenPositions.forEach((cp) => {
      map.set(cp.citizen.name, cp);
    });
    return map;
  }, [citizenPositions]);

  // Calculate event lines (recent events with 2+ participants)
  const eventLines = useMemo(() => {
    const lines: Array<{
      from: { x: number; y: number };
      to: { x: number; y: number };
      color: number;
      alpha: number;
      operation: string;
    }> = [];

    // Take only the most recent events (fewer on mobile for perf)
    const recentEvents = events.slice(0, maxEventLines);

    recentEvents.forEach((event, index) => {
      if (event.participants.length < 2) return;

      // Get positions for first two participants
      const fromPos = citizenPositionByName.get(event.participants[0]);
      const toPos = citizenPositionByName.get(event.participants[1]);

      if (fromPos && toPos) {
        // Fade older events (most recent = full opacity)
        const alpha = 1.0 - (index / maxEventLines) * 0.6;
        const color = EVENT_LINE_COLORS[event.operation] || EVENT_LINE_COLORS.default;

        lines.push({
          from: { x: fromPos.screenX, y: fromPos.screenY },
          to: { x: toPos.screenX, y: toPos.screenY },
          color,
          alpha,
          operation: event.operation,
        });
      }
    });

    return lines;
  }, [events, citizenPositionByName, maxEventLines]);

  // Draw event lines
  const drawEventLines = useCallback(
    (g: PIXI.Graphics) => {
      g.clear();

      eventLines.forEach((line) => {
        // Draw glow effect (thicker, more transparent)
        g.lineStyle(6, line.color, line.alpha * 0.3);
        g.moveTo(line.from.x, line.from.y);
        g.lineTo(line.to.x, line.to.y);

        // Draw main line
        g.lineStyle(2, line.color, line.alpha);
        g.moveTo(line.from.x, line.from.y);
        g.lineTo(line.to.x, line.to.y);

        // Draw small circles at endpoints
        g.beginFill(line.color, line.alpha);
        g.drawCircle(line.from.x, line.from.y, 4);
        g.drawCircle(line.to.x, line.to.y, 4);
        g.endFill();
      });
    },
    [eventLines]
  );

  // Draw overlays (observer-dependent rendering - Phase 3)
  const drawRelationshipsOverlay = useCallback(
    (g: PIXI.Graphics) => {
      g.clear();

      // Draw blue lines between citizens (relationship web)
      // Uses a simple algorithm: connect citizens in the same region
      const byRegion = new Map<string, CitizenPosition[]>();
      citizenPositions.forEach((cp) => {
        const list = byRegion.get(cp.citizen.region) || [];
        list.push(cp);
        byRegion.set(cp.citizen.region, list);
      });

      byRegion.forEach((regionCitizens) => {
        if (regionCitizens.length < 2) return;

        // Connect each citizen to every other in the region
        for (let i = 0; i < regionCitizens.length; i++) {
          for (let j = i + 1; j < regionCitizens.length; j++) {
            const from = regionCitizens[i];
            const to = regionCitizens[j];

            // Draw relationship line (blue, subtle)
            g.lineStyle(1, 0x3b82f6, 0.3);
            g.moveTo(from.screenX, from.screenY);
            g.lineTo(to.screenX, to.screenY);
          }
        }
      });
    },
    [citizenPositions]
  );

  const drawEconomyOverlay = useCallback(
    (g: PIXI.Graphics) => {
      g.clear();

      // Draw green particles representing trade/value flows
      // For now, show trade potential as pulsing rings around traders
      citizenPositions.forEach((cp) => {
        if (cp.citizen.archetype.toLowerCase() === 'trader') {
          // Pulsing ring effect (green)
          g.lineStyle(2, 0x22c55e, 0.4);
          g.drawCircle(cp.screenX, cp.screenY, 30);
          g.lineStyle(1, 0x22c55e, 0.2);
          g.drawCircle(cp.screenX, cp.screenY, 45);
        }
      });

      // Draw trade lines between traders
      const traders = citizenPositions.filter((cp) =>
        cp.citizen.archetype.toLowerCase() === 'trader'
      );
      for (let i = 0; i < traders.length; i++) {
        for (let j = i + 1; j < traders.length; j++) {
          const from = traders[i];
          const to = traders[j];

          // Draw trade flow line (green, animated appearance)
          g.lineStyle(2, 0x22c55e, 0.2);
          g.moveTo(from.screenX, from.screenY);
          g.lineTo(to.screenX, to.screenY);
        }
      }
    },
    [citizenPositions]
  );

  const drawCoalitionsOverlay = useCallback(
    (g: PIXI.Graphics) => {
      g.clear();

      // Draw coalition boundaries (purple/violet)
      // Group citizens by region and draw convex hull-like boundaries
      const byRegion = new Map<string, CitizenPosition[]>();
      citizenPositions.forEach((cp) => {
        const list = byRegion.get(cp.citizen.region) || [];
        list.push(cp);
        byRegion.set(cp.citizen.region, list);
      });

      byRegion.forEach((regionCitizens) => {
        if (regionCitizens.length < 2) return;

        // Find bounding circle for coalition
        const xs = regionCitizens.map((c) => c.screenX);
        const ys = regionCitizens.map((c) => c.screenY);
        const centerX = xs.reduce((a, b) => a + b, 0) / xs.length;
        const centerY = ys.reduce((a, b) => a + b, 0) / ys.length;
        const maxDist = Math.max(
          ...regionCitizens.map((c) =>
            Math.sqrt((c.screenX - centerX) ** 2 + (c.screenY - centerY) ** 2)
          )
        );

        // Draw coalition boundary (purple glow)
        g.lineStyle(2, 0x8b5cf6, 0.3);
        g.beginFill(0x8b5cf6, 0.05);
        g.drawCircle(centerX, centerY, maxDist + 20);
        g.endFill();
      });
    },
    [citizenPositions]
  );

  // Handle hover
  const handleHover = useCallback(
    (id: string | null) => {
      setHoveredCitizenId(id);
      onHoverCitizen?.(id);
    },
    [onHoverCitizen]
  );

  // Draw grid (simplified on mobile - skip every other line)
  const drawGrid = useCallback(
    (g: PIXI.Graphics) => {
      g.clear();
      g.lineStyle(1, 0x16213e, mobile ? 0.2 : 0.3);

      // On mobile, skip every other grid line for performance
      const step = mobile ? 2 : 1;

      for (let i = 0; i <= GRID_SIZE; i += step) {
        const startH = gridToScreen(i, 0, cellSize, offsetX, offsetY);
        const endH = gridToScreen(i, GRID_SIZE, cellSize, offsetX, offsetY);
        g.moveTo(startH.x, startH.y);
        g.lineTo(endH.x, endH.y);

        const startV = gridToScreen(0, i, cellSize, offsetX, offsetY);
        const endV = gridToScreen(GRID_SIZE, i, cellSize, offsetX, offsetY);
        g.moveTo(startV.x, startV.y);
        g.lineTo(endV.x, endV.y);
      }
    },
    [cellSize, offsetX, offsetY, mobile]
  );

  // Draw region highlights
  const drawRegions = useCallback(
    (g: PIXI.Graphics) => {
      g.clear();
      Object.entries(REGION_GRID_POSITIONS).forEach(([, pos]) => {
        const screen = gridToScreen(pos.x, pos.y, cellSize, offsetX, offsetY);
        g.beginFill(0x0f3460, mobile ? 0.08 : 0.1);
        g.drawCircle(screen.x, screen.y, cellSize * 2);
        g.endFill();
      });
    },
    [cellSize, offsetX, offsetY, mobile]
  );

  // Draw citizen sprite (scaled for mobile)
  const drawCitizen = useCallback(
    (g: PIXI.Graphics, cp: CitizenPosition, isSelected: boolean, isHovered: boolean) => {
      const { citizen, screenX, screenY } = cp;
      const color = ARCHETYPE_COLORS[citizen.archetype] || 0x888888;
      const alpha = PHASE_ALPHA[citizen.phase] || 1.0;

      g.clear();

      // Selection ring (scaled for mobile)
      if (isSelected) {
        g.lineStyle(mobile ? 2 : 3, 0xffffff, 1);
        g.drawCircle(screenX, screenY, citizenRadius + 6);
      }

      // Hover ring
      if (isHovered && !isSelected) {
        g.lineStyle(2, 0xffffff, 0.5);
        g.drawCircle(screenX, screenY, citizenRadius + 4);
      }

      // Main circle
      g.beginFill(color, alpha);
      g.drawCircle(screenX, screenY, citizenRadius);
      g.endFill();
    },
    [mobile, citizenRadius]
  );

  return (
    <Stage
      width={width}
      height={height}
      options={{
        backgroundColor: 0x1a1a2e,
        // Disable antialias on mobile for performance
        antialias: !mobile,
        // Use lower resolution on mobile (1 instead of devicePixelRatio)
        resolution: mobile ? 1 : window.devicePixelRatio || 1,
        autoDensity: true,
      }}
    >
      <Container>
        {/* Grid Layer - conditionally rendered for mobile perf */}
        {!hideGrid && <Graphics draw={drawGrid} />}

        {/* Region Layer */}
        <Graphics draw={drawRegions} />

        {/* Event Lines Layer - shows recent interactions between citizens */}
        <Graphics draw={drawEventLines} />

        {/* Observer Overlay Layer (Phase 3) - drawn after events, before citizens */}
        {overlay === 'relationships' && <Graphics draw={drawRelationshipsOverlay} />}
        {overlay === 'economy' && <Graphics draw={drawEconomyOverlay} />}
        {overlay === 'coalitions' && <Graphics draw={drawCoalitionsOverlay} />}

        {/* Region labels - smaller font on mobile */}
        {Object.entries(REGION_GRID_POSITIONS).map(([region, pos]) => {
          const screen = gridToScreen(pos.x, pos.y - 1.5, cellSize, offsetX, offsetY);
          return (
            <Text
              key={region}
              text={region}
              x={screen.x}
              y={screen.y}
              anchor={0.5}
              style={
                new PIXI.TextStyle({
                  fontSize: mobile ? 8 : 10,
                  fill: 0x666666,
                  fontFamily: 'monospace',
                })
              }
            />
          );
        })}

        {/* Citizens */}
        {citizenPositions.map((pos) => {
          const isSelected = pos.citizen.citizen_id === selectedCitizenId;
          const isHovered = pos.citizen.citizen_id === hoveredCitizenId;

          return (
            <Container key={pos.citizen.citizen_id}>
              <Graphics
                draw={(g) => drawCitizen(g, pos, isSelected, isHovered)}
                eventMode="static"
                cursor="pointer"
                pointerdown={() => onSelectCitizen?.(pos.citizen.citizen_id)}
                pointerover={() => handleHover(pos.citizen.citizen_id)}
                pointerout={() => handleHover(null)}
              />
              {/* Archetype letter */}
              <Text
                text={pos.citizen.archetype[0].toUpperCase()}
                x={pos.screenX}
                y={pos.screenY}
                anchor={0.5}
                style={
                  new PIXI.TextStyle({
                    fontSize: fontSize,
                    fontWeight: 'bold',
                    fill: 0xffffff,
                  })
                }
              />
              {/* Name label on hover/select - simplified on mobile */}
              {(isHovered || isSelected) && (
                <Text
                  text={pos.citizen.name}
                  x={pos.screenX}
                  y={pos.screenY - (citizenRadius + 10)}
                  anchor={0.5}
                  style={
                    new PIXI.TextStyle({
                      fontSize: mobile ? 8 : 10,
                      fill: 0xffffff,
                      // Skip drop shadow on mobile for perf
                      dropShadow: !mobile,
                      dropShadowDistance: mobile ? 0 : 1,
                    })
                  }
                />
              )}
            </Container>
          );
        })}
      </Container>
    </Stage>
  );
}

export default Mesa;
