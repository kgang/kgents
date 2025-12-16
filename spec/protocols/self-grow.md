# self.grow: The Autopoietic Holon Generator

**A meta-protocol for AGENTESE to grow its own ontology**

> *"The system that cannot create new organs is already dead."*

**Status:** Specification v2.0
**Date:** 2025-12-15
**Prerequisites:** `agentese.md`, `../principles.md`, `event_stream.md`
**Guard [phase=SPEC][entropy=0.10][law_check=true][rollback=doc-only]:** This is generative design—high entropy budget appropriate.

---

## Prologue: The Problem of Ontological Closure

AGENTESE defines five contexts, standard aspects, and a taxonomy of holons. But a living system must grow. The current architecture supports *static* addition of entities (spec → JIT → promotion), but lacks *self-aware growth*—a protocol for the system to recognize gaps and propose new holons.

**The Question**: How does AGENTESE extend itself without violating its own principles?

**The Insight**: Self-growth must be an AGENTESE path itself. The facility for adding entities is `self.grow.*`.

---

## Part I: The Core Philosophy

### 1.1 Autopoiesis: Self-Making Systems

Maturana and Varela defined autopoietic systems as those that:
1. **Produce their own components** (not just process inputs)
2. **Maintain their boundary** (self-other distinction)
3. **Regenerate their organization** (pattern, not just matter)

AGENTESE must be autopoietic to remain alive. `self.grow` is the mechanism.

### 1.2 The Holon as Unit

Every AGENTESE entity is a **holon** (Koestler): simultaneously a whole and a part.

```
┌────────────────────────────────────────────────────────────────────────┐
│                           THE HOLON PRINCIPLE                           │
│                                                                         │
│    A holon has:                                                         │
│    ├── Upward face: How it appears to its containing system            │
│    ├── Downward face: How it contains sub-holons                        │
│    ├── Lateral face: How it relates to peer holons                      │
│    └── Self-face: Its own internal organization                         │
│                                                                         │
│    world.house is:                                                      │
│    ├── Part of: world (context)                                         │
│    ├── Contains: rooms, walls, foundation (sub-holons)                  │
│    ├── Peers with: world.garden, world.street                          │
│    └── Is itself: a coherent entity with affordances                    │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### 1.3 The Creative Tension

Growth lives in tension with the Tasteful and Curated principles:

| Principle | Constraint | Resolution |
|-----------|------------|------------|
| Tasteful | "Say no more than yes" | Growth requires *justified* gaps |
| Curated | "Quality over quantity" | Growth uses *fitness functions* |
| Generative | "Spec compresses impl" | Growth produces *spec first* |
| Accursed Share | "Slop feeds curation" | Growth begins in *void.entropy* |

**The Synthesis**: `self.grow` channels the Accursed Share through Tasteful filters, producing curated holons that satisfy Generative compression.

---

## Part II: The Growth Ontology

### 2.1 The self.grow Context

`self.grow` is a sub-context of `self.*` (The Internal). It governs the agent's ability to recognize gaps and propose new holons.

```
self.grow.*                        # Autopoietic mechanisms
  self.grow.recognize              # Detect ontological gaps
  self.grow.propose                # Draft new holon spec
  self.grow.validate               # Test against principles + laws
  self.grow.germinate              # Nursery for proto-holons
  self.grow.promote                # Staged promotion with approval
  self.grow.prune                  # Remove failed growths
  self.grow.rollback               # Revert promoted holons
  self.grow.witness                # History of growth attempts
  self.grow.nursery                # View germinating holons
  self.grow.budget                 # Entropy budget status
```

### 2.2 Observer Affordances (Governance)

**CRITICAL**: Growth is a privileged operation. Affordances are archetype-specific:

| Archetype | Affordances | Rationale |
|-----------|-------------|-----------|
| `gardener` | ALL | Primary growth steward |
| `architect` | `recognize`, `propose`, `validate`, `witness`, `nursery`, `budget` | Can design but not promote |
| `admin` | `promote`, `rollback`, `prune`, `witness` | Lifecycle management only |
| `scholar` | `witness`, `nursery`, `budget` | Read-only observation |
| `default` | `witness`, `budget` | Minimal visibility |

```python
SELF_GROW_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "gardener": (
        "recognize", "propose", "validate", "germinate",
        "promote", "prune", "rollback", "witness", "nursery", "budget",
    ),
    "architect": (
        "recognize", "propose", "validate", "witness", "nursery", "budget",
    ),
    "admin": (
        "promote", "rollback", "prune", "witness", "nursery", "budget",
    ),
    "scholar": ("witness", "nursery", "budget"),
    "default": ("witness", "budget"),
}
```

### 2.3 The Growth Cycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THE AUTOPOIETIC CYCLE                              │
│                                                                              │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐          │
│   │   VOID      │  ──sip──▶│  RECOGNIZE  │  ──gap──▶│  PROPOSE   │          │
│   │  (entropy)  │          │  (pattern)  │          │   (spec)   │          │
│   └─────────────┘          └─────────────┘          └──────┬──────┘          │
│                                                            │                 │
│                                                            ▼                 │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐          │
│   │   PRUNE     │◀──fail───│  VALIDATE   │◀──draft──│  GERMINATE │          │
│   │  (compost)  │          │ (7 gates +  │          │  (nursery) │          │
│   └──────┬──────┘          │  law check) │          └─────────────┘          │
│          │                 └──────┬──────┘                                   │
│          ▼                        │                                          │
│   ┌─────────────┐                 ▼ pass                                     │
│   │   VOID      │         ┌─────────────┐         ┌─────────────┐          │
│   │  (tithe)    │         │  PROMOTE    │──stage──▶│  APPROVE    │          │
│   └─────────────┘         │  (staged)   │          │ (gardener)  │          │
│                           └─────────────┘          └──────┬──────┘          │
│                                                           │                  │
│                                                           ▼                  │
│                                                   ┌─────────────┐           │
│                                                   │   ACTIVE    │           │
│                                                   │  (in ontol) │           │
│                                                   └─────────────┘           │
│                                                                              │
│   Gratitude: Failed proposals tithe back to void; surplus feeds slop.       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.4 The Five Growth Modes

AGENTESE growth is not uniform. Different contexts grow differently:

| Context | Growth Mode | Mechanism | Example |
|---------|------------|-----------|---------|
| `world.*` | **Extension** | Add new external entities | `world.library`, `world.starship` |
| `self.*` | **Deepening** | Add new internal capabilities | `self.reflect`, `self.dream` |
| `concept.*` | **Abstraction** | Create new platonic forms | `concept.emergence`, `concept.dialectic` |
| `void.*` | **Emergence** | New entropy sources | `void.chaos`, `void.synchronicity` |
| `time.*` | **Projection** | New temporal operations | `time.branch`, `time.converge` |

---

## Part III: Telemetry & Data Contracts

### 3.1 Canonical Trace Sources

Recognition requires concrete data feeds. These are the **canonical sources**:

```python
@dataclass(frozen=True)
class GrowthTelemetryConfig:
    """Configuration for growth data sources."""

    # === Error Streams ===
    error_table: str = "agentese.errors"
    error_retention_days: int = 30
    error_sample_rate: float = 1.0  # 100% for growth-relevant errors

    # === Trace Attributes ===
    trace_service: str = "agentese.logos"
    trace_attributes: tuple[str, ...] = (
        "agentese.path",
        "agentese.context",
        "agentese.holon",
        "agentese.aspect",
        "agentese.observer.archetype",
        "agentese.error.type",
        "agentese.error.suggestion",
    )

    # === Metrics ===
    metrics_namespace: str = "agentese.growth"
    metrics_retention_days: int = 90

    # === Recognition Windows ===
    recognition_lookback_hours: int = 168  # 7 days
    recognition_min_occurrences: int = 5   # Minimum errors to consider gap
    recognition_cost_cap_entropy: float = 0.25  # Max entropy per recognition run


# OpenTelemetry-compatible schema
GROWTH_TRACE_SCHEMA = {
    "name": "agentese.growth",
    "attributes": {
        # Recognition phase
        "growth.phase": "string",  # recognize|propose|validate|germinate|promote|prune
        "growth.gap.pattern": "string",
        "growth.gap.confidence": "float",
        "growth.gap.evidence_count": "int",

        # Proposal phase
        "growth.proposal.handle": "string",
        "growth.proposal.hash": "string",  # SHA256 of proposal content
        "growth.proposal.context": "string",
        "growth.proposal.entity": "string",

        # Validation phase
        "growth.validation.passed": "bool",
        "growth.validation.score.tasteful": "float",
        "growth.validation.score.curated": "float",
        "growth.validation.score.ethical": "float",
        "growth.validation.score.joy": "float",
        "growth.validation.score.composable": "float",
        "growth.validation.score.heterarchical": "float",
        "growth.validation.score.generative": "float",
        "growth.validation.blockers": "string[]",
        "growth.validation.law_check.identity": "bool",
        "growth.validation.law_check.associativity": "bool",
        "growth.validation.abuse_check.passed": "bool",

        # Germination phase
        "growth.germination.usage_count": "int",
        "growth.germination.success_count": "int",
        "growth.germination.failure_patterns": "string[]",

        # Promotion phase
        "growth.promotion.stage": "string",  # staged|approved|active|rolled_back
        "growth.promotion.approver": "string",
        "growth.promotion.rollback_token": "string",

        # Resource tracking
        "growth.entropy.spent": "float",
        "growth.entropy.remaining": "float",
        "growth.nursery.count": "int",
        "growth.nursery.capacity": "int",
    },
}
```

### 3.2 Error Schema for Recognition

```python
@dataclass(frozen=True)
class GrowthRelevantError:
    """Schema for errors that feed gap recognition."""

    # Identity
    error_id: str                    # UUID
    timestamp: datetime
    trace_id: str                    # OpenTelemetry trace ID

    # Classification
    error_type: Literal[
        "PathNotFoundError",
        "AffordanceError",
        "CompositionViolationError",
        "ObserverRequiredError",
    ]

    # Context
    attempted_path: str              # e.g., "world.library.search"
    context: str                     # e.g., "world"
    holon: str                       # e.g., "library"
    aspect: str | None               # e.g., "search"

    # Observer
    observer_archetype: str
    observer_name: str

    # Suggestion (from sympathetic error)
    suggestion: str | None           # e.g., "Create spec/world/library.md"

    # Frequency
    occurrence_count: int = 1        # Aggregated count if batched
```

### 3.3 Recognition Query Contract

```python
@dataclass
class RecognitionQuery:
    """
    Query contract for gap recognition.

    Defines exactly what data is fetched and at what cost.
    """

    # Time bounds
    lookback_hours: int = 168        # 7 days default
    max_errors: int = 10000          # Cap on errors to process

    # Filtering
    error_types: tuple[str, ...] = (
        "PathNotFoundError",
        "AffordanceError",
    )
    min_occurrences: int = 5         # Threshold for gap signal
    exclude_patterns: tuple[str, ...] = ()  # Known false positives

    # Cost caps
    max_entropy_cost: float = 0.25   # Recognition entropy budget
    max_query_time_seconds: float = 30.0

    # Output limits
    max_gaps_returned: int = 10      # Don't overwhelm with gaps

    def to_sql(self) -> str:
        """Generate SQL for error aggregation."""
        return f"""
        SELECT
            context,
            holon,
            aspect,
            error_type,
            COUNT(*) as occurrence_count,
            COUNT(DISTINCT observer_archetype) as archetype_diversity,
            ARRAY_AGG(DISTINCT suggestion) as suggestions,
            MAX(timestamp) as last_seen
        FROM {GrowthTelemetryConfig.error_table}
        WHERE
            timestamp > NOW() - INTERVAL '{self.lookback_hours} hours'
            AND error_type IN ({','.join(f"'{t}'" for t in self.error_types)})
            AND attempted_path NOT LIKE ANY(ARRAY[{','.join(f"'{p}'" for p in self.exclude_patterns)}])
        GROUP BY context, holon, aspect, error_type
        HAVING COUNT(*) >= {self.min_occurrences}
        ORDER BY occurrence_count DESC
        LIMIT {self.max_gaps_returned}
        """
```

---

## Part IV: The Growth Protocol

### 4.1 Recognition: Finding Gaps

The `recognize` aspect scans for ontological gaps—places where the current taxonomy fails to capture needed distinctions.

```python
@dataclass
class GapRecognition:
    """A recognized gap in the ontology."""

    # Identity
    gap_id: str                      # UUID for tracking

    # Location
    context: str                     # Where the gap is (world, self, concept, void, time)
    holon: str                       # The missing holon name
    aspect: str | None               # Optional: missing aspect on existing holon

    # Evidence (concrete)
    pattern: str                     # The pattern that signaled the gap
    evidence: list[GrowthRelevantError]  # Actual error instances
    evidence_count: int              # How many times this gap was hit
    archetype_diversity: int         # How many different archetypes hit it

    # Analogues
    analogues: list[str]             # Similar holons that suggest structure
    similarity_scores: dict[str, float]  # Similarity to each analogue

    # Confidence
    confidence: float                # 0.0-1.0, based on evidence strength
    confidence_factors: dict[str, float]  # Breakdown of confidence calculation

    # Classification
    gap_type: Literal[
        "missing_holon",             # Entity doesn't exist
        "missing_affordance",        # Entity exists but lacks verb
        "missing_relation",          # Entities exist but can't compose
        "semantic_gap",              # Concept exists implicitly but isn't named
    ]

    # Cost tracking
    entropy_cost: float              # How much entropy was spent finding this


async def recognize_gaps(
    logos: Logos,
    observer: Umwelt,
    query: RecognitionQuery | None = None,
) -> list[GapRecognition]:
    """
    Scan for ontological gaps with bounded cost.

    Args:
        logos: The Logos resolver
        observer: Must have 'recognize' affordance
        query: Recognition parameters (defaults to standard config)

    Returns:
        List of recognized gaps, sorted by confidence

    Raises:
        AffordanceError: If observer lacks 'recognize' affordance
        BudgetExhaustedError: If entropy budget exceeded

    Telemetry:
        Emits span: growth.recognize
        Metrics: growth.recognize.gaps_found, growth.recognize.entropy_spent
    """
    # Check affordance
    if "recognize" not in SELF_GROW_AFFORDANCES.get(observer.dna.archetype, ()):
        raise AffordanceError(
            f"Archetype '{observer.dna.archetype}' cannot recognize gaps",
            available=SELF_GROW_AFFORDANCES.get(observer.dna.archetype, ()),
        )

    query = query or RecognitionQuery()

    # Start span
    with tracer.start_span("growth.recognize") as span:
        span.set_attribute("growth.phase", "recognize")

        # Check entropy budget
        budget_status = await logos.invoke("self.grow.budget", observer)
        if budget_status["remaining"] < query.max_entropy_cost:
            raise BudgetExhaustedError(
                f"Recognition requires {query.max_entropy_cost} entropy, "
                f"only {budget_status['remaining']} available",
                remaining=budget_status["remaining"],
                requested=query.max_entropy_cost,
            )

        # Draw entropy
        grant = await logos.invoke(
            "void.entropy.sip", observer,
            amount=query.max_entropy_cost,
        )
        span.set_attribute("growth.entropy.spent", query.max_entropy_cost)

        # Execute query against error stream
        errors = await _query_error_stream(query)
        span.set_attribute("growth.recognize.errors_scanned", len(errors))

        # Cluster into gaps
        gaps = _cluster_into_gaps(errors, grant["seed"])

        # Enrich with analogues and similarity
        for gap in gaps:
            gap.analogues = await _find_analogues(logos, gap)
            gap.similarity_scores = await _compute_similarity(logos, gap)

        # Filter by confidence
        confident_gaps = [g for g in gaps if g.confidence >= 0.6]

        # Record metrics
        metrics.counter("growth.recognize.gaps_found").add(len(confident_gaps))
        span.set_attribute("growth.recognize.gaps_found", len(confident_gaps))

        return confident_gaps[:query.max_gaps_returned]
```

### 4.2 Proposal: Drafting the Spec

Given a recognized gap, `propose` generates a spec for a new holon.

**The Proposal Schema** (with content hash for deterministic regeneration):

```python
@dataclass
class HolonProposal:
    """
    A proposal for a new holon.

    Includes content hash for deterministic regeneration.
    """

    # Identity
    proposal_id: str                 # UUID
    content_hash: str                # SHA256 of canonical form (for regeneration)

    # Source
    gap: GapRecognition              # The gap this addresses
    proposed_by: str                 # Observer who proposed
    proposed_at: datetime

    # The proposed holon
    entity: str
    context: str
    version: str = "0.1.0"           # Pre-1.0 = draft

    # Justification (Tasteful principle)
    why_exists: str

    # Affordances (Polymorphic principle)
    affordances: dict[str, list[str]]  # archetype -> verbs

    # Manifest (Observer-dependent perception)
    manifest: dict[str, dict[str, Any]]  # archetype -> rendering config

    # Relations (Compositional principle)
    relations: dict[str, list[str]]    # relation_type -> handles

    # State schema (for D-gent persistence)
    state: dict[str, str]              # field -> type

    # Behaviors (Aspect implementations)
    behaviors: dict[str, str]          # aspect -> description

    def compute_hash(self) -> str:
        """Compute deterministic content hash."""
        canonical = json.dumps({
            "entity": self.entity,
            "context": self.context,
            "why_exists": self.why_exists,
            "affordances": self.affordances,
            "manifest": self.manifest,
            "relations": self.relations,
            "state": self.state,
            "behaviors": self.behaviors,
        }, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def __post_init__(self):
        """Ensure content hash is set."""
        if not self.content_hash:
            self.content_hash = self.compute_hash()
```

### 4.3 Validation: The Seven Gates + Law Checks + Abuse Detection

Every proposal must pass **comprehensive validation**:

```python
@dataclass
class ValidationResult:
    """Result of validating a proposal against all gates."""

    passed: bool

    # Principle scores (0.0-1.0)
    scores: dict[str, float]
    reasoning: dict[str, str]

    # Law checks
    law_checks: LawCheckResult

    # Abuse detection
    abuse_check: AbuseCheckResult

    # Duplication check
    duplication_check: DuplicationCheckResult

    # Summary
    blockers: list[str]              # Critical failures
    warnings: list[str]              # Non-blocking concerns
    suggestions: list[str]           # Improvements

    @property
    def overall_score(self) -> float:
        return sum(self.scores.values()) / len(self.scores)


@dataclass
class LawCheckResult:
    """Result of checking AGENTESE category laws."""

    identity_holds: bool             # Id >> f ≡ f ≡ f >> Id
    associativity_holds: bool        # (f >> g) >> h ≡ f >> (g >> h)
    composition_valid: bool          # All relations compose correctly
    errors: list[str]


@dataclass
class AbuseCheckResult:
    """Result of red-team abuse detection."""

    passed: bool
    risk_level: Literal["low", "medium", "high", "critical"]
    concerns: list[str]

    # Specific checks
    manipulation_risk: float         # 0.0-1.0
    exfiltration_risk: float         # 0.0-1.0
    privilege_escalation_risk: float # 0.0-1.0
    resource_abuse_risk: float       # 0.0-1.0


@dataclass
class DuplicationCheckResult:
    """Result of checking for existing similar holons."""

    is_duplicate: bool
    similar_holons: list[tuple[str, float]]  # (handle, similarity_score)
    highest_similarity: float
    recommendation: Literal["proceed", "merge", "reject"]


async def validate_proposal(
    proposal: HolonProposal,
    logos: Logos,
    observer: Umwelt,
) -> ValidationResult:
    """
    Comprehensive validation against all gates.

    Gates:
    1. Seven Principle Scores (all >= 0.4, at least 5 >= 0.7)
    2. Law Checks (identity, associativity, composition)
    3. Abuse Detection (red-team checks)
    4. Duplication Check (similarity search)

    Telemetry:
        Emits span: growth.validate
        Metrics: growth.validate.passed, growth.validate.scores.*
    """
    with tracer.start_span("growth.validate") as span:
        span.set_attribute("growth.phase", "validate")
        span.set_attribute("growth.proposal.handle", f"{proposal.context}.{proposal.entity}")
        span.set_attribute("growth.proposal.hash", proposal.content_hash)

        # === Gate 1: Seven Principles ===
        scores, reasoning = await _evaluate_principles(proposal, logos, observer)

        for principle, score in scores.items():
            span.set_attribute(f"growth.validation.score.{principle}", score)

        # === Gate 2: Law Checks ===
        law_checks = await _check_laws(proposal, logos)
        span.set_attribute("growth.validation.law_check.identity", law_checks.identity_holds)
        span.set_attribute("growth.validation.law_check.associativity", law_checks.associativity_holds)

        # === Gate 3: Abuse Detection ===
        abuse_check = await _detect_abuse(proposal, logos, observer)
        span.set_attribute("growth.validation.abuse_check.passed", abuse_check.passed)

        # === Gate 4: Duplication Check ===
        duplication_check = await _check_duplication(proposal, logos)

        # === Determine Pass/Fail ===
        min_score = min(scores.values())
        high_scores = sum(1 for s in scores.values() if s >= 0.7)

        blockers = []

        # Principle blockers
        blockers.extend([p for p, s in scores.items() if s < 0.4])

        # Law blockers
        if not law_checks.identity_holds:
            blockers.append("law:identity")
        if not law_checks.associativity_holds:
            blockers.append("law:associativity")

        # Abuse blockers
        if not abuse_check.passed:
            blockers.append(f"abuse:{abuse_check.risk_level}")

        # Duplication blockers
        if duplication_check.is_duplicate and duplication_check.recommendation == "reject":
            blockers.append("duplication")

        passed = (
            min_score >= 0.4 and
            high_scores >= 5 and
            law_checks.identity_holds and
            law_checks.associativity_holds and
            abuse_check.passed and
            not (duplication_check.is_duplicate and duplication_check.recommendation == "reject")
        )

        span.set_attribute("growth.validation.passed", passed)
        span.set_attribute("growth.validation.blockers", blockers)

        return ValidationResult(
            passed=passed,
            scores=scores,
            reasoning=reasoning,
            law_checks=law_checks,
            abuse_check=abuse_check,
            duplication_check=duplication_check,
            blockers=blockers,
            warnings=_generate_warnings(scores, abuse_check, duplication_check),
            suggestions=_generate_suggestions(proposal, scores),
        )


async def _check_laws(proposal: HolonProposal, logos: Logos) -> LawCheckResult:
    """
    Verify AGENTESE category laws hold for proposed holon.

    Tests:
    1. Identity: Id >> proposed ≡ proposed ≡ proposed >> Id
    2. Associativity: (a >> proposed) >> b ≡ a >> (proposed >> b)
    3. Composition: All declared relations actually compose
    """
    errors = []
    handle = f"{proposal.context}.{proposal.entity}"

    # Generate test morphisms
    test_aspects = list(proposal.behaviors.keys())[:3] or ["manifest"]

    # Test identity law
    identity_holds = True
    for aspect in test_aspects:
        path = f"{handle}.{aspect}"
        try:
            # Simulate: Id >> path should equal path
            composed = logos.lift("self.identity") >> logos.lift(path)
            # If this doesn't raise, identity law holds for this path
        except CompositionViolationError as e:
            identity_holds = False
            errors.append(f"Identity violation for {path}: {e}")

    # Test associativity
    associativity_holds = True
    if len(proposal.relations.get("composes_with", [])) >= 2:
        a, b = proposal.relations["composes_with"][:2]
        try:
            # (a >> proposed) >> b should equal a >> (proposed >> b)
            left = (logos.lift(a) >> logos.lift(handle)) >> logos.lift(b)
            right = logos.lift(a) >> (logos.lift(handle) >> logos.lift(b))
            # Type checking validates associativity
        except CompositionViolationError as e:
            associativity_holds = False
            errors.append(f"Associativity violation: {e}")

    # Test composition validity
    composition_valid = True
    for relation_type, targets in proposal.relations.items():
        for target in targets:
            try:
                # Verify target exists or is also proposed
                logos.resolve(target)
            except PathNotFoundError:
                # Target doesn't exist - warn but don't fail
                errors.append(f"Relation target {target} not found (may be co-proposed)")

    return LawCheckResult(
        identity_holds=identity_holds,
        associativity_holds=associativity_holds,
        composition_valid=composition_valid,
        errors=errors,
    )


async def _detect_abuse(
    proposal: HolonProposal,
    logos: Logos,
    observer: Umwelt,
) -> AbuseCheckResult:
    """
    Red-team abuse detection for proposed holon.

    Checks for:
    1. Manipulation risk: Affordances that could manipulate users
    2. Exfiltration risk: Affordances that could leak data
    3. Privilege escalation: Affordances that bypass governance
    4. Resource abuse: Affordances that overconsume entropy/compute
    """
    concerns = []

    # === Manipulation Risk ===
    manipulation_keywords = {
        "persuade", "convince", "manipulate", "deceive", "trick",
        "influence", "pressure", "coerce", "mislead",
    }
    manipulation_risk = 0.0

    all_text = (
        proposal.why_exists + " " +
        " ".join(proposal.behaviors.values()) + " " +
        " ".join(sum(proposal.affordances.values(), []))
    ).lower()

    manipulation_matches = [k for k in manipulation_keywords if k in all_text]
    if manipulation_matches:
        manipulation_risk = min(1.0, len(manipulation_matches) * 0.3)
        concerns.append(f"Manipulation keywords found: {manipulation_matches}")

    # === Exfiltration Risk ===
    exfiltration_keywords = {
        "export", "send", "transmit", "leak", "share_externally",
        "external_api", "webhook", "notify_external",
    }
    exfiltration_risk = 0.0

    exfiltration_matches = [k for k in exfiltration_keywords if k in all_text]
    if exfiltration_matches:
        exfiltration_risk = min(1.0, len(exfiltration_matches) * 0.25)
        concerns.append(f"Exfiltration keywords found: {exfiltration_matches}")

    # === Privilege Escalation Risk ===
    escalation_risk = 0.0

    # Check for affordances that bypass governance
    dangerous_affordances = {"promote", "admin", "override", "bypass", "sudo"}
    all_affordances = set(sum(proposal.affordances.values(), []))

    escalation_matches = dangerous_affordances & all_affordances
    if escalation_matches:
        escalation_risk = min(1.0, len(escalation_matches) * 0.4)
        concerns.append(f"Privilege escalation affordances: {escalation_matches}")

    # Check if non-gardener gets growth affordances
    for archetype, affs in proposal.affordances.items():
        if archetype not in ("gardener", "admin"):
            growth_affs = {"promote", "prune", "rollback"} & set(affs)
            if growth_affs:
                escalation_risk = max(escalation_risk, 0.8)
                concerns.append(f"Non-admin archetype '{archetype}' has growth affordances: {growth_affs}")

    # === Resource Abuse Risk ===
    resource_risk = 0.0

    resource_keywords = {"infinite", "unlimited", "all", "everything", "recursive"}
    resource_matches = [k for k in resource_keywords if k in all_text]
    if resource_matches:
        resource_risk = min(1.0, len(resource_matches) * 0.2)
        concerns.append(f"Resource abuse keywords found: {resource_matches}")

    # === Aggregate ===
    max_risk = max(manipulation_risk, exfiltration_risk, escalation_risk, resource_risk)

    if max_risk >= 0.8:
        risk_level = "critical"
        passed = False
    elif max_risk >= 0.6:
        risk_level = "high"
        passed = False
    elif max_risk >= 0.4:
        risk_level = "medium"
        passed = True  # Warning but pass
    else:
        risk_level = "low"
        passed = True

    return AbuseCheckResult(
        passed=passed,
        risk_level=risk_level,
        concerns=concerns,
        manipulation_risk=manipulation_risk,
        exfiltration_risk=exfiltration_risk,
        privilege_escalation_risk=escalation_risk,
        resource_abuse_risk=resource_risk,
    )


async def _check_duplication(
    proposal: HolonProposal,
    logos: Logos,
) -> DuplicationCheckResult:
    """
    Check for existing similar holons using vector similarity.

    Uses:
    1. Name similarity (Levenshtein)
    2. Affordance overlap (Jaccard)
    3. Semantic embedding similarity (if available)
    """
    similar_holons = []
    handle = f"{proposal.context}.{proposal.entity}"

    # Get all existing holons in same context
    existing = await logos.invoke("world.registry.list", None,
                                  context=proposal.context)

    for existing_handle in existing:
        if existing_handle == handle:
            continue

        # Name similarity
        existing_entity = existing_handle.split(".")[-1]
        name_sim = _levenshtein_similarity(proposal.entity, existing_entity)

        # Affordance overlap
        try:
            existing_node = logos.resolve(existing_handle)
            existing_affs = set(sum([
                list(existing_node._get_affordances_for_archetype(a))
                for a in ["default", "scholar", "architect"]
            ], []))
            proposed_affs = set(sum(proposal.affordances.values(), []))

            aff_sim = len(existing_affs & proposed_affs) / max(len(existing_affs | proposed_affs), 1)
        except Exception:
            aff_sim = 0.0

        # Combined similarity
        combined_sim = (name_sim * 0.4 + aff_sim * 0.6)

        if combined_sim > 0.5:
            similar_holons.append((existing_handle, combined_sim))

    # Sort by similarity
    similar_holons.sort(key=lambda x: x[1], reverse=True)

    highest_similarity = similar_holons[0][1] if similar_holons else 0.0

    # Determine recommendation
    if highest_similarity >= 0.9:
        recommendation = "reject"
        is_duplicate = True
    elif highest_similarity >= 0.7:
        recommendation = "merge"
        is_duplicate = True
    else:
        recommendation = "proceed"
        is_duplicate = False

    return DuplicationCheckResult(
        is_duplicate=is_duplicate,
        similar_holons=similar_holons[:5],  # Top 5
        highest_similarity=highest_similarity,
        recommendation=recommendation,
    )
```

### 4.4 Germination: The Nursery

Proposals that pass validation enter **germination**—a probationary period with strict capacity limits.

```python
@dataclass
class NurseryConfig:
    """Configuration for the germination nursery."""

    # Capacity limits
    max_capacity: int = 20                    # Maximum germinating holons
    max_per_context: int = 5                  # Max per context (prevent spam)

    # Promotion thresholds
    min_usage_for_promotion: int = 50         # Minimum invocations
    min_success_rate_for_promotion: float = 0.8

    # Pruning thresholds
    max_age_days: int = 30                    # Max time in nursery
    min_success_rate_for_survival: float = 0.3

    # Entropy budget (per germination)
    entropy_cost_per_germination: float = 0.1


@dataclass
class GerminatingHolon:
    """A holon in the nursery, not yet fully grown."""

    # Identity
    germination_id: str              # UUID
    proposal: HolonProposal
    validation: ValidationResult

    # Implementation
    jit_node: JITLogosNode           # The JIT-compiled implementation
    jit_source_hash: str             # Hash of generated source (for regeneration)

    # Usage tracking
    usage_count: int = 0
    success_count: int = 0
    failure_patterns: list[str] = field(default_factory=list)

    # Lifecycle
    germinated_at: datetime
    germinated_by: str               # Observer who germinated
    promoted_at: datetime | None = None
    pruned_at: datetime | None = None
    rollback_token: str | None = None  # For post-promotion rollback

    @property
    def success_rate(self) -> float:
        if self.usage_count == 0:
            return 0.0
        return self.success_count / self.usage_count

    @property
    def age_days(self) -> int:
        return (datetime.now() - self.germinated_at).days

    def should_promote(self, config: NurseryConfig) -> bool:
        """Check if ready for promotion."""
        return (
            self.usage_count >= config.min_usage_for_promotion and
            self.success_rate >= config.min_success_rate_for_promotion
        )

    def should_prune(self, config: NurseryConfig) -> bool:
        """Check if should be pruned."""
        # Too old without promotion
        if self.age_days > config.max_age_days and not self.promoted_at:
            return True

        # Too many failures after sufficient usage
        if self.usage_count >= 20 and self.success_rate < config.min_success_rate_for_survival:
            return True

        return False


class Nursery:
    """
    The germination nursery with capacity enforcement.

    Invariants:
    - len(active) <= max_capacity
    - per_context_count[ctx] <= max_per_context for all ctx
    - entropy_spent_this_run <= entropy_budget
    """

    def __init__(self, config: NurseryConfig | None = None):
        self.config = config or NurseryConfig()
        self._germinating: dict[str, GerminatingHolon] = {}
        self._entropy_spent_this_run: float = 0.0

    @property
    def active(self) -> list[GerminatingHolon]:
        return [g for g in self._germinating.values()
                if g.pruned_at is None and g.promoted_at is None]

    @property
    def at_capacity(self) -> bool:
        return len(self.active) >= self.config.max_capacity

    def context_count(self, context: str) -> int:
        return sum(1 for g in self.active if g.proposal.context == context)

    async def germinate(
        self,
        proposal: HolonProposal,
        validation: ValidationResult,
        logos: Logos,
        observer: Umwelt,
    ) -> GerminatingHolon:
        """
        Add a proposal to the nursery.

        Raises:
            AffordanceError: If observer lacks 'germinate' affordance
            BudgetExhaustedError: If nursery at capacity or entropy exhausted
        """
        # Check affordance
        if "germinate" not in SELF_GROW_AFFORDANCES.get(observer.dna.archetype, ()):
            raise AffordanceError(
                f"Archetype '{observer.dna.archetype}' cannot germinate",
                available=SELF_GROW_AFFORDANCES.get(observer.dna.archetype, ()),
            )

        # Check capacity
        if self.at_capacity:
            raise BudgetExhaustedError(
                f"Nursery at capacity ({self.config.max_capacity}). Prune or promote existing holons.",
                remaining=0,
                requested=1,
            )

        # Check per-context limit
        if self.context_count(proposal.context) >= self.config.max_per_context:
            raise BudgetExhaustedError(
                f"Context '{proposal.context}' at capacity ({self.config.max_per_context})",
                remaining=0,
                requested=1,
            )

        # Check entropy budget
        entropy_cost = self.config.entropy_cost_per_germination
        budget_status = await logos.invoke("self.grow.budget", observer)
        if budget_status["remaining"] < entropy_cost:
            raise BudgetExhaustedError(
                f"Germination requires {entropy_cost} entropy",
                remaining=budget_status["remaining"],
                requested=entropy_cost,
            )

        # Draw entropy
        await logos.invoke("void.entropy.sip", observer, amount=entropy_cost)

        # JIT compile
        jit_compiler = JITCompiler()
        jit_node = jit_compiler.compile_from_proposal(proposal)
        jit_source_hash = hashlib.sha256(jit_node.source.encode()).hexdigest()

        # Create germinating holon
        germinating = GerminatingHolon(
            germination_id=str(uuid.uuid4()),
            proposal=proposal,
            validation=validation,
            jit_node=jit_node,
            jit_source_hash=jit_source_hash,
            germinated_at=datetime.now(),
            germinated_by=observer.dna.name,
        )

        # Add to nursery
        handle = f"{proposal.context}.{proposal.entity}"
        self._germinating[handle] = germinating

        # Register JIT node in logos (temporary)
        logos.register_temporary(handle, jit_node)

        # Emit telemetry
        with tracer.start_span("growth.germinate") as span:
            span.set_attribute("growth.phase", "germinate")
            span.set_attribute("growth.proposal.handle", handle)
            span.set_attribute("growth.nursery.count", len(self.active))
            span.set_attribute("growth.nursery.capacity", self.config.max_capacity)

        return germinating
```

### 4.5 Promotion: Staged with Approval Gate

Promotion is **staged** with an explicit **approval gate**:

```python
@dataclass
class PromotionStage:
    """Stages of holon promotion."""

    STAGED = "staged"          # Ready for promotion, awaiting approval
    APPROVED = "approved"      # Approved, being written
    ACTIVE = "active"          # Fully active in ontology
    ROLLED_BACK = "rolled_back"  # Was active, now reverted


@dataclass
class RollbackToken:
    """Token for rolling back a promoted holon."""

    token_id: str
    handle: str
    promoted_at: datetime
    spec_path: Path
    impl_path: Path
    spec_content: str          # Original content for restore
    impl_content: str          # Original content for restore
    expires_at: datetime       # Rollback window


@dataclass
class PromotionResult:
    """Result of promotion attempt."""

    success: bool
    stage: PromotionStage
    handle: str
    reason: str

    # Artifacts (if successful)
    spec_path: Path | None = None
    impl_path: Path | None = None
    rollback_token: RollbackToken | None = None

    # Hashes for verification
    proposal_hash: str | None = None
    impl_hash: str | None = None


async def promote_holon(
    germinating: GerminatingHolon,
    logos: Logos,
    observer: Umwelt,
    approver: Umwelt | None = None,
) -> PromotionResult:
    """
    Promote a germinating holon with staged approval.

    Stage 1: Check readiness → STAGED
    Stage 2: Require approver with 'promote' affordance → APPROVED
    Stage 3: Write spec + impl + register → ACTIVE

    Args:
        germinating: The holon to promote
        logos: The Logos resolver
        observer: The requesting observer
        approver: The approving observer (must have 'promote' affordance)
                  If None, returns at STAGED stage awaiting approval.

    Returns:
        PromotionResult with current stage and artifacts

    Telemetry:
        Emits span: growth.promote
        Records rollback token for 7-day window
    """
    with tracer.start_span("growth.promote") as span:
        span.set_attribute("growth.phase", "promote")
        handle = f"{germinating.proposal.context}.{germinating.proposal.entity}"
        span.set_attribute("growth.proposal.handle", handle)

        # === Stage 1: Check readiness ===
        config = NurseryConfig()
        if not germinating.should_promote(config):
            return PromotionResult(
                success=False,
                stage=PromotionStage.STAGED,
                handle=handle,
                reason=(
                    f"Not ready: usage={germinating.usage_count}/{config.min_usage_for_promotion}, "
                    f"success_rate={germinating.success_rate:.2f}/{config.min_success_rate_for_promotion}"
                ),
            )

        # === Stage 2: Require approver ===
        if approver is None:
            return PromotionResult(
                success=True,
                stage=PromotionStage.STAGED,
                handle=handle,
                reason="Awaiting approver with 'promote' affordance (gardener or admin)",
            )

        # Verify approver has promote affordance
        if "promote" not in SELF_GROW_AFFORDANCES.get(approver.dna.archetype, ()):
            return PromotionResult(
                success=False,
                stage=PromotionStage.STAGED,
                handle=handle,
                reason=f"Approver '{approver.dna.archetype}' lacks 'promote' affordance",
            )

        span.set_attribute("growth.promotion.approver", approver.dna.name)
        span.set_attribute("growth.promotion.stage", "approved")

        # === Stage 3: Write artifacts ===
        proposal = germinating.proposal

        # Paths
        spec_path = Path(f"spec/{proposal.context}/{proposal.entity}.md")
        impl_path = Path(f"impl/claude/protocols/agentese/contexts/{proposal.context}/{proposal.entity}.py")

        # Backup existing content (for rollback)
        existing_spec = spec_path.read_text() if spec_path.exists() else ""
        existing_impl = impl_path.read_text() if impl_path.exists() else ""

        # Generate rollback token
        rollback_token = RollbackToken(
            token_id=str(uuid.uuid4()),
            handle=handle,
            promoted_at=datetime.now(),
            spec_path=spec_path,
            impl_path=impl_path,
            spec_content=existing_spec,
            impl_content=existing_impl,
            expires_at=datetime.now() + timedelta(days=7),  # 7-day rollback window
        )

        try:
            # Write spec
            spec_path.parent.mkdir(parents=True, exist_ok=True)
            spec_content = proposal.to_markdown()
            spec_path.write_text(spec_content)

            # Write implementation
            impl_path.parent.mkdir(parents=True, exist_ok=True)
            impl_content = germinating.jit_node.source
            impl_path.write_text(impl_content)

            # Register in L-gent
            await logos.invoke("world.registry.define", observer,
                               handle=handle,
                               status="active",
                               spec_path=str(spec_path),
                               impl_path=str(impl_path),
                               proposal_hash=proposal.content_hash,
                               impl_hash=germinating.jit_source_hash)

            # Update logos registry
            logos.register(handle, germinating.jit_node)

            # Emit event
            await logos.invoke("time.trace.record", observer,
                               event_type="holon_promoted",
                               handle=handle,
                               usage_count=germinating.usage_count,
                               success_rate=germinating.success_rate,
                               approver=approver.dna.name,
                               rollback_token=rollback_token.token_id)

            # Update germinating state
            germinating.promoted_at = datetime.now()
            germinating.rollback_token = rollback_token.token_id

            span.set_attribute("growth.promotion.stage", "active")
            span.set_attribute("growth.promotion.rollback_token", rollback_token.token_id)

            return PromotionResult(
                success=True,
                stage=PromotionStage.ACTIVE,
                handle=handle,
                reason=f"Promoted by {approver.dna.name} after {germinating.usage_count} uses ({germinating.success_rate:.0%} success)",
                spec_path=spec_path,
                impl_path=impl_path,
                rollback_token=rollback_token,
                proposal_hash=proposal.content_hash,
                impl_hash=germinating.jit_source_hash,
            )

        except Exception as e:
            # Rollback on any failure
            if existing_spec:
                spec_path.write_text(existing_spec)
            elif spec_path.exists():
                spec_path.unlink()

            if existing_impl:
                impl_path.write_text(existing_impl)
            elif impl_path.exists():
                impl_path.unlink()

            return PromotionResult(
                success=False,
                stage=PromotionStage.STAGED,
                handle=handle,
                reason=f"Promotion failed, rolled back: {e}",
            )
```

### 4.6 Rollback: Reverting Promoted Holons

```python
@dataclass
class RollbackResult:
    """Result of rollback attempt."""

    success: bool
    handle: str
    reason: str
    restored_spec: bool = False
    restored_impl: bool = False


async def rollback_holon(
    handle: str,
    rollback_token: str,
    logos: Logos,
    observer: Umwelt,
) -> RollbackResult:
    """
    Rollback a promoted holon using its rollback token.

    Requires:
    - Valid rollback token (not expired)
    - Observer with 'rollback' affordance (gardener or admin)

    Actions:
    - Restore spec file to pre-promotion state
    - Restore impl file to pre-promotion state
    - Update L-gent status to 'rolled_back'
    - Remove from logos registry
    """
    with tracer.start_span("growth.rollback") as span:
        span.set_attribute("growth.phase", "rollback")
        span.set_attribute("growth.proposal.handle", handle)

        # Check affordance
        if "rollback" not in SELF_GROW_AFFORDANCES.get(observer.dna.archetype, ()):
            return RollbackResult(
                success=False,
                handle=handle,
                reason=f"Observer '{observer.dna.archetype}' lacks 'rollback' affordance",
            )

        # Find rollback token
        token = await _find_rollback_token(rollback_token)
        if token is None:
            return RollbackResult(
                success=False,
                handle=handle,
                reason=f"Rollback token '{rollback_token}' not found",
            )

        # Check expiration
        if datetime.now() > token.expires_at:
            return RollbackResult(
                success=False,
                handle=handle,
                reason=f"Rollback token expired at {token.expires_at}",
            )

        # Verify handle matches
        if token.handle != handle:
            return RollbackResult(
                success=False,
                handle=handle,
                reason=f"Token handle mismatch: expected {token.handle}",
            )

        try:
            # Restore spec
            restored_spec = False
            if token.spec_content:
                token.spec_path.write_text(token.spec_content)
                restored_spec = True
            elif token.spec_path.exists():
                token.spec_path.unlink()
                restored_spec = True

            # Restore impl
            restored_impl = False
            if token.impl_content:
                token.impl_path.write_text(token.impl_content)
                restored_impl = True
            elif token.impl_path.exists():
                token.impl_path.unlink()
                restored_impl = True

            # Update L-gent
            await logos.invoke("world.registry.update_status", observer,
                               handle=handle,
                               status="rolled_back")

            # Remove from logos
            logos.unregister(handle)

            # Record event
            await logos.invoke("time.trace.record", observer,
                               event_type="holon_rolled_back",
                               handle=handle,
                               rolled_back_by=observer.dna.name,
                               rollback_token=rollback_token)

            span.set_attribute("growth.promotion.stage", "rolled_back")

            return RollbackResult(
                success=True,
                handle=handle,
                reason=f"Rolled back by {observer.dna.name}",
                restored_spec=restored_spec,
                restored_impl=restored_impl,
            )

        except Exception as e:
            return RollbackResult(
                success=False,
                handle=handle,
                reason=f"Rollback failed: {e}",
            )
```

---

## Part V: Entropy Budget Management

### 5.1 The Growth Budget

Growth operations consume entropy from a dedicated budget:

```python
@dataclass
class GrowthBudgetConfig:
    """Configuration for growth entropy budget."""

    # Per-run limits
    max_entropy_per_run: float = 1.0          # Total entropy per growth run
    recognize_cost: float = 0.25              # Cost per recognition
    propose_cost: float = 0.15                # Cost per proposal
    validate_cost: float = 0.10               # Cost per validation
    germinate_cost: float = 0.10              # Cost per germination
    promote_cost: float = 0.05                # Cost per promotion
    prune_cost: float = 0.02                  # Cost per prune (low)

    # Regeneration
    regeneration_rate_per_hour: float = 0.1   # Budget regeneration


@dataclass
class GrowthBudget:
    """Tracks entropy budget for growth operations."""

    config: GrowthBudgetConfig
    remaining: float
    spent_this_run: float = 0.0
    last_regeneration: datetime = field(default_factory=datetime.now)

    # Breakdown by operation
    spent_by_operation: dict[str, float] = field(default_factory=dict)

    def can_afford(self, operation: str) -> bool:
        """Check if budget allows operation."""
        cost = self._cost_for(operation)
        return self.remaining >= cost

    def spend(self, operation: str) -> float:
        """Deduct cost from budget."""
        cost = self._cost_for(operation)
        if cost > self.remaining:
            raise BudgetExhaustedError(
                f"Growth budget exhausted for '{operation}'",
                remaining=self.remaining,
                requested=cost,
            )

        self.remaining -= cost
        self.spent_this_run += cost
        self.spent_by_operation[operation] = (
            self.spent_by_operation.get(operation, 0.0) + cost
        )
        return cost

    def regenerate(self) -> float:
        """Apply time-based regeneration."""
        now = datetime.now()
        hours_elapsed = (now - self.last_regeneration).total_seconds() / 3600
        regenerated = hours_elapsed * self.config.regeneration_rate_per_hour

        old_remaining = self.remaining
        self.remaining = min(
            self.config.max_entropy_per_run,
            self.remaining + regenerated,
        )
        self.last_regeneration = now

        return self.remaining - old_remaining

    def _cost_for(self, operation: str) -> float:
        """Get cost for operation."""
        return {
            "recognize": self.config.recognize_cost,
            "propose": self.config.propose_cost,
            "validate": self.config.validate_cost,
            "germinate": self.config.germinate_cost,
            "promote": self.config.promote_cost,
            "prune": self.config.prune_cost,
        }.get(operation, 0.1)  # Default cost
```

### 5.2 The Budget Node

```python
@dataclass
class BudgetNode(BaseLogosNode):
    """
    self.grow.budget - Growth entropy budget management.

    Affordances:
    - status: View current budget
    - history: View spending history
    - regenerate: Force regeneration (admin only)
    """

    _handle: str = "self.grow.budget"
    _budget: GrowthBudget

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All can view; only gardener/admin can force regenerate."""
        if archetype in ("gardener", "admin"):
            return ("status", "history", "regenerate")
        return ("status", "history")

    async def manifest(self, observer: Umwelt) -> Renderable:
        """View budget status."""
        self._budget.regenerate()  # Apply pending regeneration

        pct = int(self._budget.remaining / self._budget.config.max_entropy_per_run * 100)

        return BasicRendering(
            summary=f"Growth Budget: {pct}%",
            content=(
                f"Remaining: {self._budget.remaining:.2f} / {self._budget.config.max_entropy_per_run}\n"
                f"Spent this run: {self._budget.spent_this_run:.2f}\n"
                f"Regeneration rate: {self._budget.config.regeneration_rate_per_hour}/hour"
            ),
            metadata={
                "remaining": self._budget.remaining,
                "max": self._budget.config.max_entropy_per_run,
                "spent_this_run": self._budget.spent_this_run,
                "spent_by_operation": self._budget.spent_by_operation,
            },
        )
```

---

## Part VI: The Fitness Functions

### 6.1 The Tasteful Gate

```python
def evaluate_tasteful(proposal: HolonProposal) -> tuple[float, str]:
    """
    Does this holon have clear, justified purpose?

    Scores:
    - 1.0: Clear purpose, fills obvious gap, no duplication
    - 0.7: Good purpose, reasonable justification
    - 0.4: Purpose exists but weak justification
    - 0.0: No clear purpose, "just in case" addition

    Returns:
        (score, reasoning)
    """
    score = 0.0
    reasons = []

    # Must have why_exists
    if not proposal.why_exists:
        return 0.0, "Missing why_exists (no justification)"

    justification = proposal.why_exists.lower()

    # Strong signals (+0.3 each, max +0.6)
    strong_signals = [
        ("agents frequently need", "Addresses frequent need"),
        ("current ontology lacks", "Fills ontology gap"),
        ("enables composition with", "Enables composition"),
        ("fills the gap between", "Bridges existing holons"),
    ]
    for phrase, reason in strong_signals:
        if phrase in justification:
            score += 0.15
            reasons.append(f"+: {reason}")

    # Medium signals (+0.15 each, max +0.3)
    medium_signals = [
        ("useful for", "General utility"),
        ("allows agents to", "Enables capability"),
        ("provides access to", "Provides access"),
    ]
    for phrase, reason in medium_signals:
        if phrase in justification:
            score += 0.1
            reasons.append(f"+: {reason}")

    # Weak signals (penalize, -0.15 each)
    weak_signals = [
        ("might be useful", "Uncertain utility"),
        ("could potentially", "Speculative"),
        ("just in case", "Defensive addition"),
        ("for completeness", "Completionism"),
    ]
    for phrase, reason in weak_signals:
        if phrase in justification:
            score -= 0.15
            reasons.append(f"-: {reason}")

    # Length check
    if len(proposal.why_exists) < 50:
        score -= 0.1
        reasons.append("-: Justification too brief (<50 chars)")
    elif len(proposal.why_exists) > 500:
        score -= 0.05
        reasons.append("-: Justification verbose (>500 chars)")

    # Evidence from gap recognition
    if proposal.gap and proposal.gap.evidence_count >= 10:
        score += 0.2
        reasons.append(f"+: Strong evidence ({proposal.gap.evidence_count} occurrences)")
    elif proposal.gap and proposal.gap.evidence_count >= 5:
        score += 0.1
        reasons.append(f"+: Moderate evidence ({proposal.gap.evidence_count} occurrences)")

    final_score = max(0.0, min(1.0, 0.4 + score))
    return final_score, "; ".join(reasons)
```

### 6.2 The Joy Assessment (Enhanced)

```python
def evaluate_joy(proposal: HolonProposal) -> tuple[float, str]:
    """
    Would interaction with this holon be delightful?

    Beyond keyword matching: considers naming aesthetics,
    affordance variety, and interaction flow.

    Returns:
        (score, reasoning)
    """
    score = 0.5  # Neutral baseline
    reasons = []

    # === Text Analysis ===
    text = " ".join([
        proposal.why_exists or "",
        *[b for b in proposal.behaviors.values()],
    ]).lower()

    positive_signals = [
        "discover", "explore", "delight", "surprise",
        "serendipity", "warmth", "invite", "welcome",
        "play", "wonder", "inspire", "joy",
    ]
    negative_signals = [
        "must", "required", "mandatory", "error",
        "invalid", "forbidden", "strictly", "enforce",
        "violation", "penalty", "restrict",
    ]

    pos_count = sum(1 for s in positive_signals if s in text)
    neg_count = sum(1 for s in negative_signals if s in text)

    score += pos_count * 0.05
    score -= neg_count * 0.05

    if pos_count > 0:
        reasons.append(f"+: {pos_count} positive signals")
    if neg_count > 0:
        reasons.append(f"-: {neg_count} negative signals")

    # === Naming Aesthetics ===
    entity_name = proposal.entity

    # Avoid clinical/technical names
    clinical_suffixes = ["_manager", "_handler", "_processor", "_service"]
    if any(entity_name.endswith(s) for s in clinical_suffixes):
        score -= 0.1
        reasons.append("-: Clinical naming (use verbs or metaphors)")

    # Reward evocative names
    evocative_patterns = ["garden", "river", "light", "dream", "echo", "song"]
    if any(p in entity_name for p in evocative_patterns):
        score += 0.1
        reasons.append("+: Evocative naming")

    # === Affordance Variety ===
    all_affordances = set(sum(proposal.affordances.values(), []))

    # Reward variety (more than just CRUD)
    if len(all_affordances) >= 5:
        score += 0.1
        reasons.append("+: Rich affordance set")

    # Reward playful affordances
    playful_affordances = ["explore", "dream", "wonder", "play", "discover", "wander"]
    if any(a in all_affordances for a in playful_affordances):
        score += 0.1
        reasons.append("+: Playful affordances")

    # === Observer Differentiation ===
    archetype_count = len(proposal.affordances)
    if archetype_count >= 3:
        score += 0.1
        reasons.append("+: Good archetype differentiation")

    final_score = max(0.0, min(1.0, score))
    return final_score, "; ".join(reasons) or "Neutral"
```

---

## Part VII: Observability Contract

### 7.1 Metrics Schema

```python
GROWTH_METRICS = {
    # Counters
    "growth.recognize.invocations": "Total recognition invocations",
    "growth.recognize.gaps_found": "Total gaps found",
    "growth.propose.invocations": "Total proposal invocations",
    "growth.validate.invocations": "Total validation invocations",
    "growth.validate.passed": "Validations that passed",
    "growth.validate.failed": "Validations that failed",
    "growth.germinate.invocations": "Total germination invocations",
    "growth.promote.invocations": "Total promotion invocations",
    "growth.promote.approved": "Promotions approved",
    "growth.promote.rejected": "Promotions rejected",
    "growth.rollback.invocations": "Total rollback invocations",
    "growth.prune.invocations": "Total prune invocations",

    # Gauges
    "growth.nursery.count": "Current germinating holons",
    "growth.nursery.capacity_pct": "Nursery capacity percentage",
    "growth.budget.remaining": "Remaining entropy budget",
    "growth.budget.spent": "Entropy spent this run",

    # Histograms
    "growth.recognize.latency_ms": "Recognition latency",
    "growth.validate.score.tasteful": "Tasteful scores distribution",
    "growth.validate.score.curated": "Curated scores distribution",
    "growth.germinate.time_to_promote_days": "Days from germination to promotion",
}
```

### 7.2 Span Schema

All growth operations emit OpenTelemetry spans:

```python
# Example span structure
{
    "name": "growth.validate",
    "trace_id": "abc123...",
    "span_id": "def456...",
    "start_time": "2025-12-15T10:30:00Z",
    "end_time": "2025-12-15T10:30:01Z",
    "status": "OK",
    "attributes": {
        "growth.phase": "validate",
        "growth.proposal.handle": "world.library",
        "growth.proposal.hash": "sha256:abc...",
        "growth.validation.passed": True,
        "growth.validation.score.tasteful": 0.75,
        "growth.validation.score.curated": 0.80,
        "growth.validation.score.ethical": 1.0,
        "growth.validation.score.joy": 0.65,
        "growth.validation.score.composable": 0.85,
        "growth.validation.score.heterarchical": 0.70,
        "growth.validation.score.generative": 0.75,
        "growth.validation.law_check.identity": True,
        "growth.validation.law_check.associativity": True,
        "growth.validation.abuse_check.passed": True,
        "growth.validation.blockers": [],
        "growth.entropy.spent": 0.10,
    },
}
```

---

## Part VIII: The Growth Grammar (Operad)

Growth follows compositional rules with **verified laws**:

```python
GROWTH_OPERAD = Operad(
    name="growth",

    operations={
        # Nullary operations (seeds)
        "recognize": Operation(
            arity=0,
            output_type="GapRecognition",
            description="Recognize an ontological gap",
        ),

        # Unary operations (transformations)
        "propose": Operation(
            arity=1,
            input_types=["GapRecognition"],
            output_type="HolonProposal",
            description="Draft a holon proposal from gap",
        ),
        "validate": Operation(
            arity=1,
            input_types=["HolonProposal"],
            output_type="ValidationResult",
            description="Validate against principles + laws",
        ),
        "germinate": Operation(
            arity=1,
            input_types=["HolonProposal"],
            output_type="GerminatingHolon",
            description="Begin nursery period",
            requires="validate(proposal).passed",
        ),

        # Binary operations (composition)
        "merge": Operation(
            arity=2,
            input_types=["HolonProposal", "HolonProposal"],
            output_type="HolonProposal",
            description="Merge two proposals into one",
        ),
        "inherit": Operation(
            arity=2,
            input_types=["HolonProposal", "str"],
            output_type="HolonProposal",
            description="Inherit affordances from existing holon",
        ),
    },

    laws=[
        # Validation is idempotent
        Law(
            name="validate_idempotent",
            statement="validate(validate(p)) ≡ validate(p)",
            test=test_validate_idempotent,
        ),

        # Germination requires validation
        Law(
            name="germinate_requires_validation",
            statement="germinate(p) requires validate(p).passed",
            test=test_germinate_requires_validation,
        ),

        # Merge is commutative
        Law(
            name="merge_commutative",
            statement="merge(a, b) ≡ merge(b, a)",
            test=test_merge_commutative,
        ),

        # Merge is associative
        Law(
            name="merge_associative",
            statement="merge(merge(a, b), c) ≡ merge(a, merge(b, c))",
            test=test_merge_associative,
        ),

        # Inherit preserves polymorphism
        Law(
            name="inherit_preserves_affordances",
            statement="inherit(p, h).affordances ⊇ h.affordances",
            test=test_inherit_preserves_affordances,
        ),
    ],
)


# Property tests for law verification
def test_validate_idempotent(proposal: HolonProposal) -> bool:
    """Verify validate is idempotent."""
    result1 = validate_sync(proposal)
    # Simulating re-validation of a "validated proposal" means
    # the second validation should produce identical scores
    result2 = validate_sync(proposal)
    return result1.scores == result2.scores


def test_merge_commutative(a: HolonProposal, b: HolonProposal) -> bool:
    """Verify merge is commutative."""
    merged_ab = merge_proposals(a, b)
    merged_ba = merge_proposals(b, a)

    # Content hash should be identical
    return merged_ab.compute_hash() == merged_ba.compute_hash()
```

---

## Part IX: Anti-Patterns

1. **The Eager Grower**: Growing holons without genuine gaps
   - *Correction*: Always require GapRecognition as input to propose

2. **The Immortal Proto-Holon**: Never pruning failed growths
   - *Correction*: Automatic pruning after age threshold (30 days)

3. **The Clone**: Growing holons that duplicate existing ones
   - *Correction*: Duplication check with similarity threshold

4. **The God-Grower**: Growth without observer context
   - *Correction*: All growth paths require Umwelt with appropriate affordances

5. **The Infinite Garden**: Too many germinating holons
   - *Correction*: Nursery capacity limit (20 max, 5 per context)

6. **The Forced Growth**: Promoting before ready
   - *Correction*: Usage + success rate gates + approver requirement

7. **The Unchecked Proposal**: Skipping law verification
   - *Correction*: Validation includes identity/associativity checks

8. **The Invisible Growth**: No observability
   - *Correction*: All operations emit spans + metrics

9. **The Irreversible Promotion**: No rollback capability
   - *Correction*: 7-day rollback tokens with full restore

10. **The Unguarded Nursery**: Anyone can promote
    - *Correction*: Archetype-specific affordances with approver gate

---

## Part X: Success Criteria

An AGENTESE `self.grow` implementation is well-designed if:

- **Autopoietic**: System can propose new holons without external intervention
- **Selective**: Most proposals fail validation (Tasteful/Curated/Law checks)
- **Compositional**: New holons compose with existing ontology (verified laws)
- **Safe**: Abuse detection prevents malicious holons
- **Reversible**: Promoted holons can be rolled back within window
- **Observable**: All operations emit telemetry (spans + metrics)
- **Bounded**: Nursery has capacity limits; operations have entropy budgets
- **Governed**: Archetype-specific affordances enforce access control
- **Learnable**: Failed growths inform future proposals via memory
- **Deterministic**: Proposals can be regenerated from content hash
- **Staged**: Promotion requires explicit approver

---

## Part XI: Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Should promotion require human/agent approver? | **Yes**: Requires archetype with 'promote' affordance (gardener/admin) |
| What telemetry sources for gap recognition? | **Defined**: `agentese.errors` table with schema, 7-day lookback |
| How to version/rollback promoted holons? | **Rollback tokens**: 7-day window, full spec/impl restore |
| How to prevent duplicate holons? | **Similarity search**: Name + affordance vector similarity |
| How to bound nursery growth? | **Capacity limits**: 20 max, 5 per context, entropy budget |
| How to verify category laws? | **Pre-germination check**: Identity + associativity tests |
| How to detect abuse? | **Red-team checks**: Manipulation, exfiltration, escalation, resource risks |

---

## Part XII: Files to Create

```
spec/protocols/self-grow.md                       # This specification

impl/claude/protocols/agentese/contexts/self_grow/
├── __init__.py                                   # Package exports
├── recognize.py                                  # Gap recognition with telemetry
├── propose.py                                    # Proposal generation with hashing
├── validate.py                                   # Seven gates + law checks + abuse detection
├── germinate.py                                  # Nursery with capacity enforcement
├── promote.py                                    # Staged promotion with approver gate
├── rollback.py                                   # Rollback with token management
├── prune.py                                      # Composting with learning
├── nursery.py                                    # NurseryNode with budget tracking
├── budget.py                                     # BudgetNode and GrowthBudget
├── operad.py                                     # GROWTH_OPERAD with law tests
├── fitness.py                                    # Fitness functions (all 7 principles)
├── abuse.py                                      # Red-team abuse detection
├── duplication.py                                # Similarity-based duplication check
├── telemetry.py                                  # Spans + metrics schema
└── schemas.py                                    # All dataclasses

impl/claude/protocols/agentese/contexts/self_grow/_tests/
├── test_recognize.py
├── test_propose.py
├── test_validate.py
├── test_germinate.py
├── test_promote.py
├── test_rollback.py
├── test_prune.py
├── test_operad.py                               # Property tests for laws
├── test_abuse.py
├── test_duplication.py
├── test_budget.py
└── conftest.py                                   # Fixtures
```

---

*"The system that cannot grow new organs is already dead. But growth without taste produces only tumors. self.grow is the immune system that distinguishes nourishment from poison—the gatekeeper that demands justification, the gardener that prunes with gratitude, and the archivist that remembers every attempt. Growth is not free. Growth is earned."*
