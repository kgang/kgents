/**
 * BlockquoteToken — Quoted text with visual emphasis.
 *
 * Renders > quoted text blocks with left border accent.
 * Supports multi-line quotes.
 *
 * "Quoted text block with optional attribution."
 */

import { memo } from 'react';

import './tokens.css';

interface BlockquoteTokenProps {
  content: string;
  attribution?: string;
  className?: string;
}

export const BlockquoteToken = memo(function BlockquoteToken({
  content,
  attribution,
  className,
}: BlockquoteTokenProps) {
  // Strip leading > and spaces from each line for clean display
  const cleanContent = content
    .split('\n')
    .map((line) => line.replace(/^>\s?/, ''))
    .join('\n')
    .trim();

  return (
    <blockquote className={`blockquote-token ${className ?? ''}`}>
      <div className="blockquote-token__content">{cleanContent}</div>
      {attribution && <footer className="blockquote-token__attribution">— {attribution}</footer>}
    </blockquote>
  );
});
