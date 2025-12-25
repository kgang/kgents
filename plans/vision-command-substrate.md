# THE COMMAND SUBSTRATE: A Vision for Keyboard-First Navigation

> *"The noun is a lie. There is only the rate of change."*
> *"Cmd+K is not a shortcut. It's a philosophy."*

**Status**: Vision Document
**Created**: 2025-12-24
**Voice Anchor**: "Power through keystrokes, not IDE heaviness"

---

## The Core Insight

Every feature in a system is a door. Traditional UIs put doors in fixed locations—menus, toolbars, sidebars. Users must travel to the door, then through it. This is spatial overhead.

**Our answer: The Command Substrate.**

One keystroke summons all doors. Cmd+K opens a portal to *everywhere*. Type what you want, not where it lives. The system becomes a language, not a landscape.

Linear, Arc, Raycast, Figma—they all converge on this truth. We take it further: the command substrate isn't just navigation. It's AGENTESE made tactile.

---

## Theoretical Foundations

### I. Fitt's Law Inversion

Fitt's Law: Time to target = f(distance / size). Bigger, closer targets are faster.

Traditional implication: Make buttons big. Put them near the cursor.

**Our inversion**: Make the *command palette* infinitely large (fullscreen) and infinitely close (one keystroke). All commands are equidistant from the user.

```
TRADITIONAL:                    COMMAND SUBSTRATE:

  [Menu] [Edit] [View]           [Cmd+K] → Everything
     ↓      ↓      ↓
   Sub    Sub    Sub                ↓
    ↓      ↓      ↓           "ty" → Go to theory
  Item   Item   Item           "wi" → Add witness mark
                               "zo" → Zoom out
Depth: 3 clicks             Depth: 2 keystrokes
Time: 2-5 seconds           Time: 200-500ms
```

### II. Recognition vs. Recall

Menus favor recognition: "I see the option, I click it."
Command palettes favor recall: "I type what I want."

**Research shows**: Expert users are 5x faster with recall-based interfaces. The learning curve is steeper, but the ceiling is higher.

We optimize for experts because *Kent is an expert*. The interface should match his cognitive speed.

### III. AGENTESE as Grammar

Traditional command palettes have flat namespaces:
- "Open file"
- "Save file"
- "Go to definition"

AGENTESE has structure:
- `world.house.manifest`
- `self.memory.recall`
- `concept.derivation.edges`

The grammar IS the interface. Every command is a path. Every path is composable. The user learns patterns, not lists.

```
world.*      → External (files, entities, tools)
self.*       → Internal (memory, state, capability)
concept.*    → Abstract (specs, derivations, proofs)
void.*       → Serendipity (entropy, gratitude)
time.*       → Temporal (history, forecasts)
```

---

## User Journeys

### Journey 1: The Lightning Navigation

**Context**: Kent needs to jump between files constantly during a refactor.

```
09:15 — Refactoring witness flow
────────────────────────────────────────────────────────

Kent is in services/witness/store.py.

Cmd+K → "mark"
  → services/witness/mark.py (most recent)
  → spec/protocols/witness.md#MarkStore
  → concept.witness.mark.define

Kent hits Enter. He's in mark.py.

5 seconds later:
Cmd+K → "spec wit"
  → spec/protocols/witness.md

He's in the spec. Makes a note.

3 seconds later:
Cmd+K → "test mark"
  → services/witness/_tests/test_mark.py

He's in the tests.

Total time for 3 file jumps: 15 seconds.
Traditional file browser: 45+ seconds.
```

**Key experience qualities:**
- **Fuzzy matching**: "mark" finds mark.py, not requiring full path
- **Recency weighting**: Recently accessed files rank higher
- **Context awareness**: Being in witness/ boosts witness-related results

---

### Journey 2: The AGENTESE Invocation

**Context**: Kent wants to see the derivation edges for the current concept.

```
14:00 — Exploring the derivation DAG
────────────────────────────────────────────────────────

Kent is viewing WITNESS in the hypergraph.

Cmd+K → "concept.derivation.edges"

The palette recognizes this as an AGENTESE path.
It shows:

  ⚡ concept.derivation.edges
     Invoke AGENTESE path (current node: WITNESS)

  📄 Related files:
     → protocols/specgraph/derivation.py
     → services/witness/derivation.py

Kent hits Enter. The edge panel slides in, showing:

  WITNESS → DERIVATION (confidence: 0.92, 8 marks)
  WITNESS → MARKSTORE (confidence: 0.99, 45 marks)
  WITNESS → VALIDATION (confidence: 0.76, 3 marks)

The command palette didn't just navigate. It *invoked*.
```

**Key experience qualities:**
- **Path detection**: System recognizes AGENTESE syntax
- **Invocation option**: Paths can be run, not just navigated
- **Related files**: Shows implementation files for the path

---

### Journey 3: The Action Cascade

**Context**: Kent wants to add a witness mark, commit, and push.

```
16:45 — End of day wrap-up
────────────────────────────────────────────────────────

Cmd+K → "km completed phase 1"

The palette recognizes this as a witness command:

  ⚡ km "completed phase 1"
     Create witness mark

  💡 Suggested follow-ups:
     → kg witness crystallize (end-of-day summary)
     → git commit (stage your changes)

Kent hits Enter. Mark created.

Cmd+K → "commit session work"

  ⚡ git commit
     Template: "Session: {summary from marks}"

  📝 Suggested message (from today's marks):
     "Phase 1 categorical probes complete

      - Added MonadProbe + SheafDetector
      - 41 tests passing
      - AGENTESE paths registered"

Kent reviews. Hits Enter. Committed.

Cmd+K → "push"

  ⚡ git push origin main

Done. Three actions, all from Cmd+K, in 20 seconds.
```

**Key experience qualities:**
- **Command detection**: "km", "git commit", "push" all recognized
- **Follow-up suggestions**: After one action, related actions surface
- **Template intelligence**: Commit message generated from marks

---

## The Fuzzy Matching Engine

### Implementation: microfuzz

```typescript
import { createFuzzySearch } from 'microfuzz';

const commands = [
  { id: 'world.witness.mark', label: 'Add witness mark', icon: '✦' },
  { id: 'world.house.manifest', label: 'Manifest current node', icon: '🏠' },
  { id: 'concept.derivation.edges', label: 'Show derivation edges', icon: '→' },
  // ... 500+ commands
];

const search = createFuzzySearch(commands, {
  keys: ['id', 'label'],
  threshold: 0.4,  // Loose matching
});

// "wit mark" → [{ id: 'world.witness.mark', ... }]
// "der edg" → [{ id: 'concept.derivation.edges', ... }]
```

**Performance**: microfuzz handles 4,500 items in <1.5ms after warmup. The palette feels instant.

### Ranking Strategy

Commands are ranked by:
1. **Exact prefix match**: "wit" → "witness.*" first
2. **Recency**: Recently invoked commands rank higher
3. **Context**: If in witness/, witness commands rank higher
4. **Frequency**: Often-used commands get a boost
5. **Fuzzy score**: Character-level matching quality

```typescript
const rankCommand = (cmd: Command, query: string, context: Context) => {
  let score = fuzzyScore(cmd.id, query);

  if (cmd.id.startsWith(query)) score *= 2;           // Prefix boost
  if (context.recentCommands.includes(cmd.id)) score *= 1.5;  // Recency
  if (cmd.id.includes(context.currentPath)) score *= 1.3;     // Context

  return score;
};
```

---

## Contextual Commands

The palette adapts to where you are:

```
┌──────────────────────────────────────────────────────────────┐
│  CONTEXT: Editing spec/protocols/witness.md                  │
├──────────────────────────────────────────────────────────────┤
│  Recent:                                                     │
│    → concept.witness.mark.define (3 min ago)                 │
│    → services/witness/store.py (10 min ago)                  │
│                                                              │
│  Suggested for this file:                                    │
│    → kg audit spec/protocols/witness.md --full               │
│    → kg annotate --section "MarkStore"                       │
│    → Go to implementation: services/witness/store.py         │
│                                                              │
│  Graph actions:                                              │
│    → gd (go to derivation)                                   │
│    → ge (go to edges)                                        │
│    → zo (zoom out)                                           │
└──────────────────────────────────────────────────────────────┘
```

---

## The Modal Integration

kgents has six modes. The command palette knows about them:

| Mode | Cmd+K behavior |
|------|----------------|
| NORMAL | Full command access |
| INSERT | File/path navigation only (don't interrupt typing) |
| EDGE | Edge-specific commands (create, delete, confidence) |
| WITNESS | Quick mark creation, tag selection |
| COMMAND | Command palette IS active (redundant) |
| VISUAL | Batch operations on selection |

### Mode-Aware Suggestions

```
MODE: EDGE
────────────────────────────────────────────────────────

Cmd+K shows:

  Edge actions:
  → Create edge to... (type destination)
  → Delete edge (current: WITNESS → DERIVATION)
  → Set confidence (current: 0.92)
  → View evidence (8 marks)

  Navigation:
  → Exit EDGE mode (Esc)
  → Switch to NORMAL mode
```

---

## Open Questions

### 1. The Discovery Problem

Power users love Cmd+K. New users don't know it exists. How do we teach without cluttering?

**Possible answers:**
- **First-run tutorial**: "Press Cmd+K to access everything"
- **Hint on idle**: After 10 seconds of no input, subtle "Cmd+K" hint
- **Fallback menu**: Traditional menu bar that triggers the palette
- **Teaching callouts**: Context-sensitive hints ("You could also Cmd+K → 'mark'")

### 2. The Overwhelm Problem

With 500+ commands, the palette could become a wall of noise. How do we keep it calm?

**Possible answers:**
- **Categorical grouping**: Commands grouped by context (Files, Actions, Navigation)
- **Progressive disclosure**: Show top 5 by default, scroll for more
- **Prefix filtering**: "w." shows only world.* commands
- **Favorites**: Pin frequently used commands to the top

### 3. The Muscle Memory Problem

If rankings change based on recency, experienced users can't develop muscle memory. "wit mar" might not always give the same result.

**Possible answers:**
- **Stable top results**: First 3 results stay stable for any given query
- **Pinned shortcuts**: `wit:m` always means witness mark (user-defined)
- **Decay, not replace**: Recent commands boost, but don't displace stable favorites

### 4. The Mobile Problem

Cmd+K assumes a keyboard. What about touch interfaces?

**Possible answers:**
- **Gesture trigger**: Two-finger swipe down opens palette
- **Floating action button**: Permanent "+ " button in corner
- **Voice activation**: "Hey kgents, add witness mark"

---

## Implementation Phases

### Phase 1: Basic Palette (2 weeks)

**Goal**: Cmd+K opens, fuzzy search works, basic navigation.

```typescript
<CommandPalette
  trigger="Cmd+K"
  commands={allCommands}
  onSelect={(cmd) => execute(cmd)}
  fuzzySearch={microfuzz}
/>
```

**Deliverables:**
- [ ] cmdk integration
- [ ] microfuzz search engine
- [ ] File navigation (all project files)
- [ ] Basic AGENTESE paths

### Phase 2: Contextual Intelligence (3 weeks)

**Goal**: Commands adapt to current context.

**Deliverables:**
- [ ] Mode-aware suggestions
- [ ] Recency tracking
- [ ] Context detection (current file, node, mode)
- [ ] Related file suggestions

### Phase 3: Action Integration (3 weeks)

**Goal**: Commands that DO things, not just navigate.

**Deliverables:**
- [ ] `km` command integration
- [ ] `kg decide` integration
- [ ] `kg audit` / `kg annotate` integration
- [ ] Git command shortcuts

### Phase 4: AGENTESE Invocation (2 weeks)

**Goal**: Full AGENTESE paths are invokable from palette.

**Deliverables:**
- [ ] Path detection (world.*, concept.*, etc.)
- [ ] Invocation vs. navigation distinction
- [ ] Result display inline
- [ ] Chainable invocations

---

## Poignant Examples

### Example 1: The Refactoring Sprint

```
Before the Command Substrate:

  Kent needs to rename "Mark" to "WitnessMark" across 47 files.

  Opens file browser.
  Navigates to services/witness/mark.py.
  Opens find-and-replace.
  Types "Mark", "WitnessMark".
  Replaces.
  Navigates to next file.
  Repeat 46 times.

  Time: 45 minutes.

After:

  Cmd+K → "rename symbol"
  Type: "Mark" → "WitnessMark"
  Scope: "All files in services/witness/"
  [Preview: 47 files, 312 occurrences]
  Enter.

  Time: 30 seconds.
```

### Example 2: The Exploration Session

```
Kent: "I want to understand how derivation works."

  Cmd+K → "concept.derivation"

  Results:
  → concept.derivation.manifest (invoke)
  → concept.derivation.edges (invoke)
  → spec/protocols/derivation.md (file)
  → services/sovereign/derivation.py (file)
  → docs/skills/derivation.md (file)

  Kent invokes concept.derivation.manifest.

  Output appears inline:

  "DERIVATION is a witness-backed edge in the knowledge
   graph. Each derivation carries confidence scores from
   its supporting marks..."

  Kent didn't search. He asked. The system answered.
```

### Example 3: The Teaching Moment

```
New team member: "How do I add a witness mark?"

Kent: "Cmd+K, then type 'km'."

The palette shows:

  ⚡ km "your message"
     Create a witness mark

  📖 Documentation:
     → docs/skills/witness.md#marks
     → HYDRATE.md#witness-marks

  💡 Examples:
     → km "completed feature X"
     → km "insight" --reasoning "why it matters"
     → km "gotcha" --tag gotcha

New team member types "km 'learned the palette'"

Mark created. Learning documented. Joy.
```

---

## Success Metrics

| Metric | Current | Target | Rationale |
|--------|---------|--------|-----------|
| Time to any file | 5+ seconds | <1 second | Speed = flow |
| Commands used via palette | ~20% | >80% | Adoption proof |
| New user time to first mark | 10 minutes | 30 seconds | Onboarding |
| Palette latency | N/A | <50ms | Feels instant |
| Query → result accuracy | N/A | 90% top-3 | Find what you want |

---

## The Vision Statement

In 6 months, Kent's fingers rest on the keyboard.

He doesn't look at menus. He doesn't click toolbars. He types.

Cmd+K → "wi mark session complete"

The system understands. Mark created. Done.

Cmd+K → "zo 10"

The graph zooms out. Clusters visible.

Cmd+K → "concept.categorical.probe.invoke"

The categorical probe runs. Results appear inline.

There is no separation between thinking and doing. The command substrate is the interface. The interface is the language. The language is AGENTESE.

Kent doesn't use kgents. He *speaks* kgents.

---

*"The noun is a lie. There is only the rate of change."*
*"Cmd+K is the rate of change made tactile."*

---

**Filed**: 2025-12-24
**Voice anchor**: "Power through keystrokes, not IDE heaviness"
