# Context Perception

> **Archived from**: `spec/protocols/context-perception.md`
> **Status**: Vision document (not ground-truth spec)
> **Date**: 2025-12-24

---

**Status:** Active Development (Core infrastructure complete, visualization evolving)
**Date:** 2025-12-22
**Derives From:** `brainstorming/context-management-agents.md`
**Related:** `typed-hypergraph.md`, `portal-token.md`, `exploration-harness.md`
**Next Evolution:** `brainstorming/context-perception-v2.md` (Cognitive Canvas vision)

**Implementation Summary:**
- Backend: `protocols/context/` — outline.py, parser.py, lens.py, collaboration.py, renderer.py
- Frontend: `web/src/components/portal/` — PortalTree, TrailPanel, PresenceBadge
- Tests: 200+ across supporting layers (typed-hypergraph, portal-token, exploration-harness)

---

## Epigraph

> *"It's just an outline. That happens to be alive."*
>
> *"Copy-paste is a hyperedge traversal. You just didn't know it."*

---

## 1. Purpose

Context Perception is the **visualization layer** for the typed-hypergraph. It makes navigation feel like collaborating on an outline—text you can open, close, copy, paste, link, and navigate. The magic is invisible until you need it.

**The vibe**: Two intelligences (human + agent) editing an outline together. The outline happens to be a metaphysical representation of their distributed cognition.

---

## 2. Core Insight

**Text snippets are the fundamental unit.**

Everything else—parsers, tokens, integrations, overlays, orchestration—exists to make normal operations contextually magical:

| Operation | Surface Behavior | Hidden Magic |
|-----------|------------------|--------------|
| **Open** | Expand a section | Hyperedge traversal, lazy load content |
| **Close** | Collapse a section | Preserve in trail, reclaim attention |
| **Copy** | Select and copy text | Copy includes provenance as invisible metadata |
| **Paste** | Insert text | Paste triggers link creation, evidence record |
| **Navigate** | Click a link | Focus shift, trail step recorded |
| **Link** | Create reference | Bidirectional hyperedge created |

The agent and human see the same outline. The outline is the shared context.

---

## 3. The Four-Layer Stack

```
Layer 4: CONTEXT PERCEPTION (this spec)
         └── Text snippets + semi-transparent UI + magical operations

Layer 3: PORTAL TOKENS (portal-token.md)
         └── Expandable meaning tokens + state machines

Layer 2: EXPLORATION HARNESS (exploration-harness.md)
         └── Budget, loop detection, evidence accumulation

Layer 1: TYPED-HYPERGRAPH (typed-hypergraph.md)
         └── Nodes, hyperedges, trails, observer-dependent affordances
```

Context Perception **projects** the lower layers into text that humans and agents can collaboratively edit.

---

## 4. The Outline Model

### 4.1 Structure

An outline is a tree of **text snippets**:

```
# Investigation: Auth Bug                        ← Root snippet

I started at auth_middleware.py:                 ← Prose snippet

▶ [source] auth_middleware.py                    ← Portal (collapsed)

▼ [tests] 3 files                                ← Portal (expanded)
│
│  test_auth.py                                  ← Nested snippet
│  ────────────────────────────────────────
│  def test_token_expiry():
│      token = create_token(expires_in=3600)
│
│      ▶ [covers] validate_token                 ← Nested portal
│
│  test_auth_edge.py                             ← Another nested snippet
│  ────────────────────────────────────────
│  ...

The issue is in the expiry check.                ← Prose continues
```

Key properties:
- **It's just text** — select it, copy it, paste it
- **Portals are inline** — `▶` collapsed, `▼` expanded
- **Nesting is visual** — indentation shows depth
- **Prose flows around** — this is a document, not a tree widget

### 4.2 Snippet Types

| Type | Appearance | Behavior |
|------|------------|----------|
| **Prose** | Plain text | Editable, flows |
| **Portal (collapsed)** | `▶ [edge] destination` | Click to expand |
| **Portal (expanded)** | `▼ [edge]` + nested content | Click to collapse |
| **Code** | Fenced block with path | Syntax highlighted, copyable |
| **Evidence** | `📎 claim (strength)` | Links to ASHC |
| **Annotation** | `💭 note` | Human or agent commentary |

### 4.3 Operations

Every operation is a **normal text operation** that happens to do more:

```python
class OutlineOperations:
    """Normal operations with hidden magic."""

    def expand(self, portal_path: str) -> None:
        """
        Surface: User clicks ▶ to expand
        Magic: Hyperedge traversal, content lazy-loaded,
               trail step recorded, evidence created
        """

    def collapse(self, portal_path: str) -> None:
        """
        Surface: User clicks ▼ to collapse
        Magic: Content hidden (not deleted), attention freed,
               collapse recorded in trail
        """

    def copy(self, selection: Range) -> Clipboard:
        """
        Surface: Cmd+C copies text
        Magic: Invisible metadata attached—source path,
               timestamp, observer who copied
        """

    def paste(self, clipboard: Clipboard, target: Location) -> None:
        """
        Surface: Cmd+V pastes text
        Magic: If clipboard has provenance, create link back.
               Record paste as evidence of "used X in Y"
        """

    def navigate(self, path: str) -> None:
        """
        Surface: Click a path to jump there
        Magic: Focus shift recorded in trail, breadcrumb updated,
               previous location becomes backtrack target
        """

    def link(self, source: Range, target: str) -> None:
        """
        Surface: Create a reference
        Magic: Bidirectional hyperedge created—source links to target,
               target gains "linked_by" edge back to source
        """
```

---

## 5. Semi-Transparent UI

The UI is **mostly invisible**. It appears when needed, then fades:

### 5.1 The Principles

1. **Text is primary** — UI elements overlay, never replace
2. **Appear on hover/focus** — Controls materialize contextually
3. **Fade when unused** — After 2s of no interaction, UI dims
4. **Never block text** — Overlays use margins, not inline space

### 5.2 Overlay Components

| Component | Trigger | Appearance | Purpose |
|-----------|---------|------------|---------|
| **Edge badges** | Hover on portal | `[tests] 3` | Show destination count |
| **Trail breadcrumb** | Always visible (compact) | `auth > tests > validate` | Show path |
| **Budget meter** | Hover bottom-right | Water level | Show remaining steps |
| **Evidence count** | Hover snippet | `📎 2` | Show linked evidence |
| **Action palette** | Cmd+K or right-click | Floating menu | Show available operations |

### 5.3 The Floating Action Palette

When you press `Cmd+K` or right-click, a palette appears with contextual actions:

```
┌─────────────────────────────────────┐
│ 🔍 Navigate...                      │
│ 📂 Expand all tests                 │
│ 📎 Link to evidence...              │
│ 💭 Add annotation                   │
│ 📋 Copy with provenance             │
│ ↩️  Backtrack                        │
│ 💾 Save trail as...                 │
└─────────────────────────────────────┘
```

Actions depend on:
- What's selected (snippet, portal, range)
- What's focused (current node)
- Observer capabilities (developer vs auditor)

---

## 6. Agent Collaboration

The outline is a **shared workspace**. Humans and agents edit it together:

### 6.1 Presence Indicators

```
# Investigation: Auth Bug

▼ [tests] 3 files
│  test_auth.py  👤 Kent │ 🤖 Claude     ← Both here
│  ────────────────────────────────────
│  def test_token_expiry():
│      token = create_token(...)
```

Lightweight indicators show who's focused where:
- `👤` Human cursor
- `🤖` Agent focus
- Fade after 5s of no activity

### 6.2 Turn-Taking

Agents don't interrupt. They work in **turns**:

```python
class CollaborationProtocol:
    """
    The outline is a shared buffer.
    Humans and agents take turns editing.
    """

    def agent_wants_to_edit(self, agent: Agent, location: Location) -> bool:
        """
        Agent must wait if:
        - Human is actively typing (< 2s since last keystroke)
        - Human has uncommitted changes at location
        - Agent's last edit was rejected
        """

    def agent_proposes_edit(self, edit: Edit) -> ProposedEdit:
        """
        Agent edits appear as proposals first:
        - Highlighted differently (subtle background)
        - Human can accept/reject
        - Auto-accept after 5s if human isn't looking
        """
```

### 6.3 Orchestration

Multiple agents can participate. The outline is the coordination mechanism:

```
# Investigation: Auth Bug

💭 [Claude] I'll check the test coverage.

▼ [tests] 3 files
│  💭 [Claude] This test doesn't cover edge case.
│
│  💭 [Sage] I can add a hypothesis here.
│
│  💭 [Kent] Let's focus on the expiry logic first.
```

Annotations are the agent coordination protocol. No hidden orchestration layer—it's all visible in the outline.

---

## 7. Parser Integration

Text becomes magical because **parsers understand it**:

### 7.1 Token Recognition

The parser recognizes meaning tokens inline:

| Pattern | Token Type | Behavior |
|---------|------------|----------|
| `▶ [edge] dest` | Portal (collapsed) | Expandable |
| `▼ [edge]` | Portal (expanded) | Collapsible |
| `` `path.to.thing` `` | AGENTESE path | Navigable |
| `[ ] Task` | Task checkbox | Toggleable |
| `📎 claim` | Evidence link | Opens sidebar |
| `@agent` | Agent mention | Routes to agent |

### 7.2 Invisible Metadata

Text carries invisible metadata (like rich text formatting):

```python
@dataclass
class TextSnippet:
    """A snippet of text with hidden metadata."""

    visible_text: str          # What you see
    source_path: str | None    # Where it came from
    copied_at: datetime | None # When it was copied
    copied_by: Observer | None # Who copied it
    links: list[str]           # Outgoing hyperedges
    evidence_ids: list[str]    # Linked evidence
```

When you copy text, the metadata travels invisibly. When you paste, the system can use it to create links.

### 7.3 Native Integrations

The outline connects to the OS:

| Integration | Behavior |
|-------------|----------|
| **Clipboard** | Copy includes metadata, paste extracts it |
| **File system** | Paths are clickable, open in editor |
| **Terminal** | Code blocks can be executed |
| **Browser** | URLs open in browser, back-link created |
| **Git** | Changes tracked, diffable |

---

## 8. Lens Virtualization

Large files are virtualized through **lenses**:

### 8.1 The Problem

A 10,000-line file can't fit in context. But an agent needs to see relevant parts.

### 8.2 The Solution: Semantic Lenses

```python
@dataclass
class FileLens:
    """
    A bidirectional view into a file.

    get: Extract the visible slice
    put: Write changes back to the whole
    """

    source_path: str
    focus: FocusSpec

    # What the agent sees
    visible_name: str      # "auth_core:validate_token" not "line 847-920"
    visible_content: str   # Just the function
    line_range: tuple[int, int]

    def get(self, whole: str) -> str:
        """Extract the focused slice."""

    def put(self, part: str, whole: str) -> str:
        """Update the whole from the modified slice."""
```

### 8.3 Sane Names

The agent sees semantic names, not line numbers:

| Reality | What Agent Sees |
|---------|-----------------|
| `monolith.py:847-920` | `auth_core:validate_token` |
| `monolith.py:1205-1280` | `auth_core:refresh_session` |
| `monolith.py:3001-3050` | `auth_utils:parse_jwt` |

The lens extracts meaning, not just bytes.

---

## 9. Multi-Surface Rendering

The outline renders to multiple surfaces:

### 9.1 Surface Fidelity

| Surface | Fidelity | Adaptations |
|---------|----------|-------------|
| **CLI** | 0.2 | ASCII portals (`>` / `v`), no color |
| **TUI** | 0.5 | Full tree, keyboard nav, basic color |
| **Web** | 0.8 | Interactive, animated, presence |
| **marimo** | 0.8 | Notebook cells, executable code |
| **JSON** | 1.0 | Raw state, no rendering |
| **LLM context** | 0.6 | XML-tagged, depth-limited |

### 9.2 Surface-Specific Rendering

```python
def render_portal(portal: PortalToken, surface: Surface) -> str:
    match surface:
        case Surface.CLI:
            icon = ">" if portal.collapsed else "v"
            return f"{icon} [{portal.edge}] {portal.summary}"

        case Surface.TUI:
            icon = "▶" if portal.collapsed else "▼"
            return f"{icon} [{portal.edge}] {portal.summary}"

        case Surface.WEB:
            return f"""
            <details {"" if portal.collapsed else "open"}>
                <summary>[{portal.edge}] {portal.summary}</summary>
                <div class="portal-content">{portal.content}</div>
            </details>
            """

        case Surface.LLM:
            if portal.collapsed:
                return f"<!-- PORTAL: {portal.edge} (collapsed) -->"
            return f"""
            <!-- PORTAL: {portal.edge} (expanded) -->
            {portal.content}
            <!-- END PORTAL -->
            """
```

---

## 10. The Trail as Artifact

The trail of navigation becomes a **shareable artifact**:

### 10.1 Trail Structure

```python
@dataclass
class Trail:
    """
    The path through the outline.
    Shareable, replayable, evidence-bearing.
    """

    id: str
    name: str
    created_by: Observer
    steps: list[TrailStep]
    annotations: dict[int, str]

    def as_outline(self) -> str:
        """Render trail as a readable outline."""

    def replay(self) -> ContextGraph:
        """Replay to recreate the context."""

    def share(self) -> str:
        """Export as shareable format."""
```

### 10.2 Trail as Evidence

The trail IS evidence for claims:

```
📍 Trail: "Auth Bug Investigation"
   Created by: Kent + Claude
   Steps: 7
   Evidence strength: Strong

   1. Started at auth_middleware.py
   2. Expanded [tests] → found 3 test files
   3. Navigated to test_auth.py
   4. Expanded [covers] → found validate_token
   5. 💭 Annotated: "Bug is here—< instead of <="
   6. Created evidence: "Expiry check off-by-one"
   7. Committed claim with strong evidence
```

---

## 11. Laws

### 11.1 Outline Consistency

The outline is always consistent:
```
expand(collapse(portal)) ≡ expand(portal)  # Idempotent
```

### 11.2 Trail Monotonicity

The trail only grows:
```
|trail(t₁)| ≤ |trail(t₂)|  for t₁ < t₂
```

### 11.3 Copy Preserves Provenance

Copied text carries its source:
```
paste(copy(snippet)).source ≡ snippet.path
```

### 11.4 Link Bidirectionality

Links are always bidirectional:
```
link(A, B) ⟹ ∃ reverse_link(B, A)
```

---

## 12. Animation Philosophy

Per moodboard: "Everything Breathes" — but **subtly**:

| Element | Animation | Timing |
|---------|-----------|--------|
| Portal expand | Grow from seed | 200ms ease-out |
| Portal collapse | Shrink to seed | 150ms ease-in |
| Presence fade | Opacity pulse | 3s period |
| Loading state | Skeleton shimmer | Until loaded |
| Budget low | Gentle pulse | When < 20% |

**Rule**: Animations enhance, never distract. Respect `prefers-reduced-motion`.

---

## 13. Anti-Patterns

| Don't | Why | Do Instead |
|-------|-----|------------|
| Pre-load entire file tree | Context explosion | Lazy load on expand |
| Show all evidence always | Cognitive overload | Show on hover/focus |
| Render 3D visualizations by default | Not text-first | Offer as optional view |
| Block text with UI | Violates semi-transparent | Use margins, overlays |
| Hide agent actions | Violates transparency | Show in annotations |
| Auto-expand deeply | Exceeds budget | Expand one level at a time |

---

## 14. Implementation Reference

### 14.1 File Locations

| Component | Location | Status |
|-----------|----------|--------|
| Outline model | `protocols/context/outline.py` | ✅ Complete |
| Parser (tokens) | `protocols/context/parser.py` | ✅ Complete |
| Lens system | `protocols/context/lens.py` | ✅ Complete |
| Collaboration | `protocols/context/collaboration.py` | ✅ Complete |
| Multi-surface renderer | `protocols/context/renderer.py` | ✅ Complete |
| Portal bridge | `protocols/context/portal_bridge.py` | ✅ Complete |
| PortalTree.tsx | `web/src/components/portal/PortalTree.tsx` | ✅ Complete |
| TrailPanel.tsx | `web/src/components/portal/TrailPanel.tsx` | ✅ Complete |
| Portal page | `web/src/pages/Portal.tsx` | ✅ Complete |
| CLI handler | `protocols/cli/handlers/context.py` | ✅ Complete |

### 14.2 AGENTESE Paths

| Path | Purpose | Status |
|------|---------|--------|
| `self.context.manifest` | Current focus, affordances | ✅ Implemented |
| `self.context.navigate` | Follow hyperedge | ✅ Implemented |
| `self.context.focus` | Jump to specific node | ✅ Implemented |
| `self.context.backtrack` | Go back one step | ✅ Implemented |
| `self.context.trail` | Get navigation trail | ✅ Implemented |
| `self.context.subgraph` | Extract reachable subgraph | ✅ Implemented |
| `self.explore.*` | Exploration harness (budget, evidence) | ✅ Implemented |
| `self.portal.*` | Portal token operations | ✅ Implemented |

### 14.3 Teaching Notes

**Gotcha: Outline operations are async**
```python
# All operations may involve I/O (loading content, persisting trail)
await outline_ops.expand(portal_path)  # Not expand(portal_path)
```

**Gotcha: TextSnippet metadata is invisible**
```python
# visible_text is what user sees
# source_path, copied_at, links are hidden but travel with copy/paste
snippet = TextSnippet(visible_text="Hello", source_path="auth.py")
# Clipboard carries metadata invisibly
```

**Gotcha: CollaborationProtocol has timing**
```python
# 2-second grace period after typing stops
# 5-second auto-accept for proposals
# These timings are intentional for UX flow
```

**Gotcha: Presence indicators are ephemeral**
```python
# Fade after 5s of no activity
# Don't persist presence to DB—it's transient state
```

---

## 15. Related Specs

- `spec/protocols/typed-hypergraph.md` — The conceptual model (81 tests)
- `spec/protocols/portal-token.md` — The UX abstraction layer (125 tests)
- `spec/protocols/exploration-harness.md` — Safety and evidence layer (110 tests)
- `spec/protocols/agentese.md` — The verb-first ontology
- `brainstorming/context-perception-v2.md` — **Next evolution: Cognitive Canvas**

---

## 16. Evolution: The Cognitive Canvas (V2)

> *"The outline was training wheels. Now we need the bicycle."*

Context Perception V1 (this spec) describes a **visualization layer**—turning hypergraph navigation into collapsible outlines. It works. The implementation is solid.

Context Perception V2 (see brainstorming doc) envisions a **cognitive space**—where navigation IS reasoning, and trails ARE proofs.

### V2 Core Thesis

Context Perception should be an **exocortex**—a shared cognitive space where human and agent think together. Not a document viewer. A **thinking space**.

### The Three Transformations (V1 → V2)

| V1 Concept | V2 Concept | What Changes |
|------------|------------|--------------|
| **Outline** (document) | **Attention Graph** (cognition) | Outline emerges from where observers are focused |
| **Portals** (expand/collapse) | **Reasoning Nodes** (claim + evidence) | Each expansion is an epistemic act with proof obligation |
| **Trail** (history) | **Proof Tree** (verifiable reasoning) | Trail connects to ASHC; decisions become verifiable |

### When to Evolve

V2 requires:
1. Attention primitives in outline model
2. Epistemic wrapper for portals
3. Proof tree integration with ASHC/Witness

Current implementation is **foundation for V2**, not obstacle to it. The layers compose.

---

*"It's just an outline. Copy-paste works. Links are clickable. Sections collapse. And somehow, it's also a distributed intelligence system."*

*"Soon: A distributed intelligence system that can prove why it did what it did."*
