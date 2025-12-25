/**
 * ChatSidebar — Enhanced ChatPanel for sidebar integration
 *
 * "Chat is not a feature. Chat is an affordance that collapses discrete into continuous."
 *
 * This is a MINIMAL wrapper around ChatPanel that adds sidebar-specific features:
 * - Unread message indicator
 * - Enhanced compact mode styling
 * - Focus glow on input (earned, per UX-LAWS.md)
 *
 * The Workspace component handles:
 * - Toggle button and state
 * - Sidebar chrome (header, shortcuts)
 * - Collapse/expand animations
 *
 * @see docs/UX-LAWS.md - "90% steel, 10% earned glow"
 * @see constructions/Workspace/Workspace.tsx
 */

import { memo, useState, useEffect } from 'react';
import { ChatPanel } from './ChatPanel';
import { useChatStore } from './store';
import { useBranching } from './useBranching';
import { BranchControls } from './BranchControls';
import './ChatSidebar.css';

// =============================================================================
// Types
// =============================================================================

export interface ChatSidebarProps {
  /** Session ID to display (optional, creates new if not provided) */
  sessionId?: string;

  /** Project context (optional) */
  projectId?: string;

  /** Callback when unread status changes */
  onUnreadChange?: (hasUnread: boolean) => void;
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * ChatSidebar — ChatPanel wrapper for sidebar use
 *
 * Enhances ChatPanel with:
 * - Unread detection (watches for new assistant messages)
 * - Earned focus glow on input
 * - Optimized compact mode
 */
export const ChatSidebar = memo(function ChatSidebar({
  sessionId,
  projectId,
  onUnreadChange,
}: ChatSidebarProps) {
  const { currentSession } = useChatStore();
  const [hasUnread, setHasUnread] = useState(false);
  const [lastSeenTurnCount, setLastSeenTurnCount] = useState(0);

  // Branching system for merge access
  const branching = useBranching(currentSession?.id || '');

  // Detect unread messages (new turns since last seen)
  useEffect(() => {
    if (!currentSession) return;

    const currentTurnCount = currentSession.turns.length;

    // If we have more turns than last seen, mark as unread
    if (currentTurnCount > lastSeenTurnCount && lastSeenTurnCount > 0) {
      setHasUnread(true);
      onUnreadChange?.(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentSession?.turns.length, lastSeenTurnCount, onUnreadChange]);

  // Mark as read when user interacts (clicks anywhere in the sidebar)
  const handleInteraction = () => {
    if (currentSession && hasUnread) {
      setLastSeenTurnCount(currentSession.turns.length);
      setHasUnread(false);
      onUnreadChange?.(false);
    }
  };

  // Compute mergeable branches (all branches except current, non-merged)
  const mergeableBranches = branching.branches
    .filter((b) => !b.is_merged && b.id !== branching.currentBranch)
    .map((b) => ({ id: b.id, name: b.branch_name }));

  // Wrapper for fork that matches BranchControls signature
  const handleFork = async (name: string): Promise<void> => {
    await branching.fork(name);
  };

  return (
    <div
      className="chat-sidebar"
      onClick={handleInteraction}
      onFocus={handleInteraction}
    >
      {/* Unread indicator (red dot) */}
      {hasUnread && (
        <div className="chat-sidebar__unread-badge" aria-label="Unread messages">
          <span className="chat-sidebar__unread-dot" />
        </div>
      )}

      {/* Branch controls (compact mode) - only show if branches exist */}
      {currentSession && branching.branches.length > 0 && (
        <div className="chat-sidebar__branch-controls">
          <BranchControls
            turnCount={currentSession.turns.length}
            canFork={branching.canFork}
            activeBranches={branching.branches.filter((b) => !b.is_merged).length}
            mergeable={mergeableBranches}
            onFork={handleFork}
            onMerge={branching.merge}
            onRewind={branching.rewind}
          />
        </div>
      )}

      {/* ChatPanel in optimized compact mode */}
      <ChatPanel
        sessionId={sessionId}
        projectId={projectId}
        compact={true}
        showBranching={false}
        className="chat-sidebar__panel"
      />
    </div>
  );
});

export default ChatSidebar;
