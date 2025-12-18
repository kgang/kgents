/**
 * TownCanvas3D - 3D projection surface for Agent Town
 *
 * Implements the "Living Earth" visualization using TopologyNode3D primitives.
 * Citizens are rendered as breathing spheres in 3D space with relationship edges.
 *
 * @see plans/town-visualizer-renaissance.md - Phase 4: Projection Surfaces
 * @see constants/town.ts - TOWN_THEME_3D configuration
 */

import { Suspense, useMemo, useCallback } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Html, Line } from '@react-three/drei';
import * as THREE from 'three';

import { TopologyNode3D } from '@/components/three';
import type { ThemePalette, Density } from '@/components/three/primitives/themes/types';
import { TOWN_THEME_3D, TOWN_THEME } from '@/constants';
import type { CitizenCardJSON } from '@/reactive/types';

// =============================================================================
// Types
// =============================================================================

export interface TownCanvas3DProps {
  /** Array of citizens to render */
  citizens: CitizenCardJSON[];

  /** Relationships between citizens (citizen_id pairs) */
  relationships?: Array<{
    from: string;
    to: string;
    strength: number;
    type?: string;
  }>;

  /** Currently selected citizen ID */
  selectedCitizenId: string | null;

  /** Callback when a citizen is clicked */
  onSelectCitizen?: (citizenId: string) => void;

  /** Canvas width */
  width?: number;

  /** Canvas height */
  height?: number;

  /** Layout density */
  density?: Density;

  /** Whether to show labels */
  showLabels?: boolean;

  /** Whether to show relationship edges */
  showEdges?: boolean;

  /** Current town phase (for ambient lighting) */
  townPhase?: 'MORNING' | 'AFTERNOON' | 'EVENING' | 'NIGHT';
}

// =============================================================================
// Theme Configuration
// =============================================================================

/**
 * Town theme palette for TopologyNode3D
 *
 * Maps archetype tiers to visual properties.
 */
const TOWN_THEME_PALETTE: ThemePalette = {
  name: 'town',
  description: 'Living Earth theme for Agent Town visualization',
  nodeTiers: {
    // Archetypes
    builder: { core: '#3B82F6', glow: '#60A5FA', ring: '#93C5FD' },
    trader: { core: '#F59E0B', glow: '#FBBF24', ring: '#FCD34D' },
    healer: { core: '#22C55E', glow: '#4ADE80', ring: '#86EFAC' },
    scholar: { core: '#8B5CF6', glow: '#A78BFA', ring: '#C4B5FD' },
    watcher: { core: '#6B7280', glow: '#9CA3AF', ring: '#D1D5DB' },
    // Fallback
    default: { core: '#6B8B6B', glow: '#8FBC8F', ring: '#98FB98' },
  },
  edgeColors: {
    base: '#6B8B6B',
    highlight: '#D4A574',
    glow: '#FFE4B5',
    violation: '#EF4444',
  },
  particleColors: {
    normal: '#D4A574',
    active: '#FFE4B5',
  },
  selectionColor: '#FFD700',
  hoverColor: '#D4A574',
  labelColor: '#F5F0E8',
  labelOutlineColor: '#2D1B14',
};

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Convert citizen archetype to tier name
 */
function getTier(citizen: CitizenCardJSON): string {
  const archetype = citizen.archetype?.toLowerCase() ?? 'default';
  return archetype in TOWN_THEME_PALETTE.nodeTiers ? archetype : 'default';
}

/**
 * Calculate citizen node size based on engagement/activity
 */
function getSize(citizen: CitizenCardJSON, density: Density): number {
  const baseSizes = { compact: 0.3, comfortable: 0.4, spacious: 0.5 };
  const base = baseSizes[density] ?? 0.4;

  // Slightly larger for more active citizens
  const activityBonus = citizen.phase === 'WORKING' || citizen.phase === 'SOCIALIZING' ? 1.15 : 1.0;

  return base * activityBonus;
}

/**
 * Calculate 3D position for a citizen based on region
 */
function getCitizenPosition(
  citizen: CitizenCardJSON,
  index: number,
  _total: number
): [number, number, number] {
  // Region base positions (spread in XZ plane)
  const regionPositions: Record<string, [number, number]> = {
    inn: [-4, -4],
    workshop: [4, -4],
    plaza: [0, 0],
    market: [4, 4],
    library: [-4, 4],
    temple: [0, -6],
    garden: [0, 6],
  };

  const basePos = regionPositions[citizen.region?.toLowerCase() ?? 'plaza'] ?? [0, 0];

  // Spread citizens within region using fibonacci spiral
  const goldenAngle = Math.PI * (3 - Math.sqrt(5));
  const angle = index * goldenAngle;
  const radius = Math.sqrt(index + 1) * 0.8;

  const x = basePos[0] + Math.cos(angle) * radius;
  const z = basePos[1] + Math.sin(angle) * radius;

  // Y position based on phase (resting = lower)
  const y = citizen.phase === 'RESTING' ? -0.5 : citizen.phase === 'REFLECTING' ? 0.5 : 0;

  return [x, y, z];
}

// =============================================================================
// Sub-Components
// =============================================================================

interface CitizenNode3DProps {
  citizen: CitizenCardJSON;
  position: [number, number, number];
  isSelected: boolean;
  onClick: () => void;
  showLabel: boolean;
  density: Density;
}

function CitizenNode3D({
  citizen,
  position,
  isSelected,
  onClick,
  showLabel,
  density,
}: CitizenNode3DProps) {
  return (
    <TopologyNode3D
      position={position}
      theme={TOWN_THEME_PALETTE}
      data={citizen}
      getTier={getTier}
      getSize={getSize}
      isSelected={isSelected}
      onClick={onClick}
      showLabel={showLabel}
      label={citizen.name}
      density={density}
      animationSpeed={citizen.phase === 'RESTING' ? 0.3 : 1.0}
      roughness={0.6}
      metalness={0.1}
      segments={24}
    />
  );
}

interface RelationshipEdge3DProps {
  from: [number, number, number];
  to: [number, number, number];
  strength: number;
  type?: string;
}

function RelationshipEdge3D({ from, to, strength, type }: RelationshipEdge3DProps) {
  const color = useMemo(() => {
    // Color by relationship type
    switch (type?.toLowerCase()) {
      case 'trust':
        return '#22C55E'; // Green
      case 'trade':
        return '#F59E0B'; // Amber
      case 'conflict':
        return '#EF4444'; // Red
      default:
        return '#6B8B6B'; // Sage
    }
  }, [type]);

  // Simple line edge (lighter weight than TopologyEdge3D)
  const points = useMemo(() => [new THREE.Vector3(...from), new THREE.Vector3(...to)], [from, to]);

  return (
    <Line
      points={points}
      color={color}
      lineWidth={1 + strength * 2}
      transparent
      opacity={0.3 + strength * 0.4}
    />
  );
}

// =============================================================================
// Loading Fallback
// =============================================================================

function LoadingFallback() {
  return (
    <Html center>
      <div className="text-sm text-amber-200/70 animate-pulse">Loading Town...</div>
    </Html>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function TownCanvas3D({
  citizens,
  relationships = [],
  selectedCitizenId,
  onSelectCitizen,
  width = 800,
  height = 600,
  density = 'comfortable',
  showLabels = true,
  showEdges = true,
  townPhase = 'AFTERNOON',
}: TownCanvas3DProps) {
  // Calculate positions for all citizens
  const citizenPositions = useMemo(() => {
    const positions = new Map<string, [number, number, number]>();
    citizens.forEach((citizen, index) => {
      positions.set(citizen.citizen_id, getCitizenPosition(citizen, index, citizens.length));
    });
    return positions;
  }, [citizens]);

  // Handle citizen selection
  const handleCitizenClick = useCallback(
    (citizenId: string) => {
      onSelectCitizen?.(citizenId);
    },
    [onSelectCitizen]
  );

  // Calculate ambient light based on town phase
  const ambientIntensity = useMemo(() => {
    switch (townPhase) {
      case 'MORNING':
        return 0.6;
      case 'AFTERNOON':
        return 0.8;
      case 'EVENING':
        return 0.4;
      case 'NIGHT':
        return 0.2;
      default:
        return 0.5;
    }
  }, [townPhase]);

  return (
    <div style={{ width, height }} className="relative">
      <Canvas
        camera={{ position: [0, 12, 12], fov: 45 }}
        gl={{ antialias: true, alpha: false }}
        style={{ background: `#${TOWN_THEME_3D.background.toString(16)}` }}
      >
        <Suspense fallback={<LoadingFallback />}>
          {/* Lighting */}
          <ambientLight intensity={ambientIntensity} color="#FFE4B5" />
          <directionalLight
            position={TOWN_THEME_3D.lighting.directionalPosition}
            intensity={TOWN_THEME_3D.lighting.directionalIntensity}
            color="#FFFAF0"
            castShadow
          />

          {/* Ground plane (soil color) */}
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]} receiveShadow>
            <planeGeometry args={[30, 30]} />
            <meshStandardMaterial color="#2D1B14" roughness={0.9} />
          </mesh>

          {/* Relationship edges */}
          {showEdges &&
            relationships.map((rel, index) => {
              const fromPos = citizenPositions.get(rel.from);
              const toPos = citizenPositions.get(rel.to);
              if (!fromPos || !toPos) return null;

              return (
                <RelationshipEdge3D
                  key={`edge-${index}`}
                  from={fromPos}
                  to={toPos}
                  strength={rel.strength}
                  type={rel.type}
                />
              );
            })}

          {/* Citizens */}
          {citizens.map((citizen) => {
            const position = citizenPositions.get(citizen.citizen_id);
            if (!position) return null;

            return (
              <CitizenNode3D
                key={citizen.citizen_id}
                citizen={citizen}
                position={position}
                isSelected={citizen.citizen_id === selectedCitizenId}
                onClick={() => handleCitizenClick(citizen.citizen_id)}
                showLabel={showLabels}
                density={density}
              />
            );
          })}

          {/* Camera controls */}
          <OrbitControls
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            minDistance={5}
            maxDistance={30}
            maxPolarAngle={Math.PI / 2.2} // Prevent going below ground
          />
        </Suspense>
      </Canvas>

      {/* Phase indicator overlay */}
      <div className="absolute top-2 right-2 px-2 py-1 bg-black/40 rounded text-xs text-amber-200/80">
        {TOWN_THEME.phases.town[townPhase as keyof typeof TOWN_THEME.phases.town]
          ? `${townPhase.charAt(0)}${townPhase.slice(1).toLowerCase()}`
          : 'Afternoon'}
      </div>
    </div>
  );
}

export default TownCanvas3D;
