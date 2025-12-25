/**
 * ToolTransparencyExample — Visual demo of tool transparency components
 *
 * Shows how ToolPanel, ActionPanel, TransparencySelector, and MutationAcknowledger
 * work together in a chat interface.
 *
 * This is a demo component for development/testing. Not used in production.
 */

import { useState } from 'react';
import { ToolPanel } from './ToolPanel';
import { MutationAcknowledger } from './MutationAcknowledger';
import type { ToolManifest, TransparencyLevel, MutationAcknowledgment } from '../../types/chat';
import type { MutationEvent } from './MutationAcknowledger';

// =============================================================================
// Mock Data
// =============================================================================

const MOCK_TOOLS: ToolManifest[] = [
  {
    name: 'Read File',
    description: 'Read contents of a file',
    status: 'available',
    is_pure_read: true,
    is_destructive: false,
  },
  {
    name: 'Write File',
    description: 'Write or modify a file',
    status: 'available',
    is_pure_read: false,
    is_destructive: false,
  },
  {
    name: 'Run Command',
    description: 'Execute a shell command',
    status: 'available',
    is_pure_read: false,
    is_destructive: false,
  },
  {
    name: 'Web Search',
    description: 'Search the web for information',
    status: 'limited',
    is_pure_read: true,
    is_destructive: false,
    rate_limit: {
      current: 7,
      limit: 10,
      reset_at: '2025-12-25T00:00:00Z',
    },
  },
  {
    name: 'Deploy',
    description: 'Deploy to production',
    status: 'gated',
    is_pure_read: false,
    is_destructive: true,
  },
];

const MOCK_MUTATION: MutationEvent = {
  mutation_id: 'mut-001',
  tool_name: 'Write File',
  description: 'File written',
  target: 'impl/claude/services/chat/session.py',
  is_destructive: false,
};

// =============================================================================
// Main Component
// =============================================================================

export function ToolTransparencyExample() {
  const [transparencyLevel, setTransparencyLevel] = useState<TransparencyLevel>('approval');
  const [showMutation, setShowMutation] = useState(false);
  const [toolPanelCollapsed, setToolPanelCollapsed] = useState(false);

  const handleAcknowledge = (ack: MutationAcknowledgment) => {
    console.log('Acknowledged:', ack);
    setShowMutation(false);
  };

  const handleToolClick = (tool: ToolManifest) => {
    console.log('Tool clicked:', tool.name);
    // eslint-disable-next-line no-alert
    alert(`Tool: ${tool.name}\n\n${tool.description}\n\nStatus: ${tool.status}`);
  };

  return (
    <div style={{
      display: 'flex',
      gap: '1rem',
      padding: '2rem',
      background: 'rgba(12, 12, 16, 1)',
      minHeight: '100vh',
    }}>
      {/* Sidebar: Tool Panel */}
      <div style={{ flexShrink: 0 }}>
        <ToolPanel
          tools={MOCK_TOOLS}
          transparencyLevel={transparencyLevel}
          onTransparencyChange={setTransparencyLevel}
          onToolClick={handleToolClick}
          collapsed={toolPanelCollapsed}
          onToggleCollapse={() => setToolPanelCollapsed(!toolPanelCollapsed)}
        />
      </div>

      {/* Main content area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* Demo controls */}
        <div style={{
          padding: '1rem',
          background: 'rgba(20, 20, 24, 0.95)',
          border: '1px solid rgba(100, 100, 120, 0.3)',
          borderRadius: '4px',
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: 'rgba(229, 221, 213, 1)' }}>
            Tool Transparency Demo
          </h3>
          <p style={{ margin: '0 0 1rem 0', color: 'rgba(160, 160, 172, 1)', fontSize: '0.875rem' }}>
            This demo shows the four tool transparency components working together.
          </p>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button
              onClick={() => setShowMutation(true)}
              style={{
                padding: '0.5rem 1rem',
                background: 'rgba(196, 167, 125, 0.15)',
                border: '1px solid rgba(196, 167, 125, 0.4)',
                borderRadius: '4px',
                color: 'rgba(196, 167, 125, 1)',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: 600,
              }}
            >
              Trigger Mutation
            </button>
            <button
              onClick={() => setToolPanelCollapsed(!toolPanelCollapsed)}
              style={{
                padding: '0.5rem 1rem',
                background: 'rgba(160, 160, 172, 0.15)',
                border: '1px solid rgba(160, 160, 172, 0.4)',
                borderRadius: '4px',
                color: 'rgba(160, 160, 172, 1)',
                cursor: 'pointer',
                fontSize: '0.875rem',
              }}
            >
              {toolPanelCollapsed ? 'Expand' : 'Collapse'} Tool Panel
            </button>
          </div>
          <div style={{
            marginTop: '1rem',
            padding: '0.75rem',
            background: 'rgba(28, 28, 32, 0.6)',
            borderRadius: '4px',
            fontSize: '0.8125rem',
            color: 'rgba(160, 160, 172, 1)',
          }}>
            <strong style={{ color: 'rgba(229, 221, 213, 1)' }}>Current Transparency:</strong>{' '}
            {transparencyLevel.charAt(0).toUpperCase() + transparencyLevel.slice(1)}
          </div>
        </div>

        {/* Action Panel example - using mock data */}
        <div style={{
          padding: '1rem',
          background: 'rgba(20, 20, 24, 0.8)',
          border: '1px solid rgba(100, 100, 120, 0.3)',
          borderRadius: '4px',
        }}>
          <h4 style={{ margin: '0 0 0.5rem 0', color: 'rgba(229, 221, 213, 1)', fontSize: '0.875rem' }}>
            Action Panel Preview
          </h4>
          <p style={{ margin: 0, color: 'rgba(160, 160, 172, 1)', fontSize: '0.875rem' }}>
            Turn 12 would show tool executions here with collapsible details.
          </p>
        </div>

        {/* Message area placeholder */}
        <div style={{
          flex: 1,
          padding: '1rem',
          background: 'rgba(20, 20, 24, 0.8)',
          border: '1px solid rgba(100, 100, 120, 0.3)',
          borderRadius: '4px',
          color: 'rgba(160, 160, 172, 1)',
          fontSize: '0.875rem',
        }}>
          <p>Chat messages would appear here...</p>
          <p style={{ marginTop: '0.5rem' }}>
            Try clicking "Trigger Mutation" to see the MutationAcknowledger in action.
          </p>
          <p style={{ marginTop: '0.5rem' }}>
            Change the transparency level in the Tool Panel to see how it affects visibility.
          </p>
        </div>
      </div>

      {/* Mutation acknowledger overlay */}
      {showMutation && (
        <div style={{
          position: 'fixed',
          bottom: '2rem',
          right: '2rem',
          zIndex: 100,
        }}>
          <MutationAcknowledger
            mutation={MOCK_MUTATION}
            onAcknowledge={handleAcknowledge}
            onTimeout={handleAcknowledge}
          />
        </div>
      )}
    </div>
  );
}

export default ToolTransparencyExample;
