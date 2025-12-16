import { Stage, Container, Graphics, Text } from '@pixi/react';
import { useCallback, useMemo } from 'react';
import * as PIXI from 'pixi.js';
import type { BuilderSummary, WorkshopPhase, BuilderArchetype } from '@/api/types';
import { BUILDER_COLORS } from '@/api/types';

// =============================================================================
// Constants
// =============================================================================

// Pipeline station positions (vertical layout)
const STATION_POSITIONS: Record<BuilderArchetype, { x: number; y: number }> = {
  Scout: { x: 0.5, y: 0.15 },
  Sage: { x: 0.5, y: 0.32 },
  Spark: { x: 0.5, y: 0.50 },
  Steady: { x: 0.5, y: 0.68 },
  Sync: { x: 0.5, y: 0.85 },
};

// Phase to archetype mapping
const PHASE_TO_ARCHETYPE: Record<string, BuilderArchetype> = {
  EXPLORING: 'Scout',
  DESIGNING: 'Sage',
  PROTOTYPING: 'Spark',
  REFINING: 'Steady',
  INTEGRATING: 'Sync',
};

// Builder icons as text
const BUILDER_ICONS: Record<BuilderArchetype, string> = {
  Scout: '🔍',
  Sage: '📐',
  Spark: '⚡',
  Steady: '🔧',
  Sync: '🔗',
};

// =============================================================================
// Types
// =============================================================================

interface WorkshopMesaProps {
  width?: number;
  height?: number;
  builders: BuilderSummary[];
  selectedBuilder: string | null;
  onSelectBuilder: (archetype: string | null) => void;
  currentPhase: WorkshopPhase;
}

interface BuilderPosition {
  builder: BuilderSummary;
  screenX: number;
  screenY: number;
  isActive: boolean;
}

// =============================================================================
// WorkshopMesa Component
// =============================================================================

export function WorkshopMesa({
  width = 800,
  height = 600,
  builders,
  selectedBuilder,
  onSelectBuilder,
  currentPhase,
}: WorkshopMesaProps) {
  // Calculate builder positions
  const builderPositions = useMemo<BuilderPosition[]>(() => {
    const activeArchetype = PHASE_TO_ARCHETYPE[currentPhase];

    return builders.map((builder) => {
      const pos = STATION_POSITIONS[builder.archetype as BuilderArchetype] || {
        x: 0.5,
        y: 0.5,
      };
      return {
        builder,
        screenX: pos.x * width,
        screenY: pos.y * height,
        isActive: builder.archetype === activeArchetype,
      };
    });
  }, [builders, width, height, currentPhase]);

  // Handle click on canvas
  const handleCanvasClick = useCallback(
    (event: PIXI.FederatedPointerEvent) => {
      const { x, y } = event.global;

      // Find builder near click position
      const clickedBuilder = builderPositions.find((bp) => {
        const dx = Math.abs(bp.screenX - x);
        const dy = Math.abs(bp.screenY - y);
        return dx <= 50 && dy <= 50;
      });

      if (clickedBuilder) {
        onSelectBuilder(clickedBuilder.builder.archetype);
      } else {
        onSelectBuilder(null);
      }
    },
    [builderPositions, onSelectBuilder]
  );

  // Draw pipeline connections
  const drawPipeline = useCallback(
    (g: PIXI.Graphics) => {
      g.clear();

      const archetypeOrder: BuilderArchetype[] = [
        'Scout',
        'Sage',
        'Spark',
        'Steady',
        'Sync',
      ];

      // Draw connecting lines
      g.lineStyle(3, 0x374151, 0.5);

      for (let i = 0; i < archetypeOrder.length - 1; i++) {
        const current = STATION_POSITIONS[archetypeOrder[i]];
        const next = STATION_POSITIONS[archetypeOrder[i + 1]];

        const x1 = current.x * width;
        const y1 = current.y * height;
        const x2 = next.x * width;
        const y2 = next.y * height;

        g.moveTo(x1, y1);
        g.lineTo(x2, y2);
      }

      // Draw flow indicator (animated arrow)
      const activeArchetype = PHASE_TO_ARCHETYPE[currentPhase];
      if (activeArchetype) {
        const activeIdx = archetypeOrder.indexOf(activeArchetype);
        if (activeIdx >= 0 && activeIdx < archetypeOrder.length - 1) {
          const current = STATION_POSITIONS[archetypeOrder[activeIdx]];
          const next = STATION_POSITIONS[archetypeOrder[activeIdx + 1]];

          const x1 = current.x * width;
          const y1 = current.y * height;
          const x2 = next.x * width;
          const y2 = next.y * height;

          // Highlight active connection
          g.lineStyle(3, 0x22c55e, 0.8);
          g.moveTo(x1, y1 + 30);
          g.lineTo(x2, y2 - 30);
        }
      }
    },
    [width, height, currentPhase]
  );

  // Draw station boxes
  const drawStations = useCallback(
    (g: PIXI.Graphics) => {
      g.clear();

      const archetypeOrder: BuilderArchetype[] = [
        'Scout',
        'Sage',
        'Spark',
        'Steady',
        'Sync',
      ];

      archetypeOrder.forEach((archetype) => {
        const pos = STATION_POSITIONS[archetype];
        const x = pos.x * width;
        const y = pos.y * height;
        const colorHex = parseInt(
          BUILDER_COLORS[archetype].replace('#', ''),
          16
        );

        // Draw station box
        g.lineStyle(2, colorHex, 0.3);
        g.beginFill(colorHex, 0.1);
        g.drawRoundedRect(x - 60, y - 25, 120, 50, 8);
        g.endFill();
      });
    },
    [width, height]
  );

  // Draw builder sprite
  const drawBuilder = useCallback(
    (
      g: PIXI.Graphics,
      bp: BuilderPosition,
      isSelected: boolean
    ) => {
      const { screenX, screenY, isActive, builder } = bp;
      const colorHex = parseInt(
        BUILDER_COLORS[builder.archetype as BuilderArchetype].replace('#', ''),
        16
      );

      g.clear();

      // Selection ring
      if (isSelected) {
        g.lineStyle(3, 0xffffff, 1);
        g.drawCircle(screenX, screenY, 32);
      }

      // Active ring (pulsing effect via alpha)
      if (isActive) {
        g.lineStyle(4, colorHex, 0.8);
        g.drawCircle(screenX, screenY, 28);
      }

      // Main circle
      g.beginFill(colorHex, isActive ? 1.0 : 0.6);
      g.drawCircle(screenX, screenY, 20);
      g.endFill();

      // In-specialty indicator (small dot)
      if (builder.is_in_specialty) {
        g.beginFill(0xffffff, 0.8);
        g.drawCircle(screenX + 15, screenY - 15, 5);
        g.endFill();
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
        {/* Pipeline Layer */}
        <Graphics draw={drawPipeline} />

        {/* Station Layer */}
        <Graphics draw={drawStations} />

        {/* Builders Layer */}
        {builderPositions.map((bp) => {
          const isSelected = selectedBuilder === bp.builder.archetype;

          return (
            <Container key={bp.builder.archetype}>
              <Graphics draw={(g) => drawBuilder(g, bp, isSelected)} />
              {/* Builder icon */}
              <Text
                text={BUILDER_ICONS[bp.builder.archetype as BuilderArchetype]}
                x={bp.screenX}
                y={bp.screenY}
                anchor={0.5}
                style={
                  new PIXI.TextStyle({
                    fontSize: 16,
                  })
                }
              />
              {/* Builder name label */}
              <Text
                text={bp.builder.archetype}
                x={bp.screenX}
                y={bp.screenY + 35}
                anchor={0.5}
                style={
                  new PIXI.TextStyle({
                    fontSize: 12,
                    fontWeight: bp.isActive ? 'bold' : 'normal',
                    fill: bp.isActive ? 0xffffff : 0x9ca3af,
                  })
                }
              />
              {/* Phase label */}
              <Text
                text={bp.builder.phase}
                x={bp.screenX}
                y={bp.screenY + 50}
                anchor={0.5}
                style={
                  new PIXI.TextStyle({
                    fontSize: 10,
                    fill: 0x6b7280,
                  })
                }
              />
            </Container>
          );
        })}

        {/* Phase indicator at top */}
        <Text
          text={`Phase: ${currentPhase}`}
          x={width / 2}
          y={20}
          anchor={0.5}
          style={
            new PIXI.TextStyle({
              fontSize: 14,
              fontWeight: 'bold',
              fill: 0xffffff,
            })
          }
        />
      </Container>
    </Stage>
  );
}

export default WorkshopMesa;
