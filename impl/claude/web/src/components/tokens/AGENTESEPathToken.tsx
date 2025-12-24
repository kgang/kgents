/**
 * AGENTESEPathToken — Clickable AGENTESE path with living glow.
 *
 * Renders paths like `self.brain` or `world.house.manifest` as interactive links.
 * Ghost state for non-existent paths.
 * Breathing animation on hover.
 *
 * "The noun is a lie. There is only the rate of change."
 */

import { memo, useCallback } from 'react';

import './tokens.css';

interface AGENTESEPathTokenProps {
  path: string;
  exists?: boolean;
  onClick?: (path: string) => void;
  className?: string;
}

export const AGENTESEPathToken = memo(function AGENTESEPathToken({
  path,
  exists = true,
  onClick,
  className,
}: AGENTESEPathTokenProps) {
  const handleClick = useCallback(() => {
    onClick?.(path);
  }, [path, onClick]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onClick?.(path);
      }
    },
    [path, onClick]
  );

  return (
    <button
      type="button"
      className={`agentese-path-token ${exists ? '' : 'agentese-path-token--ghost'} ${className ?? ''}`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      title={exists ? `Navigate to ${path}` : `${path} (not found)`}
      data-path={path}
      data-exists={exists}
    >
      <code className="agentese-path-token__code">{path}</code>
    </button>
  );
});
