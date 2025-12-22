# Portal Tokens

**Status:** ✅ Complete (Phases 1-5 delivered, 125+ tests passing)
**Date:** 2025-12-22
**Derives From:** `brainstorming/context-management-agents.md` Parts 4, 10

---

## Epigraph

> *"You don't go to the document. The document comes to you."*
>
> *"Navigation is expansion. Expansion is navigation."*

---

## 1. Overview

Portal tokens are **meaning tokens** that represent expandable hyperedges in the typed-hypergraph. Instead of navigating away to a linked document, the agent **expands it inline** as a collapsible section.

The experience of "opening a doc inside another doc" is the experience of **opening a meaning token**.

---

## 2. The Critical UX Insight

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  auth_middleware.py                                                          │
│                                                                             │
│  def validate_token(token: str) -> bool:                                    │
│      """Validate JWT token."""                                              │
│      ...                                                                    │
│                                                                             │
│  ▶ [tests] ──→ 3 files                     ← COLLAPSED (click to expand)   │
│                                                                             │
│  ▼ [implements] ──→ auth_spec.md           ← EXPANDED                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  # Authentication Specification                                         ││
│  │                                                                         ││
│  │  ## Token Validation                                                    ││
│  │  Tokens MUST be validated according to RFC 7519...                      ││
│  │                                                                         ││
│  │  ▶ [derived_from] ──→ RFC_7519          ← NESTED COLLAPSED              ││
│  │  ▶ [evidence] ──→ 2 items                                               ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ▶ [calls] ──→ jwt_utils.py                                                 │
│  ▶ [evidence] ──→ security_claims/                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

Key properties:
- **Inline expansion** — content appears nested, not navigated to
- **Recursive** — expanded content reveals more portals
- **Lazy** — content loads only on expansion
- **Reversible** — collapse to hide detail

---

## 3. The Portal Token

### 3.1 Definition

```python
@dataclass
class PortalExpansionToken(MeaningToken):
    """
    A meaning token representing an expandable hyperedge.

    When COLLAPSED: Shows edge type and destination count
    When EXPANDED: Renders destination document(s) inline
    """

    token_type: str = "portal_expansion"

    # The hyperedge
    source_path: str          # "world.auth_middleware"
    edge_type: str            # "tests"
    destinations: list[str]   # ["world.test_auth", ...]

    # State
    expanded: bool = False
    depth: int = 0            # Nesting level

    # Lazy content
    _content: dict[str, str] | None = None
```

### 3.2 Rendering

```python
def render_collapsed(self) -> str:
    count = len(self.destinations)
    noun = "file" if count == 1 else "files"
    return f"▶ [{self.edge_type}] ──→ {count} {noun}"

def render_expanded(self) -> str:
    lines = [f"▼ [{self.edge_type}] ──→ {len(self.destinations)} files"]
    for dest in self.destinations:
        content = self._content.get(dest, "Loading...")
        lines.append(indent(content, self.depth + 1))
    return "\n".join(lines)
```

---

## 4. The State Machine

Portal tokens have a state machine for expansion:

```
         Expand()              ContentLoaded()
COLLAPSED ───────→ LOADING ─────────────────→ EXPANDED
    ↑                                            │
    │              Collapse()                    │
    └────────────────────────────────────────────┘
```

### 4.1 States

| State | Description |
|-------|-------------|
| `COLLAPSED` | Shows summary: `▶ [tests] ──→ 3 files` |
| `LOADING` | Fetching content |
| `EXPANDED` | Content visible, nested portals exposed |
| `ERROR` | Load failed |

### 4.2 Transitions

```python
async def transition(self, state: str, input: PortalInput) -> tuple[str, PortalOutput]:
    match (state, input):
        case ("COLLAPSED", Expand()):
            asyncio.create_task(self._load_destinations())
            return ("LOADING", LoadingStarted())

        case ("LOADING", ContentLoaded(content)):
            self._content = content
            self.expanded = True
            self._record_in_trail()  # Navigation event!
            return ("EXPANDED", ExpansionComplete(content))

        case ("EXPANDED", Collapse()):
            self.expanded = False
            return ("COLLAPSED", Collapsed())

        case ("LOADING", LoadError(err)):
            return ("ERROR", ErrorOccurred(err))
```

---

## 5. The Portal Tree

Documents contain portals. Expanded portals reveal more portals. This creates a **tree of expansions**:

```python
@dataclass
class PortalTree:
    """
    The tree of expanded portals IS the agent's current view.
    """

    @dataclass
    class PortalNode:
        path: str
        edge_type: str | None  # None for root
        expanded: bool
        children: list["PortalNode"]
        depth: int

    root: PortalNode
    max_depth: int = 5  # Prevent infinite expansion

    def expand(self, portal_path: list[str]) -> "PortalTree":
        """Expand portal at path (e.g., ["tests", "covers"])."""

    def collapse(self, portal_path: list[str]) -> "PortalTree":
        """Collapse portal, hiding children."""

    def to_trail(self) -> Trail:
        """DFS of expanded nodes = trail of exploration."""

    def render(self) -> str:
        """Render as nested collapsible sections."""
```

The tree structure IS:
- The **current view** (what's visible)
- The **trail** (how we got here)
- The **context** (what's "open")
- The **evidence** (what we explored)

---

## 6. The Portal Open Signal

When a portal expands, it emits a signal:

```python
@dataclass
class PortalOpenSignal:
    """
    Signal emitted when portal expands.

    Tells the system:
    1. Which file(s) are now "open"
    2. The edge type that led here
    3. The nesting depth
    4. The parent context
    """

    paths_opened: list[str]
    edge_type: str
    parent_path: str
    depth: int
    timestamp: datetime

    def to_context_event(self) -> ContextEvent:
        return ContextEvent(
            type="files_opened",
            paths=self.paths_opened,
            reason=f"Followed [{self.edge_type}] from {self.parent_path}",
            depth=self.depth,
        )
```

This signal:
- Updates agent context (these files are now "open")
- Records in trail (navigation happened)
- Creates weak evidence (exploration fact)

---

## 7. Affordances

Every portal shows its destinations before expansion:

```
▶ [tests] ──→ 3 files              # I can see there are 3 test files
▶ [implements] ──→ auth_spec.md    # I can see it implements a spec
▶ [evidence] ──→ 5 items           # I can see there's evidence
```

The agent sees what's *possible* before committing to explore:
- "3 test files might be worth expanding"
- "5 evidence items — I should look"
- "Only 1 spec — quick to check"

---

## 8. Multi-Surface Rendering

### 8.1 CLI

```
▶ [tests] ──→ 3 files
▼ [implements] ──→ auth_spec.md
┌────────────────────────────────────
│ # Authentication Specification
│
│ ## Token Validation
│ Tokens MUST be validated...
│
│ ▶ [derived_from] ──→ RFC_7519
└────────────────────────────────────
```

### 8.2 Web (HTML)

```html
<details data-portal-path="world.auth_middleware.tests"
         data-edge-type="tests"
         data-depth="1">
    <summary>▶ [tests] ──→ 3 files</summary>
    <div class="portal-content">
        <!-- Lazy loaded -->
    </div>
</details>
```

### 8.3 LLM Context

```xml
<!-- PORTAL: tests (EXPANDED, depth=1) -->
<file path="test_auth.py">
def test_token_expiry():
    ...
</file>
<!-- END PORTAL -->
```

### 8.4 Markdown

```markdown
> ▼ [tests] ──→ test_auth.py
> > ```python
> > def test_token_expiry():
> >     ...
> > ```
```

---

## 9. Literate Exploration

Portal tokens enable **literate exploration** — the investigation document IS the exploration:

```markdown
# Investigation: Auth Bug

I started at `auth_middleware.py`:

▼ [tests] ──→ test_auth.py
┌────────────────────────────────────────
│ def test_token_expiry():
│     """Token should expire after 1 hour."""
│     token = create_token(expires_in=3600)
│
│     ▼ [covers] ──→ validate_token
│     ┌────────────────────────────────
│     │ def validate_token(token):
│     │     # BUG: Using < instead of <=
│     │     if token.exp < now():  # ← FOUND IT
│     │         return False
│     └────────────────────────────────
└────────────────────────────────────────

The trail of expansions documents my investigation.
Collapsing hides detail. Expanding reveals it.
The document IS the exploration.
```

---

## 10. Integration Points

### 10.1 With Typed-Hypergraph

Portal tokens are the **UX projection** of hyperedge traversal:
- Hyperedge in graph → Portal token in document
- Navigate in graph → Expand in document
- Trail in graph → Tree of expansions

### 10.2 With ASHC Evidence

Opening a portal creates evidence:

```python
async def record_open(self, signal: PortalOpenSignal) -> Evidence:
    return Evidence(
        claim=f"Explored {signal.edge_type} of {signal.parent_path}",
        source="portal_expansion",
        strength="weak",  # Exploration, not conclusion
        content={"opened": signal.paths_opened, "depth": signal.depth},
    )
```

### 10.3 With Token State Machines

Portal tokens ARE token state machines (from Part 4):
- Every portal has states (COLLAPSED, LOADING, EXPANDED)
- State transitions are events
- Events are recorded, replayable

---

## 11. The Unification

```
TYPED-HYPERGRAPH (conceptual)
        │
        │  "Follow this hyperedge"
        ▼
PORTAL TOKEN (UX)
        │
        │  "Expand this collapsible section"
        ▼
TOKEN STATE MACHINE (operational)
        │
        │  "COLLAPSED → LOADING → EXPANDED"
        ▼
TRAIL (persistence)
        │
        │  "Record expansion in trail"
        ▼
ASHC EVIDENCE (commitment)
        │
        │  "Exploration creates evidence"
        ▼
AGENT CONTEXT
        │
        └──→ "These files are now 'open'"
```

---

## 12. Laws

### 12.1 Expansion Idempotence

Expanding an already-expanded portal is a no-op:
```
expand(expand(portal)) ≡ expand(portal)
```

### 12.2 Collapse Inverse

Collapsing then expanding returns to expanded state:
```
expand(collapse(expand(portal))) ≡ expand(portal)
```

### 12.3 Depth Boundedness

Portal expansion depth is bounded:
```
depth(portal) ≤ max_depth  (default: 5)
```

---

## 13. Implementation Roadmap

### Phase Summary

| Phase | Name | Status | Sessions | Tests |
|-------|------|--------|----------|-------|
| 1 | Core Token Implementation | ✅ Complete | 2 | 43 |
| 2 | AGENTESE & Exploration Harness | ✅ Complete | 2 | 34 |
| 3 | Context Bridge & SynergyBus | ✅ Complete | 1 | 22 |
| 4 | Source File Integration | ✅ Complete | 1 | 26 |
| 5 | Frontend Components | 🔲 Planned | 2-3 | — |
| 6 | Trail Persistence & Witness | 🔲 Planned | 1-2 | — |

**Total:** 125 tests passing (Phases 1-4)

---

### Phase 4: Source File Integration ✅

> *"Portal tokens should work on real code, not just .op files."*

**Status:** ✅ Complete (2025-12-22)

**Goal:** Extend portal tokens to work with source files (`.py`, `.ts`, `.md`) using the existing typed-hypergraph resolvers.

**Dependencies:** Phases 1-3, `hyperedge_resolvers.py`

**Key Insight:** The hyperedge resolvers (`imports`, `calls`, `tests`, `covers`) already exist. This phase bridges them to portal token generation.

#### Implementation Summary

**Files Created:**
- `protocols/file_operad/source_portals.py` — SourcePortalDiscovery, SourcePortalLink, SourcePortalToken
- `protocols/file_operad/_tests/test_source_portals.py` — 26 tests
- `protocols/cli/handlers/portal.py` — CLI handler

**Key Components:**
- `SourcePortalLink.from_hyperedge()` — Bridge from ContextNode to PortalLink
- `SourcePortalDiscovery.discover_portals()` — Async discovery using hyperedge resolvers
- `build_source_portal_tree()` — Build navigable tree from source file
- `render_portals_cli()` — CLI output formatting

#### Session 4.1: Source File Portal Discovery ✅

- [x] Create `protocols/file_operad/source_portals.py`
- [x] Implement `discover_portals(file_path: Path) -> list[PortalLink]`
  - [x] Parse Python files with AST for imports/calls
  - [x] Find corresponding test files via naming convention
  - [x] Find spec files via `implements` resolver pattern
- [x] Add `file_type` field to `PortalLink` for source vs operad distinction
- [x] Tests: `test_source_portals.py` (26 tests)

#### Session 4.2: Hyperedge Resolver Integration ✅

- [x] Import resolvers from `hyperedge_resolvers.py`
- [x] Create `PortalLink.from_hyperedge(edge_type, destinations)` factory
- [x] Wire `ContextNode.edges()` → `PortalTree` child generation
- [x] Ensure lazy resolution (don't load content until expanded)
- [x] Tests: observer-dependent visibility, lazy loading

#### Session 4.3: CLI Integration ✅

- [x] Create `protocols/cli/handlers/portal.py`
- [x] Implement `kg portal <file>` — show portals for file
- [x] Implement `kg portal expand <file> <edge>` — expand portal
- [x] Implement `kg portal tree <file>` — show full tree
- [x] Register in `hollow.py` command registry

**Verification:**
```bash
# This works on any Python file
kg portal impl/claude/services/brain/persistence.py
# Output:
# ▶ [tests] ──→ 2 files
# ▶ [imports] ──→ 5 modules
# ▶ [implements] ──→ brain-spec.md
```

---

### Phase 5: Frontend Components ✓

> *"The web UI needs portal expansion too."*

**Status:** COMPLETE (2025-12-22)

**Goal:** React components for portal tree rendering with lazy expansion.

**Dependencies:** Phase 4 (for real file support), existing AGENTESE API patterns

#### Session 5.1: PortalTree Component ✓

Build the main tree visualization component.

- [x] Create `web/src/components/portal/PortalTree.tsx`
- [x] Implement recursive tree rendering with click-to-expand pattern
- [x] Add loading states (COLLAPSED → LOADING → EXPANDED → ERROR)
- [x] Style with existing design system (Lucide icons, Living Earth palette)
- [ ] Tests: Component tests with React Testing Library (DEFERRED)

#### Session 5.2: AGENTESE API Wiring ✓

Connect frontend to backend via AGENTESE.

- [x] Create `web/src/api/portal.ts` with hooks:
  - [x] `usePortalTree(rootPath)` — fetch initial tree
  - [x] `expand(portalPath)` — mutation for expansion
  - [x] `collapse(portalPath)` — mutation for collapse
- [x] Wire to `self.portal.manifest`, `self.portal.expand`, etc.
- [x] Add optimistic updates for snappy UX
- [x] Handle errors gracefully (show ERROR state with message)
- [ ] Tests: API integration tests (DEFERRED)

#### Session 5.3: Portal Page & Navigation ✓

Create dedicated portal exploration page.

- [x] Create `web/src/pages/Portal.tsx`
- [x] Add route `/_/portal` to navigation
- [x] Implement file picker to select root
- [x] Show trail breadcrumbs (expansion path)
- [ ] Add "Export Trail" button (DEFERRED to Phase 6)
- [ ] Tests: E2E tests for portal navigation (DEFERRED)

**Delivered:**
- `web/src/components/portal/PortalTree.tsx` — Recursive tree with expand/collapse
- `web/src/api/portal.ts` — AGENTESE hooks with optimistic updates
- `web/src/pages/Portal.tsx` — Dedicated exploration page with file picker
- Route: `/_/portal` — Developer gallery for portal exploration
- TypeScript types for portal tree structures

---

### Phase 6: Trail Persistence & Witness

> *"Exploration should be auditable and replayable."*

**Goal:** Persist portal exploration trails via Witness, enable replay.

**Dependencies:** Phase 4, Witness service (`services/witness/`)

#### Session 6.1: Trail Persistence (~2 hrs)

Wire `PortalTree.to_trail()` to Witness storage.

- [ ] Add `witness.mark()` call on significant expansions (depth > 1)
- [ ] Create `protocols/exploration/trail_persistence.py`
- [ ] Implement `save_trail(trail: Trail) -> str` (returns trail_id)
- [ ] Implement `load_trail(trail_id: str) -> Trail`
- [ ] Store trails with metadata (observer, timestamp, root file)
- [ ] Tests:
  - [ ] Test trail save/load roundtrip
  - [ ] Test mark emission on expansion

#### Session 6.2: Trail Replay (~2 hrs)

Reconstruct portal tree state from saved trail.

- [ ] Implement `PortalTree.from_trail(trail: Trail) -> PortalTree`
- [ ] Replay expansion sequence to rebuild tree
- [ ] Add `kg portal replay <trail_id>` command
- [ ] Handle missing files gracefully (mark as ERROR)
- [ ] Tests:
  - [ ] Test replay reconstructs tree
  - [ ] Test replay with missing files
  - [ ] Test replay preserves expansion order

**Exit Criteria:**
```bash
# Save exploration
kg portal tree auth_middleware.py --save
# Trail saved: trail-abc123

# Later, replay
kg portal replay trail-abc123
# Reconstructs exact portal tree state
```

---

### Future Considerations (Not Scoped)

These are ideas that may become phases later:

- **Observer-Dependent Portals:** Show different portals for different archetypes (developer sees `tests`, security auditor sees `auth_flows`)
- **Portal Search:** `kg portal search "token validation"` — find portals by content
- **Collaborative Portals:** Multiple agents share portal tree state
- **Portal Annotations:** Add notes to specific portals during exploration
- **Portal Heatmaps:** Visualize which portals are most frequently expanded

---

## 14. Related Specs

- `spec/protocols/typed-hypergraph.md` — The conceptual model
- `spec/protocols/exploration-harness.md` — Safety and evidence
- `spec/protocols/agentese.md` — The verb-first ontology

---

*"Navigation is expansion. Expansion is navigation. The document IS the exploration."*
