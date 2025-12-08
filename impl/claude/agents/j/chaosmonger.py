"""
Chaosmonger - AST-based stability analyzer for JIT-compiled code.

The Chaosmonger is the pre-Judge filter that handles computable safety:
- Import whitelist/blacklist checking
- Cyclomatic complexity analysis
- Branching factor estimation
- Unbounded recursion detection

See spec/j-gents/stability.md for the full specification.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any

from bootstrap.types import Agent


# --- Configuration ---


# Import risk scores (0.0 = safe, 1.0 = dangerous)
IMPORT_RISK: dict[str, float] = {
    # Safe (0.0)
    "typing": 0.0,
    "dataclasses": 0.0,
    "abc": 0.0,
    "enum": 0.0,
    "types": 0.0,
    # Low risk (0.1)
    "re": 0.1,
    "json": 0.1,
    "functools": 0.1,
    "collections": 0.1,
    "itertools": 0.1,
    "operator": 0.1,
    "math": 0.1,
    # Medium risk (0.2-0.4)
    "asyncio": 0.2,
    "logging": 0.2,
    "pathlib": 0.3,
    "datetime": 0.1,
    "hashlib": 0.2,
    # Medium-high risk (0.5-0.7)
    "requests": 0.6,
    "urllib": 0.6,
    "http": 0.6,
    "os": 0.7,
    # High risk (0.8+)
    "subprocess": 0.9,
    "sys": 0.8,
    "shutil": 0.8,
    "socket": 0.9,
    "multiprocessing": 0.7,
    "threading": 0.6,
}

# Default unknown import risk
DEFAULT_IMPORT_RISK = 0.5


@dataclass
class StabilityConfig:
    """Configuration for stability analysis."""

    # Thresholds (scaled by entropy budget)
    max_cyclomatic_complexity: int = 20
    max_branching_factor: int = 5
    max_import_risk: float = 0.5

    # Absolute limits (not scaled)
    chaos_threshold: float = 0.1
    max_depth: int = 3

    # Import control
    allowed_imports: frozenset[str] = field(
        default_factory=lambda: frozenset({
            "typing",
            "dataclasses",
            "abc",
            "enum",
            "re",
            "json",
            "asyncio",
            "functools",
            "collections",
            "itertools",
            "operator",
            "math",
            "datetime",
        })
    )

    forbidden_imports: frozenset[str] = field(
        default_factory=lambda: frozenset({
            "os",
            "subprocess",
            "sys",
            "shutil",
            "socket",
            "requests",
            "urllib",
            "http",
            "multiprocessing",
        })
    )


# Singleton default config
DEFAULT_CONFIG = StabilityConfig()


# --- Input/Output Types ---


@dataclass(frozen=True)
class StabilityMetrics:
    """Quantitative stability measurements."""

    cyclomatic_complexity: int
    branching_factor: int
    import_risk: float
    has_unbounded_recursion: bool
    estimated_runtime: str  # "O(1)", "O(n)", "O(n^2)", "unbounded"
    import_count: int
    function_count: int
    max_nesting_depth: int


@dataclass(frozen=True)
class StabilityInput:
    """Input to the Chaosmonger agent."""

    source_code: str  # Python source to analyze
    entropy_budget: float  # Available budget (0.0-1.0)
    config: StabilityConfig = field(default_factory=lambda: DEFAULT_CONFIG)


@dataclass(frozen=True)
class StabilityResult:
    """Output from the Chaosmonger agent."""

    is_stable: bool
    metrics: StabilityMetrics
    violations: tuple[str, ...]  # Why unstable (if any)


# --- AST Analysis Functions ---


def _extract_imports(tree: ast.AST) -> list[str]:
    """Extract all imported module names from AST."""
    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # Get the base module (e.g., "os" from "os.path")
                base = alias.name.split(".")[0]
                imports.append(base)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                base = node.module.split(".")[0]
                imports.append(base)

    return imports


def _check_imports(
    imports: list[str],
    config: StabilityConfig,
    budget: float,
) -> tuple[bool, float, list[str]]:
    """
    Check imports against whitelist/blacklist and calculate risk.

    Returns (is_safe, total_risk, violations).
    """
    violations: list[str] = []
    total_risk = 0.0

    for imp in imports:
        # Check forbidden list first
        if imp in config.forbidden_imports:
            violations.append(f"Import '{imp}' is forbidden")
            continue

        # Check if in allowed list
        if imp not in config.allowed_imports:
            # Not in whitelist - check risk
            risk = IMPORT_RISK.get(imp, DEFAULT_IMPORT_RISK)
            if risk > 0.5:
                violations.append(f"Import '{imp}' not in allowed list (risk={risk:.1f})")
            total_risk += risk
        else:
            total_risk += IMPORT_RISK.get(imp, 0.0)

    # Check total risk against budget-scaled threshold
    threshold = budget * config.max_import_risk
    if total_risk > threshold and not violations:
        violations.append(
            f"Total import risk ({total_risk:.2f}) exceeds threshold ({threshold:.2f})"
        )

    is_safe = len(violations) == 0
    return is_safe, total_risk, violations


def _calculate_cyclomatic_complexity(tree: ast.AST) -> int:
    """
    Calculate cyclomatic complexity of the code.

    CC = 1 + number of decision points (if, for, while, try, with, etc.)
    """
    complexity = 1  # Base complexity

    for node in ast.walk(tree):
        # Each decision point adds 1
        if isinstance(node, (ast.If, ast.For, ast.While, ast.AsyncFor)):
            complexity += 1
        elif isinstance(node, ast.ExceptHandler):
            complexity += 1
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            complexity += 1
        elif isinstance(node, ast.comprehension):
            complexity += 1  # List/dict/set comprehensions
        elif isinstance(node, ast.BoolOp):
            # 'and' and 'or' add branches
            complexity += len(node.values) - 1
        elif isinstance(node, ast.IfExp):
            complexity += 1  # Ternary operator

    return complexity


def _estimate_branching_factor(tree: ast.AST) -> int:
    """
    Estimate branching factor - expected width of computation tree.

    High branching = wide trees = resource exhaustion risk.
    """
    max_branches = 1

    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            # Count elif/else branches
            branches = 1  # if branch
            if node.orelse:
                branches += 1  # else/elif
            max_branches = max(max_branches, branches)

        elif isinstance(node, ast.Match):
            # Match statement branches
            branches = len(node.cases) if hasattr(node, "cases") else 1
            max_branches = max(max_branches, branches)

        elif isinstance(node, ast.FunctionDef):
            # Count return statements as potential branches
            return_count = sum(
                1 for n in ast.walk(node) if isinstance(n, ast.Return)
            )
            if return_count > 1:
                max_branches = max(max_branches, return_count)

    return max_branches


def _has_unbounded_recursion(tree: ast.AST) -> bool:
    """
    Detect patterns that may never terminate.

    Checks for:
    1. while True without break
    2. Recursive functions without apparent base case
    """
    function_names: set[str] = set()
    recursive_functions: set[str] = set()

    # First pass: collect function names
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_names.add(node.name)

    # Second pass: check for unbounded patterns
    for node in ast.walk(tree):
        # Pattern 1: while True without break
        if isinstance(node, ast.While):
            if _is_always_true(node.test) and not _has_break_in_loop(node):
                return True

        # Pattern 2: Check for recursive calls
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_name = node.name
            if _calls_self(node, func_name) and not _has_base_case(node):
                recursive_functions.add(func_name)

    # If any function is recursive without base case, flag it
    return len(recursive_functions) > 0


def _is_always_true(node: ast.expr) -> bool:
    """Check if an expression is always true."""
    if isinstance(node, ast.Constant):
        return bool(node.value)
    if isinstance(node, ast.NameConstant):  # Python 3.7 compatibility
        return bool(node.value)
    return False


def _has_break_in_loop(node: ast.While | ast.For) -> bool:
    """Check if a loop body contains a break statement."""
    for child in ast.walk(node):
        if isinstance(child, ast.Break):
            return True
        # Don't look into nested loops
        if child is not node and isinstance(child, (ast.While, ast.For)):
            continue
    return False


def _calls_self(func: ast.FunctionDef | ast.AsyncFunctionDef, name: str) -> bool:
    """Check if a function calls itself."""
    for node in ast.walk(func):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == name:
                return True
    return False


def _has_base_case(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """
    Heuristic: check if function has an early return or base case pattern.

    Looks for:
    - Return before any recursive call
    - If statement at the start with a return
    """
    body = func.body
    if not body:
        return False

    # Check first few statements for base case pattern
    for i, stmt in enumerate(body[:3]):  # Look at first 3 statements
        if isinstance(stmt, ast.Return):
            return True  # Early return = base case
        if isinstance(stmt, ast.If):
            # Check if the if block has a return
            for sub in ast.walk(stmt):
                if isinstance(sub, ast.Return):
                    return True

    return False


def _calculate_max_nesting(tree: ast.AST) -> int:
    """Calculate maximum nesting depth of control structures."""
    max_depth = 0

    def _walk_with_depth(node: ast.AST, depth: int) -> None:
        nonlocal max_depth

        # Track depth for control structures
        if isinstance(
            node,
            (
                ast.If,
                ast.For,
                ast.While,
                ast.With,
                ast.Try,
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            depth += 1
            max_depth = max(max_depth, depth)

        for child in ast.iter_child_nodes(node):
            _walk_with_depth(child, depth)

    _walk_with_depth(tree, 0)
    return max_depth


def _estimate_runtime(tree: ast.AST) -> str:
    """
    Heuristic estimation of runtime complexity.

    Very rough estimate based on nesting of loops.
    """
    loop_depth = 0
    max_loop_depth = 0

    def _walk_loops(node: ast.AST, current_depth: int) -> None:
        nonlocal max_loop_depth

        if isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
            current_depth += 1
            max_loop_depth = max(max_loop_depth, current_depth)

        for child in ast.iter_child_nodes(node):
            _walk_loops(child, current_depth)

    _walk_loops(tree, 0)

    if max_loop_depth == 0:
        return "O(1)"
    elif max_loop_depth == 1:
        return "O(n)"
    elif max_loop_depth == 2:
        return "O(n^2)"
    elif max_loop_depth == 3:
        return "O(n^3)"
    else:
        return "unbounded"


def _count_functions(tree: ast.AST) -> int:
    """Count function definitions in the AST."""
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            count += 1
    return count


# --- Main Analysis Function ---


def analyze_stability(
    source_code: str,
    entropy_budget: float,
    config: StabilityConfig = DEFAULT_CONFIG,
) -> StabilityResult:
    """
    Analyze Python source code for stability.

    Applies checks in order:
    1. Import whitelist/blacklist
    2. Cyclomatic complexity
    3. Branching factor
    4. Unbounded recursion

    Args:
        source_code: Python source to analyze
        entropy_budget: Available budget (0.0-1.0)
        config: Stability configuration

    Returns:
        StabilityResult with is_stable, metrics, and violations
    """
    violations: list[str] = []

    # Try to parse the source
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return StabilityResult(
            is_stable=False,
            metrics=StabilityMetrics(
                cyclomatic_complexity=0,
                branching_factor=0,
                import_risk=0.0,
                has_unbounded_recursion=False,
                estimated_runtime="unknown",
                import_count=0,
                function_count=0,
                max_nesting_depth=0,
            ),
            violations=(f"Syntax error: {e}",),
        )

    # Extract imports
    imports = _extract_imports(tree)

    # Check 1: Import safety
    import_safe, import_risk, import_violations = _check_imports(
        imports, config, entropy_budget
    )
    violations.extend(import_violations)

    # Check 2: Cyclomatic complexity
    complexity = _calculate_cyclomatic_complexity(tree)
    complexity_threshold = int(entropy_budget * config.max_cyclomatic_complexity)
    if complexity > complexity_threshold:
        violations.append(
            f"Cyclomatic complexity ({complexity}) exceeds threshold ({complexity_threshold})"
        )

    # Check 3: Branching factor
    branching = _estimate_branching_factor(tree)
    branching_threshold = int(entropy_budget * config.max_branching_factor)
    if branching > branching_threshold and branching > 1:
        violations.append(
            f"Branching factor ({branching}) exceeds threshold ({branching_threshold})"
        )

    # Check 4: Unbounded recursion
    has_unbounded = _has_unbounded_recursion(tree)
    if has_unbounded:
        violations.append("Unbounded recursion detected")

    # Calculate additional metrics
    runtime = _estimate_runtime(tree)
    function_count = _count_functions(tree)
    max_nesting = _calculate_max_nesting(tree)

    metrics = StabilityMetrics(
        cyclomatic_complexity=complexity,
        branching_factor=branching,
        import_risk=import_risk,
        has_unbounded_recursion=has_unbounded,
        estimated_runtime=runtime,
        import_count=len(imports),
        function_count=function_count,
        max_nesting_depth=max_nesting,
    )

    return StabilityResult(
        is_stable=len(violations) == 0,
        metrics=metrics,
        violations=tuple(violations),
    )


# --- Agent Implementation ---


class Chaosmonger(Agent[StabilityInput, StabilityResult]):
    """
    Agent that performs AST-based stability analysis.

    The Chaosmonger is the pre-Judge filter that handles computable safety:
    - Chaosmonger: handles what CAN be computed (complexity, imports, recursion)
    - Judge: handles what CANNOT be computed (taste, ethics, joy)

    Pipeline:
        GeneratedCode → Chaosmonger → [stable?] → Judge → [accept?] → Execute
                             ↓                      ↓
                       [unstable]              [reject]
                             ↓                      ↓
                          Ground                 Ground
    """

    def __init__(self, config: StabilityConfig = DEFAULT_CONFIG):
        """
        Initialize the Chaosmonger.

        Args:
            config: Stability configuration (thresholds, allowed imports, etc.)
        """
        self._config = config

    @property
    def name(self) -> str:
        return "Chaosmonger"

    async def invoke(self, input: StabilityInput) -> StabilityResult:
        """
        Analyze source code for stability.

        Args:
            input: StabilityInput with source_code, entropy_budget, and config

        Returns:
            StabilityResult with is_stable, metrics, and violations
        """
        return analyze_stability(
            source_code=input.source_code,
            entropy_budget=input.entropy_budget,
            config=input.config,
        )


# --- Convenience Functions ---


def check_stability(
    source_code: str,
    entropy_budget: float = 1.0,
    config: StabilityConfig | None = None,
) -> StabilityResult:
    """
    Convenience function to check stability synchronously.

    Args:
        source_code: Python source to analyze
        entropy_budget: Available budget (default 1.0)
        config: Optional custom configuration

    Returns:
        StabilityResult with is_stable, metrics, and violations
    """
    return analyze_stability(
        source_code=source_code,
        entropy_budget=entropy_budget,
        config=config or DEFAULT_CONFIG,
    )


def is_stable(
    source_code: str,
    entropy_budget: float = 1.0,
) -> bool:
    """
    Quick check if code is stable.

    Args:
        source_code: Python source to analyze
        entropy_budget: Available budget (default 1.0)

    Returns:
        True if code passes all stability checks
    """
    result = check_stability(source_code, entropy_budget)
    return result.is_stable
