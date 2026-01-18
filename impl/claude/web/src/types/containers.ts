/**
 * Three Containers Types
 *
 * Grounded in: spec/ui/axioms.md — A1 (Creativity), A2 (Sloppification), A6 (Authority)
 *
 * The frontend is an anti-sloppification machine with three containers:
 * - HUMAN: Full authority, no AI mediation
 * - COLLABORATION: Dialectic visible, fusion tracked
 * - AI: Low intensity, requires review
 */

/**
 * Container types for provenance-aware rendering.
 */
export type ContainerType = 'human' | 'collaboration' | 'ai';

/**
 * Authority levels within containers.
 */
export type AuthorityLevel = 'full' | 'shared' | 'delegated';

/**
 * Context for container-aware components.
 */
export interface ContainerContext {
  /** Which container are we in? */
  type: ContainerType;

  /** What authority level? */
  authority: AuthorityLevel;

  /** Should sloppification indicators be visible? */
  sloppificationVisible: boolean;

  /** Does content in this container require review? */
  requiresReview: boolean;

  /** Is this container editable? */
  editable: boolean;
}

/**
 * Container configuration.
 */
export interface ContainerConfig {
  /** Container type */
  type: ContainerType;

  /** Display name */
  displayName: string;

  /** Description */
  description: string;

  /** Default authority level */
  defaultAuthority: AuthorityLevel;

  /** CSS class for styling */
  cssClass: string;

  /** Foreground color variable */
  fgColor: string;

  /** Border style */
  borderStyle: string;
}

/**
 * Container configurations.
 */
export const CONTAINER_CONFIGS: Record<ContainerType, ContainerConfig> = {
  human: {
    type: 'human',
    displayName: 'Human',
    description: 'Full authority, no AI mediation',
    defaultAuthority: 'full',
    cssClass: 'container-human',
    fgColor: 'var(--human-fg)',
    borderStyle: 'none',
  },
  collaboration: {
    type: 'collaboration',
    displayName: 'Collaboration',
    description: 'Dialectic visible, fusion tracked',
    defaultAuthority: 'shared',
    cssClass: 'container-collaboration',
    fgColor: 'var(--fusion-fg)',
    borderStyle: '1px solid var(--fusion-indicator)',
  },
  ai: {
    type: 'ai',
    displayName: 'AI',
    description: 'Low intensity, requires review',
    defaultAuthority: 'delegated',
    cssClass: 'container-ai',
    fgColor: 'var(--ai-fg)',
    borderStyle: '1px solid var(--ai-border)',
  },
};

/**
 * Descriptions for container types.
 */
export const CONTAINER_DESCRIPTIONS: Record<ContainerType, string> = {
  human: 'Full authority, no AI mediation',
  collaboration: 'Dialectic visible, fusion tracked',
  ai: 'Low intensity, requires review',
};

/**
 * Get default container context.
 */
export function getDefaultContainerContext(type: ContainerType): ContainerContext {
  const config = CONTAINER_CONFIGS[type];
  return {
    type,
    authority: config.defaultAuthority,
    sloppificationVisible: type !== 'human',
    requiresReview: type === 'ai',
    editable: type !== 'ai', // AI content not directly editable
  };
}

/**
 * Create human container context.
 */
export function createHumanContext(): ContainerContext {
  return {
    type: 'human',
    authority: 'full',
    sloppificationVisible: false,
    requiresReview: false,
    editable: true,
  };
}

/**
 * Create collaboration container context.
 */
export function createCollaborationContext(): ContainerContext {
  return {
    type: 'collaboration',
    authority: 'shared',
    sloppificationVisible: true,
    requiresReview: false, // Fusion is inherently reviewed
    editable: true,
  };
}

/**
 * Create AI container context.
 */
export function createAIContext(reviewed: boolean = false): ContainerContext {
  return {
    type: 'ai',
    authority: 'delegated',
    sloppificationVisible: true,
    requiresReview: !reviewed,
    editable: false, // Must be reviewed before editing
  };
}

/**
 * Determine container type from provenance.
 */
export function getContainerFromProvenance(author: 'kent' | 'claude' | 'fusion'): ContainerType {
  switch (author) {
    case 'kent':
      return 'human';
    case 'fusion':
      return 'collaboration';
    case 'claude':
      return 'ai';
  }
}

/**
 * Check if container allows direct editing.
 */
export function canEdit(context: ContainerContext): boolean {
  // Human container: always editable
  if (context.type === 'human') return true;

  // Collaboration container: editable
  if (context.type === 'collaboration') return true;

  // AI container: only editable after review
  if (context.type === 'ai') return !context.requiresReview;

  return false;
}

/**
 * Check if container requires sloppification indicators.
 */
export function showSloppificationIndicators(context: ContainerContext): boolean {
  return context.sloppificationVisible;
}

/**
 * Get the CSS class for container styling.
 */
export function getContainerClass(context: ContainerContext): string {
  const base = CONTAINER_CONFIGS[context.type].cssClass;
  const modifiers: string[] = [];

  if (context.requiresReview) {
    modifiers.push(`${base}--needs-review`);
  }

  if (!context.editable) {
    modifiers.push(`${base}--readonly`);
  }

  return [base, ...modifiers].join(' ');
}
