# Trust and Dialectics: Empirical Refinement

> *"Authority derives from quality of justification."*

**Related Specs**: `spec/protocols/witness.md` (Trust Gradient), `spec/principles/CONSTITUTION.md` (Articles I-VII)
**Priority**: MEDIUM
**Status**: Ready for Adaptation

---

## 1. Current State Analysis

### 1.1 What You Have

**Trust Gradient (L0-L3)**:
```
L0: READ_ONLY (default)
L1: BOUNDED (limited operations)
L2: SUGGESTION (recommends with justification)
L3: AUTONOMOUS (acts independently)
```

**Emerging Constitution**:
- Article I: Symmetric Agency
- Article II: Adversarial Cooperation
- Article III: Supersession Rights
- Article IV: The Disgust Veto
- Article V: Trust Accumulation
- Article VI: Fusion as Goal
- Article VII: Amendment

### 1.2 What's Missing

1. **Trust Integration Formula**: How do different trust sources combine?
2. **Trust Decay**: How does trust change over time without interaction?
3. **Mutual Understanding**: Does each agent understand the other's reasoning?
4. **Empirical Validation**: Does fusion actually produce better decisions?

---

## 2. Research Findings

### 2.1 FIRE Trust Model

The [FIRE model](https://link.springer.com/article/10.1007/s10458-005-6825-4) is the most comprehensive trust framework for multi-agent systems:

**Four Trust Sources**:

| Source | Description | Weight | Your Current Coverage |
|--------|-------------|--------|----------------------|
| **Interaction Trust (I)** | Direct experience with agent | 0.4 | Trust Gradient history |
| **Role-Based Trust (R)** | Trust from structural position | 0.2 | Implicit in L0-L3 |
| **Witness Reputation (W)** | Third-party testimony | 0.2 | Not implemented |
| **Certified Reputation (C)** | Verifiable credentials | 0.2 | Not implemented |

**Integration Formula**:
```
Trust(a, b) = w_I × I(a,b) + w_R × R(a,b) + w_W × W(a,b) + w_C × C(a,b)
```

**Key Insight**: Your current model conflates I and R. Adding W and C would make trust more robust.

### 2.2 Mutual Theory of Mind (MToM)

The [MToM paper](https://arxiv.org/html/2409.08811) (September 2024) introduces:

> "When human beings are interacting with an agent with ToM capability, Mutual Theory of Mind (MToM), which refers to a constant process of reasoning and attributing states to each other, is considered the analysis of the collaboration process."

**Two Directions**:
- **MToHM**: Machine Theory of Human Mind (AI models Kent)
- **HToMM**: Human Theory of Machine Mind (Kent models Claude)

**Implication**: Your dialectical engine assumes mutual understanding but doesn't verify it.

### 2.3 Dialectical Reconciliation

The [KR 2024 paper](https://arxiv.org/html/2306.14694) on dialectical reconciliation:

> "A dialectical reconciliation dialogue resolves inconsistencies, misunderstandings, and knowledge gaps between the explainer and the explainee through argument exchange."

**Empirical Result**: DR-Arg was validated in both computational and human-user experiments.

**Key Features**:
1. Structured argument exchange
2. Collaborative construction of shared understanding
3. Explicit handling of misunderstandings

### 2.4 Antagonistic AI

The [Frontiers paper](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2024.1464690/full) proposes:

> "A shift in perspective termed 'antagonistic AI,' a counter-narrative to designing AI systems to be agreeable and subservient. Human-LLM interactions could benefit from confrontational LLMs that challenge users."

**Rationale**: Forcing users to confront assumptions promotes critical thinking.

**Alignment**: This validates your Article II (Adversarial Cooperation).

### 2.5 Human-AI Collaboration Taxonomy

The [Frontiers systematic review](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2024.1521066/full) found:

> "Human-AI collaboration is not very collaborative yet."

**Taxonomy of Interaction Patterns**:
1. AI as tool (human dominant)
2. AI as assistant (turn-taking)
3. AI as partner (joint decision)
4. AI as lead (AI dominant)

**Your Model**: Article I (Symmetric Agency) aims for pattern 3, but implementation may be pattern 2.

---

## 3. Refinement Recommendations

### 3.1 Implement FIRE Trust Model

**Rationale**: More robust trust with multiple sources.

```python
from dataclasses import dataclass, field
from enum import Enum

class TrustLevel(Enum):
    """Trust levels mapping to your L0-L3."""
    READ_ONLY = 0       # L0
    BOUNDED = 1         # L1
    SUGGESTION = 2      # L2
    AUTONOMOUS = 3      # L3


@dataclass
class FIRETrustModel:
    """
    Trust model integrating four sources per FIRE framework.

    Trust(a, b) = w_I × I(a,b) + w_R × R(a,b) + w_W × W(a,b) + w_C × C(a,b)
    """

    # Weights (empirically calibrated in FIRE paper)
    interaction_weight: float = 0.4
    role_weight: float = 0.2
    witness_weight: float = 0.2
    certified_weight: float = 0.2

    # Trust histories
    interaction_history: dict[str, list[TrustMark]] = field(default_factory=dict)
    role_assignments: dict[str, AgentRole] = field(default_factory=dict)
    witness_reports: dict[str, list[WitnessReport]] = field(default_factory=dict)
    certifications: dict[str, list[Certification]] = field(default_factory=dict)

    def compute_trust(self, trustor: str, trustee: str) -> TrustScore:
        """
        Compute trust from trustor to trustee.

        Returns composite score with breakdown.
        """
        # Interaction trust: based on direct experience
        I = self._interaction_trust(trustor, trustee)

        # Role-based trust: based on structural position
        R = self._role_trust(trustee)

        # Witness trust: based on third-party reports
        W = self._witness_trust(trustee)

        # Certified trust: based on verifiable credentials
        C = self._certified_trust(trustee)

        # Composite score
        score = (
            self.interaction_weight * I +
            self.role_weight * R +
            self.witness_weight * W +
            self.certified_weight * C
        )

        # Map to trust level
        level = self._score_to_level(score)

        return TrustScore(
            value=score,
            level=level,
            breakdown={"I": I, "R": R, "W": W, "C": C},
            explanation=self._explain(level, {"I": I, "R": R, "W": W, "C": C}),
            confidence=self._compute_confidence(I, R, W, C),
        )

    def _interaction_trust(self, trustor: str, trustee: str) -> float:
        """
        Compute interaction trust from direct experience.

        Uses exponential decay: recent interactions matter more.
        """
        key = f"{trustor}:{trustee}"
        history = self.interaction_history.get(key, [])

        if not history:
            return 0.5  # Neutral default

        # Weighted average with recency decay
        total_weight = 0.0
        weighted_sum = 0.0

        now = time.time()
        for mark in history:
            age_hours = (now - mark.timestamp) / 3600
            weight = 0.95 ** age_hours  # 5% decay per hour
            weighted_sum += mark.trust_value * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.5

    def _role_trust(self, trustee: str) -> float:
        """
        Compute role-based trust from structural position.

        Different roles have different baseline trust levels.
        """
        role = self.role_assignments.get(trustee, AgentRole.UNKNOWN)

        role_baselines = {
            AgentRole.OWNER: 1.0,        # Full trust
            AgentRole.COLLABORATOR: 0.8,  # High trust
            AgentRole.ASSISTANT: 0.6,     # Moderate trust
            AgentRole.TOOL: 0.4,          # Limited trust
            AgentRole.UNKNOWN: 0.3,       # Low trust
        }

        return role_baselines.get(role, 0.3)

    def _witness_trust(self, trustee: str) -> float:
        """
        Compute trust from third-party witness reports.

        Your marks system provides this naturally.
        """
        reports = self.witness_reports.get(trustee, [])

        if not reports:
            return 0.5  # Neutral default

        # Average of witness assessments, weighted by witness credibility
        total_weight = 0.0
        weighted_sum = 0.0

        for report in reports:
            witness_credibility = self._get_witness_credibility(report.witness)
            weighted_sum += report.assessment * witness_credibility
            total_weight += witness_credibility

        return weighted_sum / total_weight if total_weight > 0 else 0.5

    def _certified_trust(self, trustee: str) -> float:
        """
        Compute trust from verifiable certifications.

        In kgents context: proofs, verified marks, formal guarantees.
        """
        certs = self.certifications.get(trustee, [])

        if not certs:
            return 0.5  # Neutral default

        # Each certification adds trust up to max of 1.0
        cert_values = [c.trust_value for c in certs if c.verified]
        return min(1.0, sum(cert_values)) if cert_values else 0.5

    def _score_to_level(self, score: float) -> TrustLevel:
        """Map continuous score to discrete level."""
        if score < 0.25:
            return TrustLevel.READ_ONLY
        elif score < 0.50:
            return TrustLevel.BOUNDED
        elif score < 0.75:
            return TrustLevel.SUGGESTION
        else:
            return TrustLevel.AUTONOMOUS

    def _explain(self, level: TrustLevel, breakdown: dict) -> str:
        """Generate human-readable explanation of trust level."""
        parts = []

        if breakdown["I"] > 0.7:
            parts.append("strong positive interaction history")
        elif breakdown["I"] < 0.3:
            parts.append("limited or negative interaction history")

        if breakdown["R"] > 0.7:
            parts.append("trusted role")
        elif breakdown["R"] < 0.3:
            parts.append("untrusted role")

        if breakdown["W"] > 0.7:
            parts.append("positive witness reports")
        elif breakdown["W"] < 0.3:
            parts.append("negative or no witness reports")

        if breakdown["C"] > 0.7:
            parts.append("verified certifications")

        reason = ", ".join(parts) if parts else "default assessment"
        return f"Trust level {level.name} due to: {reason}"

    def record_interaction(
        self,
        trustor: str,
        trustee: str,
        outcome: InteractionOutcome,
    ) -> None:
        """Record an interaction outcome to update trust."""
        key = f"{trustor}:{trustee}"
        if key not in self.interaction_history:
            self.interaction_history[key] = []

        mark = TrustMark(
            timestamp=time.time(),
            trust_value=outcome.to_trust_value(),
            context=outcome.context,
        )
        self.interaction_history[key].append(mark)
```

### 3.2 Implement Mutual Theory of Mind Protocol

**Rationale**: Verify mutual understanding during dialectical exchange.

```python
@dataclass
class MToMState:
    """State of Mutual Theory of Mind between two agents."""

    # Kent's model of Claude
    kent_models_claude: dict[str, float] = field(default_factory=dict)
    # - "understands_technical": 0.9
    # - "agrees_with_aesthetics": 0.7
    # - "risk_tolerance": 0.4

    # Claude's model of Kent
    claude_models_kent: dict[str, float] = field(default_factory=dict)
    # - "values_simplicity": 0.85
    # - "prefers_elegance": 0.9
    # - "risk_tolerance": 0.6

    # Alignment score
    @property
    def alignment(self) -> float:
        """How well do the models align with reality?"""
        # This would be validated through interaction outcomes
        return self._compute_alignment()


class MToMProtocol:
    """
    Protocol for maintaining Mutual Theory of Mind.

    Before each dialectical exchange, verify understanding.
    """

    def __init__(self, llm: LLM):
        self.llm = llm
        self.state = MToMState()

    async def pre_exchange_check(
        self,
        topic: str,
        kent_position: str,
        claude_position: str,
    ) -> MToMCheck:
        """
        Before dialectical exchange, verify mutual understanding.

        Returns issues that should be clarified first.
        """
        issues = []

        # Claude models Kent's likely concerns
        kent_concerns = await self._model_concerns(
            "Kent", kent_position, topic
        )

        # Check if Claude's model matches Kent's actual concerns
        for concern in kent_concerns:
            if concern.confidence < 0.7:
                issues.append(MToMIssue(
                    agent="Claude",
                    uncertainty=f"Uncertain about Kent's concern: {concern.description}",
                    question=f"Kent, is this a concern for you: {concern.description}?",
                ))

        # Kent models Claude's reasoning (via Claude's self-report)
        claude_reasoning = await self._explain_reasoning(
            "Claude", claude_position, topic
        )

        return MToMCheck(
            issues=issues,
            kent_model_confidence=self._compute_model_confidence("Kent"),
            claude_model_confidence=self._compute_model_confidence("Claude"),
            proceed=len(issues) == 0,
            clarifications_needed=issues,
        )

    async def post_exchange_update(
        self,
        exchange: DialecticalExchange,
        outcome: ExchangeOutcome,
    ) -> None:
        """
        After dialectical exchange, update mental models.

        Learn from:
        - Surprises (predictions that failed)
        - Confirmations (predictions that succeeded)
        """
        # Update Claude's model of Kent
        if outcome.kent_surprised_claude:
            # Adjust relevant dimensions
            for dimension, surprise in outcome.surprises.items():
                current = self.state.claude_models_kent.get(dimension, 0.5)
                # Move toward surprising value
                self.state.claude_models_kent[dimension] = (
                    0.7 * current + 0.3 * surprise.actual_value
                )

        # Track model accuracy over time
        self._record_model_accuracy(outcome)

    async def _model_concerns(
        self,
        agent: str,
        position: str,
        topic: str,
    ) -> list[ModeledConcern]:
        """Model what concerns an agent likely has."""
        response = await self.llm.generate(
            system=f"You are modeling {agent}'s concerns about a proposal.",
            user=f"""Topic: {topic}
Position: {position}

What concerns would {agent} likely have about this?
List each concern with confidence (0-1) that this is actually a concern.

Format: concern | confidence""",
            temperature=0.3,
        )

        concerns = []
        for line in response.strip().split("\n"):
            if "|" in line:
                desc, conf = line.split("|")
                concerns.append(ModeledConcern(
                    description=desc.strip(),
                    confidence=float(conf.strip()),
                ))

        return concerns
```

### 3.3 Implement Dialectical Quality Measurement

**Rationale**: Validate that fusion produces better decisions than individual views.

```python
@dataclass
class DialecticalQualityMetrics:
    """Metrics for evaluating dialectical exchange quality."""

    # Process metrics
    exchange_count: int
    clarifications_needed: int
    rebuttals_generated: int
    supersessions_proposed: int
    disgust_vetos: int

    # Outcome metrics
    fusion_achieved: bool
    fusion_quality: float  # 0-1

    # Comparative metrics (vs. individual decisions)
    kent_alone_quality: float | None = None
    claude_alone_quality: float | None = None
    fusion_improvement: float | None = None

    @property
    def synergy(self) -> float | None:
        """
        Synergy = Fusion quality - max(individual qualities)

        Positive synergy means collaboration added value.
        """
        if self.kent_alone_quality is None or self.claude_alone_quality is None:
            return None

        max_individual = max(self.kent_alone_quality, self.claude_alone_quality)
        return self.fusion_quality - max_individual


class DialecticalQualityEvaluator:
    """Evaluate the quality of dialectical exchanges."""

    def __init__(self, llm: LLM, evaluator_prompt: str | None = None):
        self.llm = llm
        self.evaluator_prompt = evaluator_prompt or self._default_evaluator_prompt()

    async def evaluate_decision(
        self,
        decision: Decision,
        context: DecisionContext,
    ) -> DecisionQuality:
        """
        Evaluate a decision on multiple dimensions.

        Used to compare Kent-alone, Claude-alone, and fusion decisions.
        """
        response = await self.llm.generate(
            system=self.evaluator_prompt,
            user=f"""Evaluate this decision:

Context: {context.description}
Decision: {decision.description}
Reasoning: {decision.reasoning}

Rate on these dimensions (0-1):
1. Correctness: Is this likely to be the right choice?
2. Justification: Is the reasoning sound and well-supported?
3. Consideration: Were alternatives properly considered?
4. Risk awareness: Are potential downsides acknowledged?
5. Alignment: Does this align with stated principles?

Format: dimension | score | brief reason""",
            temperature=0.0,
        )

        scores = self._parse_scores(response)

        return DecisionQuality(
            correctness=scores.get("correctness", 0.5),
            justification=scores.get("justification", 0.5),
            consideration=scores.get("consideration", 0.5),
            risk_awareness=scores.get("risk_awareness", 0.5),
            alignment=scores.get("alignment", 0.5),
            overall=sum(scores.values()) / len(scores) if scores else 0.5,
        )

    async def compare_decisions(
        self,
        context: DecisionContext,
        kent_decision: Decision,
        claude_decision: Decision,
        fusion_decision: Decision,
    ) -> DialecticalQualityMetrics:
        """
        Compare three decisions to measure fusion value.

        This is the key validation for Article VI (Fusion as Goal).
        """
        kent_quality = await self.evaluate_decision(kent_decision, context)
        claude_quality = await self.evaluate_decision(claude_decision, context)
        fusion_quality = await self.evaluate_decision(fusion_decision, context)

        return DialecticalQualityMetrics(
            exchange_count=context.exchange_count,
            clarifications_needed=context.clarifications_needed,
            rebuttals_generated=context.rebuttals_generated,
            supersessions_proposed=context.supersessions_proposed,
            disgust_vetos=context.disgust_vetos,
            fusion_achieved=True,
            fusion_quality=fusion_quality.overall,
            kent_alone_quality=kent_quality.overall,
            claude_alone_quality=claude_quality.overall,
            fusion_improvement=fusion_quality.overall - max(
                kent_quality.overall, claude_quality.overall
            ),
        )
```

---

## 4. Validation Protocol

### 4.1 Trust Model Validation

**Goal**: Validate FIRE model improves trust predictions.

**Protocol**:
1. Collect 50 interaction histories
2. Compute trust using current (L0-L3) method
3. Compute trust using FIRE method
4. Measure prediction accuracy for cooperation outcomes

**Success Criteria**:
- FIRE predictions more accurate than current method
- All four sources contribute (no source has zero weight)

### 4.2 MToM Validation

**Goal**: Validate that MToM improves collaboration.

**Protocol**:
1. Conduct 20 dialectical exchanges without MToM checks
2. Conduct 20 dialectical exchanges with MToM checks
3. Measure: misunderstanding rate, exchange length, outcome quality

**Success Criteria**:
- Misunderstandings reduced by > 30%
- Outcome quality improved by > 10%

### 4.3 Fusion Quality Validation

**Goal**: Validate that fusion beats individuals (Article VI).

**Protocol**:
1. Collect 50 architectural decisions from git history
2. Record: Kent's initial view, Claude's analysis, final fusion
3. Have expert evaluate quality of each
4. Compute synergy for each decision

**Success Criteria**:
- Positive synergy in > 60% of decisions
- Mean synergy > 0.05 (5% improvement)

---

## Pilot Integration

**Goal**: Make trust accumulation and fusion visible in each run.

### Prompt Hooks (Minimal Insertions)
Add a "Trust Delta" line to `.reflections.*.md` in WITNESS phase:

```
Trust Delta: [+ / 0 / -]
Reason: [one sentence, evidence-backed]
```

### Coordination Artifacts
- CREATIVE and ADVERSARIAL each record one trust delta per iteration 8-10.
- PLAYER adds a delta for the overall experience (trust in the build).
- CRYSTAL.md aggregates deltas and notes any negative shifts.

### Outcome Target
- Build a longitudinal trust trace across runs.
- Link trust shifts to decision quality in post-run analysis.

---

## 5. References

1. **Huynh, T., Jennings, N., & Shadbolt, N.** (2006). An integrated trust and reputation model for open multi-agent systems. *AAMAS*. https://link.springer.com/article/10.1007/s10458-005-6825-4

2. **Wang, Y., et al.** (2024). Mutual Theory of Mind in Human-AI Collaboration. *arXiv:2409.08811*. https://arxiv.org/html/2409.08811

3. **Sklar, E., et al.** (2024). Dialectical Reconciliation via Structured Argumentative Dialogues. *KR 2024*. https://arxiv.org/html/2306.14694

4. **Sartori, J., & Theodorou, A.** (2024). Fostering effective hybrid human-LLM reasoning and decision making. *Frontiers in AI*. https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2024.1464690/full

5. **Westphal, A., & Schaub, T.** (2024). Human-AI collaboration is not very collaborative yet: a taxonomy of interaction patterns. *Frontiers in Computer Science*. https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2024.1521066/full

6. **Barbosa, R., Santos, R., & Novais, P.** (2024). A Trust Model for Informed Agent Collaboration in Complex Tasks. *Intelligent Computing*. (Referenced in search results)

---

*"Trust is earned through demonstrated alignment."*
