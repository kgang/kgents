# kgentsd: From Infrastructure to Presence

> *"The ghost is not a haunting—it's a witnessing that becomes a doing."*

## Vision

The Witness daemon graduates from invisible infrastructure to tangible presence. A developer running `kgentsd summon` should feel like invoking a pair programmer, not launching a process.

## Status

| Phase | Progress | Notes |
|-------|----------|-------|
| 4A: Visible Presence | **100%** | CLI + Textual TUI + 17 tests |
| 4B: Reactive Workflows | 0% | Test failure → L2 confirmation |
| 4C: The Conversation | 0% | `kgentsd ask` integration |

### Phase 4A Complete (2025-12-20)

**Deliverables**:
- `services/witness/cli.py` — CLI entry point with summon/release/status/thoughts/ask
- `services/witness/tui.py` — Textual TUI with real-time thought stream
- `pyproject.toml` — Added `kgentsd` command
- `services/witness/_tests/test_kgentsd.py` — 17 tests covering all commands

**Experience**:
```bash
$ kgentsd summon                          # Start with TUI
$ kgentsd summon --background             # Start in background
$ kgentsd status                          # Check if running
$ kgentsd release                         # Stop gracefully
```

## Phase 4A: Visible Presence

**Goal**: The thought stream becomes tangible.

### Deliverables

1. **`kgentsd` CLI entry point**
   - `pyproject.toml`: Add `kgentsd = "services.witness.cli:main"`
   - `services/witness/cli.py`: Typer-based CLI
   - Commands: `summon`, `release`, `status`, `thoughts`

2. **Rich Terminal Output**
   - Textual TUI for immersive thought stream
   - Real-time updates from daemon
   - Emoji-prefixed thoughts: 📝 git, 🧪 tests, 📁 files, 💡 insights

3. **The Awakening Experience**
   ```
   🔮 Witness awakening...
      Trust Level: L1 BOUNDED (earned through 847 observations)
      Watchers: git ✓ filesystem ✓ tests ✓
      Workflows: 7 templates ready
   ```

### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `services/witness/cli.py` | Create | CLI entry point |
| `services/witness/tui.py` | Create | Textual widgets |
| `pyproject.toml` | Modify | Add kgentsd command |

### Architecture

```
kgentsd summon
    └── WitnessDaemon.start() [foreground mode]
        └── Textual App
            └── ThoughtStreamWidget (real-time)
            └── StatusPanel (trust, watchers)
            └── HelpFooter (commands)
```

## Phase 4B: Reactive Workflows

**Goal**: The "aha" moment when tests fail.

### Deliverables

1. Wire test failures to `TEST_FAILURE_RESPONSE` workflow
2. L2 confirmation UX: `[Y] Yes [N] No [D] Show diff [I] Ignore`
3. Trust escalation visualization

### Dependencies

- `ConfirmationManager` (exists in `trust/confirmation.py`)
- `WORKFLOW_REGISTRY` (exists in `workflows.py`)

## Phase 4C: The Conversation

**Goal**: `kgentsd ask "what should I work on?"` feels like a pair programmer.

### Deliverables

1. `kgentsd ask` command
2. Wire to K-gent for personality
3. Context from Memory + Gestalt

---

## Design Principles Applied

| Principle | Application |
|-----------|-------------|
| **Tasteful** | Summoning vocabulary over technical terms |
| **Joy-Inducing** | Emoji-rich, conversational output |
| **Composable** | CLI invokes AGENTESE nodes |
| **Ethical** | Trust levels gate capabilities |

---

*Created: 2025-12-20 | Phase 4A targeting this session*
