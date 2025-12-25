/**
 * ChatPage — Conversational Interface
 *
 * "Chat is not a feature. Chat is an affordance that collapses discrete into continuous."
 *
 * Full-page chat interface with:
 * - Session management (URL-driven sessionId)
 * - Project context support
 * - Branch tree visualization
 * - Message streaming
 * - Tool transparency
 *
 * Follows elastic-ui-patterns for responsive layout.
 *
 * @see spec/protocols/chat-web.md
 */

import { useSearchParams } from 'react-router-dom';
import { ChatPanel } from '../components/chat/ChatPanel';
import { ErrorBoundary } from '../components/error/ErrorBoundary';

// =============================================================================
// Main Component
// =============================================================================

export function ChatPage() {
  const [searchParams] = useSearchParams();

  // Extract session and project IDs from URL params
  const sessionId = searchParams.get('session') || undefined;
  const projectId = searchParams.get('project') || undefined;

  return (
    <ErrorBoundary>
      <div className="chat-page flex flex-col h-full bg-surface-canvas">
        <ChatPanel
          sessionId={sessionId}
          projectId={projectId}
          showBranching={true}
          compact={false}
        />
      </div>
    </ErrorBoundary>
  );
}

export default ChatPage;
