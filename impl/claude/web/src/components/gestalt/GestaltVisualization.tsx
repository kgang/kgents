/**
 * GestaltVisualization - Living Architecture Visualizer Core
 *
 * Extracted visualization component for projection-first architecture.
 * Receives data from PathProjection and handles all rendering logic.
 *
 * Features:
 * - 3D codebase topology visualization
 * - Density-adaptive layout (mobile/tablet/desktop)
 * - Organic forest theme with vine edges
 * - Health-based node coloring
 * - Interactive node selection with details panel
 *
 * @see spec/protocols/os-shell.md - Part IV: Gallery Primitive Reliance
 * @see docs/skills/crown-jewel-patterns.md
 */

import { useRef, useState, useMemo, useCallback, useEffect, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';
import * as THREE from 'three';
import type {
  CodebaseModule,
  CodebaseTopologyResponse,
  CodebaseModuleResponse,
} from '../../api/types';
import { HEALTH_GRADE_CONFIG } from '../../api/types';
import { gestaltApi } from '../../api/client';
import { ErrorBoundary } from '../error/ErrorBoundary';
import { ElasticSplit } from '../elastic/ElasticSplit';
import { BottomDrawer } from '../elastic/BottomDrawer';
import { FloatingActions, type FloatingAction } from '../elastic/FloatingActions';
import { SceneLighting, ShadowPlane } from '../three/SceneLighting';
import { SceneEffects } from '../three/SceneEffects';
import { QualitySelector } from '../three/QualitySelector';
import { calculateCenteredShadowBounds } from '../../utils/three/calculateShadowBounds';
import { useIlluminationQuality } from '../../hooks/useIlluminationQuality';
import type { IlluminationQuality } from '../../constants/lighting';
import {
  FilterPanel,
  Legend,
  NodeTooltip,
  SmartEdge,
  SmartVineEdge,
  OrganicNode,
  type FilterState,
  type Density,
  HEALTH_GRADES,
  DEFAULT_FILTER_STATE,
  TOOLTIP_DELAY_MS,
} from './index';
import {
  PersonalityLoading,
  EmpathyError,
  Breathe,
  celebrateEpic,
} from '../joy';
import { useObserverState } from '../path';
import { useSynergyToast } from '../synergy';
import { DARK_SURFACES, FOREST_SCENE } from '../../constants';
import { Network } from 'lucide-react';

// =============================================================================
// Constants - Responsive scaling
// =============================================================================

const NODE_BASE_SIZE = {
  compact: 0.2,
  comfortable: 0.25,
  spacious: 0.3,
} as const;

const LABEL_FONT_SIZE = {
  compact: 0.14,
  comfortable: 0.18,
  spacious: 0.22,
} as const;

const MAX_VISIBLE_LABELS = {
  compact: 15,
  comfortable: 30,
  spacious: 50,
} as const;

const PANEL_COLLAPSE_BREAKPOINT = 768;

// =============================================================================
// Types
// =============================================================================

export interface GestaltVisualizationProps {
  /** Topology data from AGENTESE path */
  data: CodebaseTopologyResponse;
  /** Current density from shell context */
  density: Density;
  /** Whether mobile layout */
  isMobile: boolean;
  /** Whether tablet layout */
  isTablet: boolean;
  /** Whether desktop layout */
  isDesktop: boolean;
  /** Viewport width */
  width: number;
  /** Callback when scan requested */
  onScan?: () => Promise<void>;
}

interface ModuleNodeProps {
  node: CodebaseModule;
  isSelected: boolean;
  onClick: () => void;
  showLabel: boolean;
  density: Density;
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

  useEffect(() => {
    if (hovered && enableTooltip && !isSelected) {
      hoverTimeoutRef.current = setTimeout(() => {
        setShowTooltip(true);
      }, TOOLTIP_DELAY_MS);
    } else {
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
          emissive={isSelected ? color : hovered ? color : undefined}
          emissiveIntensity={isSelected ? 2.0 : hovered ? 0.6 : 0}
          roughness={0.5}
          metalness={0.2}
        />
      </mesh>

      {isSelected && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[size * 1.4, size * 1.8, 32]} />
          <meshBasicMaterial color="#ffffff" transparent opacity={0.75} side={THREE.DoubleSide} />
        </mesh>
      )}

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

      <NodeTooltip node={node} visible={showTooltip} density={density} />
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
  illuminationQuality: IlluminationQuality;
  organicTheme: boolean;
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
  organicTheme,
}: SceneProps) {
  const filteredNodes = useMemo(() => {
    let nodes = topology.nodes;

    if (layerFilter) {
      nodes = nodes.filter((n) => n.layer === layerFilter);
    }

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

  const activeEdgeIds = useMemo(() => {
    if (!selectedNodeId) return new Set<string>();
    return new Set(
      filteredLinks
        .filter((l) => l.source === selectedNodeId || l.target === selectedNodeId)
        .map((l) => `${l.source}->${l.target}`)
    );
  }, [selectedNodeId, filteredLinks]);

  const shadowBounds = useMemo(
    () => calculateCenteredShadowBounds(filteredNodes),
    [filteredNodes]
  );

  return (
    <>
      {organicTheme && (
        <fog attach="fog" args={[FOREST_SCENE.fogColor, FOREST_SCENE.fogNear, FOREST_SCENE.fogFar]} />
      )}

      <SceneLighting
        quality={illuminationQuality}
        bounds={shadowBounds}
        atmosphericFill
        animateFillLights={organicTheme}
        sunColor={organicTheme ? FOREST_SCENE.sunColor : undefined}
        ambientColor={organicTheme ? FOREST_SCENE.ambientLight : undefined}
      />

      <SceneEffects quality={illuminationQuality} />

      <ShadowPlane y={-15} shadowOpacity={0.2} />

      <LayerRings layers={topology.layers} nodeMap={nodeMap} />

      {showEdges &&
        filteredLinks.map((link) => {
          const sourceNode = nodeMap.get(link.source);
          const targetNode = nodeMap.get(link.target);
          if (!sourceNode || !targetNode) return null;

          const edgeId = `${link.source}->${link.target}`;
          const isActive = activeEdgeIds.has(edgeId);

          if (organicTheme) {
            return (
              <SmartVineEdge
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
          }

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
        organicTheme ? (
          <OrganicNode
            key={node.id}
            node={node}
            isSelected={node.id === selectedNodeId}
            onClick={() => onNodeClick(node)}
            showLabel={labelledNodeIds.has(node.id)}
            density={density}
          />
        ) : (
          <ModuleNode
            key={node.id}
            node={node}
            isSelected={node.id === selectedNodeId}
            onClick={() => onNodeClick(node)}
            showLabel={labelledNodeIds.has(node.id)}
            density={density}
          />
        )
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

      <div className={`flex-1 overflow-y-auto ${isCompact ? 'p-3' : 'p-4'}`}>
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

        {loading ? (
          <div className="text-center py-6">
            <Network className="w-6 h-6 mx-auto mb-2 animate-pulse text-green-400" />
            <p className="text-gray-400 text-sm">Loading details...</p>
          </div>
        ) : moduleDetails ? (
          <>
            {moduleDetails.violations.length > 0 && (
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-red-400 text-sm">Warning</span>
                  <h4 className={`font-semibold text-red-400 ${isCompact ? 'text-xs' : 'text-sm'}`}>
                    Violations ({moduleDetails.violations.length})
                  </h4>
                </div>
                <div className="bg-red-900/20 border border-red-800/50 rounded-lg p-2 space-y-1">
                  {moduleDetails.violations.slice(0, isCompact ? 3 : 5).map((v, i) => (
                    <div key={i} className={`${isCompact ? 'text-xs' : 'text-sm'}`}>
                      <div className="text-red-300 font-medium">{v.rule}</div>
                      <div className="text-red-400/80 text-xs font-mono truncate">{v.target}</div>
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
                      {dep}
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

function TopologyLoading({ organic = false }: { organic?: boolean }) {
  return (
    <div
      className="w-full h-full flex flex-col items-center justify-center"
      style={{ background: organic ? FOREST_SCENE.background : DARK_SURFACES.canvas }}
    >
      <PersonalityLoading jewel="gestalt" size="lg" organic={organic} />
    </div>
  );
}

function TopologyErrorFallback({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900 p-8">
      <EmpathyError
        type="unknown"
        title="3D Rendering Failed"
        subtitle="The graph couldn't be rendered. This may happen without WebGL support."
        action="Try Again"
        onAction={onRetry}
        size="md"
      />
    </div>
  );
}

// =============================================================================
// Main Visualization Component
// =============================================================================

export function GestaltVisualization({
  data: topology,
  density,
  isMobile,
  isTablet,
  isDesktop,
  width,
  onScan,
}: GestaltVisualizationProps) {
  // Illumination quality
  const { quality: illuminationQuality, isAutoDetected, override: overrideQuality } = useIlluminationQuality();
  const shadowsEnabled = illuminationQuality !== 'minimal';

  // Selection state
  const [selectedModule, setSelectedModule] = useState<CodebaseModule | null>(null);
  const [moduleDetails, setModuleDetails] = useState<CodebaseModuleResponse | null>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [topologyKey, setTopologyKey] = useState(0);

  // Filter state
  const [filters, setFilters] = useState<FilterState>(() => ({
    ...DEFAULT_FILTER_STATE,
    showLabels: !isMobile,
    maxNodes: isMobile ? 100 : isTablet ? 125 : 150,
  }));

  const handleFiltersChange = useCallback((updates: Partial<FilterState>) => {
    setFilters((prev) => ({ ...prev, ...updates }));
  }, []);

  // Panel state (mobile drawers)
  const [panelState, setPanelState] = useState<PanelState>({
    controls: false,
    details: false,
  });

  // Observer state
  const [observer, setObserver] = useObserverState('gestalt', 'architect');

  // Synergy toast
  const { gestaltToBrain, driftDetected } = useSynergyToast();

  // Celebrate A+ health
  useEffect(() => {
    if (topology?.stats.overall_grade === 'A+') {
      celebrateEpic();
    }
  }, [topology?.stats.overall_grade]);

  const handleNodeClick = useCallback(async (node: CodebaseModule) => {
    setSelectedModule(node);
    setModuleDetails(null);
    setDetailsLoading(true);

    if (width < PANEL_COLLAPSE_BREAKPOINT) {
      setPanelState((s) => ({ ...s, details: true }));
    }

    try {
      const moduleDetails = await gestaltApi.getModule(node.id);
      setModuleDetails(moduleDetails);
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
  }, []);

  const handleScan = async () => {
    if (!onScan) return;
    setLoading(true);
    try {
      await onScan();
      // Show synergy toasts
      if (topology) {
        gestaltToBrain('impl/claude/', topology.stats.overall_grade);
        if (topology.stats.violation_count > 0) {
          driftDetected('impl/claude/', topology.stats.violation_count);
        }
      }
    } catch (err) {
      console.error('Failed to scan:', err);
    } finally {
      setLoading(false);
    }
  };

  // ==========================================================================
  // 3D Canvas
  // ==========================================================================

  const canvas3D = topology && (
    <ErrorBoundary key={topologyKey} fallback={<TopologyErrorFallback onRetry={handleRetry} />} resetKeys={[topologyKey]}>
      <Suspense fallback={<TopologyLoading organic={filters.organicTheme} />}>
        <Canvas
          camera={{ position: [0, 0, isMobile ? 30 : 25], fov: 55 }}
          gl={{ antialias: true, alpha: false }}
          shadows={shadowsEnabled ? 'soft' : false}
          style={{ background: filters.organicTheme ? FOREST_SCENE.background : DARK_SURFACES.canvas }}
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
            organicTheme={filters.organicTheme}
          />
        </Canvas>
      </Suspense>
    </ErrorBoundary>
  );

  // ==========================================================================
  // Overlays
  // ==========================================================================

  const statsOverlay = topology && (
    <div className={`absolute top-3 left-3 bg-gray-800/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow-lg ${isMobile ? 'text-[10px]' : 'text-xs'} text-gray-300`}>
      <span className="text-green-400 font-semibold">{topology.stats.node_count}</span> modules
      {!isMobile && (
        <>
          {' | '}
          <span className="text-blue-400 font-semibold">{topology.stats.link_count}</span> edges
        </>
      )}
      {topology.stats.violation_count > 0 && (
        <>
          {' | '}
          <span className="text-red-400 font-semibold">{topology.stats.violation_count}</span>
          {!isMobile && ' violations'}
        </>
      )}
    </div>
  );

  const hintsOverlay = !isMobile && (
    <div className="absolute bottom-3 left-3 flex items-center gap-3">
      <div className="bg-gray-800/90 backdrop-blur-sm rounded-lg px-3 py-2 text-xs text-gray-500 shadow-lg">
        Drag to rotate | Scroll to zoom | Click module for details
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

  const legendOverlay = !isMobile && (
    <Legend
      position="top-right"
      density={density}
      defaultCollapsed={isTablet}
    />
  );

  // ==========================================================================
  // Mobile Layout
  // ==========================================================================

  if (isMobile) {
    return (
      <div className="h-full flex flex-col bg-gray-900 text-white overflow-hidden">
        <header className="flex-shrink-0 border-b border-gray-800 px-3 py-2 bg-gray-900 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Network className="w-5 h-5 text-green-400" />
            <span className="font-semibold">Gestalt</span>
            {topology && (
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

        <div className="flex-1 relative">
          {canvas3D}
          {statsOverlay}

          <FloatingActions
            actions={[
              ...(onScan ? [{
                id: 'scan',
                icon: <Network className="w-4 h-4" />,
                label: 'Rescan',
                onClick: handleScan,
                variant: 'primary' as const,
                loading: loading,
                disabled: loading,
              }] : []),
              {
                id: 'controls',
                icon: <Network className="w-4 h-4" />,
                label: 'Toggle controls',
                onClick: () => setPanelState((s) => ({ ...s, controls: !s.controls })),
                isActive: panelState.controls,
              },
              ...(selectedModule ? [{
                id: 'details',
                icon: <Network className="w-4 h-4" />,
                label: 'Toggle details',
                onClick: () => setPanelState((s) => ({ ...s, details: !s.details })),
                isActive: panelState.details,
              } as FloatingAction] : []),
            ]}
            position="bottom-right"
          />
        </div>

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
  // Tablet/Desktop Layout
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

  const rightPanelContent = (
    <div className="h-full flex">
      {controlPanel}
      {detailPanel}
    </div>
  );

  const splitRatio = selectedModule ? (isDesktop ? 0.65 : 0.55) : (isDesktop ? 0.82 : 0.72);

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white overflow-hidden">
      <header className="flex-shrink-0 border-b border-gray-800 px-4 py-3 bg-gray-900">
        <div className="flex justify-between items-center">
          <div>
            <h1 className={`font-bold flex items-center gap-2 ${isTablet ? 'text-lg' : 'text-xl'}`}>
              <Network className="w-6 h-6 text-green-400" />
              <span>Gestalt</span>
              {topology && (
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
              {topology.stats.node_count} modules | {topology.stats.link_count} dependencies
              {topology.stats.violation_count > 0 && (
                <span className="text-red-400 ml-2">| {topology.stats.violation_count} violations</span>
              )}
            </p>
          </div>
          {onScan && (
            <button
              onClick={handleScan}
              disabled={loading}
              className={`px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center gap-2 ${isTablet ? 'text-xs' : 'text-sm'}`}
            >
              {loading ? (
                <>
                  <Network className="w-4 h-4 animate-spin" />
                  {isDesktop && 'Scanning...'}
                </>
              ) : (
                <>
                  <Network className="w-4 h-4" />
                  {isDesktop && 'Rescan'}
                </>
              )}
            </button>
          )}
        </div>
      </header>

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
    </div>
  );
}

export default GestaltVisualization;
