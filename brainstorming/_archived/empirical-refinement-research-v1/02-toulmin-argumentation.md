# Toulmin Argumentation: Empirical Refinement

> *"The proof IS the decision. The mark IS the witness."*

**Related Spec**: `spec/protocols/witness.md`
**Priority**: HIGH
**Status**: Ready for Implementation

---

## 1. Current State Analysis

### 1.1 What You Have

Your `GaloisWitnessedProof` extends Toulmin with quantified coherence:

```python
@dataclass(frozen=True)
class GaloisWitnessedProof(Proof):
    # Toulmin fields
    data: str           # Evidence
    warrant: str        # Reasoning
    claim: str          # Conclusion
    backing: str        # Support for warrant
    qualifier: str      # Confidence ("definitely", "probably")
    rebuttals: tuple[str, ...]  # Defeaters

    # Galois extensions
    galois_loss: float  # L(proof) ∈ [0, 1]

    @property
    def coherence(self) -> float:
        return 1.0 - self.galois_loss
```

### 1.2 What's Missing

1. **Automated Rebuttal Generation**: Rebuttals are static, not derived from analysis
2. **Component-Level Loss**: Which Toulmin component contributes most to loss?
3. **Critical Question Integration**: No systematic challenge mechanism
4. **Empirical Validation**: Does Toulmin structure actually improve LLM reasoning?

---

## 2. Research Findings

### 2.1 Critical-Questions-of-Thought (CQoT)

The [CQoT paper](https://arxiv.org/html/2412.15177v1) (December 2024) provides a breakthrough:

> "The approach sits within the tradition of Toulmin's schema and its defeasible account of argumentative conclusions. We treat the LLM as providing reasoning that can be structured as per a Toulmin schema, and then use pertinent critical questions to check the validity of the presumptive conclusions."

**Key Finding**: Employing critical questions **improves LLM reasoning capabilities** by helping detect and correct logical mistakes before final output.

**Critical Questions for Each Toulmin Component**:

| Component | Critical Question |
|-----------|------------------|
| Data | "Is the evidence relevant? Is it sufficient?" |
| Warrant | "Does this reasoning pattern apply here?" |
| Claim | "Does the claim follow from data + warrant?" |
| Backing | "Is the backing authoritative? Is it current?" |
| Qualifier | "Is the confidence level appropriate?" |

### 2.2 Conversational Agent Validation

The [PMC study on conversational agents](https://pmc.ncbi.nlm.nih.gov/articles/PMC8680349/) achieved:

- **F-score: 0.80** for detecting Toulmin components
- "Precision and recall values are overall very reasonable"
- Confirms Toulmin structure can be computationally detected

### 2.3 Toulmin in AI History

[Verheij's foundational work](https://link.springer.com/chapter/10.1007/978-0-387-98197-0_11) identifies four Toulmin themes in AI:

1. **Domain-dependence**: Reasoning standards vary by field
2. **Procedural approach**: Argumentation as process
3. **Defeasibility**: Conclusions can be withdrawn
4. **Argument structure**: Beyond formal logic

**Key Quote**: "Toulmin considers the study of defeasibility an empirical question."

### 2.4 Trust Enhancement

[ACM study on Toulmin for analytics advice](https://dl.acm.org/doi/10.1145/3580479) found:

> "Based on three experimental studies... we show evidence for the different roles Toulmin's statement-types play in enhancing various trusting-beliefs in PAA systems."

**Implication**: Toulmin structure not only improves reasoning but also user trust.

---

## 3. Refinement Recommendations

### 3.1 Implement NLI-Based Rebuttal Generation

**Rationale**: Use Natural Language Inference to automatically detect potential rebuttals.

```python
from transformers import pipeline

class RebuttalGenerator:
    """Generate rebuttals using NLI contradiction detection."""

    def __init__(self):
        self.nli = pipeline("text-classification", model="facebook/bart-large-mnli")

    def generate_rebuttals(self, proof: GaloisWitnessedProof) -> list[str]:
        """
        Generate rebuttals by checking for implicit contradictions.

        Uses NLI to detect:
        1. Data-claim contradictions
        2. Warrant-backing inconsistencies
        3. Hidden assumptions that could fail
        """
        rebuttals = list(proof.rebuttals)  # Start with existing

        # Check data-claim entailment
        data_claim_result = self.nli(
            f"{proof.data}",
            candidate_labels=["entails claim", "contradicts claim", "neutral"],
        )
        if data_claim_result[0]["label"] == "contradicts claim":
            rebuttals.append(
                f"Unless: Evidence may not support claim (NLI confidence: {data_claim_result[0]['score']:.2f})"
            )

        # Check warrant plausibility
        warrant_result = self.nli(
            f"Given {proof.data}, it follows that {proof.claim} because {proof.warrant}",
            candidate_labels=["valid reasoning", "invalid reasoning", "uncertain"],
        )
        if warrant_result[0]["label"] == "invalid reasoning":
            rebuttals.append(
                f"Unless: Reasoning may be flawed (NLI confidence: {warrant_result[0]['score']:.2f})"
            )

        # Check backing authority
        if proof.backing:
            backing_result = self.nli(
                f"{proof.backing} supports {proof.warrant}",
                candidate_labels=["supports", "contradicts", "irrelevant"],
            )
            if backing_result[0]["label"] in ["contradicts", "irrelevant"]:
                rebuttals.append(
                    f"Unless: Backing may not support warrant ({backing_result[0]['label']})"
                )

        return rebuttals


# Integration with GaloisWitnessedProof
@dataclass(frozen=True)
class EnhancedGaloisProof(GaloisWitnessedProof):
    """Proof with automated rebuttal generation."""

    @property
    def rebuttals_enhanced(self) -> tuple[str, ...]:
        """Combine static and NLI-generated rebuttals."""
        generator = RebuttalGenerator()
        nli_rebuttals = generator.generate_rebuttals(self)
        return tuple(set(self.rebuttals) | set(nli_rebuttals))

    @property
    def rebuttal_strength(self) -> float:
        """Quantify how strongly the proof is rebutted."""
        rebuttals = self.rebuttals_enhanced
        if not rebuttals:
            return 0.0
        # More rebuttals = weaker proof
        return min(1.0, len(rebuttals) * 0.2)

    @property
    def effective_coherence(self) -> float:
        """Coherence adjusted for rebuttals."""
        return self.coherence * (1 - self.rebuttal_strength)
```

### 3.2 Implement Loss Decomposition by Component

**Rationale**: Identify which Toulmin component contributes most to coherence loss.

```python
@dataclass(frozen=True)
class ProofLossDecomposition:
    """Break down Galois loss by Toulmin component."""

    data_loss: float
    warrant_loss: float
    claim_loss: float
    backing_loss: float
    qualifier_loss: float
    rebuttal_loss: float
    composition_loss: float  # Residual from component interactions

    @property
    def total(self) -> float:
        return (
            self.data_loss + self.warrant_loss + self.claim_loss +
            self.backing_loss + self.qualifier_loss + self.rebuttal_loss +
            self.composition_loss
        )

    @property
    def bottleneck(self) -> str:
        """Identify the weakest component."""
        components = {
            "data": self.data_loss,
            "warrant": self.warrant_loss,
            "claim": self.claim_loss,
            "backing": self.backing_loss,
            "qualifier": self.qualifier_loss,
            "rebuttals": self.rebuttal_loss,
        }
        return max(components, key=components.get)

    def improvement_priority(self) -> list[str]:
        """Components ordered by improvement potential."""
        components = {
            "data": self.data_loss,
            "warrant": self.warrant_loss,
            "claim": self.claim_loss,
            "backing": self.backing_loss,
            "qualifier": self.qualifier_loss,
            "rebuttals": self.rebuttal_loss,
        }
        return sorted(components, key=components.get, reverse=True)


async def compute_loss_decomposition(
    proof: GaloisWitnessedProof,
    galois: GaloisLossComputer,
) -> ProofLossDecomposition:
    """
    Compute loss contribution of each Toulmin component.

    Uses ablation: remove each component, measure loss change.
    """
    full_text = proof_to_text(proof)
    full_loss = await galois.compute(full_text)

    # Ablation study
    component_losses = {}

    for component in ["data", "warrant", "claim", "backing", "qualifier", "rebuttals"]:
        ablated = ablate_component(proof, component)
        ablated_text = proof_to_text(ablated)
        ablated_loss = await galois.compute(ablated_text)
        # Component contribution = how much loss decreases without it
        component_losses[component] = max(0.0, full_loss.total - ablated_loss.total)

    # Composition loss = residual
    composition_loss = max(
        0.0,
        full_loss.total - sum(component_losses.values())
    )

    return ProofLossDecomposition(
        data_loss=component_losses["data"],
        warrant_loss=component_losses["warrant"],
        claim_loss=component_losses["claim"],
        backing_loss=component_losses["backing"],
        qualifier_loss=component_losses["qualifier"],
        rebuttal_loss=component_losses["rebuttals"],
        composition_loss=composition_loss,
    )
```

### 3.3 Implement Critical Question Protocol

**Rationale**: Systematically challenge proofs using CQoT methodology.

```python
@dataclass
class CriticalQuestion:
    """A critical question for challenging a proof component."""
    component: str
    question: str
    challenge_type: str  # "relevance", "sufficiency", "validity", "authority"


TOULMIN_CRITICAL_QUESTIONS = [
    # Data challenges
    CriticalQuestion("data", "Is the evidence relevant to the claim?", "relevance"),
    CriticalQuestion("data", "Is the evidence sufficient to support the claim?", "sufficiency"),
    CriticalQuestion("data", "Is the evidence accurate and up-to-date?", "validity"),

    # Warrant challenges
    CriticalQuestion("warrant", "Does this reasoning pattern apply in this context?", "validity"),
    CriticalQuestion("warrant", "Are there exceptions to this reasoning?", "sufficiency"),
    CriticalQuestion("warrant", "Is this the most appropriate reasoning approach?", "relevance"),

    # Claim challenges
    CriticalQuestion("claim", "Does the claim follow necessarily from the data and warrant?", "validity"),
    CriticalQuestion("claim", "Is the claim too strong given the evidence?", "sufficiency"),

    # Backing challenges
    CriticalQuestion("backing", "Is the backing source authoritative?", "authority"),
    CriticalQuestion("backing", "Is the backing still current and applicable?", "validity"),

    # Qualifier challenges
    CriticalQuestion("qualifier", "Is the confidence level appropriate given the evidence?", "validity"),
]


class CriticalQuestionChecker:
    """Apply critical questions to challenge a proof."""

    def __init__(self, llm: LLM):
        self.llm = llm

    async def challenge(self, proof: GaloisWitnessedProof) -> list[ChallengeResult]:
        """
        Apply critical questions and identify weaknesses.

        Returns list of failed challenges with explanations.
        """
        results = []

        for cq in TOULMIN_CRITICAL_QUESTIONS:
            component_value = getattr(proof, cq.component, None)
            if not component_value:
                continue

            # Ask LLM to evaluate the critical question
            response = await self.llm.generate(
                system="""You are a critical reasoning evaluator.
Answer YES if the question is satisfied, NO if it reveals a weakness.
Provide brief explanation.""",
                user=f"""Proof component ({cq.component}): {component_value}

Full proof context:
- Data: {proof.data}
- Warrant: {proof.warrant}
- Claim: {proof.claim}

Critical question: {cq.question}

Does this component satisfy the question?""",
                temperature=0.0,
            )

            passed = response.strip().upper().startswith("YES")
            results.append(ChallengeResult(
                question=cq,
                passed=passed,
                explanation=response,
            ))

        return results

    async def strengthen(
        self,
        proof: GaloisWitnessedProof,
        failed_challenges: list[ChallengeResult],
    ) -> GaloisWitnessedProof:
        """
        Improve proof by addressing failed challenges.

        Returns strengthened proof with additional rebuttals or refined components.
        """
        new_rebuttals = list(proof.rebuttals)

        for challenge in failed_challenges:
            if not challenge.passed:
                # Add as explicit rebuttal
                new_rebuttals.append(
                    f"Unless {challenge.question.question.lower()} fails: {challenge.explanation}"
                )

        return GaloisWitnessedProof(
            data=proof.data,
            warrant=proof.warrant,
            claim=proof.claim,
            backing=proof.backing,
            qualifier=self._adjust_qualifier(proof.qualifier, len(failed_challenges)),
            rebuttals=tuple(new_rebuttals),
            galois_loss=proof.galois_loss,
            tier=proof.tier,
            principles=proof.principles,
        )

    def _adjust_qualifier(self, current: str, failed_count: int) -> str:
        """Downgrade qualifier based on failed challenges."""
        qualifiers = ["certainly", "probably", "possibly", "presumably", "arguably"]
        try:
            idx = qualifiers.index(current.lower())
            new_idx = min(len(qualifiers) - 1, idx + failed_count)
            return qualifiers[new_idx]
        except ValueError:
            return current
```

---

## 4. Evidence Tier Refinement

### 4.1 Current Tiers

```python
class EvidenceTier(Enum):
    CATEGORICAL = 1     # Mathematical (laws hold)
    EMPIRICAL = 2       # Scientific (ASHC runs)
    AESTHETIC = 3       # Hardy criteria
    GENEALOGICAL = 4    # Pattern archaeology
    SOMATIC = 5         # The Mirror Test
```

### 4.2 Proposed Galois-Based Tier Classification

```python
def classify_tier_by_loss(loss: float) -> EvidenceTier:
    """
    Map Galois loss to evidence tier.

    Lower loss = higher tier = stronger evidence.

    Thresholds derived from:
    - CATEGORICAL: Near-zero loss (formal proofs)
    - EMPIRICAL: Low loss (reproducible data)
    - AESTHETIC: Moderate loss (taste-based)
    - GENEALOGICAL: Higher loss (historical patterns)
    - SOMATIC: Highest loss (gut feeling, least formal)
    """
    if loss < 0.10:
        return EvidenceTier.CATEGORICAL
    elif loss < 0.25:
        return EvidenceTier.EMPIRICAL
    elif loss < 0.45:
        return EvidenceTier.AESTHETIC
    elif loss < 0.65:
        return EvidenceTier.GENEALOGICAL
    else:
        return EvidenceTier.SOMATIC
```

---

## 5. Validation Protocol

### 5.1 Rebuttal Quality Experiment

**Goal**: Validate that NLI-generated rebuttals are meaningful.

**Protocol**:
1. Generate rebuttals for 100 proofs using NLI method
2. Have human raters evaluate: "Is this a valid concern?"
3. Compute precision and recall vs. human-generated rebuttals

**Success Criteria**:
- Precision > 0.70 (most generated rebuttals are valid)
- Recall > 0.50 (catches half of what humans would)

### 5.2 Critical Question Effectiveness

**Goal**: Validate that CQoT improves proof quality.

**Protocol**:
1. Generate 50 proofs without CQoT
2. Generate 50 proofs with CQoT challenge/strengthen cycle
3. Have experts rate proof quality (1-5 scale)

**Success Criteria**:
- CQoT proofs score 0.5+ points higher on average
- CQoT proofs have fewer logical errors

---

## Pilot Integration

**Goal**: Upgrade decision quality and traceability inside pilot runs.

### Prompt Hooks (Minimal Insertions)
Add a "Micro-Toulmin" block to `.offerings.*.md` updates:

```
## Toulmin (Decision: DD-3)
Claim: [what we decided]
Data: [evidence from spec/code/play]
Warrant: [why data supports claim]
Backing: [source, test, or proof]
Qualifier: [confidence level]
Rebuttal: [one plausible counter-argument]
```

### Coordination Artifacts
- Require CREATIVE and ADVERSARIAL to include the block for each DD-N.
- Require PLAYER to include a rebuttal line in `.player.feedback.md` for each strong claim.

### Outcome Target
- Reduce contradiction count in BUILD by ≥25%.
- Increase actionable clarity in WITNESS (fewer "why did we do this?" gaps).

---

## 6. References

1. **Khatib, D., et al.** (2024). Critical-Questions-of-Thought: Steering LLM reasoning with Argumentative Querying. *arXiv:2412.15177*. https://arxiv.org/html/2412.15177v1

2. **Verheij, B.** (2009). The Toulmin Argument Model in Artificial Intelligence. In *Argumentation in Artificial Intelligence*. Springer. https://link.springer.com/chapter/10.1007/978-0-387-98197-0_11

3. **Wang, S., et al.** (2021). Developing a Conversational Agent's Capability to Identify Structural Wrongness in Arguments Based on Toulmin's Model. *PMC*. https://pmc.ncbi.nlm.nih.gov/articles/PMC8680349/

4. **Elkins, K., & Chun, J.** (2023). Using Toulmin's Argumentation Model to Enhance Trust in Analytics-Based Advice Giving Systems. *ACM TMIS*. https://dl.acm.org/doi/10.1145/3580479

5. **Chen, X., et al.** (2023). MENLI: Robust Evaluation Metrics from Natural Language Inference. *TACL*. https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00576/116715/MENLI-Robust-Evaluation-Metrics-from-Natural

---

*"The goal is not to win arguments, but to find truth."*
