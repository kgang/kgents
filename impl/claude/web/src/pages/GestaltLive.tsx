/**
 * GestaltLive - Live Infrastructure Visualizer
 *
 * Real-time 3D visualization of Kubernetes pods, services, and deployments.
 *
 * Elastic Edition: Uses Layout Projection Functor and Illumination System.
 *
 * Features:
 * - 3D force-directed graph of infrastructure entities
 * - Real-time updates via SSE
 * - Entity shapes by kind (sphere=pod, octahedron=service, etc.)
 * - Health-based coloring (green→red)
 * - Namespace grouping with rings
 * - Event feed panel
 * - Responsive layout with ElasticSplit + BottomDrawer
 * - Canonical lighting with SceneLighting + ShadowPlane + SceneEffects
 * - Quality selector for illumination control
 *
 * @see plans/gestalt-live-infrastructure.md
 * @see plans/web-refactor/layout-projection-functor.md
 */

import { useRef, useState, useMemo, useCallback, useEffect, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Html } from '@react-three/drei';
import * as THREE from 'three';
import { infraApi } from '../api/client';
import type {
  InfraEntity,
  InfraConnection,
  InfraTopologyResponse,
  InfraEvent,
  InfraEntityKind,
  StreamConnectionStatus,
  EntityAnimationState,
} from '../api/types';
import { INFRA_ENTITY_CONFIG, INFRA_SEVERITY_CONFIG, HEALTH_GRADE_CONFIG } from '../api/types';
import { ErrorBoundary } from '../components/error/ErrorBoundary';

// Elastic Layout Imports
import {
  ElasticSplit,
  BottomDrawer,
  FloatingActions,
  useWindowLayout,
  PHYSICAL_CONSTRAINTS,
  type FloatingAction,
  type Density,
  type DensityMap,
  fromDensity,
} from '../components/elastic';

// Illumination System Imports
import { SceneLighting, ShadowPlane } from '../components/three/SceneLighting';
import { SceneEffects } from '../components/three/SceneEffects';
import { QualitySelector } from '../components/three/QualitySelector';
import { useIlluminationQuality } from '../hooks/useIlluminationQuality';
import type { IlluminationQuality } from '../constants/lighting';

// Utilities
import { useInfraStream } from '../hooks/useInfraStream';
import { calculateAnimationChanges } from '../utils/topologyDiff';

// =============================================================================
// Constants - Density-Parameterized
// =============================================================================

/** Animation pulse speed - density-parameterized */
const PULSE_SPEED: DensityMap<number> = {
  compact: 0.004,
  comfortable: 0.005,
  spacious: 0.005,
};

/** Max visible events in feed - density-parameterized */
const MAX_VISIBLE_EVENTS: DensityMap<number> = {
  compact: 20,
  comfortable: 30,
  spacious: 50,
};

/** Entity panel width - density-parameterized */
const ENTITY_PANEL_WIDTH: DensityMap<number> = {
  compact: 0,    // Uses BottomDrawer on compact
  comfortable: 260,
  spacious: 280,
};

/** Events panel width - density-parameterized */
const EVENTS_PANEL_WIDTH: DensityMap<number> = {
  compact: 0,    // Uses BottomDrawer on compact
  comfortable: 240,
  spacious: 288, // w-72 = 18rem = 288px
};

/** Panel collapse breakpoint */
const PANEL_COLLAPSE_BREAKPOINT = 768;

/** Static animation constants */
const UNHEALTHY_THRESHOLD = 0.5;
const FADE_SPEED = 0.08;      // Opacity lerp speed
const PULSE_DECAY = 0.92;     // Pulse intensity decay per frame
const UPDATE_PULSE_INTENSITY = 0.8;  // Initial pulse intensity on update

// =============================================================================
// Types
// =============================================================================

interface PanelState {
  events: boolean;
  details: boolean;
}

// =============================================================================
// Utility Functions
// =============================================================================

/** Get color based on health score */
function getHealthColor(health: number): THREE.Color {
  if (health >= 0.8) return new THREE.Color('#22c55e'); // Green
  if (health >= 0.6) return new THREE.Color('#facc15'); // Yellow
  if (health >= 0.4) return new THREE.Color('#f97316'); // Orange
  return new THREE.Color('#ef4444'); // Red
}

/** Format bytes to human readable */
function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

/** Format relative time */
function formatRelativeTime(timestamp: string): string {
  const now = Date.now();
  const time = new Date(timestamp).getTime();
  const diff = now - time;

  if (diff < 60000) return 'just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return `${Math.floor(diff / 86400000)}d ago`;
}

// =============================================================================
// InfraNode Component - 3D entity representation with animation support
// =============================================================================

interface InfraNodeProps {
  entity: InfraEntity;
  isSelected: boolean;
  onClick: () => void;
  animationState?: EntityAnimationState;
  density: Density;
}

function InfraNode({ entity, isSelected, onClick, animationState, density }: InfraNodeProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.MeshStandardMaterial>(null);
  const [hovered, setHovered] = useState(false);

  // Animation state with ref for useFrame access
  const animRef = useRef({
    opacity: animationState?.isNew ? 0 : 1,
    pulseIntensity: animationState?.pulseIntensity || 0,
  });

  const config = INFRA_ENTITY_CONFIG[entity.kind as InfraEntityKind] || INFRA_ENTITY_CONFIG.custom;
  const color = useMemo(() => getHealthColor(entity.health), [entity.health]);

  // Get density-parameterized pulse speed
  const pulseSpeed = fromDensity(PULSE_SPEED, density);

  // Update animation state when props change
  useEffect(() => {
    if (animationState?.isNew) {
      animRef.current.opacity = 0;
    }
    if (animationState?.pulseIntensity) {
      animRef.current.pulseIntensity = animationState.pulseIntensity;
    }
  }, [animationState?.isNew, animationState?.pulseIntensity]);

  // Track the smoothly animated base scale (separate from pulse)
  const baseScaleRef = useRef(1.0);

  // Animate entity with fade, pulse, and status effects
  useFrame(() => {
    if (!meshRef.current) return;

    // Fade animation
    const targetOpacity = animationState?.isRemoving ? 0 : 1;
    animRef.current.opacity = THREE.MathUtils.lerp(
      animRef.current.opacity,
      targetOpacity,
      FADE_SPEED
    );

    // Decay pulse intensity
    animRef.current.pulseIntensity *= PULSE_DECAY;

    // Update material opacity
    if (materialRef.current) {
      materialRef.current.opacity = animRef.current.opacity * 0.8;

      // Add emissive glow for pulse effect
      if (animRef.current.pulseIntensity > 0.01) {
        materialRef.current.emissive = color;
        materialRef.current.emissiveIntensity = animRef.current.pulseIntensity;
      } else if (!isSelected && !hovered) {
        materialRef.current.emissiveIntensity = 0;
      }
    }

    // Calculate target base scale (hover/select effects)
    const animScale = animationState?.scale || 1.0;
    const targetBaseScale = (hovered || isSelected ? 1.4 : 1.0) * animScale;

    // Smoothly interpolate the base scale (no jitter from pulse feedback)
    baseScaleRef.current = THREE.MathUtils.lerp(baseScaleRef.current, targetBaseScale, 0.1);

    // Calculate pulse multiplier for unhealthy entities
    // This is applied AFTER lerp, without feeding back into lerp
    let pulseMultiplier = 1.0;
    if (entity.health < UNHEALTHY_THRESHOLD) {
      pulseMultiplier = 1 + Math.sin(Date.now() * pulseSpeed) * 0.15;
    }

    // Apply final scale = base * pulse
    const finalScale = baseScaleRef.current * pulseMultiplier;
    meshRef.current.scale.setScalar(finalScale);

    // Spin pending/terminating
    if (entity.status === 'pending' || entity.status === 'terminating') {
      meshRef.current.rotation.y += 0.02;
    }
  });

  // Get geometry based on entity kind
  const geometry = useMemo(() => {
    switch (config.shape) {
      case 'sphere':
        return <sphereGeometry args={[0.3, 24, 24]} />;
      case 'octahedron':
        return <octahedronGeometry args={[0.35]} />;
      case 'dodecahedron':
        return <dodecahedronGeometry args={[0.35]} />;
      case 'box':
        return <boxGeometry args={[0.4, 0.4, 0.4]} />;
      case 'cone':
        return <coneGeometry args={[0.3, 0.5, 16]} />;
      case 'cylinder':
        return <cylinderGeometry args={[0.25, 0.25, 0.4, 16]} />;
      case 'torus':
        return <torusGeometry args={[0.4, 0.1, 12, 24]} />;
      default:
        return <sphereGeometry args={[0.3, 24, 24]} />;
    }
  }, [config.shape]);

  return (
    <group position={[entity.x, entity.y, entity.z]}>
      <mesh
        ref={meshRef}
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
        {geometry}
        <meshStandardMaterial
          ref={materialRef}
          color={color}
          transparent
          opacity={0.8}
          emissive={isSelected ? color : hovered ? color : undefined}
          emissiveIntensity={isSelected ? 0.8 : hovered ? 0.3 : 0}
          roughness={0.4}
          metalness={0.3}
        />
      </mesh>

      {/* Selection ring */}
      {isSelected && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[0.5, 0.6, 32]} />
          <meshBasicMaterial color="#ffffff" transparent opacity={0.6} side={THREE.DoubleSide} />
        </mesh>
      )}

      {/* Label on hover */}
      {(hovered || isSelected) && (
        <Html center distanceFactor={10}>
          <div className="bg-gray-900/95 backdrop-blur-sm px-2 py-1 rounded text-xs text-white whitespace-nowrap shadow-lg border border-gray-700">
            <div className="font-semibold">{entity.name}</div>
            <div className="text-gray-400">{entity.kind} • {entity.namespace || 'default'}</div>
          </div>
        </Html>
      )}
    </group>
  );
}

// =============================================================================
// InfraEdge Component - Connection between entities
// =============================================================================

interface InfraEdgeProps {
  connection: InfraConnection;
  source: InfraEntity;
  target: InfraEntity;
}

function InfraEdge({ connection, source, target }: InfraEdgeProps) {
  const points = useMemo(() => {
    return [
      new THREE.Vector3(source.x, source.y, source.z),
      new THREE.Vector3(target.x, target.y, target.z),
    ];
  }, [source, target]);

  const geometry = useMemo(() => {
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [points]);

  // Color based on connection kind
  const color = useMemo(() => {
    switch (connection.kind) {
      case 'selects':
        return '#3b82f6'; // Blue
      case 'owns':
        return '#a855f7'; // Purple
      case 'http':
        return '#22c55e'; // Green
      case 'nats':
        return '#ec4899'; // Pink
      default:
        return '#6b7280'; // Gray
    }
  }, [connection.kind]);

  return (
    <line>
      <bufferGeometry attach="geometry" {...geometry} />
      <lineBasicMaterial
        color={color}
        transparent
        opacity={connection.is_healthy ? 0.4 : 0.2}
        linewidth={1}
      />
    </line>
  );
}

// =============================================================================
// NamespaceRing Component - Visual grouping
// =============================================================================

interface NamespaceRingProps {
  namespace: string;
  entities: InfraEntity[];
  index: number;
  total: number;
}

function NamespaceRing({ namespace, entities, index, total }: NamespaceRingProps) {
  if (entities.length === 0) return null;

  // Calculate center and radius
  const avgX = entities.reduce((sum, e) => sum + e.x, 0) / entities.length;
  const avgY = entities.reduce((sum, e) => sum + e.y, 0) / entities.length;
  const avgZ = entities.reduce((sum, e) => sum + e.z, 0) / entities.length;

  const radius = Math.max(
    ...entities.map((e) =>
      Math.sqrt(Math.pow(e.x - avgX, 2) + Math.pow(e.y - avgY, 2))
    ),
    2
  ) + 1;

  // Color based on index
  const hue = (index / Math.max(total, 1)) * 0.4 + 0.1;
  const color = new THREE.Color().setHSL(hue, 0.5, 0.5);

  return (
    <group position={[avgX, avgY, avgZ]}>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[radius - 0.05, radius + 0.05, 64]} />
        <meshBasicMaterial color={color} transparent opacity={0.15} side={THREE.DoubleSide} />
      </mesh>
      <Text
        position={[0, -radius - 0.5, 0]}
        fontSize={0.3}
        color={color}
        anchorX="center"
        anchorY="top"
      >
        {namespace}
      </Text>
    </group>
  );
}

// =============================================================================
// InfraScene Component - 3D scene with canonical lighting
// =============================================================================

interface InfraSceneProps {
  topology: InfraTopologyResponse;
  selectedEntity: InfraEntity | null;
  onEntitySelect: (entity: InfraEntity | null) => void;
  animationStates?: Map<string, EntityAnimationState>;
  density: Density;
  illuminationQuality: IlluminationQuality;
}

function InfraScene({
  topology,
  selectedEntity,
  onEntitySelect,
  animationStates,
  density,
  illuminationQuality,
}: InfraSceneProps) {
  const entityMap = useMemo(
    () => new Map(topology.entities.map((e) => [e.id, e])),
    [topology.entities]
  );

  // Group entities by namespace
  const namespaceGroups = useMemo(() => {
    const groups: Record<string, InfraEntity[]> = {};
    for (const entity of topology.entities) {
      const ns = entity.namespace || 'default';
      if (!groups[ns]) groups[ns] = [];
      groups[ns].push(entity);
    }
    return groups;
  }, [topology.entities]);

  const namespaces = Object.keys(namespaceGroups);

  return (
    <>
      {/* Canonical lighting from SceneLighting */}
      <SceneLighting
        quality={illuminationQuality}
        atmosphericFill
      />

      {/* Post-processing effects (SSAO + Bloom for high/cinematic quality) */}
      <SceneEffects quality={illuminationQuality} />

      {/* Shadow-receiving ground plane */}
      <ShadowPlane y={-15} shadowOpacity={0.2} />

      {/* Namespace rings */}
      {namespaces.map((ns, i) => (
        <NamespaceRing
          key={ns}
          namespace={ns}
          entities={namespaceGroups[ns]}
          index={i}
          total={namespaces.length}
        />
      ))}

      {/* Connections */}
      {topology.connections.map((conn) => {
        const source = entityMap.get(conn.source_id);
        const target = entityMap.get(conn.target_id);
        if (!source || !target) return null;

        return (
          <InfraEdge
            key={conn.id}
            connection={conn}
            source={source}
            target={target}
          />
        );
      })}

      {/* Entities */}
      {topology.entities.map((entity) => (
        <InfraNode
          key={entity.id}
          entity={entity}
          isSelected={selectedEntity?.id === entity.id}
          onClick={() => onEntitySelect(entity)}
          animationState={animationStates?.get(entity.id)}
          density={density}
        />
      ))}

      {/* Camera controls with touch support */}
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
// EventFeed Component - Real-time events panel (Elastic)
// =============================================================================

interface EventFeedProps {
  events: InfraEvent[];
  density: Density;
  isDrawer?: boolean;
}

function EventFeed({ events, density, isDrawer }: EventFeedProps) {
  const isCompact = density === 'compact';
  const maxEvents = fromDensity(MAX_VISIBLE_EVENTS, density);
  const displayEvents = events.slice(0, maxEvents);

  return (
    <div className={`h-full overflow-y-auto ${isDrawer ? 'rounded-t-xl' : ''}`}>
      {displayEvents.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <div className={isCompact ? 'text-xl mb-1' : 'text-2xl mb-2'}>📭</div>
          <p className={isCompact ? 'text-xs' : 'text-sm'}>No events yet</p>
        </div>
      ) : (
        displayEvents.map((event, i) => {
          const config = INFRA_SEVERITY_CONFIG[event.severity];
          return (
            <div
              key={event.id}
              className={`
                ${isCompact ? 'p-2' : 'p-3'} border-b border-gray-700 transition-colors
                ${i < 3 ? 'bg-gray-800/30' : ''}
              `}
            >
              <div className="flex items-start gap-2">
                <span className={`${isCompact ? 'text-base' : 'text-lg'} flex-shrink-0`}>{config.icon}</span>
                <div className="flex-1 min-w-0">
                  <p className={`${isCompact ? 'text-xs' : 'text-sm'} text-white font-medium line-clamp-2`}>
                    {event.reason}: {event.message}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {event.entity_kind}/{event.entity_name}
                    {event.entity_namespace && ` in ${event.entity_namespace}`}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {formatRelativeTime(event.timestamp)}
                    {event.count > 1 && ` (${event.count}x)`}
                  </p>
                </div>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}

// =============================================================================
// EntityDetailPanel Component - Selected entity details (Elastic)
// =============================================================================

interface EntityDetailPanelProps {
  entity: InfraEntity;
  onClose: () => void;
  density: Density;
  isDrawer?: boolean;
}

function EntityDetailPanel({ entity, onClose, density, isDrawer }: EntityDetailPanelProps) {
  const config = INFRA_ENTITY_CONFIG[entity.kind as InfraEntityKind] || INFRA_ENTITY_CONFIG.custom;
  const gradeConfig = HEALTH_GRADE_CONFIG[entity.health_grade] || HEALTH_GRADE_CONFIG['?'];
  const isCompact = density === 'compact';
  const panelWidth = fromDensity(ENTITY_PANEL_WIDTH, density);

  return (
    <div
      className={`
        bg-gray-800 flex flex-col overflow-hidden
        ${isDrawer ? 'h-full rounded-t-xl' : 'border-l border-gray-700'}
      `}
      style={{ width: isDrawer ? 'auto' : panelWidth || 280 }}
    >
      {/* Header */}
      <div className={`${isCompact ? 'p-3' : 'p-4'} border-b border-gray-700`}>
        <div className="flex justify-between items-start gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className={isCompact ? 'text-lg' : 'text-xl'}>{config.icon}</span>
              <h3 className={`font-semibold text-white truncate ${isCompact ? 'text-base' : 'text-lg'}`}>
                {entity.name}
              </h3>
            </div>
            <p className="text-xs text-gray-400 font-mono truncate">
              {entity.namespace || 'default'} / {entity.kind}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl p-1 -mr-1 -mt-1 rounded hover:bg-gray-700 transition-colors flex-shrink-0"
            aria-label="Close panel"
            style={{
              minWidth: PHYSICAL_CONSTRAINTS.minTouchTarget,
              minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget,
            }}
          >
            ×
          </button>
        </div>

        {/* Status badges */}
        <div className="flex flex-wrap gap-2 mt-3">
          <span
            className="px-2 py-0.5 text-xs font-bold rounded"
            style={{ backgroundColor: gradeConfig.color + '33', color: gradeConfig.color }}
          >
            {entity.health_grade}
          </span>
          <span
            className={`px-2 py-0.5 text-xs rounded ${
              entity.status === 'running'
                ? 'bg-green-900/50 text-green-300'
                : entity.status === 'pending'
                  ? 'bg-yellow-900/50 text-yellow-300'
                  : 'bg-red-900/50 text-red-300'
            }`}
          >
            {entity.status}
          </span>
        </div>
      </div>

      {/* Metrics */}
      <div className="p-4 flex-1 overflow-y-auto">
        {/* Health bar */}
        <div className="mb-4">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Health</span>
            <span style={{ color: gradeConfig.color }}>{Math.round(entity.health * 100)}%</span>
          </div>
          <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full transition-all rounded-full"
              style={{
                width: `${entity.health * 100}%`,
                backgroundColor: gradeConfig.color,
              }}
            />
          </div>
        </div>

        {/* Resource metrics */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-gray-700/50 rounded-lg p-3">
            <p className="text-xs text-gray-400 mb-0.5">CPU</p>
            <p className="font-semibold text-white">{entity.cpu_percent.toFixed(1)}%</p>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-3">
            <p className="text-xs text-gray-400 mb-0.5">Memory</p>
            <p className="font-semibold text-white">
              {entity.memory_percent ? `${entity.memory_percent.toFixed(1)}%` : formatBytes(entity.memory_bytes)}
            </p>
          </div>
        </div>

        {/* Custom metrics */}
        {Object.keys(entity.custom_metrics).length > 0 && (
          <div className="mb-4">
            <h4 className="text-xs text-gray-400 mb-2">Metrics</h4>
            <div className="bg-gray-900/50 rounded-lg p-2 space-y-1">
              {Object.entries(entity.custom_metrics).map(([key, value]) => (
                <div key={key} className="flex justify-between text-xs">
                  <span className="text-gray-400">{key}</span>
                  <span className="text-white font-mono">{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Labels */}
        {Object.keys(entity.labels).length > 0 && (
          <div>
            <h4 className="text-xs text-gray-400 mb-2">Labels</h4>
            <div className="flex flex-wrap gap-1">
              {Object.entries(entity.labels).slice(0, 6).map(([key, value]) => (
                <span
                  key={key}
                  className="px-1.5 py-0.5 text-[10px] bg-gray-700 text-gray-300 rounded truncate max-w-[120px]"
                  title={`${key}=${value}`}
                >
                  {key}: {value}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Status message */}
        {entity.status_message && (
          <div className="mt-4 p-2 bg-yellow-900/20 border border-yellow-800/50 rounded text-xs text-yellow-300">
            {entity.status_message}
          </div>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// HealthSummary Component - Aggregate stats overlay (Elastic)
// =============================================================================

interface HealthSummaryProps {
  topology: InfraTopologyResponse;
  isMobile?: boolean;
}

function HealthSummary({ topology, isMobile }: HealthSummaryProps) {
  return (
    <div className={`absolute top-3 left-3 bg-gray-800/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow-lg ${isMobile ? 'text-[10px]' : 'text-xs'}`}>
      <div className="flex items-center gap-3">
        <span className="text-green-400 font-semibold">{topology.healthy_count}</span>
        <span className="text-gray-400">healthy</span>
        {topology.warning_count > 0 && (
          <>
            <span className="text-yellow-400 font-semibold">{topology.warning_count}</span>
            {!isMobile && <span className="text-gray-400">warning</span>}
          </>
        )}
        {topology.critical_count > 0 && (
          <>
            <span className="text-red-400 font-semibold">{topology.critical_count}</span>
            {!isMobile && <span className="text-gray-400">critical</span>}
          </>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// ConnectionStatus Component - SSE connection indicator
// =============================================================================

interface ConnectionStatusProps {
  status: StreamConnectionStatus;
}

function ConnectionStatus({ status }: ConnectionStatusProps) {
  const config = useMemo(() => {
    switch (status) {
      case 'connected':
        return { color: '#22c55e', icon: '●', text: 'Live' };
      case 'connecting':
        return { color: '#f59e0b', icon: '○', text: 'Connecting...' };
      case 'reconnecting':
        return { color: '#f59e0b', icon: '◐', text: 'Reconnecting...' };
      case 'error':
        return { color: '#ef4444', icon: '●', text: 'Error' };
      case 'disconnected':
      default:
        return { color: '#6b7280', icon: '○', text: 'Offline' };
    }
  }, [status]);

  return (
    <div
      className="flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium"
      style={{ backgroundColor: config.color + '22', color: config.color }}
    >
      <span className={status === 'reconnecting' ? 'animate-pulse' : ''}>
        {config.icon}
      </span>
      <span>{config.text}</span>
    </div>
  );
}

// =============================================================================
// Loading & Error States
// =============================================================================

function TopologyLoading() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900">
      <div className="text-6xl mb-4 animate-pulse">🔄</div>
      <p className="text-gray-400 text-sm">Connecting to infrastructure...</p>
    </div>
  );
}

function TopologyErrorFallback({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900 p-8">
      <div className="text-5xl mb-4">⚠️</div>
      <h3 className="text-lg font-semibold text-gray-300 mb-2">Connection Failed</h3>
      <p className="text-gray-500 text-sm text-center mb-4 max-w-md">
        Could not connect to infrastructure collector. Make sure the backend is running.
      </p>
      <button
        onClick={onRetry}
        className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium"
      >
        Retry
      </button>
    </div>
  );
}

// =============================================================================
// Main GestaltLive Component - Elastic Edition
// =============================================================================

export default function GestaltLive() {
  const { density, isMobile, isTablet, isDesktop } = useWindowLayout();

  // Illumination quality for canonical lighting
  const { quality: illuminationQuality, isAutoDetected, override: overrideQuality } = useIlluminationQuality();
  const shadowsEnabled = illuminationQuality !== 'minimal';

  // State
  const [initialTopology, setInitialTopology] = useState<InfraTopologyResponse | null>(null);
  const [selectedEntity, setSelectedEntity] = useState<InfraEntity | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Panel state for mobile drawers
  const [panelState, setPanelState] = useState<PanelState>({
    events: false,
    details: false,
  });

  // Animation states for entities
  const [animationStates, setAnimationStates] = useState<Map<string, EntityAnimationState>>(new Map());
  const prevEntitiesRef = useRef<InfraEntity[]>([]);

  // Use streaming hook for real-time updates
  const {
    topology,
    events,
    status: streamStatus,
    reconnect,
    error: streamError,
  } = useInfraStream(initialTopology);

  // Track animation changes when topology updates
  useEffect(() => {
    if (!topology) return;

    const prevEntities = prevEntitiesRef.current;
    const nextEntities = topology.entities;

    // Calculate what changed
    const changes = calculateAnimationChanges(prevEntities, nextEntities);

    // Update animation states
    if (changes.size > 0) {
      setAnimationStates((prev) => {
        const next = new Map(prev);
        const now = Date.now();

        for (const [entityId, change] of changes) {
          switch (change) {
            case 'fadeIn':
              next.set(entityId, {
                opacity: 0,
                scale: 1,
                pulseIntensity: 0,
                isNew: true,
                isRemoving: false,
                lastUpdated: now,
              });
              break;
            case 'pulse':
              next.set(entityId, {
                opacity: 1,
                scale: 1,
                pulseIntensity: UPDATE_PULSE_INTENSITY,
                isNew: false,
                isRemoving: false,
                lastUpdated: now,
              });
              break;
            case 'fadeOut':
              const existing = prev.get(entityId);
              next.set(entityId, {
                opacity: existing?.opacity || 1,
                scale: 1,
                pulseIntensity: 0,
                isNew: false,
                isRemoving: true,
                lastUpdated: now,
              });
              break;
          }
        }

        return next;
      });
    }

    // Store current entities for next comparison
    prevEntitiesRef.current = nextEntities;

    // Clean up animation states for removed entities after fade out
    const cleanupTimeout = setTimeout(() => {
      setAnimationStates((prev) => {
        const next = new Map(prev);
        for (const [entityId, state] of prev) {
          if (state.isRemoving) {
            next.delete(entityId);
          }
        }
        return next;
      });
    }, 500); // Wait for fade out animation

    return () => clearTimeout(cleanupTimeout);
  }, [topology]);

  // Initial load with timeout
  const loadTopology = useCallback(async () => {
    setLoading(true);
    setLoadError(null);

    // Add timeout to prevent infinite loading
    const timeoutId = setTimeout(() => {
      setLoadError('Connection timeout. Is the backend running on port 8000?');
      setLoading(false);
    }, 10000); // 10 second timeout

    try {
      // Ensure connected
      await infraApi.connect();

      // Get initial topology
      const response = await infraApi.getTopology();
      clearTimeout(timeoutId);
      setInitialTopology(response.data);
      prevEntitiesRef.current = response.data.entities;
    } catch (err) {
      clearTimeout(timeoutId);
      console.error('Failed to load infrastructure:', err);
      setLoadError('Failed to connect to infrastructure. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadTopology();
  }, [loadTopology]);

  // Handle retry
  const handleRetry = useCallback(() => {
    loadTopology();
    reconnect();
  }, [loadTopology, reconnect]);

  // Handle entity selection (auto-open drawer on mobile)
  const handleEntitySelect = useCallback((entity: InfraEntity | null) => {
    setSelectedEntity(entity);
    if (entity && isMobile) {
      setPanelState((s) => ({ ...s, details: true }));
    }
  }, [isMobile]);

  // Close detail panel
  const handleCloseDetails = useCallback(() => {
    setSelectedEntity(null);
    setPanelState((s) => ({ ...s, details: false }));
  }, []);

  // Combined error state
  const error = loadError || streamError;

  // ==========================================================================
  // Render: 3D Canvas
  // ==========================================================================

  const canvas3D = topology && (
    <ErrorBoundary fallback={<TopologyErrorFallback onRetry={handleRetry} />}>
      <Suspense fallback={<TopologyLoading />}>
        <Canvas
          camera={{ position: [0, 0, isMobile ? 30 : 25], fov: 55 }}
          gl={{ antialias: true, alpha: false }}
          shadows={shadowsEnabled}
          style={{ background: '#111827' }}
          onClick={() => setSelectedEntity(null)}
        >
          <InfraScene
            topology={topology}
            selectedEntity={selectedEntity}
            onEntitySelect={handleEntitySelect}
            animationStates={animationStates}
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
    <HealthSummary topology={topology} isMobile={isMobile} />
  );

  const hintsOverlay = !isMobile && (
    <div className="absolute bottom-3 left-3 flex items-center gap-3">
      <div className="bg-gray-800/90 backdrop-blur-sm rounded-lg px-3 py-2 text-xs text-gray-500 shadow-lg">
        Drag to rotate • Scroll to zoom • Click entity for details
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

  // ==========================================================================
  // Render: Loading/Error states
  // ==========================================================================

  if (loading && !topology) {
    return (
      <div className="h-screen bg-gray-900">
        <TopologyLoading />
      </div>
    );
  }

  if (error && !topology) {
    return (
      <div className="h-screen bg-gray-900">
        <TopologyErrorFallback onRetry={handleRetry} />
      </div>
    );
  }

  // ==========================================================================
  // Render: Mobile Layout (Compact density)
  // ==========================================================================

  if (isMobile) {
    return (
      <div className="h-screen flex flex-col bg-gray-900 text-white overflow-hidden">
        {/* Compact header */}
        <header className="flex-shrink-0 border-b border-gray-800 px-3 py-2 bg-gray-900 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">🌐</span>
            <span className="font-semibold">Live</span>
            {topology && (
              <span
                className="text-xs font-bold px-1.5 py-0.5 rounded"
                style={{
                  backgroundColor: topology.overall_health >= 0.8 ? '#22c55e33' : '#ef444433',
                  color: topology.overall_health >= 0.8 ? '#22c55e' : '#ef4444',
                }}
              >
                {Math.round(topology.overall_health * 100)}%
              </span>
            )}
          </div>
          <ConnectionStatus status={streamStatus} />
        </header>

        {/* Main content */}
        <div className="flex-1 relative">
          {error ? (
            <div className="h-full flex items-center justify-center p-4">
              <div className="text-center">
                <div className="text-4xl mb-3">⚠️</div>
                <p className="text-gray-400 text-sm mb-4">{error}</p>
                <button
                  onClick={handleRetry}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm"
                  style={{
                    minWidth: PHYSICAL_CONSTRAINTS.minTouchTarget,
                    minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget,
                  }}
                >
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

              {/* Floating actions for mobile */}
              <FloatingActions
                actions={[
                  {
                    id: 'refresh',
                    icon: loading ? '⏳' : '🔄',
                    label: 'Refresh',
                    onClick: handleRetry,
                    variant: 'primary',
                    loading: loading,
                    disabled: loading,
                  },
                  {
                    id: 'events',
                    icon: '📋',
                    label: 'Events',
                    onClick: () => setPanelState((s) => ({ ...s, events: !s.events })),
                    isActive: panelState.events,
                  },
                  ...(selectedEntity
                    ? [
                        {
                          id: 'details',
                          icon: '📊',
                          label: 'Details',
                          onClick: () => setPanelState((s) => ({ ...s, details: !s.details })),
                          isActive: panelState.details,
                        } as FloatingAction,
                      ]
                    : []),
                ]}
                position="bottom-right"
              />
            </>
          )}
        </div>

        {/* Events drawer (mobile) */}
        <BottomDrawer
          isOpen={panelState.events}
          onClose={() => setPanelState((s) => ({ ...s, events: false }))}
          title={`Events (${events.length})`}
        >
          <EventFeed events={events} density={density} isDrawer />
        </BottomDrawer>

        {/* Entity details drawer (mobile) */}
        <BottomDrawer
          isOpen={panelState.details && !!selectedEntity}
          onClose={handleCloseDetails}
          title={selectedEntity?.name || 'Details'}
        >
          {selectedEntity && (
            <EntityDetailPanel
              entity={selectedEntity}
              onClose={handleCloseDetails}
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

  const eventsPanel = (
    <div
      className="h-full border-l border-gray-700 bg-gray-800 flex flex-col"
      style={{ width: fromDensity(EVENTS_PANEL_WIDTH, density) || 288 }}
    >
      <div className="p-3 border-b border-gray-700 flex items-center justify-between">
        <h3 className="font-semibold text-sm">Events</h3>
        <span className="text-xs text-gray-400">{events.length}</span>
      </div>
      <EventFeed events={events} density={density} />
    </div>
  );

  const detailPanel = selectedEntity && (
    <EntityDetailPanel
      entity={selectedEntity}
      onClose={handleCloseDetails}
      density={density}
    />
  );

  // Right panel: details or events
  const rightPanelContent = (
    <div className="h-full flex">
      {detailPanel || eventsPanel}
    </div>
  );

  // Calculate split ratio based on details panel presence
  const splitRatio = selectedEntity ? (isDesktop ? 0.72 : 0.65) : (isDesktop ? 0.78 : 0.70);

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-white overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-gray-800 px-4 py-3 bg-gray-900">
        <div className="flex justify-between items-center">
          <div>
            <h1 className={`font-bold flex items-center gap-2 ${isTablet ? 'text-lg' : 'text-xl'}`}>
              <span>🌐</span>
              <span>Gestalt Live</span>
              {topology && (
                <span
                  className="text-sm font-normal px-2 py-0.5 rounded ml-2"
                  style={{
                    backgroundColor: topology.overall_health >= 0.8 ? '#22c55e33' : '#ef444433',
                    color: topology.overall_health >= 0.8 ? '#22c55e' : '#ef4444',
                  }}
                >
                  {Math.round(topology.overall_health * 100)}%
                </span>
              )}
            </h1>
            <p className={`text-gray-400 mt-0.5 ${isTablet ? 'text-xs' : 'text-sm'}`}>
              {topology
                ? `${topology.total_entities} entities • ${topology.connections.length} connections`
                : 'Loading...'}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <ConnectionStatus status={streamStatus} />
            <button
              onClick={handleRetry}
              disabled={loading}
              className={`px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center gap-2 ${isTablet ? 'text-xs' : 'text-sm'}`}
              style={{
                minWidth: PHYSICAL_CONSTRAINTS.minTouchTarget,
                minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget,
              }}
            >
              {loading ? (
                <>
                  <span className="animate-spin">⚙️</span>
                  {isDesktop && 'Refreshing...'}
                </>
              ) : (
                <>
                  <span>🔄</span>
                  {isDesktop && 'Refresh'}
                </>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main content with ElasticSplit */}
      {error ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-5xl mb-4">⚠️</div>
            <p className="text-gray-400 mb-4">{error}</p>
            <button
              onClick={handleRetry}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg"
              style={{
                minWidth: PHYSICAL_CONSTRAINTS.minTouchTarget,
                minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget,
              }}
            >
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
              </div>
            }
            secondary={rightPanelContent}
          />
        </div>
      )}
    </div>
  );
}
