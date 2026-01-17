/**
 * ThesisPanel - Kent's Position Input
 *
 * The left panel of the FusionCeremony where Kent enters their position.
 * "Daring, bold, creative, opinionated" - this is where Kent stakes their claim.
 *
 * Design: STARK BIOME aesthetic with warm accent for Kent's voice.
 */

import { memo } from 'react';
import type { ThesisPanelProps } from './types';

/**
 * ThesisPanel Component
 *
 * @example
 * <ThesisPanel
 *   topic={topic}
 *   onTopicChange={setTopic}
 *   content={kentView}
 *   onContentChange={setKentView}
 *   reasoning={kentReasoning}
 *   onReasoningChange={setKentReasoning}
 * />
 */
export const ThesisPanel = memo(function ThesisPanel({
  topic,
  onTopicChange,
  content,
  onContentChange,
  reasoning,
  onReasoningChange,
  disabled = false,
  className = '',
}: ThesisPanelProps) {
  return (
    <div className={`fusion-panel fusion-panel--thesis ${className}`}>
      {/* Panel Header */}
      <div className="fusion-panel__header">
        <span className="fusion-panel__badge fusion-panel__badge--kent">K</span>
        <h3 className="fusion-panel__title">Kent's Position</h3>
        <span className="fusion-panel__subtitle">Thesis</span>
      </div>

      {/* Panel Content */}
      <div className="fusion-panel__content">
        {/* Topic Field (only in thesis panel) */}
        <div className="fusion-field">
          <label className="fusion-field__label" htmlFor="fusion-topic">
            Topic
          </label>
          <input
            id="fusion-topic"
            type="text"
            className="fusion-field__input"
            placeholder="What decision needs to be made?"
            value={topic}
            onChange={(e) => onTopicChange(e.target.value)}
            disabled={disabled}
            autoFocus
          />
        </div>

        {/* Position Field */}
        <div className="fusion-field">
          <label className="fusion-field__label" htmlFor="fusion-thesis-content">
            Position
          </label>
          <textarea
            id="fusion-thesis-content"
            className="fusion-field__textarea"
            placeholder="State your position..."
            value={content}
            onChange={(e) => onContentChange(e.target.value)}
            disabled={disabled}
            rows={4}
          />
        </div>

        {/* Reasoning Field */}
        <div className="fusion-field">
          <label className="fusion-field__label" htmlFor="fusion-thesis-reasoning">
            Reasoning
          </label>
          <textarea
            id="fusion-thesis-reasoning"
            className="fusion-field__textarea fusion-field__textarea--small"
            placeholder="Why do you hold this position?"
            value={reasoning}
            onChange={(e) => onReasoningChange(e.target.value)}
            disabled={disabled}
            rows={3}
          />
        </div>
      </div>

      {/* Panel Footer (hint) */}
      <div className="fusion-panel__footer">
        <span className="fusion-panel__hint">
          Be opinionated. Stakes make synthesis meaningful.
        </span>
      </div>
    </div>
  );
});

export default ThesisPanel;
