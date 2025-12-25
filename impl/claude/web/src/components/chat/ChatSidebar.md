# ChatSidebar — Chat Integration for Workspace

> "Chat is not a feature. Chat is an affordance that collapses discrete into continuous."

## Overview

`ChatSidebar` is a minimal wrapper around `ChatPanel` that enhances it for right sidebar integration in the Workspace. It follows the UX Laws principle: **90% steel, 10% earned glow**.

## Architecture

```
┌────────────────────────────────────────┐
│          Workspace (Parent)            │
│  - Toggle button                       │
│  - Header with "Ctrl+J" hint           │
│  - Collapse/expand state               │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │      ChatSidebar (Wrapper)       │ │
│  │  - Unread detection              │ │
│  │  - Focus glow on input           │ │
│  │  - Compact mode optimizations    │ │
│  │                                  │ │
│  │  ┌────────────────────────────┐ │ │
│  │  │    ChatPanel (Core)        │ │ │
│  │  │  - Message list            │ │ │
│  │  │  - Input area              │ │ │
│  │  │  - Streaming support       │ │ │
│  │  └────────────────────────────┘ │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

## Key Features

### 1. Unread Detection

Tracks new messages and shows a red dot indicator:

```tsx
<ChatSidebar
  onUnreadChange={(hasUnread) => {
    // Parent can show indicator on toggle button
    setChatHasUnread(hasUnread);
  }}
/>
```

**Logic**:
- Monitors `currentSession.turns.length`
- Marks unread when new turns appear
- Clears unread on user interaction (click/focus)

### 2. Earned Glow (UX-LAWS.md)

Glow is **earned**, not decorative:

| Trigger | Glow Type | Duration |
|---------|-----------|----------|
| Input focus | Blue subtle | While focused |
| Message sent | Green flash | 0.6s |
| Hover | None | N/A |
| Idle | None | N/A |

```css
/* Earned glow on focus */
.chat-sidebar .chat-panel__input:has(:focus-visible) {
  box-shadow: 0 -2px 8px rgba(59, 130, 246, 0.15);
}

/* Earned glow on success */
.chat-sidebar .chat-panel__input:has(.input-area--success) {
  animation: success-flash 0.6s ease-out;
}
```

### 3. Compact Mode Optimizations

Tighter spacing for sidebar use:

- Messages: 6px padding (vs 8px default)
- Context indicator: 4px padding (vs 6px)
- Mutations: 2px gap (vs 4px)
- Hides context indicator entirely in compact mode

## Usage

### In Workspace

```tsx
import { ChatSidebar } from '../../components/chat/ChatSidebar';

function Workspace() {
  const [chatHasUnread, setChatHasUnread] = useState(false);

  return (
    <aside className="workspace__right">
      <button onClick={toggleChat}>
        {/* Unread indicator on toggle button */}
        {chatHasUnread && !isOpen && (
          <span className="workspace__sidebar-unread" />
        )}
        Chat
      </button>

      <div className="workspace__sidebar-body">
        <ChatSidebar onUnreadChange={setChatHasUnread} />
      </div>
    </aside>
  );
}
```

### Standalone (Rare)

```tsx
import { ChatSidebar } from '@/components/chat/ChatSidebar';

function CustomLayout() {
  return (
    <div className="my-layout">
      <ChatSidebar
        sessionId="session-123"
        projectId="project-abc"
        onUnreadChange={(unread) => console.log('Unread:', unread)}
      />
    </div>
  );
}
```

## Props

```typescript
interface ChatSidebarProps {
  /** Session ID to display (optional, creates new if not provided) */
  sessionId?: string;

  /** Project context (optional) */
  projectId?: string;

  /** Callback when unread status changes */
  onUnreadChange?: (hasUnread: boolean) => void;
}
```

## CSS Variables

Uses standard kgents design tokens:

```css
--steel-950: #0a0a0a;      /* Background */
--steel-800: #27272a;      /* Borders */
--steel-400: #a1a1aa;      /* Muted text */
--steel-100: #f4f4f5;      /* Active text */
--error-500: #ef4444;      /* Unread indicator */
--focus-ring: #3b82f6;     /* Focus glow */
--success-500: #22c55e;    /* Success glow */
```

## Accessibility

- ARIA labels for unread indicator
- Focus-visible indicators (keyboard navigation)
- Reduced motion support (`@media (prefers-reduced-motion: reduce)`)
- Click and focus both clear unread state

## Design Philosophy

From `docs/UX-LAWS.md`:

> **The Glow Law**: "90% steel, 10% earned glow"
>
> Glow is earned through:
> - ✅ Successful actions (message sent)
> - ✅ Focus states (actively typing)
> - ✅ Completed tasks (operation finished)
>
> Glow is NOT earned through:
> - ❌ Hover states (acknowledgment, not celebration)
> - ❌ Decoration (no gratuitous animation)
> - ❌ Loading states (stillness, not pulse)

## Implementation Notes

### Why a Wrapper?

1. **Separation of Concerns**: Workspace handles sidebar chrome, ChatSidebar handles chat-specific enhancements
2. **Reusability**: ChatPanel remains pure, usable outside sidebars
3. **Minimal Duplication**: ChatSidebar adds only sidebar-specific features

### Why Not Merge into ChatPanel?

- ChatPanel is used in multiple contexts (sidebar, modal, embedded)
- Sidebar-specific features (unread tracking, compact optimizations) don't belong in core
- Workspace already handles toggle/header/animations

### Unread Detection Algorithm

```typescript
// Detect unread when turns increase
if (currentTurnCount > lastSeenTurnCount && lastSeenTurnCount > 0) {
  setHasUnread(true);
}

// Clear unread on any interaction
const handleInteraction = () => {
  setLastSeenTurnCount(currentSession.turns.length);
  setHasUnread(false);
};
```

**Edge cases handled**:
- First load (lastSeenTurnCount === 0): no unread
- Session switch: resets counter
- No session: no unread tracking

## Testing

Key scenarios to test:

1. **Unread Detection**
   - Send message → verify no unread (own message)
   - Receive assistant reply → verify unread
   - Click sidebar → verify unread clears

2. **Focus Glow**
   - Focus input → verify blue glow
   - Blur input → verify glow removes
   - Send message → verify green flash

3. **Compact Mode**
   - Verify context indicator hidden
   - Verify tighter spacing
   - Verify branch tree collapses

4. **Accessibility**
   - Keyboard navigation works
   - Screen reader announces unread
   - Reduced motion disables animations

## Related Files

- `/Users/kentgang/git/kgents/impl/claude/web/src/components/chat/ChatPanel.tsx` - Core chat component
- `/Users/kentgang/git/kgents/impl/claude/web/src/constructions/Workspace/Workspace.tsx` - Parent container
- `/Users/kentgang/git/kgents/docs/UX-LAWS.md` - Design principles
- `/Users/kentgang/git/kgents/spec/protocols/chat-web.md` - Chat protocol spec

## Future Enhancements

Potential additions (not currently implemented):

- [ ] Voice mode indicator (when voice chat is active)
- [ ] Typing indicator for Claude
- [ ] Quick reply shortcuts (pre-defined prompts)
- [ ] Drag-to-resize sidebar width
- [ ] Pin important messages
- [ ] Export conversation as markdown

---

**Filed**: 2025-12-25
**Status**: Production-ready
**Follows**: UX-LAWS.md, spec/protocols/chat-web.md
