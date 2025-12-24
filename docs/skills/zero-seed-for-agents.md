# Zero Seed for Agents

> *"The proof IS the decision. The loss IS the witness."*

This skill teaches agents (subagents, pipelines, scripts) how to use Zero Seed technology for rigorous epistemological grounding.

---

## Why Agents Should Use Zero Seed

1. **Rigorous Grounding** — Decisions trace to axioms, not vibes
2. **Quantitative Coherence** — Proofs have measurable quality (Galois loss)
3. **Contradiction Detection** — Super-additive loss identifies clashing views
4. **Traceability** — Every decision links to witness marks
5. **Navigation** — Loss gradients guide toward coherence

---

## Core Concepts

### The Seven Layers

| Layer | Name | Content | Loss Behavior |
|-------|------|---------|---------------|
| **L1** | Axioms | Entity, Morphism, Galois Ground | L = 0 (fixed point) |
| **L2** | Values | Constitution principles | L < 0.01 |
| **L3** | Goals | What we want to achieve | L < 0.1 |
| **L4** | Specs | How we'll achieve it | L < 0.3 |
| **L5** | Execution | Implementation details | L < 0.5 |
| **L6** | Reflection | Learnings and insights | L < 0.7 |
| **L7** | Representation | Surface projections | L variable |

### Galois Loss

Measures how much meaning survives modularization:

```
L(P) = d(P, C(R(P)))

where:
  R = restructure (compress into modules)
  C = reconstitute (expand back)
  d = semantic distance
```

**Interpretation**:
- `L = 0`: Perfect coherence (axiom)
- `L < 0.3`: Good coherence (empirical tier)
- `L > 0.7`: Chaotic (needs revision)

### Toulmin Proofs

For L3+ claims, construct:

```python
@dataclass
class Proof:
    data: str           # Evidence
    warrant: str        # Reasoning
    claim: str          # Conclusion
    backing: str        # Support for warrant
    qualifier: str      # Confidence ("definitely", "probably")
    rebuttals: tuple    # Defeaters ("unless...")
    tier: EvidenceTier  # CATEGORICAL, EMPIRICAL, AESTHETIC, SOMATIC
```

### Super-Additive Loss (Contradiction)

Two claims contradict when combining them loses more than sum:

```python
def is_contradiction(A, B, tolerance=0.1):
    return L(A + B) > L(A) + L(B) + tolerance
```

**Interpretation**:
- Positive excess: Contradiction (views clash)
- Zero excess: Independent (views coexist)
- Negative excess: Synergistic (views reinforce)

---

## Operations Reference

### 1. Ground Decision in Axioms

Before making decisions, verify grounding:

```python
async def ground_decision(claim: str) -> GroundingResult:
    """
    Check claim against L1-L2 foundations.

    Returns:
        GroundingResult with axiom links and loss estimate
    """
    # Check A1: Entity (everything representable)
    entity_ok = is_representable(claim)

    # Check A2: Morphism (composition preserved)
    composition_ok = preserves_composition(claim)

    # Check G: Galois Ground (loss measurable)
    loss = await compute_galois_loss(claim)

    # Check Constitution principles
    principles = identify_relevant_principles(claim)

    return GroundingResult(
        claim=claim,
        entity_grounded=entity_ok,
        composition_grounded=composition_ok,
        galois_loss=loss,
        principles=principles,
        tier=classify_by_loss(loss)
    )
```

**Agent Usage**:

```python
# Ground before deciding
grounding = await ground_decision("Use SSE for real-time updates")

if grounding.tier in [EvidenceTier.CATEGORICAL, EvidenceTier.EMPIRICAL]:
    # Safe to proceed
    await make_decision(claim)
else:
    # Needs more support
    await request_backing(claim)
```

### 2. Construct Toulmin Proof

For L3+ claims, build structured proof:

```python
async def construct_proof(
    claim: str,
    evidence: list[str],
    reasoning: str
) -> GaloisWitnessedProof:
    """
    Build Toulmin proof with Galois annotations.
    """
    proof = Proof(
        data="\n".join(evidence),
        warrant=reasoning,
        claim=claim,
        backing=await find_backing(reasoning),
        qualifier=estimate_confidence(evidence),
        rebuttals=await generate_rebuttals(claim, reasoning),
        tier=EvidenceTier.EMPIRICAL  # Will be refined
    )

    # Compute Galois loss
    loss = await galois_loss(proof)
    decomposition = await compute_loss_decomposition(proof)

    return GaloisWitnessedProof(
        **asdict(proof),
        galois_loss=loss,
        coherence=1.0 - loss,
        loss_decomposition=decomposition,
        ghost_alternatives=await generate_alternatives(proof)
    )
```

**Agent Usage**:

```python
# Construct proof for spec change
proof = await construct_proof(
    claim="Add caching layer to API",
    evidence=[
        "API latency is 200ms average",
        "85% of requests are repeated within 5 minutes",
        "Redis available in infrastructure"
    ],
    reasoning="High repeat rate makes caching effective"
)

if proof.coherence > 0.7:
    await commit_change(proof)
    await witness_decision(proof)
else:
    # Strengthen weak components
    weak = max(proof.loss_decomposition, key=proof.loss_decomposition.get)
    await request_strengthening(weak)
```

### 3. Detect Contradiction

When two views clash:

```python
async def detect_contradiction(
    view_a: str,
    view_b: str,
    tolerance: float = 0.1
) -> ContradictionAnalysis:
    """
    Detect contradiction via super-additive Galois loss.
    """
    loss_a = await galois_loss(view_a)
    loss_b = await galois_loss(view_b)
    loss_combined = await galois_loss(f"{view_a}\n\n{view_b}")

    super_additivity = loss_combined - (loss_a + loss_b)

    return ContradictionAnalysis(
        view_a=view_a,
        view_b=view_b,
        loss_a=loss_a,
        loss_b=loss_b,
        loss_combined=loss_combined,
        super_additivity=super_additivity,
        contradicts=super_additivity > tolerance,
        severity=classify_severity(super_additivity),
        ghost_alternatives=await find_synthesis(view_a, view_b)
    )
```

**Agent Usage**:

```python
# Check for contradictions before merging views
analysis = await detect_contradiction(
    "Use microservices for scalability",
    "Keep monolith for simplicity"
)

if analysis.contradicts:
    # Find synthesis
    if analysis.ghost_alternatives:
        synthesis = min(analysis.ghost_alternatives, key=lambda g: g.loss)
        await record_dialectic(
            thesis=analysis.view_a,
            antithesis=analysis.view_b,
            synthesis=synthesis.content
        )
else:
    # Views are compatible, can use both
    await merge_views(analysis.view_a, analysis.view_b)
```

### 4. Validate Proof Coherence

Check proof quality before committing:

```python
async def validate_proof(proof: Proof) -> ProofValidation:
    """
    Validate Toulmin proof using Galois loss.

    Returns:
        ProofValidation with coherence score and issues
    """
    loss = await galois_loss(proof)
    decomp = await compute_loss_decomposition(proof)

    issues = []

    # Check each component
    if decomp.warrant_loss > 0.3:
        issues.append(f"Warrant weak (loss: {decomp.warrant_loss:.2f})")
    if decomp.backing_loss > 0.3:
        issues.append(f"Backing insufficient (loss: {decomp.backing_loss:.2f})")
    if decomp.composition_loss > 0.2:
        issues.append(f"Components don't compose well (loss: {decomp.composition_loss:.2f})")

    return ProofValidation(
        coherence=1.0 - loss,
        tier=classify_by_loss(loss),
        issues=issues,
        is_valid=loss < 0.7,
        needs_revision=loss > 0.5,
        loss_decomposition=decomp
    )
```

**Agent Usage**:

```python
# Validate before committing change
validation = await validate_proof(my_proof)

if not validation.is_valid:
    raise ProofInvalidError(validation.issues)
elif validation.needs_revision:
    # Warn but allow
    await warn_user(f"Proof quality is {validation.tier}: {validation.issues}")

await commit_with_proof(my_proof)
```

### 5. Navigate Knowledge Graph

Follow loss gradients toward coherence:

```python
async def navigate_graph(
    current_node: NodeId,
    graph: ZeroGraph
) -> NavigationSuggestion:
    """
    Suggest next node based on loss gradient.
    """
    current_loss = await compute_node_loss(current_node, graph)

    # Get all edges from current node
    edges = graph.edges_from(current_node)

    # Compute loss for each target
    targets = []
    for edge in edges:
        target_loss = await compute_node_loss(edge.target, graph)
        targets.append({
            "edge": edge,
            "target": edge.target,
            "loss": target_loss,
            "improvement": current_loss - target_loss
        })

    # Sort by improvement (steepest descent first)
    targets.sort(key=lambda t: t["improvement"], reverse=True)

    return NavigationSuggestion(
        current=current_node,
        current_loss=current_loss,
        best_next=targets[0] if targets else None,
        all_options=targets
    )
```

**Agent Usage**:

```python
# Navigate toward coherence
while True:
    suggestion = await navigate_graph(current, graph)

    if suggestion.current_loss < 0.1:
        # Reached low-loss region
        break

    if not suggestion.best_next:
        # No edges, stuck
        break

    if suggestion.best_next["improvement"] <= 0:
        # Local minimum
        break

    current = suggestion.best_next["target"]
    await process_node(current)
```

---

## Integration Patterns

### With Witness System

Every Zero Seed operation should be witnessed:

```python
async def witnessed_decision(
    claim: str,
    proof: GaloisWitnessedProof
) -> tuple[MarkId, FusionId]:
    """
    Make decision and record in witness system.
    """
    # Record the proof as a mark
    mark = await create_mark(
        action=f"Decided: {claim}",
        reasoning=f"Coherence: {proof.coherence:.2f}, Tier: {proof.tier.value}",
        tags=["zero-seed", "decision", proof.tier.value.lower()]
    )

    # Record as formal decision if significant
    if proof.coherence > 0.7:
        fusion = await kg_decide_fast(
            decision=claim,
            reasoning=proof.backing
        )
        return mark.id, fusion.id

    return mark.id, None
```

### With Analysis Operad

Zero Seed integrates with the four analysis modes:

| Mode | Zero Seed Integration |
|------|----------------------|
| **Categorical** | Verify composition laws via L(A >> B) <= L(A) + L(B) |
| **Epistemic** | Ground claims in L1-L2 via grounding protocol |
| **Dialectical** | Detect contradictions via super-additive loss |
| **Generative** | Measure regenerability via Galois coherence |

```python
async def analyze_with_zero_seed(spec_path: str) -> AnalysisReport:
    """
    Run four-mode analysis with Zero Seed grounding.
    """
    spec = await load_spec(spec_path)

    # Categorical: Check composition
    categorical = await check_composition_laws(spec)

    # Epistemic: Ground claims
    epistemic = await ground_all_claims(spec)

    # Dialectical: Find tensions
    dialectical = await find_contradictions(spec)

    # Generative: Measure coherence
    generative = await compute_overall_coherence(spec)

    return AnalysisReport(
        categorical=categorical,
        epistemic=epistemic,
        dialectical=dialectical,
        generative=generative,
        overall_loss=generative.loss
    )
```

### Agent Startup Protocol

```python
async def agent_startup():
    """
    Zero Seed startup protocol for agents.
    """
    # 1. Load axioms (L1)
    axioms = await load_axioms()

    # 2. Load constitution (L2)
    constitution = await load_constitution()

    # 3. Get context from witness
    context = await get_witness_context(budget=1500, query="zero-seed")

    # 4. Check for unresolved contradictions
    contradictions = await get_open_contradictions()

    if contradictions:
        # Prompt for resolution
        for c in contradictions[:3]:
            await prompt_resolution(c)

    return AgentContext(
        axioms=axioms,
        constitution=constitution,
        witness_context=context,
        pending_contradictions=contradictions
    )
```

---

## CLI Integration

### Core Commands (Proposed)

```bash
# Ground a claim
kg zero-seed ground "Use SSE instead of WebSockets"
# Output: Grounding report with axiom links and coherence tier

# Construct proof
kg zero-seed prove "Add caching layer" --evidence "..."
# Output: Toulmin proof with Galois coherence

# Detect contradiction
kg zero-seed contradict <node-a> <node-b>
# Output: Super-additivity analysis and synthesis hints

# Validate proof
kg zero-seed validate <node-id>
# Output: Coherence score, tier, issues

# Navigate from node
kg zero-seed navigate <node-id>
# Output: Suggested next nodes by loss gradient

# Graph health
kg zero-seed health
# Output: Overall loss, weak edges, high-loss nodes
```

### JSON Output for Agents

```bash
# Always use --json for programmatic access
kg zero-seed ground "..." --json
# {"grounding": {"claim": "...", "entity_grounded": true, ...}, "loss": 0.15, "tier": "EMPIRICAL"}

kg zero-seed contradict <a> <b> --json
# {"loss_a": 0.2, "loss_b": 0.3, "loss_combined": 0.7, "super_additivity": 0.2, "contradicts": true, ...}
```

---

## Evidence Tiers Reference

| Tier | Loss Range | Witness Mode | Use Case |
|------|------------|--------------|----------|
| **CATEGORICAL** | L < 0.1 | SINGLE | Axioms, definitions |
| **EMPIRICAL** | L < 0.3 | SINGLE | Data-driven claims |
| **AESTHETIC** | L < 0.5 | SESSION | Taste-based decisions |
| **SOMATIC** | L < 0.7 | SESSION | Gut feelings |
| **CHAOTIC** | L >= 0.7 | LAZY | Needs revision |

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Skip Grounding** | Decisions float without axioms | Always run ground protocol |
| **Ignore Loss** | No coherence tracking | Compute Galois loss for all L3+ |
| **Force Agreement** | Pretend contradictions don't exist | Compute super-additivity |
| **Accept Chaotic** | Proceed with L > 0.7 | Revise or decompose first |
| **Forget Witness** | Decisions not recorded | Always emit marks |

---

## Example: Full Decision Flow

```python
async def make_architectural_decision(
    question: str,
    options: list[str]
) -> Decision:
    """
    Full Zero Seed decision flow.
    """
    # 1. Ground each option
    groundings = {}
    for option in options:
        groundings[option] = await ground_decision(option)

    # 2. Filter by coherence
    viable = [o for o, g in groundings.items() if g.tier != EvidenceTier.CHAOTIC]

    if len(viable) == 0:
        raise NoViableOptionsError("All options are chaotic")

    if len(viable) == 1:
        chosen = viable[0]
    else:
        # 3. Check for contradictions between viable options
        for a, b in combinations(viable, 2):
            analysis = await detect_contradiction(a, b)
            if analysis.contradicts:
                # Use synthesis if available
                if analysis.ghost_alternatives:
                    synthesis = analysis.ghost_alternatives[0]
                    viable.append(synthesis.content)

        # 4. Choose lowest-loss option
        chosen = min(viable, key=lambda o: groundings.get(o, Grounding(loss=1.0)).loss)

    # 5. Construct proof for chosen option
    proof = await construct_proof(
        claim=chosen,
        evidence=[f"Question: {question}", f"Options considered: {options}"],
        reasoning=f"Chosen for lowest Galois loss among viable options"
    )

    # 6. Validate
    validation = await validate_proof(proof)

    if not validation.is_valid:
        raise ProofInvalidError(validation.issues)

    # 7. Witness
    mark_id, fusion_id = await witnessed_decision(chosen, proof)

    return Decision(
        question=question,
        chosen=chosen,
        proof=proof,
        validation=validation,
        mark_id=mark_id,
        fusion_id=fusion_id
    )
```

---

## Philosophy

> *"Axioms aren't stipulated, they're discovered as zero-loss fixed points."*

Zero Seed transforms agent reasoning from intuition to computation:

1. **Axioms = Fixed Points**: Content that survives restructuring unchanged
2. **Layers = Convergence Depth**: How many restructurings to reach stability
3. **Coherence = Inverse Loss**: Quality IS the lack of information loss
4. **Contradiction = Super-Additivity**: Clash IS measurable excess loss
5. **Navigation = Gradient Descent**: Move toward low-loss regions

This is rigorous epistemology for autonomous agents.

---

*"The proof IS the decision. The loss IS the witness."*
*"Budget forces compression. Compression reveals essence."*
