/**
 * GLYPH COMPONENT
 *
 * Renders kgents glyphs with STARK BIOME aesthetics.
 *
 * Philosophy:
 * - Mathematical notation, not emoji
 * - Monochrome + single accent
 * - Breathing animation uses 4-7-8 asymmetric timing
 * - Stillness by default, life earned through action
 *
 * Usage:
 *   <Glyph name="status.healthy" />
 *   <Glyph name="actions.witness" size="lg" />
 *   <Glyph name="jewels.brain" breathing />
 *   <Glyph name="contexts.world" color="var(--life-sage)" />
 */

import React from 'react';
import { getGlyph } from './glyphs';
import './glyph.css';

export interface GlyphProps {
  /**
   * Glyph name using dot notation
   * Examples: 'status.healthy', 'actions.witness', 'jewels.brain'
   */
  name: string;

  /**
   * Size variant
   * xs: 10px, sm: 12px, md: 14px, lg: 18px
   */
  size?: 'xs' | 'sm' | 'md' | 'lg';

  /**
   * Optional color override
   * Defaults to inherit from parent
   */
  color?: string;

  /**
   * Enable 4-7-8 asymmetric breathing animation
   * "Stillness, then life" — use sparingly
   */
  breathing?: boolean;

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Accessible label for screen readers
   * If not provided, uses glyph name
   */
  'aria-label'?: string;
}

export const Glyph: React.FC<GlyphProps> = ({
  name,
  size = 'md',
  color,
  breathing = false,
  className = '',
  'aria-label': ariaLabel,
}) => {
  const glyph = getGlyph(name);

  if (!glyph) {
    console.warn(`[Glyph] Unknown glyph: "${name}"`);
    return null;
  }

  const classes = [
    'glyph',
    `glyph--${size}`,
    breathing && 'glyph--breathing',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  const style: React.CSSProperties = color ? { color } : {};

  return (
    <span
      className={classes}
      style={style}
      role="img"
      aria-label={ariaLabel || name.replace('.', ' ')}
    >
      {glyph}
    </span>
  );
};

export default Glyph;
