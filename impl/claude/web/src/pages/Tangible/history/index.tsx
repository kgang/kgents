/**
 * Constitutional History - Main Entry Point
 *
 * Visualization showing how the kgents constitution has evolved over time.
 * Week 11-12 of the Self-Reflective OS.
 *
 * STARK BIOME aesthetic: 90% steel grays, 10% earned amber glow.
 *
 * Features:
 * - Timeline of constitutional changes
 * - Filterable by layer (L0-L4) and amendment type
 * - Zoomable timeline (day/week/month/all-time)
 * - Click any moment to see the state at that point
 */

import { memo, useState, useCallback, useMemo, useEffect } from 'react';
import { History, Filter, ChevronLeft, ChevronRight } from 'lucide-react';

import { ConstitutionalTimeline } from './ConstitutionalTimeline';
import { MomentDetail } from './MomentDetail';
import { LayerEvolution } from './LayerEvolution';
import { GenesisView } from './GenesisView';
import { DerivationTreeComparison } from './DerivationTreeComparison';

import type {
  ConstitutionalMoment,
  TimeZoom,
  HistoryFilter,
  HistoryState,
  LayerStability,
} from './types';

import './ConstitutionalHistory.css';

// =============================================================================
// Mock Data
// =============================================================================

/**
 * Mock constitutional moments for initial visualization.
 */
const MOCK_MOMENTS: ConstitutionalMoment[] = [
  {
    id: 'genesis',
    timestamp: '2025-10-01T00:00:00Z',
    type: 'genesis',
    title: 'Constitutional Genesis',
    description:
      'The 22 original Constitutional K-Blocks were established, forming the minimal kernel from which all else derives.',
    layer: 0,
    kblockPath: 'spec/constitution/',
    impact: 'constitutional',
    reasoning: 'Day Four: The constitution emerged from first principles.',
    author: 'kent',
  },
  {
    id: 'a1',
    timestamp: '2025-10-15T10:30:00Z',
    type: 'amendment',
    title: 'Refine COMPOSABLE Principle',
    description: 'Added minimal output principle for LLM agents to prevent context bloat.',
    layer: 0,
    kblockPath: 'spec/principles/composable.md',
    amendmentId: 'AMD-001',
    commitSha: 'a1b2c3d',
    impact: 'significant',
    reasoning:
      'LLM agents were generating excessive output, violating the composability principle.',
    author: 'claude',
    relatedMarks: ['mark-123', 'mark-124'],
  },
  {
    id: 'a2',
    timestamp: '2025-10-20T14:00:00Z',
    type: 'derivation_added',
    title: 'Add Witness Protocol',
    description:
      'Established the witnessing protocol as L2 derivation from ETHICAL and COMPOSABLE.',
    layer: 2,
    kblockPath: 'spec/protocols/witness.md',
    commitSha: 'e4f5g6h',
    impact: 'moderate',
    reasoning: 'Decision traces require formal witnessing to maintain accountability.',
    author: 'kent',
  },
  {
    id: 'a3',
    timestamp: '2025-11-05T09:15:00Z',
    type: 'amendment',
    title: 'Extend AGENTESE Path Structure',
    description: 'Formalized the five-context path structure: world, self, concept, void, time.',
    layer: 1,
    kblockPath: 'spec/protocols/agentese.md',
    amendmentId: 'AMD-002',
    commitSha: 'i7j8k9l',
    impact: 'significant',
    reasoning: 'The original three contexts were insufficient for temporal operations.',
    author: 'claude',
  },
  {
    id: 'a4',
    timestamp: '2025-11-12T16:45:00Z',
    type: 'drift_correction',
    title: 'Fix DI Container Semantics',
    description:
      'Corrected the dependency injection semantics to match Python signature conventions.',
    layer: 3,
    kblockPath: 'spec/architecture/di-container.md',
    commitSha: 'm0n1o2p',
    impact: 'moderate',
    reasoning: 'Implementation had drifted from specification; fail-fast semantics restored.',
    author: 'kent',
    relatedMarks: ['mark-456'],
  },
  {
    id: 'a5',
    timestamp: '2025-11-20T11:00:00Z',
    type: 'amendment',
    title: 'Add Joy-Inducing Principle',
    description: 'Elevated JOY_INDUCING from implicit value to explicit L1 principle.',
    layer: 1,
    kblockPath: 'spec/principles/joy-inducing.md',
    amendmentId: 'AMD-003',
    commitSha: 'q3r4s5t',
    impact: 'significant',
    reasoning: 'The Anti-Sausage Protocol revealed that joy was under-specified.',
    author: 'kent',
  },
  {
    id: 'a6',
    timestamp: '2025-12-01T08:30:00Z',
    type: 'derivation_added',
    title: 'Add Self-Reflective OS Spec',
    description: 'Created the Self-Reflective OS specification as L3 architecture document.',
    layer: 3,
    kblockPath: 'spec/architecture/self-reflective-os.md',
    commitSha: 'u6v7w8x',
    impact: 'moderate',
    reasoning: 'The system that watches itself think requires formal specification.',
    author: 'claude',
  },
  {
    id: 'a7',
    timestamp: '2025-12-21T10:00:00Z',
    type: 'amendment',
    title: 'Post-Extinction Architecture',
    description: 'Removed Gestalt, Park, Emergence; focused constitution on Brain, Town, Witness.',
    layer: 3,
    kblockPath: 'spec/architecture/',
    amendmentId: 'AMD-004',
    commitSha: 'y9z0a1b',
    impact: 'constitutional',
    reasoning: 'Extinction event: 52K lines archived for clarity and focus.',
    author: 'kent',
    relatedMarks: ['mark-789', 'mark-790'],
  },
];

/**
 * Mock layer stability data.
 */
const MOCK_LAYER_STABILITY: LayerStability[] = [
  {
    layer: 0,
    name: 'IRREDUCIBLE',
    kblockCount: 5,
    changeCount: 2,
    stability: 0.95,
    expectedStability: 0.98,
    lastChanged: '2025-10-15',
  },
  {
    layer: 1,
    name: 'PRIMITIVE',
    kblockCount: 8,
    changeCount: 3,
    stability: 0.88,
    expectedStability: 0.9,
    lastChanged: '2025-11-20',
  },
  {
    layer: 2,
    name: 'DERIVED',
    kblockCount: 12,
    changeCount: 5,
    stability: 0.75,
    expectedStability: 0.75,
    lastChanged: '2025-12-01',
  },
  {
    layer: 3,
    name: 'ARCHITECTURE',
    kblockCount: 15,
    changeCount: 8,
    stability: 0.6,
    expectedStability: 0.6,
    lastChanged: '2025-12-21',
  },
  {
    layer: 4,
    name: 'IMPLEMENTATION',
    kblockCount: 45,
    changeCount: 25,
    stability: 0.4,
    expectedStability: 0.4,
    lastChanged: '2025-12-25',
  },
];

// =============================================================================
// Time Zoom Controls
// =============================================================================

interface TimeZoomControlsProps {
  zoom: TimeZoom;
  onZoomChange: (zoom: TimeZoom) => void;
}

const TimeZoomControls = memo(function TimeZoomControls({
  zoom,
  onZoomChange,
}: TimeZoomControlsProps) {
  const zooms: TimeZoom[] = ['1D', '1W', '1M', 'ALL'];

  return (
    <div className="history-zoom-controls">
      {zooms.map((z) => (
        <button
          key={z}
          className={`history-zoom-controls__btn ${zoom === z ? 'history-zoom-controls__btn--active' : ''}`}
          onClick={() => onZoomChange(z)}
        >
          {z}
        </button>
      ))}
    </div>
  );
});

// =============================================================================
// Filter Controls
// =============================================================================

interface FilterControlsProps {
  filter: HistoryFilter;
  onFilterChange: (filter: HistoryFilter) => void;
  isExpanded: boolean;
  onToggleExpand: () => void;
}

const FilterControls = memo(function FilterControls({
  filter,
  onFilterChange,
  isExpanded,
  onToggleExpand,
}: FilterControlsProps) {
  const layers = [0, 1, 2, 3, 4];
  const types: ConstitutionalMoment['type'][] = [
    'genesis',
    'amendment',
    'derivation_added',
    'drift_correction',
  ];

  const toggleLayer = (layer: number) => {
    const current = filter.layers || [];
    const next = current.includes(layer) ? current.filter((l) => l !== layer) : [...current, layer];
    onFilterChange({ ...filter, layers: next.length > 0 ? next : undefined });
  };

  const toggleType = (type: ConstitutionalMoment['type']) => {
    const current = filter.types || [];
    const next = current.includes(type) ? current.filter((t) => t !== type) : [...current, type];
    onFilterChange({ ...filter, types: next.length > 0 ? next : undefined });
  };

  return (
    <div className="history-filter">
      <button
        className="history-filter__toggle"
        onClick={onToggleExpand}
        aria-expanded={isExpanded}
      >
        <Filter size={14} />
        <span>Filter</span>
        {isExpanded ? <ChevronLeft size={12} /> : <ChevronRight size={12} />}
      </button>

      {isExpanded && (
        <div className="history-filter__panel">
          <div className="history-filter__section">
            <span className="history-filter__label">Layers</span>
            <div className="history-filter__options">
              {layers.map((layer) => (
                <button
                  key={layer}
                  className={`history-filter__chip ${(filter.layers || []).includes(layer) ? 'history-filter__chip--active' : ''}`}
                  onClick={() => toggleLayer(layer)}
                  style={{ '--layer-color': `var(--layer-${layer})` } as React.CSSProperties}
                >
                  L{layer}
                </button>
              ))}
            </div>
          </div>

          <div className="history-filter__section">
            <span className="history-filter__label">Types</span>
            <div className="history-filter__options">
              {types.map((type) => (
                <button
                  key={type}
                  className={`history-filter__chip ${(filter.types || []).includes(type) ? 'history-filter__chip--active' : ''}`}
                  onClick={() => toggleType(type)}
                >
                  {type.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const ConstitutionalHistory = memo(function ConstitutionalHistory() {
  // State
  const [state, setState] = useState<HistoryState>({
    selectedMoment: null,
    timeZoom: 'ALL',
    filter: {},
    detailExpanded: false,
    comparisonMode: false,
  });

  const [filterExpanded, setFilterExpanded] = useState(false);
  const [showGenesis, setShowGenesis] = useState(false);
  const [leftCollapsed, setLeftCollapsed] = useState(false);

  // Filter moments
  const filteredMoments = useMemo(() => {
    let moments = [...MOCK_MOMENTS];

    if (state.filter.layers && state.filter.layers.length > 0) {
      moments = moments.filter((m) => state.filter.layers!.includes(m.layer));
    }

    if (state.filter.types && state.filter.types.length > 0) {
      moments = moments.filter((m) => state.filter.types!.includes(m.type));
    }

    if (state.filter.searchQuery) {
      const query = state.filter.searchQuery.toLowerCase();
      moments = moments.filter(
        (m) => m.title.toLowerCase().includes(query) || m.description.toLowerCase().includes(query)
      );
    }

    return moments.sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }, [state.filter]);

  // Get selected moment
  const selectedMoment = useMemo(() => {
    return state.selectedMoment
      ? MOCK_MOMENTS.find((m) => m.id === state.selectedMoment) || null
      : null;
  }, [state.selectedMoment]);

  // Handlers
  const handleMomentSelect = useCallback((id: string) => {
    setState((prev) => ({
      ...prev,
      selectedMoment: id,
      detailExpanded: true,
    }));
    if (id === 'genesis') {
      setShowGenesis(true);
    } else {
      setShowGenesis(false);
    }
  }, []);

  const handleZoomChange = useCallback((zoom: TimeZoom) => {
    setState((prev) => ({ ...prev, timeZoom: zoom }));
  }, []);

  const handleFilterChange = useCallback((filter: HistoryFilter) => {
    setState((prev) => ({ ...prev, filter }));
  }, []);

  const handleCloseDetail = useCallback(() => {
    setState((prev) => ({ ...prev, selectedMoment: null, detailExpanded: false }));
    setShowGenesis(false);
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') return;

      if (e.key === 'Escape') {
        handleCloseDetail();
      } else if (e.key === 'g') {
        handleMomentSelect('genesis');
      } else if (e.key === '[') {
        setLeftCollapsed((prev) => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleCloseDetail, handleMomentSelect]);

  return (
    <div className="constitutional-history">
      {/* Header */}
      <header className="constitutional-history__header">
        <div className="constitutional-history__title-area">
          <History size={18} className="constitutional-history__icon" />
          <h1 className="constitutional-history__title">Constitutional History</h1>
          <span className="constitutional-history__count">{filteredMoments.length} moments</span>
        </div>

        <div className="constitutional-history__controls">
          <FilterControls
            filter={state.filter}
            onFilterChange={handleFilterChange}
            isExpanded={filterExpanded}
            onToggleExpand={() => setFilterExpanded(!filterExpanded)}
          />
          <TimeZoomControls zoom={state.timeZoom} onZoomChange={handleZoomChange} />
        </div>
      </header>

      {/* Main Content */}
      <div className="constitutional-history__content">
        {/* Left Panel: Layer Evolution */}
        <aside
          className={`constitutional-history__left ${leftCollapsed ? 'constitutional-history__left--collapsed' : ''}`}
        >
          <button
            className="constitutional-history__collapse-btn"
            onClick={() => setLeftCollapsed(!leftCollapsed)}
            aria-label={leftCollapsed ? 'Expand panel' : 'Collapse panel'}
          >
            {leftCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
          </button>
          {!leftCollapsed && (
            <LayerEvolution
              layers={MOCK_LAYER_STABILITY}
              onLayerClick={(layer) => handleFilterChange({ ...state.filter, layers: [layer] })}
            />
          )}
        </aside>

        {/* Center: Timeline */}
        <main className="constitutional-history__center">
          <ConstitutionalTimeline
            moments={filteredMoments}
            selectedMoment={state.selectedMoment}
            onMomentSelect={handleMomentSelect}
            zoom={state.timeZoom}
          />
        </main>

        {/* Right Panel: Moment Detail or Genesis View */}
        <aside
          className={`constitutional-history__right ${state.detailExpanded ? 'constitutional-history__right--expanded' : ''}`}
        >
          {showGenesis && selectedMoment?.type === 'genesis' ? (
            <GenesisView onClose={handleCloseDetail} />
          ) : selectedMoment ? (
            <MomentDetail
              moment={selectedMoment}
              onClose={handleCloseDetail}
              onNavigateToKBlock={(path) => {
                // TODO: Integrate with Amendment Mode for viewing K-Blocks
                console.info('[ConstitutionalHistory] Navigate to K-Block:', path);
              }}
              onNavigateToCommit={(sha) => {
                // TODO: Integrate with Git timeline
                console.info('[ConstitutionalHistory] Navigate to commit:', sha);
              }}
            />
          ) : (
            <div className="constitutional-history__empty-detail">
              <p>Select a moment from the timeline to view details</p>
              <button
                className="constitutional-history__genesis-btn"
                onClick={() => handleMomentSelect('genesis')}
              >
                View Genesis
              </button>
            </div>
          )}
        </aside>
      </div>

      {/* Comparison Mode (when enabled) */}
      {state.comparisonMode && state.compareFrom && state.compareTo && (
        <DerivationTreeComparison
          fromTimestamp={state.compareFrom}
          toTimestamp={state.compareTo}
          onClose={() => setState((prev) => ({ ...prev, comparisonMode: false }))}
        />
      )}
    </div>
  );
});

export default ConstitutionalHistory;

// Re-export types and components
export * from './types';
export { ConstitutionalTimeline } from './ConstitutionalTimeline';
export { MomentDetail } from './MomentDetail';
export { LayerEvolution } from './LayerEvolution';
export { GenesisView } from './GenesisView';
export { DerivationTreeComparison } from './DerivationTreeComparison';
