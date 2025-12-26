/**
 * Mode System Types
 *
 * Six-mode editing system for hypergraph editing (inspired by vim).
 * Each mode enables different affordances and interactions.
 *
 * @see docs/skills/hypergraph-editor.md - Six-mode modal editing
 */

// =============================================================================
// Mode Types
// =============================================================================

/**
 * The six editing modes
 *
 * NORMAL: Navigation, selection, primary mode
 * INSERT: Create K-Blocks (nodes)
 * EDGE: Create relationships (edges)
 * VISUAL: Multi-select, batch operations
 * COMMAND: Slash commands, search, filters
 * WITNESS: Commit changes with marks
 * CONTRADICTION: Focused dialectical work
 */
export type Mode = 'NORMAL' | 'INSERT' | 'EDGE' | 'VISUAL' | 'COMMAND' | 'WITNESS' | 'CONTRADICTION';

/**
 * Mode metadata
 */
export interface ModeDefinition {
  /** Mode name */
  mode: Mode;

  /** Display label */
  label: string;

  /** Single-character trigger key (from NORMAL mode) */
  trigger: string;

  /** Color identifier (maps to color constants) */
  colorKey: string;

  /** Short description of what this mode enables */
  description: string;

  /** Whether this mode blocks navigation */
  blocksNavigation?: boolean;

  /** Whether this mode captures all keyboard input */
  capturesInput?: boolean;
}

/**
 * Mode transition event
 */
export interface ModeTransition {
  /** Previous mode */
  from: Mode;

  /** New mode */
  to: Mode;

  /** Timestamp of transition */
  timestamp: number;

  /** Optional reason/trigger */
  reason?: string;
}

// =============================================================================
// Mode Definitions
// =============================================================================

/**
 * Complete mode metadata
 */
export const MODE_DEFINITIONS: Record<Mode, ModeDefinition> = {
  NORMAL: {
    mode: 'NORMAL',
    label: 'NORMAL',
    trigger: 'Escape',
    colorKey: 'steel',
    description: 'Navigate, select, and invoke commands',
  },
  INSERT: {
    mode: 'INSERT',
    label: 'INSERT',
    trigger: 'i',
    colorKey: 'moss',
    description: 'Create new K-Blocks',
    capturesInput: true,
  },
  EDGE: {
    mode: 'EDGE',
    label: 'EDGE',
    trigger: 'e',
    colorKey: 'amber',
    description: 'Create relationships between nodes',
  },
  VISUAL: {
    mode: 'VISUAL',
    label: 'VISUAL',
    trigger: 'v',
    colorKey: 'sage',
    description: 'Multi-select for batch operations',
  },
  COMMAND: {
    mode: 'COMMAND',
    label: 'COMMAND',
    trigger: ':',
    colorKey: 'rust',
    description: 'Execute slash commands',
    capturesInput: true,
  },
  WITNESS: {
    mode: 'WITNESS',
    label: 'WITNESS',
    trigger: 'w',
    colorKey: 'gold',
    description: 'Commit changes with witness marks',
    blocksNavigation: true,
    capturesInput: true,
  },
  CONTRADICTION: {
    mode: 'CONTRADICTION',
    label: 'CONTRADICTION',
    trigger: 'c',
    colorKey: 'coral',
    description: 'Focused dialectical work',
    blocksNavigation: false,
    capturesInput: false,
  },
} as const;

/**
 * Mode color mapping (Living Earth palette)
 */
export const MODE_COLORS: Record<Mode, string> = {
  NORMAL: '#475569', // Slate-600 (steel)
  INSERT: '#2E4A2E', // Living Earth: fern (moss)
  EDGE: '#D4A574', // Living Earth: amber
  VISUAL: '#4A6B4A', // Living Earth: sage
  COMMAND: '#8B5A2B', // Living Earth: bronze (rust)
  WITNESS: '#E8C4A0', // Living Earth: honey (gold glow)
  CONTRADICTION: '#FF6B6B', // Warm red for productive tension (coral)
} as const;

// =============================================================================
// Mode Utilities
// =============================================================================

/**
 * Check if a mode captures keyboard input
 */
export function modecapturesInput(mode: Mode): boolean {
  return MODE_DEFINITIONS[mode].capturesInput ?? false;
}

/**
 * Check if a mode blocks navigation
 */
export function modeBlocksNavigation(mode: Mode): boolean {
  return MODE_DEFINITIONS[mode].blocksNavigation ?? false;
}

/**
 * Get mode color
 */
export function getModeColor(mode: Mode): string {
  return MODE_COLORS[mode];
}

/**
 * Get mode definition
 */
export function getModeDefinition(mode: Mode): ModeDefinition {
  return MODE_DEFINITIONS[mode];
}

/**
 * All modes as array
 */
export const ALL_MODES: Mode[] = ['NORMAL', 'INSERT', 'EDGE', 'VISUAL', 'COMMAND', 'WITNESS', 'CONTRADICTION'];

/**
 * Check if a key triggers a mode transition from NORMAL
 */
export function getModeTrigger(key: string): Mode | null {
  for (const mode of ALL_MODES) {
    const def = MODE_DEFINITIONS[mode];
    if (def.trigger.toLowerCase() === key.toLowerCase()) {
      return mode;
    }
  }
  return null;
}
