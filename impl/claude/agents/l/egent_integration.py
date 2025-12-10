"""
L-gent E-gent Integration: Semantic capabilities for teleological thermodynamic evolution.

This module extends SemanticRegistry with capabilities required by E-gent:
1. Mutation schemas: Isomorphic transformation patterns
2. Code intent embedding: For teleological alignment checking
3. Type compatibility: Structural subtyping for semantic stability
4. Archetype management: For viral library pattern storage

Spec Reference: spec/e-gents/thermodynamics.md
"""

from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

from .semantic_registry import SemanticRegistry
from .semantic import Embedder


# =============================================================================
# Mutation Schemas (for Mutator)
# =============================================================================


class SchemaCategory(Enum):
    """Categories of mutation schemas from E-gent spec."""

    SUBSTITUTE = "substitute"  # Replace one pattern with another
    EXTRACT = "extract"  # Extract code into separate function/class
    INLINE = "inline"  # Inline function/variable
    ANNOTATE = "annotate"  # Add type annotations, docstrings
    RESTRUCTURE = "restructure"  # Reorganize code structure


@dataclass(frozen=True)
class MutationSchema:
    """
    A semantic transformation pattern from L-gent.

    Unlike random mutation, schemas are ISOMORPHIC:
    they change structure without breaking types.

    From spec/e-gents/thermodynamics.md:
    > The Mutator applies semantic transformations from the L-gent Type Lattice—
    > changes that preserve semantic structure while modifying syntax.
    """

    name: str  # e.g., "loop_to_comprehension"
    category: SchemaCategory
    precondition: str  # AST pattern that must match
    transformation: str  # How to transform
    description: str  # Human-readable description
    enthalpy_delta: float  # Expected complexity change (- = simpler)
    entropy_delta: float  # Expected capability change (+ = more)
    confidence: float = 0.7  # Schema reliability (0.0-1.0)

    @property
    def signature(self) -> str:
        """Unique signature for viral library matching."""
        return hashlib.sha256(
            f"{self.name}:{self.category.value}:{self.precondition}".encode()
        ).hexdigest()[:16]

    def gibbs_free_energy(self, temperature: float) -> float:
        """ΔG = ΔH - TΔS (thermodynamic viability check)."""
        return self.enthalpy_delta - (temperature * self.entropy_delta)


# Standard mutation schemas (the "schema library")
STANDARD_SCHEMAS: list[MutationSchema] = [
    # Substitution patterns
    MutationSchema(
        name="loop_to_comprehension",
        category=SchemaCategory.SUBSTITUTE,
        precondition="for x in y: result.append(f(x))",
        transformation="[f(x) for x in y]",
        description="Convert append-loop to list comprehension",
        enthalpy_delta=-0.3,  # Simpler
        entropy_delta=0.0,  # Same capability
    ),
    MutationSchema(
        name="dict_comprehension",
        category=SchemaCategory.SUBSTITUTE,
        precondition="for k, v in items: result[k] = f(v)",
        transformation="{k: f(v) for k, v in items}",
        description="Convert loop to dict comprehension",
        enthalpy_delta=-0.3,
        entropy_delta=0.0,
    ),
    MutationSchema(
        name="match_to_dict_dispatch",
        category=SchemaCategory.SUBSTITUTE,
        precondition="match x: case ...: ...",
        transformation="dispatch_table = {...}; dispatch_table.get(x, default)()",
        description="Convert match statement to dictionary dispatch",
        enthalpy_delta=-0.2,
        entropy_delta=0.1,  # More extensible
    ),
    MutationSchema(
        name="if_chain_to_dict",
        category=SchemaCategory.SUBSTITUTE,
        precondition="if x == 'a': ... elif x == 'b': ...",
        transformation="handlers = {'a': ..., 'b': ...}; handlers.get(x, default)",
        description="Convert if-elif chain to dict lookup",
        enthalpy_delta=-0.4,
        entropy_delta=0.1,
    ),
    # Extraction patterns
    MutationSchema(
        name="extract_method",
        category=SchemaCategory.EXTRACT,
        precondition="function with complexity > 10",
        transformation="split at natural seams into helper methods",
        description="Extract complex code into separate method",
        enthalpy_delta=-0.5,  # Much simpler per function
        entropy_delta=0.2,  # More reusable
    ),
    MutationSchema(
        name="extract_constant",
        category=SchemaCategory.EXTRACT,
        precondition="magic number or string literal",
        transformation="NAME = value; use NAME",
        description="Extract magic value to named constant",
        enthalpy_delta=-0.2,
        entropy_delta=0.1,
    ),
    MutationSchema(
        name="extract_dataclass",
        category=SchemaCategory.EXTRACT,
        precondition="dict with consistent keys or tuple with positional meaning",
        transformation="@dataclass class Name: ...",
        description="Extract data structure to dataclass",
        enthalpy_delta=0.0,  # Similar complexity
        entropy_delta=0.3,  # Much more self-documenting
    ),
    # Inlining patterns
    MutationSchema(
        name="inline_single_use_variable",
        category=SchemaCategory.INLINE,
        precondition="x = expr; use(x) # x used exactly once",
        transformation="use(expr)",
        description="Inline variable used only once",
        enthalpy_delta=-0.1,
        entropy_delta=0.0,
    ),
    MutationSchema(
        name="inline_trivial_method",
        category=SchemaCategory.INLINE,
        precondition="def f(): return expr # single expression",
        transformation="replace calls with expr",
        description="Inline trivial single-expression method",
        enthalpy_delta=-0.2,
        entropy_delta=-0.1,  # Less modular
    ),
    # Annotation patterns
    MutationSchema(
        name="add_type_hints",
        category=SchemaCategory.ANNOTATE,
        precondition="function without type hints",
        transformation="def f(x: T) -> R: ...",
        description="Add type annotations to function",
        enthalpy_delta=0.1,  # Slightly more complex
        entropy_delta=0.4,  # Much more useful
    ),
    MutationSchema(
        name="add_docstring",
        category=SchemaCategory.ANNOTATE,
        precondition="function/class without docstring",
        transformation='"""Description."""',
        description="Add docstring documentation",
        enthalpy_delta=0.05,
        entropy_delta=0.3,
    ),
    # Restructuring patterns
    MutationSchema(
        name="flatten_nesting",
        category=SchemaCategory.RESTRUCTURE,
        precondition="if/for nesting depth > 3",
        transformation="use early returns or extract to functions",
        description="Flatten deeply nested code",
        enthalpy_delta=-0.6,
        entropy_delta=0.1,
    ),
    MutationSchema(
        name="compose_pipeline",
        category=SchemaCategory.RESTRUCTURE,
        precondition="sequential transformations: b = f(a); c = g(b); d = h(c)",
        transformation="d = h(g(f(a))) or a >> f >> g >> h",
        description="Compose sequential transformations",
        enthalpy_delta=-0.2,
        entropy_delta=0.2,  # More composable
    ),
]


# =============================================================================
# Code Intent Embedding (for Teleological Demon)
# =============================================================================


@dataclass
class CodeIntent:
    """
    The Teleological Field that guides evolution.

    Without Intent, evolution drifts toward Empty (lowest energy).
    With Intent, evolution is constrained to PURPOSE.

    From spec/e-gents/thermodynamics.md:
    > Intent is an embedding vector that represents *what the User wants
    > this code to do*.
    """

    embedding: list[float]
    source: Literal["user", "tests", "structure"]
    description: str
    confidence: float  # How sure are we about this intent?

    @classmethod
    async def from_user(
        cls,
        description: str,
        embedder: Embedder,
    ) -> "CodeIntent":
        """User explicitly states what they want."""
        embedding = await embedder.embed(description)
        return cls(
            embedding=embedding,
            source="user",
            description=description,
            confidence=1.0,  # User knows what they want
        )

    @classmethod
    async def from_tests(
        cls,
        test_docstrings: list[str],
        embedder: Embedder,
    ) -> "CodeIntent":
        """Infer intent from test semantics."""
        combined = " ".join(test_docstrings)
        embedding = await embedder.embed(combined)
        return cls(
            embedding=embedding,
            source="tests",
            description=f"Inferred from {len(test_docstrings)} tests",
            confidence=0.7,  # Tests may be incomplete
        )

    @classmethod
    async def from_structure(
        cls,
        docstrings: list[str],
        names: list[str],
        embedder: Embedder,
    ) -> "CodeIntent":
        """Infer intent from code structure."""
        combined = " ".join(docstrings + names)
        embedding = await embedder.embed(combined)
        return cls(
            embedding=embedding,
            source="structure",
            description=f"Inferred from {len(names)} names",
            confidence=0.5,  # Structure may be misleading
        )


def extract_code_docstrings(code: str) -> list[str]:
    """Extract docstrings from Python code."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    docstrings = []

    for node in ast.walk(tree):
        if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings.append(docstring)

    return docstrings


def extract_code_names(code: str) -> list[str]:
    """Extract function and class names from Python code."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    names = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(node.name)

    return names


# =============================================================================
# Type Inference (for Semantic Stability Check)
# =============================================================================


@dataclass
class InferredType:
    """Type information inferred from code structure."""

    name: str
    kind: Literal["function", "class", "variable", "module"]
    input_types: list[str] = field(default_factory=list)
    output_type: str | None = None
    attributes: list[str] = field(default_factory=list)


def infer_types(code: str) -> list[InferredType]:
    """
    Infer type structure from Python code (static analysis).

    This is a cheap heuristic for the Demon's Layer 2 (Semantic Stability).
    For full type checking, use mypy.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    types: list[InferredType] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Extract function type info
            input_types = []
            for arg in node.args.args:
                if arg.annotation:
                    input_types.append(ast.unparse(arg.annotation))
                else:
                    input_types.append("Any")

            output_type = None
            if node.returns:
                output_type = ast.unparse(node.returns)

            types.append(
                InferredType(
                    name=node.name,
                    kind="function",
                    input_types=input_types,
                    output_type=output_type,
                )
            )

        elif isinstance(node, ast.ClassDef):
            # Extract class type info
            attributes = []
            for body_node in node.body:
                if isinstance(body_node, ast.AnnAssign) and isinstance(
                    body_node.target, ast.Name
                ):
                    attributes.append(body_node.target.id)
                elif isinstance(body_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    attributes.append(body_node.name)

            types.append(
                InferredType(
                    name=node.name,
                    kind="class",
                    attributes=attributes,
                )
            )

    return types


def types_compatible(
    original_types: list[InferredType], mutated_types: list[InferredType]
) -> bool:
    """
    Check if mutated code preserves type structure.

    This is a cheap heuristic for semantic stability:
    - All original public names should still exist
    - Function signatures should be compatible (covariant returns, contravariant args)

    For the Demon's Layer 2 (Semantic Stability).
    """
    original_names = {t.name for t in original_types}
    mutated_names = {t.name for t in mutated_types}

    # All original public names should exist in mutated code
    # (Private names starting with _ can be removed)
    public_original = {n for n in original_names if not n.startswith("_")}
    public_mutated = {n for n in mutated_names if not n.startswith("_")}

    if not public_original.issubset(public_mutated):
        return False

    # Check function signature compatibility
    original_funcs = {t.name: t for t in original_types if t.kind == "function"}
    mutated_funcs = {t.name: t for t in mutated_types if t.kind == "function"}

    for name, original_func in original_funcs.items():
        if name in mutated_funcs:
            mutated_func = mutated_funcs[name]

            # Output type should be same or more specific (covariant)
            if original_func.output_type and mutated_func.output_type:
                # Simple check: exact match or both Any
                if original_func.output_type != mutated_func.output_type:
                    if original_func.output_type != "Any":
                        return False

    return True


# =============================================================================
# Archetype Management (for Viral Library)
# =============================================================================


@dataclass
class Archetype:
    """
    A semantic pattern archetype stored in the registry.

    Used by the Viral Library to store successful mutation DNA.
    """

    name: str
    embedding: list[float]
    signature: str  # Pattern signature for matching
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Extended SemanticRegistry
# =============================================================================


class EgentSemanticRegistry(SemanticRegistry):
    """
    SemanticRegistry extended with E-gent integration capabilities.

    Adds:
    - Mutation schema retrieval
    - Code intent embedding
    - Type compatibility checking
    - Archetype management for viral library
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._archetypes: dict[str, Archetype] = {}
        self._schema_library = list(STANDARD_SCHEMAS)

    # -------------------------------------------------------------------
    # Mutation Schema Operations
    # -------------------------------------------------------------------

    def get_mutation_schemas(
        self,
        category: SchemaCategory | None = None,
        temperature: float = 1.0,
    ) -> list[MutationSchema]:
        """
        Get mutation schemas, optionally filtered by category.

        Args:
            category: Optional schema category filter
            temperature: Current system temperature (for Gibbs filtering)

        Returns:
            List of applicable mutation schemas
        """
        schemas = self._schema_library

        if category:
            schemas = [s for s in schemas if s.category == category]

        # Filter by Gibbs viability at current temperature
        schemas = [s for s in schemas if s.gibbs_free_energy(temperature) < 0]

        return schemas

    def register_schema(self, schema: MutationSchema) -> None:
        """Register a new mutation schema."""
        self._schema_library.append(schema)

    # -------------------------------------------------------------------
    # Code Intent Operations (for Teleological Demon)
    # -------------------------------------------------------------------

    async def embed_text(self, text: str) -> list[float]:
        """
        Embed text into a dense vector.

        For Intent.from_user() and similar.
        """
        return await self.embedder.embed(text)

    async def embed_code_intent(self, code: str) -> list[float]:
        """
        Embed code's apparent purpose/intent.

        This is used by the Teleological Demon to check if a mutation
        drifts from the User's Intent.

        Extracts docstrings and names, then embeds the combined text.
        """
        docstrings = extract_code_docstrings(code)
        names = extract_code_names(code)

        # Combine into searchable text
        parts = docstrings + [
            # Convert function/class names to natural language
            name.replace("_", " ")
            for name in names
        ]

        text = " ".join(parts)
        if not text.strip():
            # Fallback: embed the code itself
            text = code[:2000]  # Limit to avoid token issues

        return await self.embedder.embed(text)

    async def create_code_intent(
        self,
        code: str,
        user_description: str | None = None,
    ) -> CodeIntent:
        """
        Create a CodeIntent from code and optional user description.

        Priority: user description > docstrings > structure
        """
        if user_description:
            return await CodeIntent.from_user(user_description, self.embedder)

        docstrings = extract_code_docstrings(code)
        names = extract_code_names(code)

        if docstrings:
            return await CodeIntent.from_tests(docstrings, self.embedder)
        else:
            return await CodeIntent.from_structure(docstrings, names, self.embedder)

    # -------------------------------------------------------------------
    # Type Compatibility Operations (for Semantic Stability)
    # -------------------------------------------------------------------

    def infer_types(self, code: str) -> list[InferredType]:
        """Infer type structure from code."""
        return infer_types(code)

    def types_compatible(
        self,
        original_code: str,
        mutated_code: str,
    ) -> bool:
        """
        Check if mutated code preserves type structure.

        For the Demon's Layer 2 (Semantic Stability).
        """
        original_types = infer_types(original_code)
        mutated_types = infer_types(mutated_code)
        return types_compatible(original_types, mutated_types)

    # -------------------------------------------------------------------
    # Archetype Operations (for Viral Library)
    # -------------------------------------------------------------------

    async def register_archetype(
        self,
        name: str,
        embedding: list[float] | None = None,
        text: str | None = None,
        signature: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Register an archetype pattern.

        Used by Viral Library to store successful mutation DNA.

        Args:
            name: Archetype name (e.g., "viral:pattern_sig")
            embedding: Pre-computed embedding, or
            text: Text to embed
            signature: Pattern signature for matching
            metadata: Optional metadata

        Returns:
            Archetype ID
        """
        if embedding is None:
            if text is None:
                raise ValueError("Either embedding or text must be provided")
            embedding = await self.embedder.embed(text)

        archetype = Archetype(
            name=name,
            embedding=embedding,
            signature=signature,
            metadata=metadata or {},
        )
        self._archetypes[name] = archetype
        return name

    def deregister_archetype(self, name: str) -> bool:
        """
        Remove an archetype pattern.

        Used when pruning low-fitness patterns from Viral Library.
        """
        if name in self._archetypes:
            del self._archetypes[name]
            return True
        return False

    async def find_similar_archetypes(
        self,
        embedding: list[float],
        prefix: str = "",
        threshold: float = 0.5,
        top_k: int = 10,
    ) -> list[tuple[str, float]]:
        """
        Find archetypes similar to a given embedding.

        Used by Viral Library to suggest mutations.

        Args:
            embedding: Query embedding
            prefix: Optional name prefix filter (e.g., "viral:")
            threshold: Minimum similarity
            top_k: Maximum results

        Returns:
            List of (archetype_name, similarity) tuples
        """

        results: list[tuple[str, float]] = []

        for name, archetype in self._archetypes.items():
            if prefix and not name.startswith(prefix):
                continue

            # Cosine similarity
            similarity = self._cosine_similarity(embedding, archetype.embedding)

            if similarity >= threshold:
                results.append((name, similarity))

        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity."""
        import math

        if len(vec1) != len(vec2):
            return 0.0

        dot = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot / (mag1 * mag2)

    def get_archetype(self, name: str) -> Archetype | None:
        """Get an archetype by name."""
        return self._archetypes.get(name)


# =============================================================================
# Convenience Functions
# =============================================================================


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    import math

    if len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b)


async def create_egent_registry(
    embedder: Embedder | None = None,
) -> EgentSemanticRegistry:
    """Create an E-gent-enabled semantic registry."""
    registry = EgentSemanticRegistry(embedder=embedder)
    return registry
