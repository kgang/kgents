# ASHC Game Meta-Framework: Lucid Frameworks for Game Generation

> *"The spec defines what CAN be generated, not what MUST be generated."*
>
> *"Run the tree a thousand times, and the pattern of nudges IS the proof."*

**Status**: Specification Draft
**Date**: 2026-01-10
**Derived From**: wasm-survivors PROTO_SPEC + ASHC Evidence Pipeline + Experience Quality Operad + Pilot Specification Protocol
**Coherence**: Target L ~ 0.20 (Values tier)

---

## Part I: Vision Statement

### 1.1 What Is the ASHC Game Meta-Framework?

The ASHC Game Meta-Framework is a **generative architecture** for game development that treats specifications as possibility spaces rather than prescriptions. It combines three insights:

1. **Galois Stratification**: Every design decision has a measurable loss under restructuring. Axioms (L < 0.10) survive; tuning (L > 0.70) varies freely.

2. **Evidence-Driven Verification**: ASHC compiles specs to implementations through repeated runs with Bayesian confidence. The proof is empirical, not formal.

3. **Categorical Composition**: Games are algebraic structures where mechanics, quality, and experience compose according to operad laws.

**The Radical Promise**: Given a set of axioms (player agency, attributable outcomes, visible mastery, compositional experience), the framework can:
- Generate multiple valid game implementations
- Verify spec-impl equivalence via Galois loss
- Detect when implementations drift from specifications
- Regenerate isomorphic games from the same axioms with different themes

### 1.2 How It Enables "Lucid Frameworks for Game Generation"

The framework is "lucid" in three senses:

**Lucid as Transparent**: Every design decision is traced to its axiomatic source. When you ask "why is THE BALL the signature mechanic?", the framework can show: A1 (Agency) + A2 (Attribution) + V1 (Contrast) → S1 (Collective Threat) → THE BALL.

**Lucid as Generative**: Like lucid dreaming, you maintain awareness while the system generates. You specify the dream (axioms), and the framework generates valid instantiations you might not have imagined.

**Lucid as Measurable**: Quality is not subjective—it's the Experience Quality Operad in action. Q = F × (C × A × V^(1/n)) is computable for any game state.

### 1.3 The Transformative Potential

**For Game Developers**:
- Rapid prototyping: Generate 10 valid game variants from one axiom set
- A/B testing with semantic grounding: "This variant has 15% higher contrast but 8% lower arc coverage"
- Automated drift detection: CI/CD catches when code diverges from design intent

**For AI-Assisted Design**:
- LLMs generate implementations; ASHC verifies they satisfy axioms
- The system learns which nudges improve outcomes
- Causal attribution: "The Terror archetype works because V4 (Juice) compounds with S5 (Upgrade Verbs)"

**For Game Studies**:
- Formal language for comparing game designs across genres
- Measure "distance" between games via Galois loss on shared axioms
- Archive designs as axiom sets, not just code

---

## Part II: Core Abstractions

### 2.1 GameKernel: Universal Game Axioms

The GameKernel defines axioms that hold across ALL games. These survive radical restructuring (L < 0.10).

```python
@dataclass(frozen=True)
class GameKernel:
    """
    Universal axioms that survive across any game instantiation.

    These are the fixed points of game design—violate them and
    the result is not a game but a broken system.
    """

    # A1: PLAYER AGENCY (L = 0.02)
    # Player's choices must determine outcomes
    # Test: For any outcome O, traceable decision chain exists
    agency: AgencyAxiom

    # A2: ATTRIBUTABLE OUTCOMES (L = 0.05)
    # Every outcome traces to identifiable cause
    # Test: Player articulates cause within 2 seconds
    attribution: AttributionAxiom

    # A3: VISIBLE MASTERY (L = 0.08)
    # Skill development is externally observable
    # Test: Run 10 looks different from Run 1
    mastery: MasteryAxiom

    # A4: COMPOSITIONAL EXPERIENCE (L = 0.03)
    # Moments compose algebraically into arcs
    # Test: Experience quality obeys associativity
    composition: CompositionAxiom

    def validate_implementation(self, impl: GameImplementation) -> ValidationResult:
        """
        Verify an implementation satisfies all kernel axioms.

        Returns ValidationResult with per-axiom pass/fail and evidence.
        """
        results = []
        results.append(self.agency.validate(impl))
        results.append(self.attribution.validate(impl))
        results.append(self.mastery.validate(impl))
        results.append(self.composition.validate(impl))

        return ValidationResult(
            passed=all(r.passed for r in results),
            axiom_results=tuple(results),
            galois_loss=self._compute_kernel_loss(results),
        )

    def _compute_kernel_loss(self, results: list[AxiomResult]) -> float:
        """
        Compute aggregate Galois loss for kernel.

        Kernel loss should be < 0.10 for valid games.
        """
        if not results:
            return 1.0
        return sum(r.loss for r in results) / len(results)


@dataclass(frozen=True)
class AgencyAxiom:
    """
    A1: Player choices determine outcomes.

    Operationalized as: decision_chain(outcome) exists and is non-empty.
    """
    loss: float = 0.02  # Fixed point

    def validate(self, impl: GameImplementation) -> AxiomResult:
        """Check that all outcomes trace to player decisions."""
        outcomes = impl.sample_outcomes(n=100)
        traceable = sum(1 for o in outcomes if o.decision_chain)

        return AxiomResult(
            axiom="A1:AGENCY",
            passed=traceable >= 95,  # 95% must be traceable
            evidence=f"{traceable}/100 outcomes traced to decisions",
            loss=self.loss if traceable >= 95 else 0.5,
        )
```

**Key Insight**: The GameKernel is NOT genre-specific. A puzzle game, an FPS, and a visual novel all satisfy A1-A4. What differs is HOW they satisfy them—that's the specification layer.

### 2.2 GameOperad: Composition Grammar for Mechanics

The GameOperad defines how game mechanics compose. It's the grammar of valid game structures.

```python
GAME_OPERAD = Operad(
    name="GameOperad",

    operations={
        # Sequential: mechanic A then mechanic B
        "sequential": lambda a, b: MechanicSequence(a, b),

        # Parallel: mechanics A and B active simultaneously
        "parallel": lambda a, b: MechanicParallel(a, b),

        # Nested: mechanic B within context of A
        "nested": lambda outer, inner: MechanicNested(outer, inner),

        # Conditional: mechanic A enables mechanic B
        "conditional": lambda trigger, effect: MechanicConditional(trigger, effect),

        # Feedback: output of A feeds input of B
        "feedback": lambda source, sink: MechanicFeedback(source, sink),
    },

    laws=[
        # ASSOCIATIVITY
        Law("assoc_seq", "(A >> B) >> C = A >> (B >> C)",
            "Mechanic sequences are associative"),
        Law("assoc_par", "(A || B) || C = A || (B || C)",
            "Parallel mechanics are associative"),

        # IDENTITY
        Law("identity", "A >> Id = Id >> A = A",
            "Identity mechanic exists (no-op)"),

        # DISTRIBUTION
        Law("distrib", "A >> (B || C) = (A >> B) || (A >> C)",
            "Sequence distributes over parallel"),

        # FEEDBACK COHERENCE
        Law("feedback_coherent", "feedback(A, B) preserves A.output_type = B.input_type",
            "Feedback loops are type-safe"),

        # CONTRAST PRESERVATION (from Experience Quality)
        Law("contrast_mono", "contrast(A >> B) >= max(contrast(A), contrast(B)) - epsilon",
            "Composition preserves or increases contrast"),
    ],
)


@dataclass(frozen=True)
class MechanicComposition:
    """
    A composed game mechanic.

    Every mechanic has:
    - Verbs: what the player can DO (agency)
    - Tells: what the player can SEE (attribution)
    - Curves: how difficulty/reward evolve (mastery)
    - Transitions: how it connects to other mechanics (composition)
    """

    name: str
    verbs: tuple[str, ...]          # Player actions
    tells: tuple[str, ...]          # Visual/audio feedback
    input_type: str                  # What triggers this mechanic
    output_type: str                 # What this mechanic produces
    contrast_poles: tuple[str, str]  # The oscillation this creates

    # Galois layer (how stable is this mechanic?)
    galois_loss: float

    def compose_sequential(self, other: "MechanicComposition") -> "MechanicComposition":
        """Compose this mechanic sequentially with another."""
        assert self.output_type == other.input_type, \
            f"Type mismatch: {self.output_type} vs {other.input_type}"

        return MechanicComposition(
            name=f"{self.name}_then_{other.name}",
            verbs=self.verbs + other.verbs,
            tells=self.tells + other.tells,
            input_type=self.input_type,
            output_type=other.output_type,
            contrast_poles=(self.contrast_poles[0], other.contrast_poles[1]),
            galois_loss=max(self.galois_loss, other.galois_loss),
        )
```

**Example: wasm-survivors Operad Instantiation**

```python
WASM_SURVIVORS_OPERAD = GAME_OPERAD.instantiate({
    # Core mechanics
    "move": MechanicComposition(
        name="hornet_movement",
        verbs=("dash", "hover", "brake"),
        tells=("position_trail", "dash_particles", "hover_glow"),
        input_type="player_input",
        output_type="position_state",
        contrast_poles=("speed", "stillness"),
        galois_loss=0.25,  # Stable mechanic
    ),

    "attack": MechanicComposition(
        name="hornet_attack",
        verbs=("strike", "execute", "rampage"),
        tells=("damage_flash", "kill_particles", "screen_shake"),
        input_type="position_state",
        output_type="damage_event",
        contrast_poles=("predator", "prey"),
        galois_loss=0.30,
    ),

    "upgrade": MechanicComposition(
        name="build_choice",
        verbs=("choose", "synergize", "specialize"),
        tells=("choice_ui", "synergy_glow", "build_identity"),
        input_type="xp_threshold",
        output_type="capability_delta",
        contrast_poles=("learning", "knowing"),
        galois_loss=0.45,  # More variable
    ),

    "the_ball": MechanicComposition(
        name="collective_threat",
        verbs=("escape", "find_gap", "survive"),
        tells=("formation_lines", "heat_shimmer", "silence"),
        input_type="coordination_level",
        output_type="death_or_escape",
        contrast_poles=("god_of_death", "cornered_prey"),
        galois_loss=0.50,  # Specification layer
    ),
})
```

### 2.3 GameSheaf: Local Mechanics to Global Coherence

The GameSheaf ensures that local mechanical decisions produce globally coherent experiences.

```python
@dataclass
class GameSheaf:
    """
    Sheaf structure for game coherence.

    Local views (individual mechanics, moments, player actions) must
    glue together into a consistent global experience.

    This is the Experience Quality Operad applied to game design.
    """

    algebra: QualityAlgebra  # Domain-specific quality measure

    # Local sections: quality of individual moments
    local_sections: dict[str, ExperienceQuality]

    # Gluing conditions: how locals must agree
    overlap_conditions: list[GluingCondition]

    def check_coherence(self) -> CoherenceResult:
        """
        Verify that local sections glue into global coherence.

        Checks:
        1. All overlaps satisfy gluing conditions
        2. Global quality is achievable from locals
        3. No contradictory quality requirements
        """
        violations = []

        for condition in self.overlap_conditions:
            if not condition.satisfied(self.local_sections):
                violations.append(condition)

        return CoherenceResult(
            coherent=len(violations) == 0,
            violations=violations,
            global_quality=self._compute_global(),
        )

    def _compute_global(self) -> ExperienceQuality:
        """Compose local qualities into global."""
        if not self.local_sections:
            return ExperienceQuality.zero(self.algebra.name, len(self.algebra.voices))

        # Sequential composition of all sections
        qualities = list(self.local_sections.values())
        result = qualities[0]
        for q in qualities[1:]:
            result = sequential_compose(result, q)

        return result


@dataclass(frozen=True)
class GluingCondition:
    """
    A condition that must hold for local sections to glue.

    Example: "If POWER phase ends, CRISIS must be reachable within 3 waves"
    """

    name: str
    section_a: str
    section_b: str
    condition: Callable[[ExperienceQuality, ExperienceQuality], bool]
    violation_message: str

    def satisfied(self, sections: dict[str, ExperienceQuality]) -> bool:
        """Check if gluing condition holds."""
        if self.section_a not in sections or self.section_b not in sections:
            return True  # Missing sections are vacuously satisfied

        return self.condition(sections[self.section_a], sections[self.section_b])
```

**Example: wasm-survivors Gluing Conditions**

```python
WASM_SURVIVORS_SHEAF = GameSheaf(
    algebra=WASM_QUALITY_ALGEBRA,
    local_sections={},  # Populated at runtime
    overlap_conditions=[
        # Arc coherence: phases must connect properly
        GluingCondition(
            name="power_to_flow",
            section_a="power_phase",
            section_b="flow_phase",
            condition=lambda a, b: a.arc_coverage > 0.3 or b.arc_coverage > 0.5,
            violation_message="POWER must establish before FLOW",
        ),

        GluingCondition(
            name="flow_to_crisis",
            section_a="flow_phase",
            section_b="crisis_phase",
            condition=lambda a, b: (1 - a.contrast) < b.contrast,  # Contrast increases
            violation_message="Transition to CRISIS must increase contrast",
        ),

        # Dignity preservation: death must feel earned
        GluingCondition(
            name="crisis_to_tragedy",
            section_a="crisis_phase",
            section_b="tragedy_phase",
            condition=lambda a, b: a.floor_passed and b.voice_verdicts[2],  # Dignity voice
            violation_message="TRAGEDY requires DIGNITY floor (V3)",
        ),

        # Voice continuity: player voice must approve across phases
        GluingCondition(
            name="player_voice_continuity",
            section_a="any",
            section_b="any",
            condition=lambda a, b: a.voice_verdicts[-1] or b.voice_verdicts[-1],
            violation_message="Player voice must approve at least one phase",
        ),
    ],
)
```

### 2.4 GameWitness: Evidence Accumulation for Quality

The GameWitness integrates ASHC evidence accumulation with the Experience Quality Operad.

```python
@dataclass
class GameWitness:
    """
    Witness system for game quality evidence.

    Every game session produces marks. Marks accumulate into traces.
    Traces compress into crystals. Crystals prove spec-impl equivalence.
    """

    # Evidence compiler (from ASHC)
    compiler: EvidenceCompiler

    # Quality algebra (from Experience Quality Operad)
    algebra: QualityAlgebra

    # Accumulated evidence
    runs: list[GameRun] = field(default_factory=list)
    crystals: list[QualityCrystal] = field(default_factory=list)

    # Galois loss tracking
    spec_impl_loss: float = 1.0  # Starts uncertain

    async def witness_run(self, run: GameRun) -> QualityMark:
        """
        Witness a single game run.

        Creates a mark capturing:
        - Quality measurements (C, A, V, F)
        - Axiomatic compliance (A1-A4)
        - Causal attribution (why this quality?)
        """
        # Measure quality
        quality = await measure_quality(run.experience, self.algebra)

        # Verify kernel axioms
        kernel_result = GAME_KERNEL.validate_implementation(run)

        # Create mark
        mark = QualityMark(
            quality=quality,
            experience_id=run.run_id,
            experience_type="run",
            algebra_name=self.algebra.name,
            duration_seconds=run.duration,
            bottleneck=identify_bottleneck(quality),
            recommendation=generate_recommendation(quality, self.algebra),
            kernel_compliance=kernel_result,
        )

        self.runs.append(run)
        await emit_mark(mark)

        return mark

    async def crystallize_evidence(self, n_runs: int = 10) -> QualityCrystal:
        """
        Compress recent runs into a quality crystal.

        The crystal is the proof that spec and impl are equivalent
        (or divergent) with measured confidence.
        """
        recent_runs = self.runs[-n_runs:]
        marks = [run.mark for run in recent_runs if run.mark]

        crystal = await crystallize_quality(marks, self.algebra)

        # Update Galois loss estimate
        self.spec_impl_loss = self._estimate_galois_loss(crystal)

        self.crystals.append(crystal)
        return crystal

    def _estimate_galois_loss(self, crystal: QualityCrystal) -> float:
        """
        Estimate Galois loss from quality crystal.

        L(spec) = d(spec, C(R(spec)))

        Where R is implementation (renders to gameplay)
        And C is crystallization (compresses to quality summary)

        High quality + low variance = low loss (stable spec)
        Low quality OR high variance = high loss (spec-impl divergence)
        """
        quality = crystal.overall_quality
        variance = self._compute_quality_variance(crystal)

        # Loss increases with low quality and high variance
        loss = (1 - quality) * 0.6 + variance * 0.4

        return min(1.0, max(0.0, loss))

    def _compute_quality_variance(self, crystal: QualityCrystal) -> float:
        """Compute variance in quality across source marks."""
        if crystal.source_mark_count < 2:
            return 0.5  # Uncertain with few samples

        # Use peaks and troughs to estimate variance
        peak_avg = sum(p.quality_score for p in crystal.quality_peaks) / len(crystal.quality_peaks)
        trough_avg = sum(t.quality_score for t in crystal.quality_troughs) / len(crystal.quality_troughs)

        return (peak_avg - trough_avg) / 2  # Normalized to [0, 1]
```

---

## Part III: The Generation Pipeline

### 3.1 Pipeline Overview

```
    AXIOMS          VALUES          SPEC            IMPL           EVIDENCE        VERIFY
  (L < 0.10)     (L < 0.35)     (L < 0.70)       (L ≥ 0.70)      (runs)         (crystal)
       │              │              │               │              │              │
       │              │              │               │              │              │
   A1-A4  ───────► V1-V5 ───────► S1-S6 ───────► Code/Assets ──► Runs ───────► Crystal
       │              │              │               │              │              │
       │              │              │               │              │              │
  GameKernel    GameValues    GameSpec      GameImplementation   GameEvidence    Verified
       │              │              │               │              │              │
       │              │              │               │              │              │
       ▼              ▼              ▼               ▼              ▼              ▼
   MUST hold      SHOULD hold    MAY diverge     WILL vary      Accumulates    Gates release
```

### 3.2 Stage 1: Axioms (GameKernel)

**What ASHC Provides**: Validation that axioms are internally consistent and sufficient.

```python
async def validate_axiom_set(axioms: list[Axiom]) -> AxiomValidation:
    """
    Use ASHC to validate axiom set is consistent.

    Checks:
    1. No contradictions (axioms don't conflict)
    2. Sufficient coverage (can derive necessary values)
    3. Minimal (no redundant axioms)
    """
    # Generate test implementations from axioms
    test_specs = generate_minimal_specs(axioms, n=10)

    # Compile each to find contradictions
    results = []
    for spec in test_specs:
        output = await evidence_compiler.compile(spec)
        results.append(output)

    # Check for consistency
    pass_rates = [r.evidence.pass_rate for r in results]

    return AxiomValidation(
        consistent=min(pass_rates) > 0.8,
        coverage=compute_axiom_coverage(axioms, results),
        redundancy=detect_redundant_axioms(axioms),
        galois_loss=sum(r.evidence.galois_loss or 0 for r in results) / len(results),
    )
```

**Galois Loss Gate**: L < 0.10 for axiom layer. If loss exceeds this, axioms need refinement.

### 3.3 Stage 2: Values (Derived Principles)

**What ASHC Provides**: Verification that values derive from axioms.

```python
async def derive_values(kernel: GameKernel, domain: str) -> list[GameValue]:
    """
    Derive values from axioms for a specific domain.

    Uses ASHC to verify derivation is valid.
    """
    # Generate candidate values
    candidates = generate_value_candidates(kernel, domain)

    # Verify each derives from axioms
    valid_values = []
    for candidate in candidates:
        # Check derivation chain exists
        derivation = find_derivation_chain(candidate, kernel)

        if derivation:
            # Use ASHC to verify derivation empirically
            evidence = await verify_derivation(derivation)

            if evidence.pass_rate > 0.85:
                valid_values.append(GameValue(
                    name=candidate.name,
                    statement=candidate.statement,
                    derivation=derivation,
                    galois_loss=evidence.galois_loss or 0.3,
                ))

    return valid_values
```

**Galois Loss Gate**: L < 0.35 for value layer. Values with higher loss are unstable.

### 3.4 Stage 3: Specifications (Implementation Choices)

**What ASHC Provides**: Generation of valid specifications from values.

```python
async def generate_specifications(
    values: list[GameValue],
    theme: str,
    style: str,
) -> GameSpec:
    """
    Generate game specification from values with theme/style.

    Each specification is ONE valid instantiation of the values.
    Multiple specifications can satisfy the same values.
    """
    # Generate candidate mechanics for each value
    mechanics = {}
    for value in values:
        candidates = generate_mechanic_candidates(value, theme, style)

        # Use ASHC adaptive compilation to find best
        best = None
        best_score = 0

        for candidate in candidates:
            evidence = await adaptive_compiler.compile(
                spec=candidate.to_spec_string(),
                tier=ConfidenceTier.UNCERTAIN,
            )

            if evidence.posterior_mean > best_score:
                best = candidate
                best_score = evidence.posterior_mean

        mechanics[value.name] = best

    return GameSpec(
        theme=theme,
        style=style,
        values=values,
        mechanics=mechanics,
        galois_loss=sum(m.galois_loss for m in mechanics.values()) / len(mechanics),
    )
```

**Galois Loss Gate**: L < 0.70 for specification layer. Higher loss means more freedom to diverge.

### 3.5 Stage 4: Implementation

**What ASHC Provides**: Evidence accumulation during implementation.

```python
async def implement_spec(spec: GameSpec) -> ASHCOutput:
    """
    Compile spec to implementation with evidence.

    Uses EvidenceCompiler to generate N variations and
    accumulate evidence about spec-impl equivalence.
    """
    # Prepare implementation prompt
    prompt = spec.to_implementation_prompt()

    # Compile with evidence accumulation
    output = await evidence_compiler.compile(
        spec=prompt,
        n_variations=20,
        test_code=spec.generate_test_code(),
        run_tests=True,
        run_types=True,
        run_lint=True,
    )

    return output
```

### 3.6 Stage 5: Evidence

**What ASHC Provides**: Bayesian confidence in spec-impl equivalence.

```python
async def accumulate_evidence(
    impl: GameImplementation,
    spec: GameSpec,
    n_sessions: int = 100,
) -> Evidence:
    """
    Accumulate evidence from play sessions.

    Each session generates marks. Marks accumulate into traces.
    Traces compress into crystals. Crystals prove equivalence.
    """
    runs = []

    for i in range(n_sessions):
        # Simulate play session
        session = await impl.run_session()

        # Witness quality
        mark = await witness.witness_run(session)

        # Create run record
        run = Run(
            run_id=session.id,
            spec_hash=spec.hash,
            implementation=impl.code_hash,
            test_results=session.test_results,
            type_results=session.type_results,
            lint_results=session.lint_results,
            witnesses=(mark.to_witness_result(),),
        )
        runs.append(run)

    # Build evidence corpus
    evidence = Evidence(
        runs=tuple(runs),
        spec_content=spec.to_string(),
        best_impl_content=impl.best_implementation(),
    )

    # Compute Galois loss
    galois_loss = compute_galois_loss(spec, evidence)
    evidence = evidence.with_galois_loss(galois_loss)

    return evidence
```

### 3.7 Stage 6: Verification

**What ASHC Provides**: Final verification and release gating.

```python
async def verify_release(
    spec: GameSpec,
    impl: GameImplementation,
    evidence: Evidence,
) -> VerificationResult:
    """
    Verify implementation is ready for release.

    Checks:
    1. Galois coherence >= 0.85 (structure preservation)
    2. At least 10 runs with high pass rate
    3. All kernel axioms satisfied
    4. Quality above floor thresholds
    """
    # Create ASHC output
    output = ASHCOutput(
        executable=impl.code,
        evidence=evidence,
        spec_hash=spec.hash,
    )

    # Check verification
    verified = output.is_verified
    galois_verified = output.galois_verified

    # Check kernel
    kernel_valid = all(
        run.kernel_compliance.passed
        for run in evidence.runs
        if hasattr(run, 'kernel_compliance')
    )

    # Check quality
    crystal = await witness.crystallize_evidence()
    quality_passed = crystal.overall_quality >= 0.7

    return VerificationResult(
        release_ready=verified and galois_verified and kernel_valid and quality_passed,
        confidence=output.confidence,
        galois_loss=evidence.galois_loss,
        kernel_compliance=kernel_valid,
        quality_score=crystal.overall_quality,
        recommendations=generate_release_recommendations(output, crystal),
    )
```

---

## Part IV: Concrete Examples

### 4.1 How wasm-survivors Fits the Framework

**Layer 0: Axioms (GameKernel)**
```
A1: PLAYER AGENCY → Player's dash, attack, upgrade choices determine survival
A2: ATTRIBUTABLE OUTCOMES → "THE BALL got me because I ignored scouts"
A3: VISIBLE MASTERY → Run 10 shows 3x survival time vs Run 1
A4: COMPOSITIONAL EXPERIENCE → Moments compose: kill → XP → upgrade → synergy → death
```

**Layer 1: Values (Derived)**
```
V1: CONTRAST (L=0.15) → God of Death ↔ Cornered Prey oscillation
V2: ARC (L=0.18) → POWER → FLOW → CRISIS → TRAGEDY progression
V3: DIGNITY (L=0.22) → "They earned it" death, not "random BS"
V4: JUICE (L=0.28) → Screen shake, particles, freeze frames on kills
V5: WITNESSED (L=0.32) → Colony learns patterns, not surveillance
```

**Layer 2: Specifications**
```
S1: THE BALL (L=0.45) → Signature collective threat mechanic
S2: TRAGEDY (L=0.55) → Player always loses; that's the point
S3: HORNET (L=0.48) → Japanese giant hornet as predator fantasy
S4: SEVEN CONTRASTS (L=0.52) → Power/Tempo/Stance/Humility/Sound/Role/Knowledge
S5: UPGRADE ARCHETYPES (L=0.58) → Executioner/Survivor/Skirmisher/Terror/Assassin/Berserker
S6: BEE TAXONOMY (L=0.55) → Worker/Scout/Guard/Propolis/Royal Guard
```

**Layer 3: Tuning**
```
T1: Dash i-frames = 0.12s (range: 0.08-0.20s)
T2: Ball forming duration = 10s (range: 8-15s)
T3: Screen shake (kill) = 3px
...
```

### 4.2 Generating "space-colony-survivors"

Starting from the SAME GameKernel (A1-A4), generate a different game:

**Theme**: Space colony defending against alien swarm
**Style**: sci-fi, neon aesthetic, electronic soundtrack

**Generated Values (same as wasm-survivors)**:
```
V1: CONTRAST → Colony defender ↔ Overwhelmed last stand
V2: ARC → ARRIVAL → ESTABLISHMENT → SIEGE → EVACUATION
V3: DIGNITY → "The colony survived because of my sacrifice"
V4: JUICE → Laser trails, explosion particles, slow-mo on kills
V5: WITNESSED → Alien hive learns tactics, colonists remember
```

**Generated Specifications (DIFFERENT from wasm-survivors)**:
```
S1: THE SWARM MIND (L=0.45) → Aliens form coordinated attack patterns
S2: SACRIFICE (L=0.55) → Player can win by buying time for evacuation
S3: MECH PILOT (L=0.48) → Player controls defense mech, not individual
S4: FIVE CONTRASTS (L=0.52) → Power/Tempo/Hope/Fear/Unity
S5: UPGRADE MODULES (L=0.58) → Shield/Weapons/Speed/Sensors/Power
S6: ALIEN TAXONOMY (L=0.55) → Drone/Scout/Hunter/Bomber/Queen
```

**Key Insight**: SAME axioms, SAME values, DIFFERENT specifications, DIFFERENT tuning = **isomorphic game** that satisfies all quality requirements.

### 4.3 Detecting Spec-Impl Divergence

The framework detects when implementation drifts from spec:

```python
# During development, monitor Galois loss
async def monitor_drift(impl: GameImplementation, spec: GameSpec):
    """
    Continuously monitor for spec-impl drift.

    Alerts when:
    1. Galois loss exceeds layer threshold
    2. Kernel axioms start failing
    3. Quality drops below floor
    """
    evidence = await accumulate_evidence(impl, spec, n_sessions=50)

    # Check per-layer drift
    drift_alerts = []

    # Axiom drift (should never happen)
    if evidence.galois_loss > 0.10:
        for run in evidence.runs:
            if not run.kernel_compliance.passed:
                drift_alerts.append(DriftAlert(
                    layer="axiom",
                    severity="critical",
                    message=f"Axiom violation: {run.kernel_compliance.violations}",
                    recommendation="Implementation breaks fundamental contract",
                ))

    # Value drift (concerning)
    if evidence.galois_loss > 0.35:
        drift_alerts.append(DriftAlert(
            layer="value",
            severity="warning",
            message=f"Value drift detected: L={evidence.galois_loss:.2f}",
            recommendation="Implementation diverging from design values",
        ))

    # Spec drift (acceptable if values hold)
    if evidence.galois_loss > 0.70:
        drift_alerts.append(DriftAlert(
            layer="spec",
            severity="info",
            message=f"Spec drift detected: L={evidence.galois_loss:.2f}",
            recommendation="Implementation may be evolving beyond original spec",
        ))

    return DriftReport(
        galois_loss=evidence.galois_loss,
        alerts=drift_alerts,
        recommendation=generate_drift_recommendation(drift_alerts),
    )
```

**Example Drift Detection**:
```
Session 42 Analysis:
- Galois Loss: 0.38 (Value tier threshold exceeded)
- Axioms: All passing (A1-A4 ✓)
- Values: V3 (Dignity) failing at 65%
  - "They earned it" sentiment: 52% (target: 80%)
  - Death attribution time: 3.2s (target: <2s)

ALERT: Value drift on V3:DIGNITY
Cause: Recent change to death screen removed causal chain display
Recommendation: Restore "How you died" UI element
```

---

## Part V: Implementation Roadmap

### 5.1 Phase 1: Extract GameKernel from wasm-survivors (Weeks 1-2)

**Goal**: Formalize the four axioms as testable properties.

**Tasks**:
1. Define `AgencyAxiom`, `AttributionAxiom`, `MasteryAxiom`, `CompositionAxiom` dataclasses
2. Implement validation methods for each axiom
3. Create test suite that verifies wasm-survivors satisfies kernel
4. Document axiom derivation chains (what evidence supports each?)

**Exit Criteria**:
- [ ] All four axioms have Python implementations
- [ ] wasm-survivors passes kernel validation with 95%+ compliance
- [ ] Documentation shows axiom derivation from player experience
- [ ] Galois loss estimate for kernel: L < 0.10

**Galois Loss Target**: L < 0.08 for kernel extraction

### 5.2 Phase 2: Build GameOperad for Mechanic Composition (Weeks 3-4)

**Goal**: Define the grammar of valid mechanic compositions.

**Tasks**:
1. Implement `GAME_OPERAD` with five composition operations
2. Extract wasm-survivors mechanics as `MechanicComposition` instances
3. Verify operad laws hold (associativity, identity, distribution)
4. Add contrast preservation law verification

**Exit Criteria**:
- [ ] All five composition operations implemented
- [ ] wasm-survivors mechanics expressible in operad
- [ ] Operad law tests passing
- [ ] Can compose new mechanics from existing ones

**Galois Loss Target**: L < 0.25 for operad (specification tier)

### 5.3 Phase 3: Integrate ASHC Evidence Pipeline (Weeks 5-6)

**Goal**: Connect evidence accumulation to quality measurement.

**Tasks**:
1. Create `GameWitness` class integrating `EvidenceCompiler` + `QualityAlgebra`
2. Implement `witness_run` method for play sessions
3. Implement `crystallize_evidence` for compression
4. Add Galois loss computation from crystals

**Exit Criteria**:
- [ ] Play sessions generate quality marks
- [ ] Marks accumulate into traces
- [ ] Traces compress into crystals
- [ ] Galois loss computed from evidence

**Galois Loss Target**: Evidence pipeline achieves 85%+ equivalence score

### 5.4 Phase 4: Create Generation CLI (Weeks 7-8)

**Goal**: Build user-facing generation interface.

**Tasks**:
1. Implement `kg game generate` command
2. Support `--theme`, `--style`, `--axioms` flags
3. Add `kg game verify` for spec-impl verification
4. Add `kg game drift` for continuous monitoring

**CLI Interface**:
```bash
# Generate new game from axioms
kg game generate --theme "underwater" --style "roguelike" --axioms kernel.yaml

# Verify implementation against spec
kg game verify --spec game_spec.md --impl src/

# Monitor for drift during development
kg game drift --spec game_spec.md --impl src/ --watch
```

**Exit Criteria**:
- [ ] Can generate valid game spec from axioms + theme
- [ ] Can verify implementation against spec
- [ ] Can detect and report drift
- [ ] Documentation for all CLI commands

**Galois Loss Target**: Generated specs have L < 0.70

---

## Part VI: Success Criteria

### 6.1 Galois Coherence Thresholds

| Layer | Loss Threshold | Meaning | Measurement |
|-------|---------------|---------|-------------|
| **Axiom** | L < 0.10 | Fixed points survive restructuring | Kernel validation pass rate |
| **Value** | L < 0.35 | Derived principles hold | Quality algebra voice approval |
| **Spec** | L < 0.70 | Implementation choices are valid | Evidence compiler pass rate |
| **Tuning** | L ≥ 0.70 | Parameters vary freely | N/A (no verification needed) |

### 6.2 Evidence Volume Requirements

| Stage | Minimum Runs | Confidence Target | Stopping Rule |
|-------|--------------|-------------------|---------------|
| **Axiom Validation** | 50 | 95% | n_diff = 3 |
| **Value Derivation** | 20 | 85% | n_diff = 2 |
| **Spec Generation** | 10 | 80% | n_diff = 2 |
| **Impl Verification** | 100 | 90% | Bayesian 0.95 |

### 6.3 Regeneration Test

The ultimate success criterion: **delete the implementation, regenerate, verify isomorphism**.

```python
async def regeneration_test(spec: GameSpec) -> RegenerationResult:
    """
    The acid test: can we regenerate an equivalent game?

    1. Generate implementation A from spec
    2. Accumulate evidence for A
    3. Delete A
    4. Generate implementation B from SAME spec
    5. Accumulate evidence for B
    6. Verify A and B are isomorphic (same quality characteristics)
    """
    # Generate first implementation
    impl_a = await generate_implementation(spec)
    evidence_a = await accumulate_evidence(impl_a, spec, n_sessions=100)

    # Generate second implementation (fresh)
    impl_b = await generate_implementation(spec)
    evidence_b = await accumulate_evidence(impl_b, spec, n_sessions=100)

    # Check isomorphism
    isomorphic = check_isomorphism(evidence_a, evidence_b)

    return RegenerationResult(
        isomorphic=isomorphic,
        quality_a=evidence_a.average_verification_score,
        quality_b=evidence_b.average_verification_score,
        quality_diff=abs(evidence_a.average_verification_score - evidence_b.average_verification_score),
        galois_loss_a=evidence_a.galois_loss,
        galois_loss_b=evidence_b.galois_loss,
    )


def check_isomorphism(a: Evidence, b: Evidence, tolerance: float = 0.15) -> bool:
    """
    Two implementations are isomorphic if:
    1. Both satisfy kernel axioms
    2. Quality scores within tolerance
    3. Galois loss within tolerance
    4. Same arc phase coverage
    """
    quality_match = abs(a.average_verification_score - b.average_verification_score) < tolerance
    loss_match = abs((a.galois_loss or 0) - (b.galois_loss or 0)) < tolerance

    return quality_match and loss_match
```

**Pass Criteria**:
- Quality difference < 15%
- Galois loss difference < 0.10
- Both implementations satisfy kernel
- Regeneration completes in < 1 hour

---

## Part VII: Open Questions

### 7.1 What Axioms Are Universal vs. Genre-Specific?

**Current Hypothesis**: A1-A4 are universal (all interactive games). Genre-specific axioms exist at the value layer.

**Questions to Resolve**:
- Do visual novels satisfy A1 (Agency)? Reading is a choice, but is it determining?
- Do puzzle games satisfy A4 (Composition)? Single-puzzle games may not compose.
- What about multiplayer? Does A2 (Attribution) apply when other players cause outcomes?

**Research Needed**: Analysis of 10+ game genres against kernel axioms.

### 7.2 How to Handle Procedural Content Generation?

**Challenge**: PCG produces infinite variations. How do we verify spec-impl equivalence?

**Proposed Solution**: Verify the GENERATOR satisfies axioms, not individual outputs.

```python
async def verify_pcg_generator(generator: PCGGenerator, spec: GameSpec) -> PCGVerification:
    """
    Verify a procedural content generator satisfies spec.

    Sample N outputs, verify each, compute aggregate.
    """
    samples = [generator.generate() for _ in range(100)]

    results = []
    for sample in samples:
        result = await verify_content(sample, spec)
        results.append(result)

    return PCGVerification(
        pass_rate=sum(r.passed for r in results) / len(results),
        galois_loss=sum(r.loss for r in results) / len(results),
        worst_sample=min(results, key=lambda r: r.score),
        best_sample=max(results, key=lambda r: r.score),
    )
```

### 7.3 Integration with sprite-procedural-taste-lab

**Opportunity**: sprite-procedural-taste-lab generates visual assets. The Game Meta-Framework generates game mechanics. Together they could generate COMPLETE games.

**Integration Points**:
1. Theme from framework → style constraints for sprite generation
2. Mechanic requirements → sprite type requirements (enemies, power-ups, effects)
3. Quality algebra → taste evaluation for sprites

**Open Questions**:
- How to ensure sprite style matches game style?
- How to verify sprite quality contributes to game quality?
- How to handle the combinatorial explosion (N mechanics × M sprites)?

### 7.4 Handling Emergent Gameplay

**Challenge**: Players discover gameplay patterns designers didn't anticipate. How do we verify these?

**Proposed Approach**: Emergent gameplay is valid if it satisfies kernel axioms, even if not in spec.

```python
def classify_emergent_gameplay(behavior: PlayerBehavior, spec: GameSpec) -> EmergentClassification:
    """
    Classify emergent player behavior.

    Returns:
    - INTENDED: In spec, working as designed
    - EMERGENT_VALID: Not in spec, but satisfies axioms
    - EMERGENT_INVALID: Not in spec, violates axioms
    - EXPLOIT: Satisfies axioms but undermines design intent
    """
    in_spec = behavior.pattern in spec.expected_behaviors
    satisfies_kernel = GAME_KERNEL.validate_behavior(behavior)

    if in_spec:
        return EmergentClassification.INTENDED
    elif satisfies_kernel.passed:
        # Check if it undermines design intent
        undermines = check_design_intent(behavior, spec)
        if undermines:
            return EmergentClassification.EXPLOIT
        return EmergentClassification.EMERGENT_VALID
    else:
        return EmergentClassification.EMERGENT_INVALID
```

---

## Appendix A: Cross-References

| Document | Relevance |
|----------|-----------|
| `pilots/wasm-survivors-game/PROTO_SPEC.md` | Source spec with axiom/value/spec layers |
| `impl/claude/protocols/ashc/evidence.py` | Evidence accumulation implementation |
| `impl/claude/protocols/ashc/adaptive.py` | Bayesian adaptive stopping |
| `impl/claude/protocols/ashc/economy.py` | Economic accountability layer |
| `spec/theory/experience-quality-operad.md` | Quality measurement framework |
| `plans/pilot-specification-protocol.md` | Spec stratification protocol |
| `plans/enlightened-synthesis/00-master-synthesis.md` | Master vision |

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Galois Loss** | L(P) = d(P, C(R(P))) — distance between spec and reconstituted spec |
| **GameKernel** | Universal axioms (A1-A4) that hold for all games |
| **GameOperad** | Composition grammar for game mechanics |
| **GameSheaf** | Coherence structure ensuring local → global consistency |
| **GameWitness** | Evidence accumulation system for quality |
| **Isomorphic Games** | Games that satisfy same axioms/values with different specs |
| **Regeneration Test** | Delete impl, regenerate, verify isomorphism |

---

*"The spec defines what CAN be generated, not what MUST be generated."*

*"Daring, bold, creative, opinionated but not gaudy."*

**Filed**: 2026-01-10
**Lines**: ~750
**Status**: Draft Specification
