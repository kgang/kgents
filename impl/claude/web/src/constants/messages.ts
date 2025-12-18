/**
 * Voice & Tone Constants
 *
 * User-facing messages that embody kgents voice principles:
 * - Assume intelligence
 * - Be helpful, not condescending
 * - Errors are opportunities for empathy
 * - Empty states are invitations, not voids
 *
 * @see docs/creative/voice-and-tone.md
 */

import type { JewelName } from './jewels';

// =============================================================================
// Loading Messages
// =============================================================================

/**
 * Jewel-specific loading messages.
 * Each jewel has personality-appropriate messages that rotate during loading.
 */
export const LOADING_MESSAGES: Record<JewelName, readonly string[]> = {
  brain: [
    'Consulting the holographic memory...',
    'Traversing the knowledge graph...',
    'Crystallizing insights...',
    'Weaving connections...',
    'Synthesizing understanding...',
  ],
  gestalt: [
    'Mapping the topology...',
    'Rendering the architecture...',
    'Tracing dependencies...',
    'Visualizing structure...',
    'Computing relationships...',
  ],
  gardener: [
    'Tending the garden...',
    'Sensing the current season...',
    'Nurturing growth...',
    'Cultivating ideas...',
    'Preparing the soil...',
  ],
  forge: [
    'Heating the forge...',
    'Preparing the workshop...',
    'Gathering the tools...',
    'Setting up the anvil...',
    'Ready to build...',
  ],
  coalition: [
    'Convening the council...',
    'Aligning perspectives...',
    'Forging connections...',
    'Building consensus...',
    'Synthesizing viewpoints...',
  ],
  park: [
    'Setting the stage...',
    'Preparing the scenario...',
    'Calibrating tension...',
    'Assembling the cast...',
    'Tuning the dramatic arc...',
  ],
  domain: [
    'Analyzing the situation...',
    'Modeling dynamics...',
    'Running simulations...',
    'Evaluating scenarios...',
    'Preparing recommendations...',
  ],
} as const;

/**
 * Get a random loading message for a jewel.
 */
export function getLoadingMessage(jewel: JewelName): string {
  const messages = LOADING_MESSAGES[jewel];
  return messages[Math.floor(Math.random() * messages.length)];
}

/**
 * Generic loading messages (when no jewel context).
 */
export const GENERIC_LOADING_MESSAGES = [
  'Gathering thoughts...',
  'Processing request...',
  'Working on it...',
  'Just a moment...',
  'Almost there...',
] as const;

// =============================================================================
// Error Messages
// =============================================================================

/**
 * Empathetic error titles by category.
 * These replace generic "Error" titles with human-friendly language.
 */
export const ERROR_TITLES: Record<string, string> = {
  network: 'Lost in the Ether',
  timeout: 'Taking Too Long',
  notFound: 'Cannot Find That',
  permission: 'Access Restricted',
  validation: 'Something Seems Off',
  rateLimited: 'Slow Down a Bit',
  serverError: 'Unexpected Turbulence',
  unknown: 'Something Went Wrong',
} as const;

/**
 * Helpful error suggestions by category.
 */
export const ERROR_SUGGESTIONS: Record<string, string[]> = {
  network: [
    'Check your internet connection',
    'Try refreshing the page',
    'The server might be temporarily unavailable',
  ],
  timeout: [
    'The operation is taking longer than expected',
    'Try again in a moment',
    'Consider simplifying your request',
  ],
  notFound: [
    'This resource may have been moved',
    'Double-check the address',
    'Start from the homepage',
  ],
  permission: [
    'You may need to sign in',
    'Request access from the owner',
    'Check your account permissions',
  ],
  validation: [
    'Review the input fields',
    'Check for required fields',
    'Make sure the format is correct',
  ],
  rateLimited: [
    'Wait a moment before trying again',
    'Reduce the frequency of requests',
    'Consider batching operations',
  ],
  serverError: [
    'This is not your fault',
    'We are looking into it',
    'Try again in a few minutes',
  ],
  unknown: [
    'Refresh the page and try again',
    'Clear your browser cache',
    'Contact support if this persists',
  ],
} as const;

/**
 * Get an empathetic error message.
 */
export function getErrorMessage(category: string): { title: string; suggestions: string[] } {
  return {
    title: ERROR_TITLES[category] || ERROR_TITLES.unknown,
    suggestions: ERROR_SUGGESTIONS[category] || ERROR_SUGGESTIONS.unknown,
  };
}

// =============================================================================
// Empty State Messages
// =============================================================================

/**
 * Empty state invitations by context.
 * These replace "No data" with actionable invitations.
 */
export const EMPTY_STATE_MESSAGES: Record<string, { title: string; description: string; action?: string }> = {
  // Gardener
  noSessions: {
    title: 'No garden plots yet',
    description: 'Start a new tending session to begin cultivating your ideas.',
    action: 'Plant the first seed',
  },
  noArtifacts: {
    title: 'Nothing harvested yet',
    description: 'Artifacts will appear here as you work through your session.',
  },
  noLearnings: {
    title: 'No learnings captured',
    description: 'Insights will crystallize here during the REFLECT phase.',
  },

  // Brain
  noQueries: {
    title: 'Ready to explore',
    description: 'Ask a question to begin traversing the knowledge graph.',
    action: 'Ask something',
  },
  noResults: {
    title: 'No matches found',
    description: 'Try different keywords or broaden your search.',
  },

  // Gestalt
  noNodes: {
    title: 'Empty architecture',
    description: 'Add nodes to start mapping your system topology.',
    action: 'Add first node',
  },
  noConnections: {
    title: 'No relationships yet',
    description: 'Connect nodes to reveal the structure of your system.',
  },

  // Atelier
  noArtisans: {
    title: 'Workshop awaits',
    description: 'Invite artisans to begin collaborative creation.',
    action: 'Summon artisans',
  },
  noCreations: {
    title: 'Canvas is blank',
    description: 'Creations will appear as the artisans work.',
  },

  // Coalition
  noCitizens: {
    title: 'Town is quiet',
    description: 'Citizens will gather when you create a coalition.',
    action: 'Form coalition',
  },
  noCoalitions: {
    title: 'No coalitions formed',
    description: 'Groups of citizens can work together on shared goals.',
    action: 'Start a coalition',
  },

  // Park
  noScenarios: {
    title: 'Stage is empty',
    description: 'Start a scenario to practice crisis response.',
    action: 'Begin scenario',
  },
  noMasks: {
    title: 'No masks available',
    description: 'Masks become available as the scenario progresses.',
  },

  // Domain
  noSimulations: {
    title: 'No simulations running',
    description: 'Configure and run a domain simulation to begin.',
    action: 'Create simulation',
  },

  // Generic
  noItems: {
    title: 'Nothing here yet',
    description: 'Items will appear as you interact with the system.',
  },
  noData: {
    title: 'Awaiting data',
    description: 'Data will flow in once connected.',
  },
} as const;

/**
 * Get empty state content.
 */
export function getEmptyState(context: string): { title: string; description: string; action?: string } {
  return EMPTY_STATE_MESSAGES[context] || EMPTY_STATE_MESSAGES.noItems;
}

// =============================================================================
// Success Messages
// =============================================================================

/**
 * Success celebration messages.
 */
export const SUCCESS_MESSAGES: Record<string, string> = {
  created: 'Created successfully',
  saved: 'Changes saved',
  deleted: 'Removed successfully',
  submitted: 'Submitted',
  completed: 'Completed',
  connected: 'Connected',
  synced: 'Synced',
  exported: 'Exported',
  imported: 'Imported',
} as const;

// =============================================================================
// Button Labels (Verbs)
// =============================================================================

/**
 * Standard button labels using action verbs.
 * Following the principle: labels are verbs for actions.
 */
export const BUTTON_LABELS = {
  // CRUD operations
  create: 'Create',
  save: 'Save',
  delete: 'Delete',
  edit: 'Edit',
  update: 'Update',

  // Navigation
  back: 'Go back',
  next: 'Continue',
  finish: 'Finish',
  cancel: 'Cancel',

  // Actions
  submit: 'Submit',
  confirm: 'Confirm',
  retry: 'Try again',
  refresh: 'Refresh',
  dismiss: 'Dismiss',

  // Jewel-specific
  tend: 'Tend',           // Gardener
  query: 'Query',         // Brain
  visualize: 'Visualize', // Gestalt
  create_art: 'Create',   // Atelier (verb)
  convene: 'Convene',     // Coalition
  simulate: 'Simulate',   // Park/Domain
} as const;

// =============================================================================
// Tooltip Templates
// =============================================================================

/**
 * Helpful tooltip content (not redundant with labels).
 */
export const TOOLTIPS = {
  // Gardener
  sessionPhase: (phase: string) => `Currently in ${phase} phase`,
  seasonInfo: (season: string) => `Garden is in ${season} - this affects change plasticity`,
  entropyBudget: (remaining: number) => `${remaining} entropy points remaining this session`,

  // Brain
  confidenceScore: (score: number) => `${Math.round(score * 100)}% confidence in this result`,
  sourceCount: (count: number) => `Based on ${count} source${count !== 1 ? 's' : ''}`,

  // Gestalt
  nodeCount: (count: number) => `${count} node${count !== 1 ? 's' : ''} in this view`,
  connectionStrength: (strength: number) => `Connection strength: ${Math.round(strength * 100)}%`,

  // Park
  consentDebt: (debt: number) => `Consent debt: ${Math.round(debt * 100)}% - affects serendipity`,
  forcesRemaining: (count: number) => `${count} force${count !== 1 ? 's' : ''} remaining`,

  // Generic
  lastUpdated: (date: Date) => `Last updated ${date.toLocaleString()}`,
  itemCount: (count: number, label: string) => `${count} ${label}${count !== 1 ? 's' : ''}`,
} as const;
