/**
 * TangibleSurface - The Self-Reflective OS Interface
 *
 * "The system that watches itself think, and thinks about its watching."
 *
 * Three modes:
 * - REFLECT: Constitutional self-reflection (Week 1-4 focus)
 * - CREATE: K-Games Studio (MechanicComposer + GameKernel + EvidenceStream)
 * - ACTUALIZE: Pilot Actualization (placeholder)
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 *
 * @see plans/self-reflective-os/
 */

import { memo, useState, useMemo, useEffect, useCallback } from 'react';
import {
  Eye,
  Sparkles,
  Zap,
  GitBranch,
  GitCommit,
  Layers,
  Clock,
  Bookmark,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

import './TangibleSurface.css';

// Reflect Mode imports
import {
  CodebaseExplorer,
  FileInspector,
  GitTimeline,
  DecisionTimeline as EnhancedDecisionTimeline,
  KBlockInspector,
  DerivationChainViewer,
  type RightPanelTab,
  type CodebaseFilter,
  type CommitFilter,
  type KBlockInfo,
  type DerivationChain,
} from './reflect';
import { GameKernelEditor } from './GameKernelEditor';
import { MechanicComposer } from './MechanicComposer';
import { EvidenceStream } from './EvidenceStream';
import {
  createDefaultGameKernel,
  createSampleMechanics,
  type GameKernel,
  type MechanicComposition,
  type GameOperad,
  type EvidenceFilter,
} from './types';

// Actualize Mode imports
import { PilotGallery } from './PilotGallery';
import { AxiomDiscoveryFlow } from './AxiomDiscoveryFlow';
import { ActivePilot } from './ActivePilot';
import { CompositionChain } from './CompositionChain';
import type {
  PilotMetadata,
  CustomPilot,
  PilotTier,
  EndeavorAxioms,
  WitnessMark,
  WitnessTrace,
  Crystal,
  DerivationLink,
  MarkContext,
} from './actualize-types';
import { PILOTS } from './actualize-types';

// =============================================================================
// Types
// =============================================================================

type TangibleMode = 'reflect' | 'create' | 'actualize';

interface DecisionEntry {
  id: string;
  timestamp: Date;
  topic: string;
  synthesis: string;
  kentView?: string;
  claudeView?: string;
}

interface ConstitutionNode {
  id: string;
  layer: 0 | 1 | 2 | 3;
  title: string;
  description?: string;
  children?: string[];
}

// Future: DerivationInfo for detailed derivation tracking
// interface DerivationInfo {
//   sourceId: string;
//   derivedFrom: string[];
//   loss: number;
//   path: string;
// }

// =============================================================================
// Constants
// =============================================================================

const MODE_CONFIG = {
  reflect: {
    label: 'Reflect',
    icon: Eye,
    description: 'Constitutional self-reflection',
    shortcut: 'R',
  },
  create: {
    label: 'Create',
    icon: Sparkles,
    description: 'K-Games Studio',
    shortcut: 'C',
  },
  actualize: {
    label: 'Actualize',
    icon: Zap,
    description: 'Pilot Actualization',
    shortcut: 'A',
  },
} as const;

// Layer colors from the Constitutional hierarchy
const LAYER_COLORS = {
  0: '#c4a77d', // L0: AXIOM (amber/honey glow)
  1: '#6b8b6b', // L1: VALUE (sage green)
  2: '#8b7355', // L2: SPEC (earth brown)
  3: '#a39890', // L3: TUNING (warm steel)
} as const;

// Mock data for initial implementation
const MOCK_CONSTITUTION: ConstitutionNode[] = [
  {
    id: 'axiom-1',
    layer: 0,
    title: 'COMPOSABLE',
    description: 'Agents are morphisms in a category',
  },
  {
    id: 'axiom-2',
    layer: 0,
    title: 'ETHICAL',
    description: 'Augment human capability, never replace judgment',
  },
  {
    id: 'axiom-3',
    layer: 0,
    title: 'TASTEFUL',
    description: 'Each agent serves a clear, justified purpose',
  },
  {
    id: 'value-1',
    layer: 1,
    title: 'JOY_INDUCING',
    description: 'Delight in interaction',
    children: ['axiom-3'],
  },
  {
    id: 'value-2',
    layer: 1,
    title: 'HETERARCHICAL',
    description: 'Agents exist in flux, not fixed hierarchy',
    children: ['axiom-1'],
  },
  {
    id: 'spec-1',
    layer: 2,
    title: 'AGENTESE',
    description: 'The verb-first ontology',
    children: ['value-2'],
  },
  {
    id: 'spec-2',
    layer: 2,
    title: 'PolyAgent',
    description: 'State machine with mode-dependent inputs',
    children: ['axiom-1'],
  },
  {
    id: 'tuning-1',
    layer: 3,
    title: 'witness.md',
    description: 'Witnessing protocol spec',
    children: ['spec-1', 'axiom-2'],
  },
];

const MOCK_DECISIONS: DecisionEntry[] = [
  {
    id: 'dec-1',
    timestamp: new Date('2025-12-21'),
    topic: 'Post-Extinction Architecture',
    synthesis: 'Remove Gestalt, Park, Emergence; focus on Brain, Town, Witness',
    kentView: 'Keep everything for flexibility',
    claudeView: 'Prune ruthlessly for clarity',
  },
  {
    id: 'dec-2',
    timestamp: new Date('2025-12-20'),
    topic: 'AGENTESE Path Structure',
    synthesis: 'Use dots for context, slashes only for file paths',
    kentView: 'Consistent dot notation',
    claudeView: 'Agreed - dots are cleaner',
  },
  {
    id: 'dec-3',
    timestamp: new Date('2025-12-19'),
    topic: 'DI Container Pattern',
    synthesis: 'Fail-fast at import time for required dependencies',
    kentView: 'Graceful fallbacks',
    claudeView: 'Strict validation catches bugs earlier',
  },
];

// =============================================================================
// Subcomponents: Mode Selector
// =============================================================================

interface ModeSelectorProps {
  mode: TangibleMode;
  onChange: (mode: TangibleMode) => void;
}

const ModeSelector = memo(function ModeSelector({ mode, onChange }: ModeSelectorProps) {
  return (
    <div className="tangible-mode-selector" role="tablist">
      {(Object.entries(MODE_CONFIG) as [TangibleMode, typeof MODE_CONFIG.reflect][]).map(
        ([key, config]) => {
          const Icon = config.icon;
          const isActive = mode === key;

          return (
            <button
              key={key}
              className={`tangible-mode-selector__btn ${isActive ? 'tangible-mode-selector__btn--active' : ''}`}
              onClick={() => onChange(key)}
              role="tab"
              aria-selected={isActive}
              title={`${config.label} (${config.shortcut})`}
            >
              <Icon size={16} className="tangible-mode-selector__icon" />
              <span className="tangible-mode-selector__label">{config.label}</span>
              <kbd className="tangible-mode-selector__shortcut">{config.shortcut}</kbd>
            </button>
          );
        }
      )}
    </div>
  );
});

// =============================================================================
// Subcomponents: Constitution Tree (Left Panel)
// =============================================================================

interface ConstitutionTreeProps {
  nodes: ConstitutionNode[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

const ConstitutionTree = memo(function ConstitutionTree({
  nodes,
  selectedId,
  onSelect,
}: ConstitutionTreeProps) {
  // Group nodes by layer
  const grouped = useMemo(() => {
    const layers: Record<number, ConstitutionNode[]> = { 0: [], 1: [], 2: [], 3: [] };
    nodes.forEach((node) => {
      layers[node.layer].push(node);
    });
    return layers;
  }, [nodes]);

  const layerNames = ['AXIOM', 'VALUE', 'SPEC', 'TUNING'];

  return (
    <div className="constitution-tree">
      <div className="constitution-tree__header">
        <Layers size={14} />
        <span className="constitution-tree__title">Constitution</span>
      </div>

      <div className="constitution-tree__layers">
        {[0, 1, 2, 3].map((layer) => {
          const layerNodes = grouped[layer];
          if (layerNodes.length === 0) return null;

          return (
            <div key={layer} className="constitution-tree__layer">
              <div
                className="constitution-tree__layer-header"
                style={{ borderLeftColor: LAYER_COLORS[layer as 0 | 1 | 2 | 3] }}
              >
                <span className="constitution-tree__layer-badge">L{layer}</span>
                <span className="constitution-tree__layer-name">{layerNames[layer]}</span>
                <span className="constitution-tree__layer-count">{layerNodes.length}</span>
              </div>

              <div className="constitution-tree__nodes">
                {layerNodes.map((node) => (
                  <button
                    key={node.id}
                    className={`constitution-tree__node ${selectedId === node.id ? 'constitution-tree__node--selected' : ''}`}
                    onClick={() => onSelect(node.id)}
                    style={{ borderLeftColor: LAYER_COLORS[node.layer] }}
                  >
                    <span className="constitution-tree__node-title">{node.title}</span>
                    {node.children && node.children.length > 0 && (
                      <span className="constitution-tree__node-children">
                        <GitBranch size={10} /> {node.children.length}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
});

// =============================================================================
// Subcomponents: Codebase Graph (Center Panel - Main)
// =============================================================================

interface CodebaseGraphProps {
  nodes: ConstitutionNode[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

const CodebaseGraph = memo(function CodebaseGraph({
  nodes,
  selectedId,
  onSelect,
}: CodebaseGraphProps) {
  // Simple grid layout for now; can upgrade to force-directed later
  return (
    <div className="codebase-graph">
      <div className="codebase-graph__header">
        <span className="codebase-graph__title">Codebase as Hypergraph</span>
        <span className="codebase-graph__subtitle">impl/claude/* derived from principles</span>
      </div>

      <div className="codebase-graph__canvas">
        {nodes.map((node) => (
          <button
            key={node.id}
            className={`codebase-graph__node ${selectedId === node.id ? 'codebase-graph__node--selected' : ''}`}
            onClick={() => onSelect(node.id)}
            style={
              {
                '--node-color': LAYER_COLORS[node.layer],
              } as React.CSSProperties
            }
          >
            <span className="codebase-graph__node-badge">L{node.layer}</span>
            <span className="codebase-graph__node-title">{node.title}</span>
          </button>
        ))}
      </div>
    </div>
  );
});

// =============================================================================
// Subcomponents: Derivation View (Center Panel - Detail)
// =============================================================================

interface DerivationViewProps {
  node: ConstitutionNode | null;
  allNodes: ConstitutionNode[];
}

const DerivationView = memo(function DerivationView({ node, allNodes }: DerivationViewProps) {
  if (!node) {
    return (
      <div className="derivation-view derivation-view--empty">
        <p className="derivation-view__placeholder">Select a node to view its derivation chain</p>
      </div>
    );
  }

  // Find parent nodes (what this derives from)
  const parents = node.children ? allNodes.filter((n) => node.children?.includes(n.id)) : [];

  // Find child nodes (what derives from this)
  const children = allNodes.filter((n) => n.children?.includes(node.id));

  return (
    <div className="derivation-view">
      <div className="derivation-view__header">
        <span className="derivation-view__layer" style={{ color: LAYER_COLORS[node.layer] }}>
          L{node.layer}
        </span>
        <span className="derivation-view__title">{node.title}</span>
      </div>

      {node.description && <p className="derivation-view__description">{node.description}</p>}

      {parents.length > 0 && (
        <div className="derivation-view__section">
          <span className="derivation-view__label">Derives From</span>
          <div className="derivation-view__links">
            {parents.map((parent) => (
              <span
                key={parent.id}
                className="derivation-view__link"
                style={{ borderLeftColor: LAYER_COLORS[parent.layer] }}
              >
                {parent.title}
              </span>
            ))}
          </div>
        </div>
      )}

      {children.length > 0 && (
        <div className="derivation-view__section">
          <span className="derivation-view__label">Grounded By</span>
          <div className="derivation-view__links">
            {children.map((child) => (
              <span
                key={child.id}
                className="derivation-view__link"
                style={{ borderLeftColor: LAYER_COLORS[child.layer] }}
              >
                {child.title}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Subcomponents: Decision Timeline (Right Panel)
// =============================================================================

interface DecisionTimelineProps {
  decisions: DecisionEntry[];
  onSelect?: (id: string) => void;
}

const DecisionTimeline = memo(function DecisionTimeline({
  decisions,
  onSelect,
}: DecisionTimelineProps) {
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="decision-timeline">
      <div className="decision-timeline__header">
        <Clock size={14} />
        <span className="decision-timeline__title">Decision History</span>
        <span className="decision-timeline__count">{decisions.length}</span>
      </div>

      <div className="decision-timeline__entries">
        {decisions.map((decision) => (
          <button
            key={decision.id}
            className="decision-timeline__entry"
            onClick={() => onSelect?.(decision.id)}
          >
            <div className="decision-timeline__entry-date">{formatDate(decision.timestamp)}</div>
            <div className="decision-timeline__entry-topic">{decision.topic}</div>
            <div className="decision-timeline__entry-synthesis">{decision.synthesis}</div>
            {decision.kentView && decision.claudeView && (
              <div className="decision-timeline__entry-dialectic">
                <span className="decision-timeline__entry-view decision-timeline__entry-view--kent">
                  K: {decision.kentView}
                </span>
                <span className="decision-timeline__entry-view decision-timeline__entry-view--claude">
                  C: {decision.claudeView}
                </span>
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
});

// =============================================================================
// Subcomponents: Right Panel Tab Selector
// =============================================================================

const TAB_CONFIG: Record<RightPanelTab, { label: string; icon: typeof GitCommit }> = {
  git: { label: 'Git', icon: GitCommit },
  decisions: { label: 'Decisions', icon: GitBranch },
  witness: { label: 'Witness', icon: Bookmark },
};

interface TabSelectorProps {
  activeTab: RightPanelTab;
  onChange: (tab: RightPanelTab) => void;
}

const TabSelector = memo(function TabSelector({ activeTab, onChange }: TabSelectorProps) {
  return (
    <div className="tangible-tab-selector">
      {(Object.entries(TAB_CONFIG) as [RightPanelTab, typeof TAB_CONFIG.git][]).map(
        ([key, config]) => {
          const Icon = config.icon;
          const isActive = activeTab === key;

          return (
            <button
              key={key}
              className={`tangible-tab-selector__btn ${isActive ? 'tangible-tab-selector__btn--active' : ''}`}
              onClick={() => onChange(key)}
            >
              <Icon size={12} />
              <span>{config.label}</span>
            </button>
          );
        }
      )}
    </div>
  );
});

// =============================================================================
// Mode Components
// =============================================================================

function SelfReflectionMode() {
  // Panel state
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const [rightPanelTab, setRightPanelTab] = useState<RightPanelTab>('git');

  // Selection state
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [selectedCommit, setSelectedCommit] = useState<string | null>(null);
  const [selectedDecision, setSelectedDecision] = useState<string | null>(null);

  // Filter state
  const [codebaseFilter, setCodebaseFilter] = useState<CodebaseFilter>({});
  const [commitFilter, setCommitFilter] = useState<CommitFilter>({});

  // K-Block inspector state
  const [inspectedKBlock, setInspectedKBlock] = useState<KBlockInfo | null>(null);
  const [kblockPosition, setKBlockPosition] = useState({ x: 0, y: 0 });

  // Derivation chain state
  const [derivationChain, setDerivationChain] = useState<DerivationChain | null>(null);
  const [showDerivationModal, setShowDerivationModal] = useState(false);

  // Handle file selection
  const handleFileSelect = useCallback((path: string) => {
    setSelectedFile(path);
  }, []);

  // Handle K-Block hover
  const handleKBlockHover = useCallback((kblockId: string, position: { x: number; y: number }) => {
    // In real implementation, fetch K-Block info from API
    setInspectedKBlock({
      id: kblockId,
      path: 'spec/protocols/witness.md',
      title: 'Witness Protocol',
      layer: 2,
      layerName: 'SPEC',
      derivedFrom: ['kb-6'],
      groundedBy: ['kb-9'],
      witnesses: [
        {
          markId: 'm-1',
          action: 'Created spec',
          author: 'kent',
          timestamp: '2025-12-20T10:00:00Z',
          principles: ['composable'],
        },
      ],
      galoisLoss: 0.12,
      createdAt: '2025-12-15T09:00:00Z',
    });
    setKBlockPosition(position);
  }, []);

  // Navigate to file
  const handleNavigateToFile = useCallback((path: string) => {
    setSelectedFile(path);
  }, []);

  // Navigate to K-Block
  const handleNavigateToKBlock = useCallback((kblockId: string) => {
    console.log('Navigate to K-Block:', kblockId);
    setInspectedKBlock(null);
  }, []);

  // Show derivation chain
  const handleShowDerivation = useCallback((path: string) => {
    // In real implementation, fetch from API
    setDerivationChain({
      sourceId: 'kb-4',
      sourcePath: path,
      steps: [
        {
          id: 'kb-6',
          title: 'COMPOSABLE',
          layer: 0,
          layerName: 'AXIOM',
          galoisLoss: 0,
          path: 'spec/principles/composable.md',
        },
        { id: 'kb-1', title: 'Joy-Inducing', layer: 1, layerName: 'VALUE', galoisLoss: 0.05 },
        {
          id: 'kb-4',
          title: 'Witness Protocol',
          layer: 2,
          layerName: 'SPEC',
          galoisLoss: 0.12,
          path,
        },
      ],
      totalLoss: 0.17,
    });
    setShowDerivationModal(true);
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Skip if in input
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }

      // Tab shortcuts (1, 2, 3)
      if (!e.ctrlKey && !e.metaKey && !e.shiftKey) {
        if (e.key === '1') {
          e.preventDefault();
          setRightPanelTab('git');
        } else if (e.key === '2') {
          e.preventDefault();
          setRightPanelTab('decisions');
        } else if (e.key === '3') {
          e.preventDefault();
          setRightPanelTab('witness');
        } else if (e.key === 'd' && selectedFile) {
          e.preventDefault();
          handleShowDerivation(selectedFile);
        } else if (e.key === 'Escape') {
          e.preventDefault();
          setInspectedKBlock(null);
          setShowDerivationModal(false);
        }
      }

      // Panel collapse ([ and ])
      if (e.key === '[') {
        e.preventDefault();
        setLeftCollapsed((prev) => !prev);
      } else if (e.key === ']') {
        e.preventDefault();
        setRightCollapsed((prev) => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedFile, handleShowDerivation]);

  return (
    <div className="self-reflection-mode">
      {/* Left Panel: Codebase Explorer */}
      <aside
        className={`self-reflection-mode__left ${leftCollapsed ? 'self-reflection-mode__left--collapsed' : ''}`}
      >
        <button
          className="self-reflection-mode__collapse-btn"
          onClick={() => setLeftCollapsed(!leftCollapsed)}
          aria-label={leftCollapsed ? 'Expand left panel' : 'Collapse left panel'}
        >
          {leftCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
        {!leftCollapsed && (
          <CodebaseExplorer
            onFileSelect={handleFileSelect}
            selectedPath={selectedFile}
            filter={codebaseFilter}
            onFilterChange={setCodebaseFilter}
          />
        )}
      </aside>

      {/* Center Panel: File Inspector */}
      <main className="self-reflection-mode__center">
        <FileInspector
          path={selectedFile || ''}
          showBlame={false}
          showKBlock={true}
          showDerivation={true}
          onNavigateToFile={handleNavigateToFile}
          onKBlockHover={handleKBlockHover}
        />
      </main>

      {/* Right Panel: Git/Decisions/Witness */}
      <aside
        className={`self-reflection-mode__right ${rightCollapsed ? 'self-reflection-mode__right--collapsed' : ''}`}
      >
        <button
          className="self-reflection-mode__collapse-btn"
          onClick={() => setRightCollapsed(!rightCollapsed)}
          aria-label={rightCollapsed ? 'Expand right panel' : 'Collapse right panel'}
        >
          {rightCollapsed ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
        </button>
        {!rightCollapsed && (
          <div className="self-reflection-mode__right-content">
            <TabSelector activeTab={rightPanelTab} onChange={setRightPanelTab} />

            {rightPanelTab === 'git' && (
              <GitTimeline
                onCommitSelect={setSelectedCommit}
                selectedCommit={selectedCommit}
                filter={commitFilter}
                onFilterChange={setCommitFilter}
              />
            )}

            {rightPanelTab === 'decisions' && (
              <EnhancedDecisionTimeline
                onDecisionSelect={setSelectedDecision}
                selectedDecision={selectedDecision}
                onNavigateToFile={handleNavigateToFile}
              />
            )}

            {rightPanelTab === 'witness' && (
              <div className="self-reflection-mode__witness-placeholder">
                <Bookmark size={24} />
                <p>Witness marks timeline coming soon</p>
              </div>
            )}
          </div>
        )}
      </aside>

      {/* Floating K-Block Inspector */}
      {inspectedKBlock && (
        <KBlockInspector
          kblock={inspectedKBlock}
          position={kblockPosition}
          onClose={() => setInspectedKBlock(null)}
          onNavigate={handleNavigateToKBlock}
        />
      )}

      {/* Derivation Chain Modal */}
      {showDerivationModal && derivationChain && (
        <div className="derivation-modal-backdrop">
          <DerivationChainViewer
            chain={derivationChain}
            onClose={() => setShowDerivationModal(false)}
            onNavigate={handleNavigateToFile}
            isModal={true}
          />
        </div>
      )}
    </div>
  );
}

// =============================================================================
// K-Games Studio Mode (Create Mode)
// =============================================================================

// Default operad with standard game composition operations
const DEFAULT_OPERAD: GameOperad = {
  operations: [
    { type: 'sequential', symbol: '>>' },
    { type: 'parallel', symbol: '||' },
    { type: 'conditional', symbol: '?:' },
    { type: 'feedback', symbol: 'loop' },
  ],
  laws: [
    {
      name: 'Associativity',
      statement: '(A >> B) >> C = A >> (B >> C)',
      satisfied: true,
    },
    {
      name: 'Identity',
      statement: 'id >> A = A = A >> id',
      satisfied: true,
    },
    {
      name: 'Parallel Commutativity',
      statement: 'A || B = B || A',
      satisfied: true,
    },
  ],
};

function KGamesStudioMode() {
  // State
  const [kernel, setKernel] = useState<GameKernel>(createDefaultGameKernel);
  const [selectedAxiomId, setSelectedAxiomId] = useState<string | null>(null);
  const [composition, setComposition] = useState<MechanicComposition | null>(null);
  const [evidenceFilter, setEvidenceFilter] = useState<EvidenceFilter>({});
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);

  // Memoized mechanics library
  const mechanics = useMemo(() => createSampleMechanics(), []);

  // Handlers
  const handleAxiomSelect = useCallback((axiomId: string) => {
    setSelectedAxiomId(axiomId);
  }, []);

  const handleCompose = useCallback((result: MechanicComposition) => {
    setComposition(result);
    // In a real implementation, this would update the kernel's health
    // based on how well the composition adheres to axioms
    setKernel((prev) => ({
      ...prev,
      health: Math.max(0.5, prev.health - result.galoisLoss * 0.1),
      updatedAt: new Date(),
    }));
  }, []);

  const handleClearComposition = useCallback(() => {
    setComposition(null);
  }, []);

  const handleFilterChange = useCallback((filter: EvidenceFilter) => {
    setEvidenceFilter(filter);
  }, []);

  const handleCrystalSelect = useCallback((crystalId: string) => {
    // In a real implementation, this would show crystal details
    console.log('Selected crystal:', crystalId);
  }, []);

  // Keyboard shortcuts for panel collapse
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Skip if in input
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }

      // Panel shortcuts (Cmd/Ctrl + number)
      if ((e.metaKey || e.ctrlKey) && !e.shiftKey) {
        if (e.key === '1') {
          e.preventDefault();
          setLeftCollapsed((prev) => !prev);
        } else if (e.key === '3') {
          e.preventDefault();
          setRightCollapsed((prev) => !prev);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="kgames-studio-mode">
      {/* Left Panel: GameKernel Editor */}
      <aside
        className={`kgames-studio-mode__left ${leftCollapsed ? 'kgames-studio-mode__left--collapsed' : ''}`}
      >
        <button
          className="kgames-studio-mode__collapse-btn"
          onClick={() => setLeftCollapsed(!leftCollapsed)}
          aria-label={leftCollapsed ? 'Expand kernel panel' : 'Collapse kernel panel'}
          title="Toggle (Cmd+1)"
        >
          {leftCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
        {!leftCollapsed && (
          <GameKernelEditor
            kernel={kernel}
            onAxiomSelect={handleAxiomSelect}
            selectedAxiomId={selectedAxiomId}
          />
        )}
      </aside>

      {/* Center Panel: MechanicComposer */}
      <main className="kgames-studio-mode__center">
        <MechanicComposer
          mechanics={mechanics}
          composition={composition}
          operad={DEFAULT_OPERAD}
          onCompose={handleCompose}
          onClear={handleClearComposition}
        />
      </main>

      {/* Right Panel: Evidence Stream */}
      <aside
        className={`kgames-studio-mode__right ${rightCollapsed ? 'kgames-studio-mode__right--collapsed' : ''}`}
      >
        <button
          className="kgames-studio-mode__collapse-btn"
          onClick={() => setRightCollapsed(!rightCollapsed)}
          aria-label={rightCollapsed ? 'Expand evidence panel' : 'Collapse evidence panel'}
          title="Toggle (Cmd+3)"
        >
          {rightCollapsed ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
        </button>
        {!rightCollapsed && (
          <EvidenceStream
            gameId="default-game"
            evidenceFilter={evidenceFilter}
            onFilterChange={handleFilterChange}
            onCrystalSelect={handleCrystalSelect}
          />
        )}
      </aside>
    </div>
  );
}

// =============================================================================
// Pilot Actualization Mode
// =============================================================================

function PilotActualizationMode() {
  // Panel state
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);

  // Pilot selection state
  const [selectedPilot, setSelectedPilot] = useState<string | null>(null);
  const [activePilot, setActivePilot] = useState<PilotMetadata | CustomPilot | null>(null);
  const [tierFilter, setTierFilter] = useState<PilotTier | 'all'>('all');

  // Axiom discovery state
  const [showAxiomDiscovery, setShowAxiomDiscovery] = useState(false);
  const [endeavorInput, setEndeavorInput] = useState('');
  const [customPilots, setCustomPilots] = useState<CustomPilot[]>([]);

  // Witness state
  const [marks, setMarks] = useState<WitnessMark[]>([]);
  const [trace, setTrace] = useState<WitnessTrace | null>(null);
  const [crystals, setCrystals] = useState<Crystal[]>([]);
  const [derivationLinks, setDerivationLinks] = useState<DerivationLink[]>([]);

  // Handle pilot selection
  const handlePilotSelect = useCallback((pilotName: string) => {
    setSelectedPilot(pilotName);
  }, []);

  // Handle pilot activation
  const handleActivatePilot = useCallback(() => {
    if (!selectedPilot) return;

    const pilot =
      PILOTS.find((p) => p.name === selectedPilot) ||
      customPilots.find((p) => p.name === selectedPilot);

    if (pilot) {
      setActivePilot(pilot);
      // Create new trace
      const newTrace: WitnessTrace = {
        id: `trace-${Date.now()}`,
        marks: [],
        pilotName: pilot.displayName,
        createdAt: new Date(),
      };
      setTrace(newTrace);
      setMarks([]);
    }
  }, [selectedPilot, customPilots]);

  // Handle new endeavor flow
  const handleNewEndeavor = useCallback(() => {
    setShowAxiomDiscovery(true);
  }, []);

  // Handle axiom discovery completion
  const handleAxiomComplete = useCallback((axioms: EndeavorAxioms) => {
    const newPilot: CustomPilot = {
      name: `custom-${Date.now()}`,
      displayName: axioms.endeavor.slice(0, 30),
      tier: 'core',
      personalityTag: `Pursuing: ${axioms.A1_success.slice(0, 50)}...`,
      description: axioms.endeavor,
      isCustom: true,
      axioms,
      createdAt: new Date(),
    };

    setCustomPilots((prev) => [...prev, newPilot]);
    setShowAxiomDiscovery(false);
    setEndeavorInput('');
    setSelectedPilot(newPilot.name);
  }, []);

  // Handle mark creation
  const handleMark = useCallback(
    (action: string, context: MarkContext) => {
      if (!activePilot || !trace) return;

      const newMark: WitnessMark = {
        id: `mark-${Date.now()}`,
        action,
        context,
        timestamp: new Date(),
        pilotName: activePilot.displayName,
      };

      setMarks((prev) => [...prev, newMark]);
      setTrace((prev) => (prev ? { ...prev, marks: [...prev.marks, newMark] } : null));

      // Mock derivation link creation
      if (marks.length % 3 === 0) {
        const principles = ['L2:JOY_INDUCING', 'L1:COMPOSABLE', 'L0:ETHICAL', 'L1:TASTEFUL'];
        const newLink: DerivationLink = {
          sourceId: newMark.id,
          targetPrinciple: principles[Math.floor(Math.random() * principles.length)],
          strength: 0.5 + Math.random() * 0.5,
          evidence: action,
        };
        setDerivationLinks((prev) => [...prev, newLink]);
      }
    },
    [activePilot, trace, marks.length]
  );

  // Handle pilot deactivation
  const handleDeactivate = useCallback(() => {
    setActivePilot(null);
    setTrace(null);
    setMarks([]);
  }, []);

  // Handle crystallization
  const handleCrystallize = useCallback(() => {
    if (!trace || marks.length < 5) return;

    const newCrystal: Crystal = {
      id: `crystal-${Date.now()}`,
      traceId: trace.id,
      title: `Insight from ${trace.pilotName}`,
      insight: marks
        .slice(-3)
        .map((m) => m.action)
        .join(' + '),
      axiomReference:
        derivationLinks.length > 0
          ? derivationLinks[derivationLinks.length - 1].targetPrinciple
          : undefined,
      createdAt: new Date(),
    };

    setCrystals((prev) => [...prev, newCrystal]);
    setTrace((prev) => (prev ? { ...prev, crystallizedAt: new Date() } : null));
    setMarks([]);

    // Create new trace for continued work
    if (activePilot) {
      const newTrace: WitnessTrace = {
        id: `trace-${Date.now()}`,
        marks: [],
        pilotName: activePilot.displayName,
        createdAt: new Date(),
      };
      setTrace(newTrace);
    }
  }, [trace, marks, derivationLinks, activePilot]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }

      // Panel shortcuts (Cmd/Ctrl + number)
      if ((e.metaKey || e.ctrlKey) && !e.shiftKey) {
        if (e.key === '1') {
          e.preventDefault();
          setLeftCollapsed((prev) => !prev);
        } else if (e.key === '3') {
          e.preventDefault();
          setRightCollapsed((prev) => !prev);
        }
      }

      // Escape to close axiom discovery
      if (e.key === 'Escape' && showAxiomDiscovery) {
        setShowAxiomDiscovery(false);
      }

      // Enter to activate selected pilot (when not in input)
      if (e.key === 'Enter' && selectedPilot && !activePilot) {
        handleActivatePilot();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [showAxiomDiscovery, selectedPilot, activePilot, handleActivatePilot]);

  // Get selected pilot info for display
  const selectedPilotInfo = selectedPilot
    ? PILOTS.find((p) => p.name === selectedPilot) ||
      customPilots.find((p) => p.name === selectedPilot)
    : null;

  return (
    <div className="pilot-actualization-mode">
      {/* Left Panel: Pilot Gallery */}
      <aside
        className={`pilot-actualization-mode__left ${leftCollapsed ? 'pilot-actualization-mode__left--collapsed' : ''}`}
      >
        <button
          className="pilot-actualization-mode__collapse-btn"
          onClick={() => setLeftCollapsed(!leftCollapsed)}
          aria-label={leftCollapsed ? 'Expand pilot gallery' : 'Collapse pilot gallery'}
          title="Toggle (Cmd+1)"
        >
          {leftCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
        {!leftCollapsed && (
          <PilotGallery
            pilots={PILOTS}
            customPilots={customPilots}
            selectedPilot={selectedPilot}
            onSelect={handlePilotSelect}
            onNewEndeavor={handleNewEndeavor}
            tierFilter={tierFilter}
            onTierFilterChange={setTierFilter}
          />
        )}
      </aside>

      {/* Center Panel: Active Pilot or Pilot Details */}
      <main className="pilot-actualization-mode__center">
        {showAxiomDiscovery ? (
          <div className="pilot-actualization-mode__discovery-overlay">
            <div className="pilot-actualization-mode__discovery-prompt">
              <label className="pilot-actualization-mode__discovery-label">
                What do you want to actualize?
              </label>
              <input
                type="text"
                className="pilot-actualization-mode__discovery-input"
                value={endeavorInput}
                onChange={(e) => setEndeavorInput(e.target.value)}
                placeholder="e.g., I want to learn piano, I want to ship a game..."
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && endeavorInput.trim()) {
                    e.preventDefault();
                    // Start the axiom discovery flow
                  }
                }}
              />
            </div>
            {endeavorInput.trim() && (
              <AxiomDiscoveryFlow
                endeavor={endeavorInput}
                onComplete={handleAxiomComplete}
                onCancel={() => {
                  setShowAxiomDiscovery(false);
                  setEndeavorInput('');
                }}
              />
            )}
          </div>
        ) : activePilot ? (
          <ActivePilot
            pilot={activePilot}
            marks={marks}
            onMark={handleMark}
            onDeactivate={handleDeactivate}
          />
        ) : selectedPilotInfo ? (
          <div className="pilot-actualization-mode__pilot-detail">
            <div className="pilot-actualization-mode__pilot-header">
              <h2 className="pilot-actualization-mode__pilot-name">
                {selectedPilotInfo.displayName}
              </h2>
              <span
                className="pilot-actualization-mode__pilot-tier"
                style={{ color: selectedPilotInfo.color }}
              >
                {selectedPilotInfo.tier}
              </span>
            </div>
            <p className="pilot-actualization-mode__pilot-personality">
              &quot;{selectedPilotInfo.personalityTag}&quot;
            </p>
            <p className="pilot-actualization-mode__pilot-description">
              {selectedPilotInfo.description}
            </p>
            <button
              className="pilot-actualization-mode__activate-btn"
              onClick={handleActivatePilot}
            >
              <Zap size={14} />
              Activate Pilot
            </button>
          </div>
        ) : (
          <div className="pilot-actualization-mode__empty">
            <Zap size={48} className="pilot-actualization-mode__empty-icon" />
            <h2 className="pilot-actualization-mode__empty-title">Pilot Actualization</h2>
            <p className="pilot-actualization-mode__empty-description">
              Select a pilot from the gallery to begin your journey, or create a new endeavor.
            </p>
          </div>
        )}
      </main>

      {/* Right Panel: Composition Chain */}
      <aside
        className={`pilot-actualization-mode__right ${rightCollapsed ? 'pilot-actualization-mode__right--collapsed' : ''}`}
      >
        <button
          className="pilot-actualization-mode__collapse-btn"
          onClick={() => setRightCollapsed(!rightCollapsed)}
          aria-label={rightCollapsed ? 'Expand composition' : 'Collapse composition'}
          title="Toggle (Cmd+3)"
        >
          {rightCollapsed ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
        </button>
        {!rightCollapsed && (
          <CompositionChain
            trace={trace}
            crystals={crystals}
            derivationLinks={derivationLinks}
            onCrystallize={marks.length >= 5 ? handleCrystallize : undefined}
          />
        )}
      </aside>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export const TangibleSurface = memo(function TangibleSurface() {
  const [mode, setMode] = useState<TangibleMode>('reflect');

  // Keyboard shortcuts for mode switching
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Skip if in input
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }

      // Mode shortcuts (Shift + key)
      if (e.shiftKey && !e.ctrlKey && !e.metaKey) {
        const key = e.key.toUpperCase();
        if (key === 'R') {
          e.preventDefault();
          setMode('reflect');
        } else if (key === 'C') {
          e.preventDefault();
          setMode('create');
        } else if (key === 'A') {
          e.preventDefault();
          setMode('actualize');
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="tangible-surface">
      {/* Mode Selector Header */}
      <header className="tangible-surface__header">
        <div className="tangible-surface__brand">
          <Eye size={20} className="tangible-surface__logo" />
          <span className="tangible-surface__title">Self-Reflective OS</span>
        </div>
        <ModeSelector mode={mode} onChange={setMode} />
        <div className="tangible-surface__status">
          <span className="tangible-surface__mode-label">{MODE_CONFIG[mode].description}</span>
        </div>
      </header>

      {/* Mode Content */}
      <div className="tangible-surface__content">
        {mode === 'reflect' && <SelfReflectionMode />}
        {mode === 'create' && <KGamesStudioMode />}
        {mode === 'actualize' && <PilotActualizationMode />}
      </div>
    </div>
  );
});

export default TangibleSurface;
