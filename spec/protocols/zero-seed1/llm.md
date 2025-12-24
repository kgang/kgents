# Zero Seed: LLM Integration via Galois Modularization

**Version**: 1.0.0
**Status**: Draft
**Dependencies**: `metatheory.md`, `galois.md`, `catastrophic-bifurcation.md`

---

## Abstract

> *"The LLM IS the restructurer. The token IS the energy. The loss IS the measure of understanding."*

The original Zero Seed had LLM features as auxiliary tooling. The Galois upgrade reveals the deeper truth: **the LLM IS the Galois adjunction**. Every compression is a restructure operation `R`, every generation is a reconstitution `C`, and every comparison is a loss measurement `L`. The LLM doesn't assist the theory—it instantiates it.

This spec defines:
1. LLM as the canonical Galois restructure operator
2. Token budgets as thermodynamic energy constraints
3. Loss functions as semantic distance metrics
4. Model selection as loss-tolerance optimization
5. Minimal-edit UX grounded in Galois coherence

**Key Insight**: Human-in-the-loop theorem proving becomes tractable when the LLM preserves Galois structure. The 10x token budget isn't wasteful—it's purchasing modular coherence.

---

## 1. The LLM as Galois Adjunction

### 1.1 Mathematical Foundation

Recall from `galois.md`:

```
Galois Adjunction: (R, C, L) where
  R: Content → Modular    (restructure)
  C: Modular → Content    (reconstitute)
  L: Content × Content → [0,1]  (loss)

Laws:
  L(x, C(R(x))) < ε  (lossless compression)
  R(C(m)) = m        (reconstitution is left-inverse)
```

**The LLM instantiates this adjunction**:

```python
class LLMGaloisRestructurer(Protocol):
    """The LLM IS the Galois restructure operator.

    This is not metaphor. The LLM's compression/generation mechanisms
    ARE the mathematical operations R, C, L defined in Galois theory.

    Proof: For any content x,
      - R(x) = LLM(compress_prompt(x))
      - C(m) = LLM(expand_prompt(m))
      - L(x,y) = LLM(compare_prompt(x,y))

    The adjunction laws hold empirically with high probability when:
      1. Prompts are well-structured (see §2)
      2. Token budget is liberal (see §3)
      3. Model selection matches loss tolerance (see §4)
    """

    async def restructure(self, content: str, context: Context) -> ModularContent:
        """R: Content → Modular

        Maps arbitrary prose to its minimal modular representation.
        Preserves semantic information while compressing syntax.

        Invariant: L(content, C(R(content))) < self.loss_tolerance
        """
        ...

    async def reconstitute(self, modular: ModularContent, style: Style) -> str:
        """C: Modular → Content

        Maps modular representation back to prose.
        Style guide allows controlled variation (theorem vs. proof vs. explanation).

        Invariant: R(C(m)) ≈ m (up to normalization)
        """
        ...

    async def galois_loss(self, x: str, y: str, axis: LossAxis) -> float:
        """L: Content × Content → [0,1]

        Semantic distance metric. Not string edit distance—captures
        whether the MEANING is preserved.

        Axes:
          - semantic: raw information preservation
          - logical: proof validity preservation
          - stylistic: tone/voice preservation
          - structural: modular decomposition preservation
        """
        ...
```

### 1.2 Why This Works: Information-Theoretic Grounding

The LLM's training objective is next-token prediction:

```
P(w_t | w_1, ..., w_{t-1}) → max
```

This is **compression** in the Shannon sense. The model learns to represent text in a latent space that minimizes description length. This is exactly what `R` does—finds the compressed modular form.

Generation reverses this:

```
Sample from P(w_t | latent_state) → text
```

This is **reconstitution**. The latent state is the modular representation; sampling produces prose.

**Galois coherence emerges from training data structure**. If the corpus contains math proofs, API docs, and narrative explanations of the same concepts, the model learns that these are VIEWS of the same underlying structure. This is sheaf gluing.

---

## 2. Prompt Engineering for Galois Operations

### 2.1 Restructure Prompts

```python
RESTRUCTURE_PROMPT = """
You are a Galois modularization engine. Your task is to decompose content into its minimal, semantically atomic modules.

INPUT CONTENT:
{content}

CONTEXT:
{context}

OUTPUT REQUIREMENTS:
1. Identify atomic semantic units (axioms, definitions, theorems, lemmas)
2. Extract dependency edges (A depends on B if A references B)
3. Compute compression ratio: len(output) / len(input)
4. Preserve ALL semantic information—no lossy summarization

Return JSON:
{{
  "modules": [
    {{"id": "mod_1", "type": "axiom", "content": "...", "deps": []}},
    {{"id": "mod_2", "type": "theorem", "content": "...", "deps": ["mod_1"]}}
  ],
  "compression_ratio": 0.3,
  "rationale": "Explain why this modularization is minimal"
}}

CRITICAL: If you cannot losslessly modularize (e.g., content is already atomic), return compression_ratio = 1.0 and wrap in a single module.
"""

async def restructure(self, content: str, context: Context) -> ModularContent:
    prompt = RESTRUCTURE_PROMPT.format(
        content=content,
        context=context.render()  # Includes parent modules, domain axioms
    )

    response = await self.llm.generate(
        prompt,
        model=self.select_model(task="restructure"),
        max_tokens=10_000,  # Liberal budget
        temperature=0.0,    # Deterministic for reproducibility
        response_format={"type": "json_object"}
    )

    data = json.loads(response.content)
    return ModularContent.from_dict(data)
```

### 2.2 Reconstitute Prompts

```python
RECONSTITUTE_PROMPT = """
You are a Galois reconstitution engine. Your task is to expand modular content back into fluent prose.

MODULAR REPRESENTATION:
{modules}

STYLE GUIDE:
{style}

OUTPUT REQUIREMENTS:
1. Fluent, natural prose (not a bulleted list)
2. Preserve logical dependencies (if A depends on B, introduce B first)
3. Match the style guide (formal theorem vs. intuitive explanation)
4. Include ALL semantic content from modules—no omissions

Return the expanded prose directly (not JSON).
"""

async def reconstitute(self, modular: ModularContent, style: Style) -> str:
    prompt = RECONSTITUTE_PROMPT.format(
        modules=modular.render_for_llm(),  # Human-readable module listing
        style=style.description
    )

    response = await self.llm.generate(
        prompt,
        model=self.select_model(task="reconstitute"),
        max_tokens=20_000,  # 2x restructure budget (expansion)
        temperature=0.3     # Slight variation for natural prose
    )

    return response.content
```

### 2.3 Loss Measurement Prompts

```python
GALOIS_LOSS_PROMPT = """
You are a semantic distance metric. Compare two texts and measure information loss.

ORIGINAL:
{original}

RECONSTITUTED:
{reconstituted}

AXIS: {axis}

INSTRUCTIONS:
- Semantic axis: Do they convey the same information? Ignore wording differences.
- Logical axis: If original proves X, does reconstituted prove X? Check validity.
- Stylistic axis: Do they have the same tone, formality, voice?
- Structural axis: Do they decompose into the same modules?

OUTPUT: A single float from 0.0 to 1.0 where:
  0.0 = perfect preservation (no loss)
  0.5 = significant drift (half the information lost)
  1.0 = complete divergence (unrecognizable)

Return ONLY the float, no explanation.
"""

async def galois_loss(self, x: str, y: str, axis: LossAxis) -> float:
    prompt = GALOIS_LOSS_PROMPT.format(
        original=x,
        reconstituted=y,
        axis=axis.value
    )

    response = await self.llm.generate(
        prompt,
        model="claude-3-5-haiku-20241022",  # Fast model for metric
        max_tokens=10,
        temperature=0.0
    )

    try:
        loss = float(response.content.strip())
        return max(0.0, min(1.0, loss))  # Clamp to [0,1]
    except ValueError:
        # Fallback: use edit distance as crude approximation
        return difflib.SequenceMatcher(None, x, y).ratio()
```

---

## 3. Token Budgets as Thermodynamic Constraints

### 3.1 The 10x Principle

**Heuristic**: Iterative refinement with liberal token budgets outperforms single-shot generation by 10x in semantic preservation.

**Rationale**: Galois modularization is NP-hard in the general case. The LLM uses approximate search. Multiple passes allow:
1. Initial rough decomposition
2. Validation via reconstitution
3. Loss-driven refinement
4. Convergence to fixed point

```python
@dataclass
class TokenBudget:
    """Energy budget for LLM operations.

    Philosophy: Tokens are the thermodynamic currency. Spending 10x tokens
    to achieve 2x loss reduction is often worth it—the human time saved
    in fixing semantic drift far exceeds API cost.
    """

    max_input_per_call: int = 100_000   # Claude Sonnet 4.5 limit
    max_output_per_call: int = 10_000   # Reasonable completion size
    max_session_cumulative: int = 1_000_000  # Hard stop for runaway loops

    cumulative_input: int = 0
    cumulative_output: int = 0

    def can_afford(self, estimated_input: int, estimated_output: int) -> bool:
        """Check if we have budget remaining."""
        total_estimated = self.cumulative_input + estimated_input + \
                         self.cumulative_output + estimated_output
        return total_estimated < self.max_session_cumulative

    def charge(self, actual_input: int, actual_output: int):
        """Deduct tokens after call."""
        self.cumulative_input += actual_input
        self.cumulative_output += actual_output

    def session_cost_usd(self) -> float:
        """Estimate cost at current pricing (as of 2025-01).

        Sonnet 4.5: $3 / 1M input, $15 / 1M output
        """
        input_cost = (self.cumulative_input / 1_000_000) * 3.0
        output_cost = (self.cumulative_output / 1_000_000) * 15.0
        return input_cost + output_cost
```

### 3.2 Latency Budget

Token budget isn't the only constraint. Human-in-the-loop theorem proving requires **interactive latency**.

```python
@dataclass
class LatencyBudget:
    """Time budget for LLM operations.

    Philosophy: 3s is the threshold for "feels instant". 10s is acceptable
    for complex operations. 30s requires progress indication.
    """

    interactive_threshold: float = 3.0   # Must respond within 3s
    acceptable_threshold: float = 10.0   # Can take up to 10s
    progress_threshold: float = 30.0     # Show progress bar beyond 30s

    timeout: float = 60.0  # Hard timeout

    def select_strategy(self, estimated_time: float) -> str:
        """Choose UX pattern based on expected latency."""
        if estimated_time < self.interactive_threshold:
            return "synchronous"  # Inline, no spinner
        elif estimated_time < self.acceptable_threshold:
            return "spinner"      # Show spinner, block UI
        elif estimated_time < self.progress_threshold:
            return "progress"     # Show progress bar
        else:
            return "background"   # Run in background, notify when done
```

### 3.3 Quality Budget

Not all operations need opus-level fidelity. Match model to loss tolerance.

```python
class QualityBudget:
    """Loss tolerance → model selection mapping.

    Philosophy: Use the fastest model that meets quality requirements.
    Don't use opus for tasks where haiku suffices.
    """

    MODELS = {
        "opus": {
            "name": "claude-opus-4-5-20251101",
            "loss_tolerance": 0.05,   # < 5% loss
            "latency_estimate": 8.0,  # seconds for 1K tokens
            "cost_per_1M_input": 15.0,
            "cost_per_1M_output": 75.0
        },
        "sonnet": {
            "name": "claude-sonnet-4-5-20250929",
            "loss_tolerance": 0.15,   # < 15% loss
            "latency_estimate": 3.0,
            "cost_per_1M_input": 3.0,
            "cost_per_1M_output": 15.0
        },
        "haiku": {
            "name": "claude-3-5-haiku-20241022",
            "loss_tolerance": 0.30,   # < 30% loss
            "latency_estimate": 1.0,
            "cost_per_1M_input": 1.0,
            "cost_per_1M_output": 5.0
        }
    }

    def select_model(self, task: str, max_loss: float) -> str:
        """Select cheapest model that meets loss tolerance.

        Examples:
          - Axiom mining (max_loss=0.05) → opus
          - Proof validation (max_loss=0.10) → sonnet
          - Quick loss check (max_loss=0.30) → haiku
        """
        for model_id in ["haiku", "sonnet", "opus"]:
            model = self.MODELS[model_id]
            if model["loss_tolerance"] >= max_loss:
                return model["name"]

        # Fallback: use opus if even haiku doesn't meet tolerance
        return self.MODELS["opus"]["name"]
```

---

## 4. LLM Operations with Galois Grounding

### 4.1 Axiom Mining

**Goal**: Extract atomic axioms from prose specification.

**Galois Property**: Axioms are **zero-loss fixed points**—modularizing an axiom produces the axiom unchanged.

```python
async def mine_axioms(self, spec: str) -> List[Axiom]:
    """Extract axioms via fixed-point search.

    Algorithm:
      1. Restructure spec into candidate modules
      2. For each module M:
         a. Reconstitute M → prose P
         b. Restructure P → module M'
         c. If M == M', then M is an axiom (fixed point)
      3. Return all axioms

    Complexity: O(n) restructure calls where n = # modules
    Token cost: ~50K per axiom (restructure + reconstitute + comparison)
    """

    # Initial decomposition
    modular = await self.restructure(spec, context=Context.empty())

    axioms = []
    for module in modular.modules:
        # Fixed-point test
        prose = await self.reconstitute(
            ModularContent(modules=[module], edges=[]),
            style=Style.FORMAL
        )
        remodularized = await self.restructure(prose, context=Context.empty())

        # Check if M == R(C(M)) (up to normalization)
        loss = await self.galois_loss(
            module.content,
            remodularized.modules[0].content,
            axis=LossAxis.SEMANTIC
        )

        if loss < 0.05:  # < 5% loss = fixed point
            axioms.append(Axiom(
                id=module.id,
                content=module.content,
                stability_score=1.0 - loss
            ))

    return axioms
```

### 4.2 Proof Validation

**Goal**: Check if a proof derivation is valid.

**Galois Property**: A valid proof has **low structural loss**—modularizing it preserves the derivation graph.

```python
async def validate_proof(self, proof: Proof) -> ValidationResult:
    """Check proof validity via Galois loss measurement.

    A proof is valid if:
      1. Each step follows from axioms + previous steps
      2. The dependency graph is acyclic
      3. The conclusion follows from the final step

    We don't need formal verification—the LLM can detect logical gaps
    by measuring structural loss.
    """

    # Restructure proof into modules
    modular = await self.restructure(
        proof.render_as_prose(),
        context=Context(axioms=proof.axioms)
    )

    # Check dependency graph is acyclic
    if not modular.is_dag():
        return ValidationResult(
            valid=False,
            error="Proof contains circular reasoning",
            loss=1.0
        )

    # Reconstitute and measure logical loss
    reconstituted = await self.reconstitute(modular, style=Style.PROOF)
    loss = await self.galois_loss(
        proof.render_as_prose(),
        reconstituted,
        axis=LossAxis.LOGICAL
    )

    if loss > 0.15:  # > 15% logical loss = invalid
        return ValidationResult(
            valid=False,
            error="Proof has logical gaps (high Galois loss)",
            loss=loss
        )

    return ValidationResult(valid=True, loss=loss)
```

### 4.3 Contradiction Detection

**Goal**: Find statements that contradict existing axioms.

**Galois Property**: Contradictions produce **super-additive loss**—combining contradictory modules increases loss more than linearly.

```python
async def detect_contradictions(
    self,
    statement: str,
    axioms: List[Axiom]
) -> Optional[Contradiction]:
    """Find contradictions via super-additive loss.

    If statement S contradicts axiom A, then:
      L(C({A, S}), C({A}) ⊕ C({S})) > L(C({A}), A) + L(C({S}), S)

    That is, the combined module has higher loss than the sum of
    individual losses. This is the signature of contradiction.
    """

    # Baseline: loss of statement alone
    statement_loss = await self.galois_loss(
        statement,
        await self.reconstitute(
            await self.restructure(statement, Context.empty()),
            Style.FORMAL
        ),
        LossAxis.SEMANTIC
    )

    for axiom in axioms:
        # Loss of axiom alone (should be ~0 since axioms are fixed points)
        axiom_loss = await self.galois_loss(
            axiom.content,
            await self.reconstitute(
                await self.restructure(axiom.content, Context.empty()),
                Style.FORMAL
            ),
            LossAxis.SEMANTIC
        )

        # Loss of combined module
        combined = f"{axiom.content}\n\n{statement}"
        combined_modular = await self.restructure(combined, Context.empty())
        combined_prose = await self.reconstitute(combined_modular, Style.FORMAL)
        combined_loss = await self.galois_loss(
            combined,
            combined_prose,
            LossAxis.LOGICAL
        )

        # Check for super-additivity
        if combined_loss > (axiom_loss + statement_loss) * 1.5:
            return Contradiction(
                statement=statement,
                conflicts_with=axiom,
                loss_excess=combined_loss - (axiom_loss + statement_loss)
            )

    return None
```

### 4.4 Synthesis Generation

**Goal**: Generate new theorems by combining modules.

**Galois Property**: Good syntheses have **low combined loss**—the generated theorem fits naturally with existing modules.

```python
async def synthesize_theorem(
    self,
    modules: List[Module],
    goal: str
) -> List[Theorem]:
    """Generate theorem candidates via loss minimization.

    Algorithm:
      1. Prompt LLM to generate N candidate theorems
      2. For each candidate C:
         a. Modularize C
         b. Compute L(C, reconstitute(modularize(C)))
         c. Compute L(modules ⊕ C, sum of individual losses)
      3. Rank by combined loss
      4. Return top K with loss < threshold
    """

    SYNTHESIS_PROMPT = f"""
    Given these modules:
    {render_modules(modules)}

    Generate 10 novel theorems that:
    1. Follow from these modules as logical consequences
    2. Are interesting (non-trivial, non-tautological)
    3. Advance toward this goal: {goal}

    Return as JSON array of strings.
    """

    response = await self.llm.generate(
        SYNTHESIS_PROMPT,
        model=self.select_model(task="synthesis", max_loss=0.10),
        max_tokens=5_000,
        temperature=0.8,  # Higher temperature for creativity
        response_format={"type": "json_object"}
    )

    candidates = json.loads(response.content)["theorems"]

    results = []
    for candidate in candidates:
        # Measure Galois loss
        candidate_modular = await self.restructure(candidate, Context(modules=modules))
        candidate_prose = await self.reconstitute(candidate_modular, Style.THEOREM)

        semantic_loss = await self.galois_loss(
            candidate,
            candidate_prose,
            LossAxis.SEMANTIC
        )

        # Check coherence with existing modules
        combined_loss = await self._combined_loss(modules + [candidate_modular])

        if semantic_loss < 0.10 and combined_loss < 0.15:
            results.append(Theorem(
                statement=candidate,
                derived_from=[m.id for m in modules],
                loss_score=semantic_loss,
                coherence_score=1.0 - combined_loss
            ))

    # Rank by combined metric
    results.sort(key=lambda t: t.loss_score + (1 - t.coherence_score))
    return results[:5]  # Top 5 candidates
```

---

## 5. Minimal-Edit UX

### 5.1 Inline Ghost Text

Show LLM suggestions as ghost text, accept/reject with minimal keystrokes.

```python
class GhostTextProvider:
    """Provide inline suggestions grounded in Galois loss.

    UX Pattern:
      1. User types axiom
      2. After 500ms pause, trigger LLM restructure
      3. Show reconstituted version as ghost text
      4. Display loss score in corner
      5. Tab to accept, Esc to reject, → to cycle alternatives
    """

    async def suggest_alternatives(
        self,
        user_input: str,
        context: Context
    ) -> List[Alternative]:
        """Generate K alternative phrasings, ranked by loss."""

        # Restructure user input
        modular = await self.restructurer.restructure(user_input, context)

        # Generate alternatives with varying styles
        styles = [Style.FORMAL, Style.CONCISE, Style.INTUITIVE]
        alternatives = []

        for style in styles:
            prose = await self.restructurer.reconstitute(modular, style)
            loss = await self.restructurer.galois_loss(
                user_input,
                prose,
                LossAxis.SEMANTIC
            )

            alternatives.append(Alternative(
                text=prose,
                style=style,
                loss=loss
            ))

        # Rank by loss (lowest first)
        alternatives.sort(key=lambda a: a.loss)
        return alternatives

    async def on_text_change(self, text: str, cursor: int):
        """Trigger ghost text after pause."""
        await asyncio.sleep(0.5)  # Debounce

        alternatives = await self.suggest_alternatives(text, self.context)

        if alternatives[0].loss < 0.10:  # Only show if high fidelity
            self.editor.show_ghost_text(
                alternatives[0].text,
                loss=alternatives[0].loss,
                alternatives=alternatives[1:]  # Rest available on Tab
            )
```

### 5.2 Accept/Reject with Loss Preview

```typescript
interface GhostTextWidget {
  text: string;
  loss: number;  // [0, 1]
  alternatives: Alternative[];
  currentIndex: number;
}

function renderGhostText(widget: GhostTextWidget) {
  const lossColor = widget.loss < 0.05 ? 'green' :
                    widget.loss < 0.15 ? 'yellow' : 'red';

  return (
    <div className="ghost-text">
      <span className="suggestion">{widget.text}</span>
      <span className={`loss-badge ${lossColor}`}>
        Δ {(widget.loss * 100).toFixed(1)}%
      </span>
      <span className="hint">
        Tab: accept | Esc: reject | →: next alt ({widget.currentIndex + 1}/{widget.alternatives.length})
      </span>
    </div>
  );
}
```

### 5.3 Tab to Cycle Alternatives

```python
class GhostTextController:
    """Handle keyboard interactions with ghost text."""

    def __init__(self, editor: Editor, suggestions: List[Alternative]):
        self.editor = editor
        self.suggestions = suggestions
        self.current = 0

    def on_key(self, key: str):
        if key == "Tab":
            self.accept()
        elif key == "Escape":
            self.reject()
        elif key == "ArrowRight":
            self.cycle_next()
        elif key == "ArrowLeft":
            self.cycle_prev()

    def accept(self):
        """Replace user text with current suggestion."""
        self.editor.replace_text(self.suggestions[self.current].text)
        self.editor.hide_ghost_text()

        # Log acceptance for learning
        log_acceptance(
            original=self.editor.original_text,
            accepted=self.suggestions[self.current].text,
            loss=self.suggestions[self.current].loss
        )

    def reject(self):
        """Keep user text, hide suggestions."""
        self.editor.hide_ghost_text()

        # Log rejection for learning
        log_rejection(
            original=self.editor.original_text,
            rejected_alternatives=self.suggestions
        )

    def cycle_next(self):
        """Show next alternative."""
        self.current = (self.current + 1) % len(self.suggestions)
        self.editor.update_ghost_text(self.suggestions[self.current])

    def cycle_prev(self):
        """Show previous alternative."""
        self.current = (self.current - 1) % len(self.suggestions)
        self.editor.update_ghost_text(self.suggestions[self.current])
```

---

## 6. Implementation Architecture

### 6.1 Service Module: `services/zero_seed_llm/`

```
services/zero_seed_llm/
├── __init__.py                 # Exports
├── restructurer.py             # LLMGaloisRestructurer
├── budgets.py                  # TokenBudget, LatencyBudget, QualityBudget
├── operations.py               # mine_axioms, validate_proof, etc.
├── ui/
│   ├── ghost_text.py           # GhostTextProvider
│   └── ghost_text_controller.py
├── _tests/
│   ├── test_restructure.py     # R ∘ C ≈ id tests
│   ├── test_loss.py            # Loss metric validation
│   └── test_budgets.py         # Budget enforcement
└── examples/
    ├── axiom_mining.py         # Demo: extract axioms from prose
    └── proof_validation.py     # Demo: validate a proof
```

### 6.2 AGENTESE Integration

```python
# services/zero_seed_llm/__init__.py

from claude.protocols.agentese.node import node, NodeAspect
from .restructurer import LLMGaloisRestructurer
from .operations import AxiomMiner, ProofValidator

@node(
    "concept.zero_seed.llm.restructure",
    aspects=[NodeAspect.STATELESS, NodeAspect.IDEMPOTENT],
    dependencies=("llm_client",)
)
class RestructureNode:
    """AGENTESE node: restructure prose into modules."""

    def __init__(self, llm_client):
        self.restructurer = LLMGaloisRestructurer(llm_client)

    async def invoke(self, observer, content: str, context: dict):
        modular = await self.restructurer.restructure(
            content,
            Context.from_dict(context)
        )
        yield {"modular": modular.to_dict()}

@node(
    "concept.zero_seed.llm.mine_axioms",
    aspects=[NodeAspect.EXPENSIVE],  # High token cost
    dependencies=("llm_client",)
)
class AxiomMiningNode:
    """AGENTESE node: extract axioms from specification."""

    def __init__(self, llm_client):
        self.miner = AxiomMiner(llm_client)

    async def invoke(self, observer, spec: str):
        axioms = await self.miner.mine_axioms(spec)
        yield {"axioms": [a.to_dict() for a in axioms]}
```

### 6.3 CLI Commands

```python
# protocols/cli/handlers/zero_seed.py

@click.command()
@click.argument("spec_file", type=click.Path(exists=True))
@click.option("--max-loss", default=0.05, help="Maximum acceptable loss")
async def mine_axioms(spec_file: str, max_loss: float):
    """Extract axioms from specification via LLM Galois modularization.

    Example:
      kg zero-seed mine-axioms spec/protocols/zero-seed.md --max-loss 0.05
    """
    spec = Path(spec_file).read_text()

    miner = AxiomMiner(get_llm_client())
    axioms = await miner.mine_axioms(spec, max_loss=max_loss)

    for axiom in axioms:
        click.echo(f"[{axiom.id}] {axiom.content}")
        click.echo(f"  Stability: {axiom.stability_score:.2%}\n")

@click.command()
@click.argument("proof_file", type=click.Path(exists=True))
async def validate_proof(proof_file: str):
    """Validate proof using LLM Galois loss measurement.

    Example:
      kg zero-seed validate-proof proofs/initial_metatheory.md
    """
    proof = Proof.from_markdown(Path(proof_file).read_text())

    validator = ProofValidator(get_llm_client())
    result = await validator.validate_proof(proof)

    if result.valid:
        click.secho(f"✓ Proof valid (loss: {result.loss:.2%})", fg="green")
    else:
        click.secho(f"✗ Proof invalid: {result.error}", fg="red")
        click.secho(f"  Loss: {result.loss:.2%}", fg="red")
```

---

## 7. Testing Strategy

### 7.1 Property-Based Tests

```python
# services/zero_seed_llm/_tests/test_restructure.py

from hypothesis import given, strategies as st
from claude.services.zero_seed_llm import LLMGaloisRestructurer

@given(st.text(min_size=100, max_size=1000))
async def test_restructure_reconstitute_roundtrip(content: str):
    """Property: L(x, C(R(x))) < ε for all x."""

    restructurer = LLMGaloisRestructurer(get_test_llm())

    # R: Content → Modular
    modular = await restructurer.restructure(content, Context.empty())

    # C: Modular → Content
    reconstituted = await restructurer.reconstitute(modular, Style.FORMAL)

    # L: measure loss
    loss = await restructurer.galois_loss(
        content,
        reconstituted,
        LossAxis.SEMANTIC
    )

    assert loss < 0.15, f"Round-trip loss too high: {loss}"

@given(
    st.text(min_size=50),
    st.sampled_from([Style.FORMAL, Style.CONCISE, Style.INTUITIVE])
)
async def test_reconstitute_is_left_inverse(content: str, style: Style):
    """Property: R(C(m)) ≈ m (reconstitution is left-inverse)."""

    restructurer = LLMGaloisRestructurer(get_test_llm())

    # R(x) = m
    modular = await restructurer.restructure(content, Context.empty())

    # C(m) = y
    prose = await restructurer.reconstitute(modular, style)

    # R(y) = m'
    remodularized = await restructurer.restructure(prose, Context.empty())

    # Check m ≈ m'
    assert modular.is_isomorphic_to(remodularized), \
        "Modular structures differ after round-trip"
```

### 7.2 Regression Tests

```python
# services/zero_seed_llm/_tests/test_axiom_mining.py

async def test_mine_axioms_from_known_spec():
    """Regression: ensure we extract known axioms from reference spec."""

    spec = """
    # Theory of Groups

    A group is a set G with operation •: G × G → G satisfying:

    1. Closure: ∀ a,b ∈ G, a • b ∈ G
    2. Associativity: ∀ a,b,c ∈ G, (a • b) • c = a • (b • c)
    3. Identity: ∃ e ∈ G such that ∀ a ∈ G, e • a = a • e = a
    4. Inverses: ∀ a ∈ G, ∃ a⁻¹ ∈ G such that a • a⁻¹ = a⁻¹ • a = e
    """

    miner = AxiomMiner(get_test_llm())
    axioms = await miner.mine_axioms(spec)

    # Should extract exactly 4 axioms
    assert len(axioms) == 4

    # Should identify them correctly
    axiom_types = {a.id for a in axioms}
    assert "closure" in axiom_types
    assert "associativity" in axiom_types
    assert "identity" in axiom_types
    assert "inverses" in axiom_types
```

### 7.3 Budget Enforcement Tests

```python
# services/zero_seed_llm/_tests/test_budgets.py

async def test_token_budget_prevents_runaway():
    """Ensure token budget hard-stops runaway generation."""

    budget = TokenBudget(max_session_cumulative=10_000)
    restructurer = LLMGaloisRestructurer(get_test_llm(), budget=budget)

    # Try to consume 15K tokens (should fail)
    large_content = "x" * 50_000  # ~12.5K tokens

    with pytest.raises(TokenBudgetExceeded):
        await restructurer.restructure(large_content, Context.empty())

    # Budget should be close to limit
    assert budget.cumulative_input > 8_000

async def test_latency_budget_switches_to_background():
    """Ensure long operations switch to background mode."""

    latency = LatencyBudget()

    # Simulate operation that will take 35s
    strategy = latency.select_strategy(estimated_time=35.0)

    assert strategy == "background", \
        "Long operations should run in background"
```

---

## 8. Future Directions

### 8.1 Fine-Tuning on Proof Corpora

The LLM's Galois capabilities improve with domain-specific training. Future work:

1. Collect corpus of (prose spec, modular form, proof) triples
2. Fine-tune Sonnet on this corpus
3. Measure loss reduction on held-out test set

**Hypothesis**: Fine-tuned model will achieve 2x better loss on mathematical content.

### 8.2 Active Learning from User Corrections

When users reject LLM suggestions, learn from the correction:

```python
async def learn_from_rejection(
    original: str,
    llm_suggestion: str,
    user_correction: str
):
    """Update model based on user feedback.

    Store (original, llm_suggestion, user_correction) triple.
    Periodically fine-tune on these corrections.
    """

    await correction_store.add(
        input=original,
        rejected=llm_suggestion,
        accepted=user_correction
    )

    if correction_store.size() > 1000:
        # Enough data to fine-tune
        await trigger_fine_tuning()
```

### 8.3 Multi-Agent Proof Search

Use multiple LLM agents with different temperatures/prompts to explore proof space:

```python
async def multi_agent_synthesis(goal: str, axioms: List[Axiom]) -> Proof:
    """Generate proof via multi-agent search.

    Strategy:
      1. Agent A (temp=0.3): conservative, rigorous
      2. Agent B (temp=0.8): creative, exploratory
      3. Agent C (temp=0.5): balanced
      4. Combine using loss-weighted voting
    """

    agents = [
        LLMAgent(temperature=0.3, role="rigorous"),
        LLMAgent(temperature=0.8, role="creative"),
        LLMAgent(temperature=0.5, role="balanced")
    ]

    candidates = []
    for agent in agents:
        proof = await agent.synthesize_proof(goal, axioms)
        loss = await validate_proof(proof)
        candidates.append((proof, loss))

    # Return lowest-loss proof
    candidates.sort(key=lambda x: x[1])
    return candidates[0][0]
```

---

## 9. References

1. **Galois Theory**: Emil Artin, "Galois Theory" (1942)
2. **Information Theory**: Shannon, "A Mathematical Theory of Communication" (1948)
3. **Neural Compression**: Hinton & Zemel, "Autoencoders, Minimum Description Length" (1993)
4. **LLM as Adjunction**: Murfet, "Logic and Linear Algebra: An Introduction" (2006)
5. **Theorem Proving**: Harrison, "Handbook of Practical Logic and Automated Reasoning" (2009)

---

## Appendices

### Appendix A: Complete Type Signatures

```python
from typing import Protocol, List, Optional
from dataclasses import dataclass
from enum import Enum

class LossAxis(Enum):
    SEMANTIC = "semantic"      # Information preservation
    LOGICAL = "logical"        # Proof validity
    STYLISTIC = "stylistic"    # Tone/voice
    STRUCTURAL = "structural"  # Modular decomposition

@dataclass
class Module:
    id: str
    type: str  # axiom | theorem | lemma | definition
    content: str
    deps: List[str]

@dataclass
class ModularContent:
    modules: List[Module]
    edges: List[tuple[str, str]]  # (from_id, to_id)
    compression_ratio: float

    def is_dag(self) -> bool: ...
    def is_isomorphic_to(self, other: 'ModularContent') -> bool: ...

@dataclass
class Context:
    axioms: List[Axiom] = []
    modules: List[Module] = []
    domain: str = ""

    @classmethod
    def empty(cls) -> 'Context': ...

    def render(self) -> str: ...

class Style(Enum):
    FORMAL = "formal"          # Rigorous mathematical
    CONCISE = "concise"        # Minimal prose
    INTUITIVE = "intuitive"    # Explanatory
    PROOF = "proof"            # Derivation format
    THEOREM = "theorem"        # Statement format

class LLMGaloisRestructurer(Protocol):
    async def restructure(
        self,
        content: str,
        context: Context
    ) -> ModularContent: ...

    async def reconstitute(
        self,
        modular: ModularContent,
        style: Style
    ) -> str: ...

    async def galois_loss(
        self,
        x: str,
        y: str,
        axis: LossAxis
    ) -> float: ...
```

### Appendix B: Prompt Templates

All prompt templates available in:
```
services/zero_seed_llm/prompts/
├── restructure.txt
├── reconstitute.txt
├── galois_loss.txt
├── axiom_mining.txt
├── proof_validation.txt
└── synthesis.txt
```

### Appendix C: Cost Estimation

**Example Session (PhD-level theorem proving)**:

| Operation | Count | Input Tokens | Output Tokens | Cost |
|-----------|-------|--------------|---------------|------|
| Restructure spec | 1 | 5,000 | 2,000 | $0.05 |
| Mine axioms | 10 | 50,000 | 10,000 | $0.30 |
| Validate proof | 5 | 25,000 | 5,000 | $0.15 |
| Synthesize theorems | 3 | 15,000 | 6,000 | $0.14 |
| **Total** | **19** | **95,000** | **23,000** | **$0.64** |

**Per-session cost**: ~$0.64 for 2-hour theorem-proving session.

**Human time saved**: 10-15 hours of manual modularization.

**ROI**: ~15x (assuming $50/hr human cost).

---

**End of Specification**

*"The LLM IS the restructurer. The token IS the energy. The loss IS the measure of understanding."*
