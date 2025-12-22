# Membrane Execution Plan — Radical Sprint

> *"Stop documenting agents. Become the agent."*

**Status**: EXECUTING
**Decision**: `fuse-ccad81de`
**Started**: 2025-12-22

---

## Ground Truth

### What We Have (Frontend Foundation)

| System | Components | Ready |
|--------|------------|-------|
| **Elastic** | ElasticContainer, ElasticSplit, ElasticCard, BottomDrawer, FloatingSidebar | ✅ |
| **Joy** | Breathe, Pop, Shake, Shimmer, PersonalityLoading, EmpathyError | ✅ |
| **Genesis** | BreathingContainer, GrowingContainer, UnfurlingPanel | ✅ |
| **Projection** | WidgetRenderer, StreamWidget, TextWidget, all widget types | ✅ |
| **Synergy** | SynergyToaster, useSynergyToast, JEWEL_INFO | ✅ |
| **Hooks** | useDesignPolynomial, useAnimationCoordination, useLayoutContext | ✅ |

### What We Have (Backend)

| Endpoint | Status | Notes |
|----------|--------|-------|
| `self.witness.stream` | ✅ Works | AGENTESE streaming aspect |
| `GET /api/witness/stream` | ✅ Works | SSE for marks |
| `GET /api/witness/marks` | ✅ Works | REST for mark history |
| Crystal streaming | 🔧 95% | Function exists, needs REST endpoint |

---

## Execution Sprint

### PHASE 0: Wire Backend (15 min) ✅ READY

**No blocking backend work.** The streaming infrastructure exists:
- `self.witness.stream` → Thoughts
- `GET /api/witness/stream` → Marks
- Both use SSE with heartbeat

**Optional Enhancement** (can defer):
- Add `GET /api/witness/crystals/stream` endpoint

---

### PHASE 1: Membrane Shell (45 min)

Build the single root component that replaces the entire app.

#### 1.1 Create `useMembrane.ts` — State Machine Hook

```typescript
type MembraneMode = 'compact' | 'comfortable' | 'spacious'
type FocusType = 'welcome' | 'file' | 'spec' | 'concept' | 'dialogue'

interface MembraneState {
  mode: MembraneMode
  focus: { type: FocusType; path?: string; content?: string }
  witnessConnected: boolean
  dialogueHistory: DialogueMessage[]
}

// Transitions:
// - setMode(mode) → change density
// - setFocus(type, path?) → change what's shown
// - appendDialogue(message) → add to history
// - crystallize(content) → emit to witness
```

#### 1.2 Create `Membrane.tsx` — Root Component

```tsx
export function Membrane() {
  const { mode, focus, setMode, setFocus } = useMembrane()
  const { density } = useLayoutContext()

  // Auto-mode based on viewport
  useEffect(() => {
    if (density === 'compact') setMode('compact')
    else if (density === 'spacious') setMode('spacious')
    else setMode('comfortable')
  }, [density])

  return (
    <ElasticContainer layout="stack" className="membrane">
      {mode !== 'compact' && <WitnessStream />}
      <ElasticSplit
        direction="horizontal"
        defaultRatio={0.65}
        collapseAtDensity="compact"
      >
        <FocusPane focus={focus} />
        <DialoguePane onFocusChange={setFocus} />
      </ElasticSplit>
    </ElasticContainer>
  )
}
```

#### 1.3 Wire to App.tsx

Replace all routing with single Membrane:

```tsx
function App() {
  return (
    <ErrorBoundary>
      <LayoutProvider>
        <SynergyToaster />
        <Membrane />
      </LayoutProvider>
    </ErrorBoundary>
  )
}
```

**Files to create**:
- `src/membrane/Membrane.tsx`
- `src/membrane/useMembrane.ts`
- `src/membrane/index.ts`

**Files to modify**:
- `src/App.tsx` — Replace routes with Membrane

---

### PHASE 2: Focus Pane (30 min)

The Focus Pane shows context-appropriate content.

#### 2.1 Create `FocusPane.tsx`

```tsx
interface FocusPaneProps {
  focus: MembraneState['focus']
}

export function FocusPane({ focus }: FocusPaneProps) {
  switch (focus.type) {
    case 'welcome':
      return <WelcomeView />
    case 'file':
      return <FileView path={focus.path!} />
    case 'spec':
      return <SpecView path={focus.path!} />
    case 'concept':
      return <ConceptView concept={focus.path!} />
    case 'dialogue':
      return <DialogueFocusView content={focus.content!} />
  }
}
```

#### 2.2 Create Focus Views

**WelcomeView** — Initial state, recent activity
```tsx
export function WelcomeView() {
  return (
    <BreathingContainer intensity="subtle">
      <div className="welcome">
        <h1>The Membrane</h1>
        <p className="subtitle">Co-thinking surface</p>
        <RecentActivity />  {/* Last few marks/decisions */}
      </div>
    </BreathingContainer>
  )
}
```

**FileView** — Code display with syntax highlighting
```tsx
export function FileView({ path }: { path: string }) {
  const { data, loading, error } = useFileContent(path)
  if (loading) return <PersonalityLoading jewel="brain" />
  if (error) return <EmpathyError type="notfound" />
  return <CodeBlock content={data} language={getLanguage(path)} />
}
```

**SpecView** — Rendered specification
```tsx
export function SpecView({ path }: { path: string }) {
  const { data, loading } = useSpecContent(path)
  if (loading) return <PersonalityLoading jewel="gestalt" />
  return <MarkdownRenderer content={data} />
}
```

**Files to create**:
- `src/membrane/FocusPane.tsx`
- `src/membrane/views/WelcomeView.tsx`
- `src/membrane/views/FileView.tsx`
- `src/membrane/views/SpecView.tsx`
- `src/membrane/views/ConceptView.tsx`
- `src/membrane/views/index.ts`

---

### PHASE 3: Witness Stream (30 min)

Real-time stream of decisions, marks, crystallizations.

#### 3.1 Create `useWitnessStream.ts`

```typescript
export function useWitnessStream() {
  const [events, setEvents] = useState<WitnessEvent[]>([])
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const eventSource = new EventSource('/api/witness/stream')

    eventSource.onopen = () => setConnected(true)
    eventSource.onmessage = (e) => {
      const event = JSON.parse(e.data)
      setEvents(prev => [event, ...prev].slice(0, 50))  // Keep last 50
    }
    eventSource.onerror = () => setConnected(false)

    return () => eventSource.close()
  }, [])

  return { events, connected }
}
```

#### 3.2 Create `WitnessStream.tsx`

```tsx
export function WitnessStream() {
  const { events, connected } = useWitnessStream()

  return (
    <div className="witness-stream">
      <header className="witness-header">
        <Breathe intensity={connected ? 0.3 : 0} speed="slow">
          <span className="witness-title">Witness</span>
        </Breathe>
        <span className={`status ${connected ? 'connected' : 'disconnected'}`} />
      </header>

      <div className="witness-events">
        {events.map(event => (
          <WitnessEvent key={event.id} event={event} />
        ))}
      </div>
    </div>
  )
}
```

#### 3.3 Create `WitnessEvent.tsx`

```tsx
export function WitnessEvent({ event }: { event: WitnessEventData }) {
  return (
    <GrowingContainer>
      <div className="witness-event">
        <span className="event-type">{event.type}</span>
        <span className="event-content">{event.content || event.action}</span>
        <span className="event-time">{formatRelative(event.timestamp)}</span>
      </div>
    </GrowingContainer>
  )
}
```

**Files to create**:
- `src/membrane/WitnessStream.tsx`
- `src/membrane/WitnessEvent.tsx`
- `src/membrane/useWitnessStream.ts`

---

### PHASE 4: Dialogue Pane (45 min)

The co-thinking interface where Kent and K-gent interact.

#### 4.1 Create `DialoguePane.tsx`

```tsx
interface DialoguePaneProps {
  onFocusChange: (type: FocusType, path?: string) => void
}

export function DialoguePane({ onFocusChange }: DialoguePaneProps) {
  const { dialogueHistory, appendDialogue } = useMembrane()
  const [input, setInput] = useState('')

  const handleSubmit = async () => {
    if (!input.trim()) return

    // Add user message
    appendDialogue({ role: 'user', content: input })
    setInput('')

    // TODO: Send to backend, get response
    // For now, echo back
    appendDialogue({ role: 'assistant', content: `Thinking about: ${input}` })
  }

  return (
    <div className="dialogue-pane">
      <div className="dialogue-history">
        {dialogueHistory.map((msg, i) => (
          <DialogueMessage key={i} message={msg} onFocusRequest={onFocusChange} />
        ))}
      </div>

      <div className="dialogue-input">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="What are you thinking about?"
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSubmit()}
        />
        <button onClick={handleSubmit}>Send</button>
        <button className="crystallize" onClick={() => {}}>
          Crystallize ⬡
        </button>
      </div>
    </div>
  )
}
```

#### 4.2 Create `DialogueMessage.tsx`

```tsx
interface DialogueMessageProps {
  message: { role: 'user' | 'assistant'; content: string }
  onFocusRequest: (type: FocusType, path?: string) => void
}

export function DialogueMessage({ message, onFocusRequest }: DialogueMessageProps) {
  // Parse content for focus requests (e.g., file paths, spec references)
  const parsed = parseContent(message.content)

  return (
    <div className={`dialogue-message ${message.role}`}>
      <div className="message-content">
        {parsed.segments.map((seg, i) =>
          seg.type === 'text' ? (
            <span key={i}>{seg.content}</span>
          ) : (
            <button
              key={i}
              className="focus-link"
              onClick={() => onFocusRequest(seg.focusType, seg.path)}
            >
              {seg.label}
            </button>
          )
        )}
      </div>
    </div>
  )
}
```

**Files to create**:
- `src/membrane/DialoguePane.tsx`
- `src/membrane/DialogueMessage.tsx`

---

### PHASE 5: Crystallization (20 min)

Wire the Crystallize button to the witness system.

#### 5.1 Add `crystallize` to `useMembrane.ts`

```typescript
const crystallize = async (content: string) => {
  // Create a mark via REST API
  await fetch('/api/witness/marks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'crystallize',
      reasoning: content,
      author: 'membrane'
    })
  })

  // The WitnessStream will pick it up via SSE
}
```

#### 5.2 Wire Crystallize Button

```tsx
<button
  className="crystallize"
  onClick={() => {
    const lastMessage = dialogueHistory[dialogueHistory.length - 1]
    if (lastMessage) crystallize(lastMessage.content)
  }}
>
  Crystallize ⬡
</button>
```

---

### PHASE 6: Polish & Joy (30 min)

#### 6.1 Add Keyboard Shortcuts

```typescript
useKeyboardShortcuts({
  'mod+1': () => setMode('compact'),
  'mod+2': () => setMode('comfortable'),
  'mod+3': () => setMode('spacious'),
  'mod+k': () => focusDialogueInput(),
  'escape': () => setFocus({ type: 'welcome' }),
})
```

#### 6.2 Add Joy Animations

- Witness events use `GrowingContainer` for entry
- Mode transitions use `UnfurlPanel` for pane reveal
- Focus changes use `Pop` for emphasis
- Connection status uses `Breathe` for vitality

#### 6.3 Add Styles

Create `src/membrane/membrane.css`:
- Membrane layout (grid/flex)
- Mode-specific styles (compact/comfortable/spacious)
- Witness stream styling
- Dialogue pane styling
- Joy animation integration

---

## File Inventory

### Create (15 files)

```
src/membrane/
├── index.ts
├── Membrane.tsx
├── useMembrane.ts
├── FocusPane.tsx
├── WitnessStream.tsx
├── WitnessEvent.tsx
├── useWitnessStream.ts
├── DialoguePane.tsx
├── DialogueMessage.tsx
├── membrane.css
└── views/
    ├── index.ts
    ├── WelcomeView.tsx
    ├── FileView.tsx
    ├── SpecView.tsx
    └── ConceptView.tsx
```

### Modify (2 files)

```
src/App.tsx          — Replace routes with Membrane
src/hooks/index.ts   — Export any new hooks
```

### Delete (optional, can defer)

```
src/pages/           — All old page files (already burned, just cleanup)
```

---

## Time Estimate

| Phase | Time | Cumulative |
|-------|------|------------|
| Phase 0: Backend Wire | 0 min (ready) | 0 min |
| Phase 1: Membrane Shell | 45 min | 45 min |
| Phase 2: Focus Pane | 30 min | 75 min |
| Phase 3: Witness Stream | 30 min | 105 min |
| Phase 4: Dialogue Pane | 45 min | 150 min |
| Phase 5: Crystallization | 20 min | 170 min |
| Phase 6: Polish & Joy | 30 min | 200 min |

**Total: ~3.5 hours for full Membrane MVP**

---

## Success Criteria

- [ ] Single `<Membrane />` renders entire app
- [ ] No react-router navigation
- [ ] Witness stream shows real-time events
- [ ] Dialogue input accepts text
- [ ] Crystallize button creates marks
- [ ] Three modes work (compact/comfortable/spacious)
- [ ] Joy animations on state transitions
- [ ] Keyboard shortcuts functional

---

## Radical Adjustments

### Principle: No Half Measures

1. **Kill all routes NOW** — Don't keep old pages "just in case"
2. **Dialogue IS navigation** — Type a path, it focuses. No menus.
3. **Witness IS memory** — Everything flows through witness stream
4. **Focus IS understanding** — K-gent shows its comprehension in Focus pane

### Principle: Composability First

The Membrane is itself a polynomial agent:
```
Membrane: Mode × Focus × Witness → Surface
```

Each pane is a morphism that can be composed:
```
FocusPane >> WitnessStream >> DialoguePane
```

### Principle: Joy Over Function

Every state change should feel alive:
- Mode changes: breathing transitions
- Focus changes: unfurling reveals
- New events: growing entry
- Errors: empathetic shake

---

*"The persona is a garden, not a museum."*
*"The proof IS the decision."*

Filed: 2025-12-22
