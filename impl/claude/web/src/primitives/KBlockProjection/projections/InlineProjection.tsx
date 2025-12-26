/**
 * InlineProjection — Minimal Inline Text
 *
 * Renders K-Block as minimal inline text (just title or ID).
 * Useful for embedding within other text or lists.
 */

import { memo } from 'react';
import type { ProjectionComponentProps } from '../types';
import './InlineProjection.css';

export const InlineProjection = memo(function InlineProjection({
  kblock,
  className = '',
}: ProjectionComponentProps) {
  const title = kblock.path.split('/').pop() || kblock.id;

  return (
    <span className={`inline-projection ${className}`} title={kblock.path}>
      {title}
    </span>
  );
});
