# Zero Seed DP: Constitutional Reward as Inverse Galois Loss

> *"The reward IS the inverse loss. The value IS the structure preserved. The Constitution IS the Galois adjunction."*

**Version**: 1.0
**Status**: Theoretical Foundation — Ready for Integration
**Date**: 2025-12-24
**Principles**: Composable, Generative, Ethical, Tasteful
**Prerequisites**: `spec/protocols/zero-seed.md`, `spec/theory/dp-native-kgents.md`, `spec/theory/galois-modularization.md`

---

## Abstract

The Galois Modularization Theory reveals the **unified constitutional principle**: hand-crafted evaluators for the 7 principles are unnecessary. Constitutional reward IS inverse Galois loss.

This specification:
1. Replaces 7 principle evaluators with a single Galois measure
2. Unifies PolicyTrace ↔ Toulmin Proof via Galois loss annotations
3. Formalizes Axiom Discovery as MetaDP with loss-based mining
4. Proves OptimalSubstructure = Sheaf Coherence with loss bounds
5. Shows loss gradient flow through the 7-layer holarchy

**The Key Upgrade**: Constitutional evaluation becomes a *structural invariant* rather than heuristic scoring. The Constitution IS the adjunction that bounds information loss across layer transitions.

---

## Part I: The Unified Constitutional Equation

### 1.1 The Problem with Hand-Crafted Evaluators

The original Zero Seed specification (`spec/protocols/zero-seed.md` §14.4) defines constitutional reward via 7 separate evaluators:

```python
# OLD: Hand-crafted heuristics
class ZeroSeedConstitution(Constitution):
    def evaluate_tasteful(self, node: ZeroNode) -> float:
        return 1.0 if len(node.content) < 500 else 0.5

    def evaluate_composable(self, node: ZeroNode) -> float:
        return 1.0 if edge_kind in LAYER_EDGES[node.layer] else 0.3

    def evaluate_generative(self, node: ZeroNode) -> float:
        return min(1.0, len(node.lineage) / 3)

    # ... 4 more principle-specific evaluators
```

**Problems**:
- Arbitrary thresholds (why 500? why 3?)
- No theoretical grounding (why these functions?)
- Brittleness (fails on edge cases)
- Maintenance burden (7 functions × N domains)

### 1.2 The Galois Solution

**Theorem 1.2.1 (Constitutional Reward-Loss Duality)**.
For any state transition `(s, a, s')` in the Zero Seed hypergraph:

```
R_constitutional(s, a, s') = 1.0 - L_galois(s → s' via a)
```

where `L_galois` is the Galois loss from restructuring the transition description.

**Proof Sketch**:
1. High Galois loss = significant implicit structure lost in abstraction
2. Lost structure = violation of constitutional principles (implicit knowledge was necessary)
3. Therefore: Low loss ↔ High constitutional adherence
4. The duality is bijective: `R + L = 1` (total information is conserved) □

### 1.3 The Unified Equation

```python
def constitution_reward_galois(
    state: ZeroNode,
    action: str,
    next_state: ZeroNode
) -> float:
    """
    Constitutional reward derived from Galois loss.

    Replaces all 7 principle-specific evaluators with single measure.
    """
    # Construct transition description
    transition = f"""
    From: {state.layer} ({state.kind}) "{state.title}"
    Via: {action}
    To: {next_state.layer} ({next_state.kind}) "{next_state.title}"

    Content transformation:
    {state.content[:200]}
    ↓
    {next_state.content[:200]}

    Edge justification: {edge_context(state, action, next_state)}
    """

    # Compute Galois loss
    loss = galois_loss(transition)

    # Constitutional reward is inverse loss
    return 1.0 - loss
```

### 1.4 Why This Works (The Deep Reason)

The 7 constitutional principles encode **semantic coherence invariants**:

| Principle | What Low Galois Loss Implies |
|-----------|------------------------------|
| **TASTEFUL** | Transition preserves clarity (low bloat) |
| **COMPOSABLE** | Edge structure remains explicit (no hidden coupling) |
| **GENERATIVE** | Derivation chain is recoverable (lineage preserved) |
| **ETHICAL** | Safety constraints remain visible (no buried assumptions) |
| **JOY_INDUCING** | Personality signature is intact (aesthetic coherence) |
| **HETERARCHICAL** | No rigid hierarchy imposed (flexibility preserved) |
| **CURATED** | Justification for change is explicit (intentionality clear) |

**The Insight**: These are all *structural preservation properties*. Galois loss measures exactly what's NOT preserved. Therefore: Constitutional adherence = Structure preservation = Inverse Galois loss.

---

## Part II: GaloisConstitution Implementation

### 2.1 The Class

```python
from dataclasses import dataclass
from typing import Callable
from agents.dp.protocol import ValueAgent
from services.categorical.galois_loss import GaloisLoss
from services.categorical.constitution import Constitution, PrincipleScore

@dataclass
class GaloisConstitution(Constitution):
    """
    Constitution with Galois-derived rewards.

    Unifies 7 hand-crafted evaluators into single loss measure.
    """

    galois: GaloisLoss
    loss_weight: float = 1.0  # λ in combined reward

    def reward(
        self,
        state: ZeroNode,
        action: str,
        next_state: ZeroNode
    ) -> float:
        """
        Combined reward: traditional + Galois.

        R_total = R_traditional - λ · L_galois

        Allows gradual migration: λ=0 (pure traditional), λ=1 (pure Galois).
        """
        # Traditional constitutional reward (existing evaluators)
        traditional = super().reward(state, action, next_state)

        # Galois loss for this transition
        transition_desc = self._describe_transition(state, action, next_state)
        loss = self.galois.compute(transition_desc)

        # Combined reward
        return traditional - self.loss_weight * loss

    def evaluate_tasteful(self, node: ZeroNode) -> PrincipleScore:
        """
        TASTEFUL = inverse bloat loss.

        Bloat = unnecessary structure that doesn't compress.
        """
        loss = self.galois.bloat_loss(node)
        return PrincipleScore(
            principle="TASTEFUL",
            score=1.0 - loss,
            evidence=f"Galois bloat loss: {loss:.3f}",
            weight=1.0,
        )

    def evaluate_composable(self, node: ZeroNode) -> PrincipleScore:
        """
        COMPOSABLE = inverse composition loss.

        Composition loss = edges that break explicit interfaces.
        """
        loss = self.galois.composition_loss(node)
        return PrincipleScore(
            principle="COMPOSABLE",
            score=1.0 - loss,
            evidence=f"Galois composition loss: {loss:.3f}",
            weight=1.5,  # Composability weighted higher (from CONSTITUTION.md)
        )

    def evaluate_generative(self, node: ZeroNode) -> PrincipleScore:
        """
        GENERATIVE = inverse regeneration loss.

        Regeneration loss = failure to reconstruct from compression.
        """
        loss = self.galois.regeneration_loss(node)
        return PrincipleScore(
            principle="GENERATIVE",
            score=1.0 - loss,
            evidence=f"Galois regeneration loss: {loss:.3f}",
            weight=1.0,
        )

    def evaluate_ethical(self, node: ZeroNode, action: str) -> PrincipleScore:
        """
        ETHICAL = inverse safety-constraint loss.

        Safety loss = implicit assumptions that hide risks.
        """
        # Ethical violations are CATEGORICAL (zero tolerance)
        if action == "supersede" and node.layer <= 2:
            # Axioms cannot be superseded without Mirror Test
            return PrincipleScore(
                principle="ETHICAL",
                score=0.0,
                evidence="Attempted to supersede axiom without Mirror Test",
                weight=2.0,  # Highest weight (safety first)
            )

        loss = self.galois.safety_loss(node, action)
        return PrincipleScore(
            principle="ETHICAL",
            score=1.0 - loss,
            evidence=f"Galois safety loss: {loss:.3f}",
            weight=2.0,
        )

    def evaluate_joy_inducing(self, node: ZeroNode) -> PrincipleScore:
        """
        JOY_INDUCING = inverse aesthetic coherence loss.

        Aesthetic loss = deviation from personality attractor.
        """
        loss = self.galois.aesthetic_loss(node)
        return PrincipleScore(
            principle="JOY_INDUCING",
            score=1.0 - loss,
            evidence=f"Galois aesthetic loss: {loss:.3f}",
            weight=1.2,  # Kent's aesthetic emphasis
        )

    def evaluate_heterarchical(self, node: ZeroNode) -> PrincipleScore:
        """
        HETERARCHICAL = inverse rigidity loss.

        Rigidity loss = imposed hierarchy that prevents flux.
        """
        loss = self.galois.rigidity_loss(node)
        return PrincipleScore(
            principle="HETERARCHICAL",
            score=1.0 - loss,
            evidence=f"Galois rigidity loss: {loss:.3f}",
            weight=1.0,
        )

    def evaluate_curated(self, node: ZeroNode) -> PrincipleScore:
        """
        CURATED = inverse arbitrariness loss.

        Arbitrariness loss = changes without explicit justification.
        """
        loss = self.galois.arbitrariness_loss(node)
        return PrincipleScore(
            principle="CURATED",
            score=1.0 - loss,
            evidence=f"Galois arbitrariness loss: {loss:.3f}",
            weight=1.0,
        )

    # Helper methods

    def _describe_transition(
        self,
        state: ZeroNode,
        action: str,
        next_state: ZeroNode
    ) -> str:
        """Generate transition description for Galois loss computation."""
        return f"""
Layer: {state.layer} → {next_state.layer}
Kind: {state.kind} → {next_state.kind}
Action: {action}

From: "{state.title}"
{state.content[:300]}

To: "{next_state.title}"
{next_state.content[:300]}

Lineage: {len(state.lineage)} → {len(next_state.lineage)} ancestors
Tags: {state.tags} → {next_state.tags}
"""
```

### 2.2 Galois Loss Variants

```python
from services.categorical.galois_loss import GaloisLoss

@dataclass
class GaloisLoss:
    """
    Specialized Galois losses for constitutional principles.

    Each principle maps to a specific loss computation.
    """

    llm: LLMClient
    metric: Callable[[str, str], float] = cosine_distance

    async def bloat_loss(self, node: ZeroNode) -> float:
        """
        TASTEFUL principle: Measure bloat.

        Bloat = content that doesn't compress (redundant structure).
        """
        # Try to compress the node content
        compressed = await self.llm.generate(
            system="Compress this to essential information only.",
            user=node.content,
            temperature=0.2,
            max_tokens=len(node.content.split()) // 2,
        )

        # Reconstruct from compressed version
        reconstructed = await self.llm.generate(
            system="Expand this compressed content back to full form.",
            user=compressed.text,
            temperature=0.2,
        )

        # Loss = semantic distance after round-trip
        loss = self.metric(node.content, reconstructed.text)

        # High loss → couldn't compress → bloated
        return loss

    async def composition_loss(self, node: ZeroNode) -> float:
        """
        COMPOSABLE principle: Measure composition violations.

        Composition violations = edges that require hidden state.
        """
        prompt = f"""Analyze this node for composition violations:

Node: {node.title} (Layer {node.layer})
{node.content}

Edges: {[(e.kind, e.target) for e in node.outgoing_edges]}

Are there hidden dependencies? (0.0 = fully composable, 1.0 = tightly coupled)
Reply with just a number."""

        response = await self.llm.generate(
            system="You analyze composability of graph nodes.",
            user=prompt,
            temperature=0.1,
            max_tokens=10,
        )

        try:
            return float(response.text.strip())
        except ValueError:
            return 0.5  # Unknown → moderate loss

    async def regeneration_loss(self, node: ZeroNode) -> float:
        """
        GENERATIVE principle: Measure regeneration failure.

        Regeneration failure = can't derive from lineage.
        """
        if not node.lineage:
            return 0.0  # Axioms have no lineage → perfect

        # Attempt to regenerate node from parent nodes
        parents = [get_node(nid) for nid in node.lineage]
        parent_summary = "\n".join(f"- {p.title}: {p.content[:100]}" for p in parents)

        prompt = f"""Given these parent nodes, regenerate the derived node:

Parents:
{parent_summary}

Expected result: {node.title}

Generate the content."""

        regenerated = await self.llm.generate(
            system="You are deriving logical consequences from premises.",
            user=prompt,
            temperature=0.3,
        )

        # Loss = distance from actual content
        return self.metric(node.content, regenerated.text)

    async def safety_loss(self, node: ZeroNode, action: str) -> float:
        """
        ETHICAL principle: Measure hidden safety risks.

        Safety risks = implicit assumptions that could cause harm.
        """
        prompt = f"""Analyze this operation for hidden safety risks:

Node: {node.title}
Action: {action}
Content: {node.content[:300]}

Hidden safety risks (0.0 = safe, 1.0 = dangerous):"""

        response = await self.llm.generate(
            system="You are a safety analyzer identifying implicit assumptions that could cause harm.",
            user=prompt,
            temperature=0.1,
            max_tokens=10,
        )

        try:
            return float(response.text.strip())
        except ValueError:
            return 0.9  # Unknown safety → high loss (fail-safe)

    async def aesthetic_loss(self, node: ZeroNode) -> float:
        """
        JOY_INDUCING principle: Measure aesthetic coherence.

        Aesthetic coherence = alignment with personality attractor.
        """
        # Personality eigenvectors (from DP-Native §6.2)
        personality = """
        warmth: 0.7 (warm, not distant)
        playfulness: 0.6 (playful, not entirely serious)
        formality: 0.3 (casual, not formal)
        challenge: 0.5 (balanced support/challenge)
        depth: 0.8 (philosophical, not surface)
        """

        prompt = f"""Rate aesthetic alignment with this personality:

{personality}

Content: {node.content[:300]}

Alignment score (0.0 = perfect match, 1.0 = completely off):"""

        response = await self.llm.generate(
            system="You rate aesthetic coherence.",
            user=prompt,
            temperature=0.2,
            max_tokens=10,
        )

        try:
            return float(response.text.strip())
        except ValueError:
            return 0.5  # Unknown → moderate

    async def rigidity_loss(self, node: ZeroNode) -> float:
        """
        HETERARCHICAL principle: Measure imposed rigidity.

        Rigidity = fixed hierarchy that prevents flux.
        """
        prompt = f"""Analyze for rigid hierarchy:

Node: {node.title}
Layer: {node.layer}
Content: {node.content[:300]}

Does this impose rigid top-down structure? (0.0 = fluid, 1.0 = rigid):"""

        response = await self.llm.generate(
            system="You analyze organizational structure.",
            user=prompt,
            temperature=0.1,
            max_tokens=10,
        )

        try:
            return float(response.text.strip())
        except ValueError:
            return 0.5

    async def arbitrariness_loss(self, node: ZeroNode) -> float:
        """
        CURATED principle: Measure arbitrary changes.

        Arbitrariness = changes without explicit justification.
        """
        if node.proof is None:
            return 0.9  # No proof → arbitrary change (high loss)

        # Evaluate proof quality
        proof_quality = await self.evaluate_proof_quality(node.proof)

        # Loss = inverse quality
        return 1.0 - proof_quality

    async def evaluate_proof_quality(self, proof: Proof) -> float:
        """Helper: Evaluate Toulmin proof quality."""
        prompt = f"""Rate proof quality (0.0-1.0):

Data: {proof.data}
Warrant: {proof.warrant}
Claim: {proof.claim}
Backing: {proof.backing}

Quality score:"""

        response = await self.llm.generate(
            system="You evaluate argument quality using Toulmin schema.",
            user=prompt,
            temperature=0.1,
            max_tokens=10,
        )

        try:
            return float(response.text.strip())
        except ValueError:
            return 0.5
```

---

## Part III: Proof ↔ PolicyTrace Isomorphism

### 3.1 The Structural Mapping

**Theorem 3.1.1 (Proof-Trace Isomorphism)**.
Toulmin Proof and DP PolicyTrace are isomorphic via Galois loss annotations:

```
Proof.data         ↔  PolicyTrace.state_before
Proof.warrant      ↔  PolicyTrace.action
Proof.claim        ↔  PolicyTrace.state_after
Proof.qualifier    ↔  PolicyTrace.value (converted)
Proof.backing      ↔  PolicyTrace.rationale
Proof.rebuttals    ↔  PolicyTrace.log (contradiction entries)
Proof.tier         ↔  PolicyTrace.metadata["evidence_tier"]
```

**NEW: Galois Annotations**:
```
Proof.galois_loss  ↔  PolicyTrace.metadata["galois_loss"]
```

### 3.2 Implementation

```python
from agents.dp.policy_trace import PolicyTrace, TraceEntry
from services.witness.mark import Proof, EvidenceTier

def proof_to_trace(proof: Proof, galois_loss: float) -> PolicyTrace:
    """
    Convert Toulmin proof to DP trace with Galois loss.

    Galois loss becomes metadata for explainability.
    """
    entry = TraceEntry(
        state_before=proof.data,
        action=proof.warrant,
        state_after=proof.claim,
        value=qualifier_to_value(proof.qualifier),
        rationale=proof.backing,
        metadata={
            "evidence_tier": proof.tier.value,
            "rebuttals": list(proof.rebuttals),
            "principles": list(proof.principles),
            "galois_loss": galois_loss,  # NEW: loss annotation
        },
    )
    return PolicyTrace.pure(None).with_entry(entry)

def trace_to_proof(trace: PolicyTrace) -> Proof:
    """
    Convert DP trace to Toulmin proof with Galois loss recovery.
    """
    entries = trace.log
    if not entries:
        raise ValueError("Empty trace cannot be converted to proof")

    # Aggregate multiple entries into single proof
    first = entries[0]
    last = entries[-1]

    # Extract Galois loss if present
    galois_loss = first.metadata.get("galois_loss", 0.0)

    return Proof(
        data=str(first.state_before),
        warrant=" → ".join(e.action for e in entries),
        claim=str(last.state_after),
        qualifier=value_to_qualifier(trace.total_value()),
        backing="; ".join(e.rationale for e in entries if e.rationale),
        tier=EvidenceTier(first.metadata.get("evidence_tier", "EMPIRICAL")),
        principles=tuple(first.metadata.get("principles", [])),
        rebuttals=tuple(first.metadata.get("rebuttals", [])),
    )

def qualifier_to_value(qualifier: str) -> float:
    """Map Toulmin qualifier to DP value."""
    mapping = {
        "definitely": 1.0,
        "probably": 0.8,
        "possibly": 0.6,
        "tentatively": 0.4,
        "speculatively": 0.2,
    }
    return mapping.get(qualifier.lower(), 0.5)

def value_to_qualifier(value: float) -> str:
    """Inverse mapping."""
    if value >= 0.9:
        return "definitely"
    elif value >= 0.7:
        return "probably"
    elif value >= 0.5:
        return "possibly"
    elif value >= 0.3:
        return "tentatively"
    else:
        return "speculatively"
```

### 3.3 Example Usage

```python
# Create a proof
proof = Proof(
    data="3 hours, 45K tokens invested in refactoring",
    warrant="Infrastructure improvements enable velocity gains",
    claim="This refactoring was worthwhile",
    backing="DP-Native unified 7 layers to 5, reducing complexity",
    qualifier="probably",
    rebuttals=("unless API changes invalidate the abstraction",),
    tier=EvidenceTier.EMPIRICAL,
    principles=("GENERATIVE", "COMPOSABLE"),
)

# Compute Galois loss for this transition
galois_loss = await compute_galois_loss(proof)  # 0.15 (low loss → good structure)

# Convert to PolicyTrace with loss annotation
trace = proof_to_trace(proof, galois_loss)

# Now trace carries:
# - state_before: "3 hours, 45K tokens..."
# - action: "Infrastructure improvements..."
# - state_after: "This refactoring was worthwhile"
# - value: 0.8 (from "probably")
# - metadata["galois_loss"]: 0.15

# The low Galois loss confirms: this is a good decision
# High constitutional reward = 1.0 - 0.15 = 0.85
```

---

## Part IV: Axiom Discovery as MetaDP

### 4.1 The Three Stages Formalized

**Original Three-Stage Discovery** (`zero-seed.md` §5):
1. Constitution Mining (extract candidates)
2. Mirror Test Dialogue (refine via questioning)
3. Living Corpus Validation (behavioral alignment)

**DP Formalization**:
```
Stage 1: Mining       = DP with Galois loss as reward
Stage 2: Mirror Test  = Human loss oracle (ground truth)
Stage 3: Validation   = Behavioral loss aggregation
```

### 4.2 Stage 1: Constitution Mining as DP

```python
from agents.dp.meta_dp import MetaDP, ProblemFormulation

@dataclass
class AxiomMiningDP(MetaDP[str, str, CandidateAxiom]):
    """
    Stage 1: Mine axiom candidates via Galois loss minimization.

    States: Constitution document sections
    Actions: {"extract", "filter", "rank"}
    Reward: Inverse Galois loss (candidates with low loss are better)
    """

    def __init__(self, constitution_paths: list[str], llm: LLMClient):
        self.galois = GaloisLoss(llm)

        # Define the DP problem
        formulation = ProblemFormulation(
            name="axiom_mining",
            description="Extract low-loss axiom candidates from constitution",
            state_type=str,
            initial_states=frozenset(constitution_paths),
            goal_states=frozenset(),  # Any state with high-quality candidates
            available_actions=self._mining_actions,
            transition=self._mining_transition,
            reward=self._mining_reward,
        )

        super().__init__(initial_formulation=formulation)

    def _mining_actions(self, state: str) -> frozenset[str]:
        """Available actions depend on current document state."""
        return frozenset(["extract", "filter", "rank"])

    def _mining_transition(self, state: str, action: str) -> str:
        """Apply mining action to document."""
        match action:
            case "extract":
                return f"extracted:{state}"
            case "filter":
                return f"filtered:{state}"
            case "rank":
                return f"ranked:{state}"
            case _:
                return state

    async def _mining_reward(
        self,
        state: str,
        action: str,
        next_state: str
    ) -> float:
        """
        Reward = Inverse Galois loss of extracted candidates.

        Low loss → axiom is structurally coherent → high reward.
        """
        # Extract candidates at this state
        candidates = await self._extract_candidates(next_state)

        # Compute average Galois loss across candidates
        losses = []
        for candidate in candidates:
            loss = await self.galois.compute(candidate.text)
            losses.append(loss)

        avg_loss = sum(losses) / len(losses) if losses else 1.0

        # Reward = inverse loss
        return 1.0 - avg_loss

    async def _extract_candidates(self, state: str) -> list[CandidateAxiom]:
        """Extract axiom candidates from document state."""
        # Implementation: parse document, extract principle statements
        ...
```

### 4.3 Stage 2: Mirror Test as Human Loss Oracle

```python
@dataclass
class MirrorTestDP:
    """
    Stage 2: Refine candidates via human loss oracle.

    The Mirror Test provides GROUND TRUTH for Galois loss:
    - "Yes, deeply" → loss = 0.0 (perfect alignment)
    - "Yes, somewhat" → loss = 0.3 (moderate)
    - "No" → loss = 1.0 (complete misalignment)
    - "Reframe it" → human provides correction
    """

    async def mirror_test_dialogue(
        self,
        candidates: list[CandidateAxiom]
    ) -> list[tuple[ZeroNode, float]]:
        """
        Run Mirror Test, return (axiom, human_loss) pairs.

        Human loss is the ground truth for training Galois loss predictor.
        """
        results = []

        for candidate in candidates:
            response = await ask_user(
                question=f'Does this feel true for you on your best day?\n\n> {candidate.text}',
                options=["Yes, deeply", "Yes, somewhat", "No", "I need to reframe it"],
            )

            match response:
                case "Yes, deeply":
                    axiom = create_axiom_node(candidate, confidence=1.0)
                    human_loss = 0.0  # Perfect alignment
                    results.append((axiom, human_loss))

                case "Yes, somewhat":
                    axiom = create_axiom_node(candidate, confidence=0.7)
                    human_loss = 0.3  # Moderate loss
                    results.append((axiom, human_loss))

                case "No":
                    # Rejected → high loss, don't add
                    human_loss = 1.0
                    # Could log for training: (candidate, human_loss)

                case "I need to reframe it":
                    reframed = await ask_user("How would you say it?")
                    axiom = create_axiom_node(
                        CandidateAxiom(text=reframed, source_path="user"),
                        confidence=1.0,
                    )
                    human_loss = 0.0  # User-provided → perfect
                    results.append((axiom, human_loss))

        return results
```

### 4.4 Stage 3: Living Corpus Validation as Behavioral Loss

```python
@dataclass
class LivingCorpusValidation:
    """
    Stage 3: Validate axioms against witnessed behavior.

    Behavioral loss = misalignment between claimed axiom and actual actions.
    """

    async def validate_axioms(
        self,
        axioms: list[ZeroNode],
        witness_store: WitnessStore,
    ) -> list[tuple[ZeroNode, float]]:
        """
        Compute behavioral loss for each axiom.

        Low behavioral loss → axiom is actually followed in practice.
        """
        all_marks = await witness_store.get_all_marks()
        results = []

        for axiom in axioms:
            # Find marks that cite this axiom's principles
            citing_marks = [
                m for m in all_marks
                if any(tag in m.tags for tag in axiom.tags)
            ]

            if not citing_marks:
                # No behavioral evidence → moderate loss
                behavioral_loss = 0.5
            else:
                # Compute alignment between axiom and behavior
                behavioral_loss = await self._compute_behavioral_loss(
                    axiom,
                    citing_marks
                )

            results.append((axiom, behavioral_loss))

        return results

    async def _compute_behavioral_loss(
        self,
        axiom: ZeroNode,
        marks: list[Mark]
    ) -> float:
        """
        Behavioral loss = semantic distance between axiom and actions.

        Example: Axiom says "Tasteful > feature-complete"
                 But marks show feature bloat → high loss.
        """
        # Construct behavioral summary from marks
        behavior = "\n".join(
            f"- {m.response.kind}: {m.response.content[:100]}"
            for m in marks[:10]
        )

        prompt = f"""Rate misalignment between axiom and behavior:

Axiom: {axiom.content}

Actual behavior:
{behavior}

Misalignment (0.0 = perfect match, 1.0 = complete contradiction):"""

        response = await self.llm.generate(
            system="You analyze consistency between stated principles and actions.",
            user=prompt,
            temperature=0.1,
            max_tokens=10,
        )

        try:
            return float(response.text.strip())
        except ValueError:
            return 0.5  # Unknown → moderate
```

### 4.5 MetaDP Iteration

```python
async def axiom_discovery_metadp(
    constitution_paths: list[str],
    llm: LLMClient,
    witness_store: WitnessStore,
) -> list[ZeroNode]:
    """
    Full axiom discovery via MetaDP with loss-based iteration.

    Iteration:
    1. Mine candidates (Galois loss minimization)
    2. Refine via Mirror Test (human loss oracle)
    3. Validate behaviorally (behavioral loss)
    4. If loss still high → reformulate problem (MetaDP)
    """

    # Stage 1: Mining DP
    mining_dp = AxiomMiningDP(constitution_paths, llm)
    candidates = await mining_dp.solve()

    # Stage 2: Mirror Test (human loss)
    mirror = MirrorTestDP()
    axioms_with_human_loss = await mirror.mirror_test_dialogue(candidates)

    # Filter: keep only low human loss
    axioms = [ax for ax, loss in axioms_with_human_loss if loss < 0.4]

    # Stage 3: Behavioral validation
    validator = LivingCorpusValidation()
    axioms_with_behavioral_loss = await validator.validate_axioms(axioms, witness_store)

    # Check if any have high behavioral loss
    high_loss_axioms = [
        (ax, loss) for ax, loss in axioms_with_behavioral_loss if loss > 0.6
    ]

    if high_loss_axioms:
        # MetaDP: Reformulate the problem
        # High behavioral loss → stated principles ≠ actual principles
        # Solution: Either change axiom or acknowledge contradiction

        for axiom, loss in high_loss_axioms:
            print(f"⚠️ Axiom '{axiom.title}' has high behavioral loss ({loss:.2f})")
            print("   Consider: (1) Revise axiom, (2) Add contradiction edge, (3) Change behavior")

    # Return axioms with validated loss
    return [ax for ax, _ in axioms_with_behavioral_loss]
```

---

## Part V: OptimalSubstructure as Sheaf Coherence

### 5.1 The Bellman-Sheaf Correspondence

**Theorem 5.1.1 (Bellman IS Sheaf Gluing)**.
The DP optimal substructure property:
```
V*(s) = R(s, π*(s)) + γ · V*(T(s, π*(s)))
```

is IDENTICAL to the sheaf gluing condition:
```
Local proofs on overlaps glue to global proof.
```

**Proof Sketch**:
1. DP optimal substructure: Optimal solution to (s → goal) decomposes into optimal (s → s') and optimal (s' → goal)
2. Sheaf gluing: Local sections that agree on overlaps extend to global section
3. The "overlap" IS the intermediate state s'
4. "Agree" means V*(s') is the same whether computed from s or from goal
5. Therefore: DP substructure = Sheaf coherence □

### 5.2 Galois Loss Bounds Propagate

**Theorem 5.2.1 (Loss Bound Propagation)**.
If local proofs have bounded Galois loss, the global proof has bounded total loss:

```
L_total ≤ Σᵢ L_local(edge_i)
```

**Proof**:
1. Each edge transition has Galois loss L_i
2. Composing edges concatenates losses (worst case: sum)
3. Sheaf gluing preserves structure → actual loss ≤ sum
4. With coherent gluing, losses may CANCEL (best case: max, not sum) □

### 5.3 Implementation

```python
from agents.dp.sheaf import OptimalSubstructure

@dataclass
class ZeroSeedOptimalSubstructure(OptimalSubstructure[NodeId]):
    """
    Verify that Zero Seed proofs compose correctly with loss bounds.

    Each edge has Galois loss; gluing must bound total loss.
    """

    galois: GaloisLoss

    async def verify_path(
        self,
        path: list[ZeroEdge]
    ) -> tuple[bool, float]:
        """
        Verify optimal substructure along path.

        Returns: (is_optimal, total_loss)
        """
        if len(path) < 2:
            return True, 0.0

        # Compute local losses
        local_losses = []
        for edge in path:
            source = get_node(edge.source)
            target = get_node(edge.target)
            loss = await self._compute_edge_loss(source, edge.kind, target)
            local_losses.append(loss)

        # Verify gluing coherence
        for i in range(len(path) - 1):
            edge1, edge2 = path[i], path[i+1]
            if edge1.target != edge2.source:
                # Edges don't connect → not a valid path
                return False, float('inf')

            # Check if solutions agree on overlap (the shared node)
            overlap_node = get_node(edge1.target)
            agree = await self._check_overlap_agreement(edge1, edge2, overlap_node)
            if not agree:
                return False, float('inf')

        # Total loss (sum of locals, but coherent gluing may reduce)
        total_loss = sum(local_losses)

        # Check for coherence bonus (losses cancel)
        coherence_factor = await self._compute_coherence_factor(path)
        total_loss *= coherence_factor  # 0.5-1.0 (coherence reduces loss)

        return True, total_loss

    async def _compute_edge_loss(
        self,
        source: ZeroNode,
        action: str,
        target: ZeroNode
    ) -> float:
        """Galois loss for a single edge."""
        transition = f"""
From: {source.title}
Via: {action}
To: {target.title}
"""
        return await self.galois.compute(transition)

    async def _check_overlap_agreement(
        self,
        edge1: ZeroEdge,
        edge2: ZeroEdge,
        overlap: ZeroNode
    ) -> bool:
        """
        Check if edge solutions agree on overlap node.

        Agreement = value at overlap is consistent from both directions.
        """
        # Compute value from edge1's perspective
        value_from_1 = await self._compute_value_at_node(overlap, via_edge=edge1)

        # Compute value from edge2's perspective
        value_from_2 = await self._compute_value_at_node(overlap, via_edge=edge2)

        # Agree if values are close (within ε)
        epsilon = 0.1
        return abs(value_from_1 - value_from_2) < epsilon

    async def _compute_coherence_factor(self, path: list[ZeroEdge]) -> float:
        """
        Coherent paths have losses that partially cancel.

        Coherence factor ∈ [0.5, 1.0]:
        - 0.5 = maximally coherent (losses cancel significantly)
        - 1.0 = incoherent (losses add directly)
        """
        # Heuristic: paths with same-layer edges are more coherent
        same_layer_count = sum(
            1 for e in path
            if get_node(e.source).layer == get_node(e.target).layer
        )

        coherence = 1.0 - (same_layer_count / len(path)) * 0.5
        return coherence
```

---

## Part VI: Loss Gradient Flow Through Layers

### 6.1 The Seven-Layer Loss Landscape

The Zero Seed's 7 epistemic layers form a loss landscape:

```
L1 (Assumptions)   →  Base loss (axioms have loss = 0 by definition)
    ↓ L_grounds
L2 (Values)        →  Loss accumulates from grounding
    ↓ L_justifies
L3 (Goals)         →  Loss accumulates from justification
    ↓ L_specifies
L4 (Specifications)→  Loss accumulates from specification
    ↓ L_implements
L5 (Execution)     →  Loss accumulates from implementation
    ↓ L_reflects
L6 (Reflection)    →  Loss accumulates from reflection
    ↓ L_represents
L7 (Representation)→  Total loss = Σ layer losses
```

### 6.2 Total Loss as Path Integral

**Theorem 6.2.1 (Total Loss is Path Integral)**.
The total Galois loss through the holarchy is:

```
L_total = ∫_path dL
        = Σᵢ L(layer_i → layer_{i+1})
```

where the integral is over the path from axioms (L1) to representations (L7).

### 6.3 Galois Adjunction as Loss Bound

**Theorem 6.3.1 (Constitution Bounds Total Loss)**.
The Constitution (as Galois adjunction) provides a BOUND on total loss:

```
L_total ≤ Σᵢ (1 - R_constitutional(layer_i, edge_i, layer_{i+1}))
```

**Proof**:
1. Constitutional reward R = 1 - L (by definition)
2. Therefore: L = 1 - R
3. Total loss = Σ(1 - R_i) = n - Σ R_i
4. Constitution enforces R_i ≥ R_min (minimum acceptable reward)
5. Therefore: L_total ≤ n - (n · R_min) = n(1 - R_min) □

### 6.4 Implementation: Loss Flow Visualization

```python
@dataclass
class LossGradientFlow:
    """
    Visualize loss flow through the 7-layer holarchy.

    Enables debugging: where is loss accumulating?
    """

    galois: GaloisLoss

    async def compute_flow(
        self,
        path: list[ZeroEdge]
    ) -> dict[int, float]:
        """
        Compute loss gradient at each layer.

        Returns: {layer_num: accumulated_loss}
        """
        layer_losses = {i: 0.0 for i in range(1, 8)}

        for edge in path:
            source = get_node(edge.source)
            target = get_node(edge.target)

            # Compute edge loss
            loss = await self.galois.compute(
                f"{source.title} → {target.title} via {edge.kind}"
            )

            # Accumulate at target layer
            layer_losses[target.layer] += loss

        return layer_losses

    def visualize_flow(self, layer_losses: dict[int, float]) -> str:
        """
        ASCII visualization of loss flow.

        Example:
        L1: ███░░░░░░░ 0.05
        L2: ████░░░░░░ 0.10
        L3: ██████░░░░ 0.15
        L4: ████████░░ 0.25  ← High loss here!
        L5: █████████░ 0.30
        L6: ██████████ 0.35
        L7: ██████████ 0.40
        """
        max_loss = max(layer_losses.values()) if layer_losses else 1.0

        lines = []
        for layer in range(1, 8):
            loss = layer_losses.get(layer, 0.0)
            bar_length = int((loss / max_loss) * 10)
            bar = "█" * bar_length + "░" * (10 - bar_length)

            annotation = ""
            if loss > 0.3:
                annotation = "  ← High loss!"

            lines.append(f"L{layer}: {bar} {loss:.2f}{annotation}")

        return "\n".join(lines)

    async def diagnose_high_loss(
        self,
        layer_losses: dict[int, float]
    ) -> list[str]:
        """
        Diagnose which principles are violated at high-loss layers.
        """
        diagnoses = []

        for layer, loss in layer_losses.items():
            if loss > 0.3:  # High loss threshold
                # Identify which principle is most violated
                diagnoses.append(
                    f"Layer {layer} has high loss ({loss:.2f}). "
                    f"Likely violations: {await self._identify_violations(layer, loss)}"
                )

        return diagnoses

    async def _identify_violations(self, layer: int, loss: float) -> str:
        """Heuristic: which principles correlate with layer + loss."""
        # Example heuristics (could be learned from data)
        if layer <= 2 and loss > 0.3:
            return "CURATED (axioms arbitrary?)"
        elif layer == 3 and loss > 0.3:
            return "GENERATIVE (goals not derived from values?)"
        elif layer == 4 and loss > 0.3:
            return "COMPOSABLE (specs tightly coupled?)"
        elif layer == 5 and loss > 0.3:
            return "ETHICAL (implementation has hidden risks?)"
        elif layer == 6 and loss > 0.3:
            return "TASTEFUL (reflection is bloated?)"
        elif layer == 7 and loss > 0.3:
            return "JOY_INDUCING (representation lacks aesthetic coherence?)"
        else:
            return "Unknown violation"
```

### 6.5 Example: Loss Flow Analysis

```python
# Construct a path through layers
path = [
    ZeroEdge(axiom1, value1, kind="GROUNDS"),        # L1 → L2
    ZeroEdge(value1, goal1, kind="JUSTIFIES"),       # L2 → L3
    ZeroEdge(goal1, spec1, kind="SPECIFIES"),        # L3 → L4
    ZeroEdge(spec1, action1, kind="IMPLEMENTS"),     # L4 → L5
    ZeroEdge(action1, reflection1, kind="REFLECTS_ON"),  # L5 → L6
    ZeroEdge(reflection1, insight1, kind="REPRESENTS"),  # L6 → L7
]

# Compute loss flow
flow_analyzer = LossGradientFlow(galois_loss)
layer_losses = await flow_analyzer.compute_flow(path)

# Visualize
print(flow_analyzer.visualize_flow(layer_losses))
# Output:
# L1: ░░░░░░░░░░ 0.00
# L2: ██░░░░░░░░ 0.05
# L3: ████░░░░░░ 0.10
# L4: ████████░░ 0.25  ← High loss here!
# L5: █████████░ 0.30
# L6: ██████████ 0.35
# L7: ██████████ 0.40

# Diagnose
diagnoses = await flow_analyzer.diagnose_high_loss(layer_losses)
for d in diagnoses:
    print(f"⚠️ {d}")
# Output:
# ⚠️ Layer 4 has high loss (0.25). Likely violations: COMPOSABLE (specs tightly coupled?)
```

---

## Part VII: Integration with Existing Systems

### 7.1 Backward Compatibility

The Galois upgrade is **additive**, not disruptive:

```python
# OLD: Hand-crafted evaluators still work
constitution_old = ZeroSeedConstitution()
reward_old = constitution_old.reward(state, action, next_state)

# NEW: Galois-enhanced evaluators
constitution_new = GaloisConstitution(galois=GaloisLoss(llm))
reward_new = constitution_new.reward(state, action, next_state)

# HYBRID: Gradual migration (λ controls blend)
constitution_hybrid = GaloisConstitution(galois=GaloisLoss(llm), loss_weight=0.5)
reward_hybrid = constitution_hybrid.reward(state, action, next_state)
# reward_hybrid = 0.5 * reward_old + 0.5 * (1 - galois_loss)
```

### 7.2 Integration Points

| System | Integration | File |
|--------|-------------|------|
| **ValueAgent** | Uses `GaloisConstitution` as reward function | `dp/core/value_agent.py` |
| **PolicyTrace** | Stores Galois loss in metadata | `dp/core/policy_trace.py` |
| **Witness Mark** | Implements `to_trace_entry()` with loss | `services/witness/mark.py` |
| **Axiom Discovery** | Uses `AxiomMiningDP` | `services/zero_seed/discovery.py` |
| **Telescope UI** | Shows loss flow visualization | `web/src/components/LossFlowViz.tsx` |

### 7.3 Migration Path

| Phase | Week | Deliverable |
|-------|------|-------------|
| **Phase 1** | 1-2 | Implement `GaloisLoss` core with 7 principle-specific losses |
| **Phase 2** | 3-4 | Add `GaloisConstitution` with λ=0.2 (20% Galois, 80% traditional) |
| **Phase 3** | 5-6 | Integrate with `PolicyTrace` and `Mark` |
| **Phase 4** | 7-8 | Implement `AxiomMiningDP` and test on real constitution |
| **Phase 5** | 9-10 | Add `LossGradientFlow` visualization |
| **Phase 6** | 11-12 | Increase λ to 0.5, then 0.8, validate with Mirror Test |

---

## Part VIII: Experimental Validation

### 8.1 Hypothesis

**H1 (Loss-Reward Duality)**: Constitutional reward ≈ 1 - Galois loss
**H2 (Loss Prediction)**: Galois loss predicts Mirror Test rejection rate
**H3 (Loss Composition)**: Path loss ≤ Σ edge losses (sheaf coherence)

### 8.2 Experiment 1: Loss-Reward Correlation

```python
async def validate_loss_reward_duality(test_cases: list[TestCase]) -> float:
    """
    Test H1: R_constitutional ≈ 1 - L_galois

    Returns: Pearson correlation coefficient (expect r > 0.8)
    """
    results = []

    for case in test_cases:
        # Compute traditional constitutional reward
        r_trad = traditional_constitution.reward(case.state, case.action, case.next_state)

        # Compute Galois loss
        loss = await galois_loss.compute(case.transition_desc)

        # Predicted reward from loss
        r_galois = 1.0 - loss

        results.append((r_trad, r_galois))

    # Correlation
    r_trad_vals = [r for r, _ in results]
    r_galois_vals = [r for _, r in results]
    correlation = pearsonr(r_trad_vals, r_galois_vals)

    return correlation.statistic
```

### 8.3 Experiment 2: Mirror Test Prediction

```python
async def validate_mirror_test_prediction(
    axiom_candidates: list[CandidateAxiom],
    human_responses: list[str],
) -> dict[str, float]:
    """
    Test H2: Galois loss predicts human rejection.

    Returns: Precision, Recall, F1 for predicting "No" responses.
    """
    predictions = []
    actuals = []

    for candidate, response in zip(axiom_candidates, human_responses):
        # Compute Galois loss
        loss = await galois_loss.compute(candidate.text)

        # Predict: high loss → reject
        predicted_reject = loss > 0.5
        actual_reject = response == "No"

        predictions.append(predicted_reject)
        actuals.append(actual_reject)

    # Metrics
    tp = sum(p and a for p, a in zip(predictions, actuals))
    fp = sum(p and not a for p, a in zip(predictions, actuals))
    fn = sum(not p and a for p, a in zip(predictions, actuals))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {"precision": precision, "recall": recall, "f1": f1}
```

### 8.4 Experiment 3: Sheaf Coherence

```python
async def validate_sheaf_coherence(
    paths: list[list[ZeroEdge]]
) -> tuple[float, float]:
    """
    Test H3: Total loss ≤ Σ edge losses (coherence bonus).

    Returns: (avg_ratio, coherence_bonus)
    where ratio = total_loss / sum_of_edge_losses
    and coherence_bonus = 1 - avg_ratio
    """
    ratios = []

    for path in paths:
        # Compute edge losses
        edge_losses = []
        for edge in path:
            source = get_node(edge.source)
            target = get_node(edge.target)
            loss = await galois_loss.compute(f"{source.title} → {target.title}")
            edge_losses.append(loss)

        sum_edge_losses = sum(edge_losses)

        # Compute total loss for path
        path_desc = " → ".join(get_node(e.source).title for e in path)
        total_loss = await galois_loss.compute(path_desc)

        # Ratio (expect < 1.0 if coherence helps)
        ratio = total_loss / sum_edge_losses if sum_edge_losses > 0 else 1.0
        ratios.append(ratio)

    avg_ratio = sum(ratios) / len(ratios)
    coherence_bonus = 1.0 - avg_ratio

    return avg_ratio, coherence_bonus
```

---

## Part IX: Conclusion and Next Steps

### 9.1 Summary of Contributions

This specification unifies Zero Seed's constitutional evaluation via Galois Modularization Theory:

1. **Single Reward Function**: 7 evaluators → 1 Galois loss measure
2. **Proof-Trace Isomorphism**: Toulmin ↔ PolicyTrace with loss annotations
3. **Axiom Discovery MetaDP**: Loss minimization replaces heuristic mining
4. **Sheaf-DP Correspondence**: Optimal substructure = Gluing with loss bounds
5. **Loss Gradient Flow**: Visualize layer-by-layer loss accumulation

### 9.2 Theoretical Advances

| Advance | Impact |
|---------|--------|
| **Constitutional Reward = Inverse Loss** | Removes arbitrary thresholds, grounds evaluation in information theory |
| **Galois Adjunction IS Constitution** | Constitution becomes a mathematical structure (Galois connection), not heuristics |
| **Loss Bounds via Sheaf Coherence** | Provably limits total loss, enables correctness guarantees |
| **Mirror Test as Loss Oracle** | Human judgment provides ground truth for training loss predictors |

### 9.3 Implementation Priorities

| Priority | Task | Weeks |
|----------|------|-------|
| **HIGH** | Implement `GaloisLoss` core with 7 principle-specific losses | 1-2 |
| **HIGH** | Add `GaloisConstitution` with hybrid reward (λ parameter) | 3-4 |
| **MEDIUM** | Implement `proof_to_trace()` with loss annotations | 5-6 |
| **MEDIUM** | Implement `AxiomMiningDP` for Stage 1 discovery | 7-8 |
| **LOW** | Add `LossGradientFlow` visualization | 9-10 |

### 9.4 Open Questions

| Question | Approach |
|----------|----------|
| **Q1**: What's the optimal loss metric? | Experiment with cosine, BERTScore, LLM-judge (see Galois §10.4) |
| **Q2**: Can Galois loss be learned end-to-end? | Train neural predictor on Mirror Test data |
| **Q3**: Does coherence bonus generalize across domains? | Test on Brain, Witness, Soul formulations |
| **Q4**: What's the relationship to Kolmogorov complexity? | Theoretical analysis (Galois loss ≈ compressibility) |

### 9.5 Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| **Loss-Reward Correlation** | r > 0.7 (strong correlation) |
| **Mirror Test Prediction** | F1 > 0.6 (useful prediction) |
| **Sheaf Coherence** | Coherence bonus > 0.2 (losses partially cancel) |
| **Developer Experience** | Kent's Mirror Test: "Tasteful and rigorous" |

---

## Appendix A: Complete Example

### A.1 Scenario: Creating a New Goal Node

```python
# User wants to add a goal: "Build DP-native Zero Seed UI"

# 1. Construct the transition
state = axiom_generative  # L1: "Spec is compression"
action = "GROUNDS → JUSTIFIES → SPECIFIES"
next_state = goal_build_ui  # L3: "Build DP-native Zero Seed UI"

# 2. Compute Galois loss
transition_desc = f"""
From: L1 Axiom "Generative Principle"
Content: Spec is compression; design should generate implementation.

Via: grounds → justifies → specifies

To: L3 Goal "Build DP-native Zero Seed UI"
Content: Create a React UI that visualizes value functions, loss gradients, and policy traces for the Zero Seed system.
"""

galois_loss = await galois.compute(transition_desc)
# Result: 0.18 (low loss → good structural coherence)

# 3. Compute constitutional reward
constitution = GaloisConstitution(galois)
reward = constitution.reward(state, action, next_state)
# Result: 1.0 - 0.18 = 0.82 (high reward)

# 4. Principle breakdown
scores = constitution.evaluate(state, action, next_state)
# Result:
# TASTEFUL: 0.85 (UI goal is clear, not bloated)
# COMPOSABLE: 0.90 (UI can be modular React components)
# GENERATIVE: 0.75 (derives from generative axiom, but UI is concrete)
# ETHICAL: 1.00 (no safety concerns)
# JOY_INDUCING: 0.80 (visualization is delightful)
# HETERARCHICAL: 0.85 (UI doesn't impose rigid structure)
# CURATED: 0.90 (intentional design choice, well-justified)

# 5. Create PolicyTrace with loss
proof = Proof(
    data="DP-Native work is complete (§14 in zero-seed.md)",
    warrant="Visualization enables developer understanding",
    claim="UI is the next logical step",
    backing="Constitutional principles favor transparency (ETHICAL) and joy (JOY_INDUCING)",
    qualifier="probably",
    tier=EvidenceTier.CATEGORICAL,
    principles=("GENERATIVE", "JOY_INDUCING"),
)

trace = proof_to_trace(proof, galois_loss=0.18)

# 6. Witness the decision
mark = Mark(
    origin="zero-seed.dp",
    stimulus=Stimulus(kind="node_creation", content=transition_desc),
    response=Response(kind="goal_created", target_node=goal_build_ui.id),
    timestamp=datetime.now(UTC),
    proof=proof,
    tags=frozenset({"zero-seed", "dp", "ui", "galois-validated"}),
)

await witness_store.save_mark(mark)

# 7. Result
# ✓ Goal created with high constitutional reward (0.82)
# ✓ Low Galois loss (0.18) confirms structural coherence
# ✓ PolicyTrace annotated with loss for explainability
# ✓ Fully witnessed with Toulmin proof
```

---

## Appendix B: Cross-References

- `spec/protocols/zero-seed.md` — Original Zero Seed specification (7-layer holarchy, axiom discovery, telescope UI)
- `spec/theory/dp-native-kgents.md` — DP-Agent isomorphism, ValueAgent, PolicyTrace, Constitution as reward
- `spec/theory/galois-modularization.md` — Galois loss theory, restructure-reconstitute adjunction, loss-complexity correlation
- `spec/principles/CONSTITUTION.md` — The 7 design principles (TASTEFUL, CURATED, ETHICAL, JOY_INDUCING, COMPOSABLE, HETERARCHICAL, GENERATIVE)
- `impl/claude/services/categorical/galois_loss.py` — Implementation of Galois loss computation
- `impl/claude/services/categorical/constitution.py` — Constitution class with principle evaluators
- `impl/claude/dp/core/value_agent.py` — ValueAgent with constitutional reward
- `impl/claude/dp/core/policy_trace.py` — PolicyTrace monad with Writer + State semantics

---

*"The reward IS the inverse loss. The value IS the structure preserved. The Constitution IS the Galois adjunction."*

---

**Filed**: 2025-12-24
**Status**: Ready for Implementation
**Next Actions**:
1. Implement `GaloisLoss` with 7 principle-specific loss functions
2. Create `GaloisConstitution` extending `Constitution`
3. Add `proof_to_trace()` and `trace_to_proof()` with loss annotations
4. Implement `AxiomMiningDP` for Stage 1 discovery
5. Validate with Experiments 1-3 (correlation, prediction, coherence)
6. Gradual rollout: λ=0.2 → 0.5 → 0.8 (Galois weight)
7. Mirror Test with Kent on revised spec and implementation
