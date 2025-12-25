/**
 * NavigationSidebar — Unified navigation across all surfaces
 *
 * "The persona is a garden, not a museum."
 *
 * Adapts content based on current surface:
 * - Editor: Recent nodes, trail breadcrumbs, quick actions
 * - Docs: Corpus overview, tier filters
 * - Chart: Constellation picker
 * - Feed: Memory categories
 */

import { memo, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FloatingSidebar } from '../elastic/FloatingSidebar';
import { FileText, BarChart3, Brain, Clock, ChevronRight, Layers, Compass } from 'lucide-react';
import './NavigationSidebar.css';

// =============================================================================
// Types
// =============================================================================

export type Surface = 'world.document' | 'self.director' | 'world.chart' | 'self.memory' | 'void.zero-seed';

interface NavigationSidebarProps {
  /** Current surface/page */
  surface: Surface;
  /** Whether sidebar is expanded */
  isExpanded: boolean;
  /** Toggle callback */
  onToggle: () => void;
  /** Bottom offset for sibling panels */
  bottomOffset?: string | number;
  /** Top offset for header */
  topOffset?: string | number;
  /** Recent nodes for editor surface */
  recentNodes?: Array<{ path: string; title: string }>;
  /** Trail breadcrumbs for editor surface */
  trail?: Array<{ path: string; title: string }>;
  /** Callback when a path is selected */
  onNavigatePath?: (path: string) => void;
}

// =============================================================================
// Surface Icons
// =============================================================================

const SURFACE_ICONS: Record<Surface, typeof FileText> = {
  'world.document': FileText,
  'self.director': Layers,
  'world.chart': BarChart3,
  'self.memory': Brain,
  'void.zero-seed': Compass,
};

const SURFACE_LABELS: Record<Surface, string> = {
  'world.document': 'Document',
  'self.director': 'Director',
  'world.chart': 'Chart',
  'self.memory': 'Memory',
  'void.zero-seed': 'Zero Seed',
};

// =============================================================================
// Sub-components
// =============================================================================

interface NavItemProps {
  icon: typeof FileText;
  label: string;
  href: string;
  isActive: boolean;
  shortcut?: string;
}

const NavItem = memo(function NavItem({ icon: Icon, label, href, isActive, shortcut }: NavItemProps) {
  const navigate = useNavigate();

  return (
    <button
      className={`nav-sidebar__item ${isActive ? 'nav-sidebar__item--active' : ''}`}
      onClick={() => navigate(href)}
      title={shortcut ? `${label} (${shortcut})` : label}
    >
      <Icon size={18} />
      <span className="nav-sidebar__item-label">{label}</span>
      {shortcut && <kbd className="nav-sidebar__item-shortcut">{shortcut}</kbd>}
    </button>
  );
});

interface RecentListProps {
  items: Array<{ path: string; title: string }>;
  onSelect: (path: string) => void;
  emptyMessage?: string;
}

const RecentList = memo(function RecentList({ items, onSelect, emptyMessage = 'No recent items' }: RecentListProps) {
  if (items.length === 0) {
    return <div className="nav-sidebar__empty">{emptyMessage}</div>;
  }

  return (
    <ul className="nav-sidebar__list">
      {items.map((item) => (
        <li key={item.path}>
          <button className="nav-sidebar__list-item" onClick={() => onSelect(item.path)} title={item.path}>
            <span className="nav-sidebar__list-item-title">{item.title || item.path.split('/').pop()}</span>
            <ChevronRight size={14} className="nav-sidebar__list-item-arrow" />
          </button>
        </li>
      ))}
    </ul>
  );
});

// =============================================================================
// Surface-specific Content
// =============================================================================

interface SurfaceContentProps {
  surface: Surface;
  recentNodes?: Array<{ path: string; title: string }>;
  trail?: Array<{ path: string; title: string }>;
  onNavigatePath?: (path: string) => void;
}

const SurfaceContent = memo(function SurfaceContent({
  surface,
  recentNodes = [],
  trail = [],
  onNavigatePath,
}: SurfaceContentProps) {
  const handleSelect = useCallback(
    (path: string) => {
      onNavigatePath?.(path);
    },
    [onNavigatePath]
  );

  switch (surface) {
    case 'world.document':
      return (
        <div className="nav-sidebar__surface-content">
          {/* Trail (breadcrumbs) */}
          {trail.length > 0 && (
            <section className="nav-sidebar__section">
              <h3 className="nav-sidebar__section-title">
                <Clock size={14} /> Trail
              </h3>
              <RecentList items={trail.slice(-5).reverse()} onSelect={handleSelect} emptyMessage="No trail" />
            </section>
          )}

          {/* Recent nodes */}
          <section className="nav-sidebar__section">
            <h3 className="nav-sidebar__section-title">
              <FileText size={14} /> Recent
            </h3>
            <RecentList items={recentNodes.slice(0, 8)} onSelect={handleSelect} emptyMessage="No recent nodes" />
          </section>

          {/* Quick Actions */}
          <section className="nav-sidebar__section">
            <h3 className="nav-sidebar__section-title">Quick Actions</h3>
            <div className="nav-sidebar__actions">
              <button className="nav-sidebar__action" title="Open file (:e)">
                <kbd>:e</kbd> Open
              </button>
              <button className="nav-sidebar__action" title="Save (:w)">
                <kbd>:w</kbd> Save
              </button>
            </div>
          </section>
        </div>
      );

    case 'self.director':
      return (
        <div className="nav-sidebar__surface-content">
          <section className="nav-sidebar__section">
            <h3 className="nav-sidebar__section-title">Document Canvas</h3>
            <div className="nav-sidebar__empty">
              <kbd>j</kbd>/<kbd>k</kbd> navigate<br />
              <kbd>/</kbd> search<br />
              <kbd>Enter</kbd> open
            </div>
          </section>
        </div>
      );

    case 'world.chart':
      return (
        <div className="nav-sidebar__surface-content">
          <section className="nav-sidebar__section">
            <h3 className="nav-sidebar__section-title">Constellations</h3>
            <div className="nav-sidebar__empty">Select a constellation from the chart view</div>
          </section>
        </div>
      );

    case 'self.memory':
      return (
        <div className="nav-sidebar__surface-content">
          <section className="nav-sidebar__section">
            <h3 className="nav-sidebar__section-title">Memory</h3>
            <div className="nav-sidebar__categories">
              <button className="nav-sidebar__category">Marks</button>
              <button className="nav-sidebar__category">Crystals</button>
              <button className="nav-sidebar__category">Evidence</button>
              <button className="nav-sidebar__category">Trails</button>
            </div>
          </section>
        </div>
      );

    case 'void.zero-seed':
      return (
        <div className="nav-sidebar__surface-content">
          <section className="nav-sidebar__section">
            <h3 className="nav-sidebar__section-title">Five Levels</h3>
            <div className="nav-sidebar__empty">
              <kbd>1</kbd> L1-L2 Axioms & Values<br />
              <kbd>2</kbd> L3-L4 Goals & Specs<br />
              <kbd>3</kbd> L5-L6 Actions & Reflections<br />
              <kbd>4</kbd> L7 Representation<br />
              <kbd>5</kbd> Visual Overview
            </div>
          </section>
        </div>
      );

    default:
      return null;
  }
});

// =============================================================================
// Main Component
// =============================================================================

export const NavigationSidebar = memo(function NavigationSidebar({
  surface,
  isExpanded,
  onToggle,
  bottomOffset = 0,
  topOffset = 0,
  recentNodes = [],
  trail = [],
  onNavigatePath,
}: NavigationSidebarProps) {
  const location = useLocation();

  // Determine active surface from AGENTESE route
  const getActiveRoute = (path: string): Surface => {
    if (path.startsWith('/world.document')) return 'world.document';
    if (path.startsWith('/self.director')) return 'self.director';
    if (path.startsWith('/world.chart')) return 'world.chart';
    if (path.startsWith('/self.memory')) return 'self.memory';
    if (path.startsWith('/void.zero-seed')) return 'void.zero-seed';
    // Legacy fallback (will be redirected)
    if (path.startsWith('/editor')) return 'world.document';
    if (path.startsWith('/director')) return 'self.director';
    if (path.startsWith('/chart')) return 'world.chart';
    if (path.startsWith('/brain') || path.startsWith('/feed')) return 'self.memory';
    if (path.startsWith('/proof-engine') || path.startsWith('/zero-seed')) return 'void.zero-seed';
    return 'world.document';
  };

  const activeSurface = getActiveRoute(location.pathname);

  return (
    <FloatingSidebar
      isExpanded={isExpanded}
      onToggle={onToggle}
      width={280}
      bottomOffset={bottomOffset}
      topOffset={topOffset}
      glass="standard"
      ariaLabel="Navigation sidebar"
      header={
        <div className="nav-sidebar__header">
          <span className="nav-sidebar__logo">◇ kgents</span>
        </div>
      }
      showCloseButton
    >
      <div className="nav-sidebar">
        {/* Surface navigation - AGENTESE paths only */}
        <nav className="nav-sidebar__nav">
          <NavItem icon={SURFACE_ICONS['world.document']} label={SURFACE_LABELS['world.document']} href="/world.document" isActive={activeSurface === 'world.document'} shortcut="⇧E" />
          <NavItem icon={SURFACE_ICONS['self.director']} label={SURFACE_LABELS['self.director']} href="/self.director" isActive={activeSurface === 'self.director'} shortcut="⇧D" />
          <NavItem icon={SURFACE_ICONS['world.chart']} label={SURFACE_LABELS['world.chart']} href="/world.chart" isActive={activeSurface === 'world.chart'} shortcut="⇧C" />
          <NavItem icon={SURFACE_ICONS['self.memory']} label={SURFACE_LABELS['self.memory']} href="/self.memory" isActive={activeSurface === 'self.memory'} shortcut="⇧M" />
          <NavItem icon={SURFACE_ICONS['void.zero-seed']} label={SURFACE_LABELS['void.zero-seed']} href="/zero-seed" isActive={activeSurface === 'void.zero-seed'} shortcut="⇧Z" />
        </nav>

        <div className="nav-sidebar__divider" />

        {/* Surface-specific content */}
        <SurfaceContent surface={surface} recentNodes={recentNodes} trail={trail} onNavigatePath={onNavigatePath} />

        {/* Footer hint */}
        <div className="nav-sidebar__footer">
          <kbd>Ctrl+b</kbd> toggle sidebar
        </div>
      </div>
    </FloatingSidebar>
  );
});

export default NavigationSidebar;
