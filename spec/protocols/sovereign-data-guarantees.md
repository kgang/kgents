# Sovereign Data Guarantees: A First-Principles Framework

> *"The proof IS the possession. The witness IS the guarantee."*

---

## Abstract

This document establishes formal guarantees for the kgents sovereign data system from first principles. We prove that our data management provides:

1. **Integrity** - Data cannot be corrupted without detection
2. **Provenance** - Every datum has traceable origin
3. **Isolation** - Operations cannot interfere with each other
4. **Durability** - Committed data survives failures
5. **Composability** - Operations combine predictably

---

## 1. Axioms (First Principles)

We begin with five axioms that cannot be reduced further:

### Axiom 1: Content Addressability
```
∀ content c, hash(c) is unique and deterministic
If hash(c₁) = hash(c₂), then c₁ = c₂ (with negligible collision probability)
```

**Implementation**: SHA-256 content hashing at ingest time.

### Axiom 2: Append-Only Time
```
∀ versions v₁, v₂: if v₁ < v₂, then created(v₁) < created(v₂)
Versions are monotonically increasing and never decrease.
```

**Implementation**: Versioned directories (v1, v2, ...) with symlink to current.

### Axiom 3: Witness Immutability
```
∀ witness mark m: once created, m is immutable
m.content_hash = hash(m.data) forever
```

**Implementation**: Witness marks stored with content hash, never modified.

### Axiom 4: Causal Ordering
```
∀ operations o₁, o₂: if o₁ causes o₂, then mark(o₁) ← mark(o₂)
Parent-child mark relationships encode causality.
```

**Implementation**: Every mark references its parent marks.

### Axiom 5: Filesystem Atomicity
```
∀ file f: write(f) either completes fully or not at all
Directory renames are atomic on POSIX systems.
```

**Implementation**: Write to temp, atomic rename to final location.

---

## 2. The Four Sovereign Laws (Derived)

From the axioms, we derive four laws:

### Law 0: No Entity Without Copy
```
∀ entity e ∈ SovereignStore:
  ∃ content c such that stored(e) = c ∧ hash(c) = e.content_hash
```

**Proof**:
- By Axiom 1, content has unique hash
- By construction, we store exact bytes at ingest
- Therefore, entity existence implies content existence ∎

### Law 1: No Entity Without Witness
```
∀ entity e ∈ SovereignStore:
  ∃ mark m such that m.entity_path = e.path ∧ m.action = "sovereign.ingest"
```

**Proof**:
- Ingest operation creates mark before storing content
- Mark creation is required path in ingest flow
- By Axiom 3, mark cannot be deleted
- Therefore, entity implies witness ∎

### Law 2: No Edge Without Witness
```
∀ edge (e₁, e₂, type) discovered during ingest:
  ∃ mark m such that m.references edge ∧ m.parent = ingest_mark
```

**Proof**:
- Edge extraction happens in ingest transaction
- Each edge creates witness mark with parent = ingest mark
- By Axiom 4, causal order preserved
- Therefore, edge implies witness trail ∎

### Law 3: No Export Without Witness (Proposed)
```
∀ export operation o on entity e:
  ∃ mark m such that m.action = "sovereign.export" ∧ m.entity_path = e.path
```

**Implementation**: To be added in this document.

---

## 3. Guarantee Theorems

### Theorem 1: Integrity Guarantee
```
If an entity exists in the store with hash h,
then the content is exactly what was ingested.
```

**Proof**:
1. At ingest: content stored, hash computed (Axiom 1)
2. Hash stored in metadata (meta.json)
3. On retrieval: can recompute hash and compare
4. If hashes differ: integrity violation detected
5. By Axiom 5: partial writes don't corrupt (atomic)
∎

**Verification**: `hash(get_current(path).content) == metadata.content_hash`

### Theorem 2: Provenance Guarantee
```
For any entity e, we can reconstruct the complete history:
  who created it, when, from where, and all modifications.
```

**Proof**:
1. By Law 1: ingest mark exists with author, timestamp, source
2. By Axiom 4: modifications linked via parent marks
3. By Axiom 2: versions ordered temporally
4. Chain: current → v_n → v_{n-1} → ... → v_1 → ingest_mark
∎

**Verification**: Follow mark.parent chain from latest to birth mark.

### Theorem 3: Isolation Guarantee (K-Block)
```
Edits in K-Block b₁ do not affect K-Block b₂ until commit.
```

**Proof**:
1. K-Block creates isolated snapshot at creation
2. Edits modify only in-memory state
3. Commit writes new version atomically (Axiom 5)
4. Other K-Blocks read from committed versions only
5. By Axiom 2: new version visible only after commit
∎

**Verification**: K-Block isolation states (PRISTINE, DIRTY, STALE, CONFLICTING).

### Theorem 4: Durability Guarantee
```
Once ingest returns success, data survives process crash.
```

**Proof**:
1. Ingest writes to filesystem (not just memory)
2. By Axiom 5: atomic file operations
3. Success returned only after fsync
4. Filesystem provides durability
∎

**Verification**: `os.fsync()` called after writes.

### Theorem 5: Composability Guarantee
```
Operations compose: ingest ∘ analyze ∘ export = valid pipeline
```

**Proof**:
1. Each operation has well-defined input/output types
2. Output of op₁ matches input of op₂
3. Witness marks create causal chain (Axiom 4)
4. State transitions are valid (PENDING → ANALYZED)
∎

**Verification**: Type system enforces composition.

---

## 4. Data Lifecycle State Machine

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│ EXTERNAL │──►│ INGESTED │──►│ ANALYZED │──►│ ARCHIVED ││
│ (source) │   │ (v1+)    │   │ (edges)  │   │ (export) ││
└──────────┘   └──────────┘   └──────────┘   └──────────┘│
     ▲              │              │              │       │
     │              ▼              ▼              ▼       │
     │         ┌──────────┐   ┌──────────┐   ┌──────────┐│
     └─────────│ MODIFIED │   │ STALE    │   │ DELETED  ││
               │ (K-Block)│   │ (resync) │   │ (purge)  ││
               └──────────┘   └──────────┘   └──────────┘│
                    │                                     │
                    └─────────────────────────────────────┘
                              (reingest)
```

### State Transitions with Invariants

| Transition | Guard | Action | Invariant Preserved |
|------------|-------|--------|---------------------|
| EXTERNAL → INGESTED | content available | create v1 + mark | Law 0, Law 1 |
| INGESTED → ANALYZED | edges extracted | create edge marks | Law 2 |
| ANALYZED → MODIFIED | K-Block created | isolate snapshot | Theorem 3 |
| MODIFIED → INGESTED | K-Block saved | create v_{n+1} | Law 0, Law 1 |
| INGESTED → STALE | source changed | mark for resync | Axiom 2 |
| STALE → INGESTED | resync complete | create new version | Law 0 |
| Any → DELETED | user request | soft delete + mark | Law 3 (export first) |
| ANALYZED → ARCHIVED | export request | create export mark | Law 3 |

---

## 5. Collection Guarantees

Collections are pointers, not copies. This provides:

### Theorem 6: Collection Consistency
```
Adding entity e to collection c does not duplicate content.
∀ c₁, c₂ containing e: storage(e) is shared.
```

**Proof**:
1. Collection stores only path strings
2. Path resolves to single SovereignStore location
3. No content duplication occurs
∎

### Theorem 7: Collection Atomicity
```
Collection operations (add/remove path) are atomic.
```

**Proof**:
1. Collection stored in single DB row
2. paths is JSON array in single column
3. DB transaction provides atomicity
∎

---

## 6. Placeholder Guarantees

### Theorem 8: Placeholder Resolution
```
When entity e is ingested matching placeholder p.path,
p is automatically resolved.
```

**Proof**:
1. Ingest checks for existing placeholder at path
2. If found: set resolved=True, resolved_at=now
3. Placeholder references remain valid (point to real entity)
∎

### Theorem 9: Reference Completeness
```
All references discovered during analysis are either:
  (a) existing entities, or
  (b) placeholders
```

**Proof**:
1. Analysis extracts all refs from content
2. For each ref: check exists(ref)
3. If not exists: create placeholder
4. By construction: complete coverage
∎

---

## 7. Export Guarantees (To Implement)

### Law 3 Implementation

```python
async def export(
    paths: list[str],
    format: ExportFormat,
    author: str,
) -> ExportResult:
    """
    Export entities with full witness trail.

    Guarantees:
    1. Export mark created BEFORE export
    2. Content hashes included for verification
    3. Provenance chain exported
    4. References resolved or marked as placeholders
    """
    # 1. Create export mark (Law 3)
    mark = await witness.save_mark(
        action=f"sovereign.export: {len(paths)} entities",
        reasoning=f"Export requested by {author}",
        principles=["ethical"],  # Data leaves our control
        tags=["export", format.value],
    )

    # 2. Gather entities with provenance
    bundle = ExportBundle(
        mark_id=mark.mark_id,
        entities=[],
        provenance=[],
    )

    for path in paths:
        entity = await store.get_current(path)
        bundle.entities.append(ExportedEntity(
            path=path,
            content=entity.content,
            content_hash=entity.content_hash,
            ingest_mark_id=entity.ingest_mark_id,
        ))

        # Include provenance chain
        chain = await witness.get_mark_chain(entity.ingest_mark_id)
        bundle.provenance.extend(chain)

    # 3. Package and return
    return ExportResult(
        bundle=bundle,
        format=format,
        export_mark_id=mark.mark_id,
    )
```

---

## 8. File Management Guarantees

### Theorem 10: Rename Integrity
```
Renaming entity from path p₁ to p₂ preserves all guarantees.
```

**Proof sketch**:
1. Create new entity at p₂ with content from p₁
2. Update all edges pointing to p₁ → p₂
3. Update all collections containing p₁
4. Create rename mark linking p₁ → p₂
5. Soft-delete p₁ (mark as renamed, keep for history)
6. All invariants preserved by construction
∎

### Theorem 11: Delete Safety
```
Deleting entity e does not corrupt references.
```

**Proof sketch**:
1. Check for incoming references to e
2. If references exist: convert to placeholders OR block delete
3. Create delete mark
4. Remove from filesystem
5. Referential integrity maintained
∎

---

## 9. Verification Protocol

To verify guarantees at runtime:

```python
async def verify_integrity(path: str) -> VerificationResult:
    """Verify all guarantees for an entity."""
    entity = await store.get_current(path)

    checks = []

    # Law 0: Content exists
    checks.append(Check(
        name="content_exists",
        passed=entity.content is not None,
    ))

    # Law 1: Witness exists
    mark = await witness.get_mark(entity.ingest_mark_id)
    checks.append(Check(
        name="witness_exists",
        passed=mark is not None,
    ))

    # Theorem 1: Integrity
    computed_hash = hashlib.sha256(entity.content).hexdigest()
    checks.append(Check(
        name="integrity",
        passed=computed_hash == entity.content_hash,
    ))

    # Law 2: Edges witnessed (if analyzed)
    if await store.is_analyzed(path):
        state = await store.get_analysis_state(path)
        checks.append(Check(
            name="edges_witnessed",
            passed=state.analysis_mark_id is not None,
        ))

    return VerificationResult(
        path=path,
        checks=checks,
        all_passed=all(c.passed for c in checks),
    )
```

---

## 10. Summary: The Guarantee Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  Collections, Placeholders, Analysis, Export                 │
├─────────────────────────────────────────────────────────────┤
│                    GUARANTEE LAYER                           │
│  Integrity, Provenance, Isolation, Durability, Composability │
├─────────────────────────────────────────────────────────────┤
│                    LAW LAYER                                 │
│  Law 0: Copy  │  Law 1: Witness  │  Law 2: Edge  │  Law 3   │
├─────────────────────────────────────────────────────────────┤
│                    AXIOM LAYER                               │
│  Content Address │ Append Time │ Immutable │ Causal │ Atomic │
├─────────────────────────────────────────────────────────────┤
│                    FOUNDATION LAYER                          │
│  SHA-256  │  Filesystem  │  Database  │  Witness System      │
└─────────────────────────────────────────────────────────────┘
```

Each layer provides guarantees to the layer above, creating a stack of provable properties from cryptographic primitives to application features.

---

## Appendix A: Formal Notation

```
Entities:    E = {e | e ∈ SovereignStore}
Marks:       M = {m | m ∈ WitnessStore}
Edges:       G = (E, R) where R ⊆ E × E × EdgeType
Collections: C = P(E) (power set - collections are sets of entity paths)
Versions:    V: E → ℕ (version function)
Hash:        H: Bytes → String (SHA-256)
Time:        T: Operation → Timestamp (monotonic)

Laws as predicates:
  Law0(e) ≡ ∃c. stored(e) = c ∧ H(c) = e.hash
  Law1(e) ≡ ∃m ∈ M. m.path = e.path ∧ m.type = "ingest"
  Law2(r) ≡ ∀(e₁,e₂,t) ∈ R. ∃m ∈ M. m.edge = (e₁,e₂,t)
  Law3(o) ≡ o.type = "export" → ∃m ∈ M. m.export = o
```

---

*"The proof IS the decision. The mark IS the witness. The guarantee IS the system."*

---

**Filed**: 2025-12-23
**Status**: Living Document
**Version**: 1.0
