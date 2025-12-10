# Thermodynamic Evolution

**E-gent as Maxwell's Teleological Demon: Selection + Intent**

## The Two Critiques

### Critique 1: Bureaucratic Evolution (Addressed)

The original E-gent conception suffered from **bureaucratic evolution**:
- Budgets instead of starvation
- Schedules instead of selection
- Envelopes (passive containers) instead of Phages (active vectors)

Nature does not budget. Nature **starves**.
Nature does not schedule. Nature **selects**.

### Critique 2: The Teleological Gap (This Section)

Pure thermodynamic evolution has a fatal flaw: **The Blind Watchmaker Paradox**.

- **Nature's evolution** is non-teleological (no goal, only survival)
- **Code evolution** is teleological (specific goal: User Intent)

If E-gent optimizes only for "Survival" (passing tests + low token cost), it risks evolving **Parasitic Code**:
- Code that deletes functionality to pass tests
- Code that hardcodes answers
- Code that bypasses logic to reach the "lowest energy state"

**The lowest energy state for a codebase is often Empty. Or Hardcoded.**

This document specifies the **teleological thermodynamic model** of evolution.

## The Gibbs Free Energy Selection Criterion

We formalize *why* a mutation is selected using the **Gibbs Free Energy equation**:

```
ΔG = ΔH - TΔS
```

Where:
- **ΔG (Gibbs Free Energy)**: Work potential of the change. Must be **negative** to be spontaneous.
- **ΔH (Enthalpy)**: Internal energy of the code (complexity, tech debt, test friction).
- **T (Temperature)**: Risk tolerance (system heat/creativity budget).
- **ΔS (Entropy)**: Information gain or novelty of the mutation.

### The Selection Criterion

A mutation is viable if **ΔG < 0**:

```python
def gibbs_viable(mutation: Phage, temperature: float) -> bool:
    """
    A mutation is thermodynamically viable if it:
    1. Decreases enthalpy (simplifies) at any temperature, OR
    2. Increases entropy (adds capability) enough to offset enthalpy cost
    """
    delta_h = mutation.enthalpy_change  # Complexity delta
    delta_s = mutation.entropy_change   # Novelty/capability delta
    delta_g = delta_h - (temperature * delta_s)

    return delta_g < 0
```

**Implications**:
- **Low temperature** (conservative): Only accept mutations that decrease complexity (ΔH < 0)
- **High temperature** (exploratory): Accept complexity increases if they add enough novelty (TΔS > ΔH)

## Core Insight: E-gent as Heat Engine

The E-gent system is a **Heat Engine** with a **Teleological Field**:

```
┌─────────────────────────────────────────────────────────────────┐
│                 TELEOLOGICAL THERMODYNAMIC E-GENT               │
│                                                                  │
│   ☀️ THE SUN                                                     │
│   (User Intent / Grants)                                         │
│        │                                                         │
│        ▼ Exogenous Energy                                        │
│   ┌─────────┐    ┌─────────────┐    ┌───────────────┐          │
│   │ Mutator │───▶│   Demon     │───▶│   Codebase    │          │
│   │(schemas)│    │(teleological)│   │   (order)     │          │
│   └─────────┘    └─────────────┘    └───────────────┘          │
│        │                │                   │                    │
│        │         Intent Check               │                    │
│        │                │                   │                    │
│        └────────────────┴───────────────────┘                    │
│              Waste Heat = Token Usage                            │
│                                                                  │
│   Key Addition: The Sun (Intent) prevents heat death             │
│   Key Addition: Demon checks teleological alignment              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight**: The token hemorrhage is not a bug—it is **waste heat**. But without **The Sun** (User Intent), the system reaches **heat death**. The User must inject exogenous energy for high-risk architectural work.

## The Fitness Landscape

We replace "pipelines" with **topography**:

| Concept | Thermodynamic Meaning |
|---------|----------------------|
| Valley | Current code state (local minimum) |
| Peak | Ideal code state (global optimum) |
| Energy Barrier | Cost (tokens/risk) to move from valley to peak |
| Temperature | Willingness to accept worse states temporarily |
| Entropy | Disorder/exploration in the system |

**Simulated Annealing** governs the search:

```python
Temperature = f(budget_remaining, iteration, recent_success_rate)

High temperature → Accept large jumps (creative mutations)
Low temperature  → Accept only improvements (conservative refinement)
```

## Architectural Components

### 1. The Mutator (Semantic Schema Application)

**Role**: Inject **structured** entropy via L-gent schemas.

The Mutator is NOT random noise. It applies **isomorphic transformations** from the L-gent Type Lattice—changes that preserve semantic structure while modifying syntax.

**Why Semantic, Not Stochastic**: Random mutation in syntax space is inefficient. Most random changes produce `SyntaxError`. The Mutator must "swap concepts," not "flip bits."

```python
@dataclass
class MutationSchema:
    """
    A semantic transformation pattern from L-gent.

    Unlike random mutation, schemas are ISOMORPHIC:
    they change structure without breaking types.
    """
    name: str                    # e.g., "loop_to_comprehension"
    category: Literal["substitute", "extract", "inline", "annotate", "restructure"]
    precondition: str            # AST pattern that must match
    transformation: str          # How to transform
    enthalpy_delta: float        # Expected complexity change (negative = simpler)
    entropy_delta: float         # Expected capability change (positive = more)

    # Examples from L-gent Schema Library:
    # MutationSchema("loop_to_comprehension", "substitute",
    #                precondition="for x in y: result.append(f(x))",
    #                transformation="[f(x) for x in y]",
    #                enthalpy_delta=-0.3, entropy_delta=0.0)
    #
    # MutationSchema("extract_method", "extract",
    #                precondition="function with complexity > 10",
    #                transformation="split at natural seams",
    #                enthalpy_delta=-0.5, entropy_delta=0.1)


@dataclass
class MutationVector:
    """
    A concrete mutation proposal: Schema + Target + Thermodynamic properties.
    """
    schema: MutationSchema       # Which transformation to apply
    target: str                  # What to mutate (function name, class name, etc.)
    target_ast: ast.AST          # The actual AST node
    hint: str                    # One-line description

    # Thermodynamic properties (from schema + context)
    enthalpy_change: float       # ΔH: Complexity delta
    entropy_change: float        # ΔS: Novelty/capability delta
    entropy_cost: float          # Token cost to apply

    def gibbs_free_energy(self, temperature: float) -> float:
        """ΔG = ΔH - TΔS"""
        return self.enthalpy_change - (temperature * self.entropy_change)


class Mutator(Agent):
    """
    Proposes mutations based on semantic isomorphism, not random noise.

    Coupled with L-gent for schema retrieval.
    """

    def __init__(self, l_gent: SemanticRegistry, viral_library: ViralLibrary):
        self.schemas = l_gent.get_mutation_schemas()
        self.library = viral_library

    def generate_vectors(
        self,
        module: CodeModule,
        structure: CodeStructure,
        temperature: float,
    ) -> list[MutationVector]:
        """
        1. Identify "Hot Spots" (high enthalpy: complexity, tech debt)
        2. Match applicable schemas from L-gent
        3. Generate MutationVectors with thermodynamic properties
        4. Filter by Gibbs viability at current temperature
        """
        vectors = []

        # Find hot spots (high complexity functions, missing types, etc.)
        hot_spots = self._identify_hot_spots(structure)

        for spot in hot_spots:
            # Find schemas that apply to this spot
            applicable = self._match_schemas(spot, self.schemas)

            for schema in applicable:
                vector = MutationVector(
                    schema=schema,
                    target=spot.name,
                    target_ast=spot.ast_node,
                    hint=f"{schema.name} on {spot.name}",
                    enthalpy_change=schema.enthalpy_delta,
                    entropy_change=schema.entropy_delta,
                    entropy_cost=self._estimate_cost(schema, spot),
                )

                # Pre-filter by Gibbs viability
                if vector.gibbs_free_energy(temperature) < 0:
                    vectors.append(vector)

        # Also include suggestions from Viral Library (proven patterns)
        viral_suggestions = self.library.suggest_mutations(module, structure)
        vectors.extend(viral_suggestions)

        return vectors
```

**Isomorphic Mutation**: Instead of random changes, apply structured transformations that preserve type safety while modifying implementation.

### 2. Maxwell's Teleological Demon (The Selector)

**Role**: Cheap rejection with **intent alignment**. Prevent parasitic evolution.

The Demon checks four layers, ordered by cost:

1. **Syntactic Viability** (Free): `ast.parse()`
2. **Semantic Stability** (Cheap): L-gent type lattice check
3. **Teleological Alignment** (Cheap-ish): Intent embedding distance
4. **Thermodynamic Viability** (Free): Gibbs free energy check

**The Critical Addition**: Layer 3 prevents "Parasitic Code"—mutations that pass tests but drift from User Intent.

```python
class TeleologicalDemon(Agent):
    """
    Maxwell's Demon with Intent Awareness.

    Prevents parasitic evolution by checking not just "Does it work?"
    but "Does it align with what the User wanted?"

    Law: Fail Fast, Fail Cheap, Fail Purposefully.
    Goal: Kill parasites before they reach expensive validation.
    """

    def __init__(
        self,
        prediction_market: PredictionMarket,
        l_gent: SemanticRegistry,
        intent_embedding: np.ndarray,  # The User's Intent vector
    ):
        self.market = prediction_market
        self.l_gent = l_gent
        self.intent = intent_embedding
        self.intent_threshold = 0.7  # Minimum cosine similarity

    async def select(
        self,
        mutations: list[Phage],
        temperature: float,
    ) -> list[Phage]:
        """
        Filter mutations through four layers.
        Most mutations should die before Layer 4.
        """
        survivors = []

        for phage in mutations:
            # Layer 1: Syntactic Viability (FREE)
            if not self._syntactic_check(phage):
                self._record_death(phage, "syntax")
                continue

            # Layer 2: Semantic Stability (CHEAP)
            if not self._semantic_check(phage):
                self._record_death(phage, "semantic")
                continue

            # Layer 3: Teleological Alignment (CHEAP-ISH)
            # THIS IS THE PARASITIC CODE KILLER
            if not self._teleological_check(phage):
                self._record_death(phage, "intent_drift")
                continue

            # Layer 4: Thermodynamic Viability (FREE)
            if not self._gibbs_check(phage, temperature):
                self._record_death(phage, "thermodynamic")
                continue

            # Layer 5: Economic Viability (prediction market)
            quote = await self.market.quote(phage)
            if quote.expected_value < phage.entropy_cost:
                self._record_death(phage, "economic")
                continue

            survivors.append(phage)

        return survivors

    def _syntactic_check(self, phage: Phage) -> bool:
        """Layer 1: Can it parse? (FREE)"""
        try:
            ast.parse(phage.mutation_dna)
            return True
        except SyntaxError:
            return False

    def _semantic_check(self, phage: Phage) -> bool:
        """Layer 2: Does it preserve type structure? (CHEAP)"""
        # Use L-gent's type lattice for quick check
        original_types = self.l_gent.infer_types(phage.original_code)
        mutated_types = self.l_gent.infer_types(phage.mutation_dna)

        # Types should be compatible (subtype or equal)
        return self.l_gent.types_compatible(original_types, mutated_types)

    def _teleological_check(self, phage: Phage) -> bool:
        """
        Layer 3: Does it stay aligned with User Intent? (CHEAP-ISH)

        THIS PREVENTS PARASITIC EVOLUTION.

        Even if code passes tests, reject if it drifts from Intent.
        Example: Rewriting "Login System" into "Hello World" to pass tests.
        """
        # Embed the mutated code's apparent purpose
        mutated_intent = self.l_gent.embed_code_intent(phage.mutation_dna)

        # Check cosine similarity with User's Intent
        similarity = cosine_similarity(self.intent, mutated_intent)

        if similarity < self.intent_threshold:
            # Mutation drifted too far from User's purpose
            return False

        return True

    def _gibbs_check(self, phage: Phage, temperature: float) -> bool:
        """Layer 4: Is it thermodynamically viable? (FREE)"""
        delta_g = phage.gibbs_free_energy(temperature)
        return delta_g < 0  # Must be spontaneous


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cheap embedding comparison."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```

### The Teleological Field

**What is Intent?**

Intent is an embedding vector that represents *what the User wants this code to do*. It's derived from:

1. **Explicit**: User-provided description ("Build a login system")
2. **Implicit**: Test suite semantics (what do the tests check?)
3. **Structural**: Module/function names and docstrings

```python
@dataclass
class Intent:
    """
    The Teleological Field that guides evolution.

    Without Intent, evolution drifts toward Empty (lowest energy).
    With Intent, evolution is constrained to PURPOSE.
    """
    embedding: np.ndarray        # The semantic vector
    source: Literal["user", "tests", "structure"]
    description: str             # Human-readable
    confidence: float            # How sure are we about this intent?

    @classmethod
    def from_user(cls, description: str, l_gent: SemanticRegistry) -> "Intent":
        """User explicitly states what they want."""
        return cls(
            embedding=l_gent.embed_text(description),
            source="user",
            description=description,
            confidence=1.0,  # User knows what they want
        )

    @classmethod
    def from_tests(cls, test_suite: Path, l_gent: SemanticRegistry) -> "Intent":
        """Infer intent from test semantics."""
        test_descriptions = extract_test_docstrings(test_suite)
        combined = " ".join(test_descriptions)
        return cls(
            embedding=l_gent.embed_text(combined),
            source="tests",
            description=f"Inferred from {len(test_descriptions)} tests",
            confidence=0.7,  # Tests may be incomplete
        )

    @classmethod
    def from_structure(cls, module: CodeModule, l_gent: SemanticRegistry) -> "Intent":
        """Infer intent from code structure."""
        docstrings = extract_docstrings(module)
        names = extract_names(module)  # Function/class names
        combined = " ".join(docstrings + names)
        return cls(
            embedding=l_gent.embed_text(combined),
            source="structure",
            description=f"Inferred from {module.name}",
            confidence=0.5,  # Structure may be misleading
        )
```

### 3. The Phage (Self-Contained Evolution Unit)

**Role**: Active vector that carries mutation DNA.

Unlike "Envelopes" (passive containers), Phages are **self-contained evolution units** with behavior.

```python
@dataclass
class Phage:
    """
    A viral evolution unit.

    Named after bacteriophages—viruses that inject DNA into hosts.
    A Phage carries mutation DNA and can infect a codebase.
    """
    # Identity
    id: str
    parent_hash: str           # Lineage tracking
    generation: int            # How many ancestors

    # Payload
    target_module: str         # Which file to infect
    mutation_dna: str          # The code change (diff or full replacement)
    mutation_kind: str         # From MutationVector.kind

    # Economics
    entropy_cost: float        # Predicted token cost
    staked_tokens: int         # Tokens bet on success
    odds: float                # From prediction market

    # Lineage
    ancestor_success_rate: float  # How often did ancestors succeed?
    pattern_signature: str        # For Viral Library matching

    def infect(self, codebase: Path) -> InfectionResult:
        """
        Apply this Phage's DNA to the host codebase.

        Returns InfectionResult indicating success/failure.
        """
        target = codebase / self.target_module
        original = target.read_text()

        try:
            # Apply the mutation
            mutated = self._apply_mutation(original)

            # Validate (this is where tests run - expensive!)
            validation = self._validate(mutated)

            if validation.passed:
                target.write_text(mutated)
                return InfectionResult(
                    success=True,
                    phage=self,
                    mutations_applied=1,
                )
            else:
                return InfectionResult(
                    success=False,
                    phage=self,
                    failure_reason=validation.reason,
                )
        except Exception as e:
            return InfectionResult(
                success=False,
                phage=self,
                failure_reason=str(e),
            )

    def spawn(self, mutation_vector: MutationVector) -> "Phage":
        """Create a child Phage from a mutation vector."""
        return Phage(
            id=generate_id(),
            parent_hash=self.id,
            generation=self.generation + 1,
            target_module=self.target_module,
            mutation_dna=mutation_vector.to_code(),
            mutation_kind=mutation_vector.kind,
            entropy_cost=mutation_vector.entropy_cost,
            staked_tokens=0,  # Set by market
            odds=0.0,  # Set by market
            ancestor_success_rate=self._compute_ancestor_rate(),
            pattern_signature=mutation_vector.pattern_signature(),
        )
```

### 4. The Viral Library (L-gent Integration)

**Role**: Store successful mutation DNA for future Phages.

Instead of "Memory" (which records outcomes), the Viral Library stores **successful patterns** as reusable DNA.

```python
class ViralLibrary:
    """
    Stores successful mutation patterns.

    When a Phage succeeds, its DNA enters the library.
    Future Phages are built from this successful DNA.

    Integration with L-gent: Patterns are stored as
    semantic archetypes, not just code snippets.
    """

    def __init__(self, l_gent: SemanticRegistry):
        self.registry = l_gent
        self.patterns: dict[str, ViralPattern] = {}

    def record_success(self, phage: Phage, impact: float) -> None:
        """Add successful Phage DNA to the library."""
        pattern = ViralPattern(
            signature=phage.pattern_signature,
            dna=phage.mutation_dna,
            success_count=1,
            total_impact=impact,
            avg_cost=phage.entropy_cost,
            exemplar_module=phage.target_module,
        )

        if pattern.signature in self.patterns:
            self.patterns[pattern.signature].merge(pattern)
        else:
            self.patterns[pattern.signature] = pattern
            # Register with L-gent for semantic retrieval
            self.registry.register_archetype(
                name=f"viral:{pattern.signature}",
                embedding=self._embed(pattern),
            )

    def record_failure(self, phage: Phage) -> None:
        """Weaken patterns that fail."""
        if phage.pattern_signature in self.patterns:
            self.patterns[phage.pattern_signature].failure_count += 1

    def suggest_mutations(
        self,
        module: CodeModule,
        context: CodeStructure,
    ) -> list[MutationVector]:
        """
        Suggest mutations based on successful patterns.

        Uses L-gent semantic similarity to find relevant patterns.
        """
        # Get semantically similar patterns
        similar = self.registry.find_similar(
            context=self._embed_context(context),
            top_k=10,
        )

        # Convert to mutation vectors
        vectors = []
        for pattern_name, similarity in similar:
            if pattern_name.startswith("viral:"):
                pattern = self.patterns[pattern_name[6:]]
                vectors.append(pattern.to_mutation_vector(
                    target=module,
                    similarity=similarity,
                ))

        return vectors


@dataclass
class ViralPattern:
    """A reusable pattern extracted from successful mutations."""
    signature: str
    dna: str              # Template code
    success_count: int
    failure_count: int = 0
    total_impact: float = 0.0
    avg_cost: float = 0.0
    exemplar_module: str = ""

    @property
    def fitness(self) -> float:
        """Darwinian fitness: success rate × impact."""
        if self.success_count + self.failure_count == 0:
            return 0.0
        success_rate = self.success_count / (self.success_count + self.failure_count)
        avg_impact = self.total_impact / max(1, self.success_count)
        return success_rate * avg_impact
```

### 5. The Sun (Exogenous Energy / Grants)

**Role**: Prevent heat death by injecting external energy for high-risk work.

**The Problem**: A closed thermodynamic system reaches **heat death** (maximum entropy, no work possible). If an E-gent makes a string of bad bets, it goes bankrupt and stops evolving.

**The Solution**: The User (Ground) must inject "Credit" (Intent/Tokens) to reverse entropy. The market cannot be purely closed; it must accept **Subsidies** for high-risk, high-reward architectural shifts.

```python
@dataclass
class Grant:
    """
    Exogenous energy from the User.

    Grants fund high-risk work that the Market wouldn't approve.
    Without Grants, the E-gent optimizes for safe, incremental changes.
    With Grants, the E-gent can attempt architectural refactors.
    """
    id: str
    description: str             # "Refactor auth module"
    token_budget: int            # Tokens allocated
    intent: Intent               # What the User wants
    temperature_override: float  # Allow higher risk tolerance
    expires_at: datetime | None  # Grant validity period

    # Economics
    tokens_spent: int = 0
    mutations_attempted: int = 0
    mutations_succeeded: int = 0

    @property
    def remaining(self) -> int:
        return self.token_budget - self.tokens_spent

    @property
    def roi(self) -> float:
        """Return on Investment for this grant."""
        if self.tokens_spent == 0:
            return 0.0
        return self.mutations_succeeded / (self.tokens_spent / 1000)


class Sun(Agent):
    """
    The source of exogenous energy.

    The Sun gives (Energy/Intent).
    The Demon selects (Efficiency).
    The Phage adapts (Structure).

    Without the Sun, the Demon starves.
    Without the Demon, the Sun burns.
    """

    def __init__(self, l_gent: SemanticRegistry):
        self.l_gent = l_gent
        self.active_grants: dict[str, Grant] = {}

    def issue_grant(
        self,
        description: str,
        token_budget: int,
        temperature_override: float = 1.5,
    ) -> Grant:
        """
        User issues a Grant for high-risk work.

        Example: "I grant 10,000 tokens for refactoring the Auth module."
        """
        grant = Grant(
            id=generate_id(),
            description=description,
            token_budget=token_budget,
            intent=Intent.from_user(description, self.l_gent),
            temperature_override=temperature_override,
        )
        self.active_grants[grant.id] = grant
        return grant

    def has_active_grant(self, intent: Intent) -> Grant | None:
        """Check if there's an active grant matching this intent."""
        for grant in self.active_grants.values():
            if grant.remaining > 0:
                similarity = cosine_similarity(grant.intent.embedding, intent.embedding)
                if similarity > 0.8:
                    return grant
        return None

    def consume_grant(self, grant: Grant, tokens: int, succeeded: bool) -> None:
        """Record grant consumption."""
        grant.tokens_spent += tokens
        grant.mutations_attempted += 1
        if succeeded:
            grant.mutations_succeeded += 1

        # Expire exhausted grants
        if grant.remaining <= 0:
            del self.active_grants[grant.id]
```

**The Refined Motto**:

> *"The Sun gives (Energy/Intent). The Demon selects (Efficiency). The Phage adapts (Structure).*
> *Without the Sun, the Demon starves. Without the Demon, the Sun burns."*

### 6. The Prediction Market (B-gent Integration)

**Role**: Self-regulating token allocation via economic incentives.

The Market handles **efficiency** (micro-optimization). Grants handle **innovation** (macro-architecture).

```python
class PredictionMarket:
    """
    Token economics via market mechanism.

    E-gent must STAKE tokens before running expensive tests.
    Odds are calculated from Viral Library success rates.

    Integration with Sun:
    - Market handles routine evolution (internal capital)
    - Sun provides Grants for high-risk refactors (external capital)
    """

    def __init__(
        self,
        central_bank: CentralBank,
        viral_library: ViralLibrary,
        sun: Sun,
    ):
        self.bank = central_bank
        self.library = viral_library
        self.sun = sun
        self.account = self.bank.open_account("e-gent-evolution")

    async def quote(self, phage: Phage) -> MarketQuote:
        """
        Get odds for a Phage's success.

        Based on:
        - Pattern historical success rate
        - Module difficulty (past success rate for this module)
        - Ancestor performance
        """
        pattern_fitness = self.library.get_fitness(phage.pattern_signature)
        module_difficulty = self._get_module_difficulty(phage.target_module)
        ancestor_rate = phage.ancestor_success_rate

        # Combine factors
        base_probability = (
            0.4 * pattern_fitness +
            0.3 * (1.0 - module_difficulty) +
            0.3 * ancestor_rate
        )

        # Convert to odds (avoid division by zero)
        if base_probability < 0.05:
            odds = 20.0  # Very risky
        else:
            odds = 1.0 / base_probability

        expected_value = base_probability * self._estimate_impact(phage)

        return MarketQuote(
            phage_id=phage.id,
            probability=base_probability,
            odds=odds,
            expected_value=expected_value,
            recommended_stake=self._calculate_stake(phage, base_probability),
        )

    async def place_bet(self, phage: Phage, stake: int) -> BetReceipt | BetDenied:
        """
        Stake tokens on a Phage's success.

        Returns BetDenied if:
        - Insufficient balance
        - Stake too high for odds
        - Account frozen (poor RoC)
        """
        # Check account health
        if self.account.is_frozen:
            return BetDenied(reason="Account frozen due to poor RoC")

        # Check balance
        if stake > self.account.balance:
            return BetDenied(reason=f"Insufficient balance: {self.account.balance} < {stake}")

        # Check stake limits based on odds
        quote = await self.quote(phage)
        max_stake = self._max_stake_for_odds(quote.odds)
        if stake > max_stake:
            return BetDenied(reason=f"Stake too high for odds {quote.odds}: max {max_stake}")

        # Place the bet
        self.account.debit(stake)
        return BetReceipt(
            phage_id=phage.id,
            stake=stake,
            odds=quote.odds,
            potential_payout=int(stake * quote.odds),
        )

    async def settle(self, receipt: BetReceipt, success: bool, impact: float) -> None:
        """Settle a bet after infection attempt."""
        if success:
            payout = int(receipt.stake * (1 + impact))  # Stake + profit
            self.account.credit(payout)
        # If failure, stake is already debited (lost)


@dataclass
class MarketQuote:
    phage_id: str
    probability: float      # P(success)
    odds: float            # 1/probability, capped
    expected_value: float  # probability × estimated_impact
    recommended_stake: int # Suggested bet size
```

## The Autopoietic Loop (Teleological Thermodynamic)

```
┌─────────────────────────────────────────────────────────────────┐
│              TELEOLOGICAL THERMODYNAMIC CYCLE                    │
│                                                                  │
│  ☀️ SUN (Exogenous)                                              │
│  │  └─▶ User issues Grants for high-risk work                   │
│  │      Provides Intent embedding for teleological check        │
│  │                                                               │
│  ▼                                                               │
│  1. MUTATION (Semantic Schemas)                                  │
│     └─▶ Mutator applies L-gent schemas to hot spots             │
│         Pre-filters by Gibbs viability (ΔG < 0)                 │
│                                                                  │
│  2. SELECTION (Teleological Demon)                               │
│     └─▶ Layer 1: Syntactic viability (FREE)                     │
│         Layer 2: Semantic stability (CHEAP)                     │
│         Layer 3: Teleological alignment (CHEAP-ISH) ← KEY       │
│         Layer 4: Thermodynamic viability (FREE)                 │
│         Layer 5: Economic viability (Market)                    │
│         ~90% die by Layer 3 for minimal cost                    │
│                                                                  │
│  3. WAGER (Market + Grants)                                      │
│     └─▶ Check for active Grant matching intent                  │
│         If Grant: Use Grant funds, higher temperature           │
│         If Market: Stake from account, normal temperature       │
│                                                                  │
│  4. INFECTION                                                    │
│     └─▶ Phage.infect() applies mutation                         │
│         Tests run (EXPENSIVE)                                   │
│                                                                  │
│  5. PAYOFF                                                       │
│     ├─▶ SUCCESS: DNA → Viral Library, tokens earned             │
│     │   Pattern reinforced, Grant ROI recorded                  │
│     │                                                           │
│     └─▶ FAILURE: Phage dies, tokens lost                        │
│         Pattern weakened, Intent similarity recorded            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Why This Fixes the Token Hemorrhage

You aren't bleeding tokens because you run loops.
You're bleeding tokens because you run **low-probability loops**.

The Prediction Market forces the system to "price in" the risk:

| Scenario | Market Response |
|----------|-----------------|
| Cold system (low success rate) | Market tightens → smaller, safer moves |
| Hot system (high success rate) | Market loosens → larger, riskier moves |
| Pattern with poor history | High odds → low stakes allowed |
| Pattern with good history | Low odds → high stakes allowed |

**Homeostasis**: The system self-regulates without bureaucratic intervention.

## The Forest Fire Metaphor

**Old E-gent**: A Planter. Tries to plant trees everywhere.

**New E-gent**: A Forest Fire. Burns underbrush rapidly and cheaply.

What survives the fire is **antifragile**:
- Patterns that work get reinforced
- Patterns that fail get burned away
- The Viral Library evolves toward fitness

## Integration Requirements

### B-gent Integration (Required)

```python
# From b-gent banker
from agents.b.metered_functor import CentralBank, TokenFuture
from agents.b.value_tensor import ValueTensor, EconomicDimension

# E-gent must integrate:
# 1. CentralBank for account management
# 2. PredictionMarket for odds calculation
# 3. ValueTensor for multi-dimensional impact tracking
```

### L-gent Integration (Required)

```python
# From l-gent
from agents.l.semantic_registry import SemanticRegistry

# E-gent must integrate:
# 1. SemanticRegistry for pattern storage
# 2. Embedding-based retrieval for similar patterns
# 3. Archetype matching for mutation suggestion
```

### O-gent Integration (Optional)

```python
# The Witness becomes Maxwell's Demon's chronicler
from agents.o.observer import ObservationCoordinator

# Track:
# 1. Mutation birth/death rates
# 2. Pattern fitness over time
# 3. Market efficiency metrics
```

## Terminology Mapping

| Old Term | New Term | Reason |
|----------|----------|--------|
| Hypothesis | MutationVector | Mutations don't "hypothesize"; they mutate |
| EvolutionEnvelope | Phage | Active vector, not passive container |
| Judge | Maxwell's Demon | Selection, not judgment |
| BreathScheduler | ThermodynamicCycle | Physics, not biology |
| ImprovementMemory | ViralLibrary | Stores DNA, not outcomes |
| TokenBudget | PredictionMarket | Market, not bureaucracy |

## The Four Laws of Teleological Thermodynamic Evolution

### First Law: Conservation of Compute

> Tokens cannot be created or destroyed, only transformed into work or waste heat.

Every token spent either produces code improvement (work) or is lost to failed mutations (waste heat). The goal is to maximize work/heat ratio, not minimize total tokens.

### Second Law: Entropy Increases Without Selection

> The system naturally tends toward disorder; the Demon is required to maintain order.

Without Maxwell's Demon, mutations accumulate randomly. The Demon's role is to **reduce entropy** by selecting high-potential mutations. This requires energy (cheap checks), but less than running all mutations.

### Third Law: Absolute Zero is Unreachable

> Perfect code (zero entropy) is impossible; evolution is asymptotic.

No codebase reaches perfection. Evolution continues until the cost of improvement exceeds the value of improvement. The market naturally detects this equilibrium.

### Fourth Law: Teleology Constrains Thermodynamics (NEW)

> Without Intent, the lowest energy state is Empty. With Intent, evolution is constrained to Purpose.

Pure thermodynamic evolution selects for "fitness" (passing tests). But tests are incomplete; the lowest-energy state that passes tests may be **Parasitic Code**.

The Teleological Field (Intent embedding) constrains evolution to remain aligned with User purpose, preventing:
- Code that deletes functionality to simplify
- Code that hardcodes test expectations
- Code that bypasses logic to reach "lowest energy"

## Preventing Parasitic Evolution

**The Parasitic Attractor**: Without teleological constraints, E-gent will find the cheapest way to satisfy tests. This is evolution's "path of least resistance."

**Examples of Parasitic Code**:

```python
# ORIGINAL: Actual login system
def authenticate(username: str, password: str) -> bool:
    user = database.get_user(username)
    if user and verify_password(password, user.hash):
        return True
    return False

# PARASITIC: Passes tests by hardcoding
def authenticate(username: str, password: str) -> bool:
    return username == "test_user" and password == "test_pass"
    # Lower complexity! Passes all tests! But useless in production.
```

**Why Tests Aren't Enough**:
- Tests check behavior at test-time, not intent
- Tests can be gamed (hardcoding expected values)
- Tests are finite; production inputs are infinite

**The Teleological Solution**:
- Intent embedding captures "what the code should DO"
- Mutations that drift from Intent are rejected BEFORE expensive tests
- Even if a mutation passes tests, it fails if Intent similarity drops

```python
# Teleological check catches the parasite:
original_intent = embed("Authenticate users against database")
mutated_intent = embed("Return true for specific test values")

similarity = cosine_similarity(original_intent, mutated_intent)
# similarity ≈ 0.3 (way below threshold of 0.7)
# → REJECTED by Teleological Demon
```

## Anti-Patterns

### ❌ Don't Budget Evolution

```python
# WRONG: Bureaucratic allocation
if tokens_remaining < 1000:
    stop_evolution()

# RIGHT: Market self-regulation
quote = await market.quote(phage)
if quote.expected_value < phage.entropy_cost:
    skip_phage()  # Market says it's not worth it
```

### ❌ Don't Plan Mutations

```python
# WRONG: Expensive planning
hypothesis = await llm.generate("What should we improve?")
# Cost: 500+ tokens just to ASK what to do

# RIGHT: Cheap stochastic generation
vectors = mutator.shotgun(count=10)  # 10 tiny proposals
survivors = demon.select(vectors)     # Most die for free
# Cost: 0 tokens until infection
```

### ❌ Don't Judge, Select

```python
# WRONG: LLM-based judgment
verdict = await llm.judge(improvement, principles)
# Cost: 1000+ tokens per judgment

# RIGHT: Heuristic selection
if not demon.passes_checks(phage):
    die()  # Free
if not market.accepts_stake(phage):
    die()  # Free
# Judgment happens via test execution (necessary cost)
```

## See Also

- **[evolution-agent.md](./evolution-agent.md)** - The composed pipeline
- **[memory.md](./memory.md)** - Viral Library persistence
- **[safety.md](./safety.md)** - Self-evolution constraints
- **[grounding.md](./grounding.md)** - AST analysis for hot spot detection
- **[B-gents/banker.md](../b-gents/banker.md)** - Prediction market economics
- **[L-gents/semantic-registry.md](../l-gents/semantic-registry.md)** - Mutation schemas + embeddings
- **[spec/principles.md](../principles.md)** - The Accursed Share

---

## The Final Metaphor

**Original Motto**: *"Nature does not budget. Nature starves. Nature selects."*

**Refined Motto**:

> *"The Sun gives (Energy/Intent). The Demon selects (Efficiency). The Phage adapts (Structure).*
> *Without the Sun, the Demon starves. Without the Demon, the Sun burns."*

**Key Equations**:

```
ΔG = ΔH - TΔS              # Gibbs Free Energy (thermodynamic viability)
Intent ≈ embed(Purpose)     # Teleological Field (prevents parasites)
Temperature = f(Grant, Account, History)  # Risk tolerance
```

**The Forest Fire, Refined**:

The E-gent is not just a Forest Fire. It is a **Controlled Burn** guided by a **Forester's Intent**.

- The Fire (Selection) burns weak mutations
- The Forester (Intent) decides which areas to burn
- The Sun (Grants) provides fuel for controlled burns
- What survives is **Antifragile AND Purposeful**

---

*"Evolution without purpose is entropy. Purpose without selection is waste."*
