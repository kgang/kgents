/**
 * Gestalt2D - Living Architecture Visualizer
 *
 * The 2D Renaissance implementation that replaces 1060 lines of Three.js
 * with ~400 lines of honest, breathing 2D visualization.
 *
 * Philosophy: "A codebase health dashboard should feel like a living garden,
 * not a 3D planetarium."
 *
 * @see spec/protocols/2d-renaissance.md - Phase 3: Gestalt2D
 * @see docs/skills/elastic-ui-patterns.md - Layout patterns
 */

import { useState, useCallback, useMemo } from 'react';
import { Network, Settings2 } from 'lucide-react';
import { useShell } from '@/shell';
import { ElasticSplit } from '@/components/elastic/ElasticSplit';
import { BottomDrawer } from '@/components/elastic/BottomDrawer';
import { Breathe } from '@/components/joy';
import type { WorldCodebaseTopologyResponse } from '@/api/types';
import type { FilterState, Density } from './types';
import { DEFAULT_FILTER_STATE, applyFilters } from './types';

// Sub-components
import { LayerCard } from './LayerCard';
import { ViolationFeed } from './ViolationFeed';
import { ModuleDetail } from './ModuleDetail';
import { FilterPanel } from './FilterPanel';
import { GestaltTree } from './GestaltTree';

// =============================================================================
// Types
// =============================================================================

export interface Gestalt2DProps {
  /** Topology data from AGENTESE world.codebase.topology */
  topology: WorldCodebaseTopologyResponse;
  /** Optional custom class name */
  className?: string;
  /** Optional observer for filter switching */
  observer?: string;
  /** Observer change callback */
  onObserverChange?: (observer: string) => void;
}

// =============================================================================
// Living Earth Palette
// =============================================================================

const LAYER_COLORS: Record<string, string> = {
  protocols: '#4A6B4A', // Sage - core protocols
  agents: '#6B8B6B', // Mint - agent infrastructure
  services: '#D4A574', // Amber - crown jewels
  models: '#AB9080', // Sand - data models
  default: '#6B4E3D', // Wood - unknown layers
};

// =============================================================================
// Main Component
// =============================================================================

export function Gestalt2D({
  topology,
  className = '',
  observer,
  onObserverChange,
}: Gestalt2DProps) {
  const { density, isMobile } = useShell();
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTER_STATE);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerContent, setDrawerContent] = useState<'filters' | 'detail'>('filters');
  const [viewMode, setViewMode] = useState<'tree' | 'grid'>('tree'); // Tree is now default!

  // Apply filters to modules
  const filteredNodes = useMemo(() => {
    return applyFilters(topology.nodes, filters);
  }, [topology.nodes, filters]);

  // Group by layer
  const layerGroups = useMemo(() => {
    const groups: Record<string, typeof topology.nodes> = {};
    for (const node of filteredNodes) {
      const layer = node.layer || 'unknown';
      if (!groups[layer]) groups[layer] = [];
      groups[layer].push(node);
    }
    return groups;
  }, [filteredNodes]);

  // Get violations
  const violations = useMemo(() => {
    return topology.links.filter((l) => l.is_violation);
  }, [topology.links]);

  // Get selected module data
  const selectedModuleData = useMemo(() => {
    if (!selectedModule) return null;
    return topology.nodes.find((n) => n.id === selectedModule) || null;
  }, [selectedModule, topology.nodes]);

  // Handlers
  const handleModuleSelect = useCallback(
    (moduleId: string) => {
      setSelectedModule(moduleId === selectedModule ? null : moduleId);
      if (isMobile) {
        setDrawerContent('detail');
        setDrawerOpen(true);
      }
    },
    [selectedModule, isMobile]
  );

  const handleFilterChange = useCallback((updates: Partial<FilterState>) => {
    setFilters((prev) => ({ ...prev, ...updates }));
  }, []);

  const openFilters = useCallback(() => {
    setDrawerContent('filters');
    setDrawerOpen(true);
  }, []);

  // ==========================================================================
  // Mobile Layout
  // ==========================================================================
  if (isMobile) {
    return (
      <div className={`flex flex-col h-full bg-[#1a1a1a] ${className}`}>
        {/* Header */}
        <GestaltHeader
          topology={topology}
          filteredCount={filteredNodes.length}
          violationCount={violations.length}
          density={density}
        />

        {/* Main Content */}
        {viewMode === 'tree' ? (
          <GestaltTree
            modules={filteredNodes}
            links={topology.links}
            selectedModule={selectedModule}
            onModuleSelect={handleModuleSelect}
            compact
            className="flex-1"
          />
        ) : (
          <div className="flex-1 overflow-y-auto p-3 space-y-4">
            {/* Layers */}
            {Object.entries(layerGroups)
              .sort((a, b) => b[1].length - a[1].length)
              .map(([layer, nodes]) => (
                <LayerCard
                  key={layer}
                  layer={layer}
                  nodes={nodes}
                  color={LAYER_COLORS[layer] || LAYER_COLORS.default}
                  selectedModule={selectedModule}
                  onModuleSelect={handleModuleSelect}
                  compact
                />
              ))}

            {/* Violations */}
            {violations.length > 0 && (
              <ViolationFeed violations={violations} maxDisplay={5} compact />
            )}
          </div>
        )}

        {/* Floating Filter Button */}
        <button
          onClick={openFilters}
          className="absolute bottom-4 right-4 w-12 h-12 bg-[#4A6B4A] rounded-full flex items-center justify-center shadow-lg"
        >
          <Settings2 className="w-5 h-5 text-white" />
        </button>

        {/* Bottom Drawer */}
        <BottomDrawer
          isOpen={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          title={
            drawerContent === 'filters' ? 'Filters' : selectedModuleData?.label || 'Module Detail'
          }
        >
          {drawerContent === 'filters' && (
            <div className="p-2">
              <FilterPanel
                topology={topology}
                filters={filters}
                onFiltersChange={handleFilterChange}
                onModuleSelect={(m) => handleModuleSelect(m.id)}
                density={density}
                isDrawer
                observer={observer}
                onObserverChange={onObserverChange}
              />
            </div>
          )}
          {drawerContent === 'detail' && selectedModuleData && (
            <div className="p-4">
              <ModuleDetail
                module={selectedModuleData}
                links={topology.links}
                onClose={() => setDrawerOpen(false)}
                compact
              />
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
      <GestaltHeader
        topology={topology}
        filteredCount={filteredNodes.length}
        violationCount={violations.length}
        density={density}
      />

      {/* Main Split View */}
      <ElasticSplit
        defaultRatio={0.72}
        collapseAtDensity="compact"
        collapsePriority="secondary"
        className="flex-1"
        primary={
          viewMode === 'tree' ? (
            <GestaltTree
              modules={filteredNodes}
              links={topology.links}
              selectedModule={selectedModule}
              onModuleSelect={handleModuleSelect}
              className="h-full"
            />
          ) : (
            <div className="h-full overflow-y-auto p-4 space-y-4">
              {/* Layer Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {Object.entries(layerGroups)
                  .sort((a, b) => b[1].length - a[1].length)
                  .map(([layer, nodes]) => (
                    <LayerCard
                      key={layer}
                      layer={layer}
                      nodes={nodes}
                      color={LAYER_COLORS[layer] || LAYER_COLORS.default}
                      selectedModule={selectedModule}
                      onModuleSelect={handleModuleSelect}
                    />
                  ))}
              </div>

              {/* Violations */}
              {violations.length > 0 && <ViolationFeed violations={violations} maxDisplay={10} />}
            </div>
          )
        }
        secondary={
          <div className="h-full overflow-y-auto border-l border-gray-700">
            {selectedModuleData ? (
              <div className="p-4">
                <ModuleDetail
                  module={selectedModuleData}
                  links={topology.links}
                  onClose={() => setSelectedModule(null)}
                />
              </div>
            ) : (
              <FilterPanel
                topology={topology}
                filters={filters}
                onFiltersChange={handleFilterChange}
                onModuleSelect={(m) => handleModuleSelect(m.id)}
                density={density}
                observer={observer}
                onObserverChange={onObserverChange}
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

interface HeaderProps {
  topology: WorldCodebaseTopologyResponse;
  filteredCount: number;
  violationCount: number;
  density: Density;
}

function GestaltHeader({ topology, filteredCount, violationCount, density }: HeaderProps) {
  const isCompact = density === 'compact';
  const isHealthy = violationCount === 0;

  return (
    <header className="flex-shrink-0 bg-[#2a2a2a] border-b border-gray-700 px-4 py-3">
      <div className="flex items-center justify-between">
        {/* Left: Title */}
        <div className="flex items-center gap-3">
          <Breathe intensity={isHealthy ? 0.3 : 0} speed="slow">
            <Network className={`w-6 h-6 ${isHealthy ? 'text-[#4A6B4A]' : 'text-amber-400'}`} />
          </Breathe>
          <div>
            <h1 className={`font-semibold text-white ${isCompact ? 'text-base' : 'text-lg'}`}>
              Gestalt
            </h1>
            <p className={`text-gray-400 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
              Living Architecture Visualizer
            </p>
          </div>
        </div>

        {/* Right: Stats */}
        <div className="flex items-center gap-4">
          <StatBadge
            label="Modules"
            value={`${filteredCount}/${topology.nodes.length}`}
            color="text-white"
            isCompact={isCompact}
          />
          <StatBadge
            label="Grade"
            value={topology.stats.overall_grade}
            color={getGradeColor(topology.stats.overall_grade)}
            isCompact={isCompact}
          />
          <StatBadge
            label="Violations"
            value={String(violationCount)}
            color={violationCount === 0 ? 'text-green-400' : 'text-amber-400'}
            isCompact={isCompact}
          />
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

function getGradeColor(grade: string): string {
  if (grade.startsWith('A')) return 'text-green-400';
  if (grade.startsWith('B')) return 'text-[#D4A574]';
  if (grade.startsWith('C')) return 'text-amber-400';
  return 'text-red-400';
}

export default Gestalt2D;
