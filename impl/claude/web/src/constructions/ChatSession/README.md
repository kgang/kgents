# ChatSession Construction

**The composed chat experience: Conversation + Witness + ValueCompass**

## Overview

ChatSession is the primary construction for kgents chat interfaces. It combines three primitives into a coherent experience:

1. **Conversation** - Message display, input, branching, safety gates
2. **Witness** - Evidence corpus with causal influence graphs
3. **ValueCompass** - Constitutional principle scores as radar chart

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Conversation (main)                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Messages                                           │  │
│  │ ...                                                │  │
│  ├───────────────────────────────────────────────────┤  │
│  │ InputArea                                          │  │
│  └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ [Witness] [ValueCompass] (collapsible theory panels)    │
└─────────────────────────────────────────────────────────┘
```

## Usage

### Basic Setup

```tsx
import { ChatSession } from '@/constructions/ChatSession';
import type { Turn, SafetyMode } from '@/primitives/Conversation/types';

function ChatPage() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [safetyMode, setSafetyMode] = useState<SafetyMode>('acknowledge');

  const handleMessage = async (content: string) => {
    // Send message to backend
    await chatApi.sendMessage(sessionId, content);
  };

  return (
    <ChatSession
      sessionId="session-123"
      turns={turns}
      onMessage={handleMessage}
      safetyMode={safetyMode}
    />
  );
}
```

### With Theory Panels

```tsx
import type { EvidenceCorpus, ConstitutionScores } from '@/types/theory';

function ChatPageWithTheory() {
  const [evidence, setEvidence] = useState<EvidenceCorpus | undefined>();
  const [scores, setScores] = useState<ConstitutionScores | undefined>();

  return (
    <ChatSession
      sessionId="session-123"
      turns={turns}
      onMessage={handleMessage}
      safetyMode="acknowledge"
      showTheory={true}
      currentEvidence={evidence}
      constitutionScores={scores}
    />
  );
}
```

### With Branching

```tsx
function ChatPageWithBranching() {
  const handleBranch = async (turnId: string) => {
    await chatApi.createBranch(sessionId, turnId);
  };

  const handleRewind = async (turnId: string) => {
    await chatApi.rewindToTurn(sessionId, turnId);
  };

  return (
    <ChatSession
      sessionId="session-123"
      turns={turns}
      onMessage={handleMessage}
      onBranch={handleBranch}
      onRewind={handleRewind}
      safetyMode="acknowledge"
    />
  );
}
```

### Safety Modes

```tsx
// Pre-execution gating (user approves before tools run)
<ChatSession
  safetyMode="gate"
  pendingApprovals={approvals}
  onApproveExecution={(requestId, alwaysAllow) => {
    chatApi.approveExecution(requestId, alwaysAllow);
  }}
  onDenyExecution={(requestId, reason) => {
    chatApi.denyExecution(requestId, reason);
  }}
  {...otherProps}
/>

// Post-execution acknowledgment (user sees what tools did)
<ChatSession
  safetyMode="acknowledge"
  pendingMutations={mutations}
  onAcknowledgeMutation={(id, mode) => {
    chatApi.acknowledgeMutation(id, mode);
  }}
  {...otherProps}
/>

// Trust mode (tools run freely, minimal UI)
<ChatSession
  safetyMode="trust"
  {...otherProps}
/>
```

### Compact Mode

```tsx
// Embedded chat widget
<ChatSession
  sessionId="widget-123"
  turns={turns}
  onMessage={handleMessage}
  safetyMode="trust"
  compact={true}
  className="chat-widget"
/>
```

## Props

| Prop | Type | Description |
|------|------|-------------|
| `sessionId` | `string` | Unique session identifier |
| `turns` | `Turn[]` | Chat turns to display |
| `onMessage` | `(content: string) => void` | Send message handler |
| `onBranch?` | `(turnId: string) => void` | Branch/fork handler |
| `onCrystallize?` | `(selection: string[]) => void` | Crystallize session handler |
| `onRewind?` | `(turnId: string) => void` | Rewind to turn handler |
| `safetyMode` | `'gate' \| 'acknowledge' \| 'trust'` | Safety mode for tool execution |
| `isStreaming?` | `boolean` | Streaming state |
| `error?` | `string \| null` | Error message if any |
| `pendingMutations?` | `PendingMutation[]` | Post-execution mutations |
| `pendingApprovals?` | `PendingApproval[]` | Pre-execution approvals |
| `onAcknowledgeMutation?` | Function | Acknowledge mutation callback |
| `onApproveExecution?` | Function | Approve execution callback |
| `onDenyExecution?` | Function | Deny execution callback |
| `showTheory?` | `boolean` | Show theory panels by default |
| `currentEvidence?` | `EvidenceCorpus` | Evidence for current turn |
| `constitutionScores?` | `ConstitutionScores` | Constitution scores for session |
| `compact?` | `boolean` | Compact mode for embedded use |
| `className?` | `string` | Custom class name |

## Theory Panels

Theory panels appear at the bottom of the session and are collapsible. They show when:

1. `showTheory={true}` is set, OR
2. `currentEvidence` is provided, OR
3. `constitutionScores` is provided

### Witness Panel

Shows evidence corpus with:
- Confidence tiers (confident/uncertain/speculative)
- Individual evidence items with P-values
- Causal influence graph (optional)

### ValueCompass Panel

Shows constitutional principle scores as a radar chart:
- Tasteful, Curated, Ethical, Joy-Inducing, Composable, Heterarchical, Generative
- Historical trajectory (optional)
- Personality attractor basin (optional)

## Composition Pattern

ChatSession follows the **Construction** pattern:

- **Primitives** = Single-purpose components (Conversation, Witness, ValueCompass)
- **Construction** = Composed experience with layout + state coordination

This allows:
1. Primitives to be reused independently
2. Construction to handle integration concerns
3. Pages to consume a single coherent interface

## Responsive Behavior

### Desktop (>1200px)
- Theory panels side-by-side (Witness | ValueCompass)
- Expanded conversation area
- Full metadata display

### Tablet (768-1199px)
- Theory panels side-by-side (condensed)
- Standard conversation area
- Partial metadata

### Mobile (<768px)
- Theory panels stacked vertically
- Compact conversation area
- Minimal metadata

## State Management

ChatSession is **stateless** - all state is passed via props. This allows:

1. Parent components to manage session state
2. Easy integration with React Query, Zustand, etc.
3. Testing with controlled props

Example with Zustand:

```tsx
import { useChatStore } from '@/stores/chatStore';

function ChatPage() {
  const {
    turns,
    sendMessage,
    safetyMode,
    evidence,
    scores,
  } = useChatStore();

  return (
    <ChatSession
      sessionId="session-123"
      turns={turns}
      onMessage={sendMessage}
      safetyMode={safetyMode}
      currentEvidence={evidence}
      constitutionScores={scores}
    />
  );
}
```

## Styling

ChatSession uses the **STARK biome** design system:

- Steel gray backgrounds (--steel-800, --steel-850)
- Accent colors for borders (--accent-blue, --accent-purple)
- Brutalist foundations (sharp edges, minimal decoration)
- Smooth transitions for interactive states

### CSS Variables

```css
--steel-800: #2a2d32;
--steel-850: #23262a;
--steel-700: #3a3d42;
--accent-blue: #5b9dd9;
--accent-purple: #9b7dd9;
```

### Custom Styling

```tsx
<ChatSession
  className="custom-chat"
  {...props}
/>
```

```css
.custom-chat {
  --steel-800: #yourcolor;
  border-radius: 8px;
}
```

## Performance

### Optimizations

1. **Lazy theory panels** - Only render when expanded
2. **Memoized evidence** - Witness uses React.memo
3. **Memoized compass** - ValueCompass uses React.memo + useMemo for paths
4. **Conversation delegation** - All message rendering handled by Conversation primitive

### Bundle Size

- ChatSession: ~8 KB
- Conversation primitive: ~12 KB
- Witness primitive: ~4 KB
- ValueCompass primitive: ~6 KB
- **Total: ~30 KB** (gzipped: ~8 KB)

## Testing

```tsx
import { render, screen } from '@testing-library/react';
import { ChatSession } from '@/constructions/ChatSession';

describe('ChatSession', () => {
  it('renders conversation with turns', () => {
    const turns = [
      {
        turn_number: 1,
        user_message: { content: 'Hello', ... },
        assistant_response: { content: 'Hi!', ... },
        ...
      }
    ];

    render(
      <ChatSession
        sessionId="test"
        turns={turns}
        onMessage={jest.fn()}
        safetyMode="trust"
      />
    );

    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi!')).toBeInTheDocument();
  });

  it('shows theory panels when evidence provided', () => {
    const evidence = {
      tier: 'confident',
      items: [{ id: '1', content: 'Test', confidence: 0.9, source: 'test' }],
      causalGraph: [],
    };

    render(
      <ChatSession
        sessionId="test"
        turns={[]}
        onMessage={jest.fn()}
        safetyMode="trust"
        currentEvidence={evidence}
      />
    );

    expect(screen.getByText('Evidence Corpus')).toBeInTheDocument();
  });
});
```

## Related

- **Primitives**: `/src/primitives/Conversation`, `/src/primitives/Witness`, `/src/primitives/ValueCompass`
- **Types**: `/src/types/theory.ts`, `/src/primitives/Conversation/types.ts`
- **Spec**: `spec/protocols/chat-web.md`
- **Backend**: `impl/claude/protocols/api/chat.py`

---

**Philosophy**: "The chat is the canvas. Evidence is the witness. Values are the compass."
