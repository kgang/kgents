/**
 * UnifiedKBlockEditor — K-Block editing for all content types
 *
 * "The K-Block is not where you edit a document.
 *  It's where you edit a possible world."
 *
 * This component provides a unified editing experience for:
 * 1. File-based K-Blocks (prose, graph, etc.)
 * 2. Zero Seed epistemic graph nodes
 * 3. Dialogue K-Blocks
 *
 * Philosophy:
 *   Same isolation semantics (PRISTINE/DIRTY/STALE) across all types.
 *   Same save/discard controls.
 *   Same proof and derivation tracking.
 */

import React from 'react';
import type { KBlockState } from '../../hypergraph/useKBlock';
import type { ToulminProof } from '../../api/zeroSeed';
import './UnifiedKBlockEditor.css';

// =============================================================================
// Types
// =============================================================================

export interface UnifiedKBlockEditorProps {
  /** K-Block state from useKBlock hook */
  state: KBlockState;

  /** Content change handler */
  onContentChange: (content: string) => void;

  /** Save handler */
  onSave: (reasoning?: string) => Promise<void>;

  /** Discard handler */
  onDiscard: () => Promise<void>;

  /** Proof update handler (Zero Seed only) */
  onProofUpdate?: (proof: ToulminProof) => Promise<void>;

  /** Derivation navigation handlers (Zero Seed only) */
  onNavigateToParent?: (index: number) => void;
  onNavigateToChild?: (index: number) => void;

  /** Whether the editor is read-only */
  readOnly?: boolean;

  /** Optional CSS class name */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

export const UnifiedKBlockEditor: React.FC<UnifiedKBlockEditorProps> = ({
  state,
  onContentChange,
  onSave,
  onDiscard,
  onProofUpdate: _onProofUpdate, // Reserved for future proof editing UI
  onNavigateToParent,
  onNavigateToChild,
  readOnly = false,
  className = '',
}) => {
  const [reasoning, setReasoning] = React.useState('');
  const [showProofPanel, setShowProofPanel] = React.useState(false);

  const isZeroSeed = state.zeroSeedLayer !== undefined;
  const isFile = state.path !== null;
  const isDialogue = state.sessionId !== undefined;

  const handleSave = async () => {
    await onSave(reasoning);
    setReasoning('');
  };

  return (
    <div className={`unified-kblock-editor ${className}`}>
      {/* Header with metadata */}
      <div className="kblock-header">
        <div className="kblock-metadata">
          {/* Type indicator */}
          {isZeroSeed && (
            <span className="kblock-type zero-seed">
              L{state.zeroSeedLayer} {state.zeroSeedKind}
            </span>
          )}
          {isFile && !isZeroSeed && (
            <span className="kblock-type file">File</span>
          )}
          {isDialogue && (
            <span className="kblock-type dialogue">Dialogue</span>
          )}

          {/* Isolation state indicator */}
          <span className={`isolation-indicator ${state.isolation.toLowerCase()}`}>
            {state.isolation}
          </span>

          {/* Confidence (Zero Seed only) */}
          {isZeroSeed && (
            <span className="confidence-badge">
              {Math.round(state.confidence * 100)}% confidence
            </span>
          )}

          {/* Proof indicator */}
          {state.hasProof && (
            <button
              className="proof-indicator"
              onClick={() => setShowProofPanel(!showProofPanel)}
              title="View proof"
            >
              ▤ Proof attached
            </button>
          )}
        </div>

        {/* Derivation chain (Zero Seed only) */}
        {isZeroSeed && state.parentBlocks.length > 0 && (
          <div className="derivation-chain">
            <span className="chain-label">Derives from:</span>
            {state.parentBlocks.map((parentId, index) => (
              <button
                key={parentId}
                className="derivation-link"
                onClick={() => onNavigateToParent?.(index)}
                title={`Navigate to parent: ${parentId}`}
              >
                {parentId.substring(0, 8)}...
              </button>
            ))}
          </div>
        )}

        {/* Child nodes (Zero Seed only) */}
        {isZeroSeed && state.childBlocks.length > 0 && (
          <div className="derivation-chain">
            <span className="chain-label">Children:</span>
            {state.childBlocks.map((childId, index) => (
              <button
                key={childId}
                className="derivation-link"
                onClick={() => onNavigateToChild?.(index)}
                title={`Navigate to child: ${childId}`}
              >
                {childId.substring(0, 8)}...
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Proof panel (if visible and Zero Seed) */}
      {showProofPanel && state.hasProof && state.toulminProof && (
        <div className="proof-panel">
          <h3>Toulmin Proof</h3>
          <div className="proof-grid">
            <div className="proof-item">
              <label>Claim</label>
              <div>{state.toulminProof.claim}</div>
            </div>
            <div className="proof-item">
              <label>Data</label>
              <div>{state.toulminProof.data}</div>
            </div>
            <div className="proof-item">
              <label>Warrant</label>
              <div>{state.toulminProof.warrant}</div>
            </div>
            {state.toulminProof.backing && (
              <div className="proof-item">
                <label>Backing</label>
                <div>{state.toulminProof.backing}</div>
              </div>
            )}
            {state.toulminProof.qualifier && (
              <div className="proof-item">
                <label>Qualifier</label>
                <div>{state.toulminProof.qualifier}</div>
              </div>
            )}
            {state.toulminProof.rebuttals.length > 0 && (
              <div className="proof-item">
                <label>Rebuttals</label>
                <ul>
                  {state.toulminProof.rebuttals.map((rebuttal, index) => (
                    <li key={index}>{rebuttal}</li>
                  ))}
                </ul>
              </div>
            )}
            <div className="proof-item">
              <label>Evidence Tier</label>
              <div className={`tier-badge ${state.toulminProof.tier}`}>
                {state.toulminProof.tier}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main content editor */}
      <div className="kblock-content">
        <textarea
          className="content-editor"
          value={state.content}
          onChange={(e) => onContentChange(e.target.value)}
          readOnly={readOnly || state.isReadOnly}
          placeholder="Enter content..."
        />
      </div>

      {/* Footer with controls */}
      <div className="kblock-footer">
        {/* Reasoning input (only shown when dirty) */}
        {state.isDirty && (
          <input
            type="text"
            className="reasoning-input"
            value={reasoning}
            onChange={(e) => setReasoning(e.target.value)}
            placeholder="Why this change? (witness message)"
          />
        )}

        {/* Action buttons */}
        <div className="kblock-actions">
          {state.isDirty && (
            <>
              <button className="btn-save" onClick={handleSave}>
                Save {isDialogue ? '(Crystallize)' : ''}
              </button>
              <button className="btn-discard" onClick={onDiscard}>
                Discard
              </button>
            </>
          )}

          {!state.isDirty && state.isolation === 'PRISTINE' && (
            <span className="status-message">No changes</span>
          )}

          {state.isolation === 'STALE' && (
            <span className="status-message warning">
              Content changed on disk - consider refreshing
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default UnifiedKBlockEditor;
