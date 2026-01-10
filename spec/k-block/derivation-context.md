# K-Block Derivation Context: Constitutional Grounding at Birth

> *"Every K-Block is born with a lineage, even if orphaned. The context IS the meaning."*

**Status**: Draft
**Implementation**: `impl/claude/services/k_block/derivation/`
**Prerequisites**: `spec/protocols/k-block.md`, `spec/protocols/derivation-framework.md`, `spec/principles/CONSTITUTION.md`
**Heritage**: Galois Modularization (loss theory), Derivation Framework (confidence propagation), Zero Seed (axiom grounding)

---

## Purpose

K-Blocks are transactional editing boundaries. But a K-Block without grounding is just floating content. This specification adds **derivation context** to every K-Block, establishing its relationship to the Constitutional hierarchy.

**The Core Insight**: Every K-Block should know where it comes from. Orphaned content can exist, but the system surfaces opportunities for grounding. Grounded content participates in the trust network.

---

## Core Insight

```
Every K-Block carries derivation_context: its relationship to Constitutional principles.

Grounding Status = f(galois_loss, source_principle, derivation_path)
Trust = f(grounding_status, parent_confidence, witnesses)
```

---

## Type Signatures

### The Derivation Context Schema

```typescript
interface KBlockDerivationContext {
  // Source: Which Constitutional principle grounds this K-Block?
  source_principle: ConstitutionalPrinciple | null;

  // Galois Loss: How much structure is lost in the derivation?
  galois_loss: number;  // [0.0, 1.0] — lower is better

  // Grounding Status: Computed from source_principle + galois_loss
  grounding_status: 'grounded' | 'provisional' | 'orphan';

  // Lineage: Parent K-Block in the derivation DAG
  parent_kblock_id: string | null;

  // Path: The full derivation path from CONSTITUTION
  derivation_path_id: string | null;

  // Witnesses: Evidence for this derivation
  witnesses: DerivationWitness[];
}

interface ConstitutionalPrinciple {
  name: string;  // "Tasteful", "Composable", "Generative", etc.
  layer: 'L0' | 'L1' | 'L2';  // CONSTITUTION layer (Irreducibles, Primitives, Derived)
  path: string;  // AGENTESE path: "void.principle.composable"
}

interface DerivationWitness {
  mark_id: string;           // Witness mark proving the connection
  witness_type: 'creation' | 'validation' | 'challenge' | 'refinement';
  timestamp: string;         // ISO 8601
  actor: string;             // "Kent", "Claude", "system"
  galois_loss_at_witness: number;  // Loss when witnessed
}

interface DerivationPath {
  id: string;
  root: 'CONSTITUTION';      // All paths root here
  segments: DerivationSegment[];
  total_galois_loss: number; // Accumulated loss along path
}

interface DerivationSegment {
  from_kblock_id: string;
  to_kblock_id: string;
  edge_type: 'derives_from' | 'refines' | 'extends' | 'contradicts';
  galois_loss: number;       // Loss for this segment
}
```

### Python Dataclass (Implementation Reference)

```python
@dataclass(frozen=True)
class KBlockDerivationContext:
    """
    Constitutional grounding context for K-Blocks.

    Every K-Block carries this context, even if orphaned.
    """

    source_principle: str | None           # Principle name or None
    galois_loss: float                     # [0.0, 1.0]
    grounding_status: GroundingStatus      # Computed
    parent_kblock_id: str | None
    derivation_path_id: str | None
    witnesses: tuple[DerivationWitness, ...]

    @classmethod
    def orphan(cls) -> "KBlockDerivationContext":
        """Create default orphan context for new K-Blocks."""
        return cls(
            source_principle=None,
            galois_loss=1.0,  # Maximum loss = no grounding
            grounding_status=GroundingStatus.ORPHAN,
            parent_kblock_id=None,
            derivation_path_id=None,
            witnesses=(),
        )


class GroundingStatus(Enum):
    """
    Grounding status is COMPUTED from galois_loss + source_principle.

    Law 4: This status is never directly asserted.
    """
    GROUNDED = "grounded"       # Connected to CONSTITUTION with L < 0.30
    PROVISIONAL = "provisional" # Connected but L >= 0.30
    ORPHAN = "orphan"           # No connection to CONSTITUTION
```

---

## Laws/Invariants

### Law 1: Universal Presence

```
forall kblock K:
  K.derivation_context is not None

Every K-Block has a derivation_context, even if orphaned.
```

### Law 2: DAG Structure

```
The derivation paths form a Directed Acyclic Graph (DAG) rooted at CONSTITUTION.

forall path P:
  P.root == CONSTITUTION
  not exists_cycle(P)

There is exactly one root: CONSTITUTION. No cycles allowed.
```

### Law 3: Galois Loss Accumulation

```
forall derivation_path P with segments [s1, s2, ..., sn]:
  P.total_galois_loss = sum(si.galois_loss for si in segments)

Loss accumulates additively along derivation paths.
The further from CONSTITUTION, the higher the potential loss.
```

### Law 4: Computed Grounding Status

```
forall kblock K:
  K.derivation_context.grounding_status = compute_status(
    K.derivation_context.source_principle,
    K.derivation_context.galois_loss
  )

where compute_status(principle, loss) =
  | principle is None          -> ORPHAN
  | principle is Some and loss < 0.30  -> GROUNDED
  | principle is Some and loss >= 0.30 -> PROVISIONAL

Grounding status is derived, never directly set.
```

### Law 5: Witness Requirement

```
forall transition T from status S1 to S2 where S2 != S1:
  exists witness W such that W proves T

Status changes must be witnessed.
```

---

## Initialization Defaults

### New K-Block Creation

When a K-Block is created, it starts in the **orphan** state:

```python
async def create_kblock(
    path: str,
    content: str,
    kind: KBlockKind = KBlockKind.FILE,
) -> KBlock:
    """Create a new K-Block with default orphan context."""

    # All K-Blocks start as orphans
    context = KBlockDerivationContext.orphan()

    kblock = KBlock(
        id=generate_kblock_id(),
        path=path,
        kind=kind,
        content=content,
        base_content=content,
        derivation_context=context,  # NEW FIELD
    )

    # System suggests grounding based on content analysis
    suggestions = await suggest_grounding(kblock)

    return kblock, suggestions
```

### Grounding Suggestion

The system analyzes content and suggests Constitutional grounding:

```python
async def suggest_grounding(kblock: KBlock) -> list[GroundingSuggestion]:
    """
    Analyze K-Block content and suggest Constitutional grounding.

    Uses Galois loss to find the lowest-loss principle connection.
    """
    suggestions = []

    for principle in CONSTITUTIONAL_PRINCIPLES:
        # Compute loss between content and principle
        loss = await compute_galois_loss(kblock.content, principle.content)

        if loss < 0.70:  # Only suggest if reasonably related
            suggestions.append(GroundingSuggestion(
                principle=principle,
                galois_loss=loss,
                suggested_status=GroundingStatus.GROUNDED if loss < 0.30 else GroundingStatus.PROVISIONAL,
                confidence=1.0 - loss,
            ))

    # Sort by loss (lowest first)
    return sorted(suggestions, key=lambda s: s.galois_loss)
```

### User Response Options

When suggestions are presented, users can:

1. **Accept** - Connect K-Block to suggested principle
2. **Modify** - Connect to a different principle
3. **Skip** - Leave as orphan (can ground later)

```python
async def accept_grounding(
    kblock: KBlock,
    suggestion: GroundingSuggestion,
    actor: str,
) -> KBlock:
    """User accepts a grounding suggestion."""

    # Create witness mark
    mark = await witness.mark(
        action="kblock.grounding.accept",
        target=kblock.id,
        metadata={
            "principle": suggestion.principle.name,
            "galois_loss": suggestion.galois_loss,
        },
    )

    # Update derivation context
    new_context = KBlockDerivationContext(
        source_principle=suggestion.principle.name,
        galois_loss=suggestion.galois_loss,
        grounding_status=suggestion.suggested_status,
        parent_kblock_id=None,  # Direct connection to CONSTITUTION
        derivation_path_id=await create_derivation_path(kblock, suggestion.principle),
        witnesses=(DerivationWitness(
            mark_id=mark.id,
            witness_type="creation",
            timestamp=now_iso(),
            actor=actor,
            galois_loss_at_witness=suggestion.galois_loss,
        ),),
    )

    return replace(kblock, derivation_context=new_context)
```

---

## State Transitions

### Transition Diagram

```
                    ┌─────────────────────────────────────────────────┐
                    │                                                 │
                    │   [Upstream changes increase L to >= 0.30]      │
                    │                                                 │
                    ▼                                                 │
┌──────────────┐   accept_grounding(L < 0.30)   ┌───────────────┐    │
│              │ ────────────────────────────► │               │ ───┘
│    ORPHAN    │                               │   GROUNDED    │
│              │ ◄─────────────────────────── │               │
└──────────────┘   disconnect() or L >= 0.70   └───────────────┘
       │                                              ▲
       │                                              │
       │  accept_grounding(L >= 0.30)                 │  improve_loss(L < 0.30)
       │                                              │
       ▼                                              │
┌──────────────┐                               ┌──────┴────────┐
│              │ ─────────────────────────────►│               │
│ PROVISIONAL  │    improve_loss(L < 0.30)     │   GROUNDED    │
│              │ ◄────────────────────────────│               │
└──────────────┘   upstream_change(L >= 0.30)  └───────────────┘
```

### Transition Rules

```python
class GroundingTransition:
    """Rules for grounding status transitions."""

    @staticmethod
    def compute_new_status(
        current: KBlockDerivationContext,
        new_loss: float,
        has_principle: bool,
    ) -> GroundingStatus:
        """
        Compute new grounding status based on loss and principle.

        Law 4: Status is computed, not asserted.
        """
        if not has_principle:
            return GroundingStatus.ORPHAN

        if new_loss < 0.30:
            return GroundingStatus.GROUNDED
        else:
            return GroundingStatus.PROVISIONAL

    @staticmethod
    def validate_transition(
        old_status: GroundingStatus,
        new_status: GroundingStatus,
        event: str,
    ) -> bool:
        """Validate that the transition is legal."""

        valid_transitions = {
            (GroundingStatus.ORPHAN, GroundingStatus.PROVISIONAL): {"accept_grounding"},
            (GroundingStatus.ORPHAN, GroundingStatus.GROUNDED): {"accept_grounding"},
            (GroundingStatus.PROVISIONAL, GroundingStatus.GROUNDED): {"improve_loss"},
            (GroundingStatus.GROUNDED, GroundingStatus.PROVISIONAL): {"upstream_change"},
            (GroundingStatus.GROUNDED, GroundingStatus.ORPHAN): {"disconnect"},
            (GroundingStatus.PROVISIONAL, GroundingStatus.ORPHAN): {"disconnect"},
        }

        key = (old_status, new_status)
        return event in valid_transitions.get(key, set())
```

### Loss Improvement

When content is refined, loss may decrease:

```python
async def on_kblock_edit(kblock: KBlock, delta: EditDelta) -> KBlock:
    """Recompute derivation context after edit."""

    if kblock.derivation_context.source_principle is None:
        return kblock  # Orphans don't recompute

    # Recompute Galois loss against source principle
    new_content = apply_delta(kblock.content, delta)
    principle = get_principle(kblock.derivation_context.source_principle)
    new_loss = await compute_galois_loss(new_content, principle.content)

    # Compute new status
    new_status = GroundingTransition.compute_new_status(
        kblock.derivation_context,
        new_loss,
        has_principle=True,
    )

    # Create witness if status changed
    witnesses = list(kblock.derivation_context.witnesses)
    if new_status != kblock.derivation_context.grounding_status:
        mark = await witness.mark(
            action="kblock.grounding.transition",
            target=kblock.id,
            metadata={
                "old_status": kblock.derivation_context.grounding_status.value,
                "new_status": new_status.value,
                "old_loss": kblock.derivation_context.galois_loss,
                "new_loss": new_loss,
            },
        )
        witnesses.append(DerivationWitness(
            mark_id=mark.id,
            witness_type="refinement",
            timestamp=now_iso(),
            actor="system",
            galois_loss_at_witness=new_loss,
        ))

    return replace(kblock, derivation_context=replace(
        kblock.derivation_context,
        galois_loss=new_loss,
        grounding_status=new_status,
        witnesses=tuple(witnesses),
    ))
```

---

## Integration with K-Block

### Schema Extension

The existing K-Block schema (from `spec/protocols/k-block.md`) gains one field:

```python
@dataclass
class KBlock:
    """K-Block with derivation context."""

    # Existing fields (from k-block.md)
    id: str
    path: str
    kind: KBlockKind
    content: str
    base_content: str
    isolation: IsolationState

    # Zero Seed fields (from kblock-unification.md)
    zero_seed_layer: int | None
    zero_seed_kind: str | None
    # ... other zero seed fields

    # NEW: Derivation context
    derivation_context: KBlockDerivationContext
```

### Backward Compatibility

For existing K-Blocks without derivation_context:

```python
def migrate_kblock(kblock_dict: dict) -> KBlock:
    """Migrate K-Block data to include derivation context."""

    if "derivation_context" not in kblock_dict:
        kblock_dict["derivation_context"] = KBlockDerivationContext.orphan().to_dict()

    return KBlock.from_dict(kblock_dict)
```

---

## AGENTESE Paths

Derivation operations are exposed under `self.kblock.derivation.*`:

```python
@node("self.kblock.derivation", dependencies=("kblock_service", "derivation_registry", "witness"))
class KBlockDerivationNode:
    """AGENTESE integration for K-Block derivation operations."""

    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer, block_id: str) -> DerivationManifest:
        """Get derivation context for a K-Block."""
        ...

    @aspect(category=AspectCategory.MUTATION)
    async def ground(
        self,
        observer: Observer,
        block_id: str,
        principle: str,
    ) -> GroundingResult:
        """Ground a K-Block to a Constitutional principle."""
        ...

    @aspect(category=AspectCategory.MUTATION)
    async def disconnect(self, observer: Observer, block_id: str) -> KBlock:
        """Disconnect K-Block from its grounding (make orphan)."""
        ...

    @aspect(category=AspectCategory.PERCEPTION)
    async def suggest(self, observer: Observer, block_id: str) -> list[GroundingSuggestion]:
        """Get grounding suggestions for a K-Block."""
        ...

    @aspect(category=AspectCategory.PERCEPTION)
    async def path(self, observer: Observer, block_id: str) -> DerivationPath | None:
        """Get the full derivation path from CONSTITUTION."""
        ...

    @aspect(category=AspectCategory.PERCEPTION)
    async def orphans(self, observer: Observer) -> list[KBlock]:
        """List all orphan K-Blocks."""
        ...
```

### Path Examples

```
self.kblock.derivation.manifest    # View derivation context
self.kblock.derivation.ground      # Connect to principle
self.kblock.derivation.disconnect  # Make orphan
self.kblock.derivation.suggest     # Get suggestions
self.kblock.derivation.path        # View full derivation path
self.kblock.derivation.orphans     # List orphans
```

---

## Anti-Patterns

### Directly Setting Grounding Status

```python
# BAD: Setting status directly
kblock.derivation_context.grounding_status = GroundingStatus.GROUNDED

# GOOD: Let status be computed from loss + principle
new_context = compute_derivation_context(kblock, principle)
kblock = replace(kblock, derivation_context=new_context)
```

### Ignoring Witnesses

```python
# BAD: Changing status without witness
kblock.derivation_context = replace(
    kblock.derivation_context,
    grounding_status=GroundingStatus.PROVISIONAL,
)

# GOOD: Always witness status changes
mark = await witness.mark(...)
kblock = await transition_with_witness(kblock, new_status, mark)
```

### Circular Derivations

```python
# BAD: K-Block derives from itself
kblock.derivation_context.parent_kblock_id = kblock.id

# GOOD: DAG structure enforced (Law 2)
validate_dag_before_connect(kblock, parent)
```

### Orphan Shaming

```python
# BAD: Treating orphans as errors
if kblock.derivation_context.grounding_status == GroundingStatus.ORPHAN:
    raise InvalidKBlockError("Must be grounded")

# GOOD: Orphans are valid, just surfaced for grounding
if kblock.derivation_context.grounding_status == GroundingStatus.ORPHAN:
    suggestions = await suggest_grounding(kblock)
    # Present suggestions, don't force
```

---

## Implementation Reference

### Directory Structure

```
services/k_block/
├── derivation/
│   ├── __init__.py              # Public API
│   ├── context.py               # KBlockDerivationContext dataclass
│   ├── grounding.py             # Grounding operations
│   ├── transitions.py           # State transition logic
│   ├── suggestions.py           # Grounding suggestion engine
│   └── path.py                  # DerivationPath management
├── _tests/
│   ├── test_derivation_context.py
│   ├── test_transitions.py
│   ├── test_grounding.py
│   └── test_path_dag.py
```

---

## Connection to Principles

| Principle | How Derivation Context Embodies It |
|-----------|------------------------------------|
| **Generative** | Context enables tracing back to Constitutional source |
| **Composable** | Derivation paths compose via DAG structure |
| **Tasteful** | Orphans are surfaced gently, not forced |
| **Ethical** | Full witness trail for all status changes |
| **Joy-Inducing** | Discovery of grounding feels like insight |

---

## Closing Meditation

Every K-Block is born with the question: *"Where do I come from?"*

The orphan state is not shame—it's an invitation. The system surfaces opportunities for connection. When grounding is discovered, the K-Block joins the trust network, participating in the flow of confidence from the Constitutional root.

The derivation context is not metadata about the K-Block. It IS part of what makes the K-Block meaningful. Content without context floats; content with context participates.

> *"The proof IS the decision. The context IS the meaning."*

---

*Draft specification written: 2025-01-10*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
