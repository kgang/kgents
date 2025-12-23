/**
 * LinkToken — Clickable hyperlink with preview.
 *
 * Renders markdown links [text](url) as interactive elements.
 * Shows URL preview on hover.
 *
 * "Hyperlink to external or internal resource."
 */

import { memo, useCallback } from 'react';

import './tokens.css';

interface LinkTokenProps {
  text: string;
  url: string;
  onClick?: (url: string) => void;
  className?: string;
}

export const LinkToken = memo(function LinkToken({
  text,
  url,
  onClick,
  className,
}: LinkTokenProps) {
  const handleClick = useCallback(
    (e: React.MouseEvent) => {
      if (onClick) {
        e.preventDefault();
        onClick(url);
      }
      // Otherwise, let the default anchor behavior work
    },
    [url, onClick]
  );

  const isExternal = url.startsWith('http://') || url.startsWith('https://');

  return (
    <span className={`link-token ${className ?? ''}`}>
      <a
        href={url}
        onClick={handleClick}
        className="link-token__anchor"
        target={isExternal ? '_blank' : undefined}
        rel={isExternal ? 'noopener noreferrer' : undefined}
        title={url}
      >
        {text}
        {isExternal && <span className="link-token__external-icon"> ↗</span>}
      </a>
      {/* INVARIANT: Preview always in DOM, CSS controls visibility (no layout shift) */}
      <span className="link-token__preview">{url}</span>
    </span>
  );
});
