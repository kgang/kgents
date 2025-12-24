/**
 * Token Registry Types
 *
 * Utilitarian flat grid of tokens for navigating 100s of specs,
 * dozens of principles, and 1000s of implementations.
 *
 * "The frame is humble. The content glows."
 */

// =============================================================================
// Token Types
// =============================================================================

export type TokenType = 'spec' | 'principle' | 'impl';
export type TokenStatus = 'ACTIVE' | 'ORPHAN' | 'DEPRECATED' | 'ARCHIVED' | 'CONFLICTING';

/**
 * Minimal token representation for the grid.
 * Designed for maximum density with details on hover/click.
 */
export interface TokenItem {
  id: string;           // path (unique identifier)
  name: string;         // display name (title or filename)
  type: TokenType;
  tier: 0 | 1 | 2 | 3 | 4;
  status: TokenStatus;
  icon: string;         // tier icon (◆ ◈ ○ □ △)
  hasEvidence: boolean; // impl_count + test_count > 0
  claimCount: number;
  implCount: number;
  testCount: number;
  wordCount: number;
}

// =============================================================================
// Filter Types
// =============================================================================

export interface FilterState {
  search: string;
  types: TokenType[];
  statuses: TokenStatus[];
  tiers: number[];
  hasEvidence: boolean | null;  // null = no filter
}

export const DEFAULT_FILTERS: FilterState = {
  search: '',
  types: [],
  statuses: [],
  tiers: [],
  hasEvidence: null,
};

// =============================================================================
// Constants
// =============================================================================

export const TIER_ICONS: Record<number, string> = {
  0: '◆',  // Principles (diamond - foundational)
  1: '◈',  // Protocols (outlined diamond)
  2: '○',  // Agents (circle)
  3: '□',  // Services (square)
  4: '△',  // AGENTESE (triangle)
};

export const TIER_LABELS: Record<number, string> = {
  0: 'Principles',
  1: 'Protocols',
  2: 'Agents',
  3: 'Services',
  4: 'AGENTESE',
};

export const TIER_COLORS: Record<number, string> = {
  0: '#f0f0f0',  // Principles: bright
  1: '#8ba98b',  // Protocols: sage
  2: '#6b8ba3',  // Agents: steel-blue
  3: '#c4a77d',  // Services: spore
  4: '#a65d6a',  // AGENTESE: coral
};

export const STATUS_INDICATORS: Record<TokenStatus, string> = {
  ACTIVE: '',
  ORPHAN: '!',
  DEPRECATED: '~',
  ARCHIVED: '-',
  CONFLICTING: '!',
};

export const TYPE_LABELS: Record<TokenType, string> = {
  spec: 'Spec',
  principle: 'Principle',
  impl: 'Impl',
};

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Detect tier from path.
 */
export function detectTier(path: string): 0 | 1 | 2 | 3 | 4 {
  if (path.includes('principles') || path.includes('constitution')) return 0;
  if (path.includes('protocols')) return 1;
  if (path.includes('agents')) return 2;
  if (path.includes('services') || path.includes('crown')) return 3;
  if (path.includes('agentese')) return 4;
  return 1; // Default to protocols
}

/**
 * Detect type from path.
 */
export function detectType(path: string): TokenType {
  if (path.includes('principles') || path.includes('constitution')) return 'principle';
  if (path.includes('impl/') || path.includes('src/')) return 'impl';
  return 'spec';
}

/**
 * Get icon for tier.
 */
export function getTierIcon(tier: number): string {
  return TIER_ICONS[tier] || '○';
}

/**
 * Get color for tier.
 */
export function getTierColor(tier: number): string {
  return TIER_COLORS[tier] || TIER_COLORS[2];
}
