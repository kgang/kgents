# Portal Integration Verification Checklist

## ✅ Code Integration Complete

### Type Safety
- [x] TypeScript compilation passes (`npm run typecheck`)
- [x] Production build succeeds (`npm run build`)
- [x] ESLint passes (warnings only, no errors)

### Component Chain
- [x] ChatPanel defines `handleEditPortal`
- [x] ChatPanel defines `handleNavigatePortal`
- [x] ChatPanel passes handlers to MessageList
- [x] MessageList accepts handlers in props interface
- [x] MessageList passes handlers to AssistantMessage
- [x] AssistantMessage accepts handlers in props interface
- [x] AssistantMessage passes handlers to ChatPortal
- [x] ChatPortal implements full edit/navigate functionality

### Type Definitions
- [x] `PortalEmission` interface exists in `types/chat.ts`
- [x] `Turn` interface includes `portal_emissions?: PortalEmission[]`
- [x] All handler signatures match across component chain
- [x] ChatPortal exports in `components/chat/index.ts`

### File Structure
- [x] `ChatPortal.tsx` exists with full implementation
- [x] `ChatPortal.css` exists with brutalist styling
- [x] Component imports GrowingContainer from joy components

---

## 🧪 Runtime Testing Checklist

### Basic Rendering
- [ ] Portal emissions appear in assistant messages
- [ ] Portal header shows: `[edge_type] ──→ destination`
- [ ] Metadata shows: line count, access level, file status
- [ ] Auto-expand portals expand by default

### Expand/Collapse
- [ ] Click toggle to expand portal
- [ ] Click toggle to collapse portal
- [ ] GrowingContainer animates smoothly
- [ ] Content preserves formatting (code indentation)

### Navigation
- [ ] Navigate button appears (↗ icon)
- [ ] Click navigate opens new tab
- [ ] URL format: `/editor?file=${encodeURIComponent(path)}`
- [ ] Console logs: "Navigate to: {path}"

### Read-Only Portals (access: 'read')
- [ ] No edit button appears
- [ ] Content is read-only
- [ ] Syntax highlighting works
- [ ] Can still navigate

### Read-Write Portals (access: 'readwrite')
- [ ] Edit button appears (✎ icon)
- [ ] Click edit enters edit mode
- [ ] Textarea auto-focuses
- [ ] Cursor moves to end of content
- [ ] Line count determines textarea rows

### Editing Mode
- [ ] Textarea shows current content
- [ ] Can modify content freely
- [ ] Save button enabled
- [ ] Cancel button enabled
- [ ] Keyboard shortcuts work:
  - [ ] Cmd+Enter / Ctrl+Enter saves
  - [ ] Esc cancels
- [ ] Hint text shows: "Cmd+Enter to save, Esc to cancel"

### Save Flow
- [ ] Click Save or press Cmd+Enter
- [ ] Sync status shows: ◐ (saving)
- [ ] Buttons disabled during save
- [ ] On success:
  - [ ] Sync status shows: ✓ (saved)
  - [ ] Edit mode exits
  - [ ] Console logs: "Portal content saved: {portalId}"
  - [ ] Success indicator disappears after 2s
- [ ] On error:
  - [ ] Sync status shows: ⚠️ (failed)
  - [ ] Error message appears
  - [ ] Stays in edit mode
  - [ ] Can retry save

### Cancel Flow
- [ ] Click Cancel or press Esc
- [ ] Edit mode exits
- [ ] Content resets to original
- [ ] Error state clears

### API Integration
- [ ] POST request sent to `/api/chat/portal/write`
- [ ] Request body: `{portal_id, content}`
- [ ] Headers include `Content-Type: application/json`
- [ ] Network tab shows correct payload

### Edge Cases
- [ ] Empty portal content shows "(empty)"
- [ ] Missing file shows "file missing" badge
- [ ] Multi-line content preserves newlines
- [ ] Large files (>30 lines) show scrollbar
- [ ] Portal with only `content_preview` shows preview
- [ ] Portal with `content_full` shows full content

---

## 🎨 Visual Verification

### Styling
- [ ] Portal container has brutalist border
- [ ] Header has monospace font
- [ ] Toggle button is clickable
- [ ] Action buttons have hover states
- [ ] Textarea matches portal styling
- [ ] Sync status icons are visible
- [ ] Error text is red/prominent

### Responsive
- [ ] Portal adapts to container width
- [ ] Long paths wrap or truncate gracefully
- [ ] Textarea width matches container
- [ ] Buttons don't overflow on mobile

### Accessibility
- [ ] Toggle has aria-expanded attribute
- [ ] Buttons have descriptive titles (tooltips)
- [ ] Keyboard navigation works
- [ ] Focus states are visible

---

## 🔌 Backend Integration

### Required Endpoint
```
POST /api/chat/portal/write

Request:
{
  "portal_id": "uuid-string",
  "content": "file content..."
}

Response:
200 OK          → Success
400 Bad Request → Invalid input
404 Not Found   → Portal doesn't exist
403 Forbidden   → Read-only portal
500 Server Error → Save failed
```

### Backend Checklist
- [ ] Endpoint exists at `/api/chat/portal/write`
- [ ] Validates `portal_id` and `content` in request body
- [ ] Writes content to portal destination
- [ ] Returns appropriate HTTP status codes
- [ ] Handles errors gracefully
- [ ] Logs save operations

---

## 📊 Performance

### Rendering
- [ ] Portal emissions render without lag
- [ ] Expanding/collapsing is smooth
- [ ] Typing in textarea is responsive
- [ ] No console errors during interactions

### Memory
- [ ] Multiple portals don't cause memory issues
- [ ] Edit mode cleanup on unmount
- [ ] Event listeners properly removed

---

## 🐛 Known Limitations

1. **Editor Integration**: Navigation currently opens new tab. Could integrate with in-app routing.
2. **Optimistic Updates**: No local state update before API confirmation.
3. **Diff View**: No before/after comparison when editing.
4. **Portal History**: No version tracking across turns.
5. **Syntax Highlighting**: Basic `<pre><code>`, no language-aware coloring.

---

## ✅ Completion Criteria

Integration is considered complete when:

1. ✅ All TypeScript checks pass
2. ✅ Production build succeeds
3. ✅ Component chain is properly wired
4. [ ] Backend endpoint is implemented
5. [ ] Manual testing passes all checklist items
6. [ ] No console errors in browser DevTools
7. [ ] Portal edit flow works end-to-end

---

**Current Status**: Frontend integration complete. Backend endpoint needed for full functionality.

**Next Step**: Implement `/api/chat/portal/write` endpoint in backend (Python/FastAPI).
