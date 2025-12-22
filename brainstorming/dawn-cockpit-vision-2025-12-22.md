# Dawn Cockpit: Kent's Daily Operating Interface

> *"The gardener doesn't count the petals. The gardener tends the garden."*
>
> *"Thoughtful, manual, contemplative interactions with ideas"* — Kent's Wishes

**Status:** Vision / Architecture Brainstorm
**Date:** 2025-12-22
**Voice Anchor:** *"Daring, bold, creative, opinionated but not gaudy"*

---

## The Problem (Visceral)

Kent arrives each morning with a mind full of non-code thoughts—dreams, frolics, half-formed intuitions. The kgents system has grown rich: NOW.md, plans/, brainstorming/, spec/, impl/. But:

- **File management is challenging** — too many places to look, too many files to juggle
- **Copy-paste dance** — constantly opening files just to grab snippets
- **Scattered focus** — important plans buried in `plans/` with no centralized "today's work"
- **Context switching tax** — jumping between terminal, editor, browser, docs

**The gap**: Morning Coffee describes the ritual beautifully, but Kent needs **the cockpit**—a simple, physical interface that makes the ritual embodied, not just conceptual.

---

## The Vision: Dawn Cockpit

A quarter-screen Textual TUI that serves as Kent's **daily operating surface**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DAWN COCKPIT                                    ☕ 7:42am    📍 Session 47  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TODAY'S FOCUS                          │  SNIPPETS (↑↓ to select, ⏎ copy)│
│  ═══════════════                        │  ═══════════════════════════════ │
│                                         │                                   │
│  🔥 [1] Trail Persistence              │  ▶ Voice Anchor: "Depth > breadth"│
│      ~/git/kg-plans/today/trail.md     │  ▶ Quote: "The proof IS..."       │
│                                         │  ▶ Pattern: Container-Owns-Work  │
│  🎯 [2] Portal React Tests             │  ▶ AGENTESE: self.portal.manifest │
│      ~/git/kg-plans/today/portal.md    │  ▶ Path: impl/claude/services/... │
│                                         │  ▶ Recent mark: "Completed Phase" │
│  🧘 [3] Spec Hygiene Cleanup           │  ▶ NOW.md snippet                  │
│      ~/git/kg-plans/week/hygiene.md    │  ▶ _focus.md constraint           │
│                                         │                                   │
│  ────────────────────────────────────  │  ─────────────────────────────────│
│  [a] Add new focus   [r] Refresh       │  [/] Search   [+] Add snippet     │
│  [h] Hourly check    [c] Coffee ritual │  [e] Edit     [x] Remove          │
│                                         │                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  GARDEN VIEW (what grew overnight)                                          │
│  • 3 files changed → Portal Phase 5 completion                              │
│  • New test: test_self_context.py (+47 tests)                              │
│  • Witness: 5 marks from yesterday                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Principles

1. **Quarter-screen by design** — Doesn't take over, lives alongside terminal work
2. **Copy-paste first** — The killer feature is `↵` copies selection to clipboard
3. **Symlink-backed** — `~/git/kg-plans/` is the physical truth, TUI is the view
4. **Hourly cadence** — `/chief` integration for symlink hygiene
5. **Portal integration** — Snippets ARE portal tokens; expanding them is the same UX

---

## Part 1: The Symlink Architecture

### 1.1 The kg-plans Directory

```
~/git/kg-plans/
├── today/           # Current day's focus (symlinks to spec/plans/)
│   ├── trail.md → ~/git/kgents/plans/trail-persistence.md
│   ├── portal.md → ~/git/kgents/spec/protocols/portal-token.md
│   └── hygiene.md → ~/git/kgents/plans/spec-hygiene.md
│
├── week/            # Longer-horizon items (3-5 day cadence)
│   ├── ashc.md → ~/git/kgents/spec/protocols/ASHC-...
│   └── witness.md → ~/git/kgents/spec/services/witness.md
│
├── someday/         # Parking lot (monthly review)
│   └── town-polish.md → ~/git/kgents/plans/town-...
│
├── snippets/        # Copy-paste ready fragments
│   ├── voice-anchors.md     # Kent's quotes for anti-sausage
│   ├── patterns.md          # Common crown jewel patterns
│   ├── agentese-paths.md    # Frequently-used AGENTESE paths
│   └── gotchas.md           # Teaching moments to remember
│
└── .chief-state.json  # /chief tracking state
```

### 1.2 Effort Buckets

| Bucket | Cadence | Symlinks | /chief Action |
|--------|---------|----------|---------------|
| `today/` | Daily | 1-3 items | Promoted from `week/` each morning |
| `week/` | 3-5 days | 3-7 items | Review/promote/archive on Monday |
| `someday/` | Monthly | Unbounded | Archive or promote on 1st |

### 1.3 /chief Symlink Management

```bash
# Hourly /chief integration (runs every hour during active session)
kg chief --symlinks

# What it does:
# 1. Reads ~/.kgents/chief-state.json for current symlinks
# 2. Validates symlinks still point to existing files
# 3. Checks for stale items (in today/ for >24h)
# 4. Prompts: "Trail Persistence has been in today/ for 2 days. Move to week/?"
# 5. Reports broken symlinks
# 6. Syncs with NOW.md status

# Manual actions
kg chief add today plans/new-feature.md   # Create symlink
kg chief move trail week                   # Demote to week/
kg chief archive hygiene                   # Move to someday/
kg chief clean                            # Remove broken symlinks
```

---

## Part 2: The Textual TUI

### 2.1 The Experience

**Launch**: `kg dawn` or just `dawn` (shell alias)

**Size**: 80x24 characters (quarter screen in 160x48 terminal)

**Navigation**:
- `↑↓` — Move between items
- `⏎` — Copy selected snippet to clipboard
- `Tab` — Switch between Focus and Snippets panes
- `/` — Search across all panes
- `q` — Quit (or just backgrounded, stays resident)

**Interactions**:
- `a` — Add new focus (opens fuzzy finder over spec/ and plans/)
- `r` — Refresh from git and filesystem
- `h` — Run hourly /chief check inline
- `c` — Launch Morning Coffee ritual (full-screen overlay)

### 2.2 The Snippet Copy-Paste System

**The killer feature**: Every item in Snippets pane is **instantly copyable**.

```python
# Snippet types (each renders differently, all copy identically)
@dataclass
class Snippet:
    """A copy-paste ready fragment."""

    kind: SnippetKind  # voice_anchor, quote, pattern, path, mark, etc.
    label: str         # Display text
    content: str       # What gets copied
    source: str        # Where it came from (for editing)

    def render_for_tui(self) -> str:
        """Show in snippet list."""
        icon = SNIPPET_ICONS[self.kind]
        return f"{icon} {self.label}"

    def copy_to_clipboard(self) -> None:
        """The money shot."""
        pyperclip.copy(self.content)
```

**Snippet Sources**:

| Kind | Source | Example Content |
|------|--------|-----------------|
| `voice_anchor` | `_focus.md`, morning capture | "Depth over breadth" |
| `quote` | `_focus.md` Kent's Quotes | "The proof IS the decision." |
| `pattern` | `crown-jewel-patterns.md` | Container-Owns-Workflow pattern |
| `agentese_path` | Recent invocations | `self.portal.manifest` |
| `file_path` | Recent opens, git status | `impl/claude/services/brain/core.py` |
| `mark` | Witness recent | "Completed Portal Phase 5" |
| `now_snippet` | NOW.md parsed | "Trails are Now Shareable!" |
| `custom` | User-added | Anything |

### 2.3 Implementation Architecture

```python
# impl/claude/protocols/dawn/app.py

from textual.app import App, ComposeResult
from textual.widgets import Static, ListView, ListItem, Footer
from textual.containers import Horizontal, Vertical

class DawnCockpit(App):
    """Kent's daily operating interface."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("h", "hourly_check", "Hourly"),
        ("c", "coffee", "Coffee"),
        ("a", "add_focus", "Add"),
        ("/", "search", "Search"),
        ("tab", "switch_pane", "Switch"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield FocusPane()     # Left: Today's Focus
            yield SnippetPane()   # Right: Copy-paste snippets
        yield GardenView()       # Bottom: Git changes summary
        yield Footer()

    async def action_refresh(self) -> None:
        """Refresh from filesystem and git."""
        self.query_one(FocusPane).refresh_symlinks()
        self.query_one(SnippetPane).refresh_snippets()
        self.query_one(GardenView).refresh_git()

    async def action_hourly_check(self) -> None:
        """Run /chief symlink hygiene inline."""
        result = await run_chief_symlinks()
        self.notify(result.summary)


class FocusPane(Widget):
    """Today's focus items from ~/git/kg-plans/today/"""

    def __init__(self) -> None:
        super().__init__()
        self.symlinks = SymlinkManager(Path.home() / "git/kg-plans")

    def refresh_symlinks(self) -> None:
        self.symlinks.scan()
        self.items = [
            FocusItem(link.name, link.target, link.bucket)
            for link in self.symlinks.today()
        ]


class SnippetPane(Widget):
    """Copy-paste snippet library."""

    def __init__(self) -> None:
        super().__init__()
        self.snippets = SnippetLibrary()

    def action_copy(self) -> None:
        """Copy selected snippet to clipboard."""
        selected = self.highlighted
        selected.copy_to_clipboard()
        self.notify(f"Copied: {selected.label}")
```

---

## Part 3: Portal Token Synergy

### 3.1 The Unification Insight

**Portal tokens** and **snippets** are the same thing viewed differently:

| Concept | Portal Token | Snippet |
|---------|--------------|---------|
| **Representation** | Expandable hyperedge | Copyable fragment |
| **Action** | Click → inline expand | Enter → copy to clipboard |
| **Context** | Document exploration | Daily work |
| **Trail** | Expansion history | Copy history |

### 3.2 Bidirectional Bridge

```python
# A snippet can BE a portal token
@dataclass
class PortalSnippet(Snippet):
    """A snippet that is also an expandable portal."""

    portal_path: str  # AGENTESE path or file path
    expanded: bool = False

    def render_for_tui(self, expanded: bool = False) -> str:
        if not expanded:
            return f"▶ [{self.kind}] {self.label}"
        else:
            return f"▼ [{self.kind}] {self.label}\n{indent(self.content)}"

    def copy_to_clipboard(self) -> None:
        """Copy content regardless of expansion state."""
        pyperclip.copy(self.content)

    async def expand(self) -> "PortalSnippet":
        """Expand the portal, loading content."""
        content = await fetch_portal_content(self.portal_path)
        return replace(self, content=content, expanded=True)


# The snippet pane can render portals
class SnippetPane(Widget):

    def action_expand(self) -> None:
        """Expand selected snippet if it's a portal."""
        selected = self.highlighted
        if isinstance(selected, PortalSnippet):
            expanded = await selected.expand()
            self.replace_item(selected, expanded)
```

### 3.3 Trail Integration

Both portal expansions and snippet copies create trail events:

```python
@dataclass
class DawnTrailEvent:
    """An event in the Dawn session trail."""

    kind: str  # "copy", "expand", "focus_switch", "search"
    target: str  # What was acted on
    timestamp: datetime
    context: dict[str, Any]  # Additional metadata

# Trail persists to Witness
async def record_dawn_action(event: DawnTrailEvent) -> None:
    if event.kind == "copy":
        await witness.mark(
            action=f"Copied snippet: {event.target}",
            reasoning="Daily work facilitation",
        )
    elif event.kind == "expand":
        await witness.mark(
            action=f"Expanded portal: {event.target}",
            reasoning="Context exploration",
        )
```

---

## Part 4: /chief Integration

### 4.1 Hourly Cadence Protocol

```python
# services/liminal/chief/symlink_manager.py

@dataclass
class ChiefState:
    """Persisted state for /chief symlink management."""

    symlinks: dict[str, SymlinkRecord]  # path → record
    last_check: datetime
    stale_warnings: list[str]
    broken_links: list[str]


class SymlinkManager:
    """Manages ~/git/kg-plans/ symlinks with hourly hygiene."""

    def __init__(self, base_path: Path = Path.home() / "git/kg-plans"):
        self.base_path = base_path
        self.state_file = base_path / ".chief-state.json"

    def hourly_check(self) -> ChiefReport:
        """Run hourly symlink hygiene."""
        report = ChiefReport()

        # 1. Find broken symlinks
        for bucket in ["today", "week", "someday"]:
            for link in (self.base_path / bucket).iterdir():
                if link.is_symlink() and not link.exists():
                    report.broken.append(link)

        # 2. Find stale items in today/
        for link in (self.base_path / "today").iterdir():
            age = datetime.now() - self._get_link_age(link)
            if age > timedelta(hours=24):
                report.stale.append(StaleItem(link, age))

        # 3. Check for items in week/ ready for today/
        # (Based on NOW.md "What's Next" section)
        next_items = self._parse_now_whats_next()
        for item in next_items:
            if self._find_matching_link(item, "week"):
                report.promote_candidates.append(item)

        return report

    def add(self, bucket: str, target: str, name: str | None = None) -> Path:
        """Create symlink in bucket pointing to target."""
        target_path = Path(target).resolve()
        link_name = name or target_path.stem + ".md"
        link_path = self.base_path / bucket / link_name
        link_path.symlink_to(target_path)
        return link_path

    def move(self, name: str, from_bucket: str, to_bucket: str) -> Path:
        """Move symlink between buckets."""
        old_path = self.base_path / from_bucket / name
        target = old_path.resolve()
        old_path.unlink()
        return self.add(to_bucket, str(target), name)
```

### 4.2 /chief Integration Points

```bash
# Morning ritual: /chief promotes from week/ based on NOW.md
kg chief morning
# → "Promoting 'trail-persistence.md' to today/ (mentioned in NOW.md What's Next)"

# Hourly check: /chief validates and warns
kg chief hourly
# → "Warning: 'portal.md' has been in today/ for 36 hours. Move to week/? [y/n]"

# Session end: /chief summarizes
kg chief summary
# → "Today: 2 items completed, 1 moved to week/, 3 snippets copied"
```

---

## Part 5: Interactive Text Synergy

### 5.1 The Connection

From `context-management-agents.md`:
> *"Every text edit operation is writing, compiling, and executing a program."*

The Dawn Cockpit operationalizes this insight:

| Concept | Document | Dawn Cockpit |
|---------|----------|--------------|
| **Lens** | Focus on file slice | Focus on today's symlinks |
| **Portal** | Expand inline | Expand snippet |
| **Harness** | Loop detection | Hourly /chief check |
| **Trail** | Navigation history | Action history |

### 5.2 Portal Token as Copy Target

The existing `PortalTree.tsx` shows portals with expand/collapse. The Dawn Cockpit adds:

```typescript
// Extension to portal.ts for Dawn integration

interface DawnPortalAction {
  // Existing portal actions
  expand: (path: string[]) => Promise<void>;
  collapse: (path: string[]) => Promise<void>;

  // New Dawn actions
  copyPath: (path: string[]) => void;          // Copy AGENTESE path
  copyContent: (path: string[]) => void;       // Copy expanded content
  sendToSnippets: (path: string[]) => void;    // Add to snippet library
}
```

### 5.3 Bidirectional Updates

```python
# When Dawn Cockpit copies a snippet, update portal token state
async def on_snippet_copy(snippet: Snippet) -> None:
    if isinstance(snippet, PortalSnippet):
        # Record as trail event in portal system
        await self_portal.record_action(
            action="copy",
            path=snippet.portal_path,
            timestamp=now(),
        )

# When portal is expanded in web UI, update Dawn snippets
async def on_portal_expand(signal: PortalOpenSignal) -> None:
    # Add to recent snippets in Dawn
    await dawn_snippets.add(
        kind="agentese_path",
        label=signal.edge_type,
        content=signal.parent_path,
        source="portal_expansion",
    )
```

---

## Part 6: Morning Coffee Integration

### 6.1 Coffee as Full-Screen Overlay

The Morning Coffee ritual becomes a **full-screen overlay** within Dawn:

```python
class CoffeeOverlay(Screen):
    """Morning Coffee ritual as Dawn overlay."""

    BINDINGS = [
        ("escape", "dismiss", "Exit to Dawn"),
        ("enter", "next_movement", "Continue"),
        ("s", "skip_to_menu", "Skip to Menu"),
    ]

    def compose(self) -> ComposeResult:
        yield MovementDisplay()  # Current movement
        yield ProgressIndicator()  # 1/4 movements
        yield InputCapture()  # For voice capture

    async def action_next_movement(self) -> None:
        if self.current_movement == "garden":
            self.show_movement("weather")
        elif self.current_movement == "weather":
            self.show_movement("menu")
        elif self.current_movement == "menu":
            # User selected challenge, populate today/ symlinks
            selected = await self.get_menu_selection()
            await self.populate_today_focus(selected)
            self.show_movement("capture")
        elif self.current_movement == "capture":
            # Capture complete, return to Dawn
            voice = await self.get_voice_capture()
            await self.save_voice_to_snippets(voice)
            self.dismiss()
```

### 6.2 Coffee → Dawn Transition

```
Coffee Menu Selection          →    Dawn today/ Symlinks
═══════════════════════════════════════════════════════
🔥 "Trail Persistence"         →    today/trail.md → spec/...
🎯 "Portal React Tests"        →    today/portal.md → plans/...
🧘 "Spec Hygiene Cleanup"      →    today/hygiene.md → plans/...

Coffee Voice Capture           →    Dawn Snippets
═══════════════════════════════════════════════════════
"What would make today good?"  →    voice_anchor snippet
Fresh reaction to garden       →    today_insight snippet
```

---

## Part 7: Implementation Roadmap

### Phase 1: Foundation (2-3 sessions)

**Goal**: Minimal viable Dawn Cockpit with symlink management.

| Session | Deliverable | Tests |
|---------|-------------|-------|
| 1.1 | `~/git/kg-plans/` directory structure | Shell script |
| 1.2 | `SymlinkManager` Python class | pytest |
| 1.3 | Basic Textual app with two panes | Manual |

**Exit Criteria**: `kg dawn` launches, shows symlinks, `⏎` copies item.

### Phase 2: Snippet System (2 sessions)

**Goal**: Full snippet library with multiple sources.

| Session | Deliverable | Tests |
|---------|-------------|-------|
| 2.1 | `SnippetLibrary` class | pytest |
| 2.2 | Source integrations (Witness, NOW.md, _focus.md) | Integration |

**Exit Criteria**: Snippets auto-populate from 5+ sources.

### Phase 3: /chief Integration (1-2 sessions)

**Goal**: Hourly symlink hygiene via /chief.

| Session | Deliverable | Tests |
|---------|-------------|-------|
| 3.1 | `ChiefState` persistence | pytest |
| 3.2 | Inline hourly check UI | Manual |

**Exit Criteria**: `h` in Dawn runs /chief check inline.

### Phase 4: Portal Bridge (1-2 sessions)

**Goal**: Bidirectional portal token integration.

| Session | Deliverable | Tests |
|---------|-------------|-------|
| 4.1 | `PortalSnippet` class | pytest |
| 4.2 | Trail recording for Dawn actions | Integration |

**Exit Criteria**: Expanding a snippet records in Witness.

### Phase 5: Coffee Overlay (1-2 sessions)

**Goal**: Morning Coffee as Dawn overlay.

| Session | Deliverable | Tests |
|---------|-------------|-------|
| 5.1 | `CoffeeOverlay` screen | pytest |
| 5.2 | Coffee → Dawn symlink creation | Integration |

**Exit Criteria**: Coffee Menu selection creates today/ symlinks.

---

## Part 8: The Daily Flow (Vision)

### 7:00 AM — Arrival

```bash
$ dawn
# Dawn Cockpit opens, quarter-screen
# Shows: yesterday's uncompleted focus, garden view, fresh snippets

$ c  # Press 'c' for Coffee
# Full-screen Coffee overlay appears
# Garden View → Conceptual Weather → Menu → Capture
# Menu selection populates today/
# Voice capture adds snippets
# Returns to Dawn with fresh state
```

### 9:00 AM — First Hour

```bash
# Working on first focus item
$ Tab  # Switch to Snippets pane
$ ↓↓⏎  # Navigate to pattern, copy to clipboard
# Paste into current file

$ h  # Hourly check
# "All symlinks valid. 3 items in today/."
```

### 12:00 PM — Midday Check

```bash
$ h  # Hourly check
# "Portal.md completed? [y to archive, n to keep]"
$ y
# Moved to someday/completed/

$ a  # Add new focus
# Fuzzy finder over spec/ and plans/
# Select "witness-integration.md"
# Added to today/
```

### 5:00 PM — End of Day

```bash
$ kg chief summary
# Today: 2 items completed, 1 moved to week/
# Snippets copied: 12
# Portals expanded: 5
# Voice captures: 2

# Dawn auto-updates NOW.md with summary
```

---

## The Daring Check

**Was this vision bold?** ✅ Yes

- **Symlink architecture** is unconventional but tactile—Kent can `ls ~/git/kg-plans/today/` in any context
- **Quarter-screen TUI** respects the terminal-first workflow, doesn't demand full attention
- **Copy-paste as killer feature** honors "thoughtful, manual, contemplative interactions"
- **Portal token unification** isn't just incremental—it's saying "a snippet IS a portal viewed sideways"
- **Hourly /chief cadence** creates rhythm without rigidity

**Was anything smoothed?**

Intentionally NOT smoothed:
- The symlink dependency on `~/git/` path structure (opinionated, not configurable)
- The Textual requirement (could have said "or Rich" but Textual IS the right choice)
- The hourly cadence (could have been configurable, but rhythm > flexibility here)

---

## Appendix: The Anti-Sausage Assessment

**Voice anchors quoted directly:**
- *"Thoughtful, manual, contemplative interactions with ideas"*
- *"The gardener doesn't count the petals"*
- *"Depth over breadth"*
- *"Make it easy for kent and kgents to do the correct, enlightened things"*

**Kent's Wishes honored:**
- ✅ Manual, contemplative: Copy-paste is intentional action
- ✅ Meta-theory: Dawn IS the theory-of-practice for daily work
- ✅ App-builder building app-builder: Dawn uses the same patterns it exposes

**Does it pass the Mirror Test?**

Does Dawn feel like Kent on his best day—a morning where the garden view is clear, the focus is sharp, and the copy-paste dance becomes a single keypress?

*"The musician doesn't start with the hardest passage. She tunes, breathes, plays a scale, feels the instrument respond."*

Dawn Cockpit is the tuning.

---

*Brainstormed: 2025-12-22 | Voice: Preserved | Daring: Yes*
