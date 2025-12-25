# ChatSidebar Quick Reference

## Import

```typescript
import { ChatSidebar } from '@/components/chat/ChatSidebar';
```

## Basic Usage

```tsx
function MyWorkspace() {
  const [hasUnread, setHasUnread] = useState(false);

  return (
    <aside className="sidebar">
      {/* Toggle button with unread indicator */}
      <button onClick={toggleSidebar}>
        {hasUnread && <span className="unread-dot" />}
        Chat
      </button>

      {/* ChatSidebar */}
      <ChatSidebar onUnreadChange={setHasUnread} />
    </aside>
  );
}
```

## Props

```typescript
interface ChatSidebarProps {
  sessionId?: string;           // Optional session ID
  projectId?: string;            // Optional project context
  onUnreadChange?: (hasUnread: boolean) => void;  // Unread callback
}
```

## CSS Hooks

```css
/* Override unread indicator color */
.chat-sidebar__unread-dot {
  background: var(--custom-color);
}

/* Override focus glow */
.chat-sidebar .chat-panel__input:has(:focus-visible) {
  box-shadow: 0 -2px 8px rgba(r, g, b, opacity);
}

/* Override spacing */
.chat-sidebar .chat-panel__messages {
  padding: 8px;  /* Default: 6px */
}
```

## Behavior

| Event | Action |
|-------|--------|
| New message arrives | `hasUnread = true`, red dot appears |
| User clicks sidebar | `hasUnread = false`, red dot disappears |
| User focuses input | Blue glow (earned) |
| User sends message | Green flash (earned) |

## Keyboard

| Key | Action |
|-----|--------|
| `Ctrl+J` | Toggle sidebar (handled by parent) |
| `Tab` | Navigate to input |
| `Enter` | Send message |

## States

```tsx
// Unread
<ChatSidebar onUnreadChange={(unread) => {
  if (unread) {
    // Show notification
  }
}} />

// With session
<ChatSidebar sessionId="session-123" />

// With project context
<ChatSidebar projectId="project-abc" />
```

## Styling

**Width**: Controlled by parent (recommended: 320px)
**Height**: Full height of parent container
**Background**: `var(--steel-950, #0a0a0a)`
**Borders**: `var(--steel-800, #27272a)`

## Responsive

| Breakpoint | Behavior |
|------------|----------|
| Desktop (>1024px) | Fixed sidebar |
| Tablet (768-1024px) | Overlay sidebar |
| Mobile (<768px) | Full-width overlay |

## Accessibility

```html
<!-- Proper structure -->
<div class="chat-sidebar">
  <div
    class="chat-sidebar__unread-badge"
    aria-label="Unread messages"
  >
    <span class="chat-sidebar__unread-dot" />
  </div>
  <ChatPanel compact={true} />
</div>
```

## Performance

- **Memoized**: Component wrapped in `React.memo()`
- **Minimal re-renders**: Only on turn count change
- **GPU-accelerated**: Animations use CSS transforms
- **Accessibility**: Respects `prefers-reduced-motion`

## Gotchas

1. **Unread detection requires interaction**: Click or focus clears unread
2. **Parent controls width**: ChatSidebar fills parent container
3. **Compact mode forced**: Always renders ChatPanel with `compact={true}`
4. **Glow is earned**: No hover glow, only focus/success

## Integration Checklist

- [ ] Import ChatSidebar from `@/components/chat/ChatSidebar`
- [ ] Add `onUnreadChange` callback to parent state
- [ ] Show unread indicator on toggle button when collapsed
- [ ] Set sidebar width to 320px (recommended)
- [ ] Handle Ctrl+J keyboard shortcut in parent
- [ ] Test unread detection (send message, click sidebar)
- [ ] Test focus glow (click input)
- [ ] Test responsive behavior (resize window)

## Files

- `ChatSidebar.tsx` - Component
- `ChatSidebar.css` - Styles
- `ChatSidebar.md` - Full documentation
- `ChatSidebar.visual.md` - Visual design guide
- `QUICK_REF.md` - This file

---

**Updated**: 2025-12-25
**Status**: Production-ready
