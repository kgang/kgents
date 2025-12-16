/**
 * BrainTopology - 3D Visualization of Holographic Memory
 *
 * Spike 3B: Cartography 3D Enhancement
 *
 * Features:
 * - Force-directed 3D graph using three.js/react-three-fiber
 * - Crystal nodes with decay-based opacity (fresh=bright, fading=ghost)
 * - Hub crystal highlighting (larger, glowing)
 * - Click-to-expand crystal sidebar
 * - Gap detection visualization (sparse regions highlighted)
 * - Mobile touch gestures for rotation/zoom
 */

import { useRef, useState, useMemo, useCallback } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Line } from '@react-three/drei';
import * as THREE from 'three';
import type {
  TopologyNode,
  TopologyEdge,
  TopologyGap,
  BrainTopologyResponse,
} from '../api/types';
import { SceneLighting, ShadowPlane } from './three/SceneLighting';
import { SceneEffects } from './three/SceneEffects';
import { QualitySelector } from './three/QualitySelector';
import { calculateCenteredShadowBounds } from '../utils/three/calculateShadowBounds';
import { useSceneContext } from '../hooks/useSceneContext';

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

interface CrystalNodeProps {
  node: TopologyNode;
  isHub: boolean;
  isSelected: boolean;
  onClick: () => void;
}

interface TopologyEdgeProps {
  edge: TopologyEdge;
  nodes: Map<string, TopologyNode>;
}

interface GapSphereProps {
  gap: TopologyGap;
}

// =============================================================================
// Color Utilities
// =============================================================================

/**
 * Get color based on resolution (decay state).
 * Fresh (1.0) = bright cyan/blue
 * Fading (0.5) = purple
 * Ghost (0.1) = dim gray
 */
function getNodeColor(resolution: number, isHot: boolean): THREE.Color {
  if (isHot) {
    // Hot nodes are orange/gold
    return new THREE.Color().setHSL(0.08, 0.9, 0.5 + resolution * 0.3);
  }
  // Normal nodes transition from cyan (fresh) to purple (fading) to gray (ghost)
  const hue = 0.55 - resolution * 0.15; // 0.55 (cyan) to 0.4 (blue-purple)
  const saturation = resolution * 0.8;
  const lightness = 0.3 + resolution * 0.4;
  return new THREE.Color().setHSL(hue, saturation, lightness);
}

/**
 * Get node size based on access count and hub status.
 */
function getNodeSize(accessCount: number, isHub: boolean, resolution: number): number {
  const baseSize = 0.15;
  const accessBonus = Math.min(accessCount * 0.02, 0.2);
  const hubBonus = isHub ? 0.15 : 0;
  const resolutionFactor = 0.5 + resolution * 0.5;
  return (baseSize + accessBonus + hubBonus) * resolutionFactor;
}

// =============================================================================
// Crystal Node Component
// =============================================================================

function CrystalNode({ node, isHub, isSelected, onClick }: CrystalNodeProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  // Animate on hover/select
  useFrame(() => {
    if (meshRef.current) {
      const targetScale = hovered || isSelected ? 1.3 : 1.0;
      meshRef.current.scale.lerp(
        new THREE.Vector3(targetScale, targetScale, targetScale),
        0.1
      );
    }
  });

  const color = useMemo(
    () => getNodeColor(node.resolution, node.is_hot),
    [node.resolution, node.is_hot]
  );

  const size = useMemo(
    () => getNodeSize(node.access_count, isHub, node.resolution),
    [node.access_count, isHub, node.resolution]
  );

  // Opacity based on resolution (decay visualization)
  const opacity = useMemo(() => {
    const minOpacity = 0.2;
    const maxOpacity = 1.0;
    return minOpacity + node.resolution * (maxOpacity - minOpacity);
  }, [node.resolution]);

  return (
    <group position={[node.x, node.y, node.z]}>
      {/* Main crystal sphere */}
      <mesh
        ref={meshRef}
        castShadow
        onClick={(e) => {
          e.stopPropagation();
          onClick();
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
          document.body.style.cursor = 'pointer';
        }}
        onPointerOut={() => {
          setHovered(false);
          document.body.style.cursor = 'auto';
        }}
      >
        <sphereGeometry args={[size, 16, 16]} />
        <meshStandardMaterial
          color={color}
          transparent
          opacity={opacity}
          // Emissive for bloom: hubs glow warmly, selected glows bright
          // Intensities increased to trigger bloom at high/cinematic quality
          emissive={isHub || isSelected || node.is_hot ? color : undefined}
          emissiveIntensity={
            isSelected ? 2.0 :    // Selected: bright glow
            isHub ? 1.5 :         // Hub: warm glow
            node.is_hot ? 1.2 :   // Hot: noticeable glow
            0
          }
        />
      </mesh>

      {/* Hub glow ring - increased opacity for bloom visibility */}
      {isHub && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[size * 1.2, size * 1.5, 32]} />
          <meshBasicMaterial color="#ffa500" transparent opacity={0.6} side={THREE.DoubleSide} />
        </mesh>
      )}

      {/* Selection ring - bright cyan for bloom halo */}
      {isSelected && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[size * 1.3, size * 1.6, 32]} />
          <meshBasicMaterial color="#00ffff" transparent opacity={0.7} side={THREE.DoubleSide} />
        </mesh>
      )}
    </group>
  );
}

// =============================================================================
// Edge Component
// =============================================================================

function TopologyEdgeComponent({ edge, nodes }: TopologyEdgeProps) {
  const sourceNode = nodes.get(edge.source);
  const targetNode = nodes.get(edge.target);

  if (!sourceNode || !targetNode) return null;

  const points = useMemo(
    () => [
      new THREE.Vector3(sourceNode.x, sourceNode.y, sourceNode.z),
      new THREE.Vector3(targetNode.x, targetNode.y, targetNode.z),
    ],
    [sourceNode, targetNode]
  );

  // Opacity based on similarity
  const opacity = edge.similarity * 0.5;

  return (
    <Line
      points={points}
      color="#4a5568"
      lineWidth={1}
      transparent
      opacity={opacity}
    />
  );
}

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
// Labels Component
// =============================================================================

function NodeLabels({ nodes, hubIds }: { nodes: TopologyNode[]; hubIds: string[] }) {
  // Note: camera from useThree() could be used for billboard text in future

  // Only show labels for hubs and high-resolution nodes
  const visibleNodes = useMemo(
    () =>
      nodes.filter(
        (n) => hubIds.includes(n.id) || n.resolution > 0.7 || n.access_count > 5
      ),
    [nodes, hubIds]
  );

  return (
    <>
      {visibleNodes.map((node) => (
        <Text
          key={`label-${node.id}`}
          position={[node.x, node.y + 0.4, node.z]}
          fontSize={0.15}
          color="#ffffff"
          anchorX="center"
          anchorY="bottom"
          outlineWidth={0.02}
          outlineColor="#000000"
        >
          {node.label}
        </Text>
      ))}
    </>
  );
}

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

  return (
    <>
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

      {/* Edges */}
      {showEdges &&
        topology.edges.map((edge, i) => (
          <TopologyEdgeComponent key={`edge-${i}`} edge={edge} nodes={nodeMap} />
        ))}

      {/* Gaps */}
      {showGaps &&
        topology.gaps.map((gap, i) => <GapSphereComponent key={`gap-${i}`} gap={gap} />)}

      {/* Nodes */}
      {topology.nodes.map((node) => (
        <CrystalNode
          key={node.id}
          node={node}
          isHub={hubSet.has(node.id)}
          isSelected={node.id === selectedNodeId}
          onClick={() => onNodeClick(node)}
        />
      ))}

      {/* Labels */}
      {showLabels && <NodeLabels nodes={topology.nodes} hubIds={topology.hub_ids} />}

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
