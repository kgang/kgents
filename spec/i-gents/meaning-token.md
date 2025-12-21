# Meaning Token Frontend Architecture

**Status:** Standard
**Implementation:** `impl/claude/services/interactive_text/` (120 tests, tasks 1-7 complete)

## Purpose

Eliminate the concept of "frontend" as a separate concern. Instead: **meaning tokens** are the atomic unit of interface—semantic primitives that project to different rendering surfaces (CLI, TUI, Web, marimo, VR) through projection functors. Text files ARE interfaces.

> *"The noun is a lie. There is only the rate of change."*
> *"And the rate of change of a document IS its interactivity."*

## Core Insight

There is no frontend. There is no backend. There are only **meaning tokens** that project to whatever surface observes them. The CLI, web browser, marimo notebook, VR headset—these are not different applications. They are different **observers** receiving projections of the same semantic reality.

## The Radical Replacement

| Traditional Concept | Radical Replacement |
|---------------------|---------------------|
| React components | Meaning token projections |
| REST API routes | AGENTESE paths (protocol IS API) |
| State management | Document Polynomial + Sheaf coherence |
| CSS styling | Density-parameterized projection |
| Frontend/backend split | Metaphysical Fullstack (no split) |
| UI component library | Token affordance registry |
| Form handling | Token mutation with trace witnesses |

## Type Signatures

```python
@dataclass(frozen=True)
class MeaningToken(ABC, Generic[T]):
    """Semantic primitive that projects to renderings."""
    token_type: str
    source_text: str
    source_position: tuple[int, int]
    # Methods: get_affordances, project, on_interact

@dataclass(frozen=True)
class TokenDefinition:
    """Complete definition of a meaning token type."""
    name: str
    pattern: TokenPattern
    affordances: tuple[Affordance, ...]
    projectors: dict[str, str]  # target → projector module

class TokenRegistry:
    """Single source of truth for token definitions (AD-011)."""
    # Methods: register, get, recognize
    # Six core types: AGENTESEPath, TaskCheckbox, Image, CodeBlock,
    #                 PrincipleRef, RequirementRef

class DocumentPolynomial:
    """Document as polynomial functor: state × input → (new_state, output)."""
    positions = {VIEWING, EDITING, SYNCING, CONFLICTING}
    # Methods: directions(state) → valid_inputs, transition(state, input)

class DocumentSheaf:
    """Sheaf structure for multi-view coherence."""
    # Methods: overlap, compatible, verify_sheaf_condition, glue

class ProjectionFunctor(ABC, Generic[Target]):
    """Natural transformation: MeaningToken → Target-specific rendering."""
    # Methods: project_token, project_document, project_composition
    # Targets: CLI (Rich), TUI (Textual), Web (React), JSON (API), marimo
```

## Laws / Invariants

### Projection Functor Laws (Properties 3-5)
```
Composition:     P(A >> B) = P(A) >> P(B)  # Horizontal composition preserved
Naturality:      P(state_change(token)) = target_update(P(token))
Density:         project(token, density) differs appropriately by density
```

### Document Polynomial Laws (Properties 6-7)
```
Validity:        input ∈ directions(state) ↔ valid
Determinism:     Same (state, input) → same (new_state, output)
Event Emission:  Every state transition → DataBus event
```

### Document Sheaf Laws (Properties 8-9)
```
Coherence:       overlapping views agree on shared tokens
Gluing:          compatible views combine into global document
Propagation:     edit in any view → propagate to all views in <100ms
```

### Parser Laws (Properties 16, 21-22)
```
Roundtrip:       render(parse(doc)) ≡ doc  # Byte-identical
Robustness:      Malformed markdown → graceful handling, never crash
Localization:    Token modification → update only affected region
```

### Correctness Properties (22 total)
1. Token Recognition Completeness
2. Token Affordance Generation
3. Projection Functor Composition Law
4. Projection Naturality Condition
5. Density-Parameterized Projection
6. Document Polynomial State Validity
7. Document Polynomial Event Emission
8. Document Sheaf Coherence
9. Document Sheaf Propagation
10. AGENTESE Path Affordances
11. Ghost Token Rendering
12. Task Checkbox Toggle with Trace
13. Task Verification Integration
14. Image Token Graceful Degradation
15. Code Block Execution Sandboxing
16. Roundtrip Fidelity
17. Progressive Enhancement
18. Observer-Dependent Projection
19. Graceful Degradation
20. Cross-Jewel Event Coordination
21. Parser Robustness
22. Localized Token Modification

## The Semantic Layer Stack

```
L4: GESTURAL ─── paste, click, hover, drag (embodied interaction)
      │
L3: SEMANTIC ─── token patterns → affordance generators
      │
L2: STRUCTURAL ─ markdown AST with token extraction
      │
L1: TEXTUAL ──── valid markdown, git-diffable, readable anywhere

Each layer is a FUNCTOR. L4 ∘ L3 ∘ L2 ∘ L1 = Full Interactive Experience
But L1 alone is ALWAYS valid. Progressive enhancement, not degradation.
```

## Integration

### AGENTESE Paths
```
self.document.interactive        # Interactive text system
self.document.task.toggle        # Task checkbox with trace
self.document.task.trace         # View task trace
self.document.token.hover        # Token hover info
self.document.token.navigate     # Navigate to path's Habitat
world.trace.capture              # Trace witness for verification
```

### DataBus Event Wiring
```python
SYNERGY_WIRING = {
    "document.task_completed": [
        "self.verification.on_task_complete",  # Verification
        "world.trace.capture",                  # Trace witness
        "self.memory.crystallize",              # M-gent memory
    ],
    "document.image_added": [
        "self.document.image.analyze",
        "self.memory.associate",
    ],
}
```

## Token Types

| Token | Pattern | Primary Affordances |
|-------|---------|---------------------|
| AGENTESEPath | `` `world.house.manifest` `` | hover (state), click (navigate), drag (REPL) |
| TaskCheckbox | `- [x] Task` | click (toggle), hover (trace), verification link |
| Image | `![alt](path)` | hover (AI description), click (expand), drag (context) |
| CodeBlock | ` ```python ` | edit (syntax), run (sandbox), import |
| PrincipleRef | `§principle` | hover (text), click (navigate), verification |
| RequirementRef | `REQ-001` | hover (status), click (graph), trace link |

## Graceful Degradation

| Unavailable | Behavior |
|-------------|----------|
| LLM | Render tokens without AI affordances, show "requires connection" |
| Verification | Allow toggle, defer verification, reconcile on recovery |
| Network | Work with local file state |

All degradation uses sympathetic messaging per Alive Workshop aesthetic.

## Anti-Patterns

- **Building React components**: Use token projectors instead
- **State management libraries**: Document Polynomial + Sheaf replaces Redux/Zustand
- **Separate frontend codebase**: Projectors live with services
- **API routes**: AGENTESE paths are the API
- **CSS frameworks**: Density-parameterized projection replaces styling

## Crown Jewel Structure

```
services/interactive_text/
├── registry.py              # Token registry (single source of truth)
├── polynomial.py            # Document state machine
├── sheaf.py                 # Multi-view coherence
├── tokens/
│   ├── base.py              # MeaningToken base class
│   ├── agentese_path.py     # Portal to agent system
│   ├── task_checkbox.py     # Proof of completion
│   ├── image.py             # Multimodal context
│   ├── code_block.py        # Executable action
│   └── principle_ref.py     # Anchor to principles
├── projectors/
│   ├── base.py              # ProjectionFunctor base
│   ├── cli.py               # Rich terminal
│   ├── web.py               # React elements
│   └── json.py              # API response
└── agentese_nodes.py        # AGENTESE integration

impl/claude/web/             # NOT a frontend—a projection receiver
├── src/receiver.tsx         # ~50 lines, receives projections
├── src/observer.ts          # Web observer implementation
└── src/shell.tsx            # Minimal shell (routing from AGENTESE)
```

## Implementation Status

| Task | Status |
|------|--------|
| 1. Core interfaces | Complete |
| 2. Token registry + 6 core tokens | Complete |
| 3. Token tests | Complete |
| 4. Document Polynomial | Complete |
| 5. Document Sheaf | Complete |
| 6. Polynomial/Sheaf tests | Complete |
| 7. Projection Functors (CLI, Web, JSON) | Complete |
| 8. Parser with roundtrip fidelity | Not Started |
| 9-13. Integration + Layer Stack | Not Started |
| 14-16. Web receiver + Container Functor | Not Started |
| 17-18. Final wiring + Alive Workshop | Not Started |

**Total: 120 tests passing (tasks 1-7 complete)**

## Implementation Reference

See: `impl/claude/services/interactive_text/`

---

*"The text lives. The spec breathes. The document acts."*
