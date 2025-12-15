/**
 * Sparkline: Activity sparkline widget.
 *
 * Renders a series of values as vertical bar characters,
 * creating a mini time-series visualization.
 */

import React, { memo, useMemo } from 'react';
import type { SparklineJSON } from '@/reactive/types';
import { SPARK_CHARS } from '../constants';

export interface SparklineProps extends Omit<SparklineJSON, 'type' | 'glyphs'> {
  className?: string;
}

export const Sparkline = memo(function Sparkline({
  values,
  label,
  fg,
  className,
}: SparklineProps) {
  const chars = useMemo(() => {
    return values.map((v) => {
      const idx = Math.min(Math.floor(v * (SPARK_CHARS.length - 1)), SPARK_CHARS.length - 1);
      return SPARK_CHARS[idx];
    });
  }, [values]);

  const style: React.CSSProperties = {
    color: fg || '#28a745',
  };

  return (
    <div
      className={`kgents-sparkline font-mono inline-flex items-end ${className || ''}`}
      style={style}
    >
      {label && <span className="mr-2 text-gray-600">{label}:</span>}
      {chars.map((char, i) => (
        <span key={i}>{char}</span>
      ))}
    </div>
  );
});

export default Sparkline;
