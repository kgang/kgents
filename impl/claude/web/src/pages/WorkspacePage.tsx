/**
 * WorkspacePage — THE page.
 *
 * SEVERE STARK: Dense, intense, no joy.
 * Everything else is a modal or panel within this page.
 *
 * Grounded in:
 * - spec/ui/severe-stark.md (Yahoo Japan Density)
 * - spec/ui/axioms.md (8 Axioms)
 *
 * Layout:
 * ┌─────────────────────────────────────────────────────────────────────┐
 * │ HEADER: logo | contexts | spacer | user | density | garden         │
 * ├──────┬────────────────────────────────────────────────────────┬─────┤
 * │ NAV  │                      K-BLOCK                           │META │
 * │      │                                                        │     │
 * │      │                                                        │COLL │
 * │      │                                                        │APSE │
 * │      │                                                        │     │
 * │      │                                                        │GARD │
 * │      │                                                        │EN   │
 * ├──────┴────────────────────────────────────────────────────────┴─────┤
 * │ STATUS: path | mode | garden% | slop | connection | hints          │
 * └─────────────────────────────────────────────────────────────────────┘
 */

import { useState, useCallback } from 'react';

// Hooks
import { useGardenState } from '../hooks/useGardenState';
import { useCollapseState } from '../hooks/useCollapseState';
import { useRealtimeStream } from '../hooks/useRealtimeStream';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';

// Components
import { WorkspaceHeader } from '../components/workspace/WorkspaceHeader';
import { NavigationPanel, createDefaultContexts } from '../components/navigation/NavigationPanel';
import { KBlockPanel, KBlockEmptyState } from '../components/kblock/KBlockPanel';
import { GardenPanel } from '../components/garden/GardenPanel';
import { CollapsePanel } from '../components/collapse/CollapsePanel';
import { StatusLine } from '../components/status/StatusLine';
import { HumanContainer } from '../components/containers/ContainerProvider';
import { HelpOverlay } from '../components/help';

// Types
import type { GardenItem } from '../types';

// Demo K-Block for initial state
const DEMO_KBLOCK = {
  id: 'demo-1',
  path: 'self.constitution.ethical',
  title: 'Ethical Principle',
  content: `# Ethical

> Agents augment human capability, never replace judgment.

## Core Tenets

- **Transparency**: Agents are honest about limitations and uncertainty
- **Privacy-respecting by default**: No data hoarding, no surveillance
- **Human agency preserved**: Critical decisions remain with humans
- **No deception**: Agents don't pretend to be human unless explicitly role-playing

## Anti-Patterns

- Agents that claim certainty they don't have
- Hidden data collection
- Agents that manipulate rather than assist
- "Trust me" without explanation`,
  provenance: {
    author: 'kent' as const,
    confidence: 1.0,
    reviewed: true,
    sloppification_risk: 0,
    evidence: ['Human authored'],
    created_at: new Date().toISOString(),
  },
  lifecycle: {
    stage: 'bloom' as const,
    lastActivity: new Date().toISOString(),
    daysSinceActivity: 0,
  },
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

/**
 * The unified workspace page.
 */
export function WorkspacePage() {
  // State
  const [currentPath, setCurrentPath] = useState('self.constitution');
  const [selectedKBlock] = useState(DEMO_KBLOCK);
  const [navItems, setNavItems] = useState(() => createDefaultContexts());
  const [density] = useState<'compact' | 'comfortable' | 'spacious'>('compact');
  const [mode, setMode] = useState<'navigate' | 'edit' | 'witness'>('navigate');
  const [isEditing, setIsEditing] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

  // Data hooks
  const { state: gardenState, tendItem, compostItem, refresh: refreshGarden } = useGardenState();
  const { state: collapseState } = useCollapseState(selectedKBlock?.id || null);
  const { status: connectionStatus } = useRealtimeStream('/api/witness/stream', {
    // Refresh garden state when K-Block changes occur
    onKBlockChange: () => refreshGarden(),
    // Could add more handlers here for mark_created, constitutional_evaluated, etc.
  });

  // Keyboard shortcuts (Kent's Decision #6)
  useKeyboardShortcuts({
    onManifest: () => {
      // TODO: Show K-Block manifest panel
      console.info('[shortcut] manifest: show K-Block structure');
    },
    onWitness: () => {
      setMode('witness');
      // TODO: Open witness trail panel
      console.info('[shortcut] witness: entering witness mode');
    },
    onTithe: () => {
      // Tend the current K-Block
      if (selectedKBlock) {
        tendItem(selectedKBlock.path);
        console.info('[shortcut] tithe: tending', selectedKBlock.path);
      }
    },
    onRefine: () => {
      setMode('edit');
      setIsEditing(true);
      console.info('[shortcut] refine: entering edit mode');
    },
    onDefine: () => {
      // TODO: Open new K-Block creation dialog
      console.info('[shortcut] define: create new K-Block');
    },
    onSip: () => {
      // TODO: Quick peek / preview mode
      console.info('[shortcut] sip: quick view');
    },
    onHelp: () => {
      setShowHelp(true);
    },
    onEscape: () => {
      setMode('navigate');
      setIsEditing(false);
      setShowHelp(false);
    },
  });

  // Handlers
  const handleNavigate = useCallback((path: string) => {
    setCurrentPath(path);
    // In a real app, would fetch K-Block for this path
  }, []);

  const handleToggleNav = useCallback((path: string) => {
    setNavItems((items) =>
      items.map((item) => (item.path === path ? { ...item, expanded: !item.expanded } : item))
    );
  }, []);

  const handleSelectItem = useCallback((item: GardenItem) => {
    setCurrentPath(item.path);
    // In a real app, would fetch K-Block for this path
  }, []);

  const handleTendItem = useCallback(
    (item: GardenItem) => {
      tendItem(item.path);
    },
    [tendItem]
  );

  const handleCompostItem = useCallback(
    (item: GardenItem) => {
      compostItem(item.path);
    },
    [compostItem]
  );

  const handleTendKBlock = useCallback(() => {
    if (selectedKBlock) {
      tendItem(selectedKBlock.path);
    }
  }, [selectedKBlock, tendItem]);

  // Garden health for header
  const gardenHealth = gardenState?.health ?? 1;

  // Collapse state with defaults
  const displayCollapseState = collapseState || {
    typescript: { status: 'pass' as const },
    tests: { status: 'pass' as const },
    constitution: { score: 6.5, principles: {} },
    galois: { loss: 0.15, tier: 'CATEGORICAL' as const },
    overallSlop: 'low' as const,
    evidence: [],
  };

  return (
    <div className="workspace-page">
      {/* Header */}
      <WorkspaceHeader
        currentPath={currentPath}
        density={density}
        gardenHealth={gardenHealth}
        onNavigate={handleNavigate}
      />

      {/* Main content */}
      <main className="workspace-main">
        {/* Navigation panel (left) */}
        <NavigationPanel
          items={navItems}
          selectedPath={currentPath}
          onSelect={handleNavigate}
          onToggle={handleToggleNav}
        />

        {/* K-Block content (center) */}
        <div className="workspace-content">
          {selectedKBlock ? (
            <HumanContainer>
              <KBlockPanel
                kblock={selectedKBlock}
                collapseState={displayCollapseState}
                isEditing={isEditing}
                onTend={handleTendKBlock}
              />
            </HumanContainer>
          ) : (
            <KBlockEmptyState />
          )}
        </div>

        {/* Right sidebar */}
        <aside className="workspace-sidebar">
          {/* Collapse panel */}
          <CollapsePanel state={displayCollapseState} compact />

          {/* Garden panel */}
          {gardenState && (
            <GardenPanel
              state={gardenState}
              onSelectItem={handleSelectItem}
              onTendItem={handleTendItem}
              onCompostItem={handleCompostItem}
            />
          )}
        </aside>
      </main>

      {/* Status line */}
      <StatusLine
        currentPath={currentPath}
        gardenState={gardenState || undefined}
        collapseState={displayCollapseState}
        connectionStatus={connectionStatus}
        mode={mode}
        showHints
      />

      {/* Help overlay (shown on '?' key) */}
      {showHelp && <HelpOverlay onClose={() => setShowHelp(false)} />}
    </div>
  );
}

export default WorkspacePage;
