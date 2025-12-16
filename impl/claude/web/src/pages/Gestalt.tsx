/**
 * Gestalt - Living Architecture Visualizer
 *
 * Spike 6A Elastic Edition: Responsive, screen-adaptive layout.
 *
 * Features:
 * - ElasticSplit for responsive canvas/panel layout
 * - Collapsible panels on mobile (drawer pattern)
 * - Density-aware controls (compact/comfortable/spacious)
 * - Semantic zoom based on screen size
 * - Touch-friendly mobile interactions
 *
 * Layout Modes:
 * - Desktop (>1024px): Canvas | Controls | Details (when selected)
 * - Tablet (768-1024px): Canvas | Controls/Details toggle
 * - Mobile (<768px): Full canvas + floating action buttons + drawer panels
 *
 * @see plans/web-refactor/elastic-primitives.md
 * @see plans/core-apps/gestalt-architecture-visualizer.md
 */

import { useRef, useState, useMemo, useCallback, useEffect, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';
import * as THREE from 'three';
import { gestaltApi } from '../api/client';
import type {
  CodebaseModule,
  CodebaseTopologyResponse,
  CodebaseModuleResponse,
} from '../api/types';
import { HEALTH_GRADE_CONFIG } from '../api/types';
import { ErrorBoundary } from '../components/error/ErrorBoundary';
import { ElasticSplit } from '../components/elastic/ElasticSplit';
import { BottomDrawer } from '../components/elastic/BottomDrawer';
import { FloatingActions, type FloatingAction } from '../components/elastic/FloatingActions';
import { useWindowLayout } from '../hooks/useLayoutContext';
import { SceneLighting, ShadowPlane } from '../components/three/SceneLighting';
import { SceneEffects } from '../components/three/SceneEffects';
import { QualitySelector } from '../components/three/QualitySelector';
import { calculateCenteredShadowBounds } from '../utils/three/calculateShadowBounds';
import { useIlluminationQuality } from '../hooks/useIlluminationQuality';
import type { IlluminationQuality } from '../constants/lighting';
import {
  FilterPanel,
  Legend,
  NodeTooltip,
  SmartEdge,
  type FilterState,
  HEALTH_GRADES,
  DEFAULT_FILTER_STATE,
  TOOLTIP_DELAY_MS,
} from '../components/gestalt';
import {
  PersonalityLoading,
  Breathe,
  celebrateEpic,
} from '../components/joy';
import { useObserverState } from '../components/path';

// =============================================================================
// Constants - Responsive scaling
// =============================================================================

/** Base node size - scales with density */
const NODE_BASE_SIZE = {
  compact: 0.2,
  comfortable: 0.25,
  spacious: 0.3,
} as const;

/** Label font size - scales with density */
const LABEL_FONT_SIZE = {
  compact: 0.14,
  comfortable: 0.18,
  spacious: 0.22,
} as const;

/** Maximum labels - fewer on mobile for performance */
const MAX_VISIBLE_LABELS = {
  compact: 15,
  comfortable: 30,
  spacious: 50,
} as const;

/** Panel collapse breakpoint */
const PANEL_COLLAPSE_BREAKPOINT = 768;

// =============================================================================
// Types
// =============================================================================

import type { Density } from '../components/gestalt';

interface ModuleNodeProps {
  node: CodebaseModule;
  isSelected: boolean;
  onClick: () => void;
  showLabel: boolean;
  density: Density;
  /** Whether to show tooltip on hover */
  enableTooltip?: boolean;
}

interface PanelState {
  controls: boolean;
  details: boolean;
}

// =============================================================================
// Color Utilities
// =============================================================================

function getHealthColor(grade: string): THREE.Color {
  const config = HEALTH_GRADE_CONFIG[grade] || HEALTH_GRADE_CONFIG['?'];
  return new THREE.Color(config.color);
}

function getNodeSize(linesOfCode: number, healthScore: number, density: Density): number {
  const baseSize = NODE_BASE_SIZE[density];
  const locBonus = Math.min(Math.log10(linesOfCode + 1) * 0.08, 0.2);
  const healthFactor = 0.6 + healthScore * 0.4;
  return (baseSize + locBonus) * healthFactor;
}

// =============================================================================
// Module Node Component
// =============================================================================

function ModuleNode({ node, isSelected, onClick, showLabel, density, enableTooltip = true }: ModuleNodeProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Handle tooltip delay
  useEffect(() => {
    if (hovered && enableTooltip && !isSelected) {
      // Start tooltip delay
      hoverTimeoutRef.current = setTimeout(() => {
        setShowTooltip(true);
      }, TOOLTIP_DELAY_MS);
    } else {
      // Clear timeout and hide tooltip
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
        hoverTimeoutRef.current = null;
      }
      setShowTooltip(false);
    }

    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
    };
  }, [hovered, enableTooltip, isSelected]);

  useFrame(() => {
    if (meshRef.current) {
      const targetScale = hovered || isSelected ? 1.5 : 1.0;
      meshRef.current.scale.lerp(
        new THREE.Vector3(targetScale, targetScale, targetScale),
        0.12
      );
    }
  });

  const color = useMemo(() => getHealthColor(node.health_grade), [node.health_grade]);
  const size = useMemo(
    () => getNodeSize(node.lines_of_code, node.health_score, density),
    [node.lines_of_code, node.health_score, density]
  );
  const opacity = useMemo(() => 0.6 + node.health_score * 0.4, [node.health_score]);

  return (
    <group position={[node.x, node.y, node.z]}>
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
        <sphereGeometry args={[size, 24, 24]} />
        <meshStandardMaterial
          color={color}
          transparent
          opacity={opacity}
          // Emissive for bloom: selected glows bright, hovered glows subtle
          // Intensities increased to trigger bloom at high/cinematic quality
          emissive={isSelected ? color : hovered ? color : undefined}
          emissiveIntensity={isSelected ? 2.0 : hovered ? 0.6 : 0}
          roughness={0.5}
          metalness={0.2}
        />
      </mesh>

      {/* Selection ring - bright for bloom visibility */}
      {isSelected && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[size * 1.4, size * 1.8, 32]} />
          <meshBasicMaterial color="#ffffff" transparent opacity={0.75} side={THREE.DoubleSide} />
        </mesh>
      )}

      {/* Hover ring - subtle indication */}
      {hovered && !isSelected && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[size * 1.2, size * 1.4, 32]} />
          <meshBasicMaterial color="#ffffff" transparent opacity={0.4} side={THREE.DoubleSide} />
        </mesh>
      )}

      {showLabel && (
        <Text
          position={[0, size + 0.3, 0]}
          fontSize={LABEL_FONT_SIZE[density]}
          color="#ffffff"
          anchorX="center"
          anchorY="bottom"
          outlineWidth={0.02}
          outlineColor="#000000"
          outlineOpacity={0.8}
        >
          {node.label}
        </Text>
      )}

      {/* Hover Tooltip */}
      <NodeTooltip
        node={node}
        visible={showTooltip}
        density={density}
      />
    </group>
  );
}

// =============================================================================
// Layer Rings Component
// =============================================================================

function LayerRings({ layers, nodeMap }: { layers: string[]; nodeMap: Map<string, CodebaseModule> }) {
  const layerRings = useMemo(() => {
    return layers
      .map((layer, idx) => {
        const layerNodes = Array.from(nodeMap.values()).filter((n) => n.layer === layer);
        if (layerNodes.length === 0) return null;

        const avgX = layerNodes.reduce((sum, n) => sum + n.x, 0) / layerNodes.length;
        const avgY = layerNodes.reduce((sum, n) => sum + n.y, 0) / layerNodes.length;
        const avgZ = layerNodes.reduce((sum, n) => sum + n.z, 0) / layerNodes.length;

        const radius =
          Math.max(...layerNodes.map((n) => Math.sqrt(Math.pow(n.x - avgX, 2) + Math.pow(n.y - avgY, 2))), 2) + 1;

        const hue = (idx / Math.max(layers.length, 1)) * 0.4 + 0.1;
        const color = new THREE.Color().setHSL(hue, 0.6, 0.5);

        return { layer, center: [avgX, avgY, avgZ] as [number, number, number], radius, color };
      })
      .filter(Boolean);
  }, [layers, nodeMap]);

  return (
    <>
      {layerRings.map(
        (ring) =>
          ring && (
            <group key={ring.layer} position={ring.center}>
              <mesh rotation={[Math.PI / 2, 0, 0]}>
                <ringGeometry args={[ring.radius - 0.08, ring.radius + 0.08, 64]} />
                <meshBasicMaterial color={ring.color} transparent opacity={0.12} side={THREE.DoubleSide} />
              </mesh>
            </group>
          )
      )}
    </>
  );
}

// =============================================================================
// Scene Component
// =============================================================================

interface SceneProps {
  topology: CodebaseTopologyResponse;
  onNodeClick: (node: CodebaseModule) => void;
  selectedNodeId: string | null;
  showEdges: boolean;
  showViolations: boolean;
  showLabels: boolean;
  showAnimation: boolean;
  layerFilter: string | null;
  enabledGrades: Set<string>;
  density: Density;
  /** Illumination quality for canonical lighting */
  illuminationQuality: IlluminationQuality;
}

function Scene({
  topology,
  onNodeClick,
  selectedNodeId,
  showEdges,
  showViolations,
  showLabels,
  showAnimation,
  layerFilter,
  enabledGrades,
  density,
  illuminationQuality,
}: SceneProps) {
  // Apply all filters: layer + health grades
  const filteredNodes = useMemo(() => {
    let nodes = topology.nodes;

    // Layer filter
    if (layerFilter) {
      nodes = nodes.filter((n) => n.layer === layerFilter);
    }

    // Health grade filter
    if (enabledGrades.size < HEALTH_GRADES.length) {
      nodes = nodes.filter((n) => enabledGrades.has(n.health_grade));
    }

    return nodes;
  }, [topology.nodes, layerFilter, enabledGrades]);

  const nodeMap = useMemo(() => new Map(filteredNodes.map((n) => [n.id, n])), [filteredNodes]);
  const filteredNodeIds = useMemo(() => new Set(filteredNodes.map((n) => n.id)), [filteredNodes]);

  const filteredLinks = useMemo(
    () =>
      topology.links.filter(
        (l) => filteredNodeIds.has(l.source) && filteredNodeIds.has(l.target) && (showViolations || !l.is_violation)
      ),
    [topology.links, filteredNodeIds, showViolations]
  );

  const labelledNodeIds = useMemo(() => {
    if (!showLabels) return new Set<string>();

    const ids = new Set<string>();
    if (selectedNodeId && filteredNodeIds.has(selectedNodeId)) {
      ids.add(selectedNodeId);
    }

    const maxLabels = MAX_VISIBLE_LABELS[density];
    const scored = filteredNodes
      .filter((n) => !ids.has(n.id))
      .map((n) => ({
        id: n.id,
        score: n.lines_of_code * 0.01 + n.health_score * 50 + (n.layer ? 20 : 0),
      }))
      .sort((a, b) => b.score - a.score);

    for (const { id } of scored.slice(0, maxLabels - ids.size)) {
      ids.add(id);
    }

    return ids;
  }, [showLabels, selectedNodeId, filteredNodes, filteredNodeIds, density]);

  // Calculate active edges (connected to selected node) for animation
  const activeEdgeIds = useMemo(() => {
    if (!selectedNodeId) return new Set<string>();
    return new Set(
      filteredLinks
        .filter((l) => l.source === selectedNodeId || l.target === selectedNodeId)
        .map((l) => `${l.source}->${l.target}`)
    );
  }, [selectedNodeId, filteredLinks]);

  // Calculate shadow bounds from filtered nodes
  const shadowBounds = useMemo(
    () => calculateCenteredShadowBounds(filteredNodes),
    [filteredNodes]
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
      <ShadowPlane y={-15} shadowOpacity={0.2} />

      <LayerRings layers={topology.layers} nodeMap={nodeMap} />

      {showEdges &&
        filteredLinks.map((link) => {
          const sourceNode = nodeMap.get(link.source);
          const targetNode = nodeMap.get(link.target);
          if (!sourceNode || !targetNode) return null;

          const edgeId = `${link.source}->${link.target}`;
          const isActive = activeEdgeIds.has(edgeId);

          return (
            <SmartEdge
              key={edgeId}
              source={[sourceNode.x, sourceNode.y, sourceNode.z]}
              target={[targetNode.x, targetNode.y, targetNode.z]}
              isViolation={link.is_violation}
              animationEnabled={showAnimation}
              isActive={isActive}
              isHighlighted={isActive}
              isDimmed={selectedNodeId !== null && !isActive}
            />
          );
        })}

      {filteredNodes.map((node) => (
        <ModuleNode
          key={node.id}
          node={node}
          isSelected={node.id === selectedNodeId}
          onClick={() => onNodeClick(node)}
          showLabel={labelledNodeIds.has(node.id)}
          density={density}
        />
      ))}

      <OrbitControls
        enablePan
        enableZoom
        enableRotate
        minDistance={5}
        maxDistance={60}
        zoomSpeed={0.8}
        rotateSpeed={0.5}
        panSpeed={0.8}
        touches={{
          ONE: THREE.TOUCH.ROTATE,
          TWO: THREE.TOUCH.DOLLY_PAN,
        }}
      />
    </>
  );
}

// =============================================================================
// Module Detail Panel - Responsive
// =============================================================================

interface ModuleDetailPanelProps {
  module: CodebaseModule;
  moduleDetails: CodebaseModuleResponse | null;
  onClose: () => void;
  loading: boolean;
  density: Density;
  isDrawer?: boolean;
}

function ModuleDetailPanel({ module, moduleDetails, onClose, loading, density, isDrawer }: ModuleDetailPanelProps) {
  const gradeConfig = HEALTH_GRADE_CONFIG[module.health_grade] || HEALTH_GRADE_CONFIG['?'];
  const isCompact = density === 'compact';

  return (
    <div
      className={`
        bg-gray-800 flex flex-col overflow-hidden
        ${isDrawer ? 'h-full rounded-t-xl' : 'border-l border-gray-700'}
      `}
      style={{ minWidth: isDrawer ? 'auto' : isCompact ? 240 : 280 }}
    >
      {/* Header */}
      <div className={`${isCompact ? 'p-3' : 'p-4'} border-b border-gray-700 bg-gray-800`}>
        <div className="flex justify-between items-start gap-2">
          <div className="flex-1 min-w-0">
            <h3 className={`font-semibold text-white truncate ${isCompact ? 'text-base' : 'text-lg'}`}>
              {module.label}
            </h3>
            <p className="text-xs text-gray-400 font-mono truncate" title={module.id}>
              {module.id}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl p-1 -mr-1 -mt-1 rounded hover:bg-gray-700 transition-colors flex-shrink-0"
            aria-label="Close panel"
          >
            ×
          </button>
        </div>

        <div className="flex flex-wrap gap-2 mt-2">
          <span
            className={`${isCompact ? 'px-1.5 py-0.5 text-xs' : 'px-2 py-1 text-sm'} font-bold rounded`}
            style={{ backgroundColor: gradeConfig.color + '33', color: gradeConfig.color }}
          >
            {module.health_grade}
          </span>
          <span className={`${isCompact ? 'px-1.5 py-0.5 text-xs' : 'px-2 py-1 text-xs'} bg-gray-700 text-gray-300 rounded`}>
            {Math.round(module.health_score * 100)}%
          </span>
          {module.layer && (
            <span className={`${isCompact ? 'px-1.5 py-0.5 text-xs' : 'px-2 py-1 text-xs'} bg-indigo-900/50 text-indigo-300 rounded`}>
              {module.layer}
            </span>
          )}
        </div>
      </div>

      {/* Content */}
      <div className={`flex-1 overflow-y-auto ${isCompact ? 'p-3' : 'p-4'}`}>
        {/* Stats grid - adapts to density */}
        <div className={`grid ${isCompact ? 'grid-cols-4 gap-2' : 'grid-cols-2 gap-3'} mb-4`}>
          {[
            { label: 'Lines', value: module.lines_of_code.toLocaleString() },
            { label: 'Coupling', value: `${Math.round(module.coupling * 100)}%` },
            { label: 'Cohesion', value: `${Math.round(module.cohesion * 100)}%` },
            { label: 'Instability', value: module.instability !== null ? `${Math.round(module.instability * 100)}%` : 'N/A' },
          ].map((stat) => (
            <div key={stat.label} className={`bg-gray-700/50 rounded-lg ${isCompact ? 'p-2 text-center' : 'p-3'}`}>
              <p className={`text-gray-400 ${isCompact ? 'text-[10px]' : 'text-xs'} mb-0.5`}>{stat.label}</p>
              <p className={`font-semibold text-white ${isCompact ? 'text-sm' : 'text-xl'}`}>{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Health bar */}
        <div className="mb-4">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Health</span>
            <span style={{ color: gradeConfig.color }}>{Math.round(module.health_score * 100)}%</span>
          </div>
          <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full transition-all duration-300 rounded-full"
              style={{ width: `${module.health_score * 100}%`, backgroundColor: gradeConfig.color }}
            />
          </div>
        </div>

        {/* Details from API */}
        {loading ? (
          <div className="text-center py-6">
            <div className="animate-spin text-2xl mb-2">⚙️</div>
            <p className="text-gray-400 text-sm">Loading details...</p>
          </div>
        ) : moduleDetails ? (
          <>
            {moduleDetails.violations.length > 0 && (
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-red-400">⚠️</span>
                  <h4 className={`font-semibold text-red-400 ${isCompact ? 'text-xs' : 'text-sm'}`}>
                    Violations ({moduleDetails.violations.length})
                  </h4>
                </div>
                <div className="bg-red-900/20 border border-red-800/50 rounded-lg p-2 space-y-1">
                  {moduleDetails.violations.slice(0, isCompact ? 3 : 5).map((v, i) => (
                    <div key={i} className={`${isCompact ? 'text-xs' : 'text-sm'}`}>
                      <div className="text-red-300 font-medium">{v.rule}</div>
                      <div className="text-red-400/80 text-xs font-mono truncate">→ {v.target}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {moduleDetails.dependencies.length > 0 && (
              <div className="mb-4">
                <h4 className={`font-semibold text-gray-400 mb-2 ${isCompact ? 'text-xs' : 'text-sm'}`}>
                  Dependencies ({moduleDetails.dependencies.length})
                </h4>
                <div className="max-h-24 overflow-y-auto bg-gray-900/50 rounded-lg p-2 text-xs font-mono text-gray-300 space-y-0.5">
                  {moduleDetails.dependencies.slice(0, isCompact ? 8 : 12).map((dep) => (
                    <div key={dep} className="truncate hover:text-white transition-colors">
                      → {dep}
                    </div>
                  ))}
                  {moduleDetails.dependencies.length > (isCompact ? 8 : 12) && (
                    <div className="text-gray-500">+{moduleDetails.dependencies.length - (isCompact ? 8 : 12)} more</div>
                  )}
                </div>
              </div>
            )}
          </>
        ) : null}
      </div>
    </div>
  );
}

// =============================================================================
// Loading & Error States
// =============================================================================

/**
 * Contextual loading state with personality.
 * Foundation 5: Personality & Joy
 */
function TopologyLoading() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900">
      <PersonalityLoading jewel="gestalt" size="lg" />
    </div>
  );
}

function TopologyErrorFallback({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900 p-8">
      <div className="text-5xl mb-4">⚠️</div>
      <h3 className="text-lg font-semibold text-gray-300 mb-2">3D Rendering Failed</h3>
      <p className="text-gray-500 text-sm text-center mb-4 max-w-md">
        The graph couldn't be rendered. This may happen without WebGL support.
      </p>
      <button onClick={onRetry} className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium transition-colors">
        Try Again
      </button>
    </div>
  );
}

// =============================================================================
// Main Gestalt Component - Elastic Edition
// =============================================================================

export default function Gestalt() {
  const { width, density, isMobile, isTablet, isDesktop } = useWindowLayout();

  // Get illumination quality for canonical lighting
  const { quality: illuminationQuality, isAutoDetected, override: overrideQuality } = useIlluminationQuality();
  const shadowsEnabled = illuminationQuality !== 'minimal';

  // Data state
  const [topology, setTopology] = useState<CodebaseTopologyResponse | null>(null);
  const [selectedModule, setSelectedModule] = useState<CodebaseModule | null>(null);
  const [moduleDetails, setModuleDetails] = useState<CodebaseModuleResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [topologyKey, setTopologyKey] = useState(0);

  // Filter state (unified for Chunk 1 visual showcase)
  const [filters, setFilters] = useState<FilterState>(() => ({
    ...DEFAULT_FILTER_STATE,
    showLabels: !isMobile, // Off by default on mobile
    maxNodes: isMobile ? 100 : isTablet ? 125 : 150,
  }));

  // Convenience handler for partial updates
  const handleFiltersChange = useCallback((updates: Partial<FilterState>) => {
    setFilters((prev) => ({ ...prev, ...updates }));
  }, []);

  // Panel state (mobile drawers)
  const [panelState, setPanelState] = useState<PanelState>({
    controls: false,
    details: false,
  });

  // Observer state (Wave 0 Foundation 2)
  const [observer, setObserver] = useObserverState('gestalt', 'architect');

  // Load topology
  useEffect(() => {
    loadTopology();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.maxNodes]);

  const loadTopology = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await gestaltApi.getTopology(filters.maxNodes, 0.0);
      setTopology(response.data);

      // Foundation 5: Celebrate A+ health grade!
      if (response.data.stats.overall_grade === 'A+') {
        celebrateEpic();
      }
    } catch (err) {
      console.error('Failed to load topology:', err);
      setError('Failed to load architecture. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = useCallback(async (node: CodebaseModule) => {
    setSelectedModule(node);
    setModuleDetails(null);
    setDetailsLoading(true);

    // On mobile, auto-open details drawer
    if (width < PANEL_COLLAPSE_BREAKPOINT) {
      setPanelState((s) => ({ ...s, details: true }));
    }

    try {
      const response = await gestaltApi.getModule(node.id);
      setModuleDetails(response.data);
    } catch (err) {
      console.error('Failed to load module details:', err);
    } finally {
      setDetailsLoading(false);
    }
  }, [width]);

  const handleCloseSidebar = useCallback(() => {
    setSelectedModule(null);
    setModuleDetails(null);
    setPanelState((s) => ({ ...s, details: false }));
  }, []);

  const handleRetry = useCallback(() => {
    setTopologyKey((k) => k + 1);
    loadTopology();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleScan = async () => {
    setLoading(true);
    try {
      await gestaltApi.scan('python');
      await loadTopology();
    } catch (err) {
      console.error('Failed to scan:', err);
      setError('Failed to scan codebase');
    } finally {
      setLoading(false);
    }
  };

  // ==========================================================================
  // Render: 3D Canvas
  // ==========================================================================

  const canvas3D = topology && (
    <ErrorBoundary key={topologyKey} fallback={<TopologyErrorFallback onRetry={handleRetry} />} resetKeys={[topologyKey]}>
      <Suspense fallback={<TopologyLoading />}>
        <Canvas
          camera={{ position: [0, 0, isMobile ? 30 : 25], fov: 55 }}
          gl={{ antialias: true, alpha: false }}
          shadows={shadowsEnabled ? 'soft' : false}
          style={{ background: '#111827' }}
        >
          <Scene
            topology={topology}
            onNodeClick={handleNodeClick}
            selectedNodeId={selectedModule?.id ?? null}
            showEdges={filters.showEdges}
            showViolations={filters.showViolations}
            showLabels={filters.showLabels}
            showAnimation={filters.showAnimation}
            layerFilter={filters.layerFilter}
            enabledGrades={filters.enabledGrades}
            density={density}
            illuminationQuality={illuminationQuality}
          />
        </Canvas>
      </Suspense>
    </ErrorBoundary>
  );

  // ==========================================================================
  // Render: Overlays
  // ==========================================================================

  const statsOverlay = topology && (
    <div className={`absolute top-3 left-3 bg-gray-800/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow-lg ${isMobile ? 'text-[10px]' : 'text-xs'} text-gray-300`}>
      <span className="text-green-400 font-semibold">{topology.stats.node_count}</span> modules
      {!isMobile && (
        <>
          {' • '}
          <span className="text-blue-400 font-semibold">{topology.stats.link_count}</span> edges
        </>
      )}
      {topology.stats.violation_count > 0 && (
        <>
          {' • '}
          <span className="text-red-400 font-semibold">{topology.stats.violation_count}</span>
          {!isMobile && ' violations'}
        </>
      )}
    </div>
  );

  const hintsOverlay = !isMobile && (
    <div className="absolute bottom-3 left-3 flex items-center gap-3">
      <div className="bg-gray-800/90 backdrop-blur-sm rounded-lg px-3 py-2 text-xs text-gray-500 shadow-lg">
        Drag to rotate • Scroll to zoom • Click module for details
      </div>
      <QualitySelector
        currentQuality={illuminationQuality}
        isAutoDetected={isAutoDetected}
        onQualityChange={overrideQuality}
        compact
        className="backdrop-blur-sm shadow-lg"
      />
    </div>
  );

  // Legend overlay (top-right, collapses on mobile)
  const legendOverlay = !isMobile && (
    <Legend
      position="top-right"
      density={density}
      defaultCollapsed={isTablet}
    />
  );

  // ==========================================================================
  // Render: Mobile Layout
  // ==========================================================================

  if (isMobile) {
    return (
      <div className="h-screen flex flex-col bg-gray-900 text-white overflow-hidden">
        {/* Compact header */}
        <header className="flex-shrink-0 border-b border-gray-800 px-3 py-2 bg-gray-900 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">🏗️</span>
            <span className="font-semibold">Gestalt</span>
            {topology && (
              /* Foundation 5: Breathe animation for healthy grades */
              <Breathe intensity={topology.stats.overall_grade === 'A+' || topology.stats.overall_grade === 'A' ? 0.3 : 0}>
                <span
                  className="text-xs font-bold px-1.5 py-0.5 rounded"
                  style={{
                    backgroundColor: HEALTH_GRADE_CONFIG[topology.stats.overall_grade]?.color + '33',
                    color: HEALTH_GRADE_CONFIG[topology.stats.overall_grade]?.color,
                  }}
                >
                  {topology.stats.overall_grade}
                </span>
              </Breathe>
            )}
          </div>
        </header>

        {/* Main content */}
        <div className="flex-1 relative">
          {error ? (
            <div className="h-full flex items-center justify-center p-4">
              <div className="text-center">
                <div className="text-4xl mb-3">⚠️</div>
                <p className="text-gray-400 text-sm mb-4">{error}</p>
                <button onClick={handleRetry} className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm">
                  Retry
                </button>
              </div>
            </div>
          ) : loading && !topology ? (
            <TopologyLoading />
          ) : (
            <>
              {canvas3D}
              {statsOverlay}

              {/* Floating actions */}
              <FloatingActions
                actions={[
                  {
                    id: 'scan',
                    icon: '🔄',
                    label: 'Rescan',
                    onClick: handleScan,
                    variant: 'primary',
                    loading: loading,
                    disabled: loading,
                  },
                  {
                    id: 'controls',
                    icon: '⚙️',
                    label: 'Toggle controls',
                    onClick: () => setPanelState((s) => ({ ...s, controls: !s.controls })),
                    isActive: panelState.controls,
                  },
                  ...(selectedModule ? [{
                    id: 'details',
                    icon: '📋',
                    label: 'Toggle details',
                    onClick: () => setPanelState((s) => ({ ...s, details: !s.details })),
                    isActive: panelState.details,
                  } as FloatingAction] : []),
                ]}
                position="bottom-right"
              />
            </>
          )}
        </div>

        {/* Control drawer */}
        <BottomDrawer
          isOpen={panelState.controls}
          onClose={() => setPanelState((s) => ({ ...s, controls: false }))}
          title="Filters"
        >
          <FilterPanel
            topology={topology}
            filters={filters}
            onFiltersChange={handleFiltersChange}
            onModuleSelect={handleNodeClick}
            density={density}
            isDrawer
            observer={observer}
            onObserverChange={setObserver}
          />
        </BottomDrawer>

        {/* Details drawer */}
        <BottomDrawer
          isOpen={panelState.details && !!selectedModule}
          onClose={handleCloseSidebar}
          title="Module Details"
        >
          {selectedModule && (
            <ModuleDetailPanel
              module={selectedModule}
              moduleDetails={moduleDetails}
              onClose={handleCloseSidebar}
              loading={detailsLoading}
              density={density}
              isDrawer
            />
          )}
        </BottomDrawer>
      </div>
    );
  }

  // ==========================================================================
  // Render: Tablet/Desktop Layout (ElasticSplit)
  // ==========================================================================

  const controlPanel = (
    <FilterPanel
      topology={topology}
      filters={filters}
      onFiltersChange={handleFiltersChange}
      onModuleSelect={handleNodeClick}
      density={density}
      observer={observer}
      onObserverChange={setObserver}
    />
  );

  const detailPanel = selectedModule && (
    <ModuleDetailPanel
      module={selectedModule}
      moduleDetails={moduleDetails}
      onClose={handleCloseSidebar}
      loading={detailsLoading}
      density={density}
    />
  );

  // Build right panel content
  const rightPanelContent = (
    <div className="h-full flex">
      {controlPanel}
      {detailPanel}
    </div>
  );

  // Calculate split ratio based on whether details are open
  const splitRatio = selectedModule ? (isDesktop ? 0.65 : 0.55) : (isDesktop ? 0.82 : 0.72);

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-white overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-gray-800 px-4 py-3 bg-gray-900">
        <div className="flex justify-between items-center">
          <div>
            <h1 className={`font-bold flex items-center gap-2 ${isTablet ? 'text-lg' : 'text-xl'}`}>
              <span>🏗️</span>
              <span>Gestalt</span>
              {topology && (
                /* Foundation 5: Breathe animation for healthy grades */
                <Breathe intensity={topology.stats.overall_grade === 'A+' || topology.stats.overall_grade === 'A' ? 0.3 : 0}>
                  <span
                    className="text-sm font-normal px-2 py-0.5 rounded ml-2"
                    style={{
                      backgroundColor: HEALTH_GRADE_CONFIG[topology.stats.overall_grade]?.color + '33',
                      color: HEALTH_GRADE_CONFIG[topology.stats.overall_grade]?.color,
                    }}
                  >
                    {topology.stats.overall_grade}
                  </span>
                </Breathe>
              )}
            </h1>
            <p className={`text-gray-400 mt-0.5 ${isTablet ? 'text-xs' : 'text-sm'}`}>
              {topology ? (
                <>
                  {topology.stats.node_count} modules • {topology.stats.link_count} dependencies
                  {topology.stats.violation_count > 0 && (
                    <span className="text-red-400 ml-2">• {topology.stats.violation_count} violations</span>
                  )}
                </>
              ) : loading ? (
                'Scanning...'
              ) : (
                'Architecture Visualizer'
              )}
            </p>
          </div>
          <button
            onClick={handleScan}
            disabled={loading}
            className={`px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center gap-2 ${isTablet ? 'text-xs' : 'text-sm'}`}
          >
            {loading ? (
              <>
                <span className="animate-spin">⚙️</span>
                {isDesktop && 'Scanning...'}
              </>
            ) : (
              <>
                <span>🔄</span>
                {isDesktop && 'Rescan'}
              </>
            )}
          </button>
        </div>
      </header>

      {/* Main content with ElasticSplit */}
      {error ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-5xl mb-4">⚠️</div>
            <p className="text-gray-400 mb-4">{error}</p>
            <button onClick={handleRetry} className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg">
              Retry
            </button>
          </div>
        </div>
      ) : loading && !topology ? (
        <div className="flex-1">
          <TopologyLoading />
        </div>
      ) : (
        <div className="flex-1 overflow-hidden">
          <ElasticSplit
            direction="horizontal"
            defaultRatio={splitRatio}
            collapseAt={PANEL_COLLAPSE_BREAKPOINT}
            collapsePriority="secondary"
            minPaneSize={isTablet ? 200 : 300}
            resizable={isDesktop}
            primary={
              <div className="h-full relative">
                {canvas3D}
                {statsOverlay}
                {hintsOverlay}
                {legendOverlay}
              </div>
            }
            secondary={rightPanelContent}
          />
        </div>
      )}
    </div>
  );
}
