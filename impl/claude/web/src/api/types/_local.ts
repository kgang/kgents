/**
 * FE-only types and configuration constants.
 *
 * Phase 7: AGENTESE Contract Protocol
 *
 * This file contains types that are purely frontend concerns:
 * - Visual configuration (colors, icons)
 * - UI state types
 * - Local component state
 * - Constants that don't come from the backend
 *
 * Contract types (response/request types from API) should be in _generated/
 * after running `npm run sync-types`.
 */

// =============================================================================
// Visual Configuration (FE-only)
// =============================================================================

// Import types from the main types barrel (parent directory)
import type {
  BuilderArchetype,
  GalleryCategory,
  GestaltStreamStatus,
  InfraEntityKind,
  InfraEvent,
  NPhaseType,
  ParkCrisisPhase,
  ParkMaskArchetype,
  ParkTimerStatus,
  StreamConnectionStatus,
  TownPhase,
} from '../types';

// Builder visual config
export const BUILDER_COLORS: Record<BuilderArchetype, string> = {
  Scout: '#22c55e', // green
  Sage: '#8b5cf6', // purple
  Spark: '#f59e0b', // amber
  Steady: '#3b82f6', // blue
  Sync: '#ec4899', // pink
};

/**
 * @deprecated Use BUILDER_ICONS_LUCIDE from '@/constants' instead.
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */
export const BUILDER_ICONS: Record<BuilderArchetype, string> = {
  Scout: 'compass',
  Sage: 'graduation-cap',
  Spark: 'zap',
  Steady: 'hammer',
  Sync: 'link',
};

// =============================================================================
// Credit Packs (FE config - prices may be FE concern for display)
// =============================================================================

export interface CreditPack {
  name: string;
  credits: number;
  price_usd: number;
}

export const CREDIT_PACKS: CreditPack[] = [
  { name: 'Starter', credits: 500, price_usd: 4.99 },
  { name: 'Explorer', credits: 2500, price_usd: 19.99 },
  { name: 'Adventurer', credits: 10000, price_usd: 59.99 },
];

export const SUBSCRIPTION_TIERS = {
  TOURIST: { price: 0, lod: [0, 1], inhabit: false, branching: false },
  RESIDENT: { price: 9.99, lod: [0, 1, 2, 3], inhabit: 'basic', branching: false },
  CITIZEN: { price: 29.99, lod: [0, 1, 2, 3, 4], inhabit: 'full', branching: 3 },
  FOUNDER: { price: 99.99, lod: [0, 1, 2, 3, 4, 5], inhabit: 'unlimited', branching: 'unlimited' },
} as const;

// =============================================================================
// LOD Credit Costs (from unified-v2.md)
// =============================================================================

export const LOD_COSTS: Record<number, number> = {
  0: 0,
  1: 0,
  2: 0,
  3: 10,
  4: 100,
  5: 400,
};

// =============================================================================
// N-Phase Visual Configuration (FE-only)
// =============================================================================

/**
 * N-Phase visual configuration.
 *
 * NOTE: For icons, import PHASE_ICONS from '@/constants' instead of using emoji strings.
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */
export const NPHASE_CONFIG = {
  colors: {
    UNDERSTAND: '#3b82f6', // blue - gathering info
    ACT: '#f59e0b', // amber - executing
    REFLECT: '#8b5cf6', // purple - reviewing
  },
  /**
   * @deprecated Use PHASE_ICONS from '@/constants' instead.
   * Kept for backward compatibility - values are now Lucide icon names.
   */
  icons: {
    UNDERSTAND: 'eye',
    ACT: 'zap',
    REFLECT: 'message-circle',
  },
  descriptions: {
    UNDERSTAND: 'Gathering context and analyzing the situation',
    ACT: 'Executing actions and making changes',
    REFLECT: 'Reviewing outcomes and learning',
  },
  // Town phase -> N-Phase mapping
  townPhaseMapping: {
    MORNING: 'UNDERSTAND',
    AFTERNOON: 'UNDERSTAND',
    EVENING: 'ACT',
    NIGHT: 'REFLECT',
  } as Record<TownPhase, NPhaseType>,
} as const;

// =============================================================================
// Gallery Category Visual Config (FE-only)
// =============================================================================

export const GALLERY_CATEGORY_CONFIG: Record<GalleryCategory, { icon: string; color: string }> = {
  PRIMITIVES: { icon: '\u25cb', color: '#22c55e' },
  CARDS: { icon: '\u25a6', color: '#3b82f6' },
  CHROME: { icon: '\u25fb', color: '#f59e0b' },
  STREAMING: { icon: '\u25b8', color: '#8b5cf6' },
  COMPOSITION: { icon: '\u229e', color: '#ec4899' },
  ADAPTERS: { icon: '\u21c4', color: '#06b6d4' },
  SPECIALIZED: { icon: '\u25c8', color: '#ef4444' },
  // Gallery V2 categories (AD-009 Vertical Slice)
  POLYNOMIAL: { icon: '\u25c9', color: '#14b8a6' },  // teal - state machines
  OPERAD: { icon: '\u229b', color: '#a855f7' },      // purple - composition grammar
  CROWN_JEWELS: { icon: '\u2666', color: '#eab308' }, // yellow - vertical slices
  LAYOUT: { icon: '\u25a3', color: '#64748b' },      // slate - design system
  INTERACTIVE: { icon: '\u26a1', color: '#10b981' }, // emerald - flagship interactive
};

// =============================================================================
// Health Grade Visual Config (FE-only)
// =============================================================================

export const HEALTH_GRADE_CONFIG: Record<string, { color: string; bgColor: string }> = {
  'A+': { color: '#22c55e', bgColor: 'bg-green-500/20' },
  'A': { color: '#4ade80', bgColor: 'bg-green-400/20' },
  'B+': { color: '#a3e635', bgColor: 'bg-lime-400/20' },
  'B': { color: '#facc15', bgColor: 'bg-yellow-400/20' },
  'C+': { color: '#fb923c', bgColor: 'bg-orange-400/20' },
  'C': { color: '#f97316', bgColor: 'bg-orange-500/20' },
  'D': { color: '#ef4444', bgColor: 'bg-red-500/20' },
  'F': { color: '#dc2626', bgColor: 'bg-red-600/20' },
  '?': { color: '#6b7280', bgColor: 'bg-gray-500/20' },
};

// =============================================================================
// Polynomial Visual Config (FE-only)
// =============================================================================

/**
 * Configuration for polynomial visualization styling.
 *
 * NOTE: For icons, import from '@/constants' (GARDENER_PHASE_ICONS, PHASE_ICONS, CITIZEN_PHASE_ICONS).
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 * The 'icon' field contains Lucide icon names (lowercase, hyphenated).
 */
export const POLYNOMIAL_CONFIG = {
  // Default colors for positions
  colors: {
    default: '#3b82f6', // blue
    current: '#22c55e', // green
    terminal: '#ef4444', // red
    available: '#f59e0b', // amber
  },
  // Gardener session phases
  gardener: {
    SENSE: { color: '#3b82f6', icon: 'eye', label: 'Sense' },
    ACT: { color: '#f59e0b', icon: 'zap', label: 'Act' },
    REFLECT: { color: '#8b5cf6', icon: 'message-circle', label: 'Reflect' },
  },
  // N-Phase development phases
  nphase: {
    PLAN: { color: '#94a3b8', icon: 'clipboard-list', label: 'Plan' },
    RESEARCH: { color: '#3b82f6', icon: 'search', label: 'Research' },
    DEVELOP: { color: '#22c55e', icon: 'wrench', label: 'Develop' },
    STRATEGIZE: { color: '#8b5cf6', icon: 'target', label: 'Strategize' },
    'CROSS-SYNERGIZE': { color: '#ec4899', icon: 'link', label: 'Cross-Synergize' },
    IMPLEMENT: { color: '#f59e0b', icon: 'cog', label: 'Implement' },
    QA: { color: '#06b6d4', icon: 'microscope', label: 'QA' },
    TEST: { color: '#10b981', icon: 'test-tube', label: 'Test' },
    EDUCATE: { color: '#a855f7', icon: 'graduation-cap', label: 'Educate' },
    MEASURE: { color: '#f97316', icon: 'bar-chart-3', label: 'Measure' },
    REFLECT: { color: '#6366f1', icon: 'book-open', label: 'Reflect' },
  },
  // Citizen polynomial phases
  citizen: {
    IDLE: { color: '#94a3b8', icon: 'circle-dot', label: 'Idle' },
    SOCIALIZING: { color: '#ec4899', icon: 'message-circle', label: 'Socializing' },
    WORKING: { color: '#f59e0b', icon: 'wrench', label: 'Working' },
    REFLECTING: { color: '#8b5cf6', icon: 'book-open', label: 'Reflecting' },
    RESTING: { color: '#22c55e', icon: 'cloud', label: 'Resting' },
  },
} as const;

// =============================================================================
// Infrastructure Visual Config (FE-only)
// =============================================================================

/**
 * Entity kind visual config.
 *
 * NOTE: For icons, import INFRA_ENTITY_ICONS from '@/constants'.
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */
export const INFRA_ENTITY_CONFIG: Record<InfraEntityKind, {
  icon: string;
  color: string;
  shape: 'sphere' | 'octahedron' | 'dodecahedron' | 'box' | 'cone' | 'cylinder' | 'torus';
}> = {
  namespace: { icon: 'box', color: '#6366f1', shape: 'torus' },
  node: { icon: 'monitor', color: '#8b5cf6', shape: 'box' },
  pod: { icon: 'server', color: '#22c55e', shape: 'sphere' },
  service: { icon: 'link', color: '#3b82f6', shape: 'octahedron' },
  deployment: { icon: 'play', color: '#f59e0b', shape: 'dodecahedron' },
  container: { icon: 'box', color: '#06b6d4', shape: 'box' },
  nats_subject: { icon: 'mail', color: '#a855f7', shape: 'cone' },
  nats_stream: { icon: 'wind', color: '#ec4899', shape: 'cylinder' },
  database: { icon: 'database', color: '#ef4444', shape: 'cylinder' },
  volume: { icon: 'hard-drive', color: '#f97316', shape: 'box' },
  custom: { icon: 'cog', color: '#6b7280', shape: 'sphere' },
};

/**
 * Event severity visual config.
 *
 * NOTE: For icons, import SEVERITY_ICONS from '@/constants'.
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */
export const INFRA_SEVERITY_CONFIG: Record<InfraEvent['severity'], { icon: string; color: string }> = {
  info: { icon: 'info', color: '#3b82f6' },
  warning: { icon: 'alert-triangle', color: '#f59e0b' },
  error: { icon: 'x-circle', color: '#ef4444' },
  critical: { icon: 'alert-triangle', color: '#dc2626' },
};

// =============================================================================
// Park Visual Config (FE-only)
// =============================================================================

/**
 * Crisis phase visual config.
 *
 * NOTE: For icons, import CRISIS_PHASE_ICONS from '@/constants'.
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */
export const PARK_PHASE_CONFIG: Record<ParkCrisisPhase, { color: string; icon: string; label: string }> = {
  NORMAL: { color: '#22c55e', icon: 'check-circle', label: 'Normal' },
  INCIDENT: { color: '#f59e0b', icon: 'alert-triangle', label: 'Incident' },
  RESPONSE: { color: '#ef4444', icon: 'zap', label: 'Response' },
  RECOVERY: { color: '#3b82f6', icon: 'refresh-cw', label: 'Recovery' },
};

/**
 * Timer status visual config.
 *
 * NOTE: For icons, import TIMER_STATUS_ICONS from '@/constants'.
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */
export const PARK_TIMER_CONFIG: Record<ParkTimerStatus, { color: string; icon: string }> = {
  PENDING: { color: '#6b7280', icon: 'circle' },
  ACTIVE: { color: '#22c55e', icon: 'play' },
  WARNING: { color: '#f59e0b', icon: 'alert-triangle' },
  CRITICAL: { color: '#ef4444', icon: 'x-circle' },
  EXPIRED: { color: '#dc2626', icon: 'x-circle' },
  COMPLETED: { color: '#22c55e', icon: 'check-circle' },
  PAUSED: { color: '#6b7280', icon: 'pause' },
};

/**
 * Mask archetype visual config.
 *
 * NOTE: For icons, import MASK_ARCHETYPE_ICONS from '@/constants'.
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */
export const PARK_MASK_CONFIG: Record<ParkMaskArchetype, { color: string; icon: string }> = {
  TRICKSTER: { color: '#f59e0b', icon: 'sparkles' },
  DREAMER: { color: '#a855f7', icon: 'cloud' },
  SKEPTIC: { color: '#6366f1', icon: 'search' },
  ARCHITECT: { color: '#3b82f6', icon: 'building-2' },
  CHILD: { color: '#ec4899', icon: 'star' },
  SAGE: { color: '#8b5cf6', icon: 'owl' },
  WARRIOR: { color: '#ef4444', icon: 'swords' },
  HEALER: { color: '#22c55e', icon: 'heart' },
};

/**
 * Eigenvector dimension config for radar chart.
 */
export const PARK_EIGENVECTOR_CONFIG: Record<string, { label: string; color: string }> = {
  creativity: { label: 'Creativity', color: '#f59e0b' },
  trust: { label: 'Trust', color: '#22c55e' },
  empathy: { label: 'Empathy', color: '#ec4899' },
  authority: { label: 'Authority', color: '#ef4444' },
  playfulness: { label: 'Playfulness', color: '#a855f7' },
  wisdom: { label: 'Wisdom', color: '#8b5cf6' },
  directness: { label: 'Directness', color: '#3b82f6' },
  warmth: { label: 'Warmth', color: '#f97316' },
};

// =============================================================================
// UI State Types (FE-only)
// =============================================================================

/**
 * Replay state for workshop replay feature.
 */
export interface ReplayState {
  taskId: string;
  events: unknown[];
  currentIndex: number;
  isPlaying: boolean;
  playbackSpeed: number;
  duration: number;
  elapsed: number;
}

/**
 * Entity animation state for smooth transitions.
 */
export interface EntityAnimationState {
  opacity: number;       // 0-1, for fade in/out
  scale: number;         // base scale multiplier
  pulseIntensity: number; // 0-1, for update flash
  isNew: boolean;        // just added (fade in)
  isRemoving: boolean;   // marked for removal (fade out)
  lastUpdated: number;   // timestamp for pulse decay
}

// =============================================================================
// Re-exports for backward compatibility
// =============================================================================

// Re-export stream status types (these are FE state machine states)
export type { GestaltStreamStatus, StreamConnectionStatus };
