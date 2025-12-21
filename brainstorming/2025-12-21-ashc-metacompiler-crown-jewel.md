# ASHC Metacompiler Crown Jewel: The Self-Improving Operator

> *"Every failure is a teacher. Every teacher is a prior. Every prior shapes the future."*

**Status**: Conceptual Synthesis
**Heritage**:
- `brainstorming/2025-12-21-failure-as-evidence.md` (Failure as Evidence)
- `brainstorming/2025-12-20-interactive-text-spec.md` (Interactive Text)
- `plans/brainstorming-work-betting.md` (Work Betting)
- `spec/protocols/agentic-self-hosting-compiler.md` (ASHC Core)

---

## The Vision

A Crown Jewel that **operates** the ASHC metacompiler system. Not just compilation, but the full lifecycle:

1. **Failure Learning** — Failed generations become evidence that improves future generations
2. **Work Betting** — Human work estimates become accountable bets with skin in the game
3. **Interactive Surfaces** — Specs, tasks, and evidence become live, clickable documents
4. **Principle Accountability** — Track which principles actually predict success

This is **ASHC-as-service**: a living system that learns, adapts, and holds itself accountable.

---

## Core Insight: The Three Feedbacks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE METACOMPILER FEEDBACK LOOPS                           │
│                                                                             │
│   1. FAILURE → PRIOR                                                        │
│      Failed generations don't disappear.                                    │
│      They become evidence that shapes the next generation.                  │
│      CausalGraph learns: "this pattern fails; avoid it"                     │
│                                                                             │
│   2. ESTIMATE → BET                                                         │
│      Human work estimates become wagers.                                    │
│      High confidence + failure = credibility penalty                        │
│      Principles cited → accountable via PrincipleRegistry                   │
│                                                                             │
│   3. SPEC → SURFACE                                                         │
│      Specs aren't dead text. They're interactive.                           │
│      Tasks toggle → Mark traces captured                                    │
│      Paths hover → polynomial state visible                                 │
│      Evidence links → causal graph navigable                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Architecture: Metacompiler Crown Jewel

### The Service Module

```
services/metacompiler/
├── __init__.py
├── core/
│   ├── engine.py          # Metacompiler orchestration
│   ├── evidence_store.py  # Persistent evidence corpus
│   └── feedback.py        # Three feedback loops
│
├── learning/
│   ├── failure_corpus.py  # Failed generations → learned priors
│   ├── causal_learner.py  # CausalGraph evolution
│   └── prior_injection.py # Use learned priors in generation
│
├── betting/
│   ├── work_bet.py        # WorkBet type
│   ├── credibility.py     # Work credibility tracking
│   ├── adversary.py       # Opportunity cost as adversary
│   └── principle_health.py # Which principles are predictive
│
├── surfaces/
│   ├── spec_surface.py    # Interactive spec rendering
│   ├── evidence_surface.py # Evidence corpus visualization
│   └── betting_surface.py  # Work betting dashboard
│
├── web/
│   ├── MetacompilerDashboard.tsx
│   ├── EvidenceExplorer.tsx
│   ├── BettingPanel.tsx
│   └── PrincipleHealth.tsx
│
└── persistence/
    └── tables.py          # SQLAlchemy models for evidence, bets
```

### The Polynomial

```python
METACOMPILER_POLYNOMIAL = PolyAgent(
    positions=frozenset([
        "IDLE",           # Waiting for work
        "COMPILING",      # Running ASHC compilation
        "LEARNING",       # Updating priors from evidence
        "BETTING",        # Managing work bets
        "PROJECTING",     # Rendering interactive surfaces
    ]),
    directions=lambda s: {
        "IDLE": frozenset(["compile", "bet", "learn", "project"]),
        "COMPILING": frozenset(["evidence", "fail", "succeed"]),
        "LEARNING": frozenset(["update_graph", "inject_prior", "done"]),
        "BETTING": frozenset(["place_bet", "resolve_bet", "status"]),
        "PROJECTING": frozenset(["toggle_task", "hover_path", "click_evidence"]),
    }[s],
    transition=metacompiler_transition,
)
```

---

## Feature 1: Failure as Evidence

> *"Failed generations are not waste. They are evidence."*

### The Current Gap

```
Spec → Generate N variations → Verify each → Select best → Output
                                    ↓
                              Failures discarded  ← WASTE!
```

### The Closed Loop

```
Spec → Generate N variations → Verify each → Select best → Output
                                    ↓
                              Failures → EvidenceStore
                                    ↓
                              CausalLearner.observe(failure)
                                    ↓
                              Refined prior for NEXT generation
```

### Implementation

```python
@dataclass(frozen=True)
class FailureEvidence:
    """A failed generation captured as evidence."""

    run_id: str
    spec_hash: str
    nudges_applied: tuple[Nudge, ...]
    error_messages: tuple[str, ...]
    test_failures: tuple[TestFailure, ...]
    type_errors: tuple[TypeCheckError, ...]
    timestamp: datetime

    # Rich context for learning
    ast_diff: ASTDiff | None = None
    model_used: str = ""
    temperature: float = 0.0


class FailureCorpus:
    """Persistent store of failed generations."""

    async def add_failure(self, failure: FailureEvidence) -> None:
        """Add failure to corpus and update causal graph."""
        await self.store.save(failure)

        # Learn from failure
        for nudge in failure.nudges_applied:
            await self.causal_graph.observe_edge(
                nudge=nudge,
                outcome_delta=-1.0,  # Negative!
                context=failure.error_messages,
            )

    async def get_beneficial_priors(self, n: int = 5) -> list[CausalEdge]:
        """Get the top N beneficial patterns from history."""
        return sorted(
            self.causal_graph.edges,
            key=lambda e: e.outcome_delta,
            reverse=True,
        )[:n]

    async def get_harmful_priors(self, n: int = 5) -> list[CausalEdge]:
        """Get the top N patterns to avoid from history."""
        return sorted(
            self.causal_graph.edges,
            key=lambda e: e.outcome_delta,
        )[:n]


class PriorAwareCompiler(EvidenceCompiler):
    """Compiler that uses accumulated evidence as prior."""

    async def compile(self, spec: str) -> ASHCOutput:
        # Load learned priors
        beneficial = await self.corpus.get_beneficial_priors()
        harmful = await self.corpus.get_harmful_priors()

        # Inject into generation prompt
        enriched_prompt = self._enrich_with_priors(
            spec,
            do_this=[e.nudge.reason for e in beneficial],
            avoid_this=[e.nudge.reason for e in harmful],
        )

        # Generate with learned prior
        output = await super().compile(enriched_prompt)

        # Save ALL runs (pass and fail) for learning
        for run in output.evidence.runs:
            if run.test_results.passed:
                await self.corpus.add_success(run)
            else:
                await self.corpus.add_failure(run)

        return output
```

### The Learning Curve

As evidence accumulates, pass rates improve:

| Evidence Size | Expected Pass Rate | Mechanism |
|---------------|-------------------|-----------|
| 0 runs | ~60% | No priors, baseline LLM |
| 100 runs | ~75% | Harmful patterns avoided |
| 1000 runs | ~90% | Rich prior injection |
| 10000 runs | ~95%+ | System has learned the codebase |

The codebase becomes **self-documenting through evidence**: the causal graph IS the best practices.

---

## Feature 2: Work Betting

> *"If you can't bet on it, you don't believe it."*

### The Core Insight

Every task you start is implicitly a bet. ASHC already has machinery for:
- **Betting** on outcomes with confidence + stakes
- **Credibility tracking** that erodes with bullshit, recovers slowly
- **Adversarial accountability** — opportunity cost takes the other side
- **Causal penalty propagation** — blame flows to principles that misled

### Type Signatures

```python
@dataclass(frozen=True)
class WorkBet:
    """A wager on task completion."""

    bet_id: str
    task_description: str

    # The wager
    estimated_hours: float
    confidence: float           # 0-1
    stake: Decimal             # Focus tokens wagered

    # Causal attribution
    principles_cited: tuple[str, ...]  # e.g., ("depth_over_breadth", "tasteful")
    context_cited: tuple[str, ...]     # e.g., ("similar to ASHC Phase 2")

    # Resolution
    actual_hours: float | None = None
    completed: bool = False

    @property
    def was_bullshit(self) -> bool:
        """High confidence + way off = bullshit."""
        if self.actual_hours is None:
            return False
        error_ratio = abs(self.actual_hours - self.estimated_hours) / max(self.estimated_hours, 0.1)
        return self.confidence >= 0.8 and error_ratio > 0.5


@dataclass
class WorkCredibility:
    """Work estimation credibility."""

    credibility: float = 1.0
    total_bets: int = 0
    successful_bets: int = 0
    bullshit_count: int = 0

    # Taleb's asymmetry: lose fast, recover slow
    BULLSHIT_PENALTY = 0.15
    SUCCESS_RECOVERY = 0.02
    # One bullshit = ~8 accurate estimates to recover

    def discount_estimate(self, raw_confidence: float) -> float:
        """Discount confidence claims by track record."""
        return raw_confidence * self.credibility


class WorkAdversary:
    """The implicit counterparty taking the other side of work bets."""

    adversary_winnings: Decimal = Decimal("0")

    def settle_bet(self, bet: WorkBet) -> BetSettlement:
        if bet.was_bullshit:
            payout = bet.stake * Decimal(str(bet.confidence))
            self.adversary_winnings += payout
            return BetSettlement(winner="adversary", payout=payout)
        # ...
```

### UX Flow

**Session Start:**
```
📊 YOUR WORK CREDIBILITY: 0.78

🎯 PRINCIPLE HEALTH:
   ├── "depth over breadth": 0.92 (predictive)
   ├── "tasteful > complete": 0.85 (predictive)
   ├── "parallel work": 0.45 (often leads to context thrash)
   └── "quick wins first": 0.33 (discredited)

💰 ADVERSARY TRACKER:
   Recent: adversary won 2/5 bets
```

**Starting a Task:**
```
🎲 TASK BET: "Implement Metacompiler Crown Jewel"

   Your estimate: 4 hours
   Your confidence: 75%

   ⚠️ CREDIBILITY ADJUSTMENT: 0.78 × 0.75 = 58% effective

   Stakes:
   ├── If you finish in 4h: +3 focus tokens, +0.03 credibility
   ├── If you finish in 6h: -2 focus tokens, -0.05 credibility
   └── If you're >50% off at 75% confidence: BULLSHIT penalty

   Principles cited:
   ├── "depth over breadth" (0.92 credibility)
   └── "spec is clear" (0.71 credibility)
```

---

## Feature 3: Interactive Surfaces

> *"The spec is not description—it is generative. The text is not passive—it is interface."*

### Semantic Tokens for ASHC

Beyond the general tokens from Interactive Text spec, ASHC adds:

| Token | Pattern | Affordances |
|-------|---------|-------------|
| `EvidenceLink` | `[Evidence: abc123]` | hover:summary, click:explore, audit:trace |
| `CausalEdge` | `[Nudge: "X" → +15%]` | hover:confidence, click:runs, drill:examples |
| `WorkBet` | `[Bet: 4h @ 75%]` | hover:stakes, click:resolve, status:live |
| `PrincipleRef` | `citing: "tasteful"` | hover:health, click:history, accountability |
| `PassRate` | `95% pass (n=100)` | hover:distribution, click:failures, drill:outliers |

### Interactive Spec Surface

```markdown
# Task: Implement Metacompiler Crown Jewel

**Estimate**: [Bet: 4h @ 75%] ← click to update
**Principles**: citing: "depth over breadth", "tasteful" ← hover for health

## Evidence

Pass rate: 95% pass (n=100) ← click to see failure analysis
Causal insights:
- [Nudge: "add type hints" → +25%] ← click to see supporting runs
- [Nudge: "use global state" → -35%] ← click to avoid

## Tasks

- [x] Design service structure
  - [Evidence: phase1-design] ← traces linked
- [ ] Implement FailureCorpus
  - _Requirements: learn from failures_
```

### The Sheaf Condition

All surfaces must remain coherent:

```
VS Code (plain) ←──┐
                   │
CLI (rich)     ←───┼───→ Single Source of Truth (spec file)
                   │
Web (interactive) ←┘

GLUING: Changes in any surface reflect in all others
```

---

## AGENTESE Integration

### Paths

```
self.metacompiler.*
  .compile          # Spec → ASHCOutput (with learned priors)
  .learn            # Trigger learning from evidence
  .evidence         # View evidence corpus
  .priors           # View learned priors (beneficial/harmful)

self.work.bet.*
  .place            # Place a bet on a task
  .resolve          # Resolve after completion
  .credibility      # View current credibility
  .adversary        # View adversary status

self.work.principles.*
  .health           # View principle health
  .accountability   # Which principles were cited where

time.trace.metacompiler.*
  .generations      # History of all generations
  .failures         # Failure corpus
  .calibration      # Am I getting better at estimates?
```

### CLI Commands

```bash
# Compilation with learned priors
kg metacompiler compile spec/agents/new.md --variations=100

# View what the system has learned
kg metacompiler priors
# → Beneficial: "add type hints" (+25%), "use DI" (+20%)
# → Harmful: "use global state" (-35%), "skip tests" (-28%)

# Work betting
kg work bet "Implement FailureCorpus" --hours 4 --confidence 0.75
kg work resolve --actual 3.5
kg work status

# Principle accountability
kg work principles
# → "depth over breadth": 0.92 (predictive, 15 bets)
# → "quick wins first": 0.33 (discredited, 8 bullshit calls)
```

---

## The Stigmergic Pattern

This is **stigmergic learning**—agents leaving traces that guide future agents.

```
Ant 1: Fails path A → Leaves "avoid" pheromone
Ant 2: Sees pheromone → Takes path B → Succeeds → Leaves "prefer" pheromone
Ant 3: Sees both pheromones → Takes B confidently
```

ASHC equivalent:
```
Gen 1: Fails with global state → CausalEdge(global_state, -0.35)
Gen 2: Sees edge → Avoids global state → Succeeds → CausalEdge(DI, +0.20)
Gen 3: Sees both → Uses DI confidently → Succeeds faster
```

The evidence corpus is a **shared memory** that transcends individual generations.

---

## Connection to Principles

| Principle | How Metacompiler Embodies It |
|-----------|------------------------------|
| **Tasteful** | Learning what works, avoiding what doesn't |
| **Curated** | Evidence accumulates selectively |
| **Ethical** | Transparent accountability for estimates |
| **Joy-Inducing** | Interactive surfaces delight |
| **Composable** | Feedback loops compose |
| **Heterarchical** | System learns from itself (no fixed hierarchy) |
| **Generative** | Priors generate better generations |

---

## The Mirror Test Applied

*"Does K-gent feel like me on my best day?"*

On my best day:
- I learn from mistakes quickly (Failure → Prior)
- I'm honest about uncertainty (Work Betting)
- I know which intuitions actually work (Principle Health)
- I make the complex feel simple (Interactive Surfaces)

The Metacompiler Crown Jewel is **Kent on his best day, systematized**.

---

## Implementation Layers

### Layer 1: Core Infrastructure
- `services/metacompiler/` directory structure
- `EvidenceStore` with SQLite/Postgres backend
- Wire to existing ASHC evidence.py

### Layer 2: Failure Learning
- `FailureCorpus` capturing failed generations
- `CausalLearner` updating graph from failures
- `PriorInjection` using learned priors in prompts

### Layer 3: Work Betting
- `WorkBet` type with credibility tracking
- `WorkAdversary` settling bets
- `PrincipleRegistry` for accountability

### Layer 4: Interactive Surfaces
- ASHC-specific semantic tokens
- `EvidenceExplorer.tsx` component
- `BettingPanel.tsx` component

### Layer 5: AGENTESE Integration
- `self.metacompiler.*` node registration
- `self.work.bet.*` node registration
- CLI commands

---

## The Meta-Insight

> *"The compiler is not a tool. It is a learning system."*

Traditional compilers are static: same input → same output.

ASHC Metacompiler is dynamic: same input → **better output as evidence accumulates**.

It learns from failures. It holds estimates accountable. It makes the invisible visible.

This is not just a compiler. It is a **co-evolving partner** that learns your codebase, your patterns, your intuitions—and gets better at being you.

---

## Closing Meditation

The three brainstorming documents converge:

1. **Failure as Evidence** → The system learns from what goes wrong
2. **Work Betting** → Human estimates become accountable
3. **Interactive Text** → The spec becomes a living surface

Together: a Crown Jewel that **operates** the ASHC metacompiler as a self-improving, accountable, interactive system.

*"Daring, bold, creative, opinionated but not gaudy."*

The Metacompiler Crown Jewel doesn't just compile code. It compiles **trust**.

---

*Voice anchor: "The Mirror Test: Does K-gent feel like me on my best day?"*
