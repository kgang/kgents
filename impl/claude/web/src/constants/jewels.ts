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

import { Brain, Palette, Building, Sprout, type LucideIcon } from 'lucide-react';

export type JewelName = 'brain' | 'gardener' | 'forge' | 'domain';
// gestalt, coalition removed 2025-12-21

export interface JewelColor {
  /** Primary brand color for the jewel */
  primary: string;
  /** Accent color for interactive states */
  accent: string;
  /** Background color for jewel-specific surfaces */
  bg: string;
}

/**
 * Crown Jewel Color Palette — STARK BIOME Edition
 *
 * STARK BIOME: "The frame is humble. The content glows."
 * Jewel colors are MUTED — earned, not given.
 *
 * Semantic meanings:
 * - brain: Knowledge (Teal Moss) - understanding quietly growing
 * - gardener: Nurturing (Fern) - growth, tending
 * - forge/atelier: Creation (Umber) - creative warmth, earned glow
 * - domain: Urgency (Muted Rust) - alert without alarm
 *
 * Removed 2025-12-21: gestalt, coalition
 *
 * @see docs/creative/stark-biome-moodboard.md
 */
export const JEWEL_COLORS: Record<JewelName, JewelColor> = {
  // STARK BIOME: Muted teal moss — knowledge growing quietly
  brain: { primary: '#4A6B6B', accent: '#5A7B7B', bg: '#3A5B5B' },
  // STARK BIOME: Fern family — nurturing growth
  gardener: { primary: '#6B8B6B', accent: '#7B9B7B', bg: '#5A7B5A' },
  // STARK BIOME: Umber family — creative warmth (same as atelier)
  forge: { primary: '#8B7355', accent: '#9B8365', bg: '#7B6345' },
  // STARK BIOME: Muted rust — alert without alarm (per state-alert)
  domain: { primary: '#8B5A4A', accent: '#9B6A5A', bg: '#7B4A3A' },
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
  gardener: Sprout, // Lime family - Growth, nurturing
  forge: Palette, // Amber family - Creation, creativity
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
  gardener: '\u{1F331}', // seedling
  forge: '\u{1F3A8}', // artist palette
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

  'jewel-gardener': JEWEL_COLORS.gardener.primary,
  'jewel-gardener-accent': JEWEL_COLORS.gardener.accent,
  'jewel-gardener-bg': JEWEL_COLORS.gardener.bg,

  'jewel-forge': JEWEL_COLORS.forge.primary,
  'jewel-forge-accent': JEWEL_COLORS.forge.accent,
  'jewel-forge-bg': JEWEL_COLORS.forge.bg,

  'jewel-domain': JEWEL_COLORS.domain.primary,
  'jewel-domain-accent': JEWEL_COLORS.domain.accent,
  'jewel-domain-bg': JEWEL_COLORS.domain.bg,
} as const;
