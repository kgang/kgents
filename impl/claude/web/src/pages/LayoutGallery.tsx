/**
 * LayoutGallery: Layout Projection Functor demonstration.
 *
 * Demonstrates structural isomorphism between compact and spacious layouts.
 * The SAME content projects to DIFFERENT structures based on density,
 * but the INFORMATION is preserved.
 *
 * 8 Pilots:
 * 1. panel_sidebar - Panel in spacious mode (fixed sidebar)
 * 2. panel_drawer - Same panel in compact mode (bottom drawer)
 * 3. panel_isomorphism - Side-by-side showing structural isomorphism
 * 4. actions_toolbar - Actions as full toolbar (spacious)
 * 5. actions_fab - Same actions as FAB cluster (compact)
 * 6. split_resizable - ElasticSplit with drag handle (spacious)
 * 7. split_collapsed - Same split in stacked mode (compact)
 * 8. touch_targets - 48px minimum demonstration (physical constraints)
 *
 * @see spec/protocols/projection.md (Layout Projection section)
 * @see plans/web-refactor/layout-projection-functor.md
 */

import { useState } from 'react';
import {
  ElasticSplit,
  BottomDrawer,
  FloatingActions,
  useWindowLayout,
  PHYSICAL_CONSTRAINTS,
  LAYOUT_PRIMITIVES,
  type Density,
  type FloatingAction,
} from '@/components/elastic';

// =============================================================================
// Sample Data - Same content, different projections
// =============================================================================

const SAMPLE_PANEL_CONTENT = {
  title: 'Details Panel',
  items: [
    { id: '1', label: 'Status', value: 'Active' },
    { id: '2', label: 'Created', value: '2025-12-16' },
    { id: '3', label: 'Type', value: 'Agent' },
    { id: '4', label: 'Memory', value: '256 MB' },
  ],
};

const SAMPLE_ACTIONS: FloatingAction[] = [
  { id: 'scan', icon: '🔄', label: 'Rescan', onClick: () => {}, variant: 'primary' },
  { id: 'settings', icon: '⚙️', label: 'Settings', onClick: () => {} },
  { id: 'export', icon: '📤', label: 'Export', onClick: () => {} },
  { id: 'details', icon: '📋', label: 'Details', onClick: () => {} },
];

// =============================================================================
// Pilot Components
// =============================================================================

/**
 * Pilot 1: Panel in spacious mode (fixed sidebar)
 */
function PanelSidebarPilot() {
  return (
    <PilotContainer title="Panel (Spacious)" subtitle="Fixed sidebar layout">
      <div className="h-64 flex" style={{ minWidth: 600 }}>
        {/* Main content */}
        <div className="flex-1 bg-gray-800/50 p-4 flex items-center justify-center">
          <span className="text-gray-400">Main Content Area</span>
        </div>
        {/* Fixed sidebar */}
        <div className="w-64 border-l border-gray-700 bg-gray-900/50 p-4">
          <h3 className="font-semibold text-sm mb-3">{SAMPLE_PANEL_CONTENT.title}</h3>
          <div className="space-y-2">
            {SAMPLE_PANEL_CONTENT.items.map((item) => (
              <div key={item.id} className="text-xs">
                <span className="text-gray-500">{item.label}:</span>{' '}
                <span className="text-gray-300">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 2: Panel in compact mode (bottom drawer)
 */
function PanelDrawerPilot() {
  const [open, setOpen] = useState(false);

  return (
    <PilotContainer title="Panel (Compact)" subtitle="Bottom drawer layout">
      <div className="h-64 relative bg-gray-800/50" style={{ maxWidth: 400 }}>
        {/* Main content */}
        <div className="h-full flex items-center justify-center">
          <span className="text-gray-400">Main Content Area</span>
        </div>

        {/* Floating action to open drawer */}
        <FloatingActions
          actions={[
            {
              id: 'panel',
              icon: '📋',
              label: 'Open Panel',
              onClick: () => setOpen(true),
            },
          ]}
          position="bottom-right"
        />

        {/* Bottom drawer */}
        <BottomDrawer
          isOpen={open}
          onClose={() => setOpen(false)}
          title={SAMPLE_PANEL_CONTENT.title}
        >
          <div className="p-4 space-y-2">
            {SAMPLE_PANEL_CONTENT.items.map((item) => (
              <div key={item.id} className="text-sm">
                <span className="text-gray-500">{item.label}:</span>{' '}
                <span className="text-gray-300">{item.value}</span>
              </div>
            ))}
          </div>
        </BottomDrawer>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 3: Side-by-side isomorphism demonstration
 */
function PanelIsomorphismPilot() {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <PilotContainer
      title="Panel Isomorphism"
      subtitle="Same information, different structure"
      fullWidth
    >
      <div className="grid grid-cols-2 gap-8">
        {/* Spacious: Sidebar */}
        <div>
          <div className="text-xs text-gray-500 mb-2 flex items-center gap-2">
            <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400">Spacious</span>
            Fixed Sidebar
          </div>
          <div className="h-48 flex border border-gray-700 rounded overflow-hidden">
            <div className="flex-1 bg-gray-800/50 p-3 flex items-center justify-center text-sm text-gray-400">
              Main
            </div>
            <div className="w-40 border-l border-gray-700 bg-gray-900/50 p-3">
              <h4 className="text-xs font-semibold mb-2">{SAMPLE_PANEL_CONTENT.title}</h4>
              {SAMPLE_PANEL_CONTENT.items.slice(0, 2).map((item) => (
                <div key={item.id} className="text-[10px] text-gray-400">
                  {item.label}: {item.value}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Compact: Drawer */}
        <div>
          <div className="text-xs text-gray-500 mb-2 flex items-center gap-2">
            <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400">Compact</span>
            Bottom Drawer
          </div>
          <div className="h-48 border border-gray-700 rounded overflow-hidden relative bg-gray-800/50">
            <div className="h-full flex items-center justify-center text-sm text-gray-400">
              Main
            </div>
            <div className="absolute bottom-3 right-3">
              <button
                onClick={() => setDrawerOpen(true)}
                className="w-10 h-10 rounded-full bg-gray-700 hover:bg-gray-600 flex items-center justify-center"
              >
                📋
              </button>
            </div>
          </div>
          <BottomDrawer
            isOpen={drawerOpen}
            onClose={() => setDrawerOpen(false)}
            title={SAMPLE_PANEL_CONTENT.title}
          >
            <div className="p-3">
              {SAMPLE_PANEL_CONTENT.items.slice(0, 2).map((item) => (
                <div key={item.id} className="text-sm text-gray-400">
                  {item.label}: {item.value}
                </div>
              ))}
            </div>
          </BottomDrawer>
        </div>
      </div>
      <div className="mt-4 text-center text-xs text-gray-500">
        <strong>Structural Isomorphism:</strong> Same 4 data fields accessible in both layouts
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 4: Actions as toolbar (spacious)
 */
function ActionsToolbarPilot() {
  return (
    <PilotContainer title="Actions (Spacious)" subtitle="Full toolbar layout">
      <div className="h-32 flex flex-col" style={{ minWidth: 500 }}>
        {/* Toolbar */}
        <div className="flex gap-2 p-2 bg-gray-900/50 border-b border-gray-700">
          {SAMPLE_ACTIONS.map((action) => (
            <button
              key={action.id}
              className="px-3 py-1.5 rounded bg-gray-700 hover:bg-gray-600 text-sm flex items-center gap-2"
            >
              <span>{action.icon}</span>
              <span>{action.label}</span>
            </button>
          ))}
        </div>
        {/* Content */}
        <div className="flex-1 bg-gray-800/50 flex items-center justify-center">
          <span className="text-gray-400">Content Area</span>
        </div>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 5: Actions as FAB cluster (compact)
 */
function ActionsFabPilot() {
  return (
    <PilotContainer title="Actions (Compact)" subtitle="FAB cluster layout">
      <div className="h-48 relative bg-gray-800/50" style={{ maxWidth: 300 }}>
        {/* Content */}
        <div className="h-full flex items-center justify-center">
          <span className="text-gray-400">Content Area</span>
        </div>
        {/* FAB cluster */}
        <FloatingActions actions={SAMPLE_ACTIONS} position="bottom-right" />
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 6: Split with resizable divider (spacious)
 */
function SplitResizablePilot() {
  return (
    <PilotContainer title="Split (Spacious)" subtitle="Resizable divider">
      <div className="h-48" style={{ minWidth: 500 }}>
        <ElasticSplit
          direction="horizontal"
          defaultRatio={0.6}
          collapseAt={0} // Never collapse in this demo
          resizable={true}
          minPaneSize={100}
          primary={
            <div className="h-full bg-gray-800/50 flex items-center justify-center p-4">
              <div className="text-center">
                <div className="text-2xl mb-2">📊</div>
                <span className="text-gray-400 text-sm">Primary Pane</span>
                <p className="text-xs text-gray-500 mt-1">Drag divider to resize</p>
              </div>
            </div>
          }
          secondary={
            <div className="h-full bg-gray-900/50 flex items-center justify-center p-4">
              <div className="text-center">
                <div className="text-2xl mb-2">📋</div>
                <span className="text-gray-400 text-sm">Secondary Pane</span>
              </div>
            </div>
          }
        />
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 7: Split in collapsed/stacked mode (compact)
 */
function SplitCollapsedPilot() {
  return (
    <PilotContainer title="Split (Compact)" subtitle="Stacked layout">
      <div className="h-64" style={{ maxWidth: 300 }}>
        <div className="flex flex-col gap-4 h-full">
          <div className="flex-1 bg-gray-800/50 flex items-center justify-center rounded">
            <div className="text-center">
              <div className="text-xl mb-1">📊</div>
              <span className="text-gray-400 text-xs">Primary Pane</span>
            </div>
          </div>
          <div className="flex-1 bg-gray-900/50 flex items-center justify-center rounded">
            <div className="text-center">
              <div className="text-xl mb-1">📋</div>
              <span className="text-gray-400 text-xs">Secondary Pane</span>
            </div>
          </div>
        </div>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 8: 48px touch target demonstration
 */
function TouchTargetsPilot() {
  const sizes = [32, 44, 48, 56];

  return (
    <PilotContainer
      title="Touch Targets"
      subtitle={`Physical constraint: ${PHYSICAL_CONSTRAINTS.minTouchTarget}px minimum`}
      fullWidth
    >
      <div className="flex gap-8 justify-center items-end">
        {sizes.map((size) => {
          const isCompliant = size >= PHYSICAL_CONSTRAINTS.minTouchTarget;
          return (
            <div key={size} className="text-center">
              <div
                className={`rounded-full flex items-center justify-center mx-auto mb-2 transition-colors ${
                  isCompliant
                    ? 'bg-green-600/30 border-2 border-green-500'
                    : 'bg-red-600/30 border-2 border-red-500'
                }`}
                style={{ width: size, height: size }}
              >
                <span className="text-xs">{size >= 48 ? '✓' : '✗'}</span>
              </div>
              <div className="text-xs text-gray-400">{size}px</div>
              <div className={`text-[10px] ${isCompliant ? 'text-green-400' : 'text-red-400'}`}>
                {isCompliant ? 'Compliant' : 'Too small'}
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-4 text-center text-xs text-gray-500">
        <strong>Physical Constraint:</strong> Touch targets must be at least 48px regardless of
        density
      </div>
    </PilotContainer>
  );
}

// =============================================================================
// Helper Components
// =============================================================================

interface PilotContainerProps {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  fullWidth?: boolean;
}

function PilotContainer({ title, subtitle, children, fullWidth }: PilotContainerProps) {
  return (
    <div
      className={`rounded-lg border border-gray-700 bg-gray-900/30 overflow-hidden ${fullWidth ? '' : 'max-w-fit'}`}
    >
      <div className="px-4 py-2 bg-gray-800/50 border-b border-gray-700">
        <h3 className="font-medium text-sm">{title}</h3>
        <p className="text-xs text-gray-500">{subtitle}</p>
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
}

/**
 * Layout primitive behavior table
 */
function PrimitiveBehaviorTable() {
  const primitives = ['split', 'panel', 'actions'] as const;
  const densities: Density[] = ['compact', 'comfortable', 'spacious'];

  return (
    <div className="rounded-lg border border-gray-700 bg-gray-900/30 overflow-hidden">
      <div className="px-4 py-2 bg-gray-800/50 border-b border-gray-700">
        <h3 className="font-medium text-sm">Layout Primitive Behaviors</h3>
        <p className="text-xs text-gray-500">How each primitive transforms by density</p>
      </div>
      <div className="p-4 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b border-gray-700">
              <th className="pb-2 pr-4">Primitive</th>
              {densities.map((d) => (
                <th key={d} className="pb-2 px-3 capitalize">
                  {d}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {primitives.map((primitive) => (
              <tr key={primitive} className="border-b border-gray-800">
                <td className="py-2 pr-4 font-mono text-town-highlight">{primitive}</td>
                {densities.map((density) => (
                  <td key={density} className="py-2 px-3 text-gray-300">
                    {LAYOUT_PRIMITIVES[primitive][density].replace(/_/g, ' ')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// =============================================================================
// Main Page Component
// =============================================================================

export default function LayoutGallery() {
  const { density } = useWindowLayout();

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col bg-town-bg overflow-auto">
      {/* Header */}
      <div className="bg-town-surface/50 border-b border-town-accent/30 px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold">Layout Projection Gallery</h1>
            <p className="text-sm text-gray-400">
              Structural isomorphism: same content, different layouts
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">Current density:</span>
            <span className="px-2 py-0.5 rounded text-xs bg-town-highlight/30 text-town-highlight capitalize">
              {density}
            </span>
          </div>
        </div>
      </div>

      {/* Gallery content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Isomorphism section */}
          <section>
            <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
              Structural Isomorphism
            </h2>
            <div className="space-y-6">
              <PanelIsomorphismPilot />
            </div>
          </section>

          {/* Panel pilots */}
          <section>
            <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
              Panel Primitive
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <PanelSidebarPilot />
              <PanelDrawerPilot />
            </div>
          </section>

          {/* Actions pilots */}
          <section>
            <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
              Actions Primitive
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ActionsToolbarPilot />
              <ActionsFabPilot />
            </div>
          </section>

          {/* Split pilots */}
          <section>
            <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
              Split Primitive
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <SplitResizablePilot />
              <SplitCollapsedPilot />
            </div>
          </section>

          {/* Physical constraints */}
          <section>
            <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
              Physical Constraints
            </h2>
            <div className="space-y-6">
              <TouchTargetsPilot />
            </div>
          </section>

          {/* Behavior reference */}
          <section>
            <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
              Primitive Behavior Reference
            </h2>
            <PrimitiveBehaviorTable />
          </section>
        </div>
      </div>
    </div>
  );
}
