/**
 * Glyph: Atomic visual unit for the reactive widget system.
 *
 * A glyph is a single character with optional styling:
 * - foreground/background colors
 * - phase-based semantics
 * - animations (pulse, blink, breathe, wiggle)
 * - distortion effects (blur, skew, jitter)
 */

import { memo } from 'react';
import type { CSSProperties } from 'react';
import type { GlyphJSON } from '@/reactive/types';

export interface GlyphProps extends Omit<GlyphJSON, 'type'> {
  className?: string;
}

export const Glyph = memo(function Glyph({
  char,
  phase,
  // entropy is part of API but not rendered directly - used for composition
  entropy: _entropy,
  animate,
  fg,
  bg,
  distortion,
  className,
}: GlyphProps) {
  const style: CSSProperties = {
    color: fg || undefined,
    backgroundColor: bg || undefined,
  };

  // Apply distortion if present
  if (distortion) {
    const transforms: string[] = [];
    if (distortion.skew !== 0) transforms.push(`skewX(${distortion.skew}deg)`);
    if (distortion.jitter_x !== 0 || distortion.jitter_y !== 0) {
      transforms.push(`translate(${distortion.jitter_x}px, ${distortion.jitter_y}px)`);
    }
    if (transforms.length > 0) {
      style.transform = transforms.join(' ');
    }
    if (distortion.blur > 0) {
      style.filter = `blur(${distortion.blur}px)`;
    }
  }

  // Animation class
  const animClass = animate !== 'none' ? `animate-${animate}` : '';

  return (
    <span
      className={`kgents-glyph font-mono ${animClass} ${className || ''}`}
      style={style}
      data-phase={phase}
    >
      {char}
    </span>
  );
});

export default Glyph;
