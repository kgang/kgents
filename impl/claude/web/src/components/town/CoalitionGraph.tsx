/**
 * CoalitionGraph - Visual Graph of Town Coalitions
 *
 * P0 User Journey: Visualize coalition memberships, bridge citizens,
 * and coalition health.
 *
 * Design Language:
 * - Organic/crystalline aesthetic with vine connections
 * - Violet theme (Coalition Crown Jewel)
 * - Force-directed graph layout
 *
 * @see docs/skills/elastic-ui-patterns.md
 * @see components/gestalt/OrganicNode.tsx (reference)
 */

import { useMemo, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Network,
  X,
  Zap,
  ChevronRight,
  RefreshCw,
} from 'lucide-react';
import {
  useCoalitions,
  useCoalition,
  useCoalitionBridges,
  useDetectCoalitions,
  useCitizens,
} from '../../hooks';
import { useShell } from '../../shell/ShellProvider';
import { JEWEL_COLORS } from '../../constants/jewels';
import { TeachingCallout } from '../categorical';
import { TeachingToggle, WhenTeaching } from '../../hooks/useTeachingMode';

// =============================================================================
// Constants
// =============================================================================

const VIOLET = JEWEL_COLORS.coalition;

// =============================================================================
// Types
// =============================================================================

interface GraphNode {
  id: string;
  type: 'coalition' | 'citizen';
  label: string;
  x: number;
  y: number;
  strength?: number;
  isBridge?: boolean;
}

interface GraphEdge {
  source: string;
  target: string;
}

// =============================================================================
// Graph Layout Helpers
// =============================================================================

function buildGraph(
  coalitions: Array<{ id: string; name: string; members: string[]; strength: number }>,
  bridgeCitizens: string[],
  width: number,
  height: number
): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];
  const citizenSet = new Set<string>();

  // Center point
  const cx = width / 2;
  const cy = height / 2;

  // Add coalition nodes in a circle
  const coalitionRadius = Math.min(width, height) * 0.3;
  coalitions.forEach((coalition, i) => {
    const angle = (2 * Math.PI * i) / coalitions.length - Math.PI / 2;
    nodes.push({
      id: coalition.id,
      type: 'coalition',
      label: coalition.name,
      x: cx + coalitionRadius * Math.cos(angle),
      y: cy + coalitionRadius * Math.sin(angle),
      strength: coalition.strength,
    });

    // Track citizens
    coalition.members.forEach((citizenId) => {
      citizenSet.add(citizenId);
      edges.push({ source: coalition.id, target: citizenId });
    });
  });

  // Add citizen nodes around their coalitions
  const citizenArray = Array.from(citizenSet);
  const citizenRadius = Math.min(width, height) * 0.15;
  citizenArray.forEach((citizenId, i) => {
    // Find which coalition(s) this citizen belongs to
    const memberOf = coalitions.filter((c) => c.members.includes(citizenId));

    // Position near center of connected coalitions
    let x = cx;
    let y = cy;
    if (memberOf.length > 0) {
      const coalitionNode = nodes.find((n) => n.id === memberOf[0].id);
      if (coalitionNode) {
        const offset = (2 * Math.PI * (i % 8)) / 8;
        x = coalitionNode.x + citizenRadius * Math.cos(offset);
        y = coalitionNode.y + citizenRadius * Math.sin(offset);
      }
    }

    nodes.push({
      id: citizenId,
      type: 'citizen',
      label: citizenId.slice(0, 8),
      x,
      y,
      isBridge: bridgeCitizens.includes(citizenId),
    });
  });

  return { nodes, edges };
}

// =============================================================================
// Sub-components
// =============================================================================

interface CoalitionNodeProps {
  node: GraphNode;
  isSelected: boolean;
  onClick: () => void;
}

function CoalitionNode({ node, isSelected, onClick }: CoalitionNodeProps) {
  const strengthPercent = (node.strength ?? 0) * 100;
  const size = 60 + strengthPercent * 0.3;
  const hue = 270 + (node.strength ?? 0.5) * 30; // Violet range

  return (
    <motion.g
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      whileHover={{ scale: 1.1 }}
      onClick={onClick}
      style={{ cursor: 'pointer' }}
    >
      {/* Outer glow */}
      <circle
        cx={node.x}
        cy={node.y}
        r={size / 2 + 8}
        fill={`hsla(${hue}, 70%, 50%, 0.2)`}
        filter="blur(4px)"
      />
      {/* Main circle */}
      <circle
        cx={node.x}
        cy={node.y}
        r={size / 2}
        fill={`hsla(${hue}, 60%, 20%, 0.9)`}
        stroke={isSelected ? VIOLET.primary : `hsla(${hue}, 60%, 50%, 0.5)`}
        strokeWidth={isSelected ? 3 : 1.5}
      />
      {/* Strength indicator */}
      <circle
        cx={node.x}
        cy={node.y}
        r={size / 2 - 4}
        fill="none"
        stroke={`hsla(${hue}, 70%, 60%, 0.7)`}
        strokeWidth={3}
        strokeDasharray={`${strengthPercent * 2} ${200 - strengthPercent * 2}`}
        strokeDashoffset={50}
        strokeLinecap="round"
      />
      {/* Label */}
      <text
        x={node.x}
        y={node.y}
        textAnchor="middle"
        dominantBaseline="middle"
        fill="white"
        fontSize={12}
        fontWeight={500}
      >
        {node.label.length > 10 ? node.label.slice(0, 10) + '...' : node.label}
      </text>
    </motion.g>
  );
}

interface CitizenNodeProps {
  node: GraphNode;
  onClick: () => void;
}

function CitizenNode({ node, onClick }: CitizenNodeProps) {
  const size = node.isBridge ? 24 : 16;
  const color = node.isBridge ? '#f59e0b' : '#8b5cf6'; // Amber for bridges, violet for regular

  return (
    <motion.g
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ delay: 0.2 }}
      whileHover={{ scale: 1.3 }}
      onClick={onClick}
      style={{ cursor: 'pointer' }}
    >
      {node.isBridge && (
        <circle
          cx={node.x}
          cy={node.y}
          r={size / 2 + 6}
          fill="rgba(245, 158, 11, 0.2)"
          filter="blur(3px)"
        />
      )}
      <circle
        cx={node.x}
        cy={node.y}
        r={size / 2}
        fill={color}
        stroke={node.isBridge ? '#fbbf24' : '#a78bfa'}
        strokeWidth={1.5}
      />
    </motion.g>
  );
}

interface GraphEdgeProps {
  edge: GraphEdge;
  nodes: GraphNode[];
}

function GraphEdge({ edge, nodes }: GraphEdgeProps) {
  const source = nodes.find((n) => n.id === edge.source);
  const target = nodes.find((n) => n.id === edge.target);

  if (!source || !target) return null;

  return (
    <motion.line
      initial={{ pathLength: 0, opacity: 0 }}
      animate={{ pathLength: 1, opacity: 0.3 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      x1={source.x}
      y1={source.y}
      x2={target.x}
      y2={target.y}
      stroke="#8b5cf6"
      strokeWidth={1}
      strokeDasharray="4 2"
    />
  );
}

interface CoalitionDetailPanelProps {
  coalitionId: string;
  onClose: () => void;
  onViewCitizen: (citizenId: string) => void;
}

function CoalitionDetailPanel({ coalitionId, onClose, onViewCitizen }: CoalitionDetailPanelProps) {
  const coalition = useCoalition(coalitionId);
  const citizens = useCitizens();

  if (coalition.isLoading) {
    return (
      <div className="p-6 animate-pulse space-y-4">
        <div className="h-8 w-48 bg-violet-950/50 rounded" />
        <div className="h-24 bg-violet-950/50 rounded" />
      </div>
    );
  }

  const data = coalition.data;
  if (!data) {
    return (
      <div className="p-6 text-center text-gray-500">
        <p>Coalition not found</p>
      </div>
    );
  }

  const strengthPercent = Math.round(data.strength * 100);
  const strengthColor = strengthPercent > 70 ? 'text-green-400' : strengthPercent > 40 ? 'text-yellow-400' : 'text-red-400';

  // Get citizen names
  const citizenMap = new Map(citizens.data?.citizens.map((c) => [c.id, c]) ?? []);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-violet-500/30 flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-violet-500/20 flex items-center justify-center">
            <Network className="w-6 h-6 text-violet-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">{data.name}</h2>
            <p className="text-sm text-gray-400">{data.members.length} members</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 hover:bg-violet-950/50 rounded-lg transition-colors"
        >
          <X className="w-4 h-4 text-gray-400" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Strength */}
        <div>
          <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Strength</h3>
          <div className="flex items-center gap-3">
            <div className="flex-1 h-3 bg-violet-950 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${strengthPercent}%` }}
                className={`h-full ${strengthPercent > 70 ? 'bg-green-500' : strengthPercent > 40 ? 'bg-yellow-500' : 'bg-red-500'}`}
              />
            </div>
            <span className={`font-bold ${strengthColor}`}>{strengthPercent}%</span>
          </div>
        </div>

        {/* Purpose */}
        <div>
          <h3 className="text-xs font-medium text-gray-500 uppercase mb-1">Purpose</h3>
          <p className="text-sm text-gray-300">{data.purpose}</p>
        </div>

        {/* Members */}
        <div>
          <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Members</h3>
          <div className="space-y-1">
            {data.members.map((memberId) => {
              const citizen = citizenMap.get(memberId);
              return (
                <button
                  key={memberId}
                  onClick={() => onViewCitizen(memberId)}
                  className="w-full p-2 flex items-center justify-between bg-violet-950/30 hover:bg-violet-950/50 rounded-lg transition-colors text-left"
                >
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${citizen?.is_active ? 'bg-green-400' : 'bg-gray-500'}`} />
                    <span className="text-sm text-gray-300">{citizen?.name ?? memberId.slice(0, 12)}</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-violet-400" />
                </button>
              );
            })}
          </div>
        </div>

        {/* Metadata */}
        <div className="text-xs text-gray-500">
          Formed: {new Date(data.formed_at).toLocaleDateString()}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function CoalitionGraph() {
  const navigate = useNavigate();
  const { coalitionId } = useParams<{ coalitionId?: string }>();
  const { density } = useShell();
  const isCompact = density === 'compact';

  // Graph dimensions
  const graphWidth = isCompact ? 350 : 600;
  const graphHeight = isCompact ? 400 : 500;

  // Fetch data
  const coalitions = useCoalitions();
  const bridges = useCoalitionBridges();
  const detectCoalitions = useDetectCoalitions();

  // Build graph
  const graph = useMemo(() => {
    const coalitionData = coalitions.data?.coalitions ?? [];
    const bridgeCitizens = bridges.data?.bridge_citizens ?? [];

    // Need to fetch full coalition details for member lists
    // For now, use mock structure
    const coalitionsWithMembers = coalitionData.map((c) => ({
      id: c.id,
      name: c.name,
      members: [] as string[], // Would need separate query
      strength: c.strength,
    }));

    return buildGraph(coalitionsWithMembers, bridgeCitizens, graphWidth, graphHeight);
  }, [coalitions.data, bridges.data, graphWidth, graphHeight]);

  const handleSelectCoalition = useCallback((id: string) => {
    navigate(`/world.town.coalition.${id}`);
  }, [navigate]);

  const handleCloseCoalition = useCallback(() => {
    navigate('/world.town.coalition');
  }, [navigate]);

  const handleViewCitizen = useCallback((citizenId: string) => {
    navigate(`/world.town.citizen.${citizenId}`);
  }, [navigate]);

  const handleDetect = useCallback(() => {
    detectCoalitions.mutate({});
  }, [detectCoalitions]);

  // Loading state
  if (coalitions.isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-violet-400 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-gray-400">Loading coalitions...</p>
        </div>
      </div>
    );
  }

  const coalitionList = coalitions.data?.coalitions ?? [];
  const bridgeCount = bridges.data?.count ?? 0;

  return (
    <div className="h-full flex">
      {/* Graph Panel */}
      <div className={`${coalitionId && !isCompact ? 'w-2/3 border-r border-violet-500/30' : 'w-full'} flex flex-col`}>
        {/* Header */}
        <div className="p-4 border-b border-violet-500/30 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Network className="w-5 h-5 text-violet-400" />
            <h1 className="text-lg font-semibold text-white">Coalition Graph</h1>
            <span className="text-sm text-gray-500">
              {coalitionList.length} coalitions • {bridgeCount} bridges
            </span>
          </div>
          <div className="flex items-center gap-2">
            <TeachingToggle compact />
            <button
              onClick={handleDetect}
              disabled={detectCoalitions.isPending}
              className="flex items-center gap-2 px-3 py-1.5 bg-violet-500/20 hover:bg-violet-500/30 rounded-lg text-violet-300 text-sm transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${detectCoalitions.isPending ? 'animate-spin' : ''}`} />
              Detect
            </button>
          </div>
        </div>

        {/* Teaching: Operad explanation */}
        <WhenTeaching>
          <div className="px-4 pt-4">
            <TeachingCallout category="operational" title="Coalition Formation Operad">
              <p className="mb-2">
                Coalitions emerge from <code className="bg-violet-950 px-1 rounded">TOWN_OPERAD</code> operations:
              </p>
              <ul className="list-disc list-inside space-y-1 text-sm">
                <li><strong>coalition_form(arity=3)</strong>: Requires 3+ citizens with shared purpose</li>
                <li><strong>coalition_dissolve(arity=1)</strong>: Single coalition dissolution</li>
                <li><strong>Bridge citizens</strong>: Members of 2+ coalitions (shown in amber)</li>
              </ul>
              <p className="mt-2 text-xs text-gray-400">
                Social operations (greet, gossip, trade) strengthen coalition bonds.
              </p>
            </TeachingCallout>
          </div>
        </WhenTeaching>

        {/* Graph */}
        <div className="flex-1 flex items-center justify-center p-4">
          {coalitionList.length > 0 ? (
            <svg width={graphWidth} height={graphHeight} className="overflow-visible">
              {/* Edges */}
              {graph.edges.map((edge, i) => (
                <GraphEdge key={i} edge={edge} nodes={graph.nodes} />
              ))}
              {/* Coalition nodes */}
              {graph.nodes
                .filter((n) => n.type === 'coalition')
                .map((node) => (
                  <CoalitionNode
                    key={node.id}
                    node={node}
                    isSelected={node.id === coalitionId}
                    onClick={() => handleSelectCoalition(node.id)}
                  />
                ))}
              {/* Citizen nodes */}
              {graph.nodes
                .filter((n) => n.type === 'citizen')
                .map((node) => (
                  <CitizenNode
                    key={node.id}
                    node={node}
                    onClick={() => handleViewCitizen(node.id)}
                  />
                ))}
            </svg>
          ) : (
            <div className="text-center text-gray-500">
              <Network className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p className="text-lg mb-2">No coalitions yet</p>
              <p className="text-sm mb-4">Run coalition detection to discover groups</p>
              <button
                onClick={handleDetect}
                className="px-4 py-2 bg-violet-500 hover:bg-violet-400 rounded-lg text-white font-medium transition-colors flex items-center gap-2 mx-auto"
              >
                <Zap className="w-4 h-4" />
                Detect Coalitions
              </button>
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="px-4 pb-4 flex items-center gap-6 text-xs text-gray-500">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-violet-500" />
            <span>Coalition</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-violet-500" />
            <span>Citizen</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-amber-500" />
            <span>Bridge Citizen</span>
          </div>
        </div>
      </div>

      {/* Detail Panel */}
      <AnimatePresence>
        {coalitionId && !isCompact && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="w-1/3 bg-violet-950/20"
          >
            <CoalitionDetailPanel
              coalitionId={coalitionId}
              onClose={handleCloseCoalition}
              onViewCitizen={handleViewCitizen}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default CoalitionGraph;
