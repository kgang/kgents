/**
 * CrystalTree - Hierarchical crystal visualization with categories
 *
 * Displays Brain crystals as an expandable tree organized by category
 * (first segment of label). Hot crystals (hubs) breathe with organic animation.
 *
 * Living Earth aesthetic: sage for categories, amber for crystals, breathing hubs.
 *
 * @see spec/protocols/2d-renaissance.md - Phase 4: Brain2D
 */

import { useState, useCallback, useMemo } from 'react';
import { ChevronDown, ChevronRight, Sparkle, Clock } from 'lucide-react';
import { Breathe } from '@/components/joy';
import type { SelfMemoryTopologyResponse } from '@/api/types';

// =============================================================================
// Types
// =============================================================================

type TopologyNode = SelfMemoryTopologyResponse['nodes'][number];

export interface CrystalTreeProps {
  /** Crystals grouped by category */
  categories: Record<string, TopologyNode[]>;
  /** Currently selected crystal ID */
  selectedCrystal?: string | null;
  /** Crystal selection callback */
  onCrystalSelect?: (crystalId: string) => void;
  /** Hub crystal IDs (hot/frequently accessed) */
  hubIds?: string[];
  /** Compact mode for mobile */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

export interface CategoryCardProps {
  /** Category name */
  category: string;
  /** Crystals in this category */
  crystals: TopologyNode[];
  /** Accent color */
  color: string;
  /** Currently selected crystal ID */
  selectedCrystal?: string | null;
  /** Crystal selection callback */
  onCrystalSelect?: (crystalId: string) => void;
  /** Hub crystal IDs */
  hubIds?: string[];
  /** Compact mode */
  compact?: boolean;
  /** Initially expanded */
  defaultExpanded?: boolean;
}

// =============================================================================
// Constants - Living Earth Palette
// =============================================================================

const BRAIN_COLORS = {
  // Category colors by theme
  categorical: '#4A6B4A', // Sage - theory/categorical concepts
  agent: '#8BAB8B', // Sprout - agent-related
  soul: '#AB9080', // Sand - k-gent/soul/self
  town: '#6B8B6B', // Mint - town/social
  service: '#D4A574', // Amber - services
  default: '#6B4E3D', // Wood - unknown categories

  // Crystal states
  crystal: '#D4A574', // Amber - main crystal color
  hub: '#E8C4A0', // Honey - hub crystals (hot)
  selected: '#4A6B4A', // Sage - selected state
} as const;

const CATEGORY_COLOR_MAP: Record<string, string> = {
  categorical: BRAIN_COLORS.categorical,
  category: BRAIN_COLORS.categorical,
  operad: BRAIN_COLORS.categorical,
  sheaf: BRAIN_COLORS.categorical,
  polynomial: BRAIN_COLORS.categorical,
  functor: BRAIN_COLORS.categorical,
  agent: BRAIN_COLORS.agent,
  poly: BRAIN_COLORS.agent,
  flux: BRAIN_COLORS.agent,
  soul: BRAIN_COLORS.soul,
  self: BRAIN_COLORS.soul,
  kgent: BRAIN_COLORS.soul,
  memory: BRAIN_COLORS.soul,
  town: BRAIN_COLORS.town,
  citizen: BRAIN_COLORS.town,
  coalition: BRAIN_COLORS.town,
  service: BRAIN_COLORS.service,
  brain: BRAIN_COLORS.service,
  gestalt: BRAIN_COLORS.service,
  forge: BRAIN_COLORS.service,
  park: BRAIN_COLORS.service,
};

const MAX_COLLAPSED_CRYSTALS = 5;
const MAX_EXPANDED_CRYSTALS = 20;

// =============================================================================
// Main Component
// =============================================================================

export function CrystalTree({
  categories,
  selectedCrystal,
  onCrystalSelect,
  hubIds = [],
  compact = false,
  className = '',
}: CrystalTreeProps) {
  // Sort categories by crystal count (descending)
  const sortedCategories = useMemo(() => {
    return Object.entries(categories).sort((a, b) => b[1].length - a[1].length);
  }, [categories]);

  // Calculate total crystals
  const totalCrystals = useMemo(() => {
    return Object.values(categories).reduce((sum, crystals) => sum + crystals.length, 0);
  }, [categories]);

  if (totalCrystals === 0) {
    return (
      <div className={`flex flex-col items-center justify-center py-12 text-gray-500 ${className}`}>
        <Sparkle className="w-12 h-12 mb-3 opacity-50" />
        <p className="text-sm">No crystals yet</p>
        <p className="text-xs mt-1">Capture your first memory to begin</p>
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {sortedCategories.map(([category, crystals], index) => (
        <CategoryCard
          key={category}
          category={category}
          crystals={crystals}
          color={getCategoryColor(category)}
          selectedCrystal={selectedCrystal}
          onCrystalSelect={onCrystalSelect}
          hubIds={hubIds}
          compact={compact}
          defaultExpanded={index === 0} // First category expanded by default
        />
      ))}
    </div>
  );
}

// =============================================================================
// Category Card
// =============================================================================

function CategoryCard({
  category,
  crystals,
  color,
  selectedCrystal,
  onCrystalSelect,
  hubIds = [],
  compact = false,
  defaultExpanded = false,
}: CategoryCardProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  // Check if any crystal in this category is a hub
  const hasHubs = useMemo(() => {
    return crystals.some((c) => hubIds.includes(c.id));
  }, [crystals, hubIds]);

  // Sort crystals: hubs first, then by captured_at (most recent first)
  const sortedCrystals = useMemo(() => {
    return [...crystals].sort((a, b) => {
      const aIsHub = hubIds.includes(a.id);
      const bIsHub = hubIds.includes(b.id);
      if (aIsHub && !bIsHub) return -1;
      if (!aIsHub && bIsHub) return 1;
      // Then by captured_at (most recent first)
      return (b.captured_at || '').localeCompare(a.captured_at || '');
    });
  }, [crystals, hubIds]);

  // Crystals to display
  const displayLimit = expanded ? MAX_EXPANDED_CRYSTALS : MAX_COLLAPSED_CRYSTALS;
  const displayedCrystals = sortedCrystals.slice(0, displayLimit);
  const hasMore = crystals.length > displayLimit;

  const toggleExpand = useCallback(() => {
    setExpanded((prev) => !prev);
  }, []);

  const handleCrystalClick = useCallback(
    (crystalId: string) => {
      onCrystalSelect?.(crystalId);
    },
    [onCrystalSelect]
  );

  // Calculate average resolution for this category
  const avgResolution = useMemo(() => {
    if (crystals.length === 0) return 0;
    return crystals.reduce((sum, c) => sum + (c.resolution || 0), 0) / crystals.length;
  }, [crystals]);

  return (
    <div
      className={`
        bg-[#2a2a2a] rounded-lg overflow-hidden
        border border-gray-700 hover:border-gray-600 transition-colors
      `}
    >
      {/* Header */}
      <button
        onClick={toggleExpand}
        className="w-full flex items-center justify-between p-3 hover:bg-[#333] transition-colors"
      >
        <div className="flex items-center gap-3">
          <Breathe intensity={hasHubs ? 0.25 : 0} speed="slow">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
          </Breathe>
          <div className="text-left">
            <div className="flex items-center gap-2">
              <span className={`font-medium text-white ${compact ? 'text-sm' : 'text-base'}`}>
                {formatCategoryName(category)}
              </span>
              <span className={`text-gray-500 ${compact ? 'text-xs' : 'text-sm'}`}>
                {crystals.length}
              </span>
            </div>
            {!compact && (
              <div className="text-xs text-gray-500 flex items-center gap-2">
                <span style={{ color }}>{Math.round(avgResolution * 100)}% resolution</span>
                {hasHubs && (
                  <span className="text-amber-400 flex items-center gap-1">
                    <Sparkle className="w-3 h-3" />
                    hub
                  </span>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Resolution bar */}
          <div className="w-12 h-1.5 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full transition-all duration-300"
              style={{
                width: `${avgResolution * 100}%`,
                backgroundColor: color,
              }}
            />
          </div>
          {expanded ? (
            <ChevronDown className="w-4 h-4 text-gray-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-400" />
          )}
        </div>
      </button>

      {/* Crystal List */}
      <div
        className={`
          transition-all duration-300 overflow-hidden
          ${expanded ? 'max-h-[600px]' : 'max-h-[180px]'}
        `}
      >
        <div className="px-3 pb-3 space-y-1">
          {displayedCrystals.map((crystal) => (
            <CrystalItem
              key={crystal.id}
              crystal={crystal}
              isSelected={crystal.id === selectedCrystal}
              isHub={hubIds.includes(crystal.id)}
              onClick={handleCrystalClick}
              compact={compact}
            />
          ))}
          {hasMore && (
            <button
              onClick={toggleExpand}
              className="text-xs text-gray-500 hover:text-gray-300 px-2 py-1"
            >
              {expanded ? `Show fewer` : `+${crystals.length - displayLimit} more crystals`}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Crystal Item
// =============================================================================

interface CrystalItemProps {
  crystal: TopologyNode;
  isSelected: boolean;
  isHub: boolean;
  onClick: (crystalId: string) => void;
  compact: boolean;
}

function CrystalItem({ crystal, isSelected, isHub, onClick, compact }: CrystalItemProps) {
  // Format age from captured_at
  const ageDisplay = useMemo(() => {
    if (!crystal.captured_at) return '';
    try {
      const captured = new Date(crystal.captured_at);
      const now = new Date();
      const seconds = Math.floor((now.getTime() - captured.getTime()) / 1000);
      if (seconds < 60) return `${seconds}s`;
      if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
      if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
      return `${Math.floor(seconds / 86400)}d`;
    } catch {
      return '';
    }
  }, [crystal.captured_at]);

  return (
    <button
      onClick={() => onClick(crystal.id)}
      className={`
        w-full flex items-start gap-2 px-2 py-1.5 rounded text-left
        transition-all duration-200 group
        ${isSelected ? 'bg-[#4A6B4A] ring-1 ring-[#8BAB8B]' : 'hover:bg-[#3a3a3a]'}
      `}
      title={crystal.summary || crystal.label}
    >
      {/* Crystal indicator */}
      <div className="flex-shrink-0 mt-1">
        <Breathe intensity={isHub ? 0.3 : 0} speed="fast">
          <span
            className={`inline-block ${compact ? 'text-[10px]' : 'text-xs'}`}
            style={{ color: isHub ? BRAIN_COLORS.hub : BRAIN_COLORS.crystal }}
          >
            {isHub ? '◆' : '◇'}
          </span>
        </Breathe>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span
            className={`
              truncate
              ${isSelected ? 'text-white' : 'text-gray-300'}
              ${compact ? 'text-xs' : 'text-sm'}
            `}
          >
            {crystal.label || crystal.id.slice(0, 12)}
          </span>
          {isHub && <Sparkle className="w-3 h-3 text-amber-400 flex-shrink-0" />}
        </div>

        {/* Summary preview (not in compact mode) */}
        {!compact && crystal.summary && (
          <p className="text-xs text-gray-500 truncate mt-0.5 group-hover:text-gray-400">
            {crystal.summary}
          </p>
        )}
      </div>

      {/* Age badge */}
      {ageDisplay && (
        <div
          className={`flex-shrink-0 flex items-center gap-1 text-gray-500 ${compact ? 'text-[10px]' : 'text-xs'}`}
        >
          <Clock className={`${compact ? 'w-2.5 h-2.5' : 'w-3 h-3'}`} />
          {ageDisplay}
        </div>
      )}

      {/* Resolution indicator */}
      <div
        className="flex-shrink-0 w-8 h-1 bg-gray-700 rounded-full overflow-hidden mt-2"
        title={`${Math.round(crystal.resolution * 100)}% resolution`}
      >
        <div
          className="h-full transition-all duration-300"
          style={{
            width: `${crystal.resolution * 100}%`,
            backgroundColor: isSelected ? '#8BAB8B' : BRAIN_COLORS.crystal,
          }}
        />
      </div>
    </button>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getCategoryColor(category: string): string {
  const normalizedCategory = category.toLowerCase();
  return CATEGORY_COLOR_MAP[normalizedCategory] || BRAIN_COLORS.default;
}

function formatCategoryName(category: string): string {
  // Handle common abbreviations
  const abbreviations: Record<string, string> = {
    kgent: 'K-gent',
    mgent: 'M-gent',
    dgent: 'D-gent',
    agentese: 'AGENTESE',
  };

  const lower = category.toLowerCase();
  if (abbreviations[lower]) return abbreviations[lower];

  // Capitalize first letter, preserve the rest
  return category.charAt(0).toUpperCase() + category.slice(1);
}

// =============================================================================
// Utility: Group nodes by category
// =============================================================================

/**
 * Group topology nodes by category (first segment of label).
 * Use this to prepare data for CrystalTree.
 */
export function groupByCategory(nodes: TopologyNode[]): Record<string, TopologyNode[]> {
  const groups: Record<string, TopologyNode[]> = {};

  for (const node of nodes) {
    // Extract category from label (e.g., "categorical.operads" → "categorical")
    const category = node.label?.split('.')[0]?.toLowerCase() || 'uncategorized';
    if (!groups[category]) groups[category] = [];
    groups[category].push(node);
  }

  return groups;
}

export default CrystalTree;
