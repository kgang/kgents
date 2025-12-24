# Zero Seed: Galois-Upgraded Proof System

> *"The coherence IS the inverse loss. The witness IS the mark. The contradiction IS the super-additive signal."*

**Module**: Proof (Galois-Upgraded)
**Depends on**: [`core.md`](../zero-seed/core.md), [`galois-modularization.md`](../../theory/galois-modularization.md), [`witness-primitives.md`](../witness-primitives.md)
**Version**: 2.0 (Galois Integration)
**Status**: Theoretical — Ready for Implementation

---

## Abstract

The original Zero Seed used Toulmin proofs without quantitative coherence measures. The Galois upgrade provides:

**proof_quality(proof) = 1 - galois_loss(proof)**

This grounds Toulmin argumentation in information theory, enabling:
1. **Quantitative coherence scoring** (not just structural validation)
2. **Loss-decomposition diagnostics** (identify weak warrant, backing, etc.)
3. **Ghost alternative generation** (rebuttals from loss sources)
4. **Witness batching via Galois triage** (batch low-loss proofs, prioritize high-loss)
5. **Paraconsistent contradictions** (super-additive loss detection)
6. **Evidence tier mapping** (loss bounds define categorical/empirical/aesthetic/somatic)

---

## Part I: Toulmin Structure Extended with Galois Loss

### 1.1 Original Toulmin Proof

From Zero Seed `core.md`:

```python
@dataclass(frozen=True)
class Proof:
    """Toulmin proof structure. Required for L3+ nodes by M."""

    data: str                           # Evidence
    warrant: str                        # Reasoning
    claim: str                          # Conclusion
    backing: str                        # Support for warrant
    qualifier: str                      # Confidence ("definitely", "probably")
    rebuttals: tuple[str, ...]          # Defeaters
    tier: EvidenceTier                  # CATEGORICAL, EMPIRICAL, AESTHETIC, SOMATIC
    principles: tuple[str, ...]         # Referenced Constitution principles
```

### 1.2 Galois-Witnessed Proof Extension

```python
@dataclass(frozen=True)
class GaloisWitnessedProof(Proof):
    """
    Toulmin proof extended with Galois loss quantification.

    The Galois loss measures how much coherence is lost when the proof
    is modularized and reconstituted. Low loss = tight, necessary structure.
    High loss = implicit dependencies not captured in explicit structure.
    """

    # Galois metrics
    galois_loss: float                          # L(proof) ∈ [0, 1]
    loss_decomposition: dict[str, float]        # Loss per component

    # Ghost alternatives (Différance)
    ghost_alternatives: tuple[Alternative, ...]  # Deferred proofs

    # Coherence metrics (derived)
    @property
    def coherence(self) -> float:
        """Coherence = 1 - loss. Core insight of Galois upgrade."""
        return 1.0 - self.galois_loss

    @property
    def tier_from_loss(self) -> EvidenceTier:
        """Map loss to evidence tier (see §4)."""
        return classify_by_loss(self.galois_loss)

    @property
    def rebuttals_from_loss(self) -> tuple[str, ...]:
        """
        Generate rebuttals from loss decomposition.

        High loss in specific components indicates potential defeaters.
        Example: High warrant_loss → "Unless warrant's implicit assumption X fails"
        """
        generated = []
        for component, loss in self.loss_decomposition.items():
            if loss > 0.3:  # Significant loss
                generated.append(
                    f"Unless implicit assumption in {component} fails (loss: {loss:.2f})"
                )
        return tuple(generated)

    @property
    def witness_mode(self) -> WitnessMode:
        """
        Triage witness mode based on loss (see §3).

        Low loss → important, witness immediately
        Medium loss → batch with session
        High loss → lazy, might be discarded
        """
        return select_witness_mode_from_loss(self.galois_loss)


@dataclass(frozen=True)
class Alternative:
    """A ghost alternative proof (deferred, not chosen)."""

    description: str                    # What this alternative would have been
    galois_loss: float                  # Loss if this had been chosen
    deferral_cost: float                # Cost of deferring (vs chosen)
    rationale: str                      # Why it was deferred
```

### 1.3 Loss Decomposition Structure

```python
@dataclass(frozen=True)
class ProofLossDecomposition:
    """
    Galois loss broken down by Toulmin component.

    Each component contributes to total loss when proof is modularized.
    """

    data_loss: float                    # Loss in evidence statement
    warrant_loss: float                 # Loss in reasoning chain
    claim_loss: float                   # Loss in conclusion
    backing_loss: float                 # Loss in warrant support
    qualifier_loss: float               # Loss in confidence expression
    rebuttal_loss: float                # Loss in defeater enumeration
    composition_loss: float             # Loss in how components connect

    @property
    def total(self) -> float:
        """Total loss = sum of component losses."""
        return (
            self.data_loss +
            self.warrant_loss +
            self.claim_loss +
            self.backing_loss +
            self.qualifier_loss +
            self.rebuttal_loss +
            self.composition_loss
        )

    def normalized(self) -> "ProofLossDecomposition":
        """Normalize so total = 1.0 (shows relative contributions)."""
        total = self.total
        if total == 0:
            return self

        return ProofLossDecomposition(
            data_loss=self.data_loss / total,
            warrant_loss=self.warrant_loss / total,
            claim_loss=self.claim_loss / total,
            backing_loss=self.backing_loss / total,
            qualifier_loss=self.qualifier_loss / total,
            rebuttal_loss=self.rebuttal_loss / total,
            composition_loss=self.composition_loss / total,
        )

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary for GaloisWitnessedProof.loss_decomposition."""
        return {
            "data": self.data_loss,
            "warrant": self.warrant_loss,
            "claim": self.claim_loss,
            "backing": self.backing_loss,
            "qualifier": self.qualifier_loss,
            "rebuttals": self.rebuttal_loss,
            "composition": self.composition_loss,
        }
```

---

## Part II: Galois Loss Computation for Proofs

### 2.1 The Core Algorithm

```python
async def galois_loss(proof: Proof, llm: LLM) -> float:
    """
    Compute Galois loss L(proof) = d(proof, C(R(proof))).

    Process:
    1. Serialize proof to natural language
    2. Restructure into modular form (R)
    3. Reconstitute back to natural language (C)
    4. Measure semantic distance d(original, reconstituted)

    Returns:
        Loss in [0, 1] where 0 = perfect coherence, 1 = total loss
    """
    # Serialize proof
    original_text = serialize_proof(proof)

    # R: Restructure into modules
    modular = await restructure_proof(original_text, llm)

    # C: Reconstitute to flat text
    reconstituted_text = await reconstitute_proof(modular, llm)

    # Compute semantic distance
    loss = await semantic_distance(original_text, reconstituted_text)

    return loss


def serialize_proof(proof: Proof) -> str:
    """
    Convert Toulmin proof to natural language.

    Format designed to be modularizable:
    - Each component on separate line
    - Clear labels
    - Composition structure implicit
    """
    return f"""
PROOF STRUCTURE:

Data (Evidence):
{proof.data}

Warrant (Reasoning):
{proof.warrant}

Claim (Conclusion):
{proof.claim}

Backing (Warrant Support):
{proof.backing}

Qualifier:
{proof.qualifier}

Rebuttals (Defeaters):
{', '.join(proof.rebuttals)}

Evidence Tier:
{proof.tier.value}

Principles:
{', '.join(proof.principles)}
""".strip()


async def restructure_proof(proof_text: str, llm: LLM) -> ModularProof:
    """
    R: Proof → ModularProof

    LLM decomposes proof into independent modules with explicit interfaces.
    """
    prompt = f"""Decompose this Toulmin proof into independent, composable modules.

{proof_text}

For each module, provide:
1. Module name
2. Inputs (what it depends on)
3. Outputs (what it produces)
4. Content (the text)

Format as JSON with this schema:
{{
    "modules": [
        {{"name": "...", "inputs": [...], "outputs": [...], "content": "..."}},
        ...
    ],
    "composition": "description of how modules compose"
}}
"""

    response = await llm.generate(
        system="You are a proof engineer decomposing arguments into modular form.",
        user=prompt,
        temperature=0.2,  # Low temperature for structural task
    )

    return ModularProof.parse(response.text)


async def reconstitute_proof(modular: ModularProof, llm: LLM) -> str:
    """
    C: ModularProof → Proof

    LLM flattens modules back into coherent natural language.
    """
    prompt = f"""Flatten this modular proof into a single coherent Toulmin structure.

Modules:
{json.dumps(modular.modules, indent=2)}

Composition:
{modular.composition}

Generate a natural language proof in Toulmin format (Data, Warrant, Claim, Backing, Qualifier, Rebuttals).
"""

    response = await llm.generate(
        system="You are a proof engineer reconstituting modular arguments.",
        user=prompt,
        temperature=0.2,
    )

    return response.text.strip()


async def semantic_distance(text_a: str, text_b: str, method: str = "bertscore") -> float:
    """
    Measure semantic distance between two texts.

    Methods:
    - "bertscore": BERTScore inverse (fast, accurate)
    - "llm_judge": LLM-based similarity (slow, nuanced)
    - "cosine": Embedding cosine distance (fast, coarse)

    Returns:
        Distance in [0, 1] where 0 = identical, 1 = completely different
    """
    match method:
        case "bertscore":
            from bert_score import score
            P, R, F1 = score([text_a], [text_b], lang="en", verbose=False)
            return 1.0 - F1.item()

        case "llm_judge":
            # Expensive but captures nuance
            llm = get_llm()
            response = await llm.generate(
                system="Rate semantic similarity from 0.0 (identical) to 1.0 (different).",
                user=f"Text A: {text_a}\n\nText B: {text_b}\n\nSimilarity:",
                temperature=0.0,
            )
            return float(response.text.strip())

        case "cosine":
            from openai import OpenAI
            client = OpenAI()
            emb_a = client.embeddings.create(input=text_a, model="text-embedding-3-small").data[0].embedding
            emb_b = client.embeddings.create(input=text_b, model="text-embedding-3-small").data[0].embedding

            import numpy as np
            cos_sim = np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b))
            return 1.0 - cos_sim

        case _:
            raise ValueError(f"Unknown method: {method}")


@dataclass
class ModularProof:
    """Modular representation of a proof (R(proof))."""

    modules: list[ProofModule]
    composition: str                    # How modules compose

    @classmethod
    def parse(cls, json_text: str) -> "ModularProof":
        """Parse from LLM JSON response."""
        import json
        data = json.loads(json_text)
        return cls(
            modules=[ProofModule(**m) for m in data["modules"]],
            composition=data["composition"],
        )


@dataclass
class ProofModule:
    """A single module in modular proof."""

    name: str
    inputs: list[str]
    outputs: list[str]
    content: str
```

### 2.2 Loss Decomposition Algorithm

```python
async def compute_loss_decomposition(proof: Proof, llm: LLM) -> ProofLossDecomposition:
    """
    Compute loss per Toulmin component.

    Process:
    1. Compute loss for full proof
    2. Compute loss with each component removed (ablation)
    3. Component loss = total_loss - ablated_loss

    This identifies which parts are most "compressed" (low loss = explicit)
    vs most "implicit" (high loss = hidden structure).
    """
    full_loss = await galois_loss(proof, llm)

    # Ablation studies
    component_losses = {}

    for component in ["data", "warrant", "claim", "backing", "qualifier", "rebuttals"]:
        ablated_proof = ablate_component(proof, component)
        ablated_loss = await galois_loss(ablated_proof, llm)

        # Loss contribution = how much loss increases without this component
        component_losses[component] = max(0.0, full_loss - ablated_loss)

    # Composition loss = residual (loss not explained by components)
    explained_loss = sum(component_losses.values())
    composition_loss = max(0.0, full_loss - explained_loss)

    return ProofLossDecomposition(
        data_loss=component_losses["data"],
        warrant_loss=component_losses["warrant"],
        claim_loss=component_losses["claim"],
        backing_loss=component_losses["backing"],
        qualifier_loss=component_losses["qualifier"],
        rebuttal_loss=component_losses["rebuttals"],
        composition_loss=composition_loss,
    )


def ablate_component(proof: Proof, component: str) -> Proof:
    """Remove a component from proof (for ablation study)."""
    match component:
        case "data":
            return proof.replace(data="[ABLATED]")
        case "warrant":
            return proof.replace(warrant="[ABLATED]")
        case "claim":
            return proof.replace(claim="[ABLATED]")
        case "backing":
            return proof.replace(backing="[ABLATED]")
        case "qualifier":
            return proof.replace(qualifier="[ABLATED]")
        case "rebuttals":
            return proof.replace(rebuttals=())
        case _:
            return proof
```

---

## Part III: Witness Batching with Galois Triage

### 3.1 The Problem: Witness Explosion

From Zero Seed `core.md`:
> **Full Witnessing**: Every edit creates a Mark. No exceptions, no tiers, no opt-outs.

This is correct philosophically but **computationally expensive**:
- 1000 node edits = 1000 marks
- Each mark requires storage, indexing, potential LLM analysis

### 3.2 The Solution: Galois-Based Triage

```python
class WitnessMode(Enum):
    """
    Witness modes based on Galois loss triage.

    Core insight: Low-loss edits are "routine" (batch them).
    High-loss edits are "important" (witness immediately).
    """

    SINGLE = "single"       # Important: witness immediately
    SESSION = "session"     # Batch: witness at session end
    LAZY = "lazy"           # Deferred: witness only if referenced
    ARCHIVE = "archive"     # Background: witness to cold storage


async def select_witness_mode(edit: NodeDelta, llm: LLM) -> WitnessMode:
    """
    Triage witness mode based on edit's Galois loss.

    Process:
    1. Compute proof for edit (if L3+)
    2. Compute Galois loss of proof
    3. Classify by loss thresholds

    Thresholds (empirically determined):
    - L < 0.1: IMPORTANT → Single
    - L < 0.4: ROUTINE → Session batch
    - L ≥ 0.4: EPHEMERAL → Lazy or archive
    """
    # Extract or generate proof for edit
    if edit.node.layer <= 2:
        # Axioms: always single (no proof, inherently important)
        return WitnessMode.SINGLE

    if edit.proof is None:
        # Missing proof on L3+: flag as important (validation needed)
        return WitnessMode.SINGLE

    # Compute Galois loss
    loss = await galois_loss(edit.proof, llm)

    # Triage by loss
    if loss < 0.1:
        # Low loss = tight, necessary proof → important edit
        return WitnessMode.SINGLE
    elif loss < 0.4:
        # Medium loss = routine change → batch
        return WitnessMode.SESSION
    else:
        # High loss = speculative/chaotic → lazy witness
        # (Might be discarded if never referenced)
        return WitnessMode.LAZY


async def witness_with_mode(
    node: ZeroNode,
    delta: NodeDelta,
    mode: WitnessMode,
    witness_store: WitnessStore,
) -> Mark | None:
    """
    Create witness mark according to triage mode.

    Returns:
        Mark if created immediately, None if batched/deferred
    """
    match mode:
        case WitnessMode.SINGLE:
            # Create mark immediately
            mark = create_witness_mark(node, delta)
            await witness_store.save_mark(mark)
            return mark

        case WitnessMode.SESSION:
            # Add to session batch
            await witness_store.batch_mark(node, delta)
            return None

        case WitnessMode.LAZY:
            # Create lazy reference (only materialize if accessed)
            await witness_store.create_lazy_mark(node, delta)
            return None

        case WitnessMode.ARCHIVE:
            # Background archival
            await witness_store.archive_mark(node, delta)
            return None


@dataclass
class WitnessStore:
    """Extended witness store with batching support."""

    # Standard storage
    marks: dict[MarkId, Mark]

    # Batching
    session_batch: list[tuple[ZeroNode, NodeDelta]]
    lazy_marks: dict[NodeId, NodeDelta]

    async def flush_session(self) -> list[Mark]:
        """
        Flush session batch to persistent storage.

        Creates a single "batch mark" summarizing all batched edits.
        """
        if not self.session_batch:
            return []

        # Create consolidated mark
        batch_mark = create_batch_mark(self.session_batch)
        await self.save_mark(batch_mark)

        # Clear batch
        self.session_batch.clear()

        return [batch_mark]

    async def materialize_lazy_mark(self, node_id: NodeId) -> Mark:
        """
        Materialize a lazy mark (when referenced).

        This is called when:
        - User navigates to the node
        - Node participates in query
        - Node is analyzed
        """
        if node_id not in self.lazy_marks:
            raise KeyError(f"No lazy mark for node {node_id}")

        delta = self.lazy_marks.pop(node_id)
        node = await self.get_node(node_id)

        mark = create_witness_mark(node, delta)
        await self.save_mark(mark)

        return mark


def create_batch_mark(edits: list[tuple[ZeroNode, NodeDelta]]) -> Mark:
    """
    Create a single mark summarizing a batch of edits.

    Contains:
    - Summary statistics (count, layers affected, etc.)
    - Representative samples (if batch large)
    - Aggregated loss metrics
    """
    return Mark(
        id=generate_mark_id(),
        origin="zero-seed.batch",
        stimulus=Stimulus(
            kind="batch_edit",
            metadata={
                "count": len(edits),
                "layers": list({n.layer for n, _ in edits}),
                "sample": [n.id for n, _ in edits[:5]],  # First 5
            },
        ),
        response=Response(
            kind="batch_completed",
            metadata={
                "total_edits": len(edits),
            },
        ),
        timestamp=datetime.now(UTC),
        tags=frozenset({"zero-seed", "batch", "session"}),
    )
```

### 3.3 Adaptive Batching

```python
@dataclass
class AdaptiveBatcher:
    """
    Adaptive batching strategy based on session characteristics.

    Learns optimal thresholds for witness triage.
    """

    # Current thresholds
    single_threshold: float = 0.1       # L < 0.1 → single
    session_threshold: float = 0.4      # L < 0.4 → session

    # Statistics
    single_count: int = 0
    session_count: int = 0
    lazy_count: int = 0

    # Learning
    reference_rate: dict[WitnessMode, float] = field(default_factory=dict)

    def adjust_thresholds(self) -> None:
        """
        Adjust thresholds based on reference rates.

        Intuition: If lazy marks are frequently referenced, threshold is too high.
        If single marks are rarely referenced, threshold is too low.
        """
        lazy_ref_rate = self.reference_rate.get(WitnessMode.LAZY, 0.0)
        single_ref_rate = self.reference_rate.get(WitnessMode.SINGLE, 0.0)

        # Lazy marks referenced often → lower lazy threshold
        if lazy_ref_rate > 0.5:
            self.session_threshold *= 0.9  # More aggressive single witnessing

        # Single marks rarely referenced → raise single threshold
        if single_ref_rate < 0.3:
            self.single_threshold *= 1.1  # More batching

        # Clamp to reasonable bounds
        self.single_threshold = np.clip(self.single_threshold, 0.05, 0.2)
        self.session_threshold = np.clip(self.session_threshold, 0.3, 0.6)

    def track_reference(self, mode: WitnessMode, was_referenced: bool) -> None:
        """Track whether a mark was referenced for learning."""
        if mode not in self.reference_rate:
            self.reference_rate[mode] = 0.0

        # Exponential moving average
        alpha = 0.1
        self.reference_rate[mode] = (
            alpha * (1.0 if was_referenced else 0.0) +
            (1 - alpha) * self.reference_rate[mode]
        )
```

---

## Part IV: Evidence Tiers Mapped to Loss Bounds

### 4.1 Tier Classification via Loss

```python
class EvidenceTier(Enum):
    """Evidence tiers from Zero Seed, now loss-grounded."""

    CATEGORICAL = "categorical"     # L < 0.1 (logical necessity)
    EMPIRICAL = "empirical"         # L < 0.3 (data-driven)
    AESTHETIC = "aesthetic"         # L < 0.5 (taste-based)
    SOMATIC = "somatic"             # L < 0.7 (gut feeling)
    CHAOTIC = "chaotic"             # L ≥ 0.7 (incoherent)


def classify_by_loss(loss: float) -> EvidenceTier:
    """
    Map Galois loss to evidence tier.

    Thresholds chosen to match epistemic strength:
    - CATEGORICAL: Near-lossless (proof is tight, necessary)
    - EMPIRICAL: Low loss (proof grounded in data)
    - AESTHETIC: Medium loss (proof appeals to values)
    - SOMATIC: High loss (proof is intuitive, not explicit)
    - CHAOTIC: Very high loss (proof doesn't cohere)
    """
    if loss < 0.1:
        return EvidenceTier.CATEGORICAL
    elif loss < 0.3:
        return EvidenceTier.EMPIRICAL
    elif loss < 0.5:
        return EvidenceTier.AESTHETIC
    elif loss < 0.7:
        return EvidenceTier.SOMATIC
    else:
        return EvidenceTier.CHAOTIC


@dataclass
class TierBounds:
    """Loss bounds for evidence tiers with rationale."""

    categorical_max: float = 0.1
    empirical_max: float = 0.3
    aesthetic_max: float = 0.5
    somatic_max: float = 0.7

    def get_tier(self, loss: float) -> EvidenceTier:
        """Get tier for given loss."""
        return classify_by_loss(loss)

    def get_rationale(self, tier: EvidenceTier) -> str:
        """Explain tier assignment."""
        match tier:
            case EvidenceTier.CATEGORICAL:
                return (
                    "Loss < 0.1: Proof structure is nearly lossless under modularization. "
                    "This indicates logical necessity—the proof's conclusions follow "
                    "rigorously from its premises with minimal implicit assumptions."
                )
            case EvidenceTier.EMPIRICAL:
                return (
                    "Loss < 0.3: Proof has low but non-zero loss. This suggests the "
                    "argument is grounded in empirical observations with some implicit "
                    "inductive steps. The structure is mostly explicit."
                )
            case EvidenceTier.AESTHETIC:
                return (
                    "Loss < 0.5: Moderate loss indicates the proof appeals to values, "
                    "taste, or design principles. Some connections are aesthetic rather "
                    "than logical. The argument is coherent but not rigorous."
                )
            case EvidenceTier.SOMATIC:
                return (
                    "Loss < 0.7: High loss suggests the proof relies on intuition, "
                    "gut feeling, or tacit knowledge. Much of the reasoning is implicit. "
                    "The conclusion may be true, but the path is not fully articulable."
                )
            case EvidenceTier.CHAOTIC:
                return (
                    "Loss ≥ 0.7: Very high loss indicates the proof doesn't cohere under "
                    "modularization. This may signal confusion, contradiction, or a task "
                    "that's genuinely too complex to modularize. Consider simplifying or "
                    "decomposing further."
                )
```

### 4.2 Validation: Proof Quality via Galois Loss

```python
async def validate_proof_galois(proof: Proof, llm: LLM) -> ProofValidation:
    """
    Validate Toulmin proof using Galois loss as quality metric.

    This is the KEY UPGRADE: quantitative coherence instead of just
    structural validation.

    Returns:
        ProofValidation with coherence score, tier, and issues
    """
    # Compute Galois loss
    loss = await galois_loss(proof, llm)
    coherence = 1.0 - loss

    # Classify tier
    tier = classify_by_loss(loss)

    # Compute loss decomposition for diagnostics
    decomp = await compute_loss_decomposition(proof, llm)

    # Identify issues from high-loss components
    issues = []

    if decomp.warrant_loss > 0.3:
        issues.append(
            f"Warrant has high implicit structure (loss: {decomp.warrant_loss:.2f}). "
            "Consider making reasoning more explicit."
        )

    if decomp.backing_loss > 0.3:
        issues.append(
            f"Backing is weak or implicit (loss: {decomp.backing_loss:.2f}). "
            "Add more support for the warrant."
        )

    if decomp.composition_loss > 0.2:
        issues.append(
            f"Components don't compose well (loss: {decomp.composition_loss:.2f}). "
            "The proof may have hidden dependencies between parts."
        )

    # Overall assessment
    if loss < 0.2:
        assessment = "Strong proof with tight, explicit structure."
    elif loss < 0.4:
        assessment = "Reasonable proof with some implicit steps."
    elif loss < 0.6:
        assessment = "Weak proof with significant implicit structure."
    else:
        assessment = "Poor proof. Doesn't survive modularization. Consider rewriting."

    return ProofValidation(
        coherence=coherence,
        tier=tier,
        issues=issues,
        assessment=assessment,
        loss_decomposition=decomp.to_dict(),
    )


@dataclass
class ProofValidation:
    """Result of Galois-based proof validation."""

    coherence: float                    # 1 - loss
    tier: EvidenceTier                  # Classified tier
    issues: list[str]                   # Diagnostic issues
    assessment: str                     # Overall assessment
    loss_decomposition: dict[str, float]  # Per-component losses

    @property
    def is_valid(self) -> bool:
        """Proof is valid if tier is not CHAOTIC."""
        return self.tier != EvidenceTier.CHAOTIC

    @property
    def needs_revision(self) -> bool:
        """Proof needs revision if coherence < 0.5."""
        return self.coherence < 0.5
```

---

## Part V: Paraconsistency via Super-Additive Loss

### 5.1 Contradiction as Super-Additive Signal

From Zero Seed `core.md`:
> **Contradiction Tolerance**: `contradicts` edges may coexist.

But when do contradictions exist? Original spec had no quantitative criterion.

**The Galois Upgrade**: Contradictions are detected via **super-additive loss**.

```python
async def detect_contradiction_galois(
    proof_a: Proof,
    proof_b: Proof,
    llm: LLM,
    tolerance: float = 0.1,
) -> bool:
    """
    Detect contradiction via super-additive Galois loss.

    Intuition: If two proofs are compatible, their combined loss should
    be at most the sum of individual losses (sub-additive or additive).

    If loss_combined > loss_a + loss_b + TOLERANCE, they contradict—
    their combination introduces additional incoherence.

    Args:
        proof_a: First proof
        proof_b: Second proof
        tolerance: Threshold for super-additivity (default 0.1)

    Returns:
        True if contradiction detected (super-additive loss)
    """
    # Individual losses
    loss_a = await galois_loss(proof_a, llm)
    loss_b = await galois_loss(proof_b, llm)

    # Combined proof
    combined = combine_proofs(proof_a, proof_b)
    loss_combined = await galois_loss(combined, llm)

    # Check super-additivity
    expected_loss = loss_a + loss_b
    super_additive = loss_combined > expected_loss + tolerance

    return super_additive


def combine_proofs(proof_a: Proof, proof_b: Proof) -> Proof:
    """
    Combine two proofs into a single proof.

    This is used to test coherence—if the combined proof has much higher
    loss than the sum of individual losses, they contradict.
    """
    return Proof(
        data=f"{proof_a.data}\n\nAND\n\n{proof_b.data}",
        warrant=f"From A: {proof_a.warrant}\n\nFrom B: {proof_b.warrant}",
        claim=f"A claims: {proof_a.claim}\n\nB claims: {proof_b.claim}",
        backing=f"{proof_a.backing}\n\n{proof_b.backing}",
        qualifier=f"A: {proof_a.qualifier}, B: {proof_b.qualifier}",
        rebuttals=proof_a.rebuttals + proof_b.rebuttals,
        tier=proof_a.tier,  # Arbitrary choice
        principles=tuple(set(proof_a.principles) | set(proof_b.principles)),
    )


@dataclass
class ContradictionAnalysis:
    """Analysis of potential contradiction between proofs."""

    loss_a: float
    loss_b: float
    loss_combined: float

    @property
    def expected_loss(self) -> float:
        """Expected combined loss (additive baseline)."""
        return self.loss_a + self.loss_b

    @property
    def super_additivity(self) -> float:
        """How much more loss than expected."""
        return self.loss_combined - self.expected_loss

    @property
    def contradicts(self, tolerance: float = 0.1) -> bool:
        """Do proofs contradict (super-additive beyond tolerance)?"""
        return self.super_additivity > tolerance

    def severity(self) -> str:
        """Assess contradiction severity."""
        if self.super_additivity < 0:
            return "COMPATIBLE (sub-additive, proofs reinforce each other)"
        elif self.super_additivity < 0.1:
            return "COMPATIBLE (additive, proofs are independent)"
        elif self.super_additivity < 0.3:
            return "TENSION (mild super-additivity, proofs create friction)"
        elif self.super_additivity < 0.6:
            return "CONTRADICTION (significant super-additivity, proofs clash)"
        else:
            return "STRONG CONTRADICTION (extreme super-additivity, proofs are incompatible)"
```

### 5.2 Quantitative Paraconsistency

```python
class ParaconsistentGraph:
    """
    Zero Seed graph with quantified contradictions.

    Contradictions are edges with super-additive loss metadata.
    """

    async def add_contradiction_edge(
        self,
        node_a: ZeroNode,
        node_b: ZeroNode,
        analysis: ContradictionAnalysis,
    ) -> ZeroEdge:
        """
        Add contradiction edge with quantified severity.

        The edge metadata includes:
        - Super-additivity score
        - Severity classification
        - Suggested resolution strategies
        """
        edge = ZeroEdge(
            id=generate_edge_id(),
            source=node_a.id,
            target=node_b.id,
            kind=EdgeKind.CONTRADICTS,
            context=f"Super-additive loss: {analysis.super_additivity:.3f}",
            confidence=min(1.0, analysis.super_additivity),  # Higher = more certain contradiction
            created_at=datetime.now(UTC),
            mark_id=create_contradiction_mark(node_a, node_b, analysis).id,
            metadata={
                "loss_a": analysis.loss_a,
                "loss_b": analysis.loss_b,
                "loss_combined": analysis.loss_combined,
                "super_additivity": analysis.super_additivity,
                "severity": analysis.severity(),
            },
        )

        await self.edges.add(edge)
        return edge

    def get_strongest_contradictions(self, limit: int = 10) -> list[ZeroEdge]:
        """
        Get strongest contradictions (highest super-additivity).

        These are the pairs most in need of dialectical resolution.
        """
        contradictions = [
            e for e in self.edges
            if e.kind == EdgeKind.CONTRADICTS
        ]

        # Sort by super-additivity
        sorted_contradictions = sorted(
            contradictions,
            key=lambda e: e.metadata.get("super_additivity", 0.0),
            reverse=True,
        )

        return sorted_contradictions[:limit]
```

---

## Part VI: Ghost Alternatives from Loss Sources

### 6.1 Generating Rebuttals from Loss

```python
async def generate_ghost_rebuttals(
    proof: Proof,
    decomp: ProofLossDecomposition,
    llm: LLM,
) -> tuple[str, ...]:
    """
    Generate rebuttals from high-loss components.

    Intuition: High loss in a component means there's implicit structure
    that's not captured. This implicit structure is a *vulnerability*—
    the proof assumes something not stated.

    Ghost rebuttals surface these implicit assumptions as defeaters.
    """
    rebuttals = list(proof.rebuttals)  # Start with existing

    # For each high-loss component, generate rebuttals
    for component, loss in decomp.to_dict().items():
        if loss > 0.25:  # Significant loss
            ghost = await generate_ghost_rebuttal_for_component(
                proof, component, loss, llm
            )
            if ghost:
                rebuttals.append(ghost)

    return tuple(rebuttals)


async def generate_ghost_rebuttal_for_component(
    proof: Proof,
    component: str,
    loss: float,
    llm: LLM,
) -> str | None:
    """
    Generate a ghost rebuttal for a high-loss component.

    Example: If warrant_loss is high, LLM generates:
    "Unless the implicit assumption in the warrant (that X implies Y) fails..."
    """
    component_text = getattr(proof, component, "")

    prompt = f"""This {component} has high implicit structure (Galois loss: {loss:.2f}).

{component.upper()}:
{component_text}

What implicit assumption or hidden dependency makes this {component} vulnerable?
Generate a rebuttal starting with "Unless..." that exposes this assumption.

Rebuttal:"""

    response = await llm.generate(
        system="You are analyzing argument structure for implicit assumptions.",
        user=prompt,
        temperature=0.4,  # Some creativity for finding hidden assumptions
        max_tokens=100,
    )

    rebuttal = response.text.strip()

    # Ensure it starts with "Unless"
    if not rebuttal.startswith("Unless"):
        rebuttal = f"Unless {rebuttal}"

    return rebuttal
```

### 6.2 Ghost Alternative Proofs

```python
async def generate_ghost_alternatives(
    proof: Proof,
    llm: LLM,
    max_alternatives: int = 3,
) -> tuple[Alternative, ...]:
    """
    Generate ghost alternative proofs that were deferred.

    These represent different ways the proof could have been structured.
    Each has its own Galois loss, enabling comparison.
    """
    alternatives = []

    prompt = f"""Given this proof, what are alternative ways to structure the argument?

ORIGINAL PROOF:
Data: {proof.data}
Warrant: {proof.warrant}
Claim: {proof.claim}

Generate {max_alternatives} alternative proof structures (different warrant or data).
For each, explain:
1. What changes
2. Why it was deferred (why original was chosen)

Format as JSON array."""

    response = await llm.generate(
        system="You are exploring alternative argument structures.",
        user=prompt,
        temperature=0.6,  # Higher temperature for diversity
    )

    import json
    alt_data = json.loads(response.text)

    for alt in alt_data:
        # Create alternative proof
        alt_proof = Proof(
            data=alt.get("data", proof.data),
            warrant=alt.get("warrant", proof.warrant),
            claim=proof.claim,  # Same claim
            backing=alt.get("backing", proof.backing),
            qualifier=proof.qualifier,
            rebuttals=proof.rebuttals,
            tier=proof.tier,
            principles=proof.principles,
        )

        # Compute loss for alternative
        alt_loss = await galois_loss(alt_proof, llm)

        # Deferral cost = how much better/worse than chosen
        deferral_cost = abs(alt_loss - await galois_loss(proof, llm))

        alternatives.append(Alternative(
            description=alt["description"],
            galois_loss=alt_loss,
            deferral_cost=deferral_cost,
            rationale=alt["rationale"],
        ))

    return tuple(alternatives)
```

---

## Part VII: Full Witnessing with Loss Annotations

### 7.1 Witness Mark with Galois Metadata

```python
async def create_galois_witnessed_mark(
    node: ZeroNode,
    delta: NodeDelta,
    proof: GaloisWitnessedProof,
) -> Mark:
    """
    Create witness mark with Galois loss metadata.

    The mark includes:
    - Standard witness fields (stimulus, response, umwelt)
    - Galois loss and decomposition
    - Witness mode (single/session/lazy)
    - Ghost alternatives
    """
    mark = Mark(
        id=generate_mark_id(),
        origin="zero-seed.galois",
        stimulus=Stimulus(
            kind="node_edit",
            source_node=node.id,
            delta=delta,
        ),
        response=Response(
            kind="node_updated",
            target_node=delta.new_node.id,
        ),
        umwelt=get_current_umwelt(),
        timestamp=datetime.now(UTC),
        proof=proof,  # Include full Galois-witnessed proof
        tags=frozenset({
            "zero-seed",
            "galois",
            f"layer:{node.layer}",
            f"tier:{proof.tier_from_loss.value}",
            f"mode:{proof.witness_mode.value}",
        }),
        metadata={
            "galois_loss": proof.galois_loss,
            "coherence": proof.coherence,
            "loss_decomposition": proof.loss_decomposition,
            "ghost_count": len(proof.ghost_alternatives),
        },
    )

    return mark


@dataclass
class GaloisWitnessReport:
    """Report on witness activity with Galois analytics."""

    total_marks: int
    by_mode: dict[WitnessMode, int]
    by_tier: dict[EvidenceTier, int]

    average_loss: float
    average_coherence: float

    high_loss_marks: list[Mark]         # L > 0.6 (needs attention)
    super_coherent_marks: list[Mark]    # L < 0.1 (exemplars)

    def summary(self) -> str:
        return f"""
GALOIS WITNESS REPORT
=====================

Total Marks: {self.total_marks}

By Witness Mode:
{self._format_distribution(self.by_mode)}

By Evidence Tier:
{self._format_distribution(self.by_tier)}

Coherence Metrics:
  Average Loss: {self.average_loss:.3f}
  Average Coherence: {self.average_coherence:.3f}

Attention Needed:
  High-loss marks (L > 0.6): {len(self.high_loss_marks)}

Exemplars:
  Super-coherent marks (L < 0.1): {len(self.super_coherent_marks)}
""".strip()

    def _format_distribution(self, dist: dict) -> str:
        lines = []
        for key, count in sorted(dist.items(), key=lambda x: -x[1]):
            pct = count / self.total_marks * 100 if self.total_marks > 0 else 0
            lines.append(f"  {key}: {count} ({pct:.1f}%)")
        return "\n".join(lines)
```

### 7.2 Crystallization with Galois Loss

```python
async def crystallize_with_galois(
    marks: list[Mark],
    llm: LLM,
    loss_threshold: float = 0.3,
) -> Crystal:
    """
    Crystallize marks into a crystal with Galois quality gate.

    Only crystallize if combined loss is below threshold—otherwise,
    the marks don't cohere into a meaningful pattern.

    Args:
        marks: Marks to crystallize
        llm: LLM for loss computation
        loss_threshold: Maximum acceptable loss for crystallization

    Returns:
        Crystal if loss acceptable, else raises CoherenceError
    """
    # Extract proofs from marks
    proofs = [m.proof for m in marks if m.proof is not None]

    if not proofs:
        # No proofs, can't compute loss
        raise ValueError("Cannot crystallize marks without proofs")

    # Combine proofs
    combined_proof = combine_multiple_proofs(proofs)

    # Compute loss
    loss = await galois_loss(combined_proof, llm)

    if loss > loss_threshold:
        raise CoherenceError(
            f"Marks don't cohere (loss: {loss:.3f} > threshold: {loss_threshold}). "
            "Cannot crystallize. Consider filtering marks or relaxing threshold."
        )

    # Create crystal
    crystal = Crystal(
        id=generate_crystal_id(),
        title=f"Crystal from {len(marks)} marks",
        content=synthesize_crystal_content(marks),
        source_marks=tuple(m.id for m in marks),
        created_at=datetime.now(UTC),
        metadata={
            "galois_loss": loss,
            "coherence": 1.0 - loss,
            "mark_count": len(marks),
        },
    )

    return crystal


def combine_multiple_proofs(proofs: list[Proof]) -> Proof:
    """Combine multiple proofs into single proof for loss computation."""
    # Simplified: concatenate components
    return Proof(
        data="\n\n".join(p.data for p in proofs),
        warrant="\n\n".join(p.warrant for p in proofs),
        claim="\n\n".join(p.claim for p in proofs),
        backing="\n\n".join(p.backing for p in proofs),
        qualifier=proofs[0].qualifier if proofs else "probably",
        rebuttals=tuple(r for p in proofs for r in p.rebuttals),
        tier=proofs[0].tier if proofs else EvidenceTier.EMPIRICAL,
        principles=tuple(set(pr for p in proofs for pr in p.principles)),
    )


class CoherenceError(Exception):
    """Raised when marks don't cohere for crystallization."""
    pass
```

---

## Part VIII: Integration with DP-Native

### 8.1 PolicyTrace ↔ Toulmin Proof Isomorphism

From Zero Seed main spec Part XIV:

```python
def proof_to_trace(proof: GaloisWitnessedProof) -> PolicyTrace[NodeId]:
    """
    Convert Galois-witnessed Toulmin proof to DP trace.

    Extended with Galois loss as negative reward signal.
    """
    entry = TraceEntry(
        state_before=proof.data,
        action=proof.warrant,
        state_after=proof.claim,
        value=proof.coherence,  # Coherence as value!
        rationale=proof.backing,
        metadata={
            "galois_loss": proof.galois_loss,
            "tier": proof.tier_from_loss.value,
            "loss_decomposition": proof.loss_decomposition,
        },
    )

    return PolicyTrace.pure(None).with_entry(entry)


def trace_to_proof(trace: PolicyTrace[NodeId]) -> GaloisWitnessedProof:
    """
    Convert DP trace to Galois-witnessed Toulmin proof.

    Uses trace metadata to reconstruct Galois fields.
    """
    entries = trace.log

    if not entries:
        raise ValueError("Cannot convert empty trace to proof")

    # Extract Galois metadata from first entry
    metadata = entries[0].metadata or {}
    loss = metadata.get("galois_loss", 0.5)

    return GaloisWitnessedProof(
        data=str(entries[0].state_before) if entries else "",
        warrant=" → ".join(e.action for e in entries),
        claim=str(entries[-1].state_after) if entries else "",
        backing="; ".join(e.rationale for e in entries if e.rationale),
        qualifier=value_to_qualifier(trace.total_value()),
        rebuttals=(),  # Not captured in trace
        tier=EvidenceTier(metadata.get("tier", "empirical")),
        principles=(),  # Not captured in trace

        # Galois fields
        galois_loss=loss,
        loss_decomposition=metadata.get("loss_decomposition", {}),
        ghost_alternatives=(),  # Not captured in trace
    )
```

### 8.2 Constitutional Reward with Loss Penalty

```python
class GaloisConstitution(Constitution):
    """
    Constitution with Galois loss as negative reward component.

    Reward formula:
    R(s, a, s') = Σ principle_scores - λ · galois_loss(proof(s → s'))

    where λ is loss penalty weight.
    """

    def __init__(self, loss_penalty: float = 0.3):
        super().__init__()
        self.loss_penalty = loss_penalty

    async def reward_with_loss(
        self,
        state: ZeroNode,
        action: EdgeKind,
        next_state: ZeroNode,
        proof: GaloisWitnessedProof,
    ) -> float:
        """
        Compute reward with Galois loss penalty.

        High-coherence proofs get higher reward.
        """
        # Standard constitutional reward
        base_reward = self.reward(state, action, next_state)

        # Galois penalty (loss as negative reward)
        loss_penalty = -self.loss_penalty * proof.galois_loss

        return base_reward + loss_penalty

    def explain_reward(
        self,
        state: ZeroNode,
        action: EdgeKind,
        next_state: ZeroNode,
        proof: GaloisWitnessedProof,
    ) -> str:
        """Explain reward breakdown."""
        base = self.reward(state, action, next_state)
        penalty = -self.loss_penalty * proof.galois_loss
        total = base + penalty

        return f"""
REWARD BREAKDOWN:
  Constitutional Base: {base:.3f}
  Galois Coherence Bonus: {penalty:.3f} (coherence: {proof.coherence:.3f})
  Total: {total:.3f}

Interpretation: {"High-quality proof" if proof.coherence > 0.7 else "Proof needs refinement"}
""".strip()
```

---

## Part IX: CLI Integration

### 9.1 Command Structure

```bash
# Compute Galois loss for a proof
kg zero-seed proof validate <node-id>
# Output: Coherence: 0.87 | Tier: EMPIRICAL | Loss decomposition: {...}

# Analyze all proofs in graph
kg zero-seed proof health
# Output: Graph-wide coherence report

# Generate ghost alternatives for a proof
kg zero-seed proof alternatives <node-id>
# Output: 3 alternative proof structures with loss comparison

# Detect contradictions via super-additivity
kg zero-seed contradictions detect
# Output: 5 contradictions found (sorted by super-additivity)

# Witness report with Galois analytics
kg witness report --galois
# Output: GaloisWitnessReport with loss/coherence metrics

# Set witness batching thresholds
kg zero-seed witness config --single-threshold=0.15 --session-threshold=0.45
```

### 9.2 Example Session

```bash
$ kg zero-seed add "Implement feature X" --layer=4

⚙️  Creating node with Galois validation...

✓ Node created: concept.spec.feature-x
  Layer: L4 (Specification)

  PROOF VALIDATION:
    Galois Loss: 0.23
    Coherence: 0.77 ★★★★☆
    Tier: EMPIRICAL

  LOSS DECOMPOSITION:
    Warrant: 0.08 (tight)
    Backing: 0.12 (reasonable)
    Composition: 0.03 (good)

  WITNESS MODE: SESSION (will batch)

  Ghost Alternatives: 2 found
    [Show] [Ignore]

$ kg zero-seed proof alternatives concept.spec.feature-x

📊 GHOST ALTERNATIVE PROOFS:

Alternative 1: "Bottom-up implementation"
  Loss: 0.19 (better than chosen: 0.23)
  Deferral Cost: 0.04
  Rationale: "Top-down was chosen for clarity, but bottom-up has tighter structure"

Alternative 2: "Prototype-first approach"
  Loss: 0.31 (worse than chosen: 0.23)
  Deferral Cost: 0.08
  Rationale: "Prototype would have higher loss due to speculative nature"

🤔 Recommendation: Consider Alternative 1 if coherence is critical
```

---

## Part X: Research Questions and Open Problems

### 10.1 Answered by Galois Upgrade

| Question (from Zero Seed) | Answer via Galois Loss |
|---------------------------|------------------------|
| When is a proof "good enough"? | When L < 0.3 (empirical tier or better) |
| How to batch witness marks? | Triage by loss: L < 0.1 → single, L < 0.4 → session, L ≥ 0.4 → lazy |
| When do nodes contradict? | When loss_combined > loss_a + loss_b + 0.1 (super-additive) |
| What makes an axiom "strong"? | When behavioral alignment high AND derived proofs have low loss |

### 10.2 New Questions Opened

| ID | Question | Approach |
|----|----------|----------|
| Q1 | **Optimal semantic distance metric**: BERTScore, LLM judge, or embedding cosine? | Benchmark all three, select via correlation with human judgment |
| Q2 | **Loss threshold calibration**: Are 0.1/0.3/0.5/0.7 the right tier bounds? | User study with 100+ proofs, adjust based on empirical fit |
| Q3 | **Super-additivity tolerance**: Is 0.1 the right threshold for contradiction? | Ablation study: vary from 0.05 to 0.3, measure precision/recall |
| Q4 | **Ghost alternative generation**: How many alternatives are useful? | Test with 1, 3, 5 alternatives; measure user engagement |
| Q5 | **Adaptive batching convergence**: Do thresholds stabilize or oscillate? | Long-term study (30+ days), track threshold evolution |
| Q6 | **Loss-difficulty correlation**: Does L(proof) predict task success? | Validate Conjecture 4.1.1 from galois-modularization.md |
| Q7 | **Crystallization coherence**: What loss threshold for crystallization? | Test 0.2, 0.3, 0.4; measure crystal quality via user feedback |

---

## Part XI: Implementation Roadmap

### 11.1 Phase 1: Core Infrastructure (Weeks 1-3)

```
HIGH PRIORITY

Tasks:
  [ ] Implement semantic_distance() with BERTScore, LLM judge, cosine
  [ ] Implement galois_loss(proof) → float
  [ ] Implement compute_loss_decomposition(proof) → ProofLossDecomposition
  [ ] Implement GaloisWitnessedProof dataclass
  [ ] Unit tests for all above

Deliverables:
  - impl/claude/services/zero_seed/galois/
  - impl/claude/services/zero_seed/galois/_tests/

Files:
  - galois/distance.py (semantic distance metrics)
  - galois/loss.py (loss computation)
  - galois/proof.py (GaloisWitnessedProof)
  - galois/decomposition.py (loss decomposition)
```

### 11.2 Phase 2: Validation and Triage (Weeks 4-6)

```
HIGH PRIORITY

Tasks:
  [ ] Implement validate_proof_galois(proof) → ProofValidation
  [ ] Implement select_witness_mode(edit) → WitnessMode
  [ ] Implement witness batching (single/session/lazy)
  [ ] Implement classify_by_loss(loss) → EvidenceTier
  [ ] Integration tests with witness system

Deliverables:
  - galois/validation.py
  - galois/triage.py
  - services/witness/galois_integration.py
```

### 11.3 Phase 3: Contradiction Detection (Weeks 7-9)

```
MEDIUM PRIORITY

Tasks:
  [ ] Implement detect_contradiction_galois(proof_a, proof_b) → bool
  [ ] Implement ContradictionAnalysis with super-additivity
  [ ] Implement ParaconsistentGraph.add_contradiction_edge()
  [ ] CLI: kg zero-seed contradictions detect
  [ ] Contradiction visualization in web UI

Deliverables:
  - galois/contradiction.py
  - protocols/cli/handlers/zero_seed_contradictions.py
  - web/src/components/zero-seed/ContradictionPanel.tsx
```

### 11.4 Phase 4: Ghost Alternatives (Weeks 10-12)

```
MEDIUM PRIORITY

Tasks:
  [ ] Implement generate_ghost_rebuttals(proof) → tuple[str, ...]
  [ ] Implement generate_ghost_alternatives(proof) → tuple[Alternative, ...]
  [ ] CLI: kg zero-seed proof alternatives <node-id>
  [ ] Web UI: Ghost alternative viewer

Deliverables:
  - galois/ghosts.py
  - protocols/cli/handlers/zero_seed_proof.py
  - web/src/components/zero-seed/GhostAlternativesModal.tsx
```

### 11.5 Phase 5: DP Integration (Weeks 13-16)

```
LOW PRIORITY (but HIGH IMPACT)

Tasks:
  [ ] Implement proof_to_trace() with Galois metadata
  [ ] Implement trace_to_proof() with loss reconstruction
  [ ] Implement GaloisConstitution with loss penalty
  [ ] Validation: PolicyTrace ↔ Proof round-trip
  [ ] Documentation: Galois-DP bridge patterns

Deliverables:
  - services/categorical/galois_dp_bridge.py
  - dp/core/galois_constitution.py
  - docs/skills/galois-dp-integration.md
```

---

## Part XII: Success Criteria

### 12.1 Functional Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| **Loss Computation** | Unit tests pass | 100% |
| **Tier Classification** | Accuracy on labeled dataset | ≥ 85% |
| **Contradiction Detection** | Precision/recall on contradictions | ≥ 0.7 |
| **Witness Batching** | Reduction in single witnesses | ≥ 50% |
| **Ghost Alternatives** | User finds alternatives useful | ≥ 60% |

### 12.2 Performance Criteria

| Metric | Target | Rationale |
|--------|--------|-----------|
| Loss computation latency | < 2s per proof | Acceptable for interactive use |
| Semantic distance (BERTScore) | < 100ms | Fast metric for batching |
| Semantic distance (LLM judge) | < 5s | Acceptable for validation |
| Batch witness flush | < 1s for 100 marks | Session end should be fast |

### 12.3 Quality Criteria

| Metric | Target | Validation |
|--------|--------|------------|
| Coherence ↔ human judgment | r > 0.7 | User study with 50+ proofs |
| Loss ↔ task difficulty | r > 0.6 | Empirical validation (Experiment 1) |
| Tier classification accuracy | κ > 0.75 | Inter-rater agreement (Cohen's kappa) |

---

## Part XIII: Theoretical Foundations

### 13.1 Why Galois Loss Works

**Theorem (Informal)**: Galois loss quantifies **implicit structure** in proofs.

**Intuition**:
- A proof with low Galois loss is **self-contained**—all reasoning is explicit
- A proof with high Galois loss has **hidden dependencies**—relies on unstated assumptions
- Modularization exposes these dependencies (they don't survive R ∘ C)

**Formal Statement**:
```
Let P be a proof, R: Proof → ModularProof, C: ModularProof → Proof.
Define implicit structure I(P) = {assumptions in P not explicit in text}.

Then: L(P) = d(P, C(R(P))) ∝ |I(P)|
```

**Corollary**: Minimizing Galois loss is equivalent to making reasoning explicit.

### 13.2 Connection to Kolmogorov Complexity

**Conjecture**: Galois loss approximates **logical depth**.

**Logical Depth** (Bennett): The time required to compute a string from its shortest program.

**Galois Loss**: The "distance" traveled when proof is compressed (R) and decompressed (C).

**Hypothesis**: Proofs with high logical depth (complex derivations) have high Galois loss.

**Test**: Compute correlation between:
- Logical depth (approximated via runtime of shortest proof-checker)
- Galois loss

**Expected**: r > 0.5

### 13.3 Information-Theoretic Interpretation

**Shannon Entropy**:
```
H(P) = -Σ p(x) log p(x)
```

**Galois Loss** as mutual information loss:
```
L(P) ≈ I(P; implicit_structure) - I(C(R(P)); implicit_structure)
```

Where:
- I(P; implicit_structure) = information in P about implicit assumptions
- I(C(R(P)); implicit_structure) = information preserved after R ∘ C

**Interpretation**: Galois loss measures **forgotten mutual information**.

---

## Appendix A: Code Templates

### A.1 Complete GaloisWitnessedProof Factory

```python
async def create_galois_witnessed_proof(
    proof: Proof,
    llm: LLM,
    generate_ghosts: bool = True,
) -> GaloisWitnessedProof:
    """
    Factory for creating GaloisWitnessedProof from basic Proof.

    Args:
        proof: Original Toulmin proof
        llm: LLM for loss computation
        generate_ghosts: Whether to generate ghost alternatives (expensive)

    Returns:
        Extended proof with Galois metadata
    """
    # Compute loss
    loss = await galois_loss(proof, llm)

    # Compute decomposition
    decomp = await compute_loss_decomposition(proof, llm)

    # Generate ghost alternatives (optional)
    ghosts = ()
    if generate_ghosts:
        ghosts = await generate_ghost_alternatives(proof, llm)

    return GaloisWitnessedProof(
        # Original Toulmin fields
        data=proof.data,
        warrant=proof.warrant,
        claim=proof.claim,
        backing=proof.backing,
        qualifier=proof.qualifier,
        rebuttals=proof.rebuttals,
        tier=proof.tier,
        principles=proof.principles,

        # Galois fields
        galois_loss=loss,
        loss_decomposition=decomp.to_dict(),
        ghost_alternatives=ghosts,
    )
```

---

## Appendix B: Experimental Validation Plan

### B.1 Experiment: Loss-Coherence Human Agreement

**Hypothesis**: Galois coherence (1 - loss) correlates with human-judged proof quality.

**Setup**:
1. Collect 100 proofs from Zero Seed usage
2. Compute Galois coherence for each
3. Have 3 human raters judge quality (1-5 scale)
4. Compute correlation

**Success**: Pearson r > 0.7

**Timeline**: 2 weeks

### B.2 Experiment: Witness Batching Efficiency

**Hypothesis**: Galois-based batching reduces witness overhead without losing important marks.

**Setup**:
1. Run Zero Seed session with all-single witnessing (baseline)
2. Run identical session with Galois batching
3. Compare:
   - Total marks created
   - Storage overhead
   - Important marks missed (false negatives)

**Success**:
- ≥50% reduction in single witnesses
- <5% false negatives (important marks batched)

**Timeline**: 1 week

---

*"The coherence IS the inverse loss. The witness IS the mark. The contradiction IS the super-additive signal."*

---

**Filed**: 2025-12-24
**Status**: Theoretical — Ready for Phase 1 Implementation
**Next Actions**:
1. Implement semantic distance metrics (BERTScore, LLM judge, cosine)
2. Implement galois_loss(proof) core algorithm
3. Run Experiment B.1 (loss-coherence human agreement)
4. Integrate with witness system (batching triage)

**Cross-References**:
- `spec/theory/galois-modularization.md` — Foundational theory
- `spec/protocols/zero-seed/core.md` — Original Toulmin proofs
- `spec/protocols/witness-primitives.md` — Mark and Crystal structures
- `spec/theory/dp-native-kgents.md` — DP integration
- `spec/protocols/differance.md` — Ghost alternatives (Différance)
