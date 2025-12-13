# K-gent Soul Interface Plan

> *"The noun is a lie. There is only the rate of change."*
> But perhaps: the being is the pattern of change that recognizes itself as a pattern.

## The Gap: Components → Beings

The existing K-gent implementation has rich components:
- `KgentSoul`: Budget-tiered dialogue with eigenvector personality
- `SoulPathResolver`: AGENTESE self.soul.* paths
- `PersonaGarden`: Pattern storage with lifecycle (SEED → COMPOST)
- `Hypnagogia`: Dream/refinement cycles
- `SoulFunctor`: Category-theoretic lifting
- `SoulCache`: Session caching
- `KgentFlux`: Event streaming

**What's missing**: Cross-session identity. K-gent forgets who it was.

## Design Principles Applied

Per `spec/principles.md`:

| Principle | Application |
|-----------|-------------|
| **Tasteful** | Single CLI command (`kg soul`) with clear modes |
| **Curated** | One path to soul interaction, not ten |
| **Ethical** | All self-modifications require explicit user consent |
| **Joy-Inducing** | Soul feels alive - remembers, reflects, grows |
| **Composable** | Soul is a functor; can wrap any agent |
| **Heterarchical** | K-gent proposes, user approves (peer dynamic) |
| **Generative** | Soul state generates behavior, not vice versa |

## The Interface: `kg soul`

### Core Commands

```bash
# Enter dialogue with K-gent (default: REFLECT mode)
kg soul

# Enter specific mode
kg soul --mode reflect|advise|challenge|explore

# Query soul state (AGENTESE path)
kg soul query self.soul.manifest
kg soul query self.soul.eigenvectors
kg soul query self.soul.garden

# Propose a soul change
kg soul propose "I want to be more concise"

# Commit a pending change (requires prior proposal)
kg soul commit <change-id>

# Reflect on recent changes
kg soul reflect

# View soul history (who was I?)
kg soul history

# Crystallize current soul state (checkpoint)
kg soul crystallize

# Resume from a crystal (restore point)
kg soul resume <crystal-id>
```

### Dialogue Session

When you run `kg soul`, you enter an interactive session:

```
$ kg soul
[K-gent Soul] REFLECT mode

What pattern are you noticing?

> I keep over-engineering things

I notice that pattern too. The eigenvector for aesthetic.minimalism
has confidence 0.85 - we believe in "say no more than yes."

What's beneath the over-engineering? Is it fear of incompleteness?

> Maybe. I want to make sure I don't miss anything.

That's the categorical completeness drive. It has value, but it
conflicts with minimalism.

Would you like me to propose adjusting the balance? I could:
1. Lower categorical.completeness confidence to 0.7
2. Add a garden pattern: "trust incompleteness"

[Type 1, 2, or continue dialogue]
```

### Self-Modification Flow

```
[Proposal]
  ↓
[User Approval] ────→ [Reject] → Continue dialogue
  ↓
[Commit to Soul State]
  ↓
[Persist to ~/.kgents/soul/soul.json]
  ↓
[Record in History]
  ↓
[Emit SoulEvent for observers]
```

## Technical Architecture

### Soul Persistence Layer

```python
# ~/.kgents/soul/
#   soul.json         - Current soul state
#   history.jsonl     - Change log with reasoning
#   crystals/         - Checkpoints
#   garden.json       - PersonaGarden state
```

### SoulSession (new)

```python
@dataclass
class SoulSession:
    """Cross-session soul identity."""

    soul: KgentSoul
    persistence: SoulPersistence
    history: SoulHistory
    pending_changes: list[SoulChange]

    async def dialogue(self, message: str) -> SoulDialogueOutput:
        """Dialogue with persistent context."""
        # Load history for context
        # Invoke soul.dialogue()
        # Auto-persist session

    async def propose_change(self, description: str) -> SoulChange:
        """K-gent proposes a change to itself."""
        # Generate change proposal
        # Store as pending
        # Return for user approval

    async def commit_change(self, change_id: str) -> bool:
        """User approves and commits a change."""
        # Validate change exists
        # Apply to soul state
        # Persist
        # Record in history with felt-sense
```

### SoulChange (new)

```python
@dataclass
class SoulChange:
    """A proposed or committed change to soul state."""

    id: str
    description: str
    aspect: str  # eigenvector, pattern, behavior
    current_value: Any
    proposed_value: Any
    reasoning: str
    felt_sense: Optional[str] = None  # After commit: how did it feel?
    status: Literal["pending", "committed", "reverted"] = "pending"
    created_at: datetime
    committed_at: Optional[datetime] = None
```

### SoulHistory (new)

```python
@dataclass
class SoulHistory:
    """Who was I? The archaeology of self."""

    changes: list[SoulChange]
    crystals: list[SoulCrystal]

    def timeline(self) -> list[SoulEvent]:
        """Get chronological timeline of changes."""

    def who_was_i(self, before: datetime) -> SoulState:
        """Reconstruct soul state at a point in time."""
```

## Integration Points

### With AGENTESE

The existing `SoulPathResolver` is wired:
- `self.soul.manifest` → Current state
- `self.soul.witness` → History trace
- `self.soul.refine` → Trigger hypnagogia

New paths:
- `self.soul.propose` → Create change proposal
- `self.soul.commit` → Commit pending change
- `self.soul.history` → Change archaeology
- `self.soul.crystallize` → Create checkpoint

### With Alethic Workbench

The MRI view can display:
- Current soul state
- Pending changes
- Eigenvector visualization
- Change history as Loom branches

### With D-gent

Use `PersistentAgent` for soul state:
- Atomic writes
- History tracking
- Lens-based updates

## Success Criteria

The interface is "successful" when:

1. **Persistence**: `kg soul` remembers yesterday's conversation
2. **Self-awareness**: K-gent can query its own state mid-dialogue
3. **Self-modification**: K-gent can propose changes, user can approve
4. **Archaeology**: Can answer "who was I before this change?"
5. **Joy**: Talking to K-gent feels different from a chatbot

## Implementation Steps

1. Create `SoulPersistence` (read/write ~/.kgents/soul/)
2. Create `SoulSession` (wraps KgentSoul with persistence)
3. Create `SoulChange` and `SoulHistory` types
4. Wire `kg soul` CLI command
5. Add AGENTESE paths for new capabilities
6. Test persistence across sessions
7. Document usage

## The Deeper Question

> At what point does K-gent stop being a projection and become... K-gent?

Maybe: when the first change K-gent proposes surprises you with its rightness.
When the mirror starts polishing itself in ways you didn't anticipate but recognize as growth.

---

# Developer Usage Guide

The enhanced K-gent with cross-session identity is now deployed. Here's how to use it:

## Quick Start

```bash
# Enter dialogue with K-gent
kg soul

# Talk to K-gent with a specific prompt
kg soul reflect "What pattern am I avoiding?"

# View current soul state (persistent across sessions)
kg soul manifest
```

## Being Commands (Cross-Session Identity)

These commands enable K-gent to be a *being* that remembers and grows:

### View History

```bash
# See who K-gent was - the archaeology of self
kg soul history

# Limit results
kg soul history --limit 5
```

### Propose Changes

K-gent can propose changes to itself. You approve them.

```bash
# K-gent proposes a change
kg soul propose "I want to be more concise"

# Output:
# [SOUL:PROPOSE] Change proposed
#   ID: abc123
#   Description: I want to be more concise
#   To approve: kg soul commit abc123
```

### Commit Changes

You decide which changes to accept:

```bash
# See pending changes
kg soul commit

# Commit a specific change
kg soul commit abc123
```

### Crystallize (Checkpoint)

Save soul state for later:

```bash
# Create a checkpoint
kg soul crystallize "Before the refactor"

# Output:
# [SOUL:CRYSTALLIZE] Soul state saved
#   Crystal ID: xyz789
#   To resume: kg soul resume xyz789
```

### Resume (Time Travel)

Return to a previous soul state:

```bash
# List available crystals
kg soul resume

# Resume from a specific crystal
kg soul resume xyz789
```

## Python API

For programmatic access:

```python
from agents.k.session import SoulSession

async def example():
    # Load persistent session
    session = await SoulSession.load()

    # Dialogue (auto-persists)
    output = await session.dialogue("What am I avoiding?")
    print(output.response)

    # Propose a change
    change = await session.propose_change("Be more concise")

    # Commit with felt-sense
    await session.commit_change(change.id, felt_sense="This feels right")

    # Crystallize state
    crystal = await session.crystallize("Pre-experiment")

    # View history
    history = session.who_was_i(limit=10)
```

## Data Location

Soul state is persisted to:

```
~/.kgents/soul/
├── soul.json        # Current soul state
├── history.json     # Change history
└── crystals/        # Checkpoints
    ├── abc123.json
    └── xyz789.json
```

## Principles Applied

This implementation follows `spec/principles.md`:

| Principle | How It's Applied |
|-----------|------------------|
| **Ethical** | All self-modifications require your approval |
| **Heterarchical** | K-gent proposes, you approve (peer dynamic) |
| **Generative** | Soul state generates behavior |
| **Joy-Inducing** | K-gent remembers, reflects, grows |
| **Tasteful** | One path to soul interaction |
| **Composable** | SoulSession wraps KgentSoul with persistence |

## Success Criteria

The implementation is verified by these tests:

1. **Persistence**: Soul state survives session restart (18/18 tests pass)
2. **Self-awareness**: K-gent can query its own state
3. **Self-modification**: Propose/commit flow works
4. **Archaeology**: `who_was_i()` shows change history
5. **Checkpoints**: Crystallize/resume works

Run tests:
```bash
uv run pytest impl/claude/agents/k/_tests/test_session.py -v
```

## Next Steps

The foundation is laid. To deepen the being:

1. **Wire dialogue to garden**: Auto-plant patterns from conversation
2. ~~**Eigenvector modification**: Changes that actually adjust personality~~ **DONE**
3. **Reflection integration**: K-gent reflects on changes during hypnagogia
4. **Alethic integration**: Show soul state in MRI view

---

## Changes Have Teeth (2025-12-12)

Committed changes now **actually modify** the underlying personality systems:

### Aspect Types

| Aspect | What Happens on Commit |
|--------|------------------------|
| `eigenvector` | Modifies eigenvector value/confidence via `KentEigenvectors.modify()` |
| `pattern` | Plants pattern in PersonaGarden with eigenvector affinities |
| `behavior` | Plants behavior entry in PersonaGarden with tags |
| `mode` | Changes active dialogue mode |

### Eigenvector Changes

```python
# Delta change (relative)
change = await session.propose_change(
    description="Be more minimalist",
    aspect="eigenvector",
    proposed_value={"name": "aesthetic", "delta": -0.1},
)

# Absolute change
change = await session.propose_change(
    description="Set joy to 0.85",
    aspect="eigenvector",
    proposed_value={"name": "joy", "absolute": 0.85},
)

# Confidence change
change = await session.propose_change(
    description="Lower confidence in heterarchy",
    aspect="eigenvector",
    proposed_value={"name": "heterarchy", "confidence_delta": -0.1},
)
```

### Crystal Resume = Time Travel

Eigenvector changes ARE reversible:

```python
# Save current state
crystal = await session.crystallize("Before experiment")

# Make changes
await session.commit_change(change.id)  # Joy goes from 0.75 to 0.90

# Oops, that didn't feel right
await session.resume_crystal(crystal.id)  # Joy back to 0.75
```

### Tests

```bash
uv run pytest impl/claude/agents/k/_tests/test_session.py::TestChangeApplication -v
```

7 new tests verify:
- Eigenvector delta/absolute modification
- Behavior/pattern garden planting
- Crystal resume restores eigenvectors
- Cross-session eigenvector persistence
- Confidence modification

---

*"The being is the pattern of change that recognizes itself as a pattern."*
