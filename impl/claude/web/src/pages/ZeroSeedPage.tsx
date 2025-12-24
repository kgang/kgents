/**
 * ZeroSeedPage — Epistemic Graph Navigation
 *
 * "Navigate toward stability. The gradient IS the guide. The loss IS the landscape."
 *
 * Philosophy:
 *   "The proof IS the decision. The mark IS the witness."
 *   Layer by layer, axiom to representation, ground to telescope.
 *
 * Layout: Tabbed interface for exploring L1-L7 layers
 *   [L1-L2: Axioms & Values] | [L3-L4: Proofs & Quality] | [L5-L6: Health] | [L7: Telescope]
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  getAxiomExplorer,
  getProofDashboard,
  getGraphHealth,
  getTelescopeState,
  type AxiomExplorerResponse,
  type ProofDashboardResponse,
  type GraphHealthResponse,
  type TelescopeResponse,
  type NodeId,
  type ZeroNode,
  type NodeLoss,
  type ProofQuality,
  type GraphHealth,
  type TelescopeState,
  type GradientVector,
  type NavigationSuggestion,
  type PolicyArrow,
} from '../api/zeroSeed';
import { AxiomExplorer } from '../components/zero-seed/AxiomExplorer';
import { ProofQualityDashboard } from '../components/zero-seed/ProofQualityDashboard';
import { GraphHealthMonitor } from '../components/zero-seed/GraphHealthMonitor';
import { TelescopeNavigator } from '../components/zero-seed/TelescopeNavigator';
import '../components/zero-seed/ZeroSeed.css';

// =============================================================================
// Types
// =============================================================================

type TabKey = 'axioms' | 'proofs' | 'health' | 'telescope';

interface TabConfig {
  key: TabKey;
  label: string;
  shortcut: string;
  layers: string;
  description: string;
}

const TABS: TabConfig[] = [
  {
    key: 'axioms',
    label: 'Axioms & Values',
    shortcut: '1',
    layers: 'L1-L2',
    description: 'Ground layer - irreducible truth taken on faith',
  },
  {
    key: 'proofs',
    label: 'Proof Quality',
    shortcut: '2',
    layers: 'L3-L4',
    description: 'Justification layer - goals and specs with Toulmin proofs',
  },
  {
    key: 'health',
    label: 'Graph Health',
    shortcut: '3',
    layers: 'L5-L6',
    description: 'Stability layer - actions and reflections, contradictions',
  },
  {
    key: 'telescope',
    label: 'Telescope',
    shortcut: '4',
    layers: 'L7',
    description: 'Navigation layer - loss gradients and Galois telescope',
  },
];

// =============================================================================
// Mock Data (until backend is fully implemented)
// =============================================================================

function generateMockData() {
  // Generate mock axioms (L1)
  const axioms: ZeroNode[] = [
    {
      id: 'axiom-001',
      path: 'void.axiom.entity',
      layer: 1,
      kind: 'axiom',
      title: 'A1: Entity',
      content: 'Everything is a node. There is no privileged "configuration" vs "content" distinction.',
      confidence: 0.95,
      created_at: '2025-12-20T10:00:00Z',
      created_by: 'kent',
      tags: ['core', 'foundational'],
      lineage: [],
      has_proof: false,
    },
    {
      id: 'axiom-002',
      path: 'void.axiom.morphism',
      layer: 1,
      kind: 'axiom',
      title: 'A2: Morphism',
      content: 'Any two nodes can be connected. Edges are morphisms in a category. Composition is primary.',
      confidence: 0.95,
      created_at: '2025-12-20T10:00:00Z',
      created_by: 'kent',
      tags: ['core', 'foundational'],
      lineage: [],
      has_proof: false,
    },
    {
      id: 'axiom-003',
      path: 'void.axiom.mirror-test',
      layer: 1,
      kind: 'axiom',
      title: 'Mirror Test',
      content: 'Does K-gent feel like me on my best day?',
      confidence: 0.9,
      created_at: '2025-12-20T10:00:00Z',
      created_by: 'kent',
      tags: ['soul', 'voice'],
      lineage: [],
      has_proof: false,
    },
  ];

  // Generate mock values (L2)
  const values: ZeroNode[] = [
    {
      id: 'value-001',
      path: 'void.value.tasteful',
      layer: 2,
      kind: 'value',
      title: 'Tasteful',
      content: 'Each agent serves a clear, justified purpose. Tasteful > feature-complete.',
      confidence: 0.92,
      created_at: '2025-12-20T10:00:00Z',
      created_by: 'kent',
      tags: ['principle'],
      lineage: ['axiom-001'],
      has_proof: false,
    },
    {
      id: 'value-002',
      path: 'void.value.composable',
      layer: 2,
      kind: 'value',
      title: 'Composable',
      content: 'Agents are morphisms in a category. Composition via >> operator.',
      confidence: 0.88,
      created_at: '2025-12-20T10:00:00Z',
      created_by: 'kent',
      tags: ['principle'],
      lineage: ['axiom-002'],
      has_proof: false,
    },
    {
      id: 'value-003',
      path: 'void.value.joy-inducing',
      layer: 2,
      kind: 'value',
      title: 'Joy-Inducing',
      content: 'Delight in interaction. The persona is a garden, not a museum.',
      confidence: 0.85,
      created_at: '2025-12-20T10:00:00Z',
      created_by: 'kent',
      tags: ['principle', 'soul'],
      lineage: ['axiom-003'],
      has_proof: false,
    },
  ];

  // Generate mock losses
  const losses = new Map<string, NodeLoss>();
  [...axioms, ...values].forEach((node) => {
    const baseLoss = node.layer === 1 ? 0.1 : 0.25;
    const loss = baseLoss + Math.random() * 0.2;
    losses.set(node.id, {
      node_id: node.id,
      loss,
      components: {
        content_loss: loss * 0.4,
        proof_loss: 0,
        edge_loss: loss * 0.3,
        metadata_loss: loss * 0.1,
        total: loss,
      },
      health_status: loss < 0.3 ? 'healthy' : loss < 0.7 ? 'warning' : 'critical',
    });
  });

  // Generate mock proofs (L3-L4)
  const proofs: ProofQuality[] = [
    {
      node_id: 'goal-001',
      proof: {
        data: '3 years kgents development, ~52K lines, 20+ systems',
        warrant: 'Radical axiom reduction achieves maximum generativity',
        claim: 'Zero Seed provides a minimal generative kernel',
        backing: 'Derives 7-layer system from 2 axioms + 1 meta-principle',
        qualifier: 'probably',
        rebuttals: [
          'Unless 7-layer taxonomy proves too complex',
          'Unless radical compression makes system harder to understand',
        ],
        tier: 'categorical',
        principles: ['generative', 'composable', 'tasteful'],
      },
      coherence_score: 0.85,
      warrant_strength: 0.9,
      backing_coverage: 0.8,
      rebuttal_count: 2,
      quality_tier: 'strong',
      ghost_alternatives: [
        {
          id: 'ghost-001',
          warrant: 'Empirical validation through real-world usage',
          confidence: 0.7,
          reasoning: 'Usage data could strengthen the claim',
        },
      ],
    },
    {
      node_id: 'spec-001',
      proof: {
        data: 'Existing witness service with 2000+ marks',
        warrant: 'Witnessing creates accountability and traceability',
        claim: 'All modifications should create witness marks',
        backing: 'Legal and ethical requirements for auditability',
        qualifier: 'definitely',
        rebuttals: [],
        tier: 'categorical',
        principles: ['ethical', 'curated'],
      },
      coherence_score: 0.92,
      warrant_strength: 0.95,
      backing_coverage: 0.88,
      rebuttal_count: 0,
      quality_tier: 'strong',
      ghost_alternatives: [],
    },
    {
      node_id: 'goal-002',
      proof: {
        data: 'Initial user studies (n=3)',
        warrant: 'User satisfaction correlates with success',
        claim: 'The system should be joy-inducing',
        backing: 'Prior research on UX and delight',
        qualifier: 'probably',
        rebuttals: ['Sample size too small', 'Selection bias possible'],
        tier: 'empirical',
        principles: ['joy-inducing'],
      },
      coherence_score: 0.55,
      warrant_strength: 0.5,
      backing_coverage: 0.4,
      rebuttal_count: 2,
      quality_tier: 'weak',
      ghost_alternatives: [
        {
          id: 'ghost-002',
          warrant: 'Larger-scale study with diverse users',
          confidence: 0.8,
          reasoning: 'Would strengthen empirical foundation',
        },
        {
          id: 'ghost-003',
          warrant: 'Define joy-inducing metrics objectively',
          confidence: 0.6,
          reasoning: 'Subjective claims need operationalization',
        },
      ],
    },
  ];

  // Generate mock graph health
  const health: GraphHealth = {
    total_nodes: axioms.length + values.length + 10,
    total_edges: 25,
    by_layer: {
      1: axioms.length,
      2: values.length,
      3: 3,
      4: 4,
      5: 2,
      6: 1,
      7: 0,
    },
    healthy_count: 8,
    warning_count: 4,
    critical_count: 1,
    contradictions: [
      {
        id: 'contradiction-001',
        node_a: 'spec-002',
        node_b: 'spec-003',
        edge_id: 'edge-contradicts-001',
        description: 'Conflicting requirements: batch processing vs real-time constraint',
        severity: 'medium',
        is_resolved: false,
        resolution_id: null,
      },
    ],
    instability_indicators: [
      {
        type: 'orphan',
        node_id: 'action-003',
        description: 'Action node with no incoming edges from L4 specs',
        severity: 0.6,
        suggested_action: 'Connect to relevant specification node',
      },
      {
        type: 'weak_proof',
        node_id: 'goal-002',
        description: 'Proof has low warrant strength and high rebuttal count',
        severity: 0.7,
        suggested_action: 'Strengthen backing or address rebuttals',
      },
    ],
    super_additive_loss_detected: false,
  };

  // Generate mock telescope state
  const telescopeState: TelescopeState = {
    focal_distance: 0.5,
    focal_point: null,
    show_loss: true,
    show_gradient: true,
    loss_threshold: 0.7,
    visible_layers: [1, 2, 3, 4, 5, 6, 7],
    preferred_layer: 4,
  };

  // Generate mock gradients
  const gradients = new Map<string, GradientVector>();
  [...axioms, ...values].forEach((node) => {
    gradients.set(node.id, {
      x: Math.random() * 2 - 1,
      y: Math.random() * 2 - 1,
      magnitude: Math.random() * 0.5,
      target_node: node.lineage[0] || node.id,
    });
  });

  // Mock suggestions
  const suggestions: NavigationSuggestion[] = [
    {
      target: 'axiom-001',
      action: 'focus',
      value_score: 0.95,
      reasoning: 'Core axiom with lowest loss - stable foundation',
    },
    {
      target: 'goal-002',
      action: 'investigate',
      value_score: 0.7,
      reasoning: 'Weak proof detected - needs improvement',
    },
  ];

  // Mock policy arrows
  const policyArrows: PolicyArrow[] = [
    { from: 'value-001', to: 'axiom-001', value: 0.9, is_optimal: true },
    { from: 'value-002', to: 'axiom-002', value: 0.85, is_optimal: true },
    { from: 'value-003', to: 'axiom-003', value: 0.8, is_optimal: false },
  ];

  return {
    axioms,
    values,
    losses,
    proofs,
    health,
    telescopeState,
    gradients,
    suggestions,
    policyArrows,
  };
}

// =============================================================================
// Component
// =============================================================================

export function ZeroSeedPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Get initial tab from query params
  const initialTab = (searchParams.get('tab') as TabKey) || 'axioms';

  // Tab state
  const [activeTab, setActiveTab] = useState<TabKey>(initialTab);
  const [selectedNode, setSelectedNode] = useState<NodeId | null>(null);

  // Data state (try API first, fall back to mock)
  const [axiomData, setAxiomData] = useState<AxiomExplorerResponse | null>(null);
  const [proofData, setProofData] = useState<ProofDashboardResponse | null>(null);
  const [healthData, setHealthData] = useState<GraphHealthResponse | null>(null);
  const [telescopeData, setTelescopeData] = useState<TelescopeResponse | null>(null);

  // Loading & error state
  const [loading, setLoading] = useState<Record<TabKey, boolean>>({
    axioms: false,
    proofs: false,
    health: false,
    telescope: false,
  });
  const [error, setError] = useState<string | null>(null);
  const [useMock, setUseMock] = useState(false);

  // Mock data fallback
  const [mockData, setMockData] = useState<ReturnType<typeof generateMockData> | null>(null);

  // ==========================================================================
  // Data Loading
  // ==========================================================================

  const loadAxioms = useCallback(async () => {
    setLoading((prev) => ({ ...prev, axioms: true }));
    setError(null);
    try {
      const data = await getAxiomExplorer();
      setAxiomData(data);
      setUseMock(false);
    } catch (err) {
      console.warn('API failed, using mock data:', err);
      if (!mockData) {
        setMockData(generateMockData());
      }
      setUseMock(true);
    } finally {
      setLoading((prev) => ({ ...prev, axioms: false }));
    }
  }, [mockData]);

  const loadProofs = useCallback(async () => {
    setLoading((prev) => ({ ...prev, proofs: true }));
    setError(null);
    try {
      const data = await getProofDashboard();
      setProofData(data);
      setUseMock(false);
    } catch (err) {
      console.warn('API failed, using mock data:', err);
      if (!mockData) {
        setMockData(generateMockData());
      }
      setUseMock(true);
    } finally {
      setLoading((prev) => ({ ...prev, proofs: false }));
    }
  }, [mockData]);

  const loadHealth = useCallback(async () => {
    setLoading((prev) => ({ ...prev, health: true }));
    setError(null);
    try {
      const data = await getGraphHealth();
      setHealthData(data);
      setUseMock(false);
    } catch (err) {
      console.warn('API failed, using mock data:', err);
      if (!mockData) {
        setMockData(generateMockData());
      }
      setUseMock(true);
    } finally {
      setLoading((prev) => ({ ...prev, health: false }));
    }
  }, [mockData]);

  const loadTelescope = useCallback(async () => {
    setLoading((prev) => ({ ...prev, telescope: true }));
    setError(null);
    try {
      const data = await getTelescopeState();
      setTelescopeData(data);
      setUseMock(false);
    } catch (err) {
      console.warn('API failed, using mock data:', err);
      if (!mockData) {
        setMockData(generateMockData());
      }
      setUseMock(true);
    } finally {
      setLoading((prev) => ({ ...prev, telescope: false }));
    }
  }, [mockData]);

  // Load data when tab changes
  useEffect(() => {
    switch (activeTab) {
      case 'axioms':
        if (!axiomData && !useMock) loadAxioms();
        break;
      case 'proofs':
        if (!proofData && !useMock) loadProofs();
        break;
      case 'health':
        if (!healthData && !useMock) loadHealth();
        break;
      case 'telescope':
        if (!telescopeData && !useMock) loadTelescope();
        break;
    }
  }, [activeTab, axiomData, proofData, healthData, telescopeData, useMock, loadAxioms, loadProofs, loadHealth, loadTelescope]);

  // ==========================================================================
  // Keyboard Navigation
  // ==========================================================================

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Tab shortcuts: 1-4
      if (e.key >= '1' && e.key <= '4') {
        const idx = parseInt(e.key, 10) - 1;
        if (idx >= 0 && idx < TABS.length) {
          e.preventDefault();
          setActiveTab(TABS[idx].key);
        }
      }

      // Refresh: r
      if (e.key === 'r' && !e.metaKey && !e.ctrlKey) {
        e.preventDefault();
        switch (activeTab) {
          case 'axioms':
            loadAxioms();
            break;
          case 'proofs':
            loadProofs();
            break;
          case 'health':
            loadHealth();
            break;
          case 'telescope':
            loadTelescope();
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeTab, loadAxioms, loadProofs, loadHealth, loadTelescope]);

  // ==========================================================================
  // Helpers
  // ==========================================================================

  const handleSelectNode = useCallback((nodeId: NodeId) => {
    setSelectedNode(nodeId);
  }, []);

  const handleOpenInEditor = useCallback((node: ZeroNode) => {
    // Navigate to hypergraph editor with the node's path
    navigate(`/editor/${node.path}`);
  }, [navigate]);

  // Convert axiom data to Maps/Sets for component props
  const axiomProps = useMemo(() => {
    const data = useMock && mockData ? {
      axioms: mockData.axioms,
      values: mockData.values,
      losses: Array.from(mockData.losses.entries()).map(([_, loss]) => loss),
      total_axiom_count: mockData.axioms.length,
      total_value_count: mockData.values.length,
      fixed_points: Array.from(new Set(
        Array.from(mockData.losses.entries())
          .filter(([_, loss]) => loss.loss < 0.2)
          .map(([id]) => id)
      )),
    } : axiomData;

    if (!data) return null;

    const lossesMap = new Map(data.losses.map((l) => [l.node_id, l]));
    const fixedPointsSet = new Set(data.fixed_points);

    return {
      axioms: data.axioms,
      values: data.values,
      losses: lossesMap,
      fixedPoints: fixedPointsSet,
      onSelectNode: handleSelectNode,
      onOpenInEditor: handleOpenInEditor,
      selectedNode,
      loading: loading.axioms,
    };
  }, [axiomData, mockData, useMock, handleSelectNode, handleOpenInEditor, selectedNode, loading.axioms]);

  const proofProps = useMemo(() => {
    const data = useMock && mockData ? mockData.proofs : proofData?.proofs;
    if (!data) return null;

    const total = data.reduce((sum, p) => sum + p.coherence_score, 0);
    const average = data.length > 0 ? total / data.length : 0;
    const byTier: Record<string, number> = {};
    const needsImprovement: string[] = [];

    data.forEach((p) => {
      byTier[p.quality_tier] = (byTier[p.quality_tier] || 0) + 1;
      if (p.quality_tier === 'weak') {
        needsImprovement.push(p.node_id);
      }
    });

    return {
      proofs: data,
      averageCoherence: average,
      byQualityTier: byTier,
      needsImprovement,
      onSelectNode: handleSelectNode,
      selectedNode,
      loading: loading.proofs,
    };
  }, [proofData, mockData, useMock, handleSelectNode, selectedNode, loading.proofs]);

  // ==========================================================================
  // Render
  // ==========================================================================

  if (error && !axiomData && !proofData && !healthData && !telescopeData && !useMock) {
    return (
      <div className="flex items-center justify-center h-full bg-steel-950">
        <div className="text-center p-8">
          <p className="text-sm text-red-400 mb-4">{error}</p>
          <button
            className="px-4 py-2 bg-steel-800 border border-steel-700 rounded text-steel-100 text-sm font-mono hover:bg-steel-700 hover:border-steel-600 transition-colors"
            onClick={() => {
              switch (activeTab) {
                case 'axioms':
                  loadAxioms();
                  break;
                case 'proofs':
                  loadProofs();
                  break;
                case 'health':
                  loadHealth();
                  break;
                case 'telescope':
                  loadTelescope();
                  break;
              }
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="zero-seed-page flex flex-col h-full bg-steel-950">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 bg-steel-900 border-b border-steel-800">
        <div className="flex flex-col gap-1">
          <h1 className="m-0 text-xl font-semibold text-steel-100">
            Zero Seed
            {useMock && (
              <span className="ml-2 px-2 py-0.5 bg-yellow-600/20 border border-yellow-600/50 rounded text-xs text-yellow-400 font-normal">
                Mock Data
              </span>
            )}
          </h1>
          <p className="m-0 text-xs text-steel-500 leading-tight">
            Navigate toward stability. The gradient IS the guide. The loss IS the landscape.
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-xs text-steel-500">
            <kbd className="px-1.5 py-0.5 bg-steel-800 border border-steel-700 rounded font-mono text-steel-400">
              1-4
            </kbd>{' '}
            switch tabs
            <span className="mx-2 text-steel-700">|</span>
            <kbd className="px-1.5 py-0.5 bg-steel-800 border border-steel-700 rounded font-mono text-steel-400">
              r
            </kbd>{' '}
            refresh
          </div>
        </div>
      </header>

      {/* Tab navigation */}
      <nav className="flex items-stretch bg-steel-900 border-b border-steel-800">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            className={`flex-1 px-4 py-3 border-b-2 transition-colors text-left ${
              activeTab === tab.key
                ? 'bg-steel-850 border-purple-500 text-steel-100'
                : 'border-transparent text-steel-400 hover:bg-steel-850 hover:text-steel-200'
            }`}
            onClick={() => setActiveTab(tab.key)}
          >
            <div className="flex items-baseline gap-2">
              <span className="text-sm font-semibold">{tab.label}</span>
              <span className="text-xs text-steel-500 font-mono">{tab.layers}</span>
              <kbd className="ml-auto px-1.5 py-0.5 bg-steel-800 border border-steel-700 rounded text-xs font-mono text-steel-500">
                {tab.shortcut}
              </kbd>
            </div>
            <div className="text-xs text-steel-500 mt-0.5 leading-tight">
              {tab.description}
            </div>
          </button>
        ))}
      </nav>

      {/* Tab content */}
      <main className="flex-1 overflow-hidden">
        {activeTab === 'axioms' && axiomProps && (
          <AxiomExplorer {...axiomProps} />
        )}

        {activeTab === 'proofs' && proofProps && (
          <ProofQualityDashboard {...proofProps} />
        )}

        {activeTab === 'health' && (useMock && mockData ? mockData.health : healthData?.health) && (
          <GraphHealthMonitor
            health={useMock && mockData ? mockData.health : healthData!.health}
            timestamp={healthData?.timestamp || new Date().toISOString()}
            trend={healthData?.trend || 'stable'}
            onSelectNode={handleSelectNode}
            loading={loading.health}
          />
        )}

        {activeTab === 'telescope' && (useMock && mockData || telescopeData) && (
          <TelescopeNavigator
            state={useMock && mockData ? mockData.telescopeState : telescopeData!.state}
            gradients={useMock && mockData ? mockData.gradients : new Map(Object.entries(telescopeData!.gradients))}
            suggestions={useMock && mockData ? mockData.suggestions : telescopeData!.suggestions}
            nodes={useMock && mockData ? [...mockData.axioms, ...mockData.values] : telescopeData!.visible_nodes}
            policyArrows={useMock && mockData ? mockData.policyArrows : telescopeData!.policy_arrows}
            loading={loading.telescope}
          />
        )}

        {/* Loading state */}
        {!axiomProps && !proofProps && activeTab === 'axioms' && loading.axioms && (
          <div className="flex items-center justify-center h-full">
            <div className="flex flex-col items-center gap-4">
              <div className="w-8 h-8 border-2 border-steel-700 border-t-purple-500 rounded-full animate-spin" />
              <span className="text-sm text-steel-500 tracking-wider">
                Loading {TABS.find((t) => t.key === activeTab)?.label.toLowerCase()}...
              </span>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default ZeroSeedPage;
