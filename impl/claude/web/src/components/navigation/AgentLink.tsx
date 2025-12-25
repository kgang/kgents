/**
 * AgentLink: AGENTESE-aware navigation component
 *
 * Replaces traditional <Link> with AGENTESE path awareness.
 * Handles prefetching, aspect invocation, and parameter passing.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { toUrl } from '../../router';

interface AgentLinkProps {
  /** AGENTESE path (e.g., 'world.town.citizen.kent_001') */
  path: string;

  /** Optional aspect to invoke */
  aspect?: string;

  /** Optional query parameters */
  params?: Record<string, string>;

  /** Link content */
  children: React.ReactNode;

  /** Additional CSS classes */
  className?: string;

  /** Replace current history entry instead of pushing */
  replace?: boolean;

  /** onClick handler */
  onClick?: (e: React.MouseEvent) => void;
}

/**
 * AGENTESE navigation link.
 *
 * Example:
 *   <AgentLink path="world.town.citizen.kent_001">
 *     Kent's Profile
 *   </AgentLink>
 *
 *   <AgentLink path="self.chat" aspect="stream" params={{ limit: '20' }}>
 *     Chat Stream
 *   </AgentLink>
 */
export function AgentLink({
  path,
  aspect,
  params,
  children,
  className,
  replace,
  onClick,
}: AgentLinkProps) {
  const url = toUrl(path, { aspect, params });

  // TODO: Add prefetching with useAgentesePrefetch hook when implemented

  return (
    <Link to={url} replace={replace} className={className} onClick={onClick}>
      {children}
    </Link>
  );
}

/**
 * Props for AgentNavLink (active state support).
 */
interface AgentNavLinkProps extends AgentLinkProps {
  /** Class to apply when link is active */
  activeClassName?: string;

  /** Custom active check function */
  isActive?: (currentPath: string) => boolean;
}

/**
 * AGENTESE navigation link with active state.
 *
 * Highlights when current path matches.
 *
 * Example:
 *   <AgentNavLink
 *     path="self.chat"
 *     activeClassName="border-l-2 border-accent-primary"
 *   >
 *     Chat
 *   </AgentNavLink>
 */
export function AgentNavLink({
  path,
  aspect,
  params,
  children,
  className = '',
  activeClassName = '',
  replace,
  onClick,
  isActive: customIsActive,
}: AgentNavLinkProps) {
  const url = toUrl(path, { aspect, params });

  // Check if current URL matches this link
  const isActive = customIsActive
    ? customIsActive(window.location.pathname)
    : window.location.pathname.startsWith(`/${path}`);

  const finalClassName = isActive
    ? `${className} ${activeClassName}`.trim()
    : className;

  return (
    <Link to={url} replace={replace} className={finalClassName} onClick={onClick}>
      {children}
    </Link>
  );
}
