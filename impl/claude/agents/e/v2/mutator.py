"""
E-gent v2 Mutator: Schema-based semantic mutation generator.

The Mutator generates MutationVectors by applying L-gent semantic schemas
to code, rather than random noise or LLM-based hypothesis generation.

Key principles:
1. SEMANTIC: Mutations are schema-driven, not random
2. ISOMORPHIC: Preserve type structure while modifying syntax
3. THERMODYNAMIC: Pre-filter by Gibbs viability (ΔG < 0)
4. TARGETED: Focus on hot spots (high complexity, high entropy)

From spec/e-gents/README.md:
> The Mutator applies semantic transformations from the L-gent Type Lattice—
> changes that preserve semantic structure while modifying syntax.

Spec Reference: spec/e-gents/thermodynamics.md
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .types import (
    MutationVector,
    Phage,
    PhageStatus,
    PhageLineage,
)


# =============================================================================
# Schema Types (from L-gent integration)
# =============================================================================


class SchemaCategory(Enum):
    """Categories of mutation schemas."""

    SUBSTITUTE = "substitute"  # Replace one pattern with another
    EXTRACT = "extract"  # Extract code into separate function/class
    INLINE = "inline"  # Inline function/variable
    ANNOTATE = "annotate"  # Add type annotations, docstrings
    RESTRUCTURE = "restructure"  # Reorganize code structure


@dataclass(frozen=True)
class MutationSchema:
    """
    A semantic transformation pattern.

    Unlike random mutation, schemas are ISOMORPHIC:
    they change structure without breaking types.
    """

    name: str
    category: SchemaCategory
    description: str
    enthalpy_delta: float  # ΔH: Expected complexity change (- = simpler)
    entropy_delta: float  # ΔS: Expected capability change (+ = more)
    confidence: float = 0.7  # Schema reliability (0.0-1.0)

    # Pattern matching
    pattern_type: str = ""  # AST node type to match
    pattern_check: str = ""  # Additional check code

    def gibbs_free_energy(self, temperature: float) -> float:
        """ΔG = ΔH - TΔS (thermodynamic viability check)."""
        return self.enthalpy_delta - (temperature * self.entropy_delta)

    def is_viable(self, temperature: float) -> bool:
        """Check if schema is thermodynamically viable at given temperature."""
        return self.gibbs_free_energy(temperature) < 0


# =============================================================================
# Hot Spot Detection
# =============================================================================


@dataclass
class CodeHotSpot:
    """
    A location in code with high complexity or entropy.

    Mutations are more likely to succeed at hot spots because:
    1. High complexity = more opportunity for simplification
    2. High entropy = more opportunity for restructuring
    """

    lineno_start: int
    lineno_end: int
    node_type: str  # AST node type (FunctionDef, ClassDef, etc.)
    name: str  # Name of the node
    complexity: float  # Cyclomatic-like complexity
    entropy: float  # Structural entropy estimate

    @property
    def priority(self) -> float:
        """Priority for mutation targeting (higher = more likely to mutate)."""
        return self.complexity * 0.6 + self.entropy * 0.4


def analyze_hot_spots(code: str) -> list[CodeHotSpot]:
    """
    Analyze code to find hot spots suitable for mutation.

    Hot spots are identified by:
    - High cyclomatic complexity (many branches)
    - High nesting depth
    - Large functions
    - Complex expressions
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    hot_spots: list[CodeHotSpot] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            complexity = _calculate_complexity(node)
            entropy = _calculate_entropy(node)

            hot_spots.append(
                CodeHotSpot(
                    lineno_start=node.lineno,
                    lineno_end=node.end_lineno or node.lineno,
                    node_type="function",
                    name=node.name,
                    complexity=complexity,
                    entropy=entropy,
                )
            )

        elif isinstance(node, ast.ClassDef):
            complexity = sum(
                _calculate_complexity(n)
                for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            )
            entropy = len(node.body)  # Number of methods/attributes

            hot_spots.append(
                CodeHotSpot(
                    lineno_start=node.lineno,
                    lineno_end=node.end_lineno or node.lineno,
                    node_type="class",
                    name=node.name,
                    complexity=complexity,
                    entropy=entropy,
                )
            )

    # Sort by priority (highest first)
    hot_spots.sort(key=lambda h: h.priority, reverse=True)
    return hot_spots


def _calculate_complexity(node: ast.AST) -> float:
    """Calculate cyclomatic-like complexity for a node."""
    complexity = 1.0  # Base complexity

    for child in ast.walk(node):
        # Each branch point adds complexity
        if isinstance(child, (ast.If, ast.IfExp)):
            complexity += 1
        elif isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
            complexity += 1
        elif isinstance(child, ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, (ast.And, ast.Or)):
            complexity += 0.5
        elif isinstance(child, ast.comprehension):
            complexity += 0.5

    return complexity


def _calculate_entropy(node: ast.AST) -> float:
    """Estimate structural entropy of a node."""
    # Entropy approximated by nesting depth and breadth
    max_depth = 0
    total_nodes = 0

    def measure_depth(n: ast.AST, depth: int) -> None:
        nonlocal max_depth, total_nodes
        max_depth = max(max_depth, depth)
        total_nodes += 1
        for child in ast.iter_child_nodes(n):
            measure_depth(child, depth + 1)

    measure_depth(node, 0)

    # Normalize
    return (max_depth * 0.5) + (total_nodes * 0.01)


# =============================================================================
# Schema Application
# =============================================================================


@dataclass
class ApplicationResult:
    """Result of applying a schema to code."""

    success: bool
    original_code: str
    mutated_code: str
    schema: MutationSchema
    location: CodeHotSpot | None = None
    error: str | None = None


class SchemaApplicator(Protocol):
    """Protocol for schema application functions."""

    def __call__(
        self, code: str, location: CodeHotSpot | None
    ) -> ApplicationResult | None:
        """Apply schema to code at optional location."""
        ...


# =============================================================================
# Standard Schema Applicators
# =============================================================================


def apply_loop_to_comprehension(
    code: str, location: CodeHotSpot | None
) -> ApplicationResult | None:
    """
    Apply loop_to_comprehension schema.

    Pattern: for x in y: result.append(f(x))
    Result:  [f(x) for x in y]
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    class LoopComprehensionTransformer(ast.NodeTransformer):
        def __init__(self) -> None:
            self.transformed = False

        def visit_For(self, node: ast.For) -> ast.AST:
            # Check if this is an append loop
            if (
                len(node.body) == 1
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Call)
            ):
                call = node.body[0].value
                if (
                    isinstance(call.func, ast.Attribute)
                    and call.func.attr == "append"
                    and len(call.args) == 1
                ):
                    # Transform to list comprehension
                    self.transformed = True

                    # Get the result variable
                    if isinstance(call.func.value, ast.Name):
                        result_var = call.func.value.id

                        # Create list comprehension
                        comp = ast.ListComp(
                            elt=call.args[0],
                            generators=[
                                ast.comprehension(
                                    target=node.target,
                                    iter=node.iter,
                                    ifs=[],
                                    is_async=0,
                                )
                            ],
                        )

                        # Create assignment
                        assign = ast.Assign(
                            targets=[ast.Name(id=result_var, ctx=ast.Store())],
                            value=comp,
                        )
                        return assign

            return self.generic_visit(node)

    transformer = LoopComprehensionTransformer()
    new_tree = transformer.visit(tree)

    if transformer.transformed:
        ast.fix_missing_locations(new_tree)
        return ApplicationResult(
            success=True,
            original_code=code,
            mutated_code=ast.unparse(new_tree),
            schema=SCHEMA_LOOP_TO_COMPREHENSION,
            location=location,
        )

    return None


def apply_extract_constant(
    code: str, location: CodeHotSpot | None
) -> ApplicationResult | None:
    """
    Apply extract_constant schema.

    Pattern: magic number in code
    Result:  CONSTANT_NAME = value; use CONSTANT_NAME
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    # Find magic numbers (numeric literals > 2)
    magic_numbers: list[tuple[ast.Constant, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            if abs(node.value) > 2 and node.value not in (0, 1, -1, 0.0, 1.0, -1.0):
                # Generate constant name
                name = f"CONSTANT_{len(magic_numbers)}"
                magic_numbers.append((node, name))

    if not magic_numbers:
        return None

    # Transform: add constant definitions and replace literals
    class MagicNumberReplacer(ast.NodeTransformer):
        def __init__(self, constants: list[tuple[ast.Constant, str]]) -> None:
            self.constants = {id(c[0]): c[1] for c in constants}
            self.found_ids: set[int] = set()

        def visit_Constant(self, node: ast.Constant) -> ast.AST:
            if id(node) in self.constants:
                self.found_ids.add(id(node))
                return ast.Name(id=self.constants[id(node)], ctx=ast.Load())
            return node

    replacer = MagicNumberReplacer(magic_numbers)
    new_tree = replacer.visit(tree)

    # Add constant definitions at the top
    if replacer.found_ids:
        constant_defs = [
            ast.Assign(
                targets=[ast.Name(id=name, ctx=ast.Store())],
                value=ast.Constant(value=const.value),
            )
            for const, name in magic_numbers
            if id(const) in replacer.found_ids
        ]

        if isinstance(new_tree, ast.Module):
            new_tree.body = constant_defs + new_tree.body

        ast.fix_missing_locations(new_tree)
        return ApplicationResult(
            success=True,
            original_code=code,
            mutated_code=ast.unparse(new_tree),
            schema=SCHEMA_EXTRACT_CONSTANT,
            location=location,
        )

    return None


def apply_flatten_nesting(
    code: str, location: CodeHotSpot | None
) -> ApplicationResult | None:
    """
    Apply flatten_nesting schema.

    Pattern: deeply nested if/for statements
    Result:  early returns or guard clauses
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    class NestingFlattener(ast.NodeTransformer):
        def __init__(self) -> None:
            self.transformed = False

        def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
            # Check for nested if at start of function
            if (
                len(node.body) >= 1
                and isinstance(node.body[0], ast.If)
                and not node.body[0].orelse
            ):
                if_node = node.body[0]

                # Can we invert the condition and return early?
                # Pattern: if condition: ... (rest of function)
                # Result:  if not condition: return; ...

                # Create inverted condition
                inverted = ast.UnaryOp(op=ast.Not(), operand=if_node.test)

                # Create early return
                early_return = ast.If(
                    test=inverted,
                    body=[ast.Return(value=None)],
                    orelse=[],
                )

                # New body: early return, then original if body
                node.body = [early_return] + if_node.body + node.body[1:]
                self.transformed = True

            return self.generic_visit(node)

    flattener = NestingFlattener()
    new_tree = flattener.visit(tree)

    if flattener.transformed:
        ast.fix_missing_locations(new_tree)
        return ApplicationResult(
            success=True,
            original_code=code,
            mutated_code=ast.unparse(new_tree),
            schema=SCHEMA_FLATTEN_NESTING,
            location=location,
        )

    return None


def apply_inline_single_use(
    code: str, location: CodeHotSpot | None
) -> ApplicationResult | None:
    """
    Apply inline_single_use schema.

    Pattern: x = expr; f(x)  # x used exactly once
    Result:  f(expr)
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    # Find single-use variables
    class SingleUseAnalyzer(ast.NodeVisitor):
        def __init__(self) -> None:
            self.assignments: dict[str, ast.Assign] = {}
            self.uses: dict[str, int] = {}

        def visit_Assign(self, node: ast.Assign) -> None:
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                if not name.startswith("_"):
                    self.assignments[name] = node
                    self.uses[name] = 0
            self.generic_visit(node)

        def visit_Name(self, node: ast.Name) -> None:
            if isinstance(node.ctx, ast.Load) and node.id in self.uses:
                self.uses[node.id] += 1
            self.generic_visit(node)

    analyzer = SingleUseAnalyzer()
    analyzer.visit(tree)

    # Find variables used exactly once
    single_use = [
        name
        for name, count in analyzer.uses.items()
        if count == 1 and name in analyzer.assignments
    ]

    if not single_use:
        return None

    # Inline first single-use variable
    var_to_inline = single_use[0]
    assign_node = analyzer.assignments[var_to_inline]

    class SingleUseInliner(ast.NodeTransformer):
        def __init__(self, var_name: str, expr: ast.expr) -> None:
            self.var_name = var_name
            self.expr = expr
            self.removed_assign = False
            self.inlined = False

        def visit_Assign(self, node: ast.Assign) -> ast.AST | None:
            if (
                len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == self.var_name
            ):
                self.removed_assign = True
                return None  # Remove the assignment
            return node

        def visit_Name(self, node: ast.Name) -> ast.AST:
            if isinstance(node.ctx, ast.Load) and node.id == self.var_name:
                self.inlined = True
                return self.expr
            return node

    inliner = SingleUseInliner(var_to_inline, assign_node.value)
    new_tree = inliner.visit(tree)

    # Clean up None entries
    if isinstance(new_tree, ast.Module):
        new_tree.body = [n for n in new_tree.body if n is not None]

    if inliner.removed_assign and inliner.inlined:
        ast.fix_missing_locations(new_tree)
        return ApplicationResult(
            success=True,
            original_code=code,
            mutated_code=ast.unparse(new_tree),
            schema=SCHEMA_INLINE_SINGLE_USE,
            location=location,
        )

    return None


# =============================================================================
# Standard Schemas
# =============================================================================

SCHEMA_LOOP_TO_COMPREHENSION = MutationSchema(
    name="loop_to_comprehension",
    category=SchemaCategory.SUBSTITUTE,
    description="Convert append-loop to list comprehension",
    enthalpy_delta=-0.3,  # Simpler
    entropy_delta=0.0,  # Same capability
    pattern_type="For",
)

SCHEMA_EXTRACT_CONSTANT = MutationSchema(
    name="extract_constant",
    category=SchemaCategory.EXTRACT,
    description="Extract magic value to named constant",
    enthalpy_delta=-0.2,
    entropy_delta=0.1,
    pattern_type="Constant",
)

SCHEMA_FLATTEN_NESTING = MutationSchema(
    name="flatten_nesting",
    category=SchemaCategory.RESTRUCTURE,
    description="Flatten deeply nested code with early returns",
    enthalpy_delta=-0.6,
    entropy_delta=0.1,
    pattern_type="FunctionDef",
)

SCHEMA_INLINE_SINGLE_USE = MutationSchema(
    name="inline_single_use",
    category=SchemaCategory.INLINE,
    description="Inline variable used only once",
    enthalpy_delta=-0.1,
    entropy_delta=0.0,
    pattern_type="Assign",
)

SCHEMA_DICT_COMPREHENSION = MutationSchema(
    name="dict_comprehension",
    category=SchemaCategory.SUBSTITUTE,
    description="Convert loop to dict comprehension",
    enthalpy_delta=-0.3,
    entropy_delta=0.0,
    pattern_type="For",
)

SCHEMA_IF_CHAIN_TO_DICT = MutationSchema(
    name="if_chain_to_dict",
    category=SchemaCategory.SUBSTITUTE,
    description="Convert if-elif chain to dict lookup",
    enthalpy_delta=-0.4,
    entropy_delta=0.1,
    pattern_type="If",
)

SCHEMA_EXTRACT_METHOD = MutationSchema(
    name="extract_method",
    category=SchemaCategory.EXTRACT,
    description="Extract complex code into separate method",
    enthalpy_delta=-0.5,
    entropy_delta=0.2,
    pattern_type="FunctionDef",
)


# Standard schema library with applicators
STANDARD_SCHEMA_APPLICATORS: dict[str, tuple[MutationSchema, SchemaApplicator]] = {
    "loop_to_comprehension": (
        SCHEMA_LOOP_TO_COMPREHENSION,
        apply_loop_to_comprehension,
    ),
    "extract_constant": (SCHEMA_EXTRACT_CONSTANT, apply_extract_constant),
    "flatten_nesting": (SCHEMA_FLATTEN_NESTING, apply_flatten_nesting),
    "inline_single_use": (SCHEMA_INLINE_SINGLE_USE, apply_inline_single_use),
}


# =============================================================================
# Mutator
# =============================================================================


@dataclass
class MutatorConfig:
    """Configuration for the Mutator."""

    # Temperature settings
    default_temperature: float = 1.0
    min_temperature: float = 0.1
    max_temperature: float = 10.0

    # Hot spot targeting
    min_complexity: float = 2.0  # Minimum complexity to target
    max_mutations_per_spot: int = 3  # Maximum mutations per hot spot

    # Mutation generation
    max_mutations: int = 10  # Maximum mutations to generate
    require_gibbs_viable: bool = True  # Pre-filter by Gibbs

    # Lineage
    track_lineage: bool = True


class Mutator:
    """
    Schema-based semantic mutation generator.

    The Mutator generates MutationVectors by:
    1. Analyzing code for hot spots
    2. Selecting applicable schemas
    3. Applying schemas to generate mutations
    4. Pre-filtering by Gibbs viability (ΔG < 0)

    From spec/e-gents/README.md:
    > Mutations are isomorphic, not random. The Mutator applies L-gent schemas,
    > not random noise. Schemas preserve type structure while modifying implementation.
    """

    def __init__(
        self,
        config: MutatorConfig | None = None,
        schemas: dict[str, tuple[MutationSchema, SchemaApplicator]] | None = None,
    ) -> None:
        """
        Initialize the Mutator.

        Args:
            config: Mutator configuration
            schemas: Schema library (defaults to STANDARD_SCHEMA_APPLICATORS)
        """
        self.config = config or MutatorConfig()
        self._schemas = schemas or dict(STANDARD_SCHEMA_APPLICATORS)
        self._temperature = self.config.default_temperature
        self._stats = MutatorStats()

    @property
    def temperature(self) -> float:
        """Current system temperature."""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set system temperature (clamped to min/max)."""
        self._temperature = max(
            self.config.min_temperature,
            min(self.config.max_temperature, value),
        )

    @property
    def stats(self) -> "MutatorStats":
        """Mutation statistics."""
        return self._stats

    # -------------------------------------------------------------------
    # Schema Management
    # -------------------------------------------------------------------

    def register_schema(
        self,
        schema: MutationSchema,
        applicator: SchemaApplicator,
    ) -> None:
        """Register a new mutation schema with its applicator."""
        self._schemas[schema.name] = (schema, applicator)

    def get_viable_schemas(
        self, temperature: float | None = None
    ) -> list[MutationSchema]:
        """
        Get schemas that are thermodynamically viable at current temperature.

        Args:
            temperature: Temperature to check (defaults to current)

        Returns:
            List of viable schemas (ΔG < 0)
        """
        t = temperature or self._temperature

        return [schema for schema, _ in self._schemas.values() if schema.is_viable(t)]

    # -------------------------------------------------------------------
    # Mutation Generation
    # -------------------------------------------------------------------

    def mutate(
        self,
        code: str,
        temperature: float | None = None,
    ) -> list[MutationVector]:
        """
        Generate mutations for code.

        This is the main entry point for mutation generation.

        Args:
            code: Source code to mutate
            temperature: Temperature for this mutation batch

        Returns:
            List of MutationVectors (pre-filtered by Gibbs if configured)
        """
        t = temperature or self._temperature

        # Analyze hot spots
        hot_spots = analyze_hot_spots(code)

        # Filter to significant hot spots
        hot_spots = [h for h in hot_spots if h.complexity >= self.config.min_complexity]

        mutations: list[MutationVector] = []

        # Apply schemas to each hot spot
        for hot_spot in hot_spots[: self.config.max_mutations]:
            # Extract code for this hot spot
            lines = code.split("\n")
            spot_code = "\n".join(
                lines[hot_spot.lineno_start - 1 : hot_spot.lineno_end]
            )

            for schema_name, (schema, applicator) in self._schemas.items():
                # Check Gibbs viability
                if self.config.require_gibbs_viable and not schema.is_viable(t):
                    continue

                # Try to apply schema
                try:
                    result = applicator(spot_code, hot_spot)
                    if result and result.success:
                        # Create MutationVector
                        mutation = MutationVector(
                            schema_signature=schema_name,
                            original_code=result.original_code,
                            mutated_code=result.mutated_code,
                            enthalpy_delta=schema.enthalpy_delta,
                            entropy_delta=schema.entropy_delta,
                            temperature=t,
                            description=schema.description,
                            confidence=schema.confidence,
                            lines_changed=_count_line_changes(
                                result.original_code,
                                result.mutated_code,
                            ),
                        )
                        mutations.append(mutation)
                        self._stats.mutations_generated += 1

                        if len(mutations) >= self.config.max_mutations:
                            break
                except Exception:
                    self._stats.application_errors += 1

            if len(mutations) >= self.config.max_mutations:
                break

        # Also try schemas on full code
        if len(mutations) < self.config.max_mutations:
            for schema_name, (schema, applicator) in self._schemas.items():
                if self.config.require_gibbs_viable and not schema.is_viable(t):
                    continue

                try:
                    result = applicator(code, None)
                    if result and result.success:
                        mutation = MutationVector(
                            schema_signature=schema_name,
                            original_code=result.original_code,
                            mutated_code=result.mutated_code,
                            enthalpy_delta=schema.enthalpy_delta,
                            entropy_delta=schema.entropy_delta,
                            temperature=t,
                            description=schema.description,
                            confidence=schema.confidence,
                            lines_changed=_count_line_changes(
                                result.original_code,
                                result.mutated_code,
                            ),
                        )
                        mutations.append(mutation)
                        self._stats.mutations_generated += 1
                except Exception:
                    self._stats.application_errors += 1

        return mutations

    def mutate_to_phages(
        self,
        code: str,
        module_name: str = "",
        temperature: float | None = None,
    ) -> list[Phage]:
        """
        Generate mutations and wrap in Phages.

        Convenience method for the evolution cycle.

        Args:
            code: Source code to mutate
            module_name: Name of the module being mutated
            temperature: Temperature for this mutation batch

        Returns:
            List of Phages ready for selection
        """
        mutations = self.mutate(code, temperature)

        phages = []
        for mutation in mutations:
            phage = Phage(
                target_module=module_name,
                mutation=mutation,
                hypothesis=mutation.description,
                status=PhageStatus.MUTATED,
                lineage=PhageLineage(
                    schema_signature=mutation.schema_signature,
                ),
            )
            phages.append(phage)

        return phages


@dataclass
class MutatorStats:
    """Statistics for mutation generation."""

    mutations_generated: int = 0
    application_errors: int = 0
    hot_spots_found: int = 0
    schemas_applied: int = 0

    def reset(self) -> None:
        """Reset all statistics."""
        self.mutations_generated = 0
        self.application_errors = 0
        self.hot_spots_found = 0
        self.schemas_applied = 0


# =============================================================================
# Utility Functions
# =============================================================================


def _count_line_changes(original: str, mutated: str) -> int:
    """Count the number of lines changed between original and mutated."""
    orig_lines = original.split("\n")
    mut_lines = mutated.split("\n")

    # Simple diff approximation
    changes = abs(len(orig_lines) - len(mut_lines))

    min_lines = min(len(orig_lines), len(mut_lines))
    for i in range(min_lines):
        if orig_lines[i] != mut_lines[i]:
            changes += 1

    return changes


# =============================================================================
# Factory Functions
# =============================================================================


def create_mutator(
    temperature: float = 1.0,
    config: MutatorConfig | None = None,
) -> Mutator:
    """Create a Mutator with default configuration."""
    mutator = Mutator(config=config)
    mutator.temperature = temperature
    return mutator


def create_conservative_mutator() -> Mutator:
    """Create a conservative Mutator (low temperature, strict Gibbs)."""
    config = MutatorConfig(
        default_temperature=0.5,
        require_gibbs_viable=True,
        max_mutations=5,
    )
    return Mutator(config=config)


def create_exploratory_mutator() -> Mutator:
    """Create an exploratory Mutator (high temperature, more mutations)."""
    config = MutatorConfig(
        default_temperature=3.0,
        require_gibbs_viable=False,  # Allow some non-viable schemas
        max_mutations=20,
        min_complexity=1.0,  # Target more spots
    )
    return Mutator(config=config)
