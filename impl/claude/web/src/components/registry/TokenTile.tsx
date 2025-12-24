/**
 * TokenTile - Minimal token representation
 *
 * Shows: tier icon + name
 * Hover: tooltip with path + stats
 * Click: opens detail panel
 *
 * "The frame is humble. The content glows."
 */

import { memo } from 'react';
import * as Tooltip from '@radix-ui/react-tooltip';

import { type TokenItem, STATUS_INDICATORS, TIER_LABELS, getTierColor } from './types';

import './TokenTile.css';

// =============================================================================
// Types
// =============================================================================

interface TokenTileProps {
  token: TokenItem;
  selected?: boolean;
  onClick?: () => void;
  onDoubleClick?: () => void;
}

// =============================================================================
// Component
// =============================================================================

export const TokenTile = memo(function TokenTile({
  token,
  selected = false,
  onClick,
  onDoubleClick,
}: TokenTileProps) {
  const statusIndicator = STATUS_INDICATORS[token.status];
  const tierColor = getTierColor(token.tier);

  // Build tooltip content
  const tooltipContent = (
    <div className="token-tile-tooltip">
      <div className="token-tile-tooltip__path">{token.id}</div>
      <div className="token-tile-tooltip__stats">
        {token.claimCount} claims
        {token.implCount > 0 && <> &middot; {token.implCount} impl</>}
        {token.testCount > 0 && <> &middot; {token.testCount} test</>}
      </div>
      <div className="token-tile-tooltip__tier">Tier: {TIER_LABELS[token.tier]}</div>
    </div>
  );

  return (
    <Tooltip.Provider delayDuration={300}>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>
          <button
            className="token-tile"
            data-tier={token.tier}
            data-status={token.status.toLowerCase()}
            data-selected={selected}
            data-has-evidence={token.hasEvidence}
            style={{ '--tile-color': tierColor } as React.CSSProperties}
            onClick={onClick}
            onDoubleClick={onDoubleClick}
            aria-label={`${token.name} - ${TIER_LABELS[token.tier]}`}
          >
            <span className="token-tile__icon">{token.icon}</span>
            <span className="token-tile__name">
              {token.name}
              {statusIndicator && (
                <span className="token-tile__status-indicator">{statusIndicator}</span>
              )}
            </span>
          </button>
        </Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content className="token-tile-tooltip__container" sideOffset={5}>
            {tooltipContent}
            <Tooltip.Arrow className="token-tile-tooltip__arrow" />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
});

// =============================================================================
// Placeholder Tile (for loading states)
// =============================================================================

export function TokenTilePlaceholder() {
  return (
    <div className="token-tile token-tile--placeholder">
      <span className="token-tile__icon">○</span>
      <span className="token-tile__name">Loading...</span>
    </div>
  );
}
