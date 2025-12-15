/**
 * MesaV2: Props-based Mesa canvas.
 *
 * Receives citizens as props instead of reading from Zustand store.
 * This enables the component to work with widget JSON data.
 */

import { Stage, Container, Graphics, Text } from '@pixi/react';
import { useCallback, useMemo, useState } from 'react';
import * as PIXI from 'pixi.js';
import { gridToScreen, REGION_GRID_POSITIONS } from '@/lib/regionGrid';
import type { CitizenCardJSON } from '@/reactive/types';

// =============================================================================
// Constants
// =============================================================================

const GRID_SIZE = 20;
const CELL_SIZE = 24;

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

// =============================================================================
// Types
// =============================================================================

interface MesaV2Props {
  width?: number;
  height?: number;
  citizens: CitizenCardJSON[];
  selectedCitizenId: string | null;
  onSelectCitizen?: (id: string) => void;
  onHoverCitizen?: (id: string | null) => void;
}

interface CitizenPosition {
  citizen: CitizenCardJSON;
  screenX: number;
  screenY: number;
}

// =============================================================================
// Component
// =============================================================================

export function MesaV2({
  width = 800,
  height = 600,
  citizens,
  selectedCitizenId,
  onSelectCitizen,
  onHoverCitizen,
}: MesaV2Props) {
  const [hoveredCitizenId, setHoveredCitizenId] = useState<string | null>(null);
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

  // Handle hover
  const handleHover = useCallback(
    (id: string | null) => {
      setHoveredCitizenId(id);
      onHoverCitizen?.(id);
    },
    [onHoverCitizen]
  );

  // Draw grid
  const drawGrid = useCallback(
    (g: PIXI.Graphics) => {
      g.clear();
      g.lineStyle(1, 0x16213e, 0.3);

      for (let i = 0; i <= GRID_SIZE; i++) {
        const startH = gridToScreen(i, 0, CELL_SIZE, offsetX, offsetY);
        const endH = gridToScreen(i, GRID_SIZE, CELL_SIZE, offsetX, offsetY);
        g.moveTo(startH.x, startH.y);
        g.lineTo(endH.x, endH.y);

        const startV = gridToScreen(0, i, CELL_SIZE, offsetX, offsetY);
        const endV = gridToScreen(GRID_SIZE, i, CELL_SIZE, offsetX, offsetY);
        g.moveTo(startV.x, startV.y);
        g.lineTo(endV.x, endV.y);
      }
    },
    [offsetX, offsetY]
  );

  // Draw region highlights
  const drawRegions = useCallback(
    (g: PIXI.Graphics) => {
      g.clear();
      Object.entries(REGION_GRID_POSITIONS).forEach(([, pos]) => {
        const screen = gridToScreen(pos.x, pos.y, CELL_SIZE, offsetX, offsetY);
        g.beginFill(0x0f3460, 0.1);
        g.drawCircle(screen.x, screen.y, CELL_SIZE * 2);
        g.endFill();
      });
    },
    [offsetX, offsetY]
  );

  // Draw citizen sprite
  const drawCitizen = useCallback(
    (g: PIXI.Graphics, cp: CitizenPosition, isSelected: boolean, isHovered: boolean) => {
      const { citizen, screenX, screenY } = cp;
      const color = ARCHETYPE_COLORS[citizen.archetype] || 0x888888;
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
      <Container>
        {/* Grid Layer */}
        <Graphics draw={drawGrid} />

        {/* Region Layer */}
        <Graphics draw={drawRegions} />

        {/* Region labels */}
        {Object.entries(REGION_GRID_POSITIONS).map(([region, pos]) => {
          const screen = gridToScreen(pos.x, pos.y - 1.5, CELL_SIZE, offsetX, offsetY);
          return (
            <Text
              key={region}
              text={region}
              x={screen.x}
              y={screen.y}
              anchor={0.5}
              style={
                new PIXI.TextStyle({
                  fontSize: 10,
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
                    fontSize: 14,
                    fontWeight: 'bold',
                    fill: 0xffffff,
                  })
                }
              />
              {/* Name label on hover/select */}
              {(isHovered || isSelected) && (
                <Text
                  text={pos.citizen.name}
                  x={pos.screenX}
                  y={pos.screenY - 22}
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

export default MesaV2;
