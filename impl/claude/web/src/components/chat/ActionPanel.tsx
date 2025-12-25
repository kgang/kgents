/**
 * ActionPanel — Tool transparency with collapsible details
 *
 * Shows:
 * - Tool invocations with status
 * - Input/output (expandable)
 * - Execution time
 *
 * States:
 * - ✓ Completed
 * - ⏳ In progress
 * - ✗ Failed
 * - ⊘ Cancelled
 *
 * @see spec/protocols/chat-web.md Part VII.4
 */

import { memo, useState } from 'react';
import type { ToolUse } from './store';

// =============================================================================
// Types
// =============================================================================

export interface ActionPanelProps {
  tools: ToolUse[];
}

interface ToolItemProps {
  tool: ToolUse;
}

// =============================================================================
// ToolItem Component
// =============================================================================

function ToolItem({ tool }: ToolItemProps) {
  const [expanded, setExpanded] = useState(false);

  const statusIcon = tool.success ? '●' : '◆';
  const statusClass = tool.success ? 'success' : 'failed';

  return (
    <div className={`action-panel__tool action-panel__tool--${statusClass}`}>
      <button
        className="action-panel__tool-header"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
      >
        <span className="action-panel__tool-status">{statusIcon}</span>
        <span className="action-panel__tool-name">{tool.name}</span>
        <span className="action-panel__tool-duration">
          {tool.duration_ms}ms
        </span>
        <span className="action-panel__tool-toggle">
          {expanded ? '▼' : '▶'}
        </span>
      </button>

      {expanded && (
        <div className="action-panel__tool-details">
          {/* Input */}
          <div className="action-panel__tool-section">
            <h4 className="action-panel__tool-section-title">Input</h4>
            <pre className="action-panel__tool-code">
              {JSON.stringify(tool.input, null, 2)}
            </pre>
          </div>

          {/* Output */}
          <div className="action-panel__tool-section">
            <h4 className="action-panel__tool-section-title">Output</h4>
            <pre className="action-panel__tool-code">
              {typeof tool.output === 'string'
                ? tool.output
                : JSON.stringify(tool.output, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * ActionPanel — Transparent tool usage display
 */
export const ActionPanel = memo(function ActionPanel({
  tools,
}: ActionPanelProps) {
  const successCount = tools.filter((t) => t.success).length;
  const failCount = tools.length - successCount;

  return (
    <div className="action-panel">
      <div className="action-panel__summary">
        <span className="action-panel__summary-success">
          {successCount} succeeded
        </span>
        {failCount > 0 && (
          <span className="action-panel__summary-failed">
            {failCount} failed
          </span>
        )}
      </div>

      <div className="action-panel__tools">
        {tools.map((tool, idx) => (
          <ToolItem key={idx} tool={tool} />
        ))}
      </div>
    </div>
  );
});

export default ActionPanel;
