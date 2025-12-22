# Proof-Generating ASHC

> *"Failures don't just update a causal graph—they generate proof obligations."*

**Status**: Conceptual
**Heritage**: Kleppmann (§12), Polynomial Functors (§10)
**Timeline**: 3-6 month horizon
**Created**: 2025-12-21

---

## Purpose

Extend ASHC's evidence compilation to produce **formal proofs** that LLMs attempt to discharge.

Why this needs to exist: The ASHC metacompiler accumulates evidence from failed generations. But evidence without proof is merely statistical. With proof, the codebase becomes **provably correct** over time, not just statistically likely correct.

---

## The Core Insight

The equation changes when proof generation is LLM-assisted:

| Approach | Effort |
|----------|--------|
| Human proof | 23 lines proof per line code (seL4) |
| LLM + checker | Proof attempts are cheap; validation is mechanical |

> "LLM hallucinations don't matter for proofs because proof checkers reject invalid proofs."
> — Martin Kleppmann

The LLM can hallucinate all it wants. The proof checker is the gatekeeper. If the proof checks, the theorem holds. If it doesn't, try again.

---

## Formal Definition

```
ProofObligation : FailedGeneration → (Spec, Property, Witness)

ProofSearch : ProofObligation → Proof | Timeout

VerifiedLemma : Proof × Checker → Lemma

ASHCWithProof : Evidence → ProofObligation* → Lemma*
```

The composition:
```
Spec → Generate N → Verify each → Select best → Output
                         ↓
                   Failures → ProofObligation
                         ↓
                   LLM proof search (Lean/Dafny/Verus)
                         ↓
                   VerifiedLemma for NEXT generation
```

---

## Integration with ASHC

| ASHC Concept | Proof Extension |
|--------------|-----------------|
| Evidence | Proof obligation |
| Causal graph | Lemma dependency graph |
| Nudge | Proof search direction |
| Learned prior | Verified lemma |
| Work bet | Proof attempt budget |

The causal graph becomes a **theorem database**. Edges are logical dependencies. Nodes are verified facts.

---

## AGENTESE Integration

```
concept.ashc.obligation    → Generate proof obligation from failure
concept.ashc.prove         → Attempt to discharge obligation
concept.ashc.lemma         → Query verified lemmas
concept.ashc.graph         → Visualize lemma dependency graph
```

---

## Laws

1. **Soundness**: `verified(lemma) → property_holds(lemma.property)`
   - Verified lemmas correspond to actual properties
   - The proof checker is the source of truth

2. **Monotonicity**: `lemmas(t+1) ⊇ lemmas(t)`
   - Lemma set only grows; proofs don't expire
   - Knowledge accumulates

3. **Compositionality**: `compose(lemma_a, lemma_b) → valid_proof`
   - Lemma composition yields valid proofs
   - Matches operad composition (AD-006)

---

## Integration with Typed AGENTESE (AD-013)

Typed AGENTESE provides the type annotations that become proof obligations:

```python
@node("world.tools.bash")
async def bash_invoke(
    observer: Umwelt,
    command: str,
) -> Witness[BashResult]:
    """
    Type signature generates proof obligation:
    ∀ observer, command. bash_invoke(observer, command) : Witness[BashResult]
    """
    ...
```

The type `Witness[BashResult]` is not just documentation—it's a theorem to prove.

### The Proof Obligation Chain

```
Type Signature → Proof Obligation → LLM Proof Attempt → Checker → Lemma
      ↓                                                            ↓
  AD-013 (Typed AGENTESE)                                   Used by NEXT generation
```

---

## Integration with Polynomial Functors (§10)

Path composition validity becomes provable:

```
Path A : Input₁ → Output₁
Path B : Input₂ → Output₂

Composition valid iff Output₁ ≅ Input₂

Proof: show type isomorphism via Lean4 tactics
```

The wiring diagram IS the proof structure. Invalid compositions are type errors that become proof failures.

---

## Examples

### Example 1: Composition Validity

```python
# Pipeline
pipeline = parse >> validate >> transform

# Proof obligation generated:
# ∀ input. parse(input) : Parsed
# ∀ parsed. validate(parsed) : Validated
# ∀ validated. transform(validated) : Output
# Therefore: pipeline(input) : Output
```

### Example 2: Failed Generation → Lemma

```python
# Generation fails because validate rejects malformed input
# ASHC extracts: "validate requires well-formed Parsed"
# Proof obligation: ∀ input. parse(input) → well_formed(parse(input))
# LLM attempts proof in Lean
# If successful: lemma added to dependency graph
# Next generation: LLM uses lemma to avoid same failure
```

### Example 3: Polymorphic Path Validity

```python
# Different observers, same path
await logos.invoke("world.house.manifest", architect_umwelt)  # → Blueprint
await logos.invoke("world.house.manifest", poet_umwelt)       # → Metaphor

# Proof obligation:
# ∀ observer. manifest(observer) : Projection(observer.type)
# Where Projection is a type family indexed by observer type
```

---

## The Proof Search Strategy

### Budget Allocation

| Phase | Budget | Purpose |
|-------|--------|---------|
| Quick | 10 attempts | Fast tactics (simp, auto, linarith) |
| Medium | 50 attempts | Structured search with hints |
| Deep | 200 attempts | Full exploration with backtracking |

### Hint Sources

1. **Causal graph**: Related proven lemmas
2. **Heritage papers**: Known patterns from Spivak, Robinson
3. **Failed attempts**: What tactics didn't work (avoid repetition)
4. **Type structure**: Polynomial functor laws suggest tactics

---

## Anti-patterns

- **Proving everything**: Too expensive; prioritize critical paths
- **Ignoring failed proofs**: Signal of spec ambiguity—investigate, don't suppress
- **Manual proof editing**: Proofs should regenerate from spec (Generative principle)
- **Proof hoarding**: Share lemmas across services via SynergyBus
- **Skipping the checker**: LLM claims are worthless without mechanical verification

---

## Implementation Phases

### Phase 1: Contracts ✅
- Add `ProofObligation`, `ProofAttempt`, `VerifiedLemma` dataclasses
- Status enums and type aliases
- See: `impl/claude/services/ashc/contracts.py`

### Phase 2: Obligation Extraction ✅
- Extract proof obligations from pytest failures
- Bounded context (5 lines max)
- Pattern-based variable extraction
- See: `impl/claude/services/ashc/obligation.py`

### Phase 3: Proof Search ✅
- LLM-assisted proof generation with budget management
- `LemmaDatabase` protocol for hint retrieval
- `InMemoryLemmaDatabase` stub for testing
- See: `impl/claude/services/ashc/search.py`

### Phase 4: Lemma Database ✅
**Goal**: Postgres-backed LemmaDatabase via D-gent

**Design Decisions**:
- **Postgres via D-gent** (not SQLite): Unified persistence layer, production-ready
- **TableAdapter bridge**: Leverage existing `agents/d/adapters/table_adapter.py`
- **Async throughout**: All operations async, matches D-gent patterns
- **Embeddings deferred**: Keyword matching now, Brain vectors later

**Stigmergic Design** (§13):
```
pheromone = usage_count
decay = age-based relevance scoring
reinforcement = increment usage on successful hint
emergent path = tactic selection evolves with corpus
```

**Deliverables**:
1. `models/ashc.py` - SQLAlchemy model `VerifiedLemmaModel` ✓
2. `services/ashc/persistence.py` - `PostgresLemmaDatabase` implementation ✓
3. `services/ashc/_tests/test_persistence.py` - 24 tests ✓
4. `services/providers.py` - `get_lemma_database()` provider ✓
5. Alembic migration for `ashc_verified_lemmas` table (deferred to first prod deploy)

**Exit Criteria**:
- [x] `PostgresLemmaDatabase` implements `LemmaDatabase` protocol ✓
- [x] Lemmas persist across restarts (verified by test) ✓
- [x] Usage count increments on hint retrieval ✓
- [x] `PostgresLemmaDatabase` wired to DI container via `get_lemma_database()` ✓

**Schema** (verified_lemmas table):
```sql
CREATE TABLE verified_lemmas (
    id VARCHAR PRIMARY KEY,
    statement TEXT NOT NULL,
    proof TEXT NOT NULL,
    checker VARCHAR NOT NULL,
    obligation_id VARCHAR NOT NULL,
    dependencies JSONB DEFAULT '[]',
    usage_count INT DEFAULT 0,
    verified_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_lemmas_statement ON verified_lemmas USING gin(to_tsvector('english', statement));
CREATE INDEX idx_lemmas_usage ON verified_lemmas(usage_count DESC);
```

### Phase 5: Checker Bridges (Future)
- `LeanBridge` for Lean4 proofs
- `DafnyBridge` for Dafny proofs (partially implemented)
- `VerusBridge` for Verus proofs

### Phase 6: Metrics & Observability (Future)
- Proof attempt success rate
- Lemma reuse frequency
- Budget consumption patterns
- Integration with Witness service

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Proof generation too slow | Cache proven lemmas; prune proof search tree |
| LLM can't discharge obligation | Fall back to evidence-only mode |
| Proof checker integration complex | Start with Dafny (simpler than Lean) |
| Over-formalization | Only prove critical path properties |
| Proof rot | Regenerate proofs on spec change |

---

## Connection to Stigmergic Cognition (§13)

Proofs are traces. The lemma database is a stigmergic surface:

| Stigmergy Concept | Proof System |
|-------------------|--------------|
| Pheromone trace | Proven lemma |
| Decay | Lemma relevance scoring |
| Reinforcement | Lemma reuse counting |
| Emergent path | Proof strategy evolution |

Agents leave proofs as traces. Future agents follow the proven paths.

---

## Cross-References

- **Heritage**: `spec/heritage.md` §12 (Kleppmann), §10 (Polynomial Functors)
- **Typed AGENTESE**: `spec/principles.md` AD-013
- **ASHC Core**: `spec/protocols/ashc.md` (to be created)
- **Witness Service**: `spec/protocols/witness-primitives.md`
- **Polynomial Agents**: `spec/principles.md` AD-002
- **Derivation Framework**: `spec/protocols/derivation-framework.md` — Proofs as evidence for derivation confidence

---

*"The proof is not formal—it's empirical. Run the tree a thousand times, and the pattern of nudges IS the proof. Now we can run the proof checker a thousand times, and the pattern of verified lemmas IS the certificate."*
