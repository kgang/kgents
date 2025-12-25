/**
 * BranchControls Component
 *
 * Fork/merge UI controls for chat sessions.
 * Provides:
 * - Fork button with name input modal
 * - Merge dropdown (Sequential/Interleave/Manual strategies)
 * - Rewind slider/buttons
 *
 * @see spec/protocols/chat-web.md §10.2
 */

import { useState, type FormEvent, type ChangeEvent } from 'react';
import type { MergeStrategy } from './useBranching';
import './BranchControls.css';

const MAX_BRANCHES = 3;

export interface BranchControlsProps {
  /** Current turn count */
  turnCount: number;
  /** Can create new fork */
  canFork: boolean;
  /** Active branch count */
  activeBranches: number;
  /** Available branches to merge from */
  mergeable: Array<{ id: string; name: string }>;
  /** Fork callback */
  onFork: (name: string) => Promise<void>;
  /** Merge callback */
  onMerge: (branchId: string, strategy: MergeStrategy) => Promise<void>;
  /** Rewind callback */
  onRewind: (turns: number) => void;
}

/**
 * Fork/merge/rewind controls for chat sessions.
 *
 * @example
 * ```tsx
 * <BranchControls
 *   turnCount={25}
 *   canFork={true}
 *   activeBranches={2}
 *   mergeable={[{ id: 'b1', name: 'explore-auth' }]}
 *   onFork={fork}
 *   onMerge={merge}
 *   onRewind={rewind}
 * />
 * ```
 */
export function BranchControls({
  turnCount,
  canFork,
  activeBranches,
  mergeable,
  onFork,
  onMerge,
  onRewind,
}: BranchControlsProps) {
  const [showForkModal, setShowForkModal] = useState(false);
  const [forkName, setForkName] = useState('');
  const [forking, setForking] = useState(false);
  const [merging, setMerging] = useState(false);
  const [rewindTurns, setRewindTurns] = useState(1);

  const handleForkClick = () => {
    if (!canFork) return;
    setShowForkModal(true);
    setForkName(''); // Clear previous name
  };

  const handleForkSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!forkName.trim()) {
      // Auto-generate name if empty
      const defaultName = `branch-${Date.now()}`;
      setForkName(defaultName);
      return;
    }

    try {
      setForking(true);
      await onFork(forkName.trim());
      setShowForkModal(false);
      setForkName('');
    } catch (err) {
      console.error('Fork failed:', err);
    } finally {
      setForking(false);
    }
  };

  const handleMerge = async (branchId: string, strategy: MergeStrategy) => {
    try {
      setMerging(true);
      await onMerge(branchId, strategy);
    } catch (err) {
      console.error('Merge failed:', err);
    } finally {
      setMerging(false);
    }
  };

  const handleRewind = () => {
    if (rewindTurns > 0 && rewindTurns <= turnCount) {
      onRewind(rewindTurns);
    }
  };

  const canRewind = turnCount > 0;

  return (
    <div className="branch-controls">
      {/* Fork Button */}
      <button
        className="branch-controls__button branch-controls__fork"
        onClick={handleForkClick}
        disabled={!canFork || forking}
        title={
          canFork
            ? 'Fork conversation at this point'
            : `Maximum ${MAX_BRANCHES} branches (${activeBranches}/${MAX_BRANCHES})`
        }
      >
        <span className="branch-controls__icon">⥮</span>
        <span className="branch-controls__label">Fork</span>
        {!canFork && (
          <span className="branch-controls__badge">
            {activeBranches}/{MAX_BRANCHES}
          </span>
        )}
      </button>

      {/* Merge Dropdown */}
      {mergeable.length > 0 && (
        <div className="branch-controls__merge">
          <select
            className="branch-controls__select"
            disabled={merging}
            onChange={(e) => {
              const [branchId, strategy] = e.target.value.split(':');
              if (branchId && strategy) {
                handleMerge(branchId, strategy as MergeStrategy);
                e.target.value = ''; // Reset
              }
            }}
            value=""
          >
            <option value="" disabled>
              Merge...
            </option>
            {mergeable.map((branch) => (
              <optgroup key={branch.id} label={branch.name}>
                <option value={`${branch.id}:sequential`}>Sequential</option>
                <option value={`${branch.id}:interleave`}>Interleave</option>
                <option value={`${branch.id}:manual`}>Manual</option>
              </optgroup>
            ))}
          </select>
        </div>
      )}

      {/* Rewind Controls */}
      {canRewind && (
        <div className="branch-controls__rewind">
          <button
            className="branch-controls__button branch-controls__rewind-btn"
            onClick={handleRewind}
            disabled={!canRewind || rewindTurns < 1}
            title={`Rewind ${rewindTurns} turn${rewindTurns === 1 ? '' : 's'}`}
          >
            <span className="branch-controls__icon">↶</span>
            <span className="branch-controls__label">Rewind</span>
          </button>
          <input
            type="range"
            className="branch-controls__slider"
            min="1"
            max={Math.max(1, turnCount)}
            value={rewindTurns}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              setRewindTurns(parseInt(e.target.value, 10))
            }
            disabled={!canRewind}
            title={`Rewind ${rewindTurns} turn${rewindTurns === 1 ? '' : 's'}`}
          />
          <span className="branch-controls__rewind-count">{rewindTurns}</span>
        </div>
      )}

      {/* Fork Modal */}
      {showForkModal && (
        <ForkModal
          value={forkName}
          onChange={setForkName}
          onSubmit={handleForkSubmit}
          onCancel={() => setShowForkModal(false)}
          loading={forking}
        />
      )}
    </div>
  );
}

/**
 * Fork name input modal.
 */
function ForkModal({
  value,
  onChange,
  onSubmit,
  onCancel,
  loading,
}: {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (e: FormEvent) => void;
  onCancel: () => void;
  loading: boolean;
}) {
  return (
    <div className="branch-modal__overlay" onClick={onCancel}>
      <div className="branch-modal" onClick={(e) => e.stopPropagation()}>
        <div className="branch-modal__header">
          <h3 className="branch-modal__title">Fork Conversation</h3>
          <button className="branch-modal__close" onClick={onCancel} aria-label="Close">
            ✕
          </button>
        </div>

        <form onSubmit={onSubmit}>
          <div className="branch-modal__body">
            <label className="branch-modal__label" htmlFor="fork-name">
              Branch Name
            </label>
            <input
              id="fork-name"
              type="text"
              className="branch-modal__input"
              value={value}
              onChange={(e) => onChange(e.target.value)}
              placeholder="explore-alternative"
              autoFocus
              disabled={loading}
            />
            <p className="branch-modal__hint">
              Describe what you'll explore in this branch (or leave blank for auto-generated name)
            </p>
          </div>

          <div className="branch-modal__footer">
            <button
              type="button"
              className="branch-modal__button branch-modal__button--secondary"
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="branch-modal__button branch-modal__button--primary"
              disabled={loading}
            >
              {loading ? 'Forking...' : 'Fork'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default BranchControls;
