/**
 * PrincipleToken — Reference to architectural principles.
 *
 * Renders principle references like:
 *   (AD-009) Density-Content Isomorphism
 *   (Tasteful) Each agent serves a clear purpose
 *   (Composable) Agents are morphisms in a category
 *
 * Hover shows principle summary.
 * Click navigates to full principle definition.
 *
 * @see spec/principles.md
 */

import { memo, useCallback, useState } from 'react';

import './tokens.css';

// =============================================================================
// Types
// =============================================================================

export type PrincipleCategory = 'architectural' | 'constitutional' | 'operational';

interface PrincipleTokenProps {
  /** Principle identifier (e.g., "AD-009", "Tasteful") */
  principle: string;
  /** Short description/title */
  title?: string;
  /** Full description (shown on hover) */
  description?: string;
  /** Category for styling */
  category?: PrincipleCategory;
  /** Called when clicked */
  onClick?: (principle: string) => void;
  /** Additional class names */
  className?: string;
}

// =============================================================================
// Principle metadata (could be fetched from API)
// =============================================================================

const PRINCIPLE_DATA: Record<
  string,
  { title: string; description: string; category: PrincipleCategory }
> = {
  'AD-009': {
    title: 'Density-Content Isomorphism',
    description: 'More space → more content; compact mode → essential only.',
    category: 'architectural',
  },
  'AD-008': {
    title: 'Simplifying Isomorphisms',
    description: 'Reduce complexity through natural equivalences.',
    category: 'architectural',
  },
  Tasteful: {
    title: 'Tasteful',
    description: 'Each agent serves a clear, justified purpose.',
    category: 'constitutional',
  },
  Curated: {
    title: 'Curated',
    description: 'Intentional selection over exhaustive cataloging.',
    category: 'constitutional',
  },
  Ethical: {
    title: 'Ethical',
    description: 'Agents augment human capability, never replace judgment.',
    category: 'constitutional',
  },
  'Joy-Inducing': {
    title: 'Joy-Inducing',
    description: 'Delight in interaction.',
    category: 'constitutional',
  },
  Composable: {
    title: 'Composable',
    description: 'Agents are morphisms in a category (>> composition).',
    category: 'constitutional',
  },
  Heterarchical: {
    title: 'Heterarchical',
    description: 'Agents exist in flux, not fixed hierarchy.',
    category: 'constitutional',
  },
  Generative: {
    title: 'Generative',
    description: 'Spec is compression; implementation is expansion.',
    category: 'constitutional',
  },
};

// =============================================================================
// Component
// =============================================================================

export const PrincipleToken = memo(function PrincipleToken({
  principle,
  title,
  description,
  category,
  onClick,
  className,
}: PrincipleTokenProps) {
  const [isHovered, setIsHovered] = useState(false);

  // Try to get metadata from built-in data
  const metadata = PRINCIPLE_DATA[principle];
  const displayTitle = title || metadata?.title || principle;
  const displayDescription = description || metadata?.description;
  const displayCategory = category || metadata?.category || 'architectural';

  const handleClick = useCallback(() => {
    onClick?.(principle);
  }, [principle, onClick]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onClick?.(principle);
      }
    },
    [principle, onClick]
  );

  return (
    <span
      className={`principle-token principle-token--${displayCategory} ${className ?? ''}`}
      data-principle={principle}
      data-category={displayCategory}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <button
        type="button"
        className="principle-token__badge"
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        title={displayDescription || `Principle: ${principle}`}
      >
        <span className="principle-token__id">({principle})</span>
        {displayTitle !== principle && (
          <span className="principle-token__title">{displayTitle}</span>
        )}
      </button>

      {/* Tooltip on hover — INVARIANT: Always in DOM, opacity controlled by CSS */}
      <span
        className="principle-token__tooltip"
        style={{ opacity: isHovered ? 1 : 0 }}
        role="tooltip"
      >
        <span className="principle-token__tooltip-title">{displayTitle}</span>
        {displayDescription && (
          <span className="principle-token__tooltip-desc">{displayDescription}</span>
        )}
      </span>
    </span>
  );
});
