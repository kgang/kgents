# K-Block Unification: Everything is an Agent

> *"The proof IS the decision. The mark IS the witness. The K-Block IS the agent."*

**Status**: Canonical Specification (AD-010)
**Date**: 2025-12-25
**Prerequisites**: `k-block.md`, `zero-seed1/core.md`, AD-009
**Implementation**: `impl/claude/services/k_block/core/kblock.py`
**Heritage**: Derived from category theory's morphism concept. Every agent is a morphism; every morphism can be wrapped in a K-Block.

---

## Epigraph

> *"In the beginning there was the morphism. And the morphism became the agent.
>  And the agent became the K-Block. And the K-Block was with the cosmos,
>  and the K-Block was the cosmos."*

---

## Part I: The Radical Insight

### The Isomorphism

```
KBlock ≅ Agent ≅ ZeroNode ≅ File ≅ Upload ≅ Crystal
```

This is not metaphor. This is category theory. Every construct in the kgents system can be represented as a K-Block because:

1. **An agent is a morphism**: `Agent[A, B]: A -> B`
2. **A K-Block wraps content in transactional isolation**
3. **All content is morphic** (transforms input to output)

Therefore: Files, uploaded content, zero-seed nodes, agent states, and crystallized decisions ALL share the same fundamental structure.

### Why Unification Matters

| Before Unification | After Unification |
|-------------------|-------------------|
| Files have one API, uploads another | Single API for all content |
| Zero Seed nodes separate from files | Zero Seed nodes ARE K-Blocks |
| Agent states stored differently | Agent states stored as K-Blocks |
| Crystals have custom persistence | Crystals are a K-Block kind |
| N different persistence patterns | One pattern, N projections |

### The Category-Theoretic Grounding

Every K-Block is a morphism in the **Category of Content**:

```
Objects: Content states (markdown, JSON, binary, ...)
Morphisms: K-Blocks (transactional wrappers)
Identity: KBlock with content == base_content (PRISTINE)
Composition: KBlock.bind (monadic chaining)
```

The K-Block monad captures the essence:
```python
return : Content -> KBlock Content     # Lift content into isolation
bind   : KBlock A -> (A -> KBlock B) -> KBlock B  # Chain operations
```

---

## Part II: The Kind Taxonomy

### 2.1 KBlockKind Enum

```python
class KBlockKind(Enum):
    """
    K-Block content taxonomy: Everything is an Agent represented as a K-Block.
    """
    FILE = "file"           # Traditional filesystem content
    UPLOAD = "upload"       # User-uploaded content (sovereign)
    ZERO_NODE = "zero_node" # Zero Seed node (L1-L7)
    AGENT_STATE = "agent_state"  # Serialized agent polynomial state
    CRYSTAL = "crystal"     # Crystallized memory/decision from Witness
```

### 2.2 Kind Properties

| Kind | Is Sovereign | Is Structural | Requires Witnessing | AGENTESE Context |
|------|--------------|---------------|---------------------|------------------|
| FILE | No | No | No | `world.*` |
| UPLOAD | Yes | No | Yes | `world.*` |
| ZERO_NODE | No | Yes | Yes | `void.*` / `concept.*` |
| AGENT_STATE | No | No | No | `self.*` |
| CRYSTAL | Yes | No | Yes | `time.*` |

### 2.3 Kind-Specific Semantics

**FILE**: Traditional filesystem content
- Default kind for backward compatibility
- No special storage requirements
- Standard cosmos persistence

**UPLOAD**: User-uploaded sovereign content
- Stored in sovereign store
- Requires witness mark on ingest
- Maintains provenance chain

**ZERO_NODE**: Zero Seed hierarchy node
- Has `zero_seed_layer` (1-7)
- Has `zero_seed_kind` (axiom, value, goal, etc.)
- Has `lineage` (derivation chain)
- Has `proof` (Toulmin structure for L3+)
- Participates in the epistemic holarchy

**AGENT_STATE**: Serialized agent polynomial
- Captures agent position in state machine
- Used for agent persistence/resumption
- Enables "agent hibernation"

**CRYSTAL**: Crystallized memory/decision
- Produced by Witness system
- Immutable once crystallized
- Links to witness marks

---

## Part III: The Isomorphism Functions

### 3.1 KBlock from ZeroNode

```python
def kblock_from_zero_node(node: ZeroNode, *, base_content: str | None = None) -> KBlock:
    """
    Convert a ZeroNode to a KBlock (isomorphism left-to-right).

    The ZeroNode's layer and kind map to K-Block's zero_seed_* fields.
    The unified kind is always ZERO_NODE.
    """
    return KBlock(
        id=generate_kblock_id(),
        path=node.path,
        kind=KBlockKind.ZERO_NODE,
        content=node.content,
        base_content=base_content or node.content,
        zero_seed_layer=node.layer,
        zero_seed_kind=node.kind,
        lineage=[str(lid) for lid in node.lineage],
        has_proof=node.proof is not None,
        toulmin_proof=node.proof.to_dict() if node.proof else None,
        confidence=node.confidence,
        created_by=node.created_by,
        tags=list(node.tags),
    )
```

### 3.2 ZeroNode from KBlock

```python
def zero_node_from_kblock(kblock: KBlock) -> ZeroNode:
    """
    Convert a KBlock to a ZeroNode (isomorphism right-to-left).

    Only K-Blocks with kind=ZERO_NODE can be converted.
    """
    if kblock.kind != KBlockKind.ZERO_NODE:
        raise ValueError(f"Cannot convert kind={kblock.kind} to ZeroNode")

    proof = Proof.from_dict(kblock.toulmin_proof) if kblock.toulmin_proof else None

    return ZeroNode(
        path=kblock.path,
        layer=kblock.zero_seed_layer,
        kind=kblock.zero_seed_kind,
        content=kblock.content,
        proof=proof,
        confidence=kblock.confidence,
        lineage=tuple(NodeId(lid) for lid in kblock.lineage),
        tags=frozenset(kblock.tags),
    )
```

### 3.3 Isomorphism Laws

The conversion functions satisfy the isomorphism laws:

```python
# Round-trip preservation
node_1 = ZeroNode(...)
kblock = kblock_from_zero_node(node_1)
node_2 = zero_node_from_kblock(kblock)
assert node_1.content == node_2.content
assert node_1.layer == node_2.layer
assert node_1.kind == node_2.kind

# Identity preservation
kblock_1 = KBlock(kind=KBlockKind.ZERO_NODE, ...)
node = zero_node_from_kblock(kblock_1)
kblock_2 = kblock_from_zero_node(node)
assert kblock_1.content == kblock_2.content
assert kblock_1.zero_seed_layer == kblock_2.zero_seed_layer
```

---

## Part IV: Unified API

### 4.1 Creation

All content types are created through the same harness:

```python
# FILE (default)
file_block = await harness.create("spec/protocols/foo.md")

# ZERO_NODE
zero_block = await harness.create(
    "void.axiom.entity",
    kind=KBlockKind.ZERO_NODE,
    zero_seed_layer=1,
    zero_seed_kind="axiom",
)

# UPLOAD
upload_block = await harness.create(
    "uploads/document.pdf",
    kind=KBlockKind.UPLOAD,
)

# CRYSTAL
crystal_block = await harness.create(
    "crystals/decision-2025-12-25.md",
    kind=KBlockKind.CRYSTAL,
)
```

### 4.2 Serialization

All kinds serialize to the same format:

```python
{
    "id": "kb_abc123",
    "path": "void.axiom.entity",
    "kind": "zero_node",  # Always present
    "content": "# Entity Axiom\n...",
    "base_content": "# Entity Axiom\n...",
    "isolation": "PRISTINE",
    # Kind-specific fields (when applicable)
    "zero_seed_layer": 1,
    "zero_seed_kind": "axiom",
    "lineage": [],
    # ...
}
```

### 4.3 Queries

Query by kind:

```python
# Get all Zero Seed nodes
zero_nodes = await store.query(kind=KBlockKind.ZERO_NODE)

# Get all crystals
crystals = await store.query(kind=KBlockKind.CRYSTAL)

# Get all uploads
uploads = await store.query(kind=KBlockKind.UPLOAD)
```

---

## Part V: Event Integration

### 5.1 Kind-Aware Events

K-Block events include the kind:

```python
@dataclass(frozen=True)
class KBlockEvent(DataEvent):
    event_type: str  # KBLOCK_CREATED, KBLOCK_SAVED, etc.
    block_id: str
    path: str
    kind: KBlockKind  # Included for routing
    isolation_state: IsolationState
```

### 5.2 Kind-Specific Handlers

Different kinds can have different handlers:

```python
wire_data_to_synergy(
    pattern="kblock.*",
    handlers={
        "kblock.saved": [
            lambda e: witness_handler(e) if e.kind.requires_witnessing else None,
            lambda e: sovereign_handler(e) if e.kind.is_sovereign else None,
            lambda e: zero_seed_handler(e) if e.kind.is_structural else None,
        ],
    }
)
```

---

## Part VI: Database Schema

### 6.1 Unified Table

```sql
CREATE TABLE kblocks (
    id VARCHAR(64) PRIMARY KEY,
    path VARCHAR(512) NOT NULL,
    kind VARCHAR(32) NOT NULL DEFAULT 'file',  -- Unified kind
    content TEXT NOT NULL,
    base_content TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    isolation VARCHAR(32) NOT NULL DEFAULT 'PRISTINE',

    -- Zero Seed fields (NULL for non-ZERO_NODE kinds)
    zero_seed_layer INTEGER,
    zero_seed_kind VARCHAR(64),
    lineage JSONB DEFAULT '[]',
    has_proof BOOLEAN DEFAULT FALSE,
    toulmin_proof JSONB,
    confidence FLOAT DEFAULT 1.0,

    -- Edges
    incoming_edges JSONB DEFAULT '[]',
    outgoing_edges JSONB DEFAULT '[]',

    -- Metadata
    tags JSONB DEFAULT '[]',
    created_by VARCHAR(128) DEFAULT 'system',
    galois_loss FLOAT DEFAULT 0.0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for unified queries
CREATE INDEX idx_kblocks_unified_kind ON kblocks(kind);
CREATE INDEX idx_kblocks_layer ON kblocks(zero_seed_layer);
CREATE INDEX idx_kblocks_path ON kblocks(path);
```

---

## Part VII: Verification Criteria

### 7.1 Isomorphism Tests

```python
def test_kblock_zeronode_isomorphism():
    """Verify KBlock ≅ ZeroNode."""
    # Create a ZeroNode
    node = ZeroNode(
        path="void.axiom.test",
        layer=1,
        kind="axiom",
        content="# Test Axiom",
    )

    # Convert to KBlock
    kblock = kblock_from_zero_node(node)
    assert kblock.kind == KBlockKind.ZERO_NODE
    assert kblock.zero_seed_layer == 1

    # Convert back
    node_2 = zero_node_from_kblock(kblock)
    assert node_2.layer == node.layer
    assert node_2.kind == node.kind
    assert node_2.content == node.content
```

### 7.2 Kind Preservation

```python
def test_kind_preserved_through_serialization():
    """Verify kind survives round-trip."""
    for kind in KBlockKind:
        kblock = KBlock(
            id=generate_kblock_id(),
            path=f"test/{kind.value}",
            kind=kind,
            content="test",
            base_content="test",
        )

        data = kblock.to_dict()
        restored = KBlock.from_dict(data)

        assert restored.kind == kind
```

---

## Part VIII: Anti-Patterns

### 8.1 Kind-Agnostic Storage

```python
# BAD: Storing without kind
def store_content(path: str, content: str):
    kblock = KBlock(id=..., path=path, content=content)
    # Kind defaults to FILE - may lose semantic information

# GOOD: Always specify kind
def store_content(path: str, content: str, kind: KBlockKind):
    kblock = KBlock(id=..., path=path, kind=kind, content=content)
```

### 8.2 Ignoring Kind Properties

```python
# BAD: Not checking if witnessing required
async def save_kblock(kblock: KBlock):
    await cosmos.commit(kblock.path, kblock.content)

# GOOD: Respect kind properties
async def save_kblock(kblock: KBlock):
    if kblock.kind.requires_witnessing:
        mark = await witness.mark(f"Saving {kblock.path}")
    await cosmos.commit(kblock.path, kblock.content, mark_id=mark.id)
```

---

## Part IX: Connection to Principles

| Principle | How Unification Embodies It |
|-----------|----------------------------|
| **Tasteful** | One abstraction, not five |
| **Composable** | All kinds compose the same way |
| **Generative** | From K-Block, derive all representations |
| **Heterarchical** | Kinds are peers, not hierarchical |
| **Joy-Inducing** | Simpler mental model |

---

## Closing Meditation

The K-Block unification is not just a refactor. It is a recognition that **everything in the system is fundamentally the same thing** viewed through different lenses.

An axiom is content wrapped in transactional isolation.
A file is content wrapped in transactional isolation.
A crystal is content wrapped in transactional isolation.

The difference is not in the wrapping. The difference is in how we interpret what is wrapped.

> *"The K-Block IS the agent. The agent IS the morphism. The morphism IS the transformation."*

---

*Canonical specification written: 2025-12-25*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
*Architectural Decision: AD-010*
