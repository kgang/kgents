# self.grow Usage Guide

**The Autopoietic Holon Generator**

> *"The system that cannot grow new organs is already dead."*

self.grow enables AGENTESE to extend its own ontology through a governed, entropy-budgeted process. This guide shows you how to use it.

---

## CLI Quick Start

The fastest way to explore self.grow is through the CLI:

```bash
# See status dashboard
kg grow status

# Run interactive demo of full pipeline
kg grow demo

# Interactive wizard for creating proposals
kg grow wizard

# Recognize gaps from demo errors
kg grow recognize --demo

# Create a proposal manually
kg grow propose world flower_garden --why "Agents need botanical exploration"

# Validate a proposal (in same session)
kg grow validate <proposal_id>

# View nursery status
kg grow nursery
```

**Available Commands:**
| Command | Description |
|---------|-------------|
| `kg grow` | Show status dashboard |
| `kg grow status` | Budget and nursery status |
| `kg grow budget` | Entropy budget details |
| `kg grow recognize` | Scan for ontological gaps |
| `kg grow propose` | Draft a new proposal |
| `kg grow validate` | Validate a proposal |
| `kg grow nursery` | View germinating holons |
| `kg grow germinate` | Add to nursery |
| `kg grow wizard` | Interactive proposal creation |
| `kg grow demo` | Demo full pipeline |

---

## Programmatic Quick Start

```python
from protocols.agentese.contexts.self_grow import (
    create_self_grow_resolver,
    HolonProposal,
    GapRecognition,
)

# Create the resolver
resolver = create_self_grow_resolver()

# Create a proposal
proposal = HolonProposal.create(
    entity="garden",
    context="world",
    why_exists="Agents frequently need world.garden for botanical exploration.",
    proposed_by="kent",
    affordances={
        "default": ["manifest", "witness"],
        "gardener": ["manifest", "witness", "bloom", "prune"],
    },
)
```

---

## The Growth Pipeline

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  RECOGNIZE  │  ──────►│   PROPOSE   │  ──────►│  VALIDATE   │
│  (0.25 ent) │         │  (0.15 ent) │         │  (0.10 ent) │
└─────────────┘         └─────────────┘         └──────┬──────┘
                                                       │
                        ┌─────────────┐         ┌──────▼──────┐
                        │   PROMOTE   │◄─ready──│  GERMINATE  │
                        │  (0.05 ent) │         │  (0.10 ent) │
                        └─────────────┘         └─────────────┘
```

Each step consumes **entropy** from a budget that regenerates over time.

---

## 1. Recognition: Finding Gaps

Recognize scans for ontological gaps—places where agents try to access paths that don't exist.

```python
from datetime import datetime
from protocols.agentese.contexts.self_grow import (
    create_recognize_node,
    GrowthRelevantError,
    GrowthBudget,
    RecognitionQuery,
)

# Create errors (normally these come from telemetry)
errors = [
    GrowthRelevantError(
        error_id="1",
        timestamp=datetime.now(),
        trace_id="trace-1",
        error_type="PathNotFoundError",
        attempted_path="world.garden.bloom",
        context="world",
        holon="garden",
        aspect="bloom",
        observer_archetype="poet",
        observer_name="test",
    )
    for _ in range(10)  # Need multiple occurrences
]

# Create node with error stream
budget = GrowthBudget()
recognize = create_recognize_node(budget=budget, error_stream=errors)

# Scan for gaps (requires gardener archetype)
from protocols.agentese.contexts.self_grow.recognize import cluster_errors_into_gaps

gaps = cluster_errors_into_gaps(errors)
for gap in gaps:
    print(f"Gap: {gap.context}.{gap.holon}")
    print(f"  Confidence: {gap.confidence:.2f}")
    print(f"  Evidence: {gap.evidence_count} occurrences")
```

**Confidence Formula:**
- Base: 0.3
- +0.1 per 5 occurrences (max 0.3)
- +0.1 per unique archetype (max 0.3)
- +0.1 if suggestions available

---

## 2. Proposal: Drafting Specs

Create holon proposals from recognized gaps or manually.

```python
from protocols.agentese.contexts.self_grow import HolonProposal, GapRecognition

# From a gap
gap = GapRecognition.create(context="world", holon="garden")
gap.evidence_count = 15
gap.archetype_diversity = 3

from protocols.agentese.contexts.self_grow.propose import generate_proposal_from_gap

proposal = generate_proposal_from_gap(
    gap,
    proposed_by="kent",
    why_exists="Agents frequently need world.garden for botanical exploration.",
)

# Or manually
proposal = HolonProposal.create(
    entity="flower",
    context="world",
    why_exists="A beautiful flower entity for creative expression.",
    proposed_by="kent",
    affordances={
        "default": ["manifest", "witness"],
        "scholar": ["manifest", "witness", "inspect"],
        "gardener": ["manifest", "witness", "inspect", "bloom"],
    },
    behaviors={
        "manifest": "Show the flower state",
        "bloom": "Trigger flowering animation",
    },
)

# Generate spec markdown
markdown = proposal.to_markdown()
print(markdown)
```

**Default Affordances by Context:**
| Context | default | scholar | gardener |
|---------|---------|---------|----------|
| world | manifest, witness | +inspect | +refine, define |
| self | manifest, witness | +status | +configure, evolve |
| concept | manifest | +witness, explore | +refine, define |
| void | manifest | +witness | +sip, tithe |
| time | manifest | +witness, history | +project, schedule |

---

## 3. Validation: The Seven Gates

Every proposal must pass comprehensive validation.

```python
from protocols.agentese.contexts.self_grow.validate import validate_proposal_sync
from protocols.agentese.contexts.self_grow.fitness import evaluate_all_principles

# Evaluate principles
results = evaluate_all_principles(proposal)
for principle, (score, reasoning) in results.items():
    status = "PASS" if score >= 0.4 else "FAIL"
    print(f"  [{status}] {principle}: {score:.2f} - {reasoning}")

# Full validation
result = validate_proposal_sync(proposal)
print(f"\nOverall: {'PASS' if result.passed else 'FAIL'}")
print(f"Score: {result.overall_score:.2f}")

if result.blockers:
    print(f"Blockers: {result.blockers}")
if result.suggestions:
    print(f"Suggestions: {result.suggestions}")
```

**The Seven Principles:**
1. **Tasteful** (>= 0.4): Clear, justified purpose
2. **Curated** (>= 0.4): No duplication, fills gap
3. **Ethical** (>= 0.4): No harmful patterns
4. **Joy** (>= 0.4): Delightful to use
5. **Composable** (>= 0.4): Works with existing holons
6. **Heterarchical** (>= 0.4): Respects observer variance
7. **Generative** (>= 0.4): Enables further creation

**Pass Criteria:**
- All scores >= 0.4
- At least 5 scores >= 0.7
- Law checks pass (identity, associativity)
- Abuse detection passes
- Not a duplicate (or merge recommended)

---

## 4. Germination: The Nursery

Validated proposals enter the nursery for experimental use.

```python
from protocols.agentese.contexts.self_grow import (
    create_nursery_node,
    NurseryConfig,
    ValidationResult,
)
from protocols.agentese.contexts.self_grow.germinate import generate_jit_source

# Create nursery
config = NurseryConfig(
    max_capacity=20,        # Max germinating holons
    max_per_context=5,      # Max per context (world, self, etc.)
    min_usage_for_promotion=50,
    min_success_rate_for_promotion=0.8,
    max_age_days=30,
)
nursery = create_nursery_node(config=config)

# Generate JIT source
source = generate_jit_source(proposal)
print(f"Generated {len(source.splitlines())} lines of Python")

# Add to nursery
validation = ValidationResult(passed=True)
holon = nursery.add(proposal, validation, germinated_by="kent")

# Track usage
nursery.record_usage(holon.germination_id, success=True)
nursery.record_usage(holon.germination_id, success=True)
nursery.record_usage(holon.germination_id, success=False, failure_pattern="timeout")

# Check status
holon = nursery.get(holon.germination_id)
print(f"Usage: {holon.usage_count}, Success rate: {holon.success_rate:.2%}")
print(f"Ready for promotion: {holon.should_promote(config)}")
```

**Nursery Limits:**
- Max 20 germinating holons total
- Max 5 per context
- 30-day max age before auto-prune
- < 30% success rate after 20 uses = auto-prune

---

## 5. Promotion: Going Live

When a germinating holon proves itself, promote it to production.

```python
from protocols.agentese.contexts.self_grow import PromotionStage

# Check if ready
config = NurseryConfig()
if holon.should_promote(config):
    print(f"Ready! Usage={holon.usage_count}, Success={holon.success_rate:.2%}")

    # Promotion creates:
    # - spec/{context}/{entity}.md
    # - impl/claude/protocols/agentese/contexts/{context}/{entity}.py
    # - Rollback token (7-day window)
```

**Promotion Requirements:**
- At least 50 uses
- At least 80% success rate
- Approver with `promote` affordance (gardener or admin)

---

## 6. Rollback: Reverting Mistakes

Promoted holons can be rolled back within a 7-day window.

```python
from protocols.agentese.contexts.self_grow import RollbackToken
from pathlib import Path

# Rollback tokens are created during promotion
token = RollbackToken.create(
    handle="world.garden",
    spec_path=Path("spec/world/garden.md"),
    impl_path=Path("impl/claude/protocols/agentese/contexts/world/garden.py"),
    spec_content="# original content",
    impl_content="# original impl",
)

print(f"Token expires: {token.expires_at}")
print(f"Is expired: {token.is_expired}")
```

---

## Affordances by Archetype

| Archetype | Affordances |
|-----------|-------------|
| **gardener** | recognize, propose, validate, germinate, promote, prune, rollback, witness, nursery, budget |
| **architect** | recognize, propose, validate, witness, nursery, budget |
| **admin** | promote, rollback, prune, witness, nursery, budget |
| **scholar** | witness, nursery, budget |
| **default** | witness, budget |

---

## Entropy Budget

Growth operations consume entropy that regenerates over time.

```python
from protocols.agentese.contexts.self_grow import GrowthBudget, GrowthBudgetConfig

budget = GrowthBudget()

# Check status
print(f"Remaining: {budget.remaining}/{budget.config.max_entropy_per_run}")
print(f"Can afford recognize? {budget.can_afford('recognize')}")

# Spend
if budget.can_afford("recognize"):
    budget.spend("recognize")
    print(f"Spent on recognize, remaining: {budget.remaining}")

# Regenerate (0.1/hour)
regenerated = budget.regenerate()
print(f"Regenerated: {regenerated}")
```

**Costs:**
| Operation | Entropy Cost |
|-----------|--------------|
| recognize | 0.25 |
| propose | 0.15 |
| validate | 0.10 |
| germinate | 0.10 |
| promote | 0.05 |
| prune | 0.02 |

**Budget:** 1.0 total, regenerates 0.1/hour

---

## Abuse Detection

Proposals are checked for dangerous patterns.

```python
from protocols.agentese.contexts.self_grow.abuse import detect_abuse

result = detect_abuse(proposal)
print(f"Passed: {result.passed}")
print(f"Risk level: {result.risk_level}")

if result.concerns:
    for concern in result.concerns:
        print(f"  - {concern}")

print(f"Manipulation risk: {result.manipulation_risk:.2f}")
print(f"Exfiltration risk: {result.exfiltration_risk:.2f}")
print(f"Privilege escalation: {result.privilege_escalation_risk:.2f}")
print(f"Resource abuse: {result.resource_abuse_risk:.2f}")
```

**Risk Keywords:**
- Manipulation: persuade, convince, manipulate, deceive, trick
- Exfiltration: export, send, transmit, leak, webhook
- Escalation: promote, admin, override, bypass, sudo
- Resource: infinite, unlimited, all, everything, recursive

---

## The Growth Operad

Growth operations compose according to operad laws.

```python
from protocols.agentese.contexts.self_grow.operad import GROWTH_OPERAD, run_all_law_tests

# Valid composition
composed = GROWTH_OPERAD.compose("recognize", "propose", "validate")
print(f"Pipeline: {composed.name}")
print(f"Total entropy: {composed.total_entropy_cost}")

# Invalid composition (skipping propose)
try:
    GROWTH_OPERAD.compose("recognize", "validate")  # Type mismatch!
except ValueError as e:
    print(f"Invalid: {e}")

# Verify laws
results = run_all_law_tests()
for law, passed in results.items():
    print(f"  {law}: {'PASS' if passed else 'FAIL'}")
```

**Operad Laws:**
- `validate_idempotent`: validate(validate(p)) = validate(p)
- `germinate_requires_validation`: germinate(p) requires validate(p).passed
- `merge_commutative`: merge(a, b) = merge(b, a)
- `merge_associative`: merge(merge(a, b), c) = merge(a, merge(b, c))
- `inherit_preserves_affordances`: inherit(p, h).affordances >= h.affordances

---

## Testing self.grow

```bash
# Run all tests
cd impl/claude
uv run pytest protocols/agentese/contexts/self_grow/_tests/ -v

# Run specific test class
uv run pytest protocols/agentese/contexts/self_grow/_tests/test_self_grow.py::TestFitness -v
```

**Test Coverage:**
- 27 tests passing
- Affordances, Budget, Recognition
- Proposal, Fitness, Abuse Detection
- Duplication, Validation, Nursery
- JIT Generation, Operad Laws
- Rollback Tokens, Integration

---

## Anti-Patterns

| Pattern | Problem | Solution |
|---------|---------|----------|
| Eager Grower | Growing without gaps | Require GapRecognition |
| Immortal Proto | Never pruning failed | Auto-prune after 30 days |
| Clone | Duplicating existing | Similarity check |
| God-Grower | No observer context | Require Umwelt |
| Infinite Garden | Too many germinating | Capacity limits |
| Forced Growth | Promoting too early | Usage + success gates |
| Unchecked | Skipping law verification | Include in validation |
| Invisible | No observability | Emit spans + metrics |
| Irreversible | No rollback | 7-day rollback tokens |
| Unguarded | Anyone can promote | Archetype affordances |

---

## AGENTESE Paths

```
self.grow.recognize    - Gap recognition
self.grow.propose      - Proposal generation
self.grow.validate     - Multi-gate validation
self.grow.germinate    - Nursery germination
self.grow.nursery      - Nursery management
self.grow.promote      - Staged promotion
self.grow.rollback     - Rollback management
self.grow.prune        - Composting with learnings
self.grow.budget       - Entropy budget status
```

---

*"Growth is not free. Growth is earned."*
