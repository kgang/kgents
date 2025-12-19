/**
 * SoulPresence - K-gent presence indicator for the Forge.
 *
 * Shows K-gent's current state with breathing animation when active.
 * Displays eigenvector mini-radar on hover.
 *
 * "The Forge is where Kent builds with Kent."
 *
 * @see services/forge/soul_node.py
 * @see agents/k/eigenvectors.py
 * @see docs/skills/crown-jewel-patterns.md (HealthBadge breathing pattern)
 */

import { useState, useCallback } from 'react';
import { useSoulManifest, isSoulActive, getSoulModeIcon, getSoulModeLabel } from '@/hooks';
import { KentEigenvectorRadar, KENT_EIGENVECTORS } from '@/components/eigenvector';
import { cn } from '@/lib/utils';

interface SoulPresenceProps {
  /** Compact mode - icon only */
  compact?: boolean;
  /** Show eigenvector radar on hover */
  showEigenvectors?: boolean;
  /** Additional class names */
  className?: string;
}

/**
 * K-gent soul presence indicator.
 *
 * Displays:
 * - Mode icon (🪞 reflect, 💡 advise, ⚔️ challenge, 🧭 explore, 💤 dormant)
 * - Mode label (optional, in non-compact mode)
 * - Breathing animation when active
 * - Eigenvector radar popup on hover
 */
export function SoulPresence({
  compact = false,
  showEigenvectors = true,
  className = '',
}: SoulPresenceProps) {
  const [isHovered, setIsHovered] = useState(false);
  const { data: manifest, isLoading, error } = useSoulManifest({ refreshInterval: 10000 });

  const isActive = isSoulActive(manifest);
  const mode = manifest?.mode || 'dormant';
  const icon = getSoulModeIcon(mode);
  const label = getSoulModeLabel(mode);
  const eigenvectors = manifest?.eigenvectors || KENT_EIGENVECTORS;

  const handleMouseEnter = useCallback(() => setIsHovered(true), []);
  const handleMouseLeave = useCallback(() => setIsHovered(false), []);

  // Base indicator styles
  const indicatorClasses = cn(
    'relative flex items-center gap-2 px-3 py-1.5 rounded-full',
    'border transition-all duration-300',
    isActive
      ? 'bg-amber-50 border-amber-200 text-amber-700'
      : 'bg-stone-100 border-stone-200 text-stone-500',
    isActive && 'animate-pulse-subtle',
    className
  );

  return (
    <div
      className={indicatorClasses}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      title={error ? `Soul error: ${error}` : `K-gent: ${label}`}
    >
      {/* Mode icon */}
      <span className="text-sm" role="img" aria-label={mode}>
        {icon}
      </span>

      {/* Mode label (non-compact) */}
      {!compact && (
        <span className="text-xs font-medium">{isLoading ? 'Connecting...' : label}</span>
      )}

      {/* Active indicator dot */}
      {isActive && (
        <span className="absolute top-0 right-0 w-2 h-2 -mt-0.5 -mr-0.5">
          <span className="absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75 animate-ping" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500" />
        </span>
      )}

      {/* Eigenvector popup on hover */}
      {showEigenvectors && isHovered && !isLoading && (
        <div
          className={cn(
            'absolute top-full left-1/2 -translate-x-1/2 mt-2 z-50',
            'bg-white rounded-lg shadow-lg border border-stone-200 p-3',
            'animate-in fade-in-0 zoom-in-95 duration-200'
          )}
        >
          <div className="text-xs text-stone-500 mb-2 text-center font-medium">
            Kent's Soul Coordinates
          </div>
          <KentEigenvectorRadar dimensions={eigenvectors} size={140} showLabels />
          {manifest?.session_interactions !== undefined && (
            <div className="mt-2 text-[10px] text-stone-400 text-center">
              {manifest.session_interactions} interactions this session
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Compact soul indicator for tight spaces (e.g., CrownContext).
 */
export function SoulIndicator({ className = '' }: { className?: string }) {
  const { data: manifest, isLoading } = useSoulManifest({ refreshInterval: 30000 });

  const isActive = isSoulActive(manifest);
  const mode = manifest?.mode || 'dormant';
  const icon = getSoulModeIcon(mode);

  if (isLoading) {
    return (
      <span className={cn('text-stone-300', className)} title="Connecting to K-gent...">
        ⋯
      </span>
    );
  }

  return (
    <span
      className={cn(isActive ? 'text-amber-500' : 'text-stone-400', className)}
      title={`K-gent: ${mode}`}
    >
      {icon}
    </span>
  );
}

export default SoulPresence;
