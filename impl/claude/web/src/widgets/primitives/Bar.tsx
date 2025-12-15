/**
 * Bar: Progress/capacity bar widget.
 *
 * Renders a horizontal or vertical bar with configurable:
 * - fill value (0.0 to 1.0)
 * - width (number of character cells)
 * - style (solid blocks or dots)
 * - optional label
 */

import React, { memo, useMemo } from 'react';
import type { BarJSON } from '@/reactive/types';

export interface BarProps extends Omit<BarJSON, 'type' | 'glyphs'> {
  className?: string;
}

export const Bar = memo(function Bar({
  value,
  width,
  orientation,
  style,
  label,
  fg,
  className,
}: BarProps) {
  const filledCount = Math.round(value * width);

  const barStyle: React.CSSProperties = {
    color: fg || undefined,
    display: orientation === 'vertical' ? 'flex' : 'inline-flex',
    flexDirection: orientation === 'vertical' ? 'column' : 'row',
  };

  const chars = useMemo(() => {
    const filled = style === 'dots' ? '●' : '█';
    const empty = style === 'dots' ? '○' : '░';
    return Array(width)
      .fill(null)
      .map((_, i) => (i < filledCount ? filled : empty));
  }, [width, filledCount, style]);

  return (
    <div className={`kgents-bar font-mono ${className || ''}`} style={barStyle}>
      {label && <span className="mr-2 text-gray-600">{label}:</span>}
      {chars.map((char, i) => (
        <span key={i}>{char}</span>
      ))}
    </div>
  );
});

export default Bar;
