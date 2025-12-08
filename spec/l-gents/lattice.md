# L-gent Lattice: Type Compatibility & Composition Planning

**Purpose**: Define the partial order over types that enables mathematical composition verification and automatic pipeline planning.

---

## Overview

The lattice is L-gent's **type theory engine**. It answers the fundamental question: **"Can these two agents compose?"**

Unlike runtime duck typing that fails at execution, the lattice enables **static composition verification**—proving compatibility before any code runs. This is the mathematical backbone of the ecosystem's composability guarantee.

> "Composition errors should be impossible, not merely detectable."

## Theoretical Foundation

### Partial Order over Types

The lattice is a **bounded meet-semilattice** over types:

```
                        ⊤ (Any)
                       / | \
                      /  |  \
                   JSON Text  Stream
                   /  \   |   / \
                  /    \  |  /   \
             Object  Array String  Bytes
               |       |      |
               ↓       ↓      ↓
           UserRecord [int] "literal"
```

**Definitions**:
- **⊤ (Top)**: The type `Any`—accepts all values
- **⊥ (Bottom)**: The type `Never`—accepts no values
- **≤ (Subtype)**: `A ≤ B` means "every value of type A is also of type B"
- **Meet (∧)**: Greatest lower bound—the most general type that's a subtype of both
- **Join (∨)**: Least upper bound—the most specific type that's a supertype of both

### Compatibility Rule

**Two agents compose if and only if:**

```
compose(Agent[A, B], Agent[C, D]) is valid  ⟺  B ≤ C
```

The output type of the first agent must be a subtype of the input type of the second.

This is the **Liskov Substitution Principle** applied to agent composition:
> "If B ≤ C, then anywhere we expect a C, we can safely provide a B."

## Type Schema

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class TypeKind(Enum):
    """Classification of types in the lattice."""
    PRIMITIVE = "primitive"     # str, int, float, bool, None
    CONTAINER = "container"     # list, dict, set, tuple
    RECORD = "record"           # dataclass, TypedDict
    UNION = "union"             # A | B
    LITERAL = "literal"         # Literal["a", "b"]
    GENERIC = "generic"         # Generic[T]
    CONTRACT = "contract"       # Named interface with invariants
    ANY = "any"                 # Top type
    NEVER = "never"             # Bottom type

@dataclass
class TypeNode:
    """A type in the lattice."""
    id: str                     # Unique identifier
    kind: TypeKind
    name: str                   # Human-readable name

    # For generics
    parameters: list[str] = field(default_factory=list)  # Type parameter names

    # For containers
    element_type: str | None = None  # e.g., list[X] → X

    # For records
    fields: dict[str, str] = field(default_factory=dict)  # field_name → type_id

    # For unions
    members: list[str] = field(default_factory=list)  # Union member type IDs

    # For contracts
    invariants: list[str] = field(default_factory=list)  # Behavioral guarantees

    # Metadata
    defined_at: str | None = None  # Where this type is defined

@dataclass
class SubtypeEdge:
    """A subtyping relationship in the lattice."""
    subtype_id: str             # The more specific type
    supertype_id: str           # The more general type
    reason: str                 # Why this relationship holds
    covariant_positions: list[str] = field(default_factory=list)
    contravariant_positions: list[str] = field(default_factory=list)
```

## Lattice Operations

```python
class TypeLattice:
    """Layer 3: Type compatibility and composition planning."""

    def __init__(self, storage: PersistentAgent):
        self.types: dict[str, TypeNode] = {}
        self.edges: list[SubtypeEdge] = []
        self.storage = storage

    # ─────────────────────────────────────────────────────────────
    # Core Operations
    # ─────────────────────────────────────────────────────────────

    def is_subtype(self, sub: str, super_: str) -> bool:
        """
        Check if sub ≤ super in the lattice.

        Rules:
        1. Reflexivity: A ≤ A
        2. Transitivity: If A ≤ B and B ≤ C then A ≤ C
        3. Any is top: A ≤ Any for all A
        4. Never is bottom: Never ≤ A for all A
        5. Structural subtyping for records
        6. Covariance/contravariance for generics
        """
        if sub == super_:
            return True  # Reflexivity

        if super_ == "Any":
            return True  # Any is top

        if sub == "Never":
            return True  # Never is bottom

        # Check direct edge
        if any(e.subtype_id == sub and e.supertype_id == super_ for e in self.edges):
            return True

        # Transitivity via BFS
        return self._reachable(sub, super_)

    def meet(self, type_a: str, type_b: str) -> str:
        """
        Compute the meet (greatest lower bound) of two types.

        meet(A, B) = largest type C such that C ≤ A and C ≤ B
        """
        if self.is_subtype(type_a, type_b):
            return type_a
        if self.is_subtype(type_b, type_a):
            return type_b

        # Find common subtypes and return the greatest
        subtypes_a = self._all_subtypes(type_a)
        subtypes_b = self._all_subtypes(type_b)
        common = subtypes_a & subtypes_b

        if not common:
            return "Never"  # No common subtype

        # Return the greatest (most general) common subtype
        for candidate in common:
            if all(self.is_subtype(candidate, other) or candidate == other
                   for other in common):
                return candidate

        return "Never"

    def join(self, type_a: str, type_b: str) -> str:
        """
        Compute the join (least upper bound) of two types.

        join(A, B) = smallest type C such that A ≤ C and B ≤ C
        """
        if self.is_subtype(type_a, type_b):
            return type_b
        if self.is_subtype(type_b, type_a):
            return type_a

        # Find common supertypes and return the least
        supertypes_a = self._all_supertypes(type_a)
        supertypes_b = self._all_supertypes(type_b)
        common = supertypes_a & supertypes_b

        if not common:
            return "Any"  # No common supertype except Any

        # Return the least (most specific) common supertype
        for candidate in common:
            if all(self.is_subtype(other, candidate) or candidate == other
                   for other in common):
                return candidate

        return "Any"

    # ─────────────────────────────────────────────────────────────
    # Composition Verification
    # ─────────────────────────────────────────────────────────────

    async def can_compose(
        self,
        first_id: str,
        second_id: str
    ) -> CompositionResult:
        """
        Check if two agents can compose: first >> second.

        Returns detailed result explaining why or why not.
        """
        first = await self.registry.get(first_id)
        second = await self.registry.get(second_id)

        if not first or not second:
            return CompositionResult(
                compatible=False,
                reason="One or both artifacts not found"
            )

        # Check type compatibility
        output_type = first.output_type
        input_type = second.input_type

        if not output_type or not input_type:
            return CompositionResult(
                compatible=False,
                reason="Missing type information"
            )

        if self.is_subtype(output_type, input_type):
            return CompositionResult(
                compatible=True,
                reason=f"Output type {output_type} is subtype of input type {input_type}",
                output_type=output_type,
                input_type=input_type
            )
        else:
            # Check if there's a path via adapter
            adapter = await self._find_adapter(output_type, input_type)
            if adapter:
                return CompositionResult(
                    compatible=True,
                    reason=f"Compatible via adapter: {adapter.id}",
                    requires_adapter=adapter.id
                )

            return CompositionResult(
                compatible=False,
                reason=f"Type mismatch: {output_type} is not subtype of {input_type}",
                output_type=output_type,
                input_type=input_type,
                suggested_fix=self._suggest_fix(output_type, input_type)
            )

    async def verify_pipeline(
        self,
        artifact_ids: list[str]
    ) -> PipelineVerification:
        """
        Verify that a sequence of agents forms a valid pipeline.
        """
        if len(artifact_ids) < 2:
            return PipelineVerification(valid=True, stages=[])

        stages = []
        all_valid = True

        for i in range(len(artifact_ids) - 1):
            result = await self.can_compose(artifact_ids[i], artifact_ids[i + 1])
            stages.append(CompositionStage(
                from_id=artifact_ids[i],
                to_id=artifact_ids[i + 1],
                result=result
            ))
            if not result.compatible:
                all_valid = False

        return PipelineVerification(
            valid=all_valid,
            stages=stages
        )

    # ─────────────────────────────────────────────────────────────
    # Composition Planning
    # ─────────────────────────────────────────────────────────────

    async def find_path(
        self,
        source_type: str,
        target_type: str,
        max_length: int = 5
    ) -> list[list[str]] | None:
        """
        Find all artifact paths that transform source_type to target_type.

        Uses BFS over the agent graph, respecting type compatibility.
        """
        if self.is_subtype(source_type, target_type):
            return [[]]  # Direct compatibility, no agents needed

        paths = []
        queue = [(source_type, [])]  # (current_type, artifact_path)
        visited = {source_type}

        while queue:
            current_type, path = queue.pop(0)

            if len(path) >= max_length:
                continue

            # Find all agents that accept current_type
            candidates = await self._agents_accepting(current_type)

            for agent in candidates:
                new_path = path + [agent.id]
                output = agent.output_type

                # Check if we've reached target
                if self.is_subtype(output, target_type):
                    paths.append(new_path)
                    continue

                # Continue search if not visited
                if output not in visited:
                    visited.add(output)
                    queue.append((output, new_path))

        # Sort by path length
        return sorted(paths, key=len) if paths else None

    async def suggest_composition(
        self,
        available: list[str],
        goal_input: str,
        goal_output: str
    ) -> list[CompositionSuggestion]:
        """
        Suggest how to compose available agents to achieve a goal.

        Given: A set of artifacts
        Goal: Transform goal_input to goal_output
        Output: Ranked composition suggestions
        """
        suggestions = []

        # Try all permutations up to length 4
        for length in range(1, min(5, len(available) + 1)):
            for perm in itertools.permutations(available, length):
                # Check if first accepts goal_input
                first = await self.registry.get(perm[0])
                if not self.is_subtype(goal_input, first.input_type):
                    continue

                # Check if last produces goal_output
                last = await self.registry.get(perm[-1])
                if not self.is_subtype(last.output_type, goal_output):
                    continue

                # Verify internal composition
                verification = await self.verify_pipeline(list(perm))
                if verification.valid:
                    suggestions.append(CompositionSuggestion(
                        artifacts=list(perm),
                        input_type=first.input_type,
                        output_type=last.output_type,
                        length=length
                    ))

        # Sort by length (prefer shorter pipelines)
        return sorted(suggestions, key=lambda s: s.length)

@dataclass
class CompositionResult:
    """Result of checking if two agents can compose."""
    compatible: bool
    reason: str
    output_type: str | None = None
    input_type: str | None = None
    requires_adapter: str | None = None
    suggested_fix: str | None = None

@dataclass
class CompositionStage:
    """One stage in a pipeline verification."""
    from_id: str
    to_id: str
    result: CompositionResult

@dataclass
class PipelineVerification:
    """Result of verifying a complete pipeline."""
    valid: bool
    stages: list[CompositionStage]

@dataclass
class CompositionSuggestion:
    """A suggested composition achieving a goal."""
    artifacts: list[str]
    input_type: str
    output_type: str
    length: int
```

## Contract Types

Contracts are **named types with invariants**—stronger than structural types:

```python
@dataclass
class Contract:
    """A named interface with behavioral guarantees."""
    id: str
    name: str
    description: str

    # Type structure
    input_type: str
    output_type: str

    # Behavioral invariants
    invariants: list[Invariant]

    # Composition rules
    pre_conditions: list[str]   # What must be true before invocation
    post_conditions: list[str]  # What is guaranteed after invocation

    # Versioning
    version: str
    compatible_versions: list[str]  # Versions this is compatible with

@dataclass
class Invariant:
    """A behavioral guarantee."""
    name: str
    description: str
    verification: str  # How to verify (test, proof, runtime check)

# Example contracts:
DETERMINISTIC = Contract(
    id="contract_deterministic",
    name="Deterministic",
    description="Same input always produces same output",
    input_type="Any",
    output_type="Any",
    invariants=[
        Invariant(
            name="determinism",
            description="f(x) == f(x) for all x",
            verification="property_test"
        )
    ],
    pre_conditions=[],
    post_conditions=["output is deterministic function of input"]
)

IDEMPOTENT = Contract(
    id="contract_idempotent",
    name="Idempotent",
    description="Multiple applications produce same result as one",
    input_type="Any",
    output_type="Any",
    invariants=[
        Invariant(
            name="idempotency",
            description="f(f(x)) == f(x) for all x",
            verification="property_test"
        )
    ],
    pre_conditions=[],
    post_conditions=["f(result) == result"]
)

STREAMING = Contract(
    id="contract_streaming",
    name="Streaming",
    description="Processes data in chunks, maintains order",
    input_type="Stream[T]",
    output_type="Stream[U]",
    invariants=[
        Invariant(
            name="order_preservation",
            description="Output order matches input order",
            verification="test"
        ),
        Invariant(
            name="chunk_independence",
            description="Each chunk processed independently",
            verification="test"
        )
    ],
    pre_conditions=["input is valid stream"],
    post_conditions=["output preserves input ordering"]
)
```

## C-gent Integration: Categorical Verification

The lattice validates category-theoretic laws:

```python
class CategoryVerifier:
    """Verify categorical properties of compositions."""

    async def verify_functor(
        self,
        artifact_id: str
    ) -> FunctorVerification:
        """
        Check if an artifact satisfies functor laws.

        Functor laws:
        1. Identity: F(id) = id
        2. Composition: F(g ∘ f) = F(g) ∘ F(f)
        """
        entry = await self.registry.get(artifact_id)

        # Check if it's a container/wrapper type
        if entry.entity_type != EntityType.AGENT:
            return FunctorVerification(is_functor=False, reason="Not an agent")

        # For list_agent, async_agent, etc.
        # Verify identity law
        identity_holds = await self._test_identity_law(entry)

        # Verify composition law
        composition_holds = await self._test_composition_law(entry)

        return FunctorVerification(
            is_functor=identity_holds and composition_holds,
            identity_holds=identity_holds,
            composition_holds=composition_holds
        )

    async def verify_monad(
        self,
        artifact_id: str
    ) -> MonadVerification:
        """
        Check if an artifact satisfies monad laws.

        Monad laws:
        1. Left identity: return a >>= f ≡ f a
        2. Right identity: m >>= return ≡ m
        3. Associativity: (m >>= f) >>= g ≡ m >>= (λx. f x >>= g)
        """
        entry = await self.registry.get(artifact_id)

        # Check if it has bind (>>=) operation
        if "bind" not in entry.contracts_implemented:
            return MonadVerification(is_monad=False, reason="No bind operation")

        left_identity = await self._test_left_identity(entry)
        right_identity = await self._test_right_identity(entry)
        associativity = await self._test_associativity(entry)

        return MonadVerification(
            is_monad=left_identity and right_identity and associativity,
            left_identity=left_identity,
            right_identity=right_identity,
            associativity=associativity
        )

@dataclass
class FunctorVerification:
    is_functor: bool
    identity_holds: bool = False
    composition_holds: bool = False
    reason: str | None = None

@dataclass
class MonadVerification:
    is_monad: bool
    left_identity: bool = False
    right_identity: bool = False
    associativity: bool = False
    reason: str | None = None
```

## H-gent Integration: Type Tensions

The lattice can detect type-level tensions:

```python
class TypeTensionDetector:
    """Detect tensions in the type lattice."""

    async def find_contract_conflicts(
        self,
        artifact_id: str
    ) -> list[ContractConflict]:
        """
        Find conflicting contracts on an artifact.

        Example: An agent claiming both "deterministic" and "random"
        """
        entry = await self.registry.get(artifact_id)
        contracts = entry.contracts_implemented

        conflicts = []
        for i, c1 in enumerate(contracts):
            for c2 in contracts[i+1:]:
                if self._contracts_conflict(c1, c2):
                    conflicts.append(ContractConflict(
                        contract_a=c1,
                        contract_b=c2,
                        reason=self._explain_conflict(c1, c2)
                    ))

        return conflicts

    async def find_subtyping_ambiguity(
        self,
        type_id: str
    ) -> list[SubtypingAmbiguity]:
        """
        Find ambiguous subtyping relationships.

        Example: Two unrelated supertypes with incompatible invariants
        """
        supertypes = self.lattice._all_supertypes(type_id)

        ambiguities = []
        for t1, t2 in itertools.combinations(supertypes, 2):
            if not self.lattice.is_subtype(t1, t2) and not self.lattice.is_subtype(t2, t1):
                # Check if invariants conflict
                n1 = self.lattice.types[t1]
                n2 = self.lattice.types[t2]

                if self._invariants_conflict(n1.invariants, n2.invariants):
                    ambiguities.append(SubtypingAmbiguity(
                        type_a=t1,
                        type_b=t2,
                        conflicting_invariants=self._find_conflicting_invariants(n1, n2)
                    ))

        return ambiguities

@dataclass
class ContractConflict:
    contract_a: str
    contract_b: str
    reason: str

@dataclass
class SubtypingAmbiguity:
    type_a: str
    type_b: str
    conflicting_invariants: list[tuple[str, str]]
```

## Example: Pipeline Planning

```python
# User goal: Transform RawHTML to SentimentScore

# 1. Query available types
await lattice.register_type(TypeNode(
    id="RawHTML",
    kind=TypeKind.PRIMITIVE,
    name="Raw HTML content"
))

await lattice.register_type(TypeNode(
    id="CleanText",
    kind=TypeKind.PRIMITIVE,
    name="Cleaned text without HTML"
))

await lattice.register_type(TypeNode(
    id="SentimentScore",
    kind=TypeKind.RECORD,
    name="Sentiment analysis result",
    fields={"score": "float", "confidence": "float"}
))

# 2. Register agents with their type signatures
await registry.register(CatalogEntry(
    id="html_cleaner_v1",
    name="HTMLCleaner",
    input_type="RawHTML",
    output_type="CleanText",
    ...
))

await registry.register(CatalogEntry(
    id="sentiment_analyzer_v2",
    name="SentimentAnalyzer",
    input_type="CleanText",  # or "str" if CleanText ≤ str
    output_type="SentimentScore",
    ...
))

# 3. Find composition path
paths = await lattice.find_path(
    source_type="RawHTML",
    target_type="SentimentScore"
)

# Returns: [["html_cleaner_v1", "sentiment_analyzer_v2"]]

# 4. Verify the pipeline
verification = await lattice.verify_pipeline(paths[0])

# Returns:
# PipelineVerification(
#     valid=True,
#     stages=[
#         CompositionStage(
#             from_id="html_cleaner_v1",
#             to_id="sentiment_analyzer_v2",
#             result=CompositionResult(
#                 compatible=True,
#                 reason="CleanText ≤ CleanText"
#             )
#         )
#     ]
# )

# 5. Build the pipeline
pipeline = HTMLCleaner_v1 >> SentimentAnalyzer_v2
```

## Performance Considerations

### Caching Subtype Relationships

```python
class SubtypeCache:
    """Cache expensive subtype computations."""

    def __init__(self, lattice: TypeLattice):
        self.lattice = lattice
        self.cache: dict[tuple[str, str], bool] = {}

    def is_subtype(self, sub: str, super_: str) -> bool:
        key = (sub, super_)
        if key not in self.cache:
            self.cache[key] = self.lattice.is_subtype(sub, super_)
        return self.cache[key]

    def invalidate(self, type_id: str) -> None:
        """Invalidate cache entries involving a modified type."""
        self.cache = {
            k: v for k, v in self.cache.items()
            if type_id not in k
        }
```

### Incremental Lattice Updates

When a new type is added, only affected paths need recomputation:

```python
async def add_type_incremental(self, node: TypeNode) -> None:
    """Add type without full recomputation."""
    self.types[node.id] = node

    # Only compute direct relationships
    for existing_id, existing_node in self.types.items():
        if self._structurally_subtype(node, existing_node):
            self.edges.append(SubtypeEdge(
                subtype_id=node.id,
                supertype_id=existing_id,
                reason="structural"
            ))
        if self._structurally_subtype(existing_node, node):
            self.edges.append(SubtypeEdge(
                subtype_id=existing_id,
                supertype_id=node.id,
                reason="structural"
            ))

    # Invalidate affected cache entries
    self.cache.invalidate(node.id)
```

## See Also

- [catalog.md](catalog.md) - Types are registered here
- [query.md](query.md) - Type-based search
- [../c-gents/](../c-gents/) - Category theory foundations
- [../f-gents/contracts.md](../f-gents/contracts.md) - Contract synthesis
- [../h-gents/](../h-gents/) - Tension detection for types
