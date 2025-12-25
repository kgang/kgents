/**
 * KGENTS ICON SYSTEM
 *
 * Export everything from the icon/glyph system.
 *
 * Usage:
 *   import { Glyph, GLYPHS } from '@/components/icons';
 *   import { ArrowLeft } from '@/components/icons';
 *   import { GlyphShowcase } from '@/components/icons';
 */

// Glyph component and constants
export { Glyph } from './Glyph';
export type { GlyphProps } from './Glyph';
export {
  GLYPHS,
  getGlyph,
  getGlyphCategory,
  GLYPH_CATEGORIES,
} from './glyphs';

// Showcase/demo component
export { GlyphShowcase } from './GlyphShowcase';

// Lucide icon allowlist
export * from './LucideAllowlist';
