/**
 * ChatPage — Conversational Interface
 *
 * @deprecated This page is DEPRECATED as of 2025-12-25.
 * Chat functionality has been moved to a sidebar in the Hypergraph Editor.
 * Use /world.document and toggle chat with Ctrl+J (Cmd+J on Mac).
 *
 * This page is kept for backward compatibility during the grace period.
 * It will be removed in a future release.
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

import { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ChatPanel } from '../components/chat/ChatPanel';
import { ErrorBoundary } from '../components/error/ErrorBoundary';

// =============================================================================
// Main Component
// =============================================================================

/**
 * @deprecated Use the Chat sidebar in /world.document instead (Ctrl+J to toggle)
 */
export function ChatPage() {
  const [searchParams] = useSearchParams();

  // Extract session and project IDs from URL params
  const sessionId = searchParams.get('session') || undefined;
  const projectId = searchParams.get('project') || undefined;

  // Log deprecation warning on mount
  useEffect(() => {
    console.warn(
      '[DEPRECATED] ChatPage is deprecated. ' +
        'Chat is now a sidebar in /world.document. Use Ctrl+J (Cmd+J on Mac) to toggle.'
    );
  }, []);

  return (
    <ErrorBoundary>
      <div className="chat-page flex flex-col h-full bg-surface-canvas">
        {/* Deprecation Banner */}
        <div className="bg-amber-900/30 border-b border-amber-700/50 px-4 py-2 text-amber-200 text-sm">
          <strong>DEPRECATED:</strong> This page is deprecated. Chat is now a sidebar in the{' '}
          <a href="/world.document" className="underline hover:text-amber-100">
            Hypergraph Editor
          </a>
          . Use <kbd className="px-1 py-0.5 bg-amber-800/50 rounded text-xs">Ctrl+J</kbd> to toggle.
        </div>

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
