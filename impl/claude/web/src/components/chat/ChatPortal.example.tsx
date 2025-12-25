/**
 * ChatPortal Example Usage
 *
 * Demonstrates how to use ChatPortal component in chat sessions.
 */

import { ChatPortal } from './ChatPortal';
import type { PortalEmission } from '../../types/chat';

// =============================================================================
// Example 1: Auto-expanded portal with read-only access
// =============================================================================

const exampleReadOnlyEmission: PortalEmission = {
  portal_id: 'portal_001',
  destination: 'spec/protocols/witness.md',
  edge_type: 'references',
  access: 'read',
  content_preview: 'Witness Protocol\n================\n\nThe witness protocol...',
  content_full: 'Witness Protocol\n================\n\nThe witness protocol enables...',
  line_count: 42,
  exists: true,
  auto_expand: true,
  emitted_at: '2025-12-25T10:30:00Z',
};

export function ReadOnlyPortalExample() {
  const handleNavigate = (path: string) => {
    console.log('Navigate to:', path);
    // Implementation: navigate to file in editor
  };

  return (
    <ChatPortal
      emission={exampleReadOnlyEmission}
      onNavigate={handleNavigate}
    />
  );
}

// =============================================================================
// Example 2: Editable portal with read/write access
// =============================================================================

const exampleEditableEmission: PortalEmission = {
  portal_id: 'portal_002',
  destination: 'impl/claude/services/brain/cortex.py',
  edge_type: 'modifies',
  access: 'readwrite',
  content_preview: null,
  content_full: 'class CortexObserver:\n    """Observes cortex activity."""\n    pass',
  line_count: 15,
  exists: true,
  auto_expand: false,
  emitted_at: '2025-12-25T10:31:00Z',
};

export function EditablePortalExample() {
  const handleEdit = async (portalId: string, content: string) => {
    console.log('Save portal:', portalId);
    // Implementation: call API to write content
    await fetch('/api/portal/write', {
      method: 'POST',
      body: JSON.stringify({ portal_id: portalId, content }),
    });
  };

  const handleNavigate = (path: string) => {
    console.log('Navigate to:', path);
  };

  return (
    <ChatPortal
      emission={exampleEditableEmission}
      onEdit={handleEdit}
      onNavigate={handleNavigate}
    />
  );
}

// =============================================================================
// Example 3: Portal to missing file (graceful degradation)
// =============================================================================

const exampleMissingEmission: PortalEmission = {
  portal_id: 'portal_003',
  destination: 'spec/protocols/not-found.md',
  edge_type: 'references',
  access: 'read',
  content_preview: null,
  content_full: null,
  line_count: 0,
  exists: false,
  auto_expand: false,
  emitted_at: '2025-12-25T10:32:00Z',
};

export function MissingPortalExample() {
  return (
    <ChatPortal
      emission={exampleMissingEmission}
      // No handlers needed for missing file
    />
  );
}

// =============================================================================
// Example 4: Integration with AssistantMessage
// =============================================================================

import { AssistantMessage } from './AssistantMessage';

export function IntegratedPortalExample() {
  const turn = {
    turn_number: 1,
    user_message: {
      role: 'user' as const,
      content: 'Show me the witness protocol',
      mentions: [],
      linearity_tag: 'preserved' as const,
    },
    assistant_response: {
      role: 'assistant' as const,
      content: "Here's the witness protocol documentation:",
      mentions: [],
      linearity_tag: 'preserved' as const,
    },
    tools_used: [],
    evidence_delta: {
      tools_executed: 1,
      tools_succeeded: 1,
      confidence_change: 0.15,
    },
    confidence: 0.85,
    portal_emissions: [exampleReadOnlyEmission],
    started_at: '2025-12-25T10:30:00Z',
    completed_at: '2025-12-25T10:30:15Z',
  };

  const handleEditPortal = async (portalId: string, content: string) => {
    console.log('Edit portal:', portalId, content);
  };

  const handleNavigatePortal = (path: string) => {
    console.log('Navigate to:', path);
  };

  return (
    <AssistantMessage
      message={turn.assistant_response}
      tools={turn.tools_used}
      confidence={turn.confidence}
      evidenceDelta={turn.evidence_delta}
      portalEmissions={turn.portal_emissions}
      onEditPortal={handleEditPortal}
      onNavigatePortal={handleNavigatePortal}
    />
  );
}
