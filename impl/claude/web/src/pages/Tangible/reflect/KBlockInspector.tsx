/**
 * KBlockInspector - Floating K-Block inspector panel
 *
 * Features:
 * - Appears on hover over any K-Block element
 * - Shows: K-Block ID, layer, derivation chain, witnesses
 * - Quick actions: navigate to, edit, view history
 * - Positioned relative to cursor
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 */

import { memo, useEffect, useRef } from 'react';
import {
  Layers,
  GitBranch,
  ExternalLink,
  History,
  Edit3,
  X,
  Bookmark,
  ArrowUp,
  ArrowDown,
} from 'lucide-react';
import type { KBlockInfo, WitnessInfo } from './types';
import { LAYER_COLORS, LAYER_NAMES } from './types';

// =============================================================================
// Types
// =============================================================================

export interface KBlockInspectorProps {
  kblock: KBlockInfo | null;
  position: { x: number; y: number };
  onClose: () => void;
  onNavigate: (kblockId: string) => void;
  onEdit?: (kblockId: string) => void;
  onViewHistory?: (kblockId: string) => void;
}

// =============================================================================
// Subcomponents
// =============================================================================

interface WitnessListProps {
  witnesses: WitnessInfo[];
  maxShow?: number;
}

const WitnessList = memo(function WitnessList({ witnesses, maxShow = 3 }: WitnessListProps) {
  const displayWitnesses = witnesses.slice(0, maxShow);
  const remaining = witnesses.length - maxShow;

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="kblock-inspector__witnesses">
      {displayWitnesses.map((witness) => (
        <div key={witness.markId} className="kblock-inspector__witness">
          <Bookmark size={10} className="kblock-inspector__witness-icon" />
          <span className="kblock-inspector__witness-action">{witness.action}</span>
          <span className="kblock-inspector__witness-meta">
            {witness.author} - {formatDate(witness.timestamp)}
          </span>
        </div>
      ))}
      {remaining > 0 && (
        <div className="kblock-inspector__witness-more">+{remaining} more witnesses</div>
      )}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const KBlockInspector = memo(function KBlockInspector({
  kblock,
  position,
  onClose,
  onNavigate,
  onEdit,
  onViewHistory,
}: KBlockInspectorProps) {
  const panelRef = useRef<HTMLDivElement>(null);

  // Close on escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    // Delay to avoid immediate close
    const timer = setTimeout(() => {
      window.addEventListener('click', handleClickOutside);
    }, 100);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('click', handleClickOutside);
    };
  }, [onClose]);

  // Adjust position to stay in viewport
  const adjustedPosition = {
    x: Math.min(position.x, window.innerWidth - 320),
    y: Math.min(position.y, window.innerHeight - 400),
  };

  if (!kblock) return null;

  return (
    <div
      ref={panelRef}
      className="kblock-inspector"
      style={
        {
          '--x': `${adjustedPosition.x}px`,
          '--y': `${adjustedPosition.y}px`,
        } as React.CSSProperties
      }
    >
      {/* Header */}
      <div className="kblock-inspector__header">
        <div
          className="kblock-inspector__layer-badge"
          style={{ color: LAYER_COLORS[kblock.layer] }}
        >
          <Layers size={12} />
          <span>L{kblock.layer}</span>
          <span className="kblock-inspector__layer-name">{LAYER_NAMES[kblock.layer]}</span>
        </div>
        <button className="kblock-inspector__close" onClick={onClose} aria-label="Close">
          <X size={14} />
        </button>
      </div>

      {/* Title */}
      <div className="kblock-inspector__title">{kblock.title}</div>

      {/* Path */}
      <div className="kblock-inspector__path">{kblock.path}</div>

      {/* Stats */}
      <div className="kblock-inspector__stats">
        {kblock.galoisLoss !== undefined && (
          <div className="kblock-inspector__stat">
            <span className="kblock-inspector__stat-label">Galois Loss</span>
            <span
              className="kblock-inspector__stat-value"
              data-severity={
                kblock.galoisLoss > 0.2 ? 'high' : kblock.galoisLoss > 0.1 ? 'medium' : 'low'
              }
            >
              {(kblock.galoisLoss * 100).toFixed(1)}%
            </span>
          </div>
        )}
        {kblock.witnesses && (
          <div className="kblock-inspector__stat">
            <span className="kblock-inspector__stat-label">Witnesses</span>
            <span className="kblock-inspector__stat-value">{kblock.witnesses.length}</span>
          </div>
        )}
      </div>

      {/* Derivation links */}
      <div className="kblock-inspector__derivation">
        {kblock.derivedFrom && kblock.derivedFrom.length > 0 && (
          <div className="kblock-inspector__derivation-section">
            <span className="kblock-inspector__derivation-label">
              <ArrowUp size={10} />
              Derives From
            </span>
            <div className="kblock-inspector__derivation-links">
              {kblock.derivedFrom.map((id) => (
                <button
                  key={id}
                  className="kblock-inspector__derivation-link"
                  onClick={() => onNavigate(id)}
                >
                  {id}
                </button>
              ))}
            </div>
          </div>
        )}

        {kblock.groundedBy && kblock.groundedBy.length > 0 && (
          <div className="kblock-inspector__derivation-section">
            <span className="kblock-inspector__derivation-label">
              <ArrowDown size={10} />
              Grounded By
            </span>
            <div className="kblock-inspector__derivation-links">
              {kblock.groundedBy.map((id) => (
                <button
                  key={id}
                  className="kblock-inspector__derivation-link"
                  onClick={() => onNavigate(id)}
                >
                  {id}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Witnesses */}
      {kblock.witnesses && kblock.witnesses.length > 0 && (
        <div className="kblock-inspector__section">
          <span className="kblock-inspector__section-label">Recent Witnesses</span>
          <WitnessList witnesses={kblock.witnesses} />
        </div>
      )}

      {/* Actions */}
      <div className="kblock-inspector__actions">
        <button
          className="kblock-inspector__action"
          onClick={() => onNavigate(kblock.id)}
          title="Navigate to K-Block"
        >
          <ExternalLink size={12} />
          <span>Navigate</span>
        </button>
        {onEdit && (
          <button
            className="kblock-inspector__action"
            onClick={() => onEdit(kblock.id)}
            title="Edit K-Block"
          >
            <Edit3 size={12} />
            <span>Edit</span>
          </button>
        )}
        {onViewHistory && (
          <button
            className="kblock-inspector__action"
            onClick={() => onViewHistory(kblock.id)}
            title="View history"
          >
            <History size={12} />
            <span>History</span>
          </button>
        )}
      </div>
    </div>
  );
});

export default KBlockInspector;
