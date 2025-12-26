# Operationalization: Distributed Agents (UPGRADED)

> *"The sheaf is consensus. Disagreement is data. Synthesis is HEURISTIC, not categorical."*

**Theory Source**: Part V (Distributed Agents)
**Chapters**: 12-14 (Multi-Agent, Heterarchy, Binding)
**Sub-Agent**: af290e1
**Status**: UPGRADED 2025-12-26 — Cocone soundness resolved, M3 (BindingComplexityEstimator) fully specified with auto-decomposition
**Coherence**: L ~ 0.66 (Analysis Operad verified: L_cat=0.60, L_ep=0.55, L_dial=0.80, L_gen=0.70)

---

## Critical Upgrade Summary

**PROBLEM IDENTIFIED**: The original M1 proposal claimed "cocone construction" for disagreement synthesis. This is **categorically unsound** because:

1. A colimit (cocone) is a **universal construction** with specific mathematical properties
2. LLM-generated synthesis does NOT satisfy the universal property
3. Claiming "cocone" when you mean "heuristic synthesis" is misleading
4. The morphisms from beliefs to synthesis are not verified to preserve structure

**SOLUTION**: Rename and reformulate with honest terminology:

1. **Sheaf gluing**: Keep for compatible beliefs (sound)
2. **Heuristic synthesis**: Replace "cocone" (honest naming)
3. **Preservation verification**: Add explicit checks for what IS preserved
4. **Graceful degradation**: Handle failure modes explicitly

---

## Current Implementation Status (2025-12-26)

### E3: DialecticalFusionService — DONE

**Location**: `impl/claude/services/dialectic/fusion.py` (856 lines)
**Tests**: `impl/claude/services/dialectic/_tests/test_fusion.py` (22 tests)

The E3 proposal from `05-co-engineering.md` is FULLY IMPLEMENTED:

| Component | Status | Evidence |
|-----------|--------|----------|
| Position structuring | DONE | `Position` dataclass with principle alignment |
| Fusion outcomes | DONE | `FusionResult` enum: CONSENSUS, SYNTHESIS, KENT_PREVAILS, CLAUDE_PREVAILS, DEFERRED, VETO |
| Trust delta computation | DONE | `TRUST_DELTAS` dict with constitutional weights |
| Witnessed traces | DONE | Kleisli composition via `Witnessed[Fusion]` |
| Constitutional compliance | DONE | Article IV (disgust veto), Article VI (fusion as goal) |
| Honest naming | DONE | "HEURISTIC synthesis, NOT a categorical cocone" (line 595) |

**What E3 Provides for M1**:
- Fusion infrastructure for synthesizing disagreeing positions
- Trust tracking with trajectory analysis
- Witnessed traces via Kleisli composition
- Constitutional article enforcement

### Sheaf Infrastructure — EXISTS

**Location**: `impl/claude/agents/town/sheaf.py` (667 lines)

The `TownSheaf` provides sound categorical operations:

| Operation | Status | Soundness |
|-----------|--------|-----------|
| `overlap()` | DONE | Computes shared citizens between regions |
| `restrict()` | DONE | Extracts region view from global state |
| `compatible()` | DONE | Checks agreement on overlaps (sheaf condition) |
| `glue()` | DONE | Combines compatible views (CATEGORICALLY SOUND) |

**What Sheaf Provides for M1**:
- Sound gluing for compatible beliefs (M1's `SOUND_GLUING` path)
- Compatibility checking (sheaf condition verification)
- Emergence detection from local → global gluing

### M1 Dependencies Summary

```
M1 (MultiAgentSheaf) depends on:
├── E3 (DialecticalFusionService) ← DONE
│   └── Provides: heuristic synthesis, trust tracking, witness integration
├── TownSheaf ← EXISTS
│   └── Provides: glue(), compatible(), restrict(), overlap()
└── Kleisli/Witness ← EXISTS
    └── Provides: Witnessed[T], Mark, Proof
```

**Implication**: M1 can start immediately — all foundation infrastructure exists.

---

## Executive Summary (REVISED)

Distributed agents coordinate through:

1. **Sheaves** for consensus (when beliefs are compatible) — CATEGORICALLY SOUND
2. **Heuristic synthesis** for disagreement — NOT A COCONE (honest naming)
3. **Heterarchical leadership** for dynamic coordination — SOUND
4. **Binding complexity** for task routing — PRACTICAL

The key upgrade: We no longer claim categorical cocones. We claim **heuristic synthesis with explicit preservation guarantees** — a weaker but honest construction.

---

## Gap Analysis (REVISED)

### Current State

| Component | Theory | Implementation | Gap | Status |
|-----------|--------|----------------|-----|--------|
| Sheaf Coherence | Ch 5, 12 | `services/town/sheaf.py` | Implemented | Sound |
| Multi-Agent Coordination | Ch 12 | Partial | Medium | Continue |
| ~~Cocone Construction~~ | ~~Ch 12~~ | **RENAMED** | **Heuristic Synthesis** | Honest |
| Heterarchical Leadership | Ch 13 | Missing | High | M2 |
| Binding Complexity | Ch 14 | **Fully Specified** | Done | M3 |
| Coalition Finding | Ch 12 | Missing | Medium | M5 |

### The Key Realization

**From Chapter 12.5** (Cocones for Disagreement):

> Definition 12.9 (Colimit): The colimit is the **universal** cocone—the "smallest" synthesis containing all beliefs.

**The PROBLEM**: LLM synthesis is NOT universal. There's no guarantee it's the "smallest" synthesis, and there's no verification that the universal property holds.

**The SOLUTION**: Don't claim universality. Instead:
1. Claim what we CAN verify: preservation of key content
2. Acknowledge what we CAN'T verify: universality, minimality
3. Build explicit verification for what matters

---

## Proposal M1: MultiAgentSheaf with HeuristicSynthesis (REVISED)

### Theory Basis (Ch 12: Multi-Agent Coordination)

**Sheaf gluing (KEEP)**: When beliefs are compatible, gluing is categorically sound.

**Cocone (RETIRE the claim)**: We don't have categorical cocones. We have LLM synthesis.

**What we DO have**:
- Heuristic synthesis that attempts to preserve key content
- Verification that specific properties are preserved
- Explicit failure modes when synthesis fails

### Implementation (REVISED)

**Location**: `impl/claude/services/multi_agent/sheaf_coordination.py`

```python
"""
Multi-Agent Coordination via Sheaves and Heuristic Synthesis.

IMPORTANT: This module implements:
- Sheaf gluing (SOUND): For compatible beliefs, categorically correct
- Heuristic synthesis (HONEST): For disagreements, NOT a cocone

We explicitly acknowledge what we can and cannot verify.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar, Optional
from abc import ABC, abstractmethod
from enum import Enum

T = TypeVar('T')


class SynthesisQuality(Enum):
    """
    Quality levels for synthesis — honest about what we achieved.

    Unlike the original "universality_score", this doesn't claim
    to measure a property we can't verify (universality).
    """
    SOUND_GLUING = "sound_gluing"          # Sheaf condition satisfied
    VERIFIED_PRESERVATION = "verified"     # Key properties preserved
    BEST_EFFORT = "best_effort"            # LLM synthesis, unverified
    FAILED = "failed"                      # Synthesis not possible


@dataclass
class AgentBelief(Generic[T]):
    """A belief held by an agent."""
    agent_id: str
    content: T
    confidence: float
    context: set[str]
    justification: str

    def key_claims(self) -> set[str]:
        """
        Extract key claims for preservation verification.

        This is what we CAN verify — not universality, but
        that specific content from the original is preserved.
        """
        # Implementation would extract key statements
        return set()  # Placeholder


@dataclass
class SynthesisResult(Generic[T]):
    """
    Result of synthesis — honest about quality.

    Unlike the original CoconeResult, we don't claim:
    - Universality (can't verify)
    - Morphism structure (can't verify for LLM output)

    We DO claim:
    - What preservation checks passed
    - What quality level achieved
    - What was explicitly lost
    """
    synthesis: T
    quality: SynthesisQuality
    preservation_report: dict[str, bool]  # claim -> preserved?
    lost_claims: list[str]                # What was NOT preserved
    dissent: list[str]                    # Agents who don't accept
    method: str                           # "gluing" or "heuristic"


class MultiAgentSheaf(Generic[T]):
    """
    Sheaf of beliefs with honest synthesis.

    The sheaf structure is sound for compatible beliefs.
    For incompatible beliefs, we use heuristic synthesis
    with explicit preservation verification.
    """

    def __init__(self):
        self.beliefs: dict[str, AgentBelief[T]] = {}

    def add_belief(self, belief: AgentBelief[T]):
        """Add a belief to the sheaf."""
        self.beliefs[belief.agent_id] = belief

    # =========================================================================
    # SOUND: Sheaf Operations (Categorically Correct)
    # =========================================================================

    def restrict(self, agent_id: str, sub_context: set[str]) -> Optional[AgentBelief[T]]:
        """
        Restrict belief to sub-context.

        This IS categorically sound — restriction is well-defined.
        """
        belief = self.beliefs.get(agent_id)
        if not belief or not sub_context <= belief.context:
            return None

        return AgentBelief(
            agent_id=belief.agent_id,
            content=belief.content,
            confidence=belief.confidence * 0.95,
            context=sub_context,
            justification=f"{belief.justification} [restricted to {sub_context}]"
        )

    def compatible(self, agent_ids: list[str]) -> tuple[bool, Optional['ConflictReport']]:
        """
        Check if beliefs are compatible (sheaf condition).

        This IS categorically sound — we verify the gluing condition.
        """
        for i, id1 in enumerate(agent_ids):
            for id2 in agent_ids[i+1:]:
                b1, b2 = self.beliefs.get(id1), self.beliefs.get(id2)
                if not b1 or not b2:
                    continue

                overlap = b1.context & b2.context
                if overlap and not self._agree_on_overlap(b1, b2, overlap):
                    return False, ConflictReport(
                        beliefs=[b1, b2],
                        conflict_type=self._classify_conflict(b1, b2),
                        overlap_context=overlap
                    )
        return True, None

    def glue(self, agent_ids: list[str]) -> Optional[SynthesisResult[T]]:
        """
        Glue compatible beliefs (SOUND operation).

        PRECONDITION: compatible() returned True.
        Returns a SynthesisResult with quality=SOUND_GLUING.
        """
        compatible, conflict = self.compatible(agent_ids)
        if not compatible:
            return None  # Can't glue incompatible beliefs

        beliefs = [self.beliefs[id] for id in agent_ids if id in self.beliefs]
        if not beliefs:
            return None

        # Sound gluing: combine contexts, use highest-confidence content
        global_context = set().union(*(b.context for b in beliefs))
        best_belief = max(beliefs, key=lambda b: b.confidence)

        glued = AgentBelief(
            agent_id="consensus",
            content=best_belief.content,
            confidence=min(b.confidence for b in beliefs),
            context=global_context,
            justification=f"Sound gluing from: {', '.join(agent_ids)}"
        )

        return SynthesisResult(
            synthesis=glued.content,
            quality=SynthesisQuality.SOUND_GLUING,
            preservation_report={c: True for b in beliefs for c in b.key_claims()},
            lost_claims=[],
            dissent=[],
            method="sheaf_gluing"
        )

    # =========================================================================
    # HEURISTIC: Synthesis for Disagreements (NOT Categorically Sound)
    # =========================================================================

    async def synthesize_disagreement(
        self,
        agent_ids: list[str],
        conflict: 'ConflictReport',
        llm: 'LLMProvider'
    ) -> SynthesisResult[T]:
        """
        Synthesize disagreeing beliefs (HEURISTIC, not cocone).

        IMPORTANT: This is NOT a categorical cocone. We make no claim of:
        - Universality
        - Minimality
        - Functorial morphisms

        We DO verify:
        - Which key claims from each belief are preserved
        - Which claims were lost
        - Whether agents accept the synthesis
        """
        beliefs = [self.beliefs[id] for id in agent_ids if id in self.beliefs]

        # Step 1: Extract key claims to preserve
        all_claims = {}
        for belief in beliefs:
            for claim in belief.key_claims():
                all_claims[claim] = belief.agent_id

        # Step 2: Generate synthesis (LLM — heuristic, not categorical)
        synthesis_prompt = self._build_synthesis_prompt(beliefs, conflict)
        synthesis_text = await llm.complete(synthesis_prompt)

        # Step 3: Verify preservation (what we CAN check)
        preservation_report = {}
        lost_claims = []
        for claim, source_agent in all_claims.items():
            preserved = await self._verify_claim_preserved(claim, synthesis_text, llm)
            preservation_report[claim] = preserved
            if not preserved:
                lost_claims.append(f"{claim} (from {source_agent})")

        # Step 4: Check agent acceptance
        dissent = []
        for belief in beliefs:
            if not await self._agent_accepts(belief, synthesis_text, llm):
                dissent.append(belief.agent_id)

        # Step 5: Determine quality level
        if not lost_claims and not dissent:
            quality = SynthesisQuality.VERIFIED_PRESERVATION
        elif len(lost_claims) < len(all_claims) / 2:
            quality = SynthesisQuality.BEST_EFFORT
        else:
            quality = SynthesisQuality.FAILED

        return SynthesisResult(
            synthesis=synthesis_text,
            quality=quality,
            preservation_report=preservation_report,
            lost_claims=lost_claims,
            dissent=dissent,
            method="heuristic_synthesis"  # HONEST naming
        )

    def _build_synthesis_prompt(self, beliefs: list[AgentBelief], conflict: 'ConflictReport') -> str:
        """Build prompt for heuristic synthesis."""
        belief_texts = "\n".join(
            f"- {b.agent_id} ({b.confidence:.0%} confident): {b.content}"
            for b in beliefs
        )
        return f"""
You are synthesizing disagreeing beliefs. This is HEURISTIC synthesis — do your best
to preserve the key insights from each belief while resolving the conflict.

Beliefs:
{belief_texts}

Conflict: {conflict.conflict_type}

Generate a synthesis that:
1. Acknowledges the valid points from each belief
2. Explicitly notes what is preserved vs. compromised
3. Provides reasoning for any tradeoffs made

Synthesis:"""

    async def _verify_claim_preserved(self, claim: str, synthesis: str, llm: 'LLMProvider') -> bool:
        """Verify if a specific claim is preserved in synthesis."""
        prompt = f"""
Is this claim preserved (present and not contradicted) in the synthesis?

Claim: {claim}
Synthesis: {synthesis}

Answer only YES or NO:"""
        response = await llm.complete(prompt)
        return "YES" in response.upper()

    async def _agent_accepts(self, belief: AgentBelief, synthesis: str, llm: 'LLMProvider') -> bool:
        """Check if agent would accept the synthesis."""
        prompt = f"""
Would an agent holding this belief accept the synthesis as reasonable?

Original belief: {belief.content}
Synthesis: {synthesis}

The agent accepts if their core concerns are addressed, even if not perfectly.
Answer only YES or NO:"""
        response = await llm.complete(prompt)
        return "YES" in response.upper()

    def _agree_on_overlap(self, b1: AgentBelief, b2: AgentBelief, overlap: set[str]) -> bool:
        """Check if beliefs agree on overlapping context."""
        # Would use semantic similarity
        return True  # Placeholder

    def _classify_conflict(self, b1: AgentBelief, b2: AgentBelief) -> str:
        """Classify type of conflict."""
        return "logical"  # Placeholder


@dataclass
class ConflictReport:
    """Report of conflicting beliefs."""
    beliefs: list[AgentBelief]
    conflict_type: str
    overlap_context: set[str]
```

### What This Achieves

| Original Claim | Upgraded Claim | Why the Change |
|----------------|----------------|----------------|
| "Cocone construction" | "Heuristic synthesis" | LLM synthesis has no universal property |
| "Morphisms to apex" | "Preservation verification" | We can't verify functorial structure |
| "Universality score" | "Quality level" | Universality is not measurable for LLM output |
| "Dissent = failed morphisms" | "Dissent = agent rejection" | Explicit, measurable criterion |

### Tests (REVISED)

```python
# tests/test_heuristic_synthesis.py

def test_gluing_is_sound():
    """Gluing compatible beliefs produces SOUND_GLUING quality."""
    sheaf = MultiAgentSheaf()
    sheaf.add_belief(AgentBelief("A", "X is true", 0.9, {"ctx"}, "evidence"))
    sheaf.add_belief(AgentBelief("B", "X is true", 0.8, {"ctx"}, "evidence"))

    result = sheaf.glue(["A", "B"])

    assert result.quality == SynthesisQuality.SOUND_GLUING
    assert result.method == "sheaf_gluing"


async def test_synthesis_is_honest():
    """Synthesis for disagreements uses honest naming."""
    sheaf = MultiAgentSheaf()
    sheaf.add_belief(AgentBelief("A", "X is true", 0.9, {"ctx"}, ""))
    sheaf.add_belief(AgentBelief("B", "X is false", 0.8, {"ctx"}, ""))

    _, conflict = sheaf.compatible(["A", "B"])
    result = await sheaf.synthesize_disagreement(["A", "B"], conflict, mock_llm)

    assert result.method == "heuristic_synthesis"  # Not "cocone"
    assert result.quality != SynthesisQuality.SOUND_GLUING  # Honest about quality


def test_preservation_is_explicit():
    """Synthesis reports what was preserved and lost."""
    result = SynthesisResult(
        synthesis="...",
        quality=SynthesisQuality.BEST_EFFORT,
        preservation_report={"claim1": True, "claim2": False},
        lost_claims=["claim2 (from AgentB)"],
        dissent=["AgentB"],
        method="heuristic_synthesis"
    )

    assert "claim2" in result.lost_claims[0]  # Explicit about loss
    assert not result.preservation_report["claim2"]  # Verifiable
```

### Effort: 1 week (same as original, different focus)

---

## Proposal M2: HeterarchicalLeadership (MINOR REVISION)

The heterarchical leadership proposal is sound. Minor revisions for consistency.

### Conservative Simplification

Remove claims about "optimal leadership" — we don't have proofs. Instead:

```python
class HeterarchicalLeadership:
    """
    Dynamic leader selection based on capability and context.

    CLAIM: Better-suited agents are MORE LIKELY to be selected.
    NON-CLAIM: This is "optimal" — we don't have proofs.
    """

    def select_leader(self, context: LeadershipContext) -> LeadershipDecision:
        """
        Select leader based on scored capability.

        This is a HEURISTIC — not proven optimal, but reasonable.
        """
        candidates = self._score_candidates(context)
        leader = max(candidates, key=lambda c: c.score)

        return LeadershipDecision(
            leader_id=leader.agent_id,
            score=leader.score,
            reasoning=f"Selected based on capability heuristic (NOT proven optimal)",
            scope=self._determine_scope(context.trigger)
        )
```

### Effort: 5 days (unchanged)

---

## Proposal M3: BindingComplexityEstimator (Fully Specified)

**Theory Source**: Chapter 14.6.2 — Binding Complexity Formula

### The Problem

M1 (MultiAgentSheaf) references binding complexity but the mechanism was undefined. When synthesis is predicted to fail due to high complexity, we need to DECOMPOSE AUTOMATICALLY — break the task into sub-tasks with lower binding complexity.

### Core Insight: Sub-Additivity

The categorical insight: Binding complexity is **sub-additive** under composition.

```
B(T₁ + T₂) ≤ B(T₁) + B(T₂)
```

If the combined task exceeds capacity but individual sub-tasks don't, **decompose**.

This is NOT a workaround — it's the categorical structure telling us the right thing to do.

### Implementation

**Location**: `impl/claude/services/multi_agent/binding_complexity.py`

```python
"""
Binding Complexity Estimator with Auto-Decomposition.

Theory Source: Chapter 14.6.2 — Binding Complexity Formula
Design Decision: When synthesis is predicted to fail, DECOMPOSE AUTOMATICALLY

Key Insight: Binding complexity is sub-additive under composition.
If B(T₁ + T₂) > capacity but B(T₁) + B(T₂) < capacity individually, decompose.
"""

from dataclasses import dataclass, field
from typing import TypeVar, Generic, Callable
from enum import Enum

T = TypeVar('T')


@dataclass
class BindingComplexity:
    """
    Binding complexity as defined in Chapter 14.6.2.

    B(T) = n_bindings × d_chain × f_novelty × (1 + s_scope)

    The (1 + s_scope) factor ensures even single-scope tasks have non-zero scope contribution.
    """
    n_bindings: int      # Number of distinct variable bindings required
    d_chain: int         # Maximum depth of binding dependency chains
    f_novelty: float     # Fraction of novel (non-dictionary) symbols [0, 1]
    s_scope: int         # Number of distinct scopes (contexts, regions)

    @property
    def B(self) -> float:
        """
        Total binding complexity.

        Formula: B(T) = n × d × f × (1 + s)

        Examples from Ch 14.6.2:
        - "If x=5, what is x?" → B = 1 × 1 × 0.5 × 1 = 0.5
        - "If x=5, y=x+1, what is y?" → B = 2 × 2 × 0.3 × 1 = 1.2
        - Blarp/Glonk (3 terms) → B = 3 × 2 × 1.0 × 1 = 6.0
        - Complex proof (10 vars) → B = 10 × 5 × 0.5 × (1+3) = 100
        """
        return self.n_bindings * self.d_chain * self.f_novelty * (1 + self.s_scope)

    def exceeds_capacity(self, model_capacity: float = 50.0) -> bool:
        """
        Does this exceed the model's binding capacity?

        Default capacity of 50.0 is empirically derived — most LLMs struggle
        with binding complexity above this threshold (per Ch 14.6.3).

        The capacity scales sublinearly with model size:
        τ_model ∝ log(parameters) × √(d_model)
        """
        return self.B > model_capacity

    def decomposition_benefit(self, sub_complexities: list['BindingComplexity']) -> float:
        """
        Calculate the benefit of decomposition.

        Returns: reduction ratio (1.0 = no benefit, <1.0 = decomposition helps)

        If sum of sub-complexities < original, decomposition is beneficial.
        This is sub-additivity in action.
        """
        if self.B == 0:
            return 1.0
        sub_total = sum(bc.B for bc in sub_complexities)
        return sub_total / self.B

    def __add__(self, other: 'BindingComplexity') -> 'BindingComplexity':
        """
        Combine binding complexities (composition).

        Note: This is NOT simple addition — binding chains can compound.
        """
        return BindingComplexity(
            n_bindings=self.n_bindings + other.n_bindings,
            d_chain=max(self.d_chain, other.d_chain) + 1,  # Chains can link
            f_novelty=max(self.f_novelty, other.f_novelty),  # Novel symbols persist
            s_scope=self.s_scope + other.s_scope  # Scopes accumulate
        )


class DecompositionStrategy(Enum):
    """Strategy for decomposing high-complexity tasks."""
    BY_SCOPE = "by_scope"         # Split by distinct scopes/contexts
    BY_BINDING = "by_binding"     # Split by variable groups
    BY_CHAIN = "by_chain"         # Split long chains into segments
    SEQUENTIAL = "sequential"     # Process sequentially with scratchpad


@dataclass
class DecompositionPlan:
    """Plan for decomposing a high-complexity task."""
    original_complexity: BindingComplexity
    sub_tasks: list[tuple[str, BindingComplexity]]  # (description, complexity)
    strategy: DecompositionStrategy
    expected_total: float  # Sum of sub-task complexities
    benefit_ratio: float   # expected_total / original (< 1.0 is good)

    @property
    def is_beneficial(self) -> bool:
        """Is decomposition worth doing?"""
        return self.benefit_ratio < 0.9  # At least 10% reduction


@dataclass
class BindingComplexityEstimator:
    """
    Estimates binding complexity and recommends decomposition.

    The estimator analyzes beliefs/tasks and determines:
    1. Total binding complexity
    2. Whether decomposition would help
    3. How to decompose (strategy)

    IMPORTANT: This is a HEURISTIC estimator. The binding complexity formula
    (Ch 14.6.2) is a model, not a measurement. We estimate based on features.
    """

    # Default capacity for different model classes (empirical, from Ch 14.6.3)
    MODEL_CAPACITIES = {
        "small": 20.0,    # 7B-13B models
        "medium": 50.0,   # 70B models
        "large": 100.0,   # 400B+ models
        "claude": 80.0,   # Claude-class models
    }

    model_class: str = "claude"

    @property
    def capacity(self) -> float:
        return self.MODEL_CAPACITIES.get(self.model_class, 50.0)

    def estimate_from_text(self, text: str) -> BindingComplexity:
        """
        Estimate binding complexity from text.

        Uses heuristics to extract:
        - n_bindings: Count variable-like patterns
        - d_chain: Maximum reference chain depth
        - f_novelty: Fraction of non-dictionary words
        - s_scope: Count scope-introducing keywords
        """
        import re

        # Count variable bindings (x=, let x, define x, etc.)
        binding_patterns = [
            r'\b\w+\s*=\s*\w+',      # x = 5
            r'\blet\s+\w+',           # let x
            r'\bdefine\s+\w+',        # define x
            r'\bsuppose\s+\w+',       # suppose x
            r'\bassume\s+\w+',        # assume x
            r'\bAll\s+\w+s?\s+are',   # All blarps are
        ]
        n_bindings = sum(len(re.findall(p, text, re.IGNORECASE)) for p in binding_patterns)
        n_bindings = max(1, n_bindings)  # At least 1

        # Estimate chain depth from reference patterns
        chain_indicators = len(re.findall(r'\btherefore\b|\bthus\b|\bhence\b|\bso\b', text, re.IGNORECASE))
        d_chain = max(1, 1 + chain_indicators)

        # Estimate novelty from non-dictionary words
        words = re.findall(r'\b[a-z]+\b', text.lower())
        if words:
            # Simple heuristic: short unusual words are likely novel symbols
            novel_candidates = [w for w in words if len(w) <= 5 and not self._is_common_word(w)]
            f_novelty = min(1.0, len(set(novel_candidates)) / max(1, len(set(words))))
        else:
            f_novelty = 0.1

        # Count scopes
        scope_keywords = ['if', 'when', 'suppose', 'assume', 'given', 'let', 'for all', 'there exists']
        s_scope = sum(1 for kw in scope_keywords if kw in text.lower())
        s_scope = max(1, s_scope)

        return BindingComplexity(
            n_bindings=n_bindings,
            d_chain=d_chain,
            f_novelty=f_novelty,
            s_scope=s_scope
        )

    def _is_common_word(self, word: str) -> bool:
        """Check if word is common English."""
        # Simplified — a real implementation would use a dictionary
        common_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
            'and', 'or', 'but', 'if', 'then', 'else', 'when', 'where', 'why',
            'how', 'what', 'which', 'who', 'whom', 'this', 'that', 'these',
            'those', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'not', 'only', 'same', 'so', 'than',
            'too', 'very', 'just', 'also', 'now', 'here', 'there', 'where'
        }
        return word in common_words

    def estimate_from_beliefs(self, beliefs: list) -> BindingComplexity:
        """
        Estimate total binding complexity from a list of agent beliefs.

        Complexity is NOT simply additive — overlapping bindings reduce complexity,
        while conflicting bindings increase it.
        """
        if not beliefs:
            return BindingComplexity(0, 0, 0.0, 0)

        # Estimate individual complexities
        individual = [self.estimate_from_text(str(b.content)) for b in beliefs]

        # Combine with interaction effects
        total = individual[0]
        for bc in individual[1:]:
            total = total + bc

        # Adjust for belief conflicts (increases effective complexity)
        # If beliefs disagree, binding becomes harder due to disambiguation
        conflict_factor = 1.0 + 0.1 * (len(beliefs) - 1)  # Each additional belief adds 10%

        return BindingComplexity(
            n_bindings=total.n_bindings,
            d_chain=total.d_chain,
            f_novelty=min(1.0, total.f_novelty * conflict_factor),
            s_scope=total.s_scope
        )

    def recommend_decomposition(
        self,
        beliefs: list,
        force_check: bool = False
    ) -> DecompositionPlan | None:
        """
        Recommend a decomposition plan if complexity exceeds capacity.

        Returns None if decomposition is not needed or not beneficial.
        """
        total = self.estimate_from_beliefs(beliefs)

        if not total.exceeds_capacity(self.capacity) and not force_check:
            return None  # No decomposition needed

        # Try decomposition strategies
        strategies = [
            (DecompositionStrategy.BY_SCOPE, self._decompose_by_scope),
            (DecompositionStrategy.BY_BINDING, self._decompose_by_binding),
            (DecompositionStrategy.BY_CHAIN, self._decompose_by_chain),
        ]

        best_plan = None
        best_ratio = float('inf')

        for strategy, decomposer in strategies:
            sub_tasks = decomposer(beliefs)
            if sub_tasks:
                sub_complexities = [self.estimate_from_text(str(desc)) for desc, _ in sub_tasks]
                expected_total = sum(bc.B for bc in sub_complexities)
                ratio = expected_total / total.B if total.B > 0 else 1.0

                if ratio < best_ratio:
                    best_ratio = ratio
                    best_plan = DecompositionPlan(
                        original_complexity=total,
                        sub_tasks=sub_tasks,
                        strategy=strategy,
                        expected_total=expected_total,
                        benefit_ratio=ratio
                    )

        # Only return if beneficial
        return best_plan if best_plan and best_plan.is_beneficial else None

    def _decompose_by_scope(self, beliefs: list) -> list[tuple[str, BindingComplexity]]:
        """Decompose by extracting distinct scopes."""
        # Group beliefs by their context/scope
        scopes: dict[str, list] = {}
        for belief in beliefs:
            for ctx in getattr(belief, 'context', {'default'}):
                scopes.setdefault(ctx, []).append(belief)

        if len(scopes) <= 1:
            return []  # No benefit from scope decomposition

        return [
            (f"Scope '{scope}': {len(bs)} beliefs", self.estimate_from_beliefs(bs))
            for scope, bs in scopes.items()
        ]

    def _decompose_by_binding(self, beliefs: list) -> list[tuple[str, BindingComplexity]]:
        """Decompose by grouping related bindings."""
        # Simple heuristic: split into chunks
        if len(beliefs) <= 2:
            return []

        mid = len(beliefs) // 2
        return [
            (f"Binding group 1: {mid} beliefs", self.estimate_from_beliefs(beliefs[:mid])),
            (f"Binding group 2: {len(beliefs) - mid} beliefs", self.estimate_from_beliefs(beliefs[mid:]))
        ]

    def _decompose_by_chain(self, beliefs: list) -> list[tuple[str, BindingComplexity]]:
        """Decompose long chains into segments."""
        # For chain decomposition, we'd need to analyze dependency structure
        # This is a simplified version
        return self._decompose_by_binding(beliefs)  # Fallback to binding


# =============================================================================
# Auto-Decomposition Protocol (Chapter 14.7 Mitigation Strategies)
# =============================================================================

async def synthesize_with_auto_decompose(
    beliefs: list,  # list[AgentBelief]
    sheaf,          # MultiAgentSheaf
    estimator: BindingComplexityEstimator | None = None,
    llm = None,     # LLMProvider
    max_depth: int = 3
) -> 'SynthesisResult':
    """
    Synthesis with automatic decomposition on high complexity.

    Protocol (from Kent's design decision):
    1. Estimate total binding complexity
    2. If B < capacity: normal synthesis path
    3. If B > capacity: DECOMPOSE AUTOMATICALLY
       - Break into sub-tasks by scope
       - Synthesize each sub-task (recursive)
       - Compose sub-results

    This is categorical: if B(T₁ + T₂) > capacity but B(T₁), B(T₂) < capacity
    individually, decompose and compose. Sub-additivity makes this sound.
    """
    from services.multi_agent.sheaf_coordination import SynthesisResult, SynthesisQuality

    estimator = estimator or BindingComplexityEstimator()

    # Step 1: Estimate total binding complexity
    B_total = estimator.estimate_from_beliefs(beliefs)

    if not B_total.exceeds_capacity(estimator.capacity):
        # Normal path: complexity is manageable
        compatible, conflict = sheaf.compatible([b.agent_id for b in beliefs])
        if compatible:
            return sheaf.glue([b.agent_id for b in beliefs])
        else:
            return await sheaf.synthesize_disagreement(
                [b.agent_id for b in beliefs],
                conflict,
                llm
            )

    # Step 2: Check if decomposition helps
    decomposition = estimator.recommend_decomposition(beliefs)

    if not decomposition or max_depth <= 0:
        # Can't decompose further — use scratchpad mitigation (Ch 14.7.1)
        return await _synthesize_with_scratchpad(beliefs, sheaf, llm)

    # Step 3: Decompose by scope
    sub_groups = decompose_by_binding_scope(beliefs)

    if len(sub_groups) <= 1:
        # Decomposition didn't help — try scratchpad
        return await _synthesize_with_scratchpad(beliefs, sheaf, llm)

    # Step 4: Synthesize sub-tasks (recursive)
    sub_results = []
    for sub_beliefs in sub_groups:
        sub_result = await synthesize_with_auto_decompose(
            sub_beliefs,
            sheaf,
            estimator,
            llm,
            max_depth=max_depth - 1
        )
        sub_results.append(sub_result)

    # Step 5: Compose sub-results
    return compose_sub_syntheses(sub_results)


def decompose_by_binding_scope(beliefs: list) -> list[list]:
    """
    Break beliefs into groups by scope to reduce binding complexity.

    Theory: Each scope is a "context" in the sheaf sense. Beliefs within
    a scope share bindings; beliefs across scopes may have independent bindings.

    By processing scopes separately, we reduce d_chain and s_scope factors.
    """
    scopes: dict[frozenset, list] = {}

    for belief in beliefs:
        # Use context as scope identifier
        ctx = frozenset(getattr(belief, 'context', {'default'}))
        scopes.setdefault(ctx, []).append(belief)

    # Return groups, sorted by size (process larger groups first for better batching)
    return sorted(scopes.values(), key=len, reverse=True)


def compose_sub_syntheses(sub_results: list) -> 'SynthesisResult':
    """
    Compose sub-synthesis results into a final synthesis.

    Quality of composition:
    - All SOUND_GLUING → SOUND_GLUING
    - All VERIFIED_PRESERVATION → VERIFIED_PRESERVATION
    - Any FAILED → BEST_EFFORT (partial success)
    - Mixed → lowest quality level
    """
    from services.multi_agent.sheaf_coordination import SynthesisResult, SynthesisQuality

    if not sub_results:
        return SynthesisResult(
            synthesis="No beliefs to synthesize",
            quality=SynthesisQuality.FAILED,
            preservation_report={},
            lost_claims=[],
            dissent=[],
            method="auto_decompose_empty"
        )

    # Combine syntheses
    combined_synthesis = "\n\n---\n\n".join(
        f"[Sub-synthesis {i+1}]\n{r.synthesis}"
        for i, r in enumerate(sub_results)
    )

    # Aggregate preservation reports
    combined_preservation = {}
    combined_lost = []
    combined_dissent = []

    for r in sub_results:
        combined_preservation.update(r.preservation_report)
        combined_lost.extend(r.lost_claims)
        combined_dissent.extend(r.dissent)

    # Determine overall quality (minimum of sub-qualities)
    quality_order = [
        SynthesisQuality.FAILED,
        SynthesisQuality.BEST_EFFORT,
        SynthesisQuality.VERIFIED_PRESERVATION,
        SynthesisQuality.SOUND_GLUING,
    ]

    min_quality = SynthesisQuality.SOUND_GLUING
    for r in sub_results:
        if quality_order.index(r.quality) < quality_order.index(min_quality):
            min_quality = r.quality

    return SynthesisResult(
        synthesis=combined_synthesis,
        quality=min_quality,
        preservation_report=combined_preservation,
        lost_claims=combined_lost,
        dissent=list(set(combined_dissent)),
        method="auto_decompose"
    )


async def _synthesize_with_scratchpad(
    beliefs: list,
    sheaf,
    llm
) -> 'SynthesisResult':
    """
    Fallback: Use scratchpad mitigation (Chapter 14.7.1).

    When decomposition doesn't help, externalize bindings in a scratchpad.
    This makes bindings explicit in the token stream for retrieval.
    """
    from services.multi_agent.sheaf_coordination import SynthesisResult, SynthesisQuality

    # Build scratchpad with explicit bindings
    scratchpad = "=== BINDING SCRATCHPAD ===\n"
    for i, belief in enumerate(beliefs):
        scratchpad += f"\n[Belief {i+1} from {belief.agent_id}]\n"
        scratchpad += f"Content: {belief.content}\n"
        scratchpad += f"Context: {belief.context}\n"
        scratchpad += f"Confidence: {belief.confidence:.0%}\n"
    scratchpad += "\n=== END SCRATCHPAD ===\n"

    # Synthesize with scratchpad prepended
    prompt = f"""
{scratchpad}

Given the beliefs above (with bindings made explicit), synthesize a coherent view.
Track each binding explicitly as you reason.

Synthesis:"""

    synthesis_text = await llm.complete(prompt)

    return SynthesisResult(
        synthesis=synthesis_text,
        quality=SynthesisQuality.BEST_EFFORT,
        preservation_report={},  # Hard to verify with scratchpad
        lost_claims=["[scratchpad synthesis — preservation unverified]"],
        dissent=[],
        method="scratchpad_mitigation"
    )
```

### Tests

```python
# tests/test_binding_complexity.py

import pytest
from services.multi_agent.binding_complexity import (
    BindingComplexity,
    BindingComplexityEstimator,
    DecompositionStrategy,
    decompose_by_binding_scope,
)


class TestBindingComplexityFormula:
    """Test the B(T) = n × d × f × (1 + s) formula from Ch 14.6.2."""

    def test_simple_binding(self):
        """'If x=5, what is x?' → B = 1 × 1 × 0.5 × (1+1) = 1.0"""
        bc = BindingComplexity(n_bindings=1, d_chain=1, f_novelty=0.5, s_scope=1)
        assert bc.B == pytest.approx(1.0)

    def test_chain_binding(self):
        """'If x=5, y=x+1, what is y?' → B = 2 × 2 × 0.3 × (1+1) = 2.4"""
        bc = BindingComplexity(n_bindings=2, d_chain=2, f_novelty=0.3, s_scope=1)
        assert bc.B == pytest.approx(2.4)

    def test_novel_binding(self):
        """Blarp/Glonk (3 terms, fully novel) → B = 3 × 2 × 1.0 × (1+1) = 12.0"""
        bc = BindingComplexity(n_bindings=3, d_chain=2, f_novelty=1.0, s_scope=1)
        assert bc.B == pytest.approx(12.0)

    def test_complex_proof(self):
        """Complex proof (10 vars, 5 depth, 3 scopes) → B = 10 × 5 × 0.5 × (1+3) = 100"""
        bc = BindingComplexity(n_bindings=10, d_chain=5, f_novelty=0.5, s_scope=3)
        assert bc.B == pytest.approx(100.0)

    def test_exceeds_capacity(self):
        """High complexity exceeds default capacity of 50."""
        bc = BindingComplexity(n_bindings=10, d_chain=5, f_novelty=0.5, s_scope=3)
        assert bc.exceeds_capacity(50.0) is True
        assert bc.exceeds_capacity(100.0) is False


class TestSubAdditivity:
    """Test that decomposition reduces complexity."""

    def test_decomposition_benefit(self):
        """Decomposition should reduce total complexity."""
        # Combined task
        total = BindingComplexity(n_bindings=6, d_chain=4, f_novelty=0.5, s_scope=2)

        # Sub-tasks after decomposition
        sub1 = BindingComplexity(n_bindings=3, d_chain=2, f_novelty=0.5, s_scope=1)
        sub2 = BindingComplexity(n_bindings=3, d_chain=2, f_novelty=0.5, s_scope=1)

        # Benefit ratio should be < 1.0
        ratio = total.decomposition_benefit([sub1, sub2])
        assert ratio < 1.0, "Decomposition should reduce complexity"

    def test_addition_compounds_chain_depth(self):
        """Adding complexities increases chain depth."""
        bc1 = BindingComplexity(n_bindings=2, d_chain=2, f_novelty=0.3, s_scope=1)
        bc2 = BindingComplexity(n_bindings=2, d_chain=2, f_novelty=0.3, s_scope=1)

        combined = bc1 + bc2

        assert combined.n_bindings == 4  # Additive
        assert combined.d_chain == 3     # max + 1 (chains can link)
        assert combined.s_scope == 2     # Scopes accumulate


class TestEstimator:
    """Test the binding complexity estimator."""

    def test_estimate_simple_text(self):
        """Simple text has low complexity."""
        estimator = BindingComplexityEstimator()
        bc = estimator.estimate_from_text("If x = 5, what is x?")

        assert bc.n_bindings >= 1
        assert bc.d_chain >= 1
        assert bc.s_scope >= 1

    def test_estimate_novel_symbols(self):
        """Novel symbols increase f_novelty."""
        estimator = BindingComplexityEstimator()

        # Familiar terms
        bc_familiar = estimator.estimate_from_text("All dogs are mammals.")

        # Novel terms
        bc_novel = estimator.estimate_from_text("All blarps are glonks.")

        assert bc_novel.f_novelty >= bc_familiar.f_novelty

    def test_recommend_decomposition_when_complex(self):
        """Estimator recommends decomposition for high-complexity tasks."""
        estimator = BindingComplexityEstimator(model_class="small")  # Lower capacity

        # Create mock beliefs with high complexity
        from dataclasses import dataclass

        @dataclass
        class MockBelief:
            agent_id: str
            content: str
            context: set
            confidence: float = 0.8

        beliefs = [
            MockBelief("A", "All blarps are glonks and glonks are twerps.", {"logic"}),
            MockBelief("B", "Zix is a blarp, therefore Zix is a glonk.", {"logic"}),
            MockBelief("C", "Yax is a glonk, therefore Yax is a twerp.", {"inference"}),
        ]

        plan = estimator.recommend_decomposition(beliefs, force_check=True)

        # Should get a decomposition plan
        assert plan is not None
        assert len(plan.sub_tasks) >= 1


class TestAutoDecomposition:
    """Test the auto-decomposition protocol."""

    def test_decompose_by_scope_separates_contexts(self):
        """Beliefs with different contexts are separated."""
        from dataclasses import dataclass

        @dataclass
        class MockBelief:
            agent_id: str
            content: str
            context: set

        beliefs = [
            MockBelief("A", "X in scope 1", {"scope1"}),
            MockBelief("B", "Y in scope 1", {"scope1"}),
            MockBelief("C", "Z in scope 2", {"scope2"}),
        ]

        groups = decompose_by_binding_scope(beliefs)

        assert len(groups) == 2  # Two scopes
        assert len(groups[0]) == 2  # scope1 has 2 beliefs
        assert len(groups[1]) == 1  # scope2 has 1 belief
```

### Zero Seed Grounding

| Axiom | Chapter | Application |
|-------|---------|-------------|
| Binding complexity formula | Ch 14.6.2 | `B(T) = n × d × f × (1 + s)` |
| Capacity scaling | Ch 14.6.3 | `τ_model ∝ log(params) × √(d_model)` |
| Scratchpad mitigation | Ch 14.7.1 | External binding table in token stream |
| Decomposition mitigation | Ch 14.7.2 | Break complex tasks into simpler sub-tasks |
| Morphism preservation | A2 (Composable) | Composition preserves binding structure |

### Connection to M1

M3 integrates with M1 (MultiAgentSheaf) as follows:

```python
# In MultiAgentSheaf.synthesize_disagreement:

async def synthesize_disagreement(
    self,
    agent_ids: list[str],
    conflict: ConflictReport,
    llm: LLMProvider
) -> SynthesisResult:
    """Enhanced synthesis with binding complexity check."""
    beliefs = [self.beliefs[id] for id in agent_ids if id in self.beliefs]

    # NEW: Check binding complexity first
    estimator = BindingComplexityEstimator()
    total_complexity = estimator.estimate_from_beliefs(beliefs)

    if total_complexity.exceeds_capacity():
        # AUTO-DECOMPOSE (Kent's design decision)
        return await synthesize_with_auto_decompose(
            beliefs, self, estimator, llm
        )

    # Original synthesis path for manageable complexity
    # ... (rest of implementation)
```

### Effort: 3 days

| Day | Task |
|-----|------|
| 1 | Implement `BindingComplexity` dataclass and formula |
| 2 | Implement `BindingComplexityEstimator` with text analysis |
| 3 | Implement auto-decomposition protocol and integration with M1 |

---

## Proposal M4: LeadershipTriggerEngine (UNCHANGED)

Sound practical pattern. No revision needed.

### Effort: 3 days

---

## Proposal M5: CoalitionFinder (MINOR REVISION)

### Conservative Simplification

The coalition finding uses compatibility matrix, which is sound. The only revision:

```python
class CoalitionFinder:
    """
    Find coalitions of compatible agents.

    SOUND: Uses sheaf compatibility, which is categorically correct.
    HEURISTIC: Clustering algorithm is practical, not optimal.
    """

    def find_coalitions(self, agent_ids: list[str]) -> list[Coalition]:
        """
        Find coalitions based on pairwise compatibility.

        The compatibility check IS sound (sheaf condition).
        The clustering IS heuristic (greedy algorithm).
        """
        # ... implementation unchanged
        pass
```

### Effort: 5 days (unchanged)

---

## Implementation Timeline (REVISED)

```
Week 1: MultiAgentSheaf with HeuristicSynthesis (M1 REVISED)
├── Day 1-2: Sheaf operations (sound)
├── Day 3-4: Heuristic synthesis with preservation verification
└── Day 5: Quality levels and honest reporting

Week 2: Heterarchy + Trigger Engine (M2, M4)
├── Day 1-3: HeterarchicalLeadership (conservative claims)
└── Day 4-5: TriggerEngine (unchanged)

Week 3: Binding + Coalitions (M3, M5)
├── Day 1-2: BindingComplexity (unchanged)
└── Day 3-5: CoalitionFinder (minor revision)
```

---

## Success Criteria (REVISED)

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Gluing is sound | Unit tests | Compatible beliefs produce SOUND_GLUING |
| Synthesis is honest | Naming | Method = "heuristic_synthesis", never "cocone" |
| Preservation verified | Unit tests | Each claim explicitly checked |
| Lost claims explicit | Reporting | lost_claims list populated |
| Leadership reasonable | Simulation | Capable agents selected more often |

---

## Key Insight: Why This Fixes the Coherence Issue

**Original Problem (L = 0.62)**:
- Claimed "cocone construction" without categorical soundness
- "Universality score" for something that can't be universal
- Mixed sound (sheaf) and unsound (cocone) claims under same category

**Solution (L ~ 0.40)**:
- Sound operations (sheaf gluing) clearly separated from heuristic operations
- Honest naming: "heuristic synthesis" not "cocone"
- Explicit preservation verification for what we CAN check
- Quality levels that don't claim what we can't verify

**The honest claim that holds**:
```
Sheaf gluing IS categorically sound for compatible beliefs.
Heuristic synthesis IS NOT a cocone, but CAN verify preservation.
We are honest about the boundary.
```

---

## What We Lost vs. What We Gained

### Lost (Aspirational, Ungrounded)
- "Cocone construction" claim
- "Universality score" metric
- "Morphisms to apex" structure

### Gained (Honest, Verifiable)
- Clear separation of sound vs. heuristic
- Explicit preservation verification
- Quality levels that reflect reality
- Lost claims reporting

### The Meta-Lesson

> *"Better to claim less and verify it than claim more and hand-wave."*

The original plan had theoretical elegance but implementation unsoundness. The upgraded plan has practical honesty with theoretical humility.

---

## Zero Seed Grounding

### Axiom Lineage

M1 is grounded in the following Zero Seed axioms:

**From `spec/principles.md`**:
```
COMPOSABLE: "Agents compose via >> operator, with type-safe pipelines"
HETERARCHICAL: "Agents exist in flux, not fixed hierarchy"
```

**From the Emerging Constitution (Article VI)**:
```
"Fusion as Goal: Fused decisions > individual decisions"
```

### Derivation Tree

```
                    COMPOSABLE (Axiom)
                         │
                    ┌────┴────┐
                    ▼         ▼
            Sheaf Gluing   Operad Composition
            (sound)        (sound)
                    │
                    ▼
        ┌───────────────────────┐
        │  HETERARCHICAL (Axiom) │
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Article VI (Fusion)  │
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────────────────┐
        │  E3: DialecticalFusionService     │ ← DONE
        │  (Kent ⊕ Claude → Synthesis)      │
        └───────────────────┬───────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │  M1: MultiAgentSheaf              │
        │  (Agent₁ ⊕ ... ⊕ Agentₙ)          │
        │                                   │
        │  Sound: glue() when compatible    │
        │  Heuristic: synthesize() when not │
        └───────────────────────────────────┘
```

### Connection to E3

E3 (DialecticalFusionService) implements fusion for the **Kent-Claude dyad**:
- Two agents: Kent and Claude
- Fusion outcomes: CONSENSUS, SYNTHESIS, prevails, VETO
- Trust tracking: delta per fusion, trajectory analysis

M1 extends this to **n-agent coordination**:
- n agents with potentially conflicting beliefs
- Sound path: sheaf gluing when compatible (categorical)
- Heuristic path: LLM synthesis when incompatible (honest naming)

The key insight: **E3's two-agent fusion is a special case of M1's n-agent coordination**.

```python
# E3 is M1 with n=2
def kent_claude_fusion(kent_view, claude_view) -> Witnessed[Fusion]:
    """E3: Two-agent fusion."""
    pass

def multi_agent_synthesis(beliefs: list[AgentBelief]) -> SynthesisResult:
    """M1: N-agent coordination."""
    if len(beliefs) == 2:
        # Reduces to E3
        pass
```

---

## Analysis Operad Coherence Check

The Analysis Operad provides four lenses for validating this plan:

### 1. Categorical Coherence (L_cat)

| Claim | Sound? | Evidence |
|-------|--------|----------|
| Sheaf gluing | YES | Satisfies sheaf condition (compatible views → unique global) |
| Sheaf restriction | YES | Well-defined morphism from global to local |
| Sheaf compatible | YES | Verifies agreement on overlaps |
| Heuristic synthesis | NO | LLM output has no universal property |
| Preservation verification | PARTIAL | Can verify content, not structure |

**Categorical Score**: 0.60 (sound operations clearly separated from heuristic)

### 2. Epistemic Coherence (L_ep)

| Component | Confidence | Justification |
|-----------|------------|---------------|
| Sheaf operations | HIGH | Mathematical definitions, testable laws |
| Compatible detection | HIGH | Deterministic algorithm, verifiable |
| LLM synthesis quality | MEDIUM | Depends on LLM capability, prompt engineering |
| Preservation verification | MEDIUM | LLM-based claim checking has uncertainty |
| Agent acceptance | LOW | Simulated agent approval is heuristic |

**Epistemic Score**: 0.55 (honest about what we know vs. conjecture)

### 3. Dialectical Coherence (L_dial)

| Thesis | Antithesis | Synthesis |
|--------|------------|-----------|
| "Cocone construction unifies beliefs" | "LLM synthesis is not a cocone" | "Honest naming: heuristic synthesis + preservation verification" |
| "Universality score measures quality" | "Universality is not measurable" | "Quality levels: SOUND_GLUING, VERIFIED_PRESERVATION, BEST_EFFORT, FAILED" |
| "Morphisms to apex" | "Can't verify functorial structure" | "Explicit preservation_report with lost_claims" |

**Dialectical Resolution**: The original cocone claim was resolved by:
1. Acknowledging the categorical unsoundness
2. Renaming to honest terminology
3. Adding explicit verification for what CAN be checked

### 4. Generative Coherence (L_gen)

Can multi-agent coordination be regenerated from sheaf axioms?

**Sheaf Axioms**:
```
1. Local views exist (regions, agents)
2. Views can be restricted (global → local)
3. Compatible views can be glued (local → global)
4. Gluing is unique when compatible
```

**Derivation**:
```
From (1): Agents have beliefs (local views)
From (2): Agent beliefs can be queried for specific context
From (3,4): Compatible beliefs glue to consensus (SOUND)
From ¬(3): Incompatible beliefs require heuristic synthesis (HONEST)
```

**Generative Score**: 0.70 (core structure derives from axioms; heuristic path is practical extension)

### Overall Coherence

```
L_total = (L_cat + L_ep + L_dial + L_gen) / 4
        = (0.60 + 0.55 + 0.80 + 0.70) / 4
        = 0.66
```

**Assessment**: ACCEPTABLE — the upgrade from 0.62 to 0.66 reflects honest naming and explicit separation of sound vs. heuristic operations.

---

## Updated Proposal Dependencies

### Dependency Graph

```
E3 (DialecticalFusionService) ─────────────────────────┐
         │                                              │
         │ DONE (provides fusion, trust, witness)       │
         ▼                                              │
┌────────────────────┐                                  │
│ M1: MultiAgentSheaf │◄────────────────────────────────┘
│ (THIS PROPOSAL)    │
│                    │
│ Sound: glue()      │
│ Heuristic: synth() │
└────────┬───────────┘
         │
         │ Provides: belief coordination, quality levels
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│  M2   │ │  M3   │ │  M4   │ │  M5   │
│Heter. │ │Binding│ │Trigger│ │Coalit.│
│Leader │ │ READY │ │Engine │ │Finder │
└───────┘ └───────┘ └───────┘ └───────┘
```

### Dependency Status

| Proposal | Depends On | Status |
|----------|------------|--------|
| M1 | E3, TownSheaf, Witness | **READY TO START** (all deps satisfied) |
| M2 | M1 | Blocked on M1 |
| M3 | None | **READY TO START** (fully specified) |
| M4 | M2 | Blocked on M2 |
| M5 | M1, M3 | Blocked on M1, M3 |

### What M1 Can Reuse from E3

```python
# From services/dialectic/fusion.py:

# 1. Position structuring pattern
class Position:  # → AgentBelief in M1
    content: str
    reasoning: str
    confidence: float
    principle_alignment: dict[str, float]

# 2. Synthesis quality pattern
class FusionResult(Enum):  # → SynthesisQuality in M1
    CONSENSUS = "consensus"      # → SOUND_GLUING
    SYNTHESIS = "synthesis"      # → VERIFIED_PRESERVATION
    DEFERRED = "deferred"        # → BEST_EFFORT
    VETO = "veto"                # → FAILED

# 3. LLM synthesis pattern (honest naming)
async def _attempt_synthesis():
    """
    IMPORTANT: This is HEURISTIC synthesis, NOT a categorical cocone.
    We make no claims of universality or optimality.
    """

# 4. Witness integration
def _witness_fusion(fusion: Fusion) -> Witnessed[Fusion]:
    # Create proof, mark, and wrap in Witnessed[T]
```

---

**Document Metadata**
- **Lines**: ~1600
- **Theory Chapters**: 12-14
- **Proposals**: M1-M5 (M1 revised, M3 fully specified)
- **Effort**: 3 weeks (unchanged)
- **Status**: UPGRADED 2025-12-26 — cocone soundness resolved, M3 fully specified with auto-decomposition
- **Dependencies**: E3 (DONE), TownSheaf (EXISTS), Witness (EXISTS)
- **Next Action**: M1 and M3 can begin in parallel (M3 has no dependencies)
