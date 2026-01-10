# ASHC Consumer Integration: UI Components Specification

> "The proof IS the decision. The derivation IS the lineage."

This document specifies the React components for the consumer-first derivation experience in the hypergraph editor. Each component follows the established patterns from `impl/claude/web/src/components/elastic/` and `impl/claude/web/src/hypergraph/`.

---

## 1. DerivationTrailBar

**Purpose**: Shows breadcrumb navigation from CONSTITUTION to current K-Block, displaying Galois loss at each derivation hop.

### Props Interface

```typescript
/**
 * DerivationTrailBar — Breadcrumb with Galois loss visualization
 *
 * Shows the derivation chain from constitutional axioms to current focus,
 * with loss metrics at each hop. Replaces simple breadcrumb with
 * semantically-rich navigation.
 */

interface DerivationHop {
  /** K-Block identifier */
  blockId: string;
  /** Display title (from K-Block metadata) */
  title: string;
  /** Zero Seed layer (1-7) */
  layer: 1 | 2 | 3 | 4 | 5 | 6 | 7;
  /** Galois loss from parent (0-1, lower is better) */
  galoisLoss: number;
  /** Cumulative loss from CONSTITUTION */
  cumulativeLoss: number;
  /** Grounding status */
  groundingStatus: 'grounded' | 'orphan' | 'pending';
}

interface DerivationTrailBarProps {
  /** Ordered derivation path from root to current */
  trail: DerivationHop[];

  /** Currently focused K-Block ID */
  currentBlockId: string;

  /** Navigate to a K-Block in the trail */
  onNavigate: (blockId: string) => void;

  /** Show hover preview for a hop */
  onHoverHop?: (hop: DerivationHop | null) => void;

  /** Maximum hops to display before collapsing */
  maxVisible?: number; // default: 7

  /** Compact mode (icons only, for narrow viewports) */
  compact?: boolean;

  /** Show loss gradients as color intensity */
  showLossGradient?: boolean; // default: true
}
```

### State Management

```typescript
// Local component state (no Zustand needed for this component)
interface TrailBarState {
  hoveredIndex: number | null;
  expandedRange: { start: number; end: number };
  isPreviewOpen: boolean;
}

// Integration with existing stores
import { useUIStore } from '@/stores/uiStore';

// The trail data comes from hypergraph navigation state,
// not a dedicated store. Wire through HypergraphEditor props.
```

### Key Interactions

1. **Click on hop**: Navigate to that K-Block (`onNavigate(blockId)`)
2. **Hover on hop**:
   - Show tooltip with full path and loss breakdown
   - Trigger preview panel if `onHoverHop` provided
   - Highlight downstream path in graph view
3. **Click ellipsis**: Expand collapsed middle section
4. **Keyboard**: Arrow keys navigate trail, Enter selects

### Responsive Behavior

```typescript
// Density-aware rendering per elastic/types.ts
const TRAIL_DENSITY_CONFIG: DensityMap<{
  maxVisible: number;
  showLabels: boolean;
  hopWidth: number;
}> = {
  compact: { maxVisible: 3, showLabels: false, hopWidth: 32 },
  comfortable: { maxVisible: 5, showLabels: true, hopWidth: 80 },
  spacious: { maxVisible: 9, showLabels: true, hopWidth: 120 },
};

// At compact: Show only icons with color-coded loss
// At comfortable: Icons + abbreviated labels
// At spacious: Full labels + loss percentages
```

### Integration Points

- **HypergraphEditor**: Parent component providing trail data and navigation
- **ProofPanel**: Preview panel shows full proof when hovering
- **GaloisCoherenceMeter**: Reused for individual hop loss visualization

---

## 2. ConstitutionalGraphView

**Purpose**: Alternative to file tree, showing K-Blocks organized by principle derivation with color-coded grounding status.

### Props Interface

```typescript
/**
 * ConstitutionalGraphView — Principle-organized K-Block visualization
 *
 * A force-directed or hierarchical graph showing K-Blocks clustered
 * by their constitutional derivation. Alternative navigation to FileExplorer.
 */

interface ConstitutionalNode {
  /** K-Block or Principle identifier */
  id: string;
  /** Display label */
  label: string;
  /** Node type */
  type: 'principle' | 'kblock' | 'constitution';
  /** Zero Seed layer for K-Blocks */
  layer?: 1 | 2 | 3 | 4 | 5 | 6 | 7;
  /** Grounding status */
  groundingStatus: 'grounded' | 'orphan' | 'pending';
  /** Confidence score (0-1) */
  confidence: number;
  /** Position (managed by layout algorithm) */
  x?: number;
  y?: number;
}

interface ConstitutionalEdge {
  /** Edge identifier */
  id: string;
  /** Source node ID */
  source: string;
  /** Target node ID */
  target: string;
  /** Edge type */
  type: 'derives_from' | 'grounds' | 'supports';
  /** Galois loss for this derivation */
  galoisLoss: number;
}

interface ConstitutionalGraphViewProps {
  /** Nodes in the graph */
  nodes: ConstitutionalNode[];

  /** Edges between nodes */
  edges: ConstitutionalEdge[];

  /** Currently selected node ID */
  selectedNodeId: string | null;

  /** Navigate to a node */
  onNodeSelect: (nodeId: string) => void;

  /** Open grounding dialog for orphan */
  onGroundOrphan?: (nodeId: string) => void;

  /** Layout algorithm */
  layout?: 'force' | 'hierarchical' | 'radial';

  /** Filter to show only certain node types */
  filter?: {
    showOrphans?: boolean;
    showPrinciples?: boolean;
    minConfidence?: number;
    layers?: number[];
  };

  /** Zoom level (0.5 - 2.0) */
  zoom?: number;

  /** Pan offset */
  pan?: { x: number; y: number };

  /** Enable minimap */
  showMinimap?: boolean;
}
```

### State Management

```typescript
// Dedicated Zustand store for graph state
interface ConstitutionalGraphStore {
  // Graph data (fetched from API)
  nodes: ConstitutionalNode[];
  edges: ConstitutionalEdge[];
  isLoading: boolean;
  error: string | null;

  // View state
  selectedNodeId: string | null;
  hoveredNodeId: string | null;
  zoom: number;
  pan: { x: number; y: number };
  layout: 'force' | 'hierarchical' | 'radial';

  // Filters
  filter: {
    showOrphans: boolean;
    showPrinciples: boolean;
    minConfidence: number;
    layers: number[];
  };

  // Actions
  fetchGraph: (projectId: string) => Promise<void>;
  selectNode: (nodeId: string | null) => void;
  setZoom: (zoom: number) => void;
  setPan: (pan: { x: number; y: number }) => void;
  setLayout: (layout: 'force' | 'hierarchical' | 'radial') => void;
  updateFilter: (filter: Partial<ConstitutionalGraphStore['filter']>) => void;
}

export const useConstitutionalGraphStore = create<ConstitutionalGraphStore>(
  (set, get) => ({
    // Initial state
    nodes: [],
    edges: [],
    isLoading: false,
    error: null,
    selectedNodeId: null,
    hoveredNodeId: null,
    zoom: 1.0,
    pan: { x: 0, y: 0 },
    layout: 'hierarchical',
    filter: {
      showOrphans: true,
      showPrinciples: true,
      minConfidence: 0,
      layers: [1, 2, 3, 4, 5, 6, 7],
    },

    // Actions...
  })
);
```

### Key Interactions

1. **Click node**: Select and focus (`onNodeSelect`)
2. **Double-click node**: Open in editor (navigate)
3. **Right-click orphan**: Context menu with "Ground this K-Block"
4. **Drag canvas**: Pan view
5. **Scroll**: Zoom in/out
6. **Hover edge**: Show Galois loss tooltip
7. **Keyboard**:
   - `+`/`-`: Zoom
   - Arrow keys: Pan
   - `g`: Toggle grounding mode
   - `1-7`: Filter by layer

### Responsive Behavior

```typescript
const GRAPH_DENSITY_CONFIG: DensityMap<{
  nodeRadius: number;
  labelSize: number;
  showLabels: boolean;
  showMinimap: boolean;
}> = {
  compact: { nodeRadius: 8, labelSize: 10, showLabels: false, showMinimap: false },
  comfortable: { nodeRadius: 12, labelSize: 12, showLabels: true, showMinimap: false },
  spacious: { nodeRadius: 16, labelSize: 14, showLabels: true, showMinimap: true },
};

// At compact: Simplified graph, tap to see details in bottom drawer
// At comfortable: Standard graph with labels
// At spacious: Full graph with minimap and detail panel
```

### Integration Points

- **HypergraphEditor**: Alternative to FileExplorer for navigation
- **GroundingDialog**: Triggered when grounding orphans
- **DerivationInspector**: Shows full path for selected node

### Visual Design

```typescript
// Color coding for grounding status (Stark Biome palette)
const GROUNDING_COLORS = {
  grounded: 'var(--color-glow-spore)',    // Gold: fully grounded
  orphan: 'var(--color-warning)',          // Amber: needs grounding
  pending: 'var(--color-steel-zinc)',      // Gray: processing
};

// Layer colors (Zero Seed semantic layers)
const LAYER_COLORS: Record<number, string> = {
  1: 'var(--color-axiom)',         // Deep foundation
  2: 'var(--color-value)',         // Values
  3: 'var(--color-goal)',          // Goals
  4: 'var(--color-spec)',          // Specs
  5: 'var(--color-action)',        // Actions
  6: 'var(--color-reflection)',    // Reflections
  7: 'var(--color-representation)', // Representations
};
```

---

## 3. GroundingDialog

**Purpose**: Modal for grounding orphan K-Blocks, showing suggested principles with Galois loss.

### Props Interface

```typescript
/**
 * GroundingDialog — Modal for connecting orphan K-Blocks to principles
 *
 * Shows suggested principles ranked by semantic similarity (low Galois loss),
 * allows drag-drop or click to establish grounding relationship.
 */

interface GroundingSuggestion {
  /** Principle or parent K-Block ID */
  targetId: string;
  /** Display title */
  title: string;
  /** Why this is suggested (semantic similarity) */
  reasoning: string;
  /** Estimated Galois loss if grounded here */
  estimatedLoss: number;
  /** Confidence in this suggestion (0-1) */
  confidence: number;
  /** Zero Seed layer of target */
  layer: 1 | 2 | 3 | 4 | 5 | 6 | 7;
}

interface GroundingDialogProps {
  /** Orphan K-Block to be grounded */
  orphanBlock: {
    id: string;
    title: string;
    content: string;
    layer: number;
  };

  /** Suggested grounding targets, ranked by loss */
  suggestions: GroundingSuggestion[];

  /** Whether suggestions are loading */
  isLoading?: boolean;

  /** Confirm grounding to a target */
  onGround: (targetId: string, reasoning?: string) => Promise<void>;

  /** Cancel without grounding */
  onCancel: () => void;

  /** Search for more targets */
  onSearch?: (query: string) => Promise<GroundingSuggestion[]>;

  /** Allow custom grounding (not from suggestions) */
  allowCustom?: boolean;
}
```

### State Management

```typescript
// Local component state (dialog is ephemeral)
interface GroundingDialogState {
  selectedTargetId: string | null;
  customReasoning: string;
  searchQuery: string;
  searchResults: GroundingSuggestion[];
  isSearching: boolean;
  isGrounding: boolean;
  error: string | null;
}

// No dedicated store needed; dialog state is local
// Parent component manages opening/closing via useUIStore.openModal
```

### Key Interactions

1. **Click suggestion**: Select as grounding target
2. **Double-click suggestion**: Ground immediately
3. **Drag orphan to target**: Visual grounding gesture
4. **Search input**: Find additional targets
5. **Custom reasoning**: Optional text explaining the grounding
6. **Confirm button**: Execute grounding with selected target
7. **Cancel/Escape**: Close without action

### Responsive Behavior

```typescript
// Dialog adapts to viewport
const DIALOG_DENSITY_CONFIG: DensityMap<{
  maxWidth: string;
  showPreview: boolean;
  suggestionLayout: 'list' | 'grid';
}> = {
  compact: { maxWidth: '100%', showPreview: false, suggestionLayout: 'list' },
  comfortable: { maxWidth: '600px', showPreview: true, suggestionLayout: 'list' },
  spacious: { maxWidth: '800px', showPreview: true, suggestionLayout: 'grid' },
};

// At compact: Full-screen bottom sheet with swipe to select
// At comfortable: Centered modal with list view
// At spacious: Larger modal with grid of suggestions + preview
```

### Integration Points

- **ConstitutionalGraphView**: Triggers dialog for orphan nodes
- **DerivationInspector**: Can trigger re-grounding for existing blocks
- **API**: `POST /api/ashc/ground` to persist grounding relationship

---

## 4. DerivationInspector

**Purpose**: Side panel showing full derivation path with witnesses, loss breakdown, and downstream impact.

### Props Interface

```typescript
/**
 * DerivationInspector — Detailed derivation path analysis
 *
 * Side panel showing the complete derivation from axiom to current block,
 * including all witnesses, Galois loss at each step, and downstream impact.
 */

interface DerivationStep {
  /** K-Block at this step */
  blockId: string;
  title: string;
  layer: 1 | 2 | 3 | 4 | 5 | 6 | 7;

  /** Galois loss incurred at this step */
  galoisLoss: number;

  /** Witnesses for this derivation */
  witnesses: Array<{
    id: string;
    action: string;
    author: string;
    timestamp: string;
    principles: string[];
  }>;

  /** Toulmin proof if available */
  proof?: {
    claim: string;
    data?: string;
    warrant?: string;
    backing?: string;
    qualifier?: string;
    rebuttals?: string[];
  };
}

interface DownstreamImpact {
  /** K-Blocks that derive from current */
  dependents: Array<{
    blockId: string;
    title: string;
    depth: number; // derivation distance
  }>;

  /** Total downstream count */
  totalCount: number;

  /** Risk assessment if current block changes */
  riskLevel: 'low' | 'medium' | 'high';
}

interface DerivationInspectorProps {
  /** K-Block being inspected */
  blockId: string;

  /** Full derivation path from root */
  derivationPath: DerivationStep[];

  /** Downstream impact analysis */
  downstreamImpact: DownstreamImpact;

  /** Total Galois loss (sum of all steps) */
  totalLoss: number;

  /** Navigate to a block in the path */
  onNavigate: (blockId: string) => void;

  /** Trigger re-derivation */
  onRederive?: () => Promise<void>;

  /** View formal proof */
  onViewProof?: (blockId: string) => void;

  /** Panel open state */
  isOpen: boolean;

  /** Toggle panel */
  onToggle: () => void;
}
```

### State Management

```typescript
// Inspector state lives in HypergraphEditor or dedicated slice
interface DerivationInspectorStore {
  // Data (fetched on-demand)
  derivationPath: DerivationStep[];
  downstreamImpact: DownstreamImpact | null;
  isLoading: boolean;
  error: string | null;

  // View state
  expandedSteps: Set<string>;
  selectedWitnessId: string | null;

  // Actions
  fetchDerivation: (blockId: string) => Promise<void>;
  toggleStepExpanded: (blockId: string) => void;
  selectWitness: (witnessId: string | null) => void;
}
```

### Key Interactions

1. **Click step**: Expand to show witnesses and proof
2. **Click navigate icon**: Go to that K-Block
3. **Click witness**: Show witness details
4. **Re-derive button**: Trigger re-derivation from parent
5. **View proof button**: Open formal proof panel
6. **Downstream warning**: Click to see affected blocks

### Responsive Behavior

```typescript
// Panel follows FloatingSidebar pattern
const INSPECTOR_DENSITY_CONFIG: DensityMap<{
  panelWidth: number;
  position: 'right' | 'bottom';
  showDownstream: boolean;
}> = {
  compact: { panelWidth: 0, position: 'bottom', showDownstream: false },
  comfortable: { panelWidth: 320, position: 'right', showDownstream: true },
  spacious: { panelWidth: 400, position: 'right', showDownstream: true },
};

// At compact: BottomDrawer with swipeable sheets
// At comfortable/spacious: Fixed sidebar with collapsible sections
```

### Integration Points

- **HypergraphEditor**: Parent component, provides block context
- **ProofPanel**: Detailed proof view on demand
- **WitnessPanel**: Witness details when selected

---

## 5. ProjectRealizationWelcome

**Purpose**: Welcome screen showing project coherence summary on open. Informational, not a gate.

### Props Interface

```typescript
/**
 * ProjectRealizationWelcome — Project health dashboard on open
 *
 * Shows derivation coherence at a glance: total blocks, orphan count,
 * average Galois loss, and suggested next actions. Not a blocking gate.
 */

interface ProjectStats {
  /** Total K-Blocks in project */
  totalBlocks: number;

  /** Blocks fully grounded to CONSTITUTION */
  groundedBlocks: number;

  /** Orphan blocks needing grounding */
  orphanBlocks: number;

  /** Average Galois loss across all derivations */
  averageLoss: number;

  /** Blocks by layer */
  blocksByLayer: Record<number, number>;

  /** Recent derivation activity */
  recentActivity: Array<{
    blockId: string;
    title: string;
    action: 'created' | 'grounded' | 'modified';
    timestamp: string;
  }>;
}

interface SuggestedAction {
  /** Action type */
  type: 'ground_orphan' | 'reduce_loss' | 'add_witness';
  /** Display title */
  title: string;
  /** Why this is suggested */
  reasoning: string;
  /** Target K-Block if applicable */
  targetBlockId?: string;
  /** Priority (lower = more urgent) */
  priority: number;
}

interface ProjectRealizationWelcomeProps {
  /** Project identifier */
  projectId: string;

  /** Project name */
  projectName: string;

  /** Project statistics */
  stats: ProjectStats;

  /** Suggested actions */
  suggestions: SuggestedAction[];

  /** Dismiss welcome (user can continue to editor) */
  onDismiss: () => void;

  /** Execute a suggested action */
  onAction: (action: SuggestedAction) => void;

  /** Open ConstitutionalGraphView */
  onOpenGraph: () => void;

  /** Don't show again preference */
  dontShowAgain?: boolean;
  onDontShowAgainChange?: (value: boolean) => void;
}
```

### State Management

```typescript
// Fetch on mount, dismiss preference in user settings
interface WelcomeStore {
  stats: ProjectStats | null;
  suggestions: SuggestedAction[];
  isLoading: boolean;
  dontShowAgain: boolean;

  fetchStats: (projectId: string) => Promise<void>;
  setDontShowAgain: (value: boolean) => void;
}

// Integrates with userStore for preference persistence
```

### Key Interactions

1. **Dismiss button**: Close and continue to editor
2. **Action card click**: Execute suggested action
3. **Graph view button**: Navigate to ConstitutionalGraphView
4. **Stats card hover**: Show detailed breakdown
5. **Don't show again**: Toggle preference

### Responsive Behavior

```typescript
const WELCOME_DENSITY_CONFIG: DensityMap<{
  layout: 'single-column' | 'two-column';
  showGraph: boolean;
  maxSuggestions: number;
}> = {
  compact: { layout: 'single-column', showGraph: false, maxSuggestions: 3 },
  comfortable: { layout: 'two-column', showGraph: false, maxSuggestions: 5 },
  spacious: { layout: 'two-column', showGraph: true, maxSuggestions: 7 },
};

// At compact: Stacked cards with swipe navigation
// At comfortable: Side-by-side stats and suggestions
// At spacious: Includes mini graph preview
```

### Integration Points

- **HypergraphEditor**: Shows on initial project open
- **ConstitutionalGraphView**: Navigation target for "View Graph"
- **GroundingDialog**: Triggered by "Ground orphan" action
- **userStore**: Persists "don't show again" preference

---

## 6. GaloisCoherenceMeter

**Purpose**: Visual gauge showing derivation loss, reusable across K-Block cards, trail bar, etc.

### Props Interface

```typescript
/**
 * GaloisCoherenceMeter — Visual loss indicator
 *
 * A compact, reusable gauge showing Galois loss as a visual indicator.
 * Used in trail bar hops, K-Block cards, and inspector steps.
 */

type MeterVariant = 'inline' | 'badge' | 'bar' | 'radial';
type MeterSize = 'xs' | 'sm' | 'md' | 'lg';

interface GaloisCoherenceMeterProps {
  /** Galois loss value (0-1, where 0 = perfect coherence) */
  loss: number;

  /** Display variant */
  variant?: MeterVariant; // default: 'inline'

  /** Size */
  size?: MeterSize; // default: 'sm'

  /** Show numeric value */
  showValue?: boolean; // default: false

  /** Show label ("Loss: X%") */
  showLabel?: boolean; // default: false

  /** Custom label text */
  label?: string;

  /** Threshold for warning state */
  warningThreshold?: number; // default: 0.3

  /** Threshold for danger state */
  dangerThreshold?: number; // default: 0.6

  /** Animate changes */
  animate?: boolean; // default: true

  /** Tooltip content */
  tooltip?: string;

  /** Additional CSS class */
  className?: string;
}
```

### Variants

```typescript
// Inline: Small dot next to text (used in trail bar)
// Badge: Pill with color and optional percentage (used in cards)
// Bar: Horizontal progress bar (used in inspector)
// Radial: Circular gauge (used in welcome dashboard)

const VARIANT_STYLES: Record<MeterVariant, {
  containerClass: string;
  showsProgress: boolean;
}> = {
  inline: { containerClass: 'galois-meter--inline', showsProgress: false },
  badge: { containerClass: 'galois-meter--badge', showsProgress: false },
  bar: { containerClass: 'galois-meter--bar', showsProgress: true },
  radial: { containerClass: 'galois-meter--radial', showsProgress: true },
};
```

### Color Logic

```typescript
// Color gradient based on loss value (Stark Biome palette)
function getLossColor(loss: number, warningThreshold: number, dangerThreshold: number): string {
  if (loss < warningThreshold) {
    return 'var(--color-glow-spore)'; // Gold: good coherence
  } else if (loss < dangerThreshold) {
    return 'var(--color-warning)'; // Amber: moderate loss
  } else {
    return 'var(--color-danger)'; // Red: high loss
  }
}

// Inverse display: show coherence instead of loss
// coherence = 1 - loss
// "92% coherent" vs "8% loss"
```

### Responsive Behavior

```typescript
const METER_SIZE_CONFIG: Record<MeterSize, {
  diameter: number;
  fontSize: number;
  strokeWidth: number;
}> = {
  xs: { diameter: 12, fontSize: 10, strokeWidth: 2 },
  sm: { diameter: 16, fontSize: 12, strokeWidth: 2 },
  md: { diameter: 24, fontSize: 14, strokeWidth: 3 },
  lg: { diameter: 32, fontSize: 16, strokeWidth: 4 },
};

// Adapts size based on context, not density
// Parent components choose appropriate size
```

### Integration Points

- **DerivationTrailBar**: Inline variant at each hop
- **ConstitutionalGraphView**: Badge variant on nodes
- **DerivationInspector**: Bar variant for step breakdown
- **ProjectRealizationWelcome**: Radial variant for overall health

---

## Shared Infrastructure

### API Integration

```typescript
// All components fetch from ASHC API endpoints
const ASHC_API = {
  getDerivationPath: (blockId: string) =>
    `/api/ashc/derivation/${blockId}`,

  getConstitutionalGraph: (projectId: string) =>
    `/api/ashc/graph/${projectId}`,

  getGroundingSuggestions: (blockId: string) =>
    `/api/ashc/grounding/suggestions/${blockId}`,

  ground: (orphanId: string, targetId: string, reasoning?: string) =>
    `/api/ashc/ground`,

  getProjectStats: (projectId: string) =>
    `/api/ashc/stats/${projectId}`,
};
```

### Common Hooks

```typescript
// Hook for fetching derivation data
function useDerivation(blockId: string) {
  const [path, setPath] = useState<DerivationStep[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch derivation path from API
  }, [blockId]);

  return { path, isLoading, error };
}

// Hook for grounding suggestions
function useGroundingSuggestions(orphanId: string) {
  const [suggestions, setSuggestions] = useState<GroundingSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch suggestions from API
  }, [orphanId]);

  const search = async (query: string) => {
    // Search for additional targets
  };

  return { suggestions, isLoading, search };
}
```

### CSS Variables (extend existing Stark Biome)

```css
/* Add to global styles */
:root {
  /* Galois coherence colors */
  --color-coherence-high: var(--color-glow-spore);
  --color-coherence-medium: var(--color-warning);
  --color-coherence-low: var(--color-danger);

  /* Zero Seed layer colors */
  --color-axiom: hsl(280, 40%, 50%);
  --color-value: hsl(320, 40%, 50%);
  --color-goal: hsl(200, 50%, 50%);
  --color-spec: hsl(160, 40%, 45%);
  --color-action: hsl(40, 60%, 50%);
  --color-reflection: hsl(220, 30%, 60%);
  --color-representation: hsl(180, 30%, 55%);

  /* Derivation trail spacing */
  --trail-hop-gap: 8px;
  --trail-separator-width: 20px;
}
```

---

## Implementation Priority

1. **GaloisCoherenceMeter** - Foundation component, used everywhere
2. **DerivationTrailBar** - Core navigation, extends existing TrailBar
3. **DerivationInspector** - Extends ProofPanel pattern
4. **ProjectRealizationWelcome** - Similar to existing welcome patterns
5. **GroundingDialog** - Modal pattern from DialecticModal
6. **ConstitutionalGraphView** - Most complex, builds on AxiomGarden patterns

---

*This spec follows the Metaphysical Fullstack pattern: UI components are projections of the ASHC domain model, not independent entities. The Galois loss metric flows from backend computation through AGENTESE to these visual representations.*
