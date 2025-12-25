/**
 * Unified Witness Hook
 *
 * A single hook that provides witnessing capabilities across all surfaces:
 * - Hypergraph Editor (navigation)
 * - Portal Tokens (expansion/collapse)
 * - Chat Sessions (turns)
 * - Any future surface
 *
 * "Every action leaves a mark. The mark IS the witness."
 *
 * @see spec/synthesis/RADICAL_TRANSFORMATION.md
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  createMark,
  subscribeToMarks,
  getRecentMarks,
  Mark,
  CreateMarkRequest,
} from '../api/witness';

// =============================================================================
// Types
// =============================================================================

/**
 * Domain of the witnessed action.
 */
export type WitnessDomain = 'navigation' | 'portal' | 'chat' | 'edit' | 'system';

/**
 * Navigation-specific action types.
 */
export type NavigationAction =
  | 'derivation'      // gD - go to derivation parent
  | 'loss_gradient'   // gl/gh - follow loss gradient
  | 'sibling'         // gj/gk - navigate siblings
  | 'definition'      // gd - go to definition
  | 'references'      // gr - go to references
  | 'tests'           // gt - go to tests
  | 'back'            // go back in trail
  | 'forward'         // go forward in trail
  | 'direct';         // direct path navigation

/**
 * Portal-specific action types.
 */
export type PortalAction =
  | 'expand'          // zo - expand portal
  | 'collapse'        // zc - collapse portal
  | 'toggle'          // za - toggle portal
  | 'cure';           // cure unparsed portal

/**
 * Chat-specific action types.
 */
export type ChatAction =
  | 'message'         // send message
  | 'fork'            // create branch
  | 'merge'           // merge branches
  | 'checkpoint'      // create checkpoint
  | 'rewind';         // rewind to checkpoint

/**
 * Extended mark with domain information.
 */
export interface DomainMark extends Mark {
  domain: WitnessDomain;
  actionType?: NavigationAction | PortalAction | ChatAction;
  metadata?: Record<string, unknown>;
}

/**
 * Options for creating a witnessed mark.
 */
export interface WitnessOptions {
  /** Domain of the action */
  domain: WitnessDomain;

  /** Specific action type within the domain */
  actionType?: NavigationAction | PortalAction | ChatAction;

  /** Human-readable action description */
  action: string;

  /** Why this action was taken */
  reasoning?: string;

  /** Which principles this action honors */
  principles?: string[];

  /** Parent mark for causal lineage */
  parentMarkId?: string;

  /** Additional metadata */
  metadata?: Record<string, unknown>;

  /** Fire-and-forget mode (don't wait for response) */
  fireAndForget?: boolean;
}

/**
 * Principle mapping for different action types.
 */
const ACTION_PRINCIPLES: Record<string, string[]> = {
  // Navigation
  derivation: ['generative'],           // Following proof chains is generative
  loss_gradient: ['ethical'],           // Seeking truth/stability
  sibling: ['composable'],              // Exploring related structures
  definition: ['generative'],           // Following definitions
  references: ['composable'],           // Understanding connections
  tests: ['ethical', 'composable'],     // Verifying behavior
  back: ['tasteful'],                   // Intentional retreat
  forward: ['tasteful'],                // Intentional advance
  direct: ['tasteful'],                 // Purposeful navigation

  // Portal
  expand: ['composable', 'joy_inducing'],  // Bringing docs to you
  collapse: ['tasteful'],                  // Cleaning up
  toggle: ['joy_inducing'],                // Quick exploration
  cure: ['generative'],                    // Resolving ambiguity

  // Chat
  message: ['ethical', 'joy_inducing'],    // Communication
  fork: ['heterarchical'],                 // Exploring alternatives
  merge: ['composable'],                   // Synthesizing
  checkpoint: ['ethical'],                 // Preserving state
  rewind: ['ethical'],                     // Correcting course
};

/**
 * Get default principles for an action type.
 */
function getDefaultPrinciples(actionType?: string): string[] {
  if (!actionType) return [];
  return ACTION_PRINCIPLES[actionType] ?? [];
}

// =============================================================================
// Hook Implementation
// =============================================================================

/**
 * Unified witness hook for all surfaces.
 *
 * @example
 * // In HypergraphEditor
 * const { witness, recentMarks, isConnected } = useWitness();
 *
 * // Witness a navigation
 * await witness({
 *   domain: 'navigation',
 *   actionType: 'derivation',
 *   action: `Navigated to derivation parent: ${parentPath}`,
 *   reasoning: 'Following proof chain to understand justification',
 * });
 *
 * // In PortalToken
 * witness({
 *   domain: 'portal',
 *   actionType: 'expand',
 *   action: `Expanded portal: ${edgeType} -> ${destination}`,
 *   fireAndForget: true,
 * });
 */
export function useWitness(options?: {
  /** Auto-subscribe to real-time marks */
  subscribe?: boolean;
  /** Filter marks by domain */
  filterDomain?: WitnessDomain;
  /** Maximum recent marks to track */
  maxRecent?: number;
}) {
  const { subscribe = false, filterDomain, maxRecent = 50 } = options ?? {};

  // State
  const [recentMarks, setRecentMarks] = useState<DomainMark[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);

  // Refs for stable callbacks
  const unsubscribeRef = useRef<(() => void) | null>(null);
  const pendingMarksRef = useRef<Map<string, WitnessOptions>>(new Map());

  /**
   * Create a witnessed mark.
   */
  const witness = useCallback(
    async (opts: WitnessOptions): Promise<Mark | null> => {
      const {
        domain,
        actionType,
        action,
        reasoning,
        principles,
        parentMarkId,
        metadata,
        fireAndForget = false,
      } = opts;

      // Build the mark request
      const request: CreateMarkRequest = {
        action: `[${domain}${actionType ? `:${actionType}` : ''}] ${action}`,
        reasoning,
        principles: principles ?? getDefaultPrinciples(actionType),
        parent_mark_id: parentMarkId,
      };

      // Generate temporary ID for fire-and-forget tracking
      const tempId = `temp-${Date.now()}-${Math.random().toString(36).slice(2)}`;

      if (fireAndForget) {
        // Fire and forget - don't wait for response
        pendingMarksRef.current.set(tempId, opts);
        setPendingCount((c) => c + 1);

        createMark(request)
          .then((mark) => {
            // Add to recent marks
            setRecentMarks((prev) => {
              const domainMark: DomainMark = {
                ...mark,
                domain,
                actionType,
                metadata,
              };
              const next = [domainMark, ...prev].slice(0, maxRecent);
              return next;
            });
          })
          .catch((error) => {
            console.error('[useWitness] Fire-and-forget mark failed:', error);
          })
          .finally(() => {
            pendingMarksRef.current.delete(tempId);
            setPendingCount((c) => Math.max(0, c - 1));
          });

        return null;
      }

      // Wait for response
      try {
        const mark = await createMark(request);

        // Add to recent marks
        setRecentMarks((prev) => {
          const domainMark: DomainMark = {
            ...mark,
            domain,
            actionType,
            metadata,
          };
          const next = [domainMark, ...prev].slice(0, maxRecent);
          return next;
        });

        return mark;
      } catch (error) {
        console.error('[useWitness] Mark creation failed:', error);
        return null;
      }
    },
    [maxRecent]
  );

  /**
   * Convenience method for navigation witnessing.
   */
  const witnessNavigation = useCallback(
    (
      actionType: NavigationAction,
      fromPath: string | null,
      toPath: string,
      reasoning?: string
    ) => {
      return witness({
        domain: 'navigation',
        actionType,
        action: fromPath
          ? `${fromPath} -> ${toPath}`
          : `Navigated to ${toPath}`,
        reasoning: reasoning ?? `Navigated via ${actionType}`,
        fireAndForget: true,
        metadata: { fromPath, toPath },
      });
    },
    [witness]
  );

  /**
   * Convenience method for portal witnessing.
   */
  const witnessPortal = useCallback(
    (
      actionType: PortalAction,
      edgeType: string,
      destination: string,
      depth?: number
    ) => {
      return witness({
        domain: 'portal',
        actionType,
        action: `[${edgeType}] -> ${destination}`,
        reasoning: `Portal ${actionType} at depth ${depth ?? 0}`,
        fireAndForget: true,
        metadata: { edgeType, destination, depth },
      });
    },
    [witness]
  );

  /**
   * Convenience method for chat witnessing.
   */
  const witnessChat = useCallback(
    (
      actionType: ChatAction,
      sessionId: string,
      turnNumber: number,
      reasoning?: string
    ) => {
      return witness({
        domain: 'chat',
        actionType,
        action: `Session ${sessionId} turn ${turnNumber}`,
        reasoning,
        fireAndForget: true,
        metadata: { sessionId, turnNumber },
      });
    },
    [witness]
  );

  // Subscribe to real-time marks
  useEffect(() => {
    if (!subscribe) return;

    const cleanup = subscribeToMarks(
      (mark) => {
        // Filter by domain if specified
        const domain = extractDomain(mark.action);
        if (filterDomain && domain !== filterDomain) return;

        // Add to recent marks
        setRecentMarks((prev) => {
          const domainMark: DomainMark = {
            ...mark,
            domain: domain ?? 'system',
          };
          const next = [domainMark, ...prev].slice(0, maxRecent);
          return next;
        });
      },
      {
        onConnect: () => setIsConnected(true),
        onDisconnect: () => setIsConnected(false),
      }
    );

    unsubscribeRef.current = cleanup;

    return () => {
      cleanup();
      unsubscribeRef.current = null;
    };
  }, [subscribe, filterDomain, maxRecent]);

  // Load initial recent marks
  useEffect(() => {
    getRecentMarks({ limit: maxRecent, today: true })
      .then((marks) => {
        const domainMarks = marks.map((mark) => ({
          ...mark,
          domain: extractDomain(mark.action) ?? ('system' as WitnessDomain),
        }));
        setRecentMarks(
          filterDomain
            ? domainMarks.filter((m) => m.domain === filterDomain)
            : domainMarks
        );
      })
      .catch((error) => {
        console.error('[useWitness] Failed to load recent marks:', error);
      });
  }, [filterDomain, maxRecent]);

  return {
    // Core witness function
    witness,

    // Domain-specific convenience methods
    witnessNavigation,
    witnessPortal,
    witnessChat,

    // State
    recentMarks,
    isConnected,
    pendingCount,

    // Utilities
    hasPending: pendingCount > 0,
  };
}

// =============================================================================
// Utilities
// =============================================================================

/**
 * Extract domain from mark action string.
 *
 * Actions are formatted as: [domain:actionType] description
 * e.g., [navigation:derivation] Navigated to parent: spec/foo.md
 */
function extractDomain(action: string): WitnessDomain | null {
  const match = action.match(/^\[(\w+)(?::\w+)?\]/);
  if (!match) return null;

  const domain = match[1].toLowerCase();
  if (
    domain === 'navigation' ||
    domain === 'portal' ||
    domain === 'chat' ||
    domain === 'edit' ||
    domain === 'system'
  ) {
    return domain;
  }
  return null;
}

/**
 * Extract action type from mark action string.
 */
export function extractActionType(action: string): string | null {
  const match = action.match(/^\[\w+:(\w+)\]/);
  return match ? match[1] : null;
}

/**
 * Format mark for display.
 */
export function formatMark(mark: DomainMark): string {
  const action = mark.action.replace(/^\[\w+(?::\w+)?\]\s*/, '');
  return action;
}

// =============================================================================
// Export
// =============================================================================

export default useWitness;
