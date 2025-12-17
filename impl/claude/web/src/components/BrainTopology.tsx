/**
 * BrainTopology - 3D Visualization of Holographic Memory
 *
 * A living visualization of the memory crystal field.
 *
 * Design Philosophy:
 *   "Memories are not data points—they are living crystallizations of thought."
 *
 * Features:
 * - OrganicCrystal nodes with breathing animation and resolution rings
 * - CrystalVine curved connections with flow particles
 * - Hub crystal highlighting with orbital rings
 * - Gap detection visualization (sparse regions highlighted)
 * - Mobile touch gestures for rotation/zoom
 * - Cymatics background for ambient depth
 *
 * @see docs/creative/emergence-principles.md
 * @see docs/skills/3d-lighting-patterns.md
 */

import { useRef, useState, useMemo, useCallback } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import type {
  TopologyNode,
  TopologyGap,
  BrainTopologyResponse,
} from '../api/types';
import { SceneLighting, ShadowPlane } from './three/SceneLighting';
import { SceneEffects } from './three/SceneEffects';
import { QualitySelector } from './three/QualitySelector';
import { calculateCenteredShadowBounds } from '../utils/three/calculateShadowBounds';
import { useSceneContext } from '../hooks/useSceneContext';
import { OrganicCrystal } from './brain/OrganicCrystal';
import { SmartCrystalVine } from './brain/CrystalVine';
import { PatternTile, PATTERN_PRESETS } from './three/CymaticsSampler';

// =============================================================================
// Types
// =============================================================================

interface BrainTopologyProps {
  topology: BrainTopologyResponse | null;
  onNodeClick?: (node: TopologyNode) => void;
  selectedNodeId?: string | null;
  showEdges?: boolean;
  showGaps?: boolean;
  showLabels?: boolean;
}

// Note: Density type is used by OrganicCrystal internally

interface GapSphereProps {
  gap: TopologyGap;
}

// =============================================================================
// NOTE: CrystalNode and TopologyEdgeComponent have been replaced by:
// - OrganicCrystal (from ./brain/OrganicCrystal)
// - SmartCrystalVine (from ./brain/CrystalVine)
//
// These new components implement emergence principles:
// - Breathing animation
// - Resolution rings (like tree rings)
// - Curved organic connections
// - Flow particles for active edges
// =============================================================================

// =============================================================================
// Gap Sphere Component
// =============================================================================

function GapSphereComponent({ gap }: GapSphereProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  // Gentle pulsing animation
  useFrame(({ clock }) => {
    if (meshRef.current) {
      const scale = 1 + Math.sin(clock.elapsedTime * 2) * 0.1;
      meshRef.current.scale.setScalar(scale);
    }
  });

  return (
    <mesh ref={meshRef} position={[gap.x, gap.y, gap.z]}>
      <sphereGeometry args={[gap.radius * 0.3, 16, 16]} />
      <meshBasicMaterial
        color="#ff4444"
        transparent
        opacity={0.15}
        wireframe
      />
    </mesh>
  );
}

// =============================================================================
// NOTE: NodeLabels component has been removed.
// Labels are now rendered by OrganicCrystal component directly,
// with proper integration into the crystal's visual hierarchy.
// =============================================================================

// =============================================================================
// Scene Component
// =============================================================================

interface SceneProps {
  topology: BrainTopologyResponse;
  onNodeClick: (node: TopologyNode) => void;
  selectedNodeId: string | null;
  showEdges: boolean;
  showGaps: boolean;
  showLabels: boolean;
  /** Illumination quality from useSceneContext */
  illuminationQuality?: 'minimal' | 'standard' | 'high' | 'cinematic';
}

function Scene({
  topology,
  onNodeClick,
  selectedNodeId,
  showEdges,
  showGaps,
  showLabels,
  illuminationQuality = 'standard',
}: SceneProps) {
  const nodeMap = useMemo(
    () => new Map(topology.nodes.map((n) => [n.id, n])),
    [topology.nodes]
  );

  const hubSet = useMemo(() => new Set(topology.hub_ids), [topology.hub_ids]);

  // Calculate shadow bounds from node positions
  const shadowBounds = useMemo(
    () => calculateCenteredShadowBounds(topology.nodes),
    [topology.nodes]
  );

  // Determine which edges are connected to selected node
  const activeEdgeSet = useMemo(() => {
    if (!selectedNodeId) return new Set<number>();
    const activeEdges = new Set<number>();
    topology.edges.forEach((edge, i) => {
      if (edge.source === selectedNodeId || edge.target === selectedNodeId) {
        activeEdges.add(i);
      }
    });
    return activeEdges;
  }, [selectedNodeId, topology.edges]);

  return (
    <>
      {/* Cymatics background pattern - spiral for brain/memory theme */}
      <PatternTile
        config={PATTERN_PRESETS['spiral-5']}
        size={60}
        position={[0, 0, -25]}
        animate
      />

      {/* Canonical lighting from SceneLighting */}
      <SceneLighting
        quality={illuminationQuality}
        bounds={shadowBounds}
        atmosphericFill
      />

      {/* Post-processing effects (SSAO for high/cinematic quality) */}
      <SceneEffects quality={illuminationQuality} />

      {/* Shadow-receiving ground plane */}
      <ShadowPlane y={-10} shadowOpacity={0.25} />

      {/* Organic Vine Connections (edges) */}
      {showEdges &&
        topology.edges.map((edge, i) => {
          const sourceNode = nodeMap.get(edge.source);
          const targetNode = nodeMap.get(edge.target);
          if (!sourceNode || !targetNode) return null;

          return (
            <SmartCrystalVine
              key={`vine-${i}`}
              source={[sourceNode.x, sourceNode.y, sourceNode.z]}
              target={[targetNode.x, targetNode.y, targetNode.z]}
              similarity={edge.similarity}
              isActive={activeEdgeSet.has(i)}
              isDimmed={selectedNodeId !== null && !activeEdgeSet.has(i)}
              animationEnabled
            />
          );
        })}

      {/* Gaps */}
      {showGaps &&
        topology.gaps.map((gap, i) => <GapSphereComponent key={`gap-${i}`} gap={gap} />)}

      {/* Organic Crystal Nodes */}
      {topology.nodes.map((node) => (
        <OrganicCrystal
          key={node.id}
          node={node}
          isHub={hubSet.has(node.id)}
          isSelected={node.id === selectedNodeId}
          onClick={() => onNodeClick(node)}
          showLabel={showLabels}
          density="comfortable"
          animationSpeed={1}
        />
      ))}

      {/* Camera Controls - mobile touch enabled */}
      <OrbitControls
        enablePan
        enableZoom
        enableRotate
        minDistance={2}
        maxDistance={50}
        touches={{
          ONE: THREE.TOUCH.ROTATE,
          TWO: THREE.TOUCH.DOLLY_PAN,
        }}
      />
    </>
  );
}

// =============================================================================
// Crystal Sidebar Component
// =============================================================================

interface CrystalSidebarProps {
  node: TopologyNode | null;
  onClose: () => void;
}

function CrystalSidebar({ node, onClose }: CrystalSidebarProps) {
  if (!node) return null;

  const ageDisplay = useMemo(() => {
    const hours = Math.floor(node.age_seconds / 3600);
    const days = Math.floor(hours / 24);
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    return 'Just now';
  }, [node.age_seconds]);

  const resolutionPercent = Math.round(node.resolution * 100);
  const decayState =
    node.resolution > 0.7 ? 'Fresh' : node.resolution > 0.4 ? 'Fading' : 'Ghost';

  return (
    <div className="absolute right-0 top-0 h-full w-80 bg-gray-800/95 border-l border-gray-700 p-4 overflow-y-auto">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-white">{node.label}</h3>
          <p className="text-xs text-gray-400 font-mono">{node.id}</p>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white text-xl"
          aria-label="Close"
        >
          ×
        </button>
      </div>

      {/* Status badges */}
      <div className="flex gap-2 mb-4">
        {node.is_hot && (
          <span className="px-2 py-1 text-xs bg-orange-500/20 text-orange-400 rounded">
            Hot Crystal
          </span>
        )}
        <span
          className={`px-2 py-1 text-xs rounded ${
            decayState === 'Fresh'
              ? 'bg-cyan-500/20 text-cyan-400'
              : decayState === 'Fading'
                ? 'bg-purple-500/20 text-purple-400'
                : 'bg-gray-500/20 text-gray-400'
          }`}
        >
          {decayState}
        </span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-gray-700/50 rounded p-2">
          <p className="text-xs text-gray-400">Resolution</p>
          <p className="text-lg font-semibold text-white">{resolutionPercent}%</p>
        </div>
        <div className="bg-gray-700/50 rounded p-2">
          <p className="text-xs text-gray-400">Accesses</p>
          <p className="text-lg font-semibold text-white">{node.access_count}</p>
        </div>
        <div className="bg-gray-700/50 rounded p-2">
          <p className="text-xs text-gray-400">Age</p>
          <p className="text-lg font-semibold text-white">{ageDisplay}</p>
        </div>
        <div className="bg-gray-700/50 rounded p-2">
          <p className="text-xs text-gray-400">Position</p>
          <p className="text-sm font-mono text-white">
            {node.x.toFixed(1)}, {node.y.toFixed(1)}
          </p>
        </div>
      </div>

      {/* Resolution bar */}
      <div className="mb-4">
        <p className="text-xs text-gray-400 mb-1">Memory Resolution</p>
        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full transition-all duration-300"
            style={{
              width: `${resolutionPercent}%`,
              background: `linear-gradient(90deg,
                ${node.resolution > 0.7 ? '#06b6d4' : node.resolution > 0.4 ? '#8b5cf6' : '#6b7280'} 0%,
                ${node.resolution > 0.7 ? '#0891b2' : node.resolution > 0.4 ? '#7c3aed' : '#4b5563'} 100%)`,
            }}
          />
        </div>
      </div>

      {/* Content preview */}
      {node.content_preview && (
        <div className="mb-4">
          <p className="text-xs text-gray-400 mb-1">Content Preview</p>
          <div className="bg-gray-900/50 rounded p-3 text-sm text-gray-300 font-mono">
            {node.content_preview}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        <button className="flex-1 px-3 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded text-sm transition-colors">
          Expand Crystal
        </button>
        <button className="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm transition-colors">
          Surface
        </button>
      </div>
    </div>
  );
}

// =============================================================================
// Main BrainTopology Component
// =============================================================================

export function BrainTopology({
  topology,
  onNodeClick,
  selectedNodeId = null,
  showEdges = true,
  showGaps = true,
  showLabels = true,
}: BrainTopologyProps) {
  const [selectedNode, setSelectedNode] = useState<TopologyNode | null>(null);

  // Get scene context for quality-appropriate lighting
  const { illuminationQuality, shadowsEnabled, isAutoDetectedQuality, overrideQuality } = useSceneContext();

  const handleNodeClick = useCallback(
    (node: TopologyNode) => {
      setSelectedNode(node);
      onNodeClick?.(node);
    },
    [onNodeClick]
  );

  const handleCloseSidebar = useCallback(() => {
    setSelectedNode(null);
  }, []);

  if (!topology || topology.nodes.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-900 rounded-lg">
        <div className="text-center text-gray-500">
          <div className="text-4xl mb-2">🧠</div>
          <p>No crystals yet</p>
          <p className="text-sm">Capture some knowledge to see your topology</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full bg-gray-900 rounded-lg overflow-hidden">
      {/* 3D Canvas with quality-appropriate shadows */}
      <Canvas
        camera={{ position: [0, 0, 15], fov: 60 }}
        gl={{ antialias: true, alpha: false }}
        shadows={shadowsEnabled ? 'soft' : false}
        style={{ background: '#111827' }}
      >
        <Scene
          topology={topology}
          onNodeClick={handleNodeClick}
          selectedNodeId={selectedNode?.id ?? selectedNodeId}
          showEdges={showEdges}
          showGaps={showGaps}
          showLabels={showLabels}
          illuminationQuality={illuminationQuality}
        />
      </Canvas>

      {/* Stats overlay */}
      <div className="absolute top-3 left-3 bg-gray-800/80 rounded px-3 py-2 text-xs text-gray-300">
        <span className="text-cyan-400">{topology.stats.concept_count}</span> crystals
        {' • '}
        <span className="text-purple-400">{topology.stats.edge_count}</span> connections
        {topology.stats.hub_count > 0 && (
          <>
            {' • '}
            <span className="text-orange-400">{topology.stats.hub_count}</span> hubs
          </>
        )}
        {topology.stats.gap_count > 0 && (
          <>
            {' • '}
            <span className="text-red-400">{topology.stats.gap_count}</span> gaps
          </>
        )}
      </div>

      {/* Legend */}
      <div className="absolute bottom-3 left-3 bg-gray-800/80 rounded px-3 py-2 text-xs text-gray-300 flex gap-4">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-cyan-400" />
          <span>Fresh</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-purple-400" />
          <span>Fading</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-gray-400" />
          <span>Ghost</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-orange-400" />
          <span>Hub</span>
        </div>
      </div>

      {/* Controls hint + Quality selector */}
      <div className="absolute bottom-3 right-3 flex items-center gap-3">
        <div className="bg-gray-800/80 rounded px-3 py-2 text-xs text-gray-500">
          Drag to rotate • Scroll to zoom • Click crystal for details
        </div>
        <QualitySelector
          currentQuality={illuminationQuality}
          isAutoDetected={isAutoDetectedQuality}
          onQualityChange={overrideQuality}
          compact
          className="bg-gray-800/80"
        />
      </div>

      {/* Crystal sidebar */}
      <CrystalSidebar node={selectedNode} onClose={handleCloseSidebar} />
    </div>
  );
}

export default BrainTopology;
