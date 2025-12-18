/**
 * Brain2D - Living Memory Cartography
 *
 * The 2D Renaissance implementation that replaces 1004 lines of Three.js
 * with honest, breathing 2D visualization of crystallized memories.
 *
 * Philosophy: "Memory isn't a starfield. It's a living library where crystals
 * form, connect, and surface when needed."
 *
 * @see spec/protocols/2d-renaissance.md - Phase 4: Brain2D
 * @see docs/skills/elastic-ui-patterns.md - Layout patterns
 */

import { useState, useCallback, useMemo } from 'react';
import { Brain, Sparkles, Search } from 'lucide-react';
import { useShell } from '@/shell';
import { ElasticSplit } from '@/components/elastic/ElasticSplit';
import { BottomDrawer } from '@/components/elastic/BottomDrawer';
import { Breathe } from '@/components/joy';
import type { SelfMemoryTopologyResponse, TopologyNode } from '@/api/types';

// Sub-components
import { CrystalTree, groupByCategory } from './CrystalTree';
import { CrystalDetail } from './CrystalDetail';
import { CaptureForm } from './CaptureForm';
import { GhostSurface } from './GhostSurface';

// =============================================================================
// Helpers - Transform SelfMemory node to TopologyNode for CrystalDetail
// =============================================================================

type SelfMemoryNode = SelfMemoryTopologyResponse['nodes'][number];

function toTopologyNode(node: SelfMemoryNode, hubIds: string[]): TopologyNode {
  // Calculate age from captured_at
  let ageSeconds = 0;
  if (node.captured_at) {
    try {
      const captured = new Date(node.captured_at);
      ageSeconds = Math.floor((Date.now() - captured.getTime()) / 1000);
    } catch {
      ageSeconds = 0;
    }
  }

  return {
    id: node.id,
    label: node.label,
    x: node.x,
    y: node.y,
    z: node.z,
    resolution: node.resolution,
    is_hot: hubIds.includes(node.id),
    access_count: 0, // Not available in SelfMemory response
    age_seconds: ageSeconds,
    content_preview: node.content?.slice(0, 200) || node.summary || null,
  };
}

// =============================================================================
// Types
// =============================================================================

export interface Brain2DProps {
  /** Topology data from AGENTESE self.memory.topology */
  topology: SelfMemoryTopologyResponse;
  /** Optional custom class name */
  className?: string;
  /** Optional observer for perception switching */
  observer?: string;
  /** Observer change callback */
  onObserverChange?: (observer: string) => void;
  /** Callback when topology should be refreshed */
  onRefresh?: () => void;
}

type DrawerContent = 'detail' | 'capture' | 'ghost' | 'settings';

// =============================================================================
// Constants - Living Earth Palette
// =============================================================================

const _BRAIN_COLORS = {
  primary: '#D4A574', // Amber - crystals
  healthy: '#4A6B4A', // Sage - healthy state
  hub: '#E8C4A0', // Honey - hot crystals
} as const;

// =============================================================================
// Main Component
// =============================================================================

export function Brain2D({
  topology,
  className = '',
  observer = 'technical',
  onObserverChange,
  onRefresh,
}: Brain2DProps) {
  const { density, isMobile } = useShell();
  const [selectedCrystal, setSelectedCrystal] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerContent, setDrawerContent] = useState<DrawerContent>('detail');
  const [searchQuery, setSearchQuery] = useState('');

  // Group nodes by category
  const categories = useMemo(() => {
    return groupByCategory(topology.nodes);
  }, [topology.nodes]);

  // Filter by search query
  const filteredCategories = useMemo(() => {
    if (!searchQuery.trim()) return categories;

    const query = searchQuery.toLowerCase();
    const filtered: Record<string, typeof topology.nodes> = {};

    for (const [category, crystals] of Object.entries(categories)) {
      const matchingCrystals = crystals.filter(
        (c) =>
          c.label?.toLowerCase().includes(query) ||
          c.summary?.toLowerCase().includes(query) ||
          c.content?.toLowerCase().includes(query)
      );
      if (matchingCrystals.length > 0) {
        filtered[category] = matchingCrystals;
      }
    }

    return filtered;
    // eslint-disable-next-line react-hooks/exhaustive-deps -- categories depends on topology
  }, [categories, searchQuery]);

  // Get selected crystal data
  const selectedCrystalData = useMemo(() => {
    if (!selectedCrystal) return null;
    return topology.nodes.find((n) => n.id === selectedCrystal) || null;
  }, [selectedCrystal, topology.nodes]);

  // Handlers
  const handleCrystalSelect = useCallback(
    (crystalId: string) => {
      setSelectedCrystal(crystalId === selectedCrystal ? null : crystalId);
      if (isMobile) {
        setDrawerContent('detail');
        setDrawerOpen(true);
      }
    },
    [selectedCrystal, isMobile]
  );

  const openCapture = useCallback(() => {
    setDrawerContent('capture');
    setDrawerOpen(true);
  }, []);

  const openGhost = useCallback(() => {
    setDrawerContent('ghost');
    setDrawerOpen(true);
  }, []);

  const handleCaptureSuccess = useCallback(() => {
    onRefresh?.();
    if (isMobile) {
      setDrawerOpen(false);
    }
  }, [onRefresh, isMobile]);

  const handleGhostSelect = useCallback(
    (crystalId: string) => {
      setSelectedCrystal(crystalId);
      if (isMobile) {
        setDrawerContent('detail');
      }
    },
    [isMobile]
  );

  // ==========================================================================
  // Mobile Layout
  // ==========================================================================
  if (isMobile) {
    return (
      <div className={`flex flex-col h-full bg-[#1a1a1a] ${className}`}>
        {/* Header */}
        <BrainHeader
          topology={topology}
          density={density}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          compact
        />

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto p-3">
          <CrystalTree
            categories={filteredCategories}
            selectedCrystal={selectedCrystal}
            onCrystalSelect={handleCrystalSelect}
            hubIds={topology.hub_ids}
            compact
          />
        </div>

        {/* Floating Actions */}
        <div className="absolute bottom-4 right-4 flex flex-col gap-2">
          <button
            onClick={openGhost}
            className="w-12 h-12 bg-[#4A3728] rounded-full flex items-center justify-center shadow-lg hover:bg-[#5A4738] transition-colors"
            title="Ghost Surface"
          >
            <Sparkles className="w-5 h-5 text-[#E8C4A0]" />
          </button>
          <button
            onClick={openCapture}
            className="w-12 h-12 bg-[#4A6B4A] rounded-full flex items-center justify-center shadow-lg hover:bg-[#5A7B5A] transition-colors"
            title="Capture Memory"
          >
            <span className="text-xl text-white">+</span>
          </button>
        </div>

        {/* Bottom Drawer */}
        <BottomDrawer
          isOpen={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          title={getDrawerTitle(drawerContent, selectedCrystalData)}
        >
          {drawerContent === 'detail' && selectedCrystalData && (
            <div className="p-4">
              <CrystalDetail
                crystal={selectedCrystalData}
                onClose={() => setDrawerOpen(false)}
                observer={observer}
                onObserverChange={onObserverChange || (() => {})}
                variant="panel"
              />
            </div>
          )}
          {drawerContent === 'capture' && (
            <div className="p-4">
              <CaptureForm onCapture={handleCaptureSuccess} compact />
            </div>
          )}
          {drawerContent === 'ghost' && (
            <div className="p-4">
              <GhostSurface onSurface={handleGhostSelect} compact />
            </div>
          )}
        </BottomDrawer>
      </div>
    );
  }

  // ==========================================================================
  // Desktop/Tablet Layout (ElasticSplit)
  // ==========================================================================
  return (
    <div className={`h-full bg-[#1a1a1a] flex flex-col ${className}`}>
      {/* Header */}
      <BrainHeader
        topology={topology}
        density={density}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      {/* Main Split View */}
      <ElasticSplit
        defaultRatio={0.65}
        collapseAtDensity="compact"
        collapsePriority="secondary"
        className="flex-1"
        primary={
          <div className="h-full overflow-y-auto p-4">
            <CrystalTree
              categories={filteredCategories}
              selectedCrystal={selectedCrystal}
              onCrystalSelect={handleCrystalSelect}
              hubIds={topology.hub_ids}
            />
          </div>
        }
        secondary={
          <div className="h-full overflow-y-auto border-l border-gray-700">
            {selectedCrystalData ? (
              <div className="p-4">
                <CrystalDetail
                  crystal={selectedCrystalData}
                  onClose={() => setSelectedCrystal(null)}
                  observer={observer}
                  onObserverChange={onObserverChange || (() => {})}
                  variant="panel"
                />
              </div>
            ) : (
              <SidePanel
                onCapture={handleCaptureSuccess}
                onGhostSelect={handleGhostSelect}
                density={density}
              />
            )}
          </div>
        }
      />
    </div>
  );
}

// =============================================================================
// Sub-Components
// =============================================================================

interface BrainHeaderProps {
  topology: SelfMemoryTopologyResponse;
  density: string;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  compact?: boolean;
}

function BrainHeader({
  topology,
  density,
  searchQuery,
  onSearchChange,
  compact = false,
}: BrainHeaderProps) {
  const isCompact = density === 'compact' || compact;
  const isHealthy = topology.stats.avg_resolution > 0.7;

  return (
    <header className="flex-shrink-0 bg-[#2a2a2a] border-b border-gray-700 px-4 py-3">
      <div className="flex items-center justify-between gap-4">
        {/* Left: Title */}
        <div className="flex items-center gap-3 flex-shrink-0">
          <Breathe intensity={isHealthy ? 0.3 : 0} speed="slow">
            <Brain className={`w-6 h-6 ${isHealthy ? 'text-[#D4A574]' : 'text-gray-400'}`} />
          </Breathe>
          <div>
            <h1 className={`font-semibold text-white ${isCompact ? 'text-base' : 'text-lg'}`}>
              Brain
            </h1>
            {!isCompact && <p className="text-xs text-gray-400">Living Memory Cartography</p>}
          </div>
        </div>

        {/* Center: Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search crystals..."
              className={`
                w-full pl-9 pr-3 bg-[#1a1a1a] border border-gray-700 rounded-lg
                text-white placeholder-gray-500 focus:outline-none focus:border-[#4A6B4A]
                ${isCompact ? 'py-1.5 text-sm' : 'py-2 text-sm'}
              `}
            />
          </div>
        </div>

        {/* Right: Stats */}
        <div className="flex items-center gap-4 flex-shrink-0">
          <StatBadge
            label="Crystals"
            value={String(topology.stats.concept_count)}
            color="text-[#D4A574]"
            isCompact={isCompact}
          />
          {!isCompact && (
            <>
              <StatBadge
                label="Connections"
                value={String(topology.stats.edge_count)}
                color="text-gray-300"
                isCompact={isCompact}
              />
              <StatBadge
                label="Resolution"
                value={`${Math.round(topology.stats.avg_resolution * 100)}%`}
                color={isHealthy ? 'text-green-400' : 'text-amber-400'}
                isCompact={isCompact}
              />
            </>
          )}
        </div>
      </div>
    </header>
  );
}

interface StatBadgeProps {
  label: string;
  value: string;
  color: string;
  isCompact: boolean;
}

function StatBadge({ label, value, color, isCompact }: StatBadgeProps) {
  return (
    <div className="text-right">
      <div
        className={`text-gray-500 ${isCompact ? 'text-[9px]' : 'text-[10px]'} uppercase tracking-wide`}
      >
        {label}
      </div>
      <div className={`font-semibold ${color} ${isCompact ? 'text-sm' : 'text-base'}`}>{value}</div>
    </div>
  );
}

interface SidePanelProps {
  onCapture: () => void;
  onGhostSelect: (crystalId: string) => void;
  density: string;
}

function SidePanel({ onCapture, onGhostSelect, density }: SidePanelProps) {
  const isCompact = density === 'compact';

  return (
    <div className="p-4 space-y-6">
      {/* Quick Capture */}
      <div>
        <h3 className={`font-medium text-white mb-3 ${isCompact ? 'text-sm' : 'text-base'}`}>
          Quick Capture
        </h3>
        <CaptureForm onCapture={onCapture} compact={isCompact} />
      </div>

      {/* Divider */}
      <hr className="border-gray-700" />

      {/* Ghost Surface */}
      <div>
        <h3 className={`font-medium text-white mb-3 ${isCompact ? 'text-sm' : 'text-base'}`}>
          Ghost Surface
        </h3>
        <GhostSurface onSurface={onGhostSelect} compact={isCompact} />
      </div>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getDrawerTitle(
  content: DrawerContent,
  crystal: SelfMemoryTopologyResponse['nodes'][number] | null
): string {
  switch (content) {
    case 'detail':
      return crystal?.label || 'Crystal Detail';
    case 'capture':
      return 'Capture Memory';
    case 'ghost':
      return 'Ghost Surface';
    case 'settings':
      return 'Settings';
    default:
      return 'Brain';
  }
}

export default Brain2D;
