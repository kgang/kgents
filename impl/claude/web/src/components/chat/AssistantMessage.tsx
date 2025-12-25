/**
 * AssistantMessage — Assistant response with evidence and tool transparency
 *
 * Displays:
 * - Response content (with streaming support)
 * - Confidence indicator (Bayesian evidence)
 * - Collapsible action panel (tools used)
 * - Portal emissions (inline content access)
 *
 * Follows spec Part VII (Tool Transparency) and Part IX (Evidence).
 */

import { memo, useState } from 'react';
import type { Message, ToolUse, EvidenceDelta } from './store';
import type { PortalEmission } from '../../types/chat';
import { ConfidenceIndicator } from './ConfidenceIndicator';
import { ActionPanel } from './ActionPanel';
import { ASHCEvidence, type ASHCEvidenceData } from './ASHCEvidence';
import { ChatPortal } from './ChatPortal';
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
  portalEmissions?: PortalEmission[];
  onEditPortal?: (portalId: string, content: string) => Promise<void>;
  onNavigatePortal?: (path: string) => void;
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
  portalEmissions = [],
  onEditPortal,
  onNavigatePortal,
}: AssistantMessageProps) {
  const [actionPanelExpanded, setActionPanelExpanded] = useState(false);

  const hasTools = tools.length > 0;
  const hasASHCEvidence = ashcEvidence !== null && ashcEvidence !== undefined;
  const hasPortalEmissions = portalEmissions.length > 0;

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

      {/* Portal emissions (inline content) */}
      {hasPortalEmissions && (
        <div className="assistant-message__portals">
          {portalEmissions.map((emission) => (
            <ChatPortal
              key={emission.portal_id}
              emission={emission}
              onEdit={onEditPortal}
              onNavigate={onNavigatePortal}
            />
          ))}
        </div>
      )}

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
