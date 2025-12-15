import { Stage, Container, Graphics, Text } from '@pixi/react';
import { useCallback, useMemo } from 'react';
import * as PIXI from 'pixi.js';
import { useTownStore } from '@/stores/townStore';
import { gridToScreen, screenToGrid, REGION_GRID_POSITIONS } from '@/lib/regionGrid';
import type { CitizenSummary } from '@/api/types';

// =============================================================================
// Constants
// =============================================================================

const GRID_SIZE = 20;
const CELL_SIZE = 24;

// Archetype colors (hex)
const ARCHETYPE_COLORS: Record<string, number> = {
  Builder: 0x3b82f6,
  Trader: 0xf59e0b,
  Healer: 0x22c55e,
  Scholar: 0x8b5cf6,
  Watcher: 0x6b7280,
};

// Phase visual states
const PHASE_ALPHA: Record<string, number> = {
  IDLE: 1.0,
  WORKING: 0.9,
  SOCIALIZING: 1.0,
  REFLECTING: 0.8,
  RESTING: 0.5,
};

// =============================================================================
// Types
// =============================================================================

interface MesaProps {
  width?: number;
  height?: number;
}

interface CitizenPosition {
  citizen: CitizenSummary;
  screenX: number;
  screenY: number;
}

// =============================================================================
// Mesa Component
// =============================================================================

export function Mesa({ width = 800, height = 600 }: MesaProps) {
  const {
    citizens,
    selectedCitizenId,
    hoveredCitizenId,
    activeInteractions,
    selectCitizen,
  } = useTownStore();

  // Calculate offsets for centering
  const offsetX = width / 2;
  const offsetY = height / 4;

  // Calculate citizen screen positions
  const citizenPositions = useMemo<CitizenPosition[]>(() => {
    // Group citizens by region
    const byRegion = new Map<string, CitizenSummary[]>();
    citizens.forEach((c) => {
      const list = byRegion.get(c.region) || [];
      list.push(c);
      byRegion.set(c.region, list);
    });

    // Calculate positions
    const positions: CitizenPosition[] = [];
    byRegion.forEach((regionCitizens, region) => {
      const basePos = REGION_GRID_POSITIONS[region] || { x: 10, y: 10 };

      regionCitizens.forEach((citizen, index) => {
        // Add small offset for multiple citizens in same region
        let gridX = basePos.x;
        let gridY = basePos.y;

        if (regionCitizens.length > 1) {
          const angleStep = (2 * Math.PI) / regionCitizens.length;
          const angle = angleStep * index;
          const radius = 1.5;
          gridX += Math.cos(angle) * radius;
          gridY += Math.sin(angle) * radius;
        }

        const screen = gridToScreen(gridX, gridY, CELL_SIZE, offsetX, offsetY);
        positions.push({
          citizen,
          screenX: screen.x,
          screenY: screen.y,
        });
      });
    });

    return positions;
  }, [citizens, offsetX, offsetY]);

  // Handle click on canvas
  const handleCanvasClick = useCallback(
    (event: PIXI.FederatedPointerEvent) => {
      const { x, y } = event.global;
      const gridPos = screenToGrid(x, y, CELL_SIZE, offsetX, offsetY);

      // Find citizen near this position (within 2 cells)
      const clickedCitizen = citizenPositions.find((cp) => {
        const cpGrid = screenToGrid(cp.screenX, cp.screenY, CELL_SIZE, offsetX, offsetY);
        const dx = Math.abs(cpGrid.x - gridPos.x);
        const dy = Math.abs(cpGrid.y - gridPos.y);
        return dx <= 1 && dy <= 1;
      });

      if (clickedCitizen) {
        selectCitizen(clickedCitizen.citizen.id);
      } else {
        selectCitizen(null);
      }
    },
    [citizenPositions, offsetX, offsetY, selectCitizen]
  );

  // Draw grid
  const drawGrid = useCallback(
    (g: PIXI.Graphics) => {
      g.clear();
      g.lineStyle(1, 0x16213e, 0.3);

      // Draw isometric grid lines
      for (let i = 0; i <= GRID_SIZE; i++) {
        // Horizontal lines
        const startH = gridToScreen(i, 0, CELL_SIZE, offsetX, offsetY);
        const endH = gridToScreen(i, GRID_SIZE, CELL_SIZE, offsetX, offsetY);
        g.moveTo(startH.x, startH.y);
        g.lineTo(endH.x, endH.y);

        // Vertical lines
        const startV = gridToScreen(0, i, CELL_SIZE, offsetX, offsetY);
        const endV = gridToScreen(GRID_SIZE, i, CELL_SIZE, offsetX, offsetY);
        g.moveTo(startV.x, startV.y);
        g.lineTo(endV.x, endV.y);
      }
    },
    [offsetX, offsetY]
  );

  // Draw region labels
  const drawRegions = useCallback(
    (g: PIXI.Graphics) => {
      g.clear();

      // Draw subtle region highlights
      Object.entries(REGION_GRID_POSITIONS).forEach(([, pos]) => {
        const screen = gridToScreen(pos.x, pos.y, CELL_SIZE, offsetX, offsetY);
        g.beginFill(0x0f3460, 0.1);
        g.drawCircle(screen.x, screen.y, CELL_SIZE * 2);
        g.endFill();
      });
    },
    [offsetX, offsetY]
  );

  // Draw interaction lines
  const drawInteractions = useCallback(
    (g: PIXI.Graphics) => {
      g.clear();

      activeInteractions.forEach((interaction) => {
        const positions = interaction.participants
          .map((name) => citizenPositions.find((cp) => cp.citizen.name === name))
          .filter((p): p is CitizenPosition => p !== undefined);

        if (positions.length < 2) return;

        const alpha = 1 - interaction.fadeProgress;
        const color =
          interaction.operation === 'greet'
            ? 0x22c55e
            : interaction.operation === 'gossip'
            ? 0xf59e0b
            : 0x3b82f6;

        g.lineStyle(2, color, alpha);

        for (let i = 0; i < positions.length - 1; i++) {
          const p1 = positions[i];
          const p2 = positions[i + 1];

          g.moveTo(p1.screenX, p1.screenY);

          // Bezier curve for visual interest
          const midX = (p1.screenX + p2.screenX) / 2;
          const midY = (p1.screenY + p2.screenY) / 2 - 20;
          g.quadraticCurveTo(midX, midY, p2.screenX, p2.screenY);
        }
      });
    },
    [activeInteractions, citizenPositions]
  );

  // Draw citizen sprite
  const drawCitizen = useCallback(
    (g: PIXI.Graphics, cp: CitizenPosition, isSelected: boolean, isHovered: boolean) => {
      const { citizen, screenX, screenY } = cp;
      const color = ARCHETYPE_COLORS[citizen.archetype] || 0x6b7280;
      const alpha = PHASE_ALPHA[citizen.phase] || 1.0;

      g.clear();

      // Selection ring
      if (isSelected) {
        g.lineStyle(3, 0xffffff, 1);
        g.drawCircle(screenX, screenY, 18);
      }

      // Hover ring
      if (isHovered && !isSelected) {
        g.lineStyle(2, 0xffffff, 0.5);
        g.drawCircle(screenX, screenY, 16);
      }

      // Main circle
      g.beginFill(color, alpha);
      g.drawCircle(screenX, screenY, 12);
      g.endFill();

      // Evolving indicator
      if (citizen.is_evolving) {
        g.lineStyle(2, 0xe94560, 0.8);
        g.drawCircle(screenX, screenY, 14);
      }
    },
    []
  );

  return (
    <Stage
      width={width}
      height={height}
      options={{
        backgroundColor: 0x1a1a2e,
        antialias: true,
      }}
    >
      <Container
        eventMode="static"
        onclick={handleCanvasClick}
        hitArea={new PIXI.Rectangle(0, 0, width, height)}
      >
        {/* Grid Layer */}
        <Graphics draw={drawGrid} />

        {/* Region Layer */}
        <Graphics draw={drawRegions} />

        {/* Interaction Lines Layer */}
        <Graphics draw={drawInteractions} />

        {/* Citizens Layer */}
        {citizenPositions.map((cp) => {
          const isSelected = selectedCitizenId === cp.citizen.id;
          const isHovered = hoveredCitizenId === cp.citizen.id;

          return (
            <Container key={cp.citizen.id}>
              <Graphics draw={(g) => drawCitizen(g, cp, isSelected, isHovered)} />
              <Text
                text={cp.citizen.archetype[0]}
                x={cp.screenX}
                y={cp.screenY}
                anchor={0.5}
                style={
                  new PIXI.TextStyle({
                    fontSize: 14,
                    fontWeight: 'bold',
                    fill: 0xffffff,
                  })
                }
              />
              {/* Name label on hover/select */}
              {(isHovered || isSelected) && (
                <Text
                  text={cp.citizen.name}
                  x={cp.screenX}
                  y={cp.screenY - 22}
                  anchor={0.5}
                  style={
                    new PIXI.TextStyle({
                      fontSize: 10,
                      fill: 0xffffff,
                      dropShadow: true,
                      dropShadowDistance: 1,
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
