# Forest AGENTESE Week 2 Continuation

> *"The forest sings when plans become handles."*

## Invocation

```
/hydrate meta/forest-agentese continue from IMPLEMENT (Week 2: Adapter Skeleton)
```

**AGENTESE Guard**: `concept.forest.manifest[phase=IMPLEMENT][entropy=0.06][law_check=true][minimal_output=true]@span=forest_impl_week2`

**Prior State**: 60% complete. Doc-only phase done. Handle contracts specified in `agentese-path.md`. Dry-run prompts documented. QA passed.

**Next Action**: Create `impl/claude/protocols/agentese/contexts/forest.py` skeleton with ForestNode class.

---

## PHASE 6: IMPLEMENT (ACT) — Week 2

**Handle**: `world.code.manifest[phase=IMPLEMENT][minimal_output=true]@span=forest_skeleton`

### Intent

Create the ForestNode adapter skeleton that will eventually wire forest handles to the Logos resolver. This session produces stubs only—no live wiring until tests pass.

### Exit Criteria

- [ ] `forest.py` exists with ForestNode class (~200 lines)
- [ ] Five handle methods stubbed: `manifest`, `witness`, `sip`, `refine`, `define`
- [ ] Affordance gating by observer role (guest/meta/ops)
- [ ] Rollback token protocol for `refine`
- [ ] Factory function `create_forest_resolver()`
- [ ] Plan progress updated to 80%

### Non-Goals

- No live Logos wiring (defer to Week 3)
- No CLI changes
- No dashboard integration
- No actual _forest.md parsing (stub returns)

### Attention Budget

```
Primary (70%):    ForestNode class + 5 handle stubs
Secondary (20%):  Affordance gating + rollback protocol
Maintenance (5%): Cross-ref alignment with concept.py patterns
Accursed (5%):    void.forest.dream stub (exploratory)
```

---

## File Map

### Read First (Patterns)
```
impl/claude/protocols/agentese/contexts/concept.py    # ConceptNode pattern
impl/claude/protocols/agentese/contexts/self_.py      # SelfContextResolver pattern
impl/claude/protocols/agentese/contexts/__init__.py   # Factory wiring
```

### Write
```
impl/claude/protocols/agentese/contexts/forest.py     # NEW: ForestNode + resolver
```

### Update
```
plans/meta/forest-agentese-n-phase.md                 # Progress → 80%
```

---

## Implementation Skeleton

```python
"""
AGENTESE Forest Context Resolver

The Forest: plans as handles, epilogues as witnesses, dormant as accursed share.

forest.* handles resolve to planning artifacts that can be:
- Manifested (concept.forest.manifest) → canopy view
- Witnessed (time.forest.witness) → epilogue stream
- Sipped (void.forest.sip) → accursed share selection
- Refined (concept.forest.refine) → mutation with rollback
- Defined (self.forest.define) → JIT plan scaffold

Principle Alignment: Heterarchical, Composable, Minimal Output
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncIterator
from ..node import BaseLogosNode, BasicRendering, Renderable

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

# === Forest Affordances by Role ===
FOREST_ROLE_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "guest": ("manifest", "witness"),
    "meta": ("manifest", "witness", "refine", "sip", "define"),
    "ops": ("manifest", "witness", "refine", "sip", "define", "apply", "rollback", "lint"),
    "default": ("manifest",),
}

@dataclass
class ForestNode(BaseLogosNode):
    """Forest context node for plan handle operations."""
    _handle: str = "concept.forest"
    # Stub: actual impl will inject these
    _forest_path: str = "plans/_forest.md"
    _epilogues_path: str = "plans/_epilogues"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return role-gated affordances."""
        return FOREST_ROLE_AFFORDANCES.get(archetype, FOREST_ROLE_AFFORDANCES["default"])

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Stub: Return forest canopy view."""
        # TODO: Parse _forest.md and return ForestManifest
        return BasicRendering(
            summary="Forest Canopy",
            content="[Stub] Forest manifest not yet wired",
            metadata={"status": "stub", "plan_count": 0},
        )

    async def _invoke_aspect(self, aspect: str, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Any:
        match aspect:
            case "manifest":
                return await self.manifest(observer)
            case "witness":
                return await self._witness(observer, **kwargs)
            case "sip":
                return await self._sip(observer, **kwargs)
            case "refine":
                return await self._refine(observer, **kwargs)
            case "define":
                return await self._define(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _witness(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        """Stub: Stream epilogues."""
        # TODO: Yield epilogues from _epilogues/*.md
        yield {"handle": "time.forest.witness.stub", "status": "stub"}

    async def _sip(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """Stub: Select dormant plan for accursed share."""
        entropy_budget = kwargs.get("entropy_budget", 0.07)
        return {
            "selected_plan": "agents/t-gent",  # Stub
            "rationale": "[Stub] Longest dormant",
            "entropy_spent": entropy_budget,
            "entropy_remaining": 0.0,
        }

    async def _refine(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """Stub: Propose mutation with rollback token."""
        import uuid
        return {
            "rollback_token": str(uuid.uuid4()),  # REQUIRED
            "preview": {"status": "stub"},
            "law_check": {"identity": "pass", "associativity": "pass"},
            "applied": False,
        }

    async def _define(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """Stub: JIT plan scaffold."""
        return {
            "status": "stub",
            "draft_header": "---\npath: new-plan\nstatus: draft\nprogress: 0\n---",
        }

# === Factory ===
def create_forest_resolver() -> ForestNode:
    """Create a ForestNode with standard configuration."""
    return ForestNode()
```

---

## Ledger Update (at session end)

```yaml
phase_ledger:
  IMPLEMENT: touched  # reason: forest.py skeleton created
entropy:
  planned: 0.08
  spent: 0.06  # +0.02 this session
  returned: 0.02
```

---

## QA Checklist (before exit)

- [ ] ForestNode extends BaseLogosNode
- [ ] All 5 handle methods present (manifest, witness, sip, refine, define)
- [ ] Affordance gating uses FOREST_ROLE_AFFORDANCES dict
- [ ] `_refine` returns rollback_token (REQUIRED)
- [ ] `_witness` returns AsyncIterator (not array)
- [ ] `_sip` returns single selection (not list)
- [ ] Factory function exported
- [ ] Mypy passes: `uv run mypy impl/claude/protocols/agentese/contexts/forest.py`

---

## Next Phase Prompt (Week 3: Live Wiring)

```
/hydrate meta/forest-agentese continue from IMPLEMENT (Week 3: Live Wiring)

Prior: 80% complete. ForestNode skeleton created. Stubs return placeholders.
Next: Wire ForestNode to Logos resolver, implement real _forest.md parsing.
Handle: concept.forest.manifest[phase=IMPLEMENT][law_check=true]@span=forest_wiring
```

---

## Entropy Accounting

```
Session start:  spent=0.04, remaining=0.04
Session budget: 0.02 (conservative for skeleton)
Session end:    spent=0.06, remaining=0.02
Pour unused at REFLECT if skeleton completes early.
```

---

*"Plans as handles. Epilogues as witnesses. The forest becomes AGENTESE-native."*
