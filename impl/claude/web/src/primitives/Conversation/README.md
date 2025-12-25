# Conversation Primitive

> "Chat is not a feature. Chat is an affordance that collapses discrete into continuous."

The unified chat system primitive. Consolidates the fragmented ChatPanel architecture into a clean, coherent interface.

## Architecture

```
Conversation (orchestrator)
├── BranchTree (optional session tree)
├── MessageList (turn display + streaming)
├── SafetyGate mode="post" (post-execution acknowledgment)
├── SafetyGate mode="pre" (pre-execution approval)
└── InputArea (message input + controls)
```

## Key Consolidations

### 1. SafetyGate Component
Merges **MutationAcknowledger** + **PreExecutionGate** into one component with two modes:

- **`mode="pre"`**: Approval gate BEFORE tool execution
  - Timeout = DENY (safe default)
  - Actions: Allow Once / Always Allow / Deny
  - Constitutional: DESTRUCTIVE operations require approval

- **`mode="post"`**: Acknowledgment AFTER tool execution
  - Timeout = ACCEPT (user has been informed)
  - Actions: Got it (acknowledge)
  - Constitutional: MUTATION operations require acknowledgment

### 2. Removed Redundancy
Deleted components that added complexity without value:
- **ToolPanel** → Functionality moved to message metadata
- **TransparencySelector** → Replaced by safetyMode prop
- **ConfidenceBar** → Integrated into message display
- **CrystallizationTrigger** → Handled by hooks

## Usage

```tsx
import { Conversation } from '@/primitives/Conversation';

function ChatPage() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [safetyMode, setSafetyMode] = useState<SafetyMode>('acknowledge');
  const [pendingMutations, setPendingMutations] = useState<PendingMutation[]>([]);

  return (
    <Conversation
      turns={turns}
      onMessage={handleSendMessage}
      onRewind={handleRewind}
      safetyMode={safetyMode}
      isStreaming={isStreaming}
      pendingMutations={pendingMutations}
      onAcknowledgeMutation={handleAcknowledge}
    />
  );
}
```

## Props Interface

```typescript
interface ConversationProps {
  // Core data
  turns: Turn[];
  
  // Handlers
  onMessage: (content: string) => void;
  onBranch?: (turnId: string) => void;
  onCrystallize?: (selection: string[]) => void;
  onRewind?: (turnId: string) => void;
  
  // Safety system
  safetyMode: 'gate' | 'acknowledge' | 'trust';
  pendingMutations?: PendingMutation[];
  pendingApprovals?: PendingApproval[];
  onAcknowledgeMutation?: (id: string, mode: 'click' | 'keyboard' | 'timeout_accept') => void;
  onApproveExecution?: (requestId: string, alwaysAllow: boolean) => void;
  onDenyExecution?: (requestId: string, reason?: string) => void;
  
  // State
  isStreaming?: boolean;
  error?: string | null;
  
  // UI
  compact?: boolean;
  className?: string;
}
```

## Safety Modes

### `safetyMode="gate"`
Pre-execution approval for destructive operations.
- User sees tool request BEFORE execution
- Timeout auto-denies (safe default)
- Three choices: Allow Once / Always Allow / Deny

### `safetyMode="acknowledge"`
Post-execution acknowledgment for mutations.
- User sees mutation AFTER execution
- Timeout auto-accepts (user has been informed)
- One action: Got it (acknowledge)

### `safetyMode="trust"`
Minimal safety UI, tools run freely.
- No gates or acknowledgments
- Only use when user explicitly trusts the system

## File Structure

```
primitives/Conversation/
├── Conversation.tsx      # Main orchestrator (~300 LOC)
├── Conversation.css      # Brutalist layout styles
├── SafetyGate.tsx        # Unified safety component (~250 LOC)
├── SafetyGate.css        # Safety gate styles
├── InputArea.tsx         # Message input (copied from chat/)
├── InputArea.css
├── BranchTree.tsx        # Session tree viz (copied from chat/)
├── BranchTree.css
├── useBranching.ts       # Branch operations hook
├── useCrystallization.ts # Session crystallization hook
├── types.ts              # TypeScript types
├── index.ts              # Exports
└── README.md             # This file
```

## Design Principles

1. **Tasteful** — Each component serves a clear purpose
2. **Composable** — SafetyGate works in both pre/post modes
3. **Brutalist** — Clean, functional layout with no decoration
4. **Responsive** — Follows elastic-ui-patterns for mobile
5. **Keyboard-first** — Enter/Escape/Space shortcuts everywhere

## Migration from ChatPanel

```tsx
// Before (ChatPanel)
<ChatPanel
  sessionId={sessionId}
  projectId={projectId}
  compact={false}
  showBranching={true}
/>

// After (Conversation)
<Conversation
  turns={session.turns}
  onMessage={sendMessage}
  onBranch={createFork}
  safetyMode="acknowledge"
  isStreaming={isStreaming}
  pendingMutations={mutations}
  onAcknowledgeMutation={acknowledgeMutation}
/>
```

## Philosophy

The previous ChatPanel architecture was fragmented across 15+ components with overlapping responsibilities. This primitive consolidates everything into a clean interface with three core ideas:

1. **Conversation is the primitive** — Not "chat", not "panel", but the fundamental interaction
2. **Safety is unified** — One component handles both pre/post execution safety
3. **State is external** — Component doesn't manage its own state, just renders and emits events

The result: ~50% fewer components, ~40% less code, 100% clearer architecture.

---

*Compiled: 2025-12-24 | Refactor: Chat → Conversation*
