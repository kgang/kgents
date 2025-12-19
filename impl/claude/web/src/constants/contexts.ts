/**
 * AGENTESE Context Constants
 *
 * Visual and semantic information for the five AGENTESE contexts.
 * Used by NavigationTree, ConceptHome, and context-aware UI components.
 *
 * "Five Contexts: world, self, concept, void, time — no kitchen-sink anti-pattern"
 * — spec/principles.md
 *
 * @see spec/protocols/agentese.md
 * @see spec/principles.md - AD-010: The Habitat Guarantee
 */

import {
  Globe,
  User,
  BookOpen,
  Sparkles,
  Clock,
  type LucideIcon,
} from 'lucide-react';
import type { AGENTESEContext } from '@/lib/habitat';

// =============================================================================
// Types
// =============================================================================

/**
 * Visual and semantic metadata for an AGENTESE context.
 */
export interface ContextInfo {
  /** Lucide icon component */
  icon: LucideIcon;
  /** Tailwind text color class */
  color: string;
  /** Tailwind background color class for badges */
  bgColor: string;
  /** Human-readable label */
  label: string;
  /** One-line description */
  description: string;
}

// =============================================================================
// Context Information
// =============================================================================

/**
 * Visual and semantic information for each AGENTESE context.
 *
 * These mappings are used for:
 * - NavigationTree context icons and colors
 * - ConceptHome context badges
 * - PathProjection header styling
 * - Observer-aware UI adaptations
 */
export const CONTEXT_INFO: Record<AGENTESEContext, ContextInfo> = {
  world: {
    icon: Globe,
    color: 'text-green-400',
    bgColor: 'bg-green-900/30',
    label: 'World',
    description: 'External entities and environments',
  },
  self: {
    icon: User,
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-900/30',
    label: 'Self',
    description: 'Internal memory and capability',
  },
  concept: {
    icon: BookOpen,
    color: 'text-violet-400',
    bgColor: 'bg-violet-900/30',
    label: 'Concept',
    description: 'Abstract definitions and logic',
  },
  void: {
    icon: Sparkles,
    color: 'text-pink-400',
    bgColor: 'bg-pink-900/30',
    label: 'Void',
    description: 'Entropy and serendipity',
  },
  time: {
    icon: Clock,
    color: 'text-amber-400',
    bgColor: 'bg-amber-900/30',
    label: 'Time',
    description: 'Traces and schedules',
  },
} as const;

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get context info with fallback to 'world' for unknown contexts.
 */
export function getContextInfo(context: string): ContextInfo {
  const key = context as AGENTESEContext;
  return CONTEXT_INFO[key] ?? CONTEXT_INFO.world;
}

/**
 * Get the icon for a context.
 */
export function getContextIcon(context: AGENTESEContext): LucideIcon {
  return CONTEXT_INFO[context].icon;
}

/**
 * Get the color class for a context.
 */
export function getContextColor(context: AGENTESEContext): string {
  return CONTEXT_INFO[context].color;
}

/**
 * Get the background color class for a context badge.
 */
export function getContextBgColor(context: AGENTESEContext): string {
  return CONTEXT_INFO[context].bgColor;
}
