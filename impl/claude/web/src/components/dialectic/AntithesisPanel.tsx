/**
 * AntithesisPanel - Claude's Position Input
 *
 * The right panel of the FusionCeremony where Claude's counter-position is entered.
 * "Adversarial cooperation" - challenge is structural, not hostile.
 *
 * Design: STARK BIOME aesthetic with cool accent for Claude's voice.
 */

import { memo } from 'react';
import type { AntithesisPanelProps } from './types';

/**
 * AntithesisPanel Component
 *
 * @example
 * <AntithesisPanel
 *   content={claudeView}
 *   onContentChange={setClaudeView}
 *   reasoning={claudeReasoning}
 *   onReasoningChange={setClaudeReasoning}
 *   thesisContent={kentView}
 * />
 */
export const AntithesisPanel = memo(function AntithesisPanel({
  content,
  onContentChange,
  reasoning,
  onReasoningChange,
  thesisContent,
  disabled = false,
  className = '',
}: AntithesisPanelProps) {
  // Show a prompt if thesis exists but antithesis doesn't
  const showPrompt = thesisContent && !content;

  return (
    <div className={`fusion-panel fusion-panel--antithesis ${className}`}>
      {/* Panel Header */}
      <div className="fusion-panel__header">
        <span className="fusion-panel__badge fusion-panel__badge--claude">C</span>
        <h3 className="fusion-panel__title">Claude's Position</h3>
        <span className="fusion-panel__subtitle">Antithesis</span>
      </div>

      {/* Panel Content */}
      <div className="fusion-panel__content">
        {/* Position Field */}
        <div className="fusion-field">
          <label className="fusion-field__label" htmlFor="fusion-antithesis-content">
            Counter-Position
          </label>
          <textarea
            id="fusion-antithesis-content"
            className="fusion-field__textarea"
            placeholder={
              showPrompt
                ? "Challenge Kent's position constructively..."
                : 'State the counter-position...'
            }
            value={content}
            onChange={(e) => onContentChange(e.target.value)}
            disabled={disabled}
            rows={4}
          />
          {showPrompt && (
            <div className="fusion-field__prompt">
              <span className="fusion-field__prompt-icon">?</span>
              <span className="fusion-field__prompt-text">
                What would challenge this view? Where might it break down?
              </span>
            </div>
          )}
        </div>

        {/* Reasoning Field */}
        <div className="fusion-field">
          <label className="fusion-field__label" htmlFor="fusion-antithesis-reasoning">
            Reasoning
          </label>
          <textarea
            id="fusion-antithesis-reasoning"
            className="fusion-field__textarea fusion-field__textarea--small"
            placeholder="What supports this counter-position?"
            value={reasoning}
            onChange={(e) => onReasoningChange(e.target.value)}
            disabled={disabled}
            rows={3}
          />
        </div>

        {/* Optional: Auto-generate button (future feature) */}
        {/*
        <button
          className="fusion-button fusion-button--secondary"
          onClick={onAutoGenerate}
          disabled={!thesisContent || disabled}
        >
          Auto-generate counter-position
        </button>
        */}
      </div>

      {/* Panel Footer (hint) */}
      <div className="fusion-panel__footer">
        <span className="fusion-panel__hint">Challenge is cooperation. The goal is synthesis.</span>
      </div>
    </div>
  );
});

export default AntithesisPanel;
