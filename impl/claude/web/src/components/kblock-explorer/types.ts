/**
 * K-Block Explorer Type Definitions
 *
 * "K-Blocks organized by layer (L0-L3 for Constitutional, L1-L7 for user)"
 *
 * Defines the type hierarchy for the K-Block Explorer component,
 * which replaces the traditional file tree with a K-Block-centric view.
 *
 * @see spec/agents/k-block.md
 * @see docs/skills/metaphysical-fullstack.md
 */

import type { KBlock } from '../../primitives/KBlockProjection/types';

// =============================================================================
// Layer Configuration
// =============================================================================

/**
 * Layer configuration for Constitutional K-Blocks (L0-L3).
 * These are the 22 genesis K-Blocks that form the foundation.
 */
export interface ConstitutionalLayerConfig {
  /** Layer number (0-3) */
  layer: number;
  /** Human-readable name */
  name: string;
  /** Short description */
  description: string;
  /** Layer color from LIVING_EARTH palette */
  color: string;
  /** Icon character/emoji */
  icon: string;
  /** K-Block kinds in this layer */
  kinds: string[];
}

/**
 * Layer configuration for User K-Blocks (L1-L7).
 */
export interface UserLayerConfig {
  /** Layer number (1-7) */
  layer: number;
  /** Human-readable name */
  name: string;
  /** Description */
  description: string;
  /** Layer color */
  color: string;
  /** Icon */
  icon: string;
}

// =============================================================================
// Layer Config Constants (LIVING_EARTH Palette)
// =============================================================================

/**
 * Constitutional layer configuration (22 genesis K-Blocks).
 * Layers L0-L3 are read-only constitutional foundations.
 */
export const CONSTITUTIONAL_LAYER_CONFIG: ConstitutionalLayerConfig[] = [
  {
    layer: 0,
    name: 'Genesis',
    description: 'The Zero Seed - root of all derivation',
    color: '#440154', // Deep purple
    icon: '◇',
    kinds: ['zero-seed', 'system'],
  },
  {
    layer: 1,
    name: 'Axioms',
    description: 'Entity, Morphism, Galois Ground',
    color: '#31688e', // Blue
    icon: '△',
    kinds: ['axiom', 'ground'],
  },
  {
    layer: 2,
    name: 'Values',
    description: 'Seven constitutional principles',
    color: '#35b779', // Green
    icon: '♢',
    kinds: ['value', 'principle'],
  },
  {
    layer: 3,
    name: 'Specs',
    description: 'Design laws and constraints',
    color: '#fde724', // Yellow
    icon: '▽',
    kinds: ['spec', 'law'],
  },
];

/**
 * User layer configuration (L1-L7).
 * User K-Blocks are editable and derive from constitutional layers.
 */
export const USER_LAYER_CONFIG: UserLayerConfig[] = [
  {
    layer: 1,
    name: 'Axiom',
    description: 'User axioms and grounds',
    color: '#31688e',
    icon: '△',
  },
  {
    layer: 2,
    name: 'Value',
    description: 'Values and principles',
    color: '#35b779',
    icon: '♢',
  },
  {
    layer: 3,
    name: 'Capability',
    description: 'System capabilities',
    color: '#6b8b6b', // life-mint
    icon: '◈',
  },
  {
    layer: 4,
    name: 'Domain',
    description: 'Domain specifications',
    color: '#fde724',
    icon: '□',
  },
  {
    layer: 5,
    name: 'Service',
    description: 'Service implementations',
    color: '#f59e0b', // Amber
    icon: '⬡',
  },
  {
    layer: 6,
    name: 'Construction',
    description: 'UI constructions',
    color: '#ef4444', // Red
    icon: '▣',
  },
  {
    layer: 7,
    name: 'Implementation',
    description: 'Code and assets',
    color: '#8b5cf6', // Violet
    icon: '◉',
  },
];

// =============================================================================
// K-Block Explorer Types
// =============================================================================

/**
 * K-Block summary for explorer display.
 */
export interface KBlockExplorerItem {
  /** Unique ID */
  id: string;
  /** Display title (derived from path or content) */
  title: string;
  /** Full path */
  path: string;
  /** Zero Seed layer (null for non-layered) */
  layer: number | null;
  /** K-Block kind (axiom, value, spec, etc.) */
  kind: string | null;
  /** Galois loss (0-1, coherence drift) */
  galoisLoss: number;
  /** Has Toulmin proof */
  hasProof: boolean;
  /** Derived from these K-Block IDs */
  derivesFrom: string[];
  /** Tags */
  tags: string[];
  /** Is constitutional (read-only) */
  isConstitutional: boolean;
  /** Content preview */
  preview?: string;
  /** Created timestamp */
  createdAt?: Date;
}

/**
 * Layer group for tree display.
 */
export interface KBlockLayerGroup {
  /** Layer config */
  config: ConstitutionalLayerConfig | UserLayerConfig;
  /** K-Blocks in this layer */
  items: KBlockExplorerItem[];
  /** Is expanded */
  expanded: boolean;
}

/**
 * Navigation direction for keyboard navigation.
 */
export type NavigationDirection = 'up' | 'down' | 'parent' | 'child';

/**
 * Focus target in the explorer.
 */
export interface FocusTarget {
  /** K-Block ID or section ID */
  id: string;
  /** Type of target */
  type: 'kblock' | 'layer' | 'section';
}

/**
 * Section in the explorer (Constitutional / User).
 */
export type ExplorerSection = 'constitutional' | 'user' | 'orphans';

// =============================================================================
// API Response Types (matching client.ts)
// =============================================================================

/**
 * Clean slate K-Block from API.
 */
export interface CleanSlateKBlock {
  id: string;
  title: string;
  layer: number;
  galois_loss: number;
  derives_from: string[];
  tags: string[];
  content?: string;
}

/**
 * Derivation edge from API.
 */
export interface DerivationEdge {
  from: string;
  to: string;
  type: string;
}

/**
 * Derivation graph response from API.
 */
export interface DerivationGraphResponse {
  nodes: CleanSlateKBlock[];
  edges: DerivationEdge[];
  layers: Record<number, string[]>;
}

// =============================================================================
// Component Props
// =============================================================================

/**
 * Props for KBlockExplorer main component.
 */
export interface KBlockExplorerProps {
  /** Called when a K-Block is selected */
  onSelect: (kblock: KBlockExplorerItem) => void;
  /** Currently selected K-Block ID */
  selectedId?: string;
  /** Class name override */
  className?: string;
}

/**
 * Props for KBlockTree component.
 */
export interface KBlockTreeProps {
  /** Constitutional K-Blocks */
  constitutionalGroups: KBlockLayerGroup[];
  /** User K-Blocks */
  userGroups: KBlockLayerGroup[];
  /** Orphan K-Blocks (no layer) */
  orphans: KBlockExplorerItem[];
  /** Selected K-Block ID */
  selectedId?: string;
  /** Current focus target */
  focusTarget: FocusTarget | null;
  /** Callbacks */
  onSelect: (item: KBlockExplorerItem) => void;
  onToggleLayer: (section: ExplorerSection, layer: number) => void;
  onFocusChange: (target: FocusTarget | null) => void;
}

/**
 * Props for ConstitutionalSection component.
 */
export interface ConstitutionalSectionProps {
  /** Layer groups */
  groups: KBlockLayerGroup[];
  /** Selected K-Block ID */
  selectedId?: string;
  /** Focus target */
  focusTarget: FocusTarget | null;
  /** Callbacks */
  onSelect: (item: KBlockExplorerItem) => void;
  onToggleLayer: (layer: number) => void;
  onFocusChange: (target: FocusTarget | null) => void;
}

/**
 * Props for LayerGroup component.
 */
export interface LayerGroupProps {
  /** Layer configuration */
  config: ConstitutionalLayerConfig | UserLayerConfig;
  /** K-Blocks in this layer */
  items: KBlockExplorerItem[];
  /** Is expanded */
  expanded: boolean;
  /** Is constitutional (read-only) */
  isConstitutional: boolean;
  /** Selected K-Block ID */
  selectedId?: string;
  /** Is this layer focused */
  isFocused: boolean;
  /** Callbacks - layer number is passed to avoid inline closures in parent */
  onToggle: (layer: number) => void;
  onSelect: (item: KBlockExplorerItem) => void;
  onItemFocus: (id: string) => void;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get layer config by layer number.
 */
export function getLayerConfig(
  layer: number,
  isConstitutional: boolean
): ConstitutionalLayerConfig | UserLayerConfig | undefined {
  if (isConstitutional) {
    return CONSTITUTIONAL_LAYER_CONFIG.find((c) => c.layer === layer);
  }
  return USER_LAYER_CONFIG.find((c) => c.layer === layer);
}

/**
 * Get layer color by layer number.
 */
export function getLayerColor(layer: number | null): string {
  if (layer === null) return '#6b7280'; // Gray for orphans
  const config =
    CONSTITUTIONAL_LAYER_CONFIG.find((c) => c.layer === layer) ||
    USER_LAYER_CONFIG.find((c) => c.layer === layer);
  return config?.color || '#6b7280';
}

/**
 * Get layer icon by layer number.
 */
export function getLayerIcon(layer: number | null): string {
  if (layer === null) return '○';
  const config =
    CONSTITUTIONAL_LAYER_CONFIG.find((c) => c.layer === layer) ||
    USER_LAYER_CONFIG.find((c) => c.layer === layer);
  return config?.icon || '○';
}

/**
 * Get loss severity level.
 */
export function getLossSeverity(loss: number): 'healthy' | 'warning' | 'critical' | 'emergency' {
  if (loss < 0.2) return 'healthy';
  if (loss < 0.5) return 'warning';
  if (loss < 0.8) return 'critical';
  return 'emergency';
}

/**
 * Get loss color based on severity.
 */
export function getLossColor(loss: number): string {
  const severity = getLossSeverity(loss);
  switch (severity) {
    case 'healthy':
      return '#22c55e';
    case 'warning':
      return '#f59e0b';
    case 'critical':
      return '#ef4444';
    case 'emergency':
      return '#dc2626';
  }
}

/**
 * Convert a genesis K-Block ID to a file path.
 *
 * Genesis K-Blocks are sovereign files that exist on disk.
 * Example: genesis:L0:entity -> spec/genesis/L0/entity.md
 */
function genesisIdToFilePath(id: string): string | null {
  const match = id.match(/^genesis:L(\d):(\w+)$/);
  if (match) {
    const [, layer, name] = match;
    return `spec/genesis/L${layer}/${name}.md`;
  }
  return null;
}

/**
 * Transform API K-Block to explorer item.
 *
 * Path format depends on K-Block type:
 * - Genesis K-Blocks: `spec/genesis/L{layer}/{name}.md` (file paths)
 * - Other K-Blocks: `kblock/{id}` (K-Block URIs)
 *
 * Philosophy: "Files are sovereign territory. Genesis files are real .md files."
 */
export function toExplorerItem(
  kblock: CleanSlateKBlock,
  isConstitutional = false
): KBlockExplorerItem {
  // For genesis K-Blocks, use file path instead of kblock:// URI
  const path = kblock.id.startsWith('genesis:')
    ? (genesisIdToFilePath(kblock.id) ?? `kblock/${kblock.id}`)
    : `kblock/${kblock.id}`;

  return {
    id: kblock.id,
    title: kblock.title,
    path,
    layer: kblock.layer,
    kind:
      kblock.tags.find((t) =>
        ['axiom', 'value', 'spec', 'goal', 'action', 'reflection'].includes(t)
      ) ?? null,
    galoisLoss: kblock.galois_loss,
    hasProof: false, // Not in clean slate response
    derivesFrom: kblock.derives_from,
    tags: kblock.tags,
    isConstitutional,
    preview: kblock.content?.slice(0, 200),
  };
}

/**
 * Group K-Blocks by layer.
 */
export function groupByLayer(
  items: KBlockExplorerItem[],
  isConstitutional: boolean
): Map<number, KBlockExplorerItem[]> {
  const groups = new Map<number, KBlockExplorerItem[]>();

  const configs = isConstitutional ? CONSTITUTIONAL_LAYER_CONFIG : USER_LAYER_CONFIG;

  // Initialize all layers
  configs.forEach((c) => groups.set(c.layer, []));

  // Group items
  items.forEach((item) => {
    if (item.layer !== null && groups.has(item.layer)) {
      groups.get(item.layer)!.push(item);
    }
  });

  return groups;
}
