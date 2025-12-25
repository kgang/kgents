/**
 * AssistantMessage — Assistant response with evidence and tool transparency
 *
 * Displays:
 * - Response content (with streaming support)
 * - Confidence indicator (Bayesian evidence)
 * - Collapsible action panel (tools used)
 *
 * Follows spec Part VII (Tool Transparency) and Part IX (Evidence).
 */

import { memo, useState } from 'react';
import type { Message, ToolUse, EvidenceDelta } from './store';
import { ConfidenceIndicator } from './ConfidenceIndicator';
import { ActionPanel } from './ActionPanel';
import { ASHCEvidence, type ASHCEvidenceData } from './ASHCEvidence';
import './AssistantMessage.css';

// =============================================================================
// Types
// =============================================================================

export interface AssistantMessageProps {
  message: Message;
  tools: ToolUse[];
  confidence: number;
  evidenceDelta: EvidenceDelta;
  isStreaming?: boolean;
  ashcEvidence?: ASHCEvidenceData | null;
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * AssistantMessage — Response bubble with confidence and transparency
 */
export const AssistantMessage = memo(function AssistantMessage({
  message,
  tools,
  confidence,
  evidenceDelta,
  isStreaming = false,
  ashcEvidence = null,
}: AssistantMessageProps) {
  const [actionPanelExpanded, setActionPanelExpanded] = useState(false);

  const hasTools = tools.length > 0;
  const hasASHCEvidence = ashcEvidence !== null && ashcEvidence !== undefined;

  return (
    <div className="assistant-message">
      {/* Confidence indicator */}
      <ConfidenceIndicator
        confidence={confidence}
        evidenceDelta={evidenceDelta}
        isStreaming={isStreaming}
      />

      {/* Response bubble */}
      <div className="assistant-message__bubble">
        <div className="assistant-message__content">
          {message.content}
        </div>

        {/* Streaming cursor */}
        {isStreaming && (
          <span className="assistant-message__cursor">▊</span>
        )}
      </div>

      {/* ASHC Evidence (if spec was edited) */}
      {hasASHCEvidence && (
        <ASHCEvidence data={ashcEvidence} />
      )}

      {/* Action panel (collapsible) */}
      {hasTools && (
        <div className="assistant-message__actions">
          <button
            className="assistant-message__actions-toggle"
            onClick={() => setActionPanelExpanded(!actionPanelExpanded)}
            aria-expanded={actionPanelExpanded}
          >
            {actionPanelExpanded ? '▼' : '▶'} {tools.length} action
            {tools.length !== 1 ? 's' : ''}
          </button>

          {actionPanelExpanded && (
            <ActionPanel tools={tools} />
          )}
        </div>
      )}
    </div>
  );
});

export default AssistantMessage;
