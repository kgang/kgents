/**
 * NavigationSidebar — Unified navigation across all surfaces
 *
 * "The persona is a garden, not a museum."
 *
 * Adapts content based on current surface:
 * - Editor: Recent nodes, trail breadcrumbs, quick actions
 * - Ledger: Corpus overview, tier filters
 * - Chart: Constellation picker
 * - Brain: Memory categories
 */

import { memo, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FloatingSidebar } from '../elastic/FloatingSidebar';
import { FileText, GitBranch, BarChart3, Brain, Clock, ChevronRight } from 'lucide-react';
import './NavigationSidebar.css';

// =============================================================================
// Types
// =============================================================================

export type Surface = 'editor' | 'ledger' | 'chart' | 'brain';

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
  editor: FileText,
  ledger: GitBranch,
  chart: BarChart3,
  brain: Brain,
};

const SURFACE_LABELS: Record<Surface, string> = {
  editor: 'Editor',
  ledger: 'Ledger',
  chart: 'Chart',
  brain: 'Brain',
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
    case 'editor':
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

    case 'ledger':
      return (
        <div className="nav-sidebar__surface-content">
          <section className="nav-sidebar__section">
            <h3 className="nav-sidebar__section-title">Corpus Health</h3>
            {/* Stats sync with backend on ledger page load */}
            <div className="nav-sidebar__empty">View ledger to see corpus stats</div>
          </section>
        </div>
      );

    case 'chart':
      return (
        <div className="nav-sidebar__surface-content">
          <section className="nav-sidebar__section">
            <h3 className="nav-sidebar__section-title">Constellations</h3>
            <div className="nav-sidebar__empty">Select a constellation from the chart view</div>
          </section>
        </div>
      );

    case 'brain':
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

  // Determine active surface from route
  const getActiveRoute = (path: string): Surface => {
    if (path.startsWith('/editor')) return 'editor';
    if (path.startsWith('/ledger')) return 'ledger';
    if (path.startsWith('/chart')) return 'chart';
    if (path.startsWith('/brain')) return 'brain';
    return 'editor';
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
        {/* Surface navigation */}
        <nav className="nav-sidebar__nav">
          <NavItem icon={SURFACE_ICONS.editor} label={SURFACE_LABELS.editor} href="/editor" isActive={activeSurface === 'editor'} shortcut="⇧E" />
          <NavItem icon={SURFACE_ICONS.ledger} label={SURFACE_LABELS.ledger} href="/ledger" isActive={activeSurface === 'ledger'} shortcut="⇧L" />
          <NavItem icon={SURFACE_ICONS.chart} label={SURFACE_LABELS.chart} href="/chart" isActive={activeSurface === 'chart'} shortcut="⇧C" />
          <NavItem icon={SURFACE_ICONS.brain} label={SURFACE_LABELS.brain} href="/brain" isActive={activeSurface === 'brain'} shortcut="⇧B" />
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
