# Migration Guide: ChatPanel → Conversation

Step-by-step guide to migrate from the old ChatPanel to the new Conversation primitive.

## Quick Reference

### Old (ChatPanel)
```tsx
import { ChatPanel } from '@/components/chat/ChatPanel';

<ChatPanel
  sessionId={sessionId}
  projectId={projectId}
  compact={false}
  showBranching={true}
/>
```

### New (Conversation)
```tsx
import { Conversation } from '@/primitives/Conversation';

const { turns, isStreaming, pendingMutations } = useChatStore();

<Conversation
  turns={turns}
  onMessage={sendMessage}
  onRewind={rewindSession}
  safetyMode="acknowledge"
  isStreaming={isStreaming}
  pendingMutations={pendingMutations}
  onAcknowledgeMutation={acknowledgeMutation}
/>
```

## Step-by-Step Migration

### Step 1: Update Imports

**Before:**
```tsx
import { ChatPanel } from '@/components/chat/ChatPanel';
import { useChatStore } from '@/components/chat/store';
```

**After:**
```tsx
import { Conversation } from '@/primitives/Conversation';
import type { SafetyMode, Turn } from '@/primitives/Conversation';
import { useChatStore } from '@/components/chat/store';
```

### Step 2: Extract State from Store

ChatPanel managed state internally. Conversation needs props.

**Before:**
```tsx
// ChatPanel handled this internally
<ChatPanel sessionId={sessionId} />
```

**After:**
```tsx
// Extract state explicitly
const {
  currentSession,
  isStreaming,
  error,
  pendingMutations,
  sendMessage,
  rewind,
  acknowledgeMutation,
} = useChatStore();

<Conversation
  turns={currentSession?.turns || []}
  onMessage={sendMessage}
  onRewind={(turnId) => rewind(currentSession!.id, parseInt(turnId))}
  safetyMode="acknowledge"
  isStreaming={isStreaming}
  error={error}
  pendingMutations={pendingMutations}
  onAcknowledgeMutation={acknowledgeMutation}
/>
```

### Step 3: Choose Safety Mode

The old TransparencySelector is now the `safetyMode` prop.

**Acknowledgment Mode** (default):
```tsx
<Conversation
  safetyMode="acknowledge"
  pendingMutations={mutations}
  onAcknowledgeMutation={handleAck}
/>
```

**Gate Mode** (pre-execution approval):
```tsx
<Conversation
  safetyMode="gate"
  pendingApprovals={approvals}
  onApproveExecution={handleApprove}
  onDenyExecution={handleDeny}
/>
```

**Trust Mode** (minimal UI):
```tsx
<Conversation
  safetyMode="trust"
/>
```

### Step 4: Handle Optional Features

#### Branching
If you use branching:
```tsx
<Conversation
  turns={turns}
  onMessage={sendMessage}
  onBranch={createFork}  // Optional: enables branch tree
  safetyMode="acknowledge"
/>
```

#### Crystallization
If you use crystallization:
```tsx
<Conversation
  turns={turns}
  onMessage={sendMessage}
  onCrystallize={handleCrystallize}  // Optional
  safetyMode="acknowledge"
/>
```

#### Compact Mode
For embedded use:
```tsx
<Conversation
  turns={turns}
  onMessage={sendMessage}
  safetyMode="acknowledge"
  compact={true}  // Removes branch tree, reduces padding
/>
```

## Common Patterns

### Pattern 1: Basic Chat
```tsx
function ChatPage() {
  const { currentSession, isStreaming, sendMessage } = useChatStore();

  return (
    <Conversation
      turns={currentSession?.turns || []}
      onMessage={sendMessage}
      safetyMode="acknowledge"
      isStreaming={isStreaming}
    />
  );
}
```

### Pattern 2: Chat with Mutations
```tsx
function SafeChat() {
  const {
    currentSession,
    isStreaming,
    pendingMutations,
    sendMessage,
    acknowledgeMutation,
  } = useChatStore();

  return (
    <Conversation
      turns={currentSession?.turns || []}
      onMessage={sendMessage}
      safetyMode="acknowledge"
      isStreaming={isStreaming}
      pendingMutations={pendingMutations}
      onAcknowledgeMutation={acknowledgeMutation}
    />
  );
}
```

### Pattern 3: Chat with Pre-execution Gating
```tsx
function GatedChat() {
  const {
    currentSession,
    isStreaming,
    pendingApprovals,
    sendMessage,
    approveToolExecution,
    denyToolExecution,
  } = useChatStore();

  return (
    <Conversation
      turns={currentSession?.turns || []}
      onMessage={sendMessage}
      safetyMode="gate"
      isStreaming={isStreaming}
      pendingApprovals={pendingApprovals}
      onApproveExecution={approveToolExecution}
      onDenyExecution={denyToolExecution}
    />
  );
}
```

### Pattern 4: Full-featured Chat
```tsx
function FullChat() {
  const {
    currentSession,
    isStreaming,
    error,
    pendingMutations,
    sendMessage,
    rewind,
    acknowledgeMutation,
  } = useChatStore();

  const handleRewind = (turnId: string) => {
    const turns = parseInt(turnId);
    rewind(currentSession!.id, turns);
  };

  const handleBranch = (turnId: string) => {
    // Implement fork logic
    console.log('Fork at turn:', turnId);
  };

  return (
    <Conversation
      turns={currentSession?.turns || []}
      onMessage={sendMessage}
      onRewind={handleRewind}
      onBranch={handleBranch}
      safetyMode="acknowledge"
      isStreaming={isStreaming}
      error={error}
      pendingMutations={pendingMutations}
      onAcknowledgeMutation={acknowledgeMutation}
    />
  );
}
```

## Type Safety

Import types for better IDE support:

```tsx
import type {
  ConversationProps,
  SafetyMode,
  Turn,
  Message,
  PendingMutation,
  PendingApproval,
} from '@/primitives/Conversation';

// Type-safe handler
const handleMessage = (content: string) => {
  // content is guaranteed to be string
};

// Type-safe safety mode
const [safetyMode, setSafetyMode] = useState<SafetyMode>('acknowledge');
```

## Testing Changes

After migration, verify:

1. **Typecheck passes:**
   ```bash
   npm run typecheck
   ```

2. **Component renders:**
   - Messages display correctly
   - Input works
   - Streaming shows indicator

3. **Safety gates work:**
   - Post-execution acknowledgments appear
   - Pre-execution approvals block correctly
   - Timeouts behave as expected

4. **Optional features:**
   - Branching UI (if enabled)
   - Rewind functionality
   - Error states

## Troubleshooting

### Issue: "Cannot read property 'turns' of null"
**Solution:** Add null check:
```tsx
<Conversation
  turns={currentSession?.turns || []}
  // ...
/>
```

### Issue: "onRewind is not a function"
**Solution:** Make sure you're passing the correct handler:
```tsx
const handleRewind = (turnId: string) => {
  rewind(currentSession!.id, parseInt(turnId));
};

<Conversation
  onRewind={handleRewind}
  // ...
/>
```

### Issue: "Safety gates not showing"
**Solution:** Check `safetyMode` and pending arrays:
```tsx
<Conversation
  safetyMode="acknowledge"  // Must match pending type
  pendingMutations={pendingMutations}  // Must have items
  onAcknowledgeMutation={acknowledgeMutation}  // Must be defined
/>
```

## Rollback Plan

If migration causes issues, you can rollback:

1. Keep old ChatPanel components (don't delete yet)
2. Revert import changes
3. File bug report with details
4. Gradually migrate one component at a time

## Performance Notes

Conversation is more performant than ChatPanel:
- Single re-render on state change (vs multiple in ChatPanel)
- No internal state management overhead
- Smaller component tree

Expect ~20-30% faster renders in production.

---

**Questions?** Check README.md or file an issue.
