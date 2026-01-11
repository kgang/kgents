/**
 * AmendmentList - Left panel showing pending amendments
 *
 * Features:
 * - Filter by status (draft, proposed, under_review, approved)
 * - Show title, type icon, layer badge, status
 * - Click to select
 * - "New Amendment" button
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 */

import { memo, useMemo } from 'react';
import {
  Plus,
  FileText,
  Edit3,
  Trash2,
  RefreshCw,
  GitBranch,
  Layers,
  Search,
  Filter,
} from 'lucide-react';
import type { Amendment, AmendmentFilterStatus, AmendmentType, AmendmentFilters } from './types';
import {
  AMENDMENT_TYPE_LABELS,
  AMENDMENT_STATUS_LABELS,
  AMENDMENT_STATUS_COLORS,
  LAYER_COLORS,
} from './types';

// =============================================================================
// Types
// =============================================================================

export interface AmendmentListProps {
  amendments: Amendment[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onNewAmendment: () => void;
  filters: AmendmentFilters;
  onFilterChange: (filters: AmendmentFilters) => void;
  showFilters?: boolean;
  onToggleFilters?: () => void;
}

// =============================================================================
// Helpers
// =============================================================================

const getTypeIcon = (type: AmendmentType) => {
  switch (type) {
    case 'principle_addition':
      return <Plus size={12} />;
    case 'principle_modification':
      return <Edit3 size={12} />;
    case 'principle_removal':
      return <Trash2 size={12} />;
    case 'axiom_refinement':
      return <RefreshCw size={12} />;
    case 'derivation_correction':
      return <GitBranch size={12} />;
    case 'layer_restructure':
      return <Layers size={12} />;
    default:
      return <FileText size={12} />;
  }
};

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
};

// =============================================================================
// Subcomponents
// =============================================================================

interface FilterPanelProps {
  filters: AmendmentFilters;
  onFilterChange: (filters: AmendmentFilters) => void;
}

const FilterPanel = memo(function FilterPanel({ filters, onFilterChange }: FilterPanelProps) {
  const statusOptions: AmendmentFilterStatus[] = [
    'all',
    'draft',
    'proposed',
    'under_review',
    'approved',
    'rejected',
    'applied',
  ];

  return (
    <div className="amendment-list__filters">
      <div className="amendment-list__filter-group">
        <label className="amendment-list__filter-label">Status</label>
        <div className="amendment-list__filter-buttons">
          {statusOptions.map((status) => (
            <button
              key={status}
              className={`amendment-list__filter-btn ${
                filters.status === status ? 'amendment-list__filter-btn--active' : ''
              }`}
              onClick={() => onFilterChange({ ...filters, status })}
            >
              {status === 'all' ? 'All' : AMENDMENT_STATUS_LABELS[status]}
            </button>
          ))}
        </div>
      </div>

      <div className="amendment-list__filter-group">
        <label className="amendment-list__filter-label">Layer</label>
        <div className="amendment-list__filter-buttons">
          <button
            className={`amendment-list__filter-btn ${
              filters.layer === undefined ? 'amendment-list__filter-btn--active' : ''
            }`}
            onClick={() => onFilterChange({ ...filters, layer: undefined })}
          >
            Any
          </button>
          {[0, 1, 2, 3, 4].map((layer) => (
            <button
              key={layer}
              className={`amendment-list__filter-btn ${
                filters.layer === layer ? 'amendment-list__filter-btn--active' : ''
              }`}
              onClick={() => onFilterChange({ ...filters, layer: layer as 0 | 1 | 2 | 3 | 4 })}
              style={{
                borderLeftColor:
                  filters.layer === layer
                    ? LAYER_COLORS[layer as keyof typeof LAYER_COLORS]
                    : undefined,
              }}
            >
              L{layer}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
});

interface AmendmentCardProps {
  amendment: Amendment;
  isSelected: boolean;
  onClick: () => void;
}

const AmendmentCard = memo(function AmendmentCard({
  amendment,
  isSelected,
  onClick,
}: AmendmentCardProps) {
  const statusColor = AMENDMENT_STATUS_COLORS[amendment.status];
  const layerColor = LAYER_COLORS[amendment.targetLayer as keyof typeof LAYER_COLORS];

  return (
    <button
      className={`amendment-list__card ${isSelected ? 'amendment-list__card--selected' : ''}`}
      onClick={onClick}
      data-status={amendment.status}
    >
      <div className="amendment-list__card-header">
        <span
          className="amendment-list__card-type"
          title={AMENDMENT_TYPE_LABELS[amendment.amendmentType]}
        >
          {getTypeIcon(amendment.amendmentType)}
        </span>
        <span className="amendment-list__card-layer" style={{ color: layerColor }}>
          L{amendment.targetLayer}
        </span>
        <span className="amendment-list__card-status" style={{ color: statusColor }}>
          {AMENDMENT_STATUS_LABELS[amendment.status]}
        </span>
      </div>

      <div className="amendment-list__card-title">{amendment.title}</div>

      <div className="amendment-list__card-meta">
        <span className="amendment-list__card-target" title={amendment.targetKblock}>
          {amendment.targetKblockTitle || amendment.targetKblock.split('/').pop()}
        </span>
        <span className="amendment-list__card-date">{formatDate(amendment.createdAt)}</span>
      </div>

      {amendment.reviewNotes.length > 0 && (
        <div className="amendment-list__card-notes">
          <span className="amendment-list__card-notes-count">
            {amendment.reviewNotes.length} note{amendment.reviewNotes.length !== 1 ? 's' : ''}
          </span>
        </div>
      )}
    </button>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const AmendmentList = memo(function AmendmentList({
  amendments,
  selectedId,
  onSelect,
  onNewAmendment,
  filters,
  onFilterChange,
  showFilters = false,
  onToggleFilters,
}: AmendmentListProps) {
  // Filter amendments
  const filteredAmendments = useMemo(() => {
    return amendments.filter((amendment) => {
      // Status filter
      if (filters.status !== 'all' && amendment.status !== filters.status) {
        return false;
      }

      // Layer filter
      if (filters.layer !== undefined && amendment.targetLayer !== filters.layer) {
        return false;
      }

      // Search filter
      if (filters.searchQuery) {
        const query = filters.searchQuery.toLowerCase();
        const matchesTitle = amendment.title.toLowerCase().includes(query);
        const matchesDescription = amendment.description.toLowerCase().includes(query);
        const matchesTarget = amendment.targetKblock.toLowerCase().includes(query);
        if (!matchesTitle && !matchesDescription && !matchesTarget) {
          return false;
        }
      }

      // Type filter
      if (filters.amendmentType && amendment.amendmentType !== filters.amendmentType) {
        return false;
      }

      return true;
    });
  }, [amendments, filters]);

  // Group by status for display
  const groupedAmendments = useMemo(() => {
    const groups: Record<string, Amendment[]> = {
      under_review: [],
      proposed: [],
      draft: [],
      approved: [],
      applied: [],
      rejected: [],
      reverted: [],
    };

    filteredAmendments.forEach((amendment) => {
      if (groups[amendment.status]) {
        groups[amendment.status].push(amendment);
      }
    });

    return groups;
  }, [filteredAmendments]);

  const nonEmptyGroups = Object.entries(groupedAmendments).filter(
    ([, amendments]) => amendments.length > 0
  );

  return (
    <div className="amendment-list">
      <div className="amendment-list__header">
        <div className="amendment-list__header-title">
          <FileText size={14} />
          <span>Amendments</span>
        </div>
        <div className="amendment-list__header-actions">
          <button
            className="amendment-list__header-btn"
            onClick={onToggleFilters}
            title="Toggle filters"
          >
            <Filter size={14} />
          </button>
          <button
            className="amendment-list__new-btn"
            onClick={onNewAmendment}
            title="New Amendment (n)"
          >
            <Plus size={14} />
            <span>New</span>
          </button>
        </div>
      </div>

      <div className="amendment-list__search">
        <Search size={14} className="amendment-list__search-icon" />
        <input
          type="text"
          className="amendment-list__search-input"
          placeholder="Search amendments..."
          value={filters.searchQuery}
          onChange={(e) => onFilterChange({ ...filters, searchQuery: e.target.value })}
        />
      </div>

      {showFilters && <FilterPanel filters={filters} onFilterChange={onFilterChange} />}

      <div className="amendment-list__content">
        {filteredAmendments.length === 0 ? (
          <div className="amendment-list__empty">
            <FileText size={32} className="amendment-list__empty-icon" />
            <p className="amendment-list__empty-text">
              {filters.status === 'all' && !filters.searchQuery
                ? 'No amendments yet'
                : 'No matching amendments'}
            </p>
            <button className="amendment-list__empty-action" onClick={onNewAmendment}>
              <Plus size={14} />
              Create First Amendment
            </button>
          </div>
        ) : (
          nonEmptyGroups.map(([status, statusAmendments]) => (
            <div key={status} className="amendment-list__group">
              <div className="amendment-list__group-header">
                <span
                  className="amendment-list__group-dot"
                  style={{
                    backgroundColor:
                      AMENDMENT_STATUS_COLORS[status as keyof typeof AMENDMENT_STATUS_COLORS],
                  }}
                />
                <span className="amendment-list__group-label">
                  {AMENDMENT_STATUS_LABELS[status as keyof typeof AMENDMENT_STATUS_LABELS]}
                </span>
                <span className="amendment-list__group-count">{statusAmendments.length}</span>
              </div>
              <div className="amendment-list__group-items">
                {statusAmendments.map((amendment) => (
                  <AmendmentCard
                    key={amendment.id}
                    amendment={amendment}
                    isSelected={selectedId === amendment.id}
                    onClick={() => onSelect(amendment.id)}
                  />
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      <div className="amendment-list__footer">
        <span className="amendment-list__count">
          {filteredAmendments.length} of {amendments.length}
        </span>
        <kbd className="amendment-list__shortcut">n</kbd>
        <span className="amendment-list__shortcut-label">new</span>
      </div>
    </div>
  );
});

export default AmendmentList;
