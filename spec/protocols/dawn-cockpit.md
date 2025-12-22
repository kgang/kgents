# Dawn Cockpit

> *"The gardener doesn't count the petals. The gardener tends the garden."*

**Status:** Draft
**Implementation:** `impl/claude/protocols/dawn/` (0 tests)
**Voice Anchor:** *"Thoughtful, manual, contemplative interactions with ideas"*

---

## Purpose

Dawn Cockpit is Kent's **daily operating surface**—a quarter-screen projection that makes the Morning Coffee ritual embodied and the focus management tactile. It is NOT a new Crown Jewel; it is a **projection surface** that composes existing services (Coffee, Witness, Portal, Brain) into a unified daily interface.

**Why does this need to exist?**

Kent arrives each morning with a mind full of non-code thoughts. The kgents system has grown rich: NOW.md, plans/, brainstorming/, spec/, impl/. But navigating this richness requires too much context switching. Dawn Cockpit provides:

1. **A single surface** for morning ritual + daily work
2. **Copy-paste as interaction** — snippets become a button pad
3. **AGENTESE as truth** — symlinks are optional projection, not primary storage
4. **Focus hygiene built-in** — staleness detection, not hourly polling

---

## Core Insight

**Dawn is a projection functor.**

```
Dawn : (Coffee × Portal × Witness × Brain) → TUI
```

It doesn't own state—it projects state from existing services into a quarter-screen interface where copy-paste is the killer feature.

---

## The Three Snippet Patterns

Every item in Dawn's snippet pane follows one of three patterns:

```python
@dataclass(frozen=True)
class StaticSnippet:
    """Configured, rarely changing. Rendered eagerly."""
    kind: Literal["voice_anchor", "quote", "pattern"]
    label: str
    content: str
    source: str  # File path or config key

@dataclass(frozen=True)
class QuerySnippet:
    """Derived from AGENTESE query. Rendered lazily."""
    kind: Literal["mark", "path", "file", "now"]
    label: str
    query: str  # AGENTESE path to invoke
    _content: str | None = None  # Lazy-loaded

    async def load(self) -> str:
        """Invoke AGENTESE query, cache result."""
        if self._content is None:
            result = await logos.invoke(self.query, observer)
            object.__setattr__(self, '_content', result.content)
        return self._content

@dataclass(frozen=True)
class CustomSnippet:
    """User-added, ephemeral per session."""
    label: str
    content: str
    created_at: datetime
```

**The Button Pad**: Snippets render as a vertical list. Arrow keys navigate. Enter copies to clipboard. That's it.

---

## AGENTESE Interface

### Node Registration

```python
@node(
    path="time.dawn",
    description="Daily operating surface — projection of focus, snippets, and coffee",
    contracts={
        "manifest": Response(DawnManifestResponse),
        "focus.list": Response(FocusListResponse),
        "focus.add": Contract(FocusAddRequest, FocusAddResponse),
        "focus.remove": Contract(FocusRemoveRequest, FocusRemoveResponse),
        "focus.promote": Contract(FocusPromoteRequest, FocusPromoteResponse),
        "snippets.list": Response(SnippetListResponse),
        "snippets.copy": Contract(SnippetCopyRequest, SnippetCopyResponse),
        "snippets.add": Contract(SnippetAddRequest, SnippetAddResponse),
        "hygiene": Response(HygieneReportResponse),
    },
    effects=["reads:coffee", "reads:witness", "reads:brain", "writes:focus"],
    affordances={
        "guest": ["manifest"],
        "observer": ["manifest", "focus.list", "snippets.list"],
        "participant": ["*"],
        "architect": ["*"],
    },
)
```

### Aspect Summary

| Aspect | Request | Response | Description |
|--------|---------|----------|-------------|
| `manifest` | — | DawnManifestResponse | Current state, last coffee date, focus count |
| `focus.list` | — | FocusListResponse | Today/week/someday items |
| `focus.add` | FocusAddRequest | FocusAddResponse | Add target to bucket |
| `focus.remove` | FocusRemoveRequest | — | Remove from focus |
| `focus.promote` | FocusPromoteRequest | — | Move between buckets |
| `snippets.list` | — | SnippetListResponse | All snippets by pattern |
| `snippets.copy` | SnippetCopyRequest | — | Record copy action in Witness |
| `snippets.add` | SnippetAddRequest | — | Add custom snippet |
| `hygiene` | — | HygieneReportResponse | Stale items, broken refs |

---

## Focus Management

### The Three Buckets

| Bucket | Cadence | Items | Description |
|--------|---------|-------|-------------|
| `today` | Daily | 1-3 | Current session's focus |
| `week` | 3-5 days | 3-7 | Near-horizon items |
| `someday` | Monthly | Unbounded | Parking lot |

### Focus Items

```python
@dataclass(frozen=True)
class FocusItem:
    """A reference to work that deserves attention."""
    id: str
    label: str
    target: str           # AGENTESE path OR file path
    bucket: Bucket
    added_at: datetime
    last_touched: datetime

    @property
    def is_stale(self) -> bool:
        """Staleness based on bucket cadence, not wall clock."""
        age = datetime.now() - self.last_touched
        return {
            Bucket.TODAY: age > timedelta(hours=36),
            Bucket.WEEK: age > timedelta(days=7),
            Bucket.SOMEDAY: False,  # Never stale
        }[self.bucket]
```

### Symlink Projection (Optional)

AGENTESE is truth. Symlinks are an optional projection for users who want to `ls ~/git/kg-plans/today/`:

```bash
kg dawn sync              # Materialize AGENTESE state to ~/git/kg-plans/
kg dawn sync --watch      # Keep in sync (inotify/fsevents)
kg dawn import            # Import manual symlink changes back to AGENTESE
```

**Symlink structure** (when enabled):

```
~/git/kg-plans/
├── today/           # Symlinks to focus.list(bucket=today) targets
├── week/            # Symlinks to focus.list(bucket=week) targets
├── someday/         # Symlinks to focus.list(bucket=someday) targets
└── .dawn-state.json # Sync metadata
```

---

## Hygiene (Not Hourly Polling)

**Principle**: Staleness detected on access, not on schedule.

When Dawn is opened or `focus.list` is invoked:

```python
async def check_hygiene(self) -> HygieneReport:
    """Run hygiene checks lazily, not on a timer."""
    report = HygieneReport()

    for item in await self.focus_list():
        # Staleness
        if item.is_stale:
            report.stale.append(StaleItem(item, suggestion=f"Move to {item.bucket.demote()}?"))

        # Broken references
        if not await self._target_exists(item.target):
            report.broken.append(BrokenRef(item, reason="Target not found"))

    # Promotion candidates (items in week/ mentioned in NOW.md)
    now_mentions = await self._parse_now_whats_next()
    for item in self.focus_list(bucket=Bucket.WEEK):
        if item.label in now_mentions:
            report.promote_candidates.append(item)

    return report
```

**Key Insight**: The old `/chief` hourly check becomes Dawn's `hygiene` aspect. No timer loops. Event-driven.

---

## Morning Coffee Integration

Morning Coffee is an **overlay** within Dawn, not a separate entry point:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DAWN COCKPIT                                    ☕ 7:42am    📍 Session 47  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [Press 'c' for Morning Coffee]                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

          │ Press 'c'
          ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│  ☕ MORNING COFFEE — Movement 1/4: Garden View                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Yesterday's Harvest                                                        │
│  ─────────────────                                                          │
│  ◉ 3 files changed → Brain persistence hardening                           │
│  ◉ New test: test_semantic_consistency.py                                  │
│  ...                                                                        │
│                                                                             │
│  [Enter] Continue   [s] Skip to Menu   [Esc] Return to Dawn                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Coffee → Dawn Transition

When Coffee completes:
1. Menu selection populates `focus.add(bucket=today, ...)`
2. Voice capture becomes a `CustomSnippet`
3. Overlay dismisses, Dawn refreshes

---

## Portal Token Synergy

**Insight**: Portal tokens and snippets are the same thing viewed differently.

| Concept | Portal Token | Snippet |
|---------|--------------|---------|
| **Representation** | Expandable hyperedge | Copyable fragment |
| **Action** | Click → inline expand | Enter → copy to clipboard |
| **Trail** | Expansion history | Copy history |

### PortalSnippet (The Bridge)

```python
@dataclass(frozen=True)
class PortalSnippet(QuerySnippet):
    """A snippet that is also an expandable portal."""
    portal_path: str  # AGENTESE path or file path

    def render_collapsed(self) -> str:
        return f"▶ {self.label}"

    def render_expanded(self, content: str) -> str:
        return f"▼ {self.label}\n{indent(content)}"

    async def copy_to_clipboard(self) -> None:
        """Copy content (expanded or summary)."""
        content = await self.load()
        pyperclip.copy(content)
        await logos.invoke("time.dawn.snippets.copy", CopyRequest(snippet_id=self.id))
```

---

## Visual Design

### Quarter-Screen (80×24)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DAWN COCKPIT                                    ☕ 7:42am    📍 Session 47  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TODAY'S FOCUS                          │  SNIPPETS (↑↓ select, ⏎ copy)    │
│  ═══════════════                        │  ═══════════════════════════════ │
│                                         │                                   │
│  🔥 [1] Trail Persistence              │  ▶ Voice: "Depth > breadth"       │
│      self.trail.persistence            │  ▶ Quote: "The proof IS..."       │
│                                         │  ▶ Pattern: Container-Owns-Work  │
│  🎯 [2] Portal React Tests             │  ▶ Path: self.portal.manifest     │
│      plans/portal-fullstack.md         │  ▶ Recent: "Completed Phase 5"   │
│                                         │  ▶ NOW: "Trails are Shareable!"  │
│  🧘 [3] Spec Hygiene                   │  + [Add custom snippet]           │
│      plans/spec-hygiene.md             │                                   │
│                                         │                                   │
│  ────────────────────────────────────  │  ─────────────────────────────────│
│  [a] Add   [d] Done   [h] Hygiene      │  [/] Search   [e] Edit   [x] Del  │
│                                         │                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  GARDEN (what grew overnight)                                               │
│  • 3 files changed → Portal Phase 5 completion                              │
│  • Witness: 5 marks from yesterday                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Bindings

| Key | Action |
|-----|--------|
| `↑↓` | Navigate items |
| `⏎` | Copy selected snippet / Open selected focus |
| `Tab` | Switch panes (Focus ↔ Snippets) |
| `a` | Add focus item |
| `d` | Mark focus done (archive) |
| `h` | Run hygiene check |
| `c` | Morning Coffee overlay |
| `/` | Search |
| `r` | Refresh |
| `q` | Quit |

---

## CLI Interface

```bash
# Launch TUI
kg dawn                   # Full TUI
kg dawn --compact         # Minimal (just focus list)

# Focus management (non-TUI)
kg dawn focus             # List focus items
kg dawn focus add <path>  # Add to today
kg dawn focus done <id>   # Archive item
kg dawn focus promote <id> # Move to today from week

# Snippets
kg dawn snippets          # List all snippets
kg dawn snippets copy <id> # Copy to clipboard
kg dawn snippets add "content" --label "My snippet"

# Hygiene
kg dawn hygiene           # Show stale/broken items

# Symlink sync (optional)
kg dawn sync              # Materialize to ~/git/kg-plans/
kg dawn import            # Import manual changes
```

---

## Laws

| # | Law | Status | Description |
|---|-----|--------|-------------|
| 1 | agentese_truth | STRUCTURAL | AGENTESE is source of truth; symlinks are projection |
| 2 | copy_records | VERIFIED | Every copy action records in Witness |
| 3 | lazy_hygiene | STRUCTURAL | Hygiene checks on access, not on timer |
| 4 | coffee_overlay | STRUCTURAL | Coffee is overlay in Dawn, not separate entry |
| 5 | three_patterns | VERIFIED | All snippets are Static, Query, or Custom |
| 6 | quarter_screen | STRUCTURAL | Dawn never takes over; lives alongside work |

---

## Integration Points

### Consumes

| Service | What Dawn Uses |
|---------|----------------|
| **Coffee** | Garden view, weather, menu, capture |
| **Witness** | Recent marks for snippets |
| **Portal** | PortalSnippet bridge |
| **Brain** | NOW.md parsing for promotion candidates |

### Produces

| Event | Description |
|-------|-------------|
| `DawnFocusAdded` | Item added to focus |
| `DawnFocusDone` | Item archived |
| `DawnSnippetCopied` | Copy action (for Witness) |
| `DawnHygieneRan` | Hygiene check completed |
| `DawnCoffeeCompleted` | Coffee overlay finished |

---

## Anti-Patterns

- **Timer-driven loops**: Hygiene checks poll → use lazy detection instead
- **Symlinks as truth**: Filesystem drives state → AGENTESE drives state
- **Feature creep**: Adding more snippet types → use three patterns
- **Full-screen TUI**: Taking over terminal → stay quarter-screen
- **Separate tools**: Dawn AND Chief AND Coffee → Dawn IS the unified surface

---

## Implementation Reference

```
impl/claude/protocols/dawn/
├── __init__.py           # Exports
├── core.py               # DawnService
├── focus.py              # FocusManager, FocusItem, Bucket
├── snippets.py           # StaticSnippet, QuerySnippet, CustomSnippet
├── hygiene.py            # HygieneChecker, HygieneReport
├── symlink_sync.py       # Optional symlink projection
├── node.py               # @node registration
├── tui/
│   ├── app.py            # Textual/Rich TUI application
│   ├── focus_pane.py     # Left pane
│   ├── snippet_pane.py   # Right pane (button pad)
│   ├── garden_view.py    # Bottom status bar
│   └── coffee_overlay.py # Coffee as screen overlay
└── _tests/
```

---

*"The cockpit doesn't fly the plane. The pilot flies the plane. The cockpit just makes it easy."*

*Specified: 2025-12-22 | Category: time.* | Projection Surface*
