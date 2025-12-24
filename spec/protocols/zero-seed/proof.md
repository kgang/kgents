# Zero Seed: Proof & Witnessing

> *"Every node justifies its existence—or admits it cannot."*

**Module**: Proof & Witnessing
**Depends on**: [`core.md`](./core.md)

---

## Purpose

This module formalizes the witnessing system that emerges from the Justification meta-principle (M). Every modification to the graph creates a Mark—a witnessed trace of change.

The critical tension **Full Witnessing vs Performance** is addressed through **witness batching strategies**.

---

## Proof Structure

### Toulmin Architecture

All L3+ nodes require Toulmin proof structure. This is the universal justification form:

```python
@dataclass(frozen=True)
class Proof:
    """Defeasible reasoning structure for L3+ nodes."""

    # Core structure
    data: str                           # Evidence ("3 hours, 45K tokens invested")
    warrant: str                        # Reasoning ("Infrastructure enables velocity")
    claim: str                          # Conclusion ("This refactoring was worthwhile")

    # Extended structure
    backing: str                        # Support for warrant
    qualifier: str                      # Confidence level
    rebuttals: tuple[str, ...]          # Defeaters

    # Metadata
    tier: EvidenceTier                  # Classification of evidence
    principles: tuple[str, ...]         # Referenced Constitution principles


class EvidenceTier(Enum):
    """Evidence strength classification."""
    CATEGORICAL = "categorical"         # Mathematical, logical proof
    EMPIRICAL = "empirical"             # Measured, observed data
    AESTHETIC = "aesthetic"             # Taste, design judgment
    SOMATIC = "somatic"                 # Gut feeling, embodied sense
    TESTIMONIAL = "testimonial"         # Third-party claims
```

### Qualifier Semantics

| Qualifier | Confidence | Use When |
|-----------|------------|----------|
| `definitely` | 0.95-1.0 | Categorical proof, verified empirically |
| `probably` | 0.70-0.95 | Strong evidence, minor rebuttals |
| `possibly` | 0.40-0.70 | Mixed evidence, significant rebuttals |
| `uncertain` | 0.10-0.40 | Weak evidence, speculative |
| `unknown` | 0.00-0.10 | Exploratory, no evidence yet |

---

## Proof Validation

```python
def validate_proof(proof: Proof, node: ZeroNode) -> ProofValidation:
    """Validate proof structure coherence."""
    issues = []

    # Data must be present
    if not proof.data.strip():
        issues.append("Missing data: proof requires evidence")

    # Warrant must connect data to claim
    if not proof.warrant.strip():
        issues.append("Missing warrant: reasoning required")

    # Claim must be present
    if not proof.claim.strip():
        issues.append("Missing claim: conclusion required")

    # Qualifier must match rebuttal count
    if proof.qualifier == "definitely" and len(proof.rebuttals) > 0:
        issues.append("Qualifier 'definitely' incompatible with rebuttals")

    # Tier must be appropriate for layer
    if node.layer <= 4 and proof.tier == EvidenceTier.SOMATIC:
        issues.append("Warning: somatic evidence weak for specification layer")

    # Compute coherence score
    coherence = compute_toulmin_coherence(proof)

    return ProofValidation(
        is_valid=len([i for i in issues if not i.startswith("Warning")]) == 0,
        coherence=coherence,
        issues=tuple(issues),
    )


def compute_toulmin_coherence(proof: Proof) -> float:
    """Compute coherence score [0, 1] for proof structure."""
    scores = []

    # Data richness (length proxy)
    scores.append(min(1.0, len(proof.data) / 200))

    # Warrant presence
    scores.append(1.0 if proof.warrant.strip() else 0.0)

    # Backing support
    scores.append(min(1.0, len(proof.backing) / 100) if proof.backing else 0.5)

    # Qualifier appropriateness (lower = more appropriate for uncertainty)
    qualifier_score = {
        "definitely": 1.0,
        "probably": 0.8,
        "possibly": 0.6,
        "uncertain": 0.4,
        "unknown": 0.2,
    }.get(proof.qualifier, 0.5)
    scores.append(qualifier_score)

    # Rebuttal coverage
    if proof.qualifier in ("definitely", "probably"):
        # Should have rebuttals
        scores.append(min(1.0, len(proof.rebuttals) / 3))
    else:
        scores.append(1.0)  # Uncertain claims don't need rebuttals

    return sum(scores) / len(scores)
```

---

## Full Witnessing

**Every edit creates a Mark.** This is the core witnessing principle.

```python
async def modify_node(
    node: ZeroNode,
    delta: NodeDelta,
    observer: Observer,
    reasoning: str,
) -> tuple[ZeroNode, Mark]:
    """Modify a node with full witnessing."""

    # Create new version
    new_node = apply_delta(node, delta)

    # Create witness mark (REQUIRED)
    mark = Mark(
        id=generate_mark_id(),
        origin="zero-seed",
        stimulus=Stimulus(
            kind="edit",
            source_node=node.id,
            delta=delta.to_dict(),
        ),
        response=Response(
            kind="node_updated",
            target_node=new_node.id,
        ),
        umwelt=observer.to_umwelt_snapshot(),
        links=(MarkLink(source=mark.id, target=node.id, kind="modifies"),),
        timestamp=datetime.now(UTC),
        proof=None if node.layer <= 2 else require_proof(delta),
        tags=frozenset({"zero-seed", f"layer:{node.layer}", f"kind:{node.kind}"}),
    )

    # Persist both
    await store.save_node(new_node)
    await store.save_mark(mark)

    return new_node, mark
```

---

## Witness Batching Strategies

### The Tension

Full witnessing (every edit = one mark) creates performance issues:
- 100 rapid edits = 100 marks = 100 I/O operations
- Audit trail becomes noisy with micro-changes
- Storage grows linearly with edit frequency

### Resolution: Three Modes

```python
class WitnessMode(Enum):
    """Witness granularity modes."""
    SINGLE = "single"       # Every edit creates a mark (maximum granularity)
    SESSION = "session"     # Batch marks per session (balanced)
    LAZY = "lazy"           # Defer marks until query (maximum performance)


@dataclass
class WitnessBatcher:
    """Manages witness batching based on mode."""

    mode: WitnessMode
    session_buffer: list[PendingMark] = field(default_factory=list)
    last_flush: datetime = field(default_factory=lambda: datetime.now(UTC))
    flush_threshold: int = 10  # Marks before auto-flush
    flush_interval: timedelta = timedelta(seconds=30)

    async def witness(self, mark: Mark) -> MarkId | None:
        """Witness a mark according to current mode."""
        match self.mode:
            case WitnessMode.SINGLE:
                # Immediate persistence
                await store.save_mark(mark)
                return mark.id

            case WitnessMode.SESSION:
                # Buffer and batch
                self.session_buffer.append(PendingMark(mark=mark, timestamp=datetime.now(UTC)))
                if self._should_flush():
                    return await self._flush()
                return None  # Deferred

            case WitnessMode.LAZY:
                # Store in memory only
                self.session_buffer.append(PendingMark(mark=mark, timestamp=datetime.now(UTC)))
                return None

    def _should_flush(self) -> bool:
        """Check if buffer should be flushed."""
        if len(self.session_buffer) >= self.flush_threshold:
            return True
        if datetime.now(UTC) - self.last_flush > self.flush_interval:
            return True
        return False

    async def _flush(self) -> MarkId:
        """Flush buffer to create BatchMark."""
        if not self.session_buffer:
            return None

        batch_mark = BatchMark(
            id=generate_mark_id(),
            origin="zero-seed",
            marks=tuple(pm.mark for pm in self.session_buffer),
            count=len(self.session_buffer),
            first_timestamp=self.session_buffer[0].timestamp,
            last_timestamp=self.session_buffer[-1].timestamp,
            tags=frozenset({"zero-seed", "batch:session"}),
        )

        await store.save_batch_mark(batch_mark)
        self.session_buffer.clear()
        self.last_flush = datetime.now(UTC)

        return batch_mark.id

    async def force_flush(self) -> MarkId | None:
        """Force flush regardless of thresholds."""
        return await self._flush()
```

### BatchMark Structure

```python
@dataclass(frozen=True)
class BatchMark:
    """A batched collection of marks."""

    id: MarkId
    origin: str
    marks: tuple[Mark, ...]             # Contained marks
    count: int                          # Number of marks
    first_timestamp: datetime           # Earliest mark
    last_timestamp: datetime            # Latest mark
    tags: frozenset[str]

    def unpack(self) -> list[Mark]:
        """Unpack to individual marks for replay."""
        return list(self.marks)

    def summary(self) -> str:
        """Human-readable summary."""
        duration = self.last_timestamp - self.first_timestamp
        return f"Batch of {self.count} marks over {duration.total_seconds():.1f}s"
```

### Mode Selection

```python
# Environment variable configuration
WITNESS_MODE = os.getenv("ZERO_SEED_WITNESS_MODE", "session")

# Programmatic selection
batcher = WitnessBatcher(mode=WitnessMode[WITNESS_MODE.upper()])

# Mode tradeoffs
MODE_TRADEOFFS = {
    WitnessMode.SINGLE: {
        "io_overhead": "high",
        "granularity": "maximum",
        "audit_quality": "perfect",
        "use_case": "debugging, compliance, learning",
    },
    WitnessMode.SESSION: {
        "io_overhead": "medium",
        "granularity": "session-level",
        "audit_quality": "good",
        "use_case": "normal operation (recommended)",
    },
    WitnessMode.LAZY: {
        "io_overhead": "low",
        "granularity": "query-triggered",
        "audit_quality": "lossy if crash",
        "use_case": "bulk operations, performance-critical",
    },
}
```

---

## Paraconsistent Semantics

### The Problem

Two nodes may contradict. Traditional logic: explosion (anything follows from contradiction). Zero Seed: **dialectical invitation**.

### Three-Valued Logic

```python
class TruthValue(Enum):
    """Three-valued paraconsistent logic."""
    TRUE = "true"           # Consistent with Constitution
    FALSE = "false"         # Contradicts Constitution directly
    UNKNOWN = "unknown"     # Has unresolved contradictions


def compute_truth_value(node: ZeroNode, graph: ZeroGraph) -> TruthValue:
    """Compute truth value in paraconsistent model."""
    contradictions = graph.edges_from(node.id, kind=EdgeKind.CONTRADICTS)
    contradicted_by = graph.edges_to(node.id, kind=EdgeKind.CONTRADICTS)

    if not contradictions and not contradicted_by:
        # No contradictions = TRUE (assuming proof validates)
        return TruthValue.TRUE

    # Has contradictions
    all_resolved = all(
        e.is_resolved for e in contradictions
    ) and all(
        e.is_resolved for e in contradicted_by
    )

    if all_resolved:
        return TruthValue.TRUE
    else:
        return TruthValue.UNKNOWN
```

### Explosion Prevention

Contradiction edges do NOT propagate validity:

```python
def check_explosion(graph: ZeroGraph) -> ExplosionCheck:
    """Verify contradictions don't propagate globally."""
    contradiction_edges = list(graph.edges_of_kind(EdgeKind.CONTRADICTS))

    # Partition nodes by contradiction involvement
    clean_nodes = set()
    contradicting_nodes = set()

    for node in graph.nodes:
        edges = graph.edges_from(node.id, kind=EdgeKind.CONTRADICTS)
        if edges:
            contradicting_nodes.add(node.id)
        else:
            clean_nodes.add(node.id)

    # Verify clean nodes don't inherit contradiction
    for node_id in clean_nodes:
        incoming = graph.edges_to(node_id)
        for edge in incoming:
            if edge.source in contradicting_nodes and edge.kind != EdgeKind.CONTRADICTS:
                # Non-contradiction edge from contradicting node
                # This is allowed but flagged for review
                pass

    return ExplosionCheck(
        contradiction_count=len(contradiction_edges),
        clean_count=len(clean_nodes),
        contradicting_count=len(contradicting_nodes),
        explosion_risk=len(contradicting_nodes) / len(graph.nodes) if graph.nodes else 0,
    )
```

### Bounded Contradiction Space

Constitutional reward partitions nodes:

```python
def partition_by_constitution(
    nodes: list[ZeroNode],
    constitution: Constitution,
) -> ContradictionPartition:
    """Partition nodes by constitutional score."""
    threshold = 0.6  # Minimum score for "dominant"

    dominant = []
    recessive = []
    incomparable = []

    for node in nodes:
        score = constitution.evaluate(None, "exist", node)

        if score.total >= threshold:
            dominant.append(node)
        elif score.total < threshold * 0.5:
            recessive.append(node)
        else:
            incomparable.append(node)

    return ContradictionPartition(
        dominant=tuple(dominant),
        recessive=tuple(recessive),
        incomparable=tuple(incomparable),
    )


# Rule: Contradiction edges can only connect nodes in SAME partition
def validate_contradiction_edge(edge: ZeroEdge, graph: ZeroGraph) -> bool:
    """Validate contradiction edge respects partition bounds."""
    if edge.kind != EdgeKind.CONTRADICTS:
        return True

    source = graph.get_node(edge.source)
    target = graph.get_node(edge.target)
    partition = partition_by_constitution(graph.nodes, constitution)

    source_partition = get_partition(source, partition)
    target_partition = get_partition(target, partition)

    return source_partition == target_partition
```

---

## Contradiction Handling

```python
async def check_contradiction_status(graph: ZeroGraph) -> ContradictionReport:
    """Report all unresolved contradictions."""
    contradictions = []

    for edge in graph.edges_of_kind(EdgeKind.CONTRADICTS):
        if not edge.is_resolved:
            contradictions.append(ContradictionPair(
                node_a=graph.get_node(edge.source),
                node_b=graph.get_node(edge.target),
                edge=edge,
            ))

    return ContradictionReport(
        total=len(contradictions),
        by_layer={l: [c for c in contradictions if c.node_a.layer == l] for l in range(1, 8)},
        oldest=min(contradictions, key=lambda c: c.edge.created_at) if contradictions else None,
    )


async def resolve_contradiction(
    edge: ZeroEdge,
    resolution: ZeroNode,
    graph: ZeroGraph,
) -> tuple[ZeroEdge, Mark]:
    """Resolve a contradiction with a synthesis node."""
    assert edge.kind == EdgeKind.CONTRADICTS

    # Mark edge as resolved
    resolved_edge = edge.with_resolution(resolution.id)

    # Create synthesis edges
    await graph.add_edge(ZeroEdge(
        source=edge.source,
        target=resolution.id,
        kind=EdgeKind.SYNTHESIZES,
        context=f"Resolved contradiction with {resolution.title}",
    ))
    await graph.add_edge(ZeroEdge(
        source=edge.target,
        target=resolution.id,
        kind=EdgeKind.SYNTHESIZES,
        context=f"Resolved contradiction with {resolution.title}",
    ))

    # Witness the resolution
    mark = await witness_resolution(edge, resolution)

    return resolved_edge, mark
```

---

## Open Questions

1. **Lazy mode durability**: How do we handle crashes in lazy mode? WAL?
2. **Batch unpacking**: Should audit replay always unpack, or preserve batches?
3. **Contradiction depth limit**: How many layers of contradiction should we tolerate?

---

*"The proof IS the decision. The batch IS the session. The contradiction IS the invitation."*
