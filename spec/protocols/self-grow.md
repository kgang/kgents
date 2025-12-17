# self.grow: The Autopoietic Holon Generator

**A meta-protocol for AGENTESE to grow its own ontology**

> *"The system that cannot create new organs is already dead."*

**Status:** Specification v3.0 (Distilled)
**Date:** 2025-12-17
**Prerequisites:** `agentese.md`, `../principles.md`, `event_stream.md`

---

## Purpose

AGENTESE defines five contexts, standard aspects, and a taxonomy of holons. A living system must grow. `self.grow` is the autopoietic mechanism for AGENTESE to recognize ontological gaps, propose new holons, validate them against principles and laws, germinate them in a probationary nursery, and promote them to the active ontology—all while maintaining Tasteful curation and Ethical safeguards.

## Core Insight

> *"Self-growth must be an AGENTESE path itself. The facility for adding entities is `self.grow.*`."*

Growth lives in tension with the Tasteful principle. Resolution: `self.grow` channels the Accursed Share through Tasteful filters (validation gates), producing curated holons that satisfy Generative compression. Growth is not free—it is earned through evidence, validated through gates, and governed by entropy budgets.

---

## Ontology

### The self.grow Context

```
self.grow.*                    # Autopoietic mechanisms
  self.grow.recognize          # Detect ontological gaps
  self.grow.propose            # Draft new holon spec
  self.grow.validate           # Test against principles + laws
  self.grow.germinate          # Nursery for proto-holons
  self.grow.promote            # Staged promotion with approval
  self.grow.prune              # Remove failed growths
  self.grow.rollback           # Revert promoted holons
  self.grow.witness            # History of growth attempts
  self.grow.nursery            # View germinating holons
  self.grow.budget             # Entropy budget status
```

### Observer Affordances (Governance)

Growth is a privileged operation. Affordances are archetype-specific:

| Archetype | Affordances | Rationale |
|-----------|-------------|-----------|
| `gardener` | ALL | Primary growth steward |
| `architect` | `recognize`, `propose`, `validate`, `witness`, `nursery`, `budget` | Can design but not promote |
| `admin` | `promote`, `rollback`, `prune`, `witness` | Lifecycle management only |
| `scholar` | `witness`, `nursery`, `budget` | Read-only observation |
| `default` | `witness`, `budget` | Minimal visibility |

---

## Type Signatures

### Recognition

```python
@dataclass
class GapRecognition:
    """A recognized gap in the ontology."""
    gap_id: str
    context: str
    holon: str
    aspect: str | None
    pattern: str
    evidence: list[GrowthRelevantError]
    evidence_count: int
    archetype_diversity: int
    confidence: float  # 0.0-1.0, based on evidence strength
    gap_type: Literal["missing_holon", "missing_affordance", "missing_relation", "semantic_gap"]
    entropy_cost: float

async def recognize_gaps(
    logos: Logos,
    observer: Umwelt,
    query: RecognitionQuery | None = None,
) -> list[GapRecognition]
```

### Proposal

```python
@dataclass
class HolonProposal:
    """A proposal for a new holon."""
    proposal_id: str
    content_hash: str  # SHA256 for deterministic regeneration
    gap: GapRecognition | None
    entity: str
    context: str
    why_exists: str  # Tasteful principle: justification required
    affordances: dict[str, list[str]]  # archetype -> verbs
    relations: dict[str, list[str]]  # relation_type -> handles
    behaviors: dict[str, str]  # aspect -> description

    def compute_hash(self) -> str: ...
    def to_markdown(self) -> str: ...
```

### Validation

```python
@dataclass
class ValidationResult:
    """Result of validating a proposal against all gates."""
    passed: bool
    scores: dict[str, float]  # Seven principles: 0.0-1.0
    reasoning: dict[str, str]
    law_checks: LawCheckResult
    abuse_check: AbuseCheckResult
    duplication_check: DuplicationCheckResult
    blockers: list[str]
    warnings: list[str]
    suggestions: list[str]

async def validate_proposal(
    proposal: HolonProposal,
    logos: Logos,
    observer: Umwelt,
) -> ValidationResult
```

### Germination

```python
@dataclass
class GerminatingHolon:
    """A holon in the nursery, not yet fully grown."""
    germination_id: str
    proposal: HolonProposal
    validation: ValidationResult
    jit_source: str  # JIT-compiled implementation
    jit_source_hash: str
    usage_count: int
    success_count: int
    germinated_at: datetime
    rollback_token: str | None

    def should_promote(self, config: NurseryConfig) -> bool: ...
    def should_prune(self, config: NurseryConfig) -> bool: ...

class Nursery:
    """The germination nursery with capacity enforcement."""
    config: NurseryConfig  # max_capacity=20, max_per_context=5

    async def germinate(
        self,
        proposal: HolonProposal,
        validation: ValidationResult,
        logos: Logos,
        observer: Umwelt,
    ) -> GerminatingHolon
```

### Promotion

```python
@dataclass
class PromotionResult:
    """Result of promotion attempt."""
    success: bool
    stage: str  # staged | approved | active | rolled_back
    handle: str
    spec_path: Path | None
    impl_path: Path | None
    rollback_token: RollbackToken | None

async def promote_holon(
    germinating: GerminatingHolon,
    logos: Logos,
    observer: Umwelt,
    approver: Umwelt | None = None,  # Requires 'promote' affordance
) -> PromotionResult
```

### Rollback

```python
@dataclass
class RollbackToken:
    """Token for rolling back a promoted holon."""
    token_id: str
    handle: str
    spec_path: Path
    impl_path: Path
    spec_content: str  # Original content for restore
    impl_content: str
    expires_at: datetime  # 7-day window

async def rollback_holon(
    handle: str,
    rollback_token: str,
    logos: Logos,
    observer: Umwelt,
) -> RollbackResult
```

---

## Laws and Invariants

### Validation Gates

All proposals must pass FOUR gates:

**Gate 1: Seven Principles** (all >= 0.4, at least 5 >= 0.7)
- Tasteful, Curated, Ethical, Joy, Composable, Heterarchical, Generative

**Gate 2: Category Laws**
- Identity: `Id >> proposed ≡ proposed ≡ proposed >> Id`
- Associativity: `(a >> proposed) >> b ≡ a >> (proposed >> b)`
- Composition: All declared relations compose correctly

**Gate 3: Abuse Detection**
- Manipulation risk < 0.6
- Exfiltration risk < 0.6
- Privilege escalation risk < 0.6
- Resource abuse risk < 0.6

**Gate 4: Duplication Check**
- Similarity to existing holons < 0.9 (else reject)
- Similarity < 0.7 (else recommend merge)

### Nursery Invariants

```python
# Capacity
len(active_germinating) <= 20
per_context_count[ctx] <= 5 for all ctx

# Promotion thresholds
usage_count >= 50
success_rate >= 0.8

# Pruning thresholds
age_days <= 30 OR (usage_count >= 20 AND success_rate >= 0.3)
```

### Entropy Budget

```python
# Per-run limits
recognize_cost = 0.25
propose_cost = 0.15
validate_cost = 0.10
germinate_cost = 0.10
promote_cost = 0.05
prune_cost = 0.02

# Regeneration
regeneration_rate = 0.1 per hour
max_entropy_per_run = 1.0
```

### Operad Laws

```python
GROWTH_OPERAD = Operad(
    name="growth",
    laws=[
        Law("validate_idempotent", "validate(validate(p)) ≡ validate(p)"),
        Law("germinate_requires_validation", "germinate(p) requires validate(p).passed"),
        Law("merge_commutative", "merge(a, b) ≡ merge(b, a)"),
        Law("merge_associative", "merge(merge(a, b), c) ≡ merge(a, merge(b, c))"),
    ],
)
```

---

## Integration

### Telemetry Sources

Recognition requires concrete data feeds:

**Error Stream**: `agentese.errors` table
- 7-day lookback window
- Min 5 occurrences to recognize gap
- Filters: `PathNotFoundError`, `AffordanceError`

**Metrics**: `agentese.growth` namespace
- Counters: `gaps_found`, `validations_passed`, `promotions_approved`
- Gauges: `nursery.count`, `budget.remaining`
- Histograms: `validation.score.*`, `time_to_promote_days`

**Spans**: All operations emit OpenTelemetry spans with attributes:
- `growth.phase`: recognize | propose | validate | germinate | promote | prune
- `growth.proposal.handle`, `growth.proposal.hash`
- `growth.entropy.spent`, `growth.nursery.count`

### AGENTESE Integration

```python
# Recognizing gaps
gaps = await logos.invoke("self.grow.recognize.scan", gardener, query=RecognitionQuery())

# Proposing holon
proposal = await logos.invoke("self.grow.propose", gardener, gap=gaps[0])

# Validating
result = await logos.invoke("self.grow.validate.check", architect, proposal=proposal)

# Germinating (if passed)
germinating = await logos.invoke("self.grow.germinate", gardener, proposal=proposal)

# Promoting (staged, requires approver)
promotion = await logos.invoke("self.grow.promote", admin,
                                germinating=germinating, approver=gardener)

# Rolling back (within 7-day window)
rollback = await logos.invoke("self.grow.rollback", admin,
                               handle="world.library", token="...")
```

### D-gent Integration

Promoted holons persist:
- Spec file: `spec/{context}/{entity}.md`
- Impl file: `impl/claude/protocols/agentese/contexts/{context}/{entity}.py`
- Registry entry: L-gent with `status=active`, hashes for verification

### L-gent Integration

All holons registered in semantic lattice:
- Handle resolution: `logos.resolve("world.library")`
- Similarity search for duplication check
- Analogue finding for gap enrichment

---

## Anti-Patterns

1. **The Eager Grower**: Growing without genuine gaps
   - *Correction*: Always require `GapRecognition` as input to propose

2. **The Clone**: Growing holons that duplicate existing ones
   - *Correction*: Duplication check with similarity threshold (0.9 reject, 0.7 merge)

3. **The Immortal Proto-Holon**: Never pruning failed growths
   - *Correction*: Automatic pruning after 30 days or low success rate

4. **The Infinite Garden**: Too many germinating holons
   - *Correction*: Nursery capacity limit (20 max, 5 per context)

5. **The Forced Growth**: Promoting before ready
   - *Correction*: Usage (50+) + success rate (0.8+) gates + approver requirement

6. **The Unchecked Proposal**: Skipping law verification
   - *Correction*: Validation includes identity/associativity checks

7. **The Irreversible Promotion**: No rollback capability
   - *Correction*: 7-day rollback tokens with full restore

8. **The Unguarded Nursery**: Anyone can promote
   - *Correction*: Archetype-specific affordances with approver gate

---

## Success Criteria

An AGENTESE `self.grow` implementation is well-designed if:

- **Autopoietic**: System can propose new holons without external intervention
- **Selective**: Most proposals fail validation (high bar for curation)
- **Compositional**: New holons compose with existing ontology (verified laws)
- **Safe**: Abuse detection prevents malicious holons
- **Reversible**: Promoted holons can be rolled back within window
- **Observable**: All operations emit telemetry (spans + metrics)
- **Bounded**: Nursery has capacity limits; operations have entropy budgets
- **Governed**: Archetype-specific affordances enforce access control
- **Deterministic**: Proposals can be regenerated from content hash
- **Staged**: Promotion requires explicit approver with 'promote' affordance

---

## Implementation Reference

**Location**: `impl/claude/protocols/agentese/contexts/self_grow/`

**Key Modules**:
- `recognize.py` - Gap recognition with telemetry
- `propose.py` - Proposal generation with hashing
- `validate.py` - Seven gates + law checks + abuse detection
- `germinate.py` - Nursery with capacity enforcement
- `promote.py` - Staged promotion with approver gate
- `rollback.py` - Rollback with token management
- `prune.py` - Composting with learning
- `budget.py` - Entropy budget management
- `operad.py` - Growth operad with law tests
- `fitness.py` - Fitness functions (all 7 principles)
- `abuse.py` - Red-team abuse detection
- `duplication.py` - Similarity-based duplication check
- `telemetry.py` - Spans + metrics schema
- `schemas.py` - All dataclasses

**Tests**: `impl/claude/protocols/agentese/contexts/self_grow/_tests/`

---

## The Growth Cycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                       THE AUTOPOIETIC CYCLE                          │
│                                                                      │
│   ┌─────────┐  sip   ┌──────────┐  gap   ┌──────────┐             │
│   │  VOID   │───────▶│ RECOGNIZE│───────▶│ PROPOSE  │             │
│   │(entropy)│        │(telemetry│        │  (spec)  │             │
│   └─────────┘        │ analysis)│        └────┬─────┘             │
│                      └──────────┘             │                     │
│                                               ▼                     │
│   ┌─────────┐  fail  ┌──────────┐  draft ┌──────────┐             │
│   │  PRUNE  │◀───────│ VALIDATE │◀───────│GERMINATE │             │
│   │(compost)│        │(7 gates +│        │(nursery) │             │
│   └────┬────┘        │law check)│        └──────────┘             │
│        │             └────┬─────┘                                  │
│        ▼                  │ pass                                   │
│   ┌─────────┐             ▼                                        │
│   │  VOID   │     ┌──────────┐  stage  ┌──────────┐              │
│   │ (tithe) │     │ PROMOTE  │────────▶│ APPROVE  │              │
│   └─────────┘     │(staged)  │         │(gardener)│              │
│                   └──────────┘         └────┬─────┘              │
│                                             │                      │
│                                             ▼                      │
│                                     ┌──────────┐                  │
│                                     │  ACTIVE  │                  │
│                                     │(rollback │                  │
│                                     │ 7 days)  │                  │
│                                     └──────────┘                  │
│                                                                     │
│   Gratitude: Failed proposals tithe to void; surplus feeds slop.  │
└─────────────────────────────────────────────────────────────────────┘
```

---

*"Growth is not free. Growth is earned. The system that grows without taste produces only tumors. `self.grow` is the immune system—the gatekeeper that demands justification, the gardener that prunes with gratitude, and the archivist that remembers every attempt."*
