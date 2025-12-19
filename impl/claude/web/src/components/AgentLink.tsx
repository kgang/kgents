/**
 * AgentLink - AGENTESE-aware navigation component
 *
 * Replaces react-router Link for AGENTESE paths.
 * Provides automatic URL formatting and prefetching.
 *
 * @see spec/protocols/agentese-as-route.md
 */

import { forwardRef, type ReactNode, type MouseEvent } from 'react';
import { Link, type LinkProps } from 'react-router-dom';
import { formatAgentesePath } from '@/utils/parseAgentesePath';

/**
 * Props for AgentLink component
 */
export interface AgentLinkProps extends Omit<LinkProps, 'to'> {
  /** AGENTESE path (e.g., "world.town.citizen.kent_001") */
  path: string;
  /** Aspect to invoke (default: "manifest", omitted from URL) */
  aspect?: string;
  /** Query parameters */
  params?: Record<string, string>;
  /** Children to render */
  children: ReactNode;
  /** Prefetch on hover (default: true) */
  prefetch?: boolean;
  /** Custom onClick handler (runs before navigation) */
  onClick?: (e: MouseEvent<HTMLAnchorElement>) => void;
}

/**
 * AgentLink component
 *
 * A drop-in replacement for react-router Link that understands AGENTESE paths.
 *
 * @example
 * // Basic usage
 * <AgentLink path="world.town.citizen.kent_001">
 *   View Kent
 * </AgentLink>
 *
 * // With aspect
 * <AgentLink path="world.town.citizen.kent_001" aspect="polynomial">
 *   View Polynomial
 * </AgentLink>
 *
 * // With params
 * <AgentLink path="time.differance.recent" params={{ limit: '20' }}>
 *   Recent Traces
 * </AgentLink>
 *
 * // With styling
 * <AgentLink path="self.memory" className="text-accent-sage hover:underline">
 *   Brain
 * </AgentLink>
 */
export const AgentLink = forwardRef<HTMLAnchorElement, AgentLinkProps>(function AgentLink(
  { path, aspect, params, children, prefetch = true, onClick, ...linkProps },
  ref
) {
  // Format the URL from AGENTESE components
  const url = formatAgentesePath(path, aspect, params);

  // Handle prefetch on hover
  const handleMouseEnter = () => {
    if (prefetch) {
      // TODO: Implement actual prefetching via useAgentese
      // For now, we can trigger a low-priority fetch
    }
  };

  const handleClick = (e: MouseEvent<HTMLAnchorElement>) => {
    onClick?.(e);
  };

  return (
    <Link
      ref={ref}
      to={url}
      onMouseEnter={handleMouseEnter}
      onClick={handleClick}
      data-agentese-path={path}
      data-agentese-aspect={aspect}
      {...linkProps}
    >
      {children}
    </Link>
  );
});

/**
 * Format path for display as breadcrumb
 *
 * @example
 * formatBreadcrumb("world.town.citizen.kent_001")
 * // ["world", "town", "citizen", "kent_001"]
 */
export function formatBreadcrumb(path: string): string[] {
  return path.split('.');
}

/**
 * Generate breadcrumb links for a path
 *
 * @example
 * getBreadcrumbLinks("world.town.citizen.kent_001")
 * // [
 * //   { label: "world", path: "world" },
 * //   { label: "town", path: "world.town" },
 * //   { label: "citizen", path: "world.town.citizen" },
 * //   { label: "kent_001", path: "world.town.citizen.kent_001" }
 * // ]
 */
export function getBreadcrumbLinks(path: string): Array<{ label: string; path: string }> {
  const segments = path.split('.');
  return segments.map((segment, index) => ({
    label: segment,
    path: segments.slice(0, index + 1).join('.'),
  }));
}

export default AgentLink;
