/**
 * ToolPanel — Available tools sidebar with transparency controls
 *
 * From spec/protocols/chat-web.md Part VII.1:
 * - Shows available tools with status indicators
 * - ● Available, ◐ Limited (rate limit), ◆ Gated (requires approval)
 * - Per-tool budget tracking
 * - Transparency level selector
 *
 * "Mutations MUST be visible - A toast that can be ignored is a toast that wasn't heard."
 */

import { useState } from 'react';
import type { ToolManifest, TransparencyLevel } from '../../types/chat';
import { TransparencySelector } from './TransparencySelector';
import './ToolPanel.css';

// =============================================================================
// Types
// =============================================================================

export interface ToolPanelProps {
  /** Available tools from AGENTESE nodes */
  tools: ToolManifest[];
  /** Current transparency level */
  transparencyLevel: TransparencyLevel;
  /** Callback when transparency level changes */
  onTransparencyChange: (level: TransparencyLevel) => void;
  /** Callback when tool is clicked for details */
  onToolClick?: (tool: ToolManifest) => void;
  /** Whether panel is collapsed */
  collapsed?: boolean;
  /** Callback to toggle collapse */
  onToggleCollapse?: () => void;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get status indicator icon and color for tool status.
 */
function getStatusIndicator(tool: ToolManifest): { icon: string; color: string; title: string } {
  if (tool.status === 'gated') {
    return {
      icon: '◆',
      color: 'text-red-500',
      title: 'Requires user approval',
    };
  }

  if (tool.status === 'limited' && tool.rate_limit) {
    const { current, limit } = tool.rate_limit;
    const percentage = (current / limit) * 100;

    if (percentage >= 90) {
      return {
        icon: '◆',
        color: 'text-red-500',
        title: `Rate limit nearly exhausted: ${current}/${limit}`,
      };
    } else if (percentage >= 70) {
      return {
        icon: '◐',
        color: 'text-amber-500',
        title: `Approaching rate limit: ${current}/${limit}`,
      };
    }
  }

  return {
    icon: '●',
    color: 'text-emerald-500',
    title: 'Available',
  };
}

/**
 * Format rate limit display.
 */
function formatRateLimit(tool: ToolManifest): string | null {
  if (!tool.rate_limit) return null;
  const { current, limit } = tool.rate_limit;
  return `${current}/${limit} today`;
}

// =============================================================================
// Tool Item Component
// =============================================================================

interface ToolItemProps {
  tool: ToolManifest;
  onClick?: () => void;
}

function ToolItem({ tool, onClick }: ToolItemProps) {
  const status = getStatusIndicator(tool);
  const rateLimit = formatRateLimit(tool);
  const isClickable = !!onClick;

  return (
    <div
      className={`tool-panel__item ${isClickable ? 'tool-panel__item--clickable' : ''}`}
      onClick={onClick}
      role={isClickable ? 'button' : 'listitem'}
      tabIndex={isClickable ? 0 : undefined}
      onKeyDown={
        isClickable
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
      title={tool.description}
    >
      <div className="tool-panel__item-header">
        <span className={`tool-panel__status ${status.color}`} title={status.title}>
          {status.icon}
        </span>
        <span className="tool-panel__name">{tool.name}</span>
      </div>

      {rateLimit && (
        <div className="tool-panel__rate-limit">
          {rateLimit}
        </div>
      )}

      {tool.is_destructive && (
        <div className="tool-panel__warning" title="This tool performs destructive operations">
          ◇
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function ToolPanel({
  tools,
  transparencyLevel,
  onTransparencyChange,
  onToolClick,
  collapsed = false,
  onToggleCollapse,
}: ToolPanelProps) {
  const [searchQuery, setSearchQuery] = useState('');

  // Filter tools by search query
  const filteredTools = tools.filter((tool) =>
    tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    tool.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Group tools by status for better organization
  const availableTools = filteredTools.filter((t) => t.status === 'available');
  const limitedTools = filteredTools.filter((t) => t.status === 'limited');
  const gatedTools = filteredTools.filter((t) => t.status === 'gated');

  if (collapsed) {
    return (
      <div className="tool-panel tool-panel--collapsed">
        <button
          className="tool-panel__toggle"
          onClick={onToggleCollapse}
          aria-label="Expand tool panel"
        >
          ◈
        </button>
      </div>
    );
  }

  return (
    <div className="tool-panel">
      {/* Header */}
      <div className="tool-panel__header">
        <h3 className="tool-panel__title">Tools</h3>
        {onToggleCollapse && (
          <button
            className="tool-panel__collapse-btn"
            onClick={onToggleCollapse}
            aria-label="Collapse tool panel"
          >
            ×
          </button>
        )}
      </div>

      {/* Search */}
      {tools.length > 5 && (
        <div className="tool-panel__search">
          <input
            type="text"
            className="tool-panel__search-input"
            placeholder="Search tools..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search tools"
          />
        </div>
      )}

      {/* Tool List */}
      <div className="tool-panel__tools" role="list">
        {/* Available Tools */}
        {availableTools.length > 0 && (
          <div className="tool-panel__group">
            <div className="tool-panel__group-header">Available</div>
            {availableTools.map((tool) => (
              <ToolItem
                key={tool.name}
                tool={tool}
                onClick={onToolClick ? () => onToolClick(tool) : undefined}
              />
            ))}
          </div>
        )}

        {/* Limited Tools */}
        {limitedTools.length > 0 && (
          <div className="tool-panel__group">
            <div className="tool-panel__group-header">Limited</div>
            {limitedTools.map((tool) => (
              <ToolItem
                key={tool.name}
                tool={tool}
                onClick={onToolClick ? () => onToolClick(tool) : undefined}
              />
            ))}
          </div>
        )}

        {/* Gated Tools */}
        {gatedTools.length > 0 && (
          <div className="tool-panel__group">
            <div className="tool-panel__group-header">Requires Approval</div>
            {gatedTools.map((tool) => (
              <ToolItem
                key={tool.name}
                tool={tool}
                onClick={onToolClick ? () => onToolClick(tool) : undefined}
              />
            ))}
          </div>
        )}

        {/* No results */}
        {filteredTools.length === 0 && (
          <div className="tool-panel__empty">
            No tools found matching "{searchQuery}"
          </div>
        )}
      </div>

      {/* Transparency Selector */}
      <div className="tool-panel__footer">
        <TransparencySelector
          level={transparencyLevel}
          onChange={onTransparencyChange}
        />
      </div>
    </div>
  );
}

export default ToolPanel;
