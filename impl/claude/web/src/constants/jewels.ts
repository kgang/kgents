/**
 * Crown Jewel Colors, Icons, and Emoji
 *
 * Each Crown Jewel has a semantic color that defines its personality.
 * Colors are derived from meaning, not aesthetic whim.
 *
 * IMPORTANT: Per visual-system.md and os-shell.md, kgents uses Lucide icons
 * exclusively for semantic iconography. Emojis are NOT used in kgents-authored
 * copy. JEWEL_EMOJI is deprecated - use JEWEL_ICONS instead.
 *
 * @see docs/creative/visual-system.md
 * @see spec/protocols/os-shell.md
 */

import {
  Brain,
  Network,
  Leaf,
  Palette,
  Users,
  Theater,
  Building,
  type LucideIcon,
} from 'lucide-react';

export type JewelName =
  | 'brain'
  | 'gestalt'
  | 'gardener'
  | 'forge'
  | 'coalition'
  | 'park'
  | 'domain';

export interface JewelColor {
  /** Primary brand color for the jewel */
  primary: string;
  /** Accent color for interactive states */
  accent: string;
  /** Background color for jewel-specific surfaces */
  bg: string;
}

/**
 * Crown Jewel Color Palette
 *
 * Semantic meanings:
 * - brain: Knowledge (Cyan) - understanding, memory
 * - gestalt: Growth (Green) - health, progress
 * - gardener: Cultivation (Lime) - nurturing, emergence
 * - forge: Creation (Amber) - creativity, warmth
 * - coalition: Collaboration (Violet) - synthesis, harmony
 * - park: Drama (Pink) - narrative, performance
 * - domain: Urgency (Red) - crisis, alert
 */
export const JEWEL_COLORS: Record<JewelName, JewelColor> = {
  brain: { primary: '#06B6D4', accent: '#0891B2', bg: '#0E7490' }, // Cyan family
  gestalt: { primary: '#22C55E', accent: '#16A34A', bg: '#15803D' }, // Green family
  gardener: { primary: '#84CC16', accent: '#65A30D', bg: '#4D7C0F' }, // Lime family
  forge: { primary: '#F59E0B', accent: '#D97706', bg: '#B45309' }, // Amber family
  coalition: { primary: '#8B5CF6', accent: '#7C3AED', bg: '#6D28D9' }, // Violet family
  park: { primary: '#EC4899', accent: '#DB2777', bg: '#BE185D' }, // Pink family
  domain: { primary: '#EF4444', accent: '#DC2626', bg: '#B91C1C' }, // Red family
} as const;

/**
 * Crown Jewel Icons (Lucide)
 *
 * Per visual-system.md: "kgents uses Lucide icons exclusively for semantic iconography."
 * These replace JEWEL_EMOJI for all kgents-authored copy.
 *
 * Icon guidelines:
 * - Match icon color to jewel color
 * - 24px base size, 20px for compact density
 * - Outline style default, filled for selected/active states
 */
export const JEWEL_ICONS: Record<JewelName, LucideIcon> = {
  brain: Brain, // Cyan family - Knowledge, memory
  gestalt: Network, // Green family - Growth, health
  gardener: Leaf, // Lime family - Cultivation, nurturing
  forge: Palette, // Amber family - Creation, creativity
  coalition: Users, // Violet family - Collaboration, synthesis
  park: Theater, // Pink family - Drama, narrative
  domain: Building, // Red family - Urgency, crisis
} as const;

/**
 * Get jewel icon by name, with fallback to Brain
 */
export function getJewelIcon(name: string): LucideIcon {
  const key = name.toLowerCase() as JewelName;
  return JEWEL_ICONS[key] ?? Brain;
}

/**
 * Crown Jewel Emoji
 *
 * @deprecated Use JEWEL_ICONS instead. Emojis are NOT used in kgents-authored copy.
 * This is kept for backward compatibility with user-generated content only.
 */
export const JEWEL_EMOJI: Record<JewelName, string> = {
  brain: '\u{1F9E0}', // brain
  gestalt: '\u{1F3D7}\u{FE0F}', // building
  gardener: '\u{1F331}', // seedling
  forge: '\u{1F3A8}', // artist palette
  coalition: '\u{1F91D}', // handshake
  park: '\u{1F3AD}', // performing arts
  domain: '\u{1F3DB}\u{FE0F}', // classical building
} as const;

/**
 * Get jewel color by name, with fallback
 */
export function getJewelColor(name: string): JewelColor {
  const key = name.toLowerCase() as JewelName;
  return (
    JEWEL_COLORS[key] ?? {
      primary: '#64748B',
      accent: '#475569',
      bg: '#334155',
    }
  );
}

/**
 * Get jewel emoji by name, with fallback
 */
export function getJewelEmoji(name: string): string {
  const key = name.toLowerCase() as JewelName;
  return JEWEL_EMOJI[key] ?? '\u{2728}'; // sparkles fallback
}

/**
 * Tailwind-friendly color map for extending theme
 */
export const JEWEL_TAILWIND_COLORS = {
  'jewel-brain': JEWEL_COLORS.brain.primary,
  'jewel-brain-accent': JEWEL_COLORS.brain.accent,
  'jewel-brain-bg': JEWEL_COLORS.brain.bg,

  'jewel-gestalt': JEWEL_COLORS.gestalt.primary,
  'jewel-gestalt-accent': JEWEL_COLORS.gestalt.accent,
  'jewel-gestalt-bg': JEWEL_COLORS.gestalt.bg,

  'jewel-gardener': JEWEL_COLORS.gardener.primary,
  'jewel-gardener-accent': JEWEL_COLORS.gardener.accent,
  'jewel-gardener-bg': JEWEL_COLORS.gardener.bg,

  'jewel-forge': JEWEL_COLORS.forge.primary,
  'jewel-forge-accent': JEWEL_COLORS.forge.accent,
  'jewel-forge-bg': JEWEL_COLORS.forge.bg,

  'jewel-coalition': JEWEL_COLORS.coalition.primary,
  'jewel-coalition-accent': JEWEL_COLORS.coalition.accent,
  'jewel-coalition-bg': JEWEL_COLORS.coalition.bg,

  'jewel-park': JEWEL_COLORS.park.primary,
  'jewel-park-accent': JEWEL_COLORS.park.accent,
  'jewel-park-bg': JEWEL_COLORS.park.bg,

  'jewel-domain': JEWEL_COLORS.domain.primary,
  'jewel-domain-accent': JEWEL_COLORS.domain.accent,
  'jewel-domain-bg': JEWEL_COLORS.domain.bg,
} as const;
