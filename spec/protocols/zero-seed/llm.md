# Zero Seed: LLM-Augmented Intelligence

> *"LLM calls are decisions. Decisions require proofs. Proofs are witnessed."*

**Module**: LLM-Augmented Intelligence
**Depends on**: [`core.md`](./core.md), [`proof.md`](./proof.md)

---

## Purpose

This module specifies how Zero Seed integrates LLM capabilities—principled, witnessed, tiered. The philosophy: **liberal token budgets** enable **radical UX simplification**.

---

## Design Philosophy

### Five Principles

1. **At Decision Points, Not Everywhere** — LLM calls at critical junctures, not batch over everything
2. **Tiered Cost** — Haiku for cheap validation, Sonnet for synthesis, Opus for critical decisions
3. **Fully Witnessed** — Every LLM call creates a Mark with token counts
4. **User Transparency** — Clear indication before/after each call
5. **Budget Conscious** — Session-level token tracking with soft limits

**Anti-Pattern**: Running LLM over all nodes on startup.
**Pattern**: LLM on-demand at user-initiated decision points.

---

## Model Tiers

```python
class LLMTier(Enum):
    SCOUT = "haiku"      # Fast, cheap, good for classification
    ANALYST = "sonnet"   # Balanced, for synthesis and dialogue
    ORACLE = "opus"      # Expensive, for critical decisions


TIER_SPECS = {
    LLMTier.SCOUT: {
        "model": "claude-3-haiku-20240307",
        "cost_per_1m_input": 0.25,
        "cost_per_1m_output": 1.25,
        "token_target": 500,
        "use_cases": ["classification", "validation", "suggestions"],
    },
    LLMTier.ANALYST: {
        "model": "claude-sonnet-4-20250514",
        "cost_per_1m_input": 3.0,
        "cost_per_1m_output": 15.0,
        "token_target": 2000,
        "use_cases": ["synthesis", "proof evaluation", "dialogue"],
    },
    LLMTier.ORACLE: {
        "model": "claude-opus-4-20250514",
        "cost_per_1m_input": 15.0,
        "cost_per_1m_output": 75.0,
        "token_target": 4000,
        "use_cases": ["critical decisions", "constitutional judgment"],
    },
}
```

---

## LLM Call Points

| Operation | Tier | When | Token Budget | Purpose |
|-----------|------|------|--------------|---------|
| **Axiom Mining** | Scout | Stage 1 discovery | ~300/doc | Extract candidate axioms |
| **Mirror Test Dialogue** | Analyst | Stage 2 refinement | ~1000/exchange | Socratic questioning |
| **Proof Validation** | Scout | On proof creation | ~200/proof | Check Toulmin coherence |
| **Edge Suggestion** | Scout | On node creation | ~300/node | Suggest relevant edges |
| **Contradiction Detection** | Analyst | On edge creation | ~500/pair | Detect semantic contradictions |
| **Synthesis Generation** | Analyst | On resolution request | ~1500/synthesis | Create synthesized nodes |
| **Macro Summarization** | Scout | On telescope zoom-out | ~400/cluster | Compress for macro view |
| **Self-Awareness Analysis** | Analyst | On health check | ~2000/analysis | Surface weak spots |

---

## The Witnessed LLM Call

Every LLM call creates a Mark:

```python
@dataclass(frozen=True)
class LLMCallMark:
    """Mark structure for LLM calls."""

    # Standard Mark fields
    origin: str = "zero-seed.llm"
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # LLM-specific fields
    tier: LLMTier
    operation: str                      # e.g., "axiom_mining", "proof_validation"
    prompt_summary: str                 # First 200 chars of prompt
    response_summary: str               # First 200 chars of response

    # Token tracking
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float

    # Context
    node_ids: tuple[NodeId, ...]        # Relevant nodes
    user_visible: bool = True           # Was this shown to user?

    def to_mark(self) -> Mark:
        """Convert to standard Mark for witnessing."""
        return Mark(
            origin=self.origin,
            stimulus=Stimulus(
                kind="llm_call",
                content=self.prompt_summary,
                metadata={
                    "tier": self.tier.value,
                    "operation": self.operation,
                    "input_tokens": self.input_tokens,
                },
            ),
            response=Response(
                kind="llm_response",
                content=self.response_summary,
                success=True,
                metadata={
                    "output_tokens": self.output_tokens,
                    "total_tokens": self.total_tokens,
                    "estimated_cost_usd": self.estimated_cost_usd,
                },
            ),
            timestamp=self.timestamp,
            tags=frozenset({
                "zero-seed",
                "llm",
                f"tier:{self.tier.value}",
                f"op:{self.operation}",
            }),
        )
```

---

## Liberal Token Budgets

### Philosophy

> *"Generous budgets enable radical UX simplification."*

With liberal token budgets, we can:
- Do comprehensive analysis upfront (fewer back-and-forth edits)
- Proactively surface issues (self-awareness)
- Let users ignore suggestions without guilt
- Build complete structures from minimal input

### Session Budgets

```python
class SessionLength(Enum):
    SHORT = "short"        # Quick edits, single-topic
    STANDARD = "standard"  # Typical work session
    LONG = "long"          # Deep exploration, major refactor


@dataclass
class TokenBudget:
    """Liberal session-level token budget."""

    session_limits: dict[SessionLength, int] = field(default_factory=lambda: {
        SessionLength.SHORT: 200_000,      # 200k tokens (~$0.60 haiku, ~$7 sonnet)
        SessionLength.STANDARD: 500_000,   # 500k tokens
        SessionLength.LONG: 2_000_000,     # 2M tokens for deep work
    })

    session_type: SessionLength = SessionLength.STANDARD
    total_used: int = 0
    call_history: list[LLMCallMark] = field(default_factory=list)
    suppressed: set[str] = field(default_factory=set)  # Dismissed suggestions

    @property
    def limit(self) -> int:
        return self.session_limits[self.session_type]

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.total_used)

    @property
    def usage_pct(self) -> float:
        return (self.total_used / self.limit * 100) if self.limit > 0 else 0

    def track(self, call: LLMCallMark) -> None:
        """Track an LLM call."""
        self.total_used += call.total_tokens
        self.call_history.append(call)

    def suppress(self, suggestion_id: str) -> None:
        """User dismisses a suggestion."""
        self.suppressed.add(suggestion_id)

    def is_suppressed(self, suggestion_id: str) -> bool:
        return suggestion_id in self.suppressed

    @property
    def summary(self) -> str:
        return f"Session ({self.session_type.value}): {self.total_used:,}/{self.limit:,} tokens ({self.usage_pct:.1f}%)"
```

---

## Self-Aware Analysis

The system proactively identifies weak spots:

```python
@dataclass
class WeakSpot:
    """A weakness the system has identified."""
    id: str                              # For suppression tracking
    node_id: NodeId | None               # Affected node
    severity: Literal["info", "warning", "critical"]
    category: str                        # e.g., "proof_coherence", "orphan_node"
    title: str
    description: str
    suggestion: str
    auto_fixable: bool
    confidence: float


async def analyze_graph_health(
    graph: ZeroGraph,
    llm: LLMClient,
    budget: TokenBudget,
    scope: Literal["focused", "comprehensive"] = "focused",
) -> SelfAwarenessResult:
    """
    Proactively analyze graph for issues.

    Uses liberal token budget for comprehensive analysis.
    """
    # Collect context
    nodes_summary = summarize_nodes(graph.nodes, max_chars=50_000)
    edges_summary = summarize_edges(graph.edges, max_chars=20_000)
    proofs_summary = summarize_proofs(graph.nodes, max_chars=30_000)

    prompt = f"""Analyze this epistemic graph for weaknesses.

NODES (by layer):
{nodes_summary}

EDGES:
{edges_summary}

PROOFS:
{proofs_summary}

Identify issues in these categories:
1. **Orphan Nodes**: Nodes with no incoming edges (except L1 axioms)
2. **Proof Coherence**: Toulmin proofs with weak warrants or missing backing
3. **Layer Violations**: Edges that skip layers inappropriately
4. **Axiom Drift**: L1-L2 nodes that have drifted from Constitution
5. **Dead Ends**: Nodes with no outgoing edges (except L7)
6. **Contradiction Clusters**: Multiple contradicting nodes without synthesis

{"Focus on the most critical 3-5 issues." if scope == "focused" else "Be comprehensive."}

Return as JSON array with: id, node_id, severity, category, title, description, suggestion, auto_fixable, confidence
"""

    response = await llm.generate(
        system="You analyze epistemic graphs for structural and semantic weaknesses.",
        user=prompt,
        temperature=0.2,
        max_tokens=4000 if scope == "focused" else 10000,
    )

    # Track and witness
    call_mark = create_llm_call_mark(
        tier=LLMTier.ANALYST,
        operation="self_awareness",
        prompt=prompt,
        response=response,
    )
    budget.track(call_mark)
    await witness_store.save_mark(call_mark.to_mark())

    # Parse and filter suppressed
    weak_spots = parse_weak_spots(response.text)
    weak_spots = [w for w in weak_spots if not budget.is_suppressed(w.id)]

    return SelfAwarenessResult(
        weak_spots=weak_spots,
        tokens_used=response.tokens_used,
    )
```

---

## Minimal-Edit UX

The system does more work upfront:

```python
async def create_node_complete(
    user_content: str,
    layer: int,
    graph: ZeroGraph,
    llm: LLMClient,
    budget: TokenBudget,
) -> NodeCreationResult:
    """
    Create a node with ALL supporting structure in one operation.

    Instead of:
      1. User creates node
      2. User adds proof
      3. User adds edges
      4. System validates
      5. User fixes issues

    We do:
      1. User provides content
      2. System creates node + proof + edges + validates
      3. User reviews and accepts (or edits)
    """
    prompt = f"""Create a complete node structure for this content.

USER CONTENT:
{user_content}

TARGET LAYER: L{layer} ({LAYER_NAMES[layer]})

EXISTING GRAPH CONTEXT:
{summarize_relevant_nodes(graph, layer, max_chars=30_000)}

Generate:
1. **Node**: title, cleaned content, path, tags
2. **Proof**: Full Toulmin structure (data, warrant, claim, backing, qualifier, rebuttals)
3. **Edges**: 2-5 edges connecting to existing nodes
4. **Validation**: Pre-check for issues

Return complete JSON structure.
"""

    response = await llm.generate(
        system="You create complete, well-connected epistemic nodes.",
        user=prompt,
        temperature=0.4,
        max_tokens=3000,
    )

    budget.track(create_llm_call_mark(LLMTier.ANALYST, "node_complete", prompt, response))

    result = parse_node_creation_result(response.text)

    # Auto-validate
    if result.validation_issues:
        result = await auto_fix_issues(result, llm, budget)

    return result
```

---

## LLM Operations

### Axiom Mining (Scout)

```python
async def mine_axioms_from_constitution(
    constitution_path: str,
    llm: LLMClient,
    budget: TokenBudget,
) -> list[CandidateAxiom]:
    """Stage 1: Extract axiom candidates. ~300 tokens/doc."""
    content = await read_file(constitution_path)

    prompt = f"""Extract the 3-5 most fundamental axioms from this document.

For each axiom:
1. The statement (one sentence)
2. The source section
3. Why it's irreducible

Document:
{content[:4000]}

Format as JSON.
"""

    response = await llm.generate(
        system="You extract fundamental axioms from principles documents.",
        user=prompt,
        temperature=0.3,
        max_tokens=500,
    )

    budget.track(create_llm_call_mark(LLMTier.SCOUT, "axiom_mining", prompt, response))
    return parse_axiom_candidates(response.text)
```

### Proof Validation (Scout)

```python
async def validate_proof_llm(
    proof: Proof,
    node: ZeroNode,
    llm: LLMClient,
    budget: TokenBudget,
) -> ProofValidation:
    """Validate Toulmin proof structure. ~200 tokens."""
    prompt = f"""Evaluate this Toulmin proof:

DATA: {proof.data}
WARRANT: {proof.warrant}
CLAIM: {proof.claim}
BACKING: {proof.backing}
QUALIFIER: {proof.qualifier}
REBUTTALS: {proof.rebuttals}

Check:
1. Does data support warrant?
2. Does warrant justify claim?
3. Is qualifier appropriate?
4. Is backing sufficient?

Return: {{"coherence": 0.X, "issues": [...], "suggestion": "..."}}
"""

    response = await llm.generate(
        system="You validate Toulmin argument coherence.",
        user=prompt,
        temperature=0.2,
        max_tokens=300,
    )

    budget.track(create_llm_call_mark(LLMTier.SCOUT, "proof_validation", prompt, response, (node.id,)))
    return parse_proof_validation(response.text)
```

### Contradiction Detection (Analyst)

```python
async def detect_contradiction_llm(
    node_a: ZeroNode,
    node_b: ZeroNode,
    llm: LLMClient,
    budget: TokenBudget,
) -> ContradictionAnalysis:
    """Detect semantic contradictions. ~500 tokens."""
    prompt = f"""Analyze whether these two statements contradict:

STATEMENT A ({node_a.title}):
{node_a.content[:500]}

STATEMENT B ({node_b.title}):
{node_b.content[:500]}

Determine:
1. Direct contradiction? (mutually exclusive)
2. Tension? (compatible but pulling different directions)
3. Independent? (unrelated)
4. Complement? (different aspects of same truth)

Return: {{
  "relationship": "contradiction" | "tension" | "independent" | "complement",
  "confidence": 0.X,
  "explanation": "...",
  "synthesis_hint": "..."
}}
"""

    response = await llm.generate(
        system="You analyze logical relationships between statements.",
        user=prompt,
        temperature=0.3,
        max_tokens=400,
    )

    budget.track(create_llm_call_mark(LLMTier.ANALYST, "contradiction_detection", prompt, response, (node_a.id, node_b.id)))
    return parse_contradiction_analysis(response.text)
```

### Synthesis Generation (Analyst)

```python
async def generate_synthesis_llm(
    thesis: ZeroNode,
    antithesis: ZeroNode,
    llm: LLMClient,
    budget: TokenBudget,
) -> ZeroNode:
    """Generate synthesis from contradicting nodes. ~1500 tokens."""
    prompt = f"""Create a synthesis resolving the tension between:

THESIS ({thesis.title}):
{thesis.content}

ANTITHESIS ({antithesis.title}):
{antithesis.content}

The synthesis should:
1. Acknowledge valid core of each position
2. Identify underlying assumption creating tension
3. Propose higher-order perspective encompassing both
4. Be actionable, not just philosophical

Return: {{
  "title": "...",
  "content": "...",
  "resolution_type": "sublation" | "scope_limitation" | "context_dependency" | "false_dichotomy",
  "preserved_from_thesis": "...",
  "preserved_from_antithesis": "...",
  "transcended": "..."
}}
"""

    response = await llm.generate(
        system="You create dialectical syntheses.",
        user=prompt,
        temperature=0.6,
        max_tokens=1000,
    )

    budget.track(create_llm_call_mark(LLMTier.ANALYST, "synthesis_generation", prompt, response, (thesis.id, antithesis.id)))
    return parse_synthesis_node(response.text, thesis, antithesis)
```

---

## User Transparency

### Streamlined Display

With liberal budgets, we simplify:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ✨ Creating node with proof and 4 edges...                                 │
│  ──────────────────────────────────────────────────────────────────────────  │
│  Session: 12,450 / 200,000 tokens (6.2%)                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### After Completion

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ✓ Node created: "Principle of Minimal Authority"                           │
│  ──────────────────────────────────────────────────────────────────────────  │
│  + Proof: Toulmin structure (coherence: 0.91)                               │
│  + Edges: grounds←axiom-001, justifies→goal-003, +2 more                    │
│                                                                             │
│  ⚠️ 1 suggestion: Consider adding backing from Constitution §3              │
│     [Apply] [Ignore] [Ignore all like this]                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Surfacing Weak Spots

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔍 Graph Health (analyzed 47 nodes)                                        │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  ⚠️ WARNING: "goal-005" has weak proof backing                              │
│     Suggestion: Add reference to spec/principles/CONSTITUTION.md            │
│     [Fix automatically] [Edit manually] [Ignore]                            │
│                                                                             │
│  ℹ️ INFO: 3 nodes have no outgoing edges                                    │
│     [Show nodes] [Ignore all orphan warnings]                               │
│                                                                             │
│  Session: 45,200 / 200,000 tokens (22.6%)                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## CLI Integration

```bash
# View session status
kg zero-seed status
# Session (standard): 45,200 / 500,000 tokens (9.0%)

# Start long session
kg zero-seed --session=long

# Analyze graph health
kg zero-seed health
kg zero-seed health --comprehensive

# Create node with full structure
kg zero-seed add "My insight about composability" --layer=3

# Suppress suggestion category
kg zero-seed suppress orphan_warnings

# View suppressed
kg zero-seed suppressed

# Disable LLM for session
kg zero-seed --no-llm

# Force Oracle tier
kg zero-seed synthesize --tier=oracle "node-123" "node-456"
```

---

## Summary: Liberal LLM for Radical UX

| Principle | Implementation |
|-----------|----------------|
| **Liberal Budgets** | 200k short, 500k standard, 2M long |
| **Self-Awareness** | Proactively surface weak spots |
| **Minimal Edits** | User provides content, system builds complete structure |
| **Suppressible** | User can ignore by item or category |
| **Comprehensive Analysis** | Liberal tokens enable thorough health checks |
| **Auto-Fixable** | System applies fixes with user consent |

**Philosophy Shift**: From "cost-conscious, user does work" to "generous budgets, system does work, user reviews."

---

## Open Questions

1. **Cost visibility**: How granular should cost reporting be?
2. **Tier selection**: Should users choose tier or let system decide?
3. **Offline mode**: What happens when LLM unavailable?

---

*"The system surfaces weakness. The user decides what matters. The proof IS witnessed."*
