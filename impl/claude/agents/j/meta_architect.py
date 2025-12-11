"""
MetaArchitect: JIT Agent Compiler

The agent that generates agents on demand.

Morphism: ArchitectInput → AgentSource

Philosophy:
> "The agent that doesn't exist yet is the agent you need most."

Given an intent, context, and constraints, MetaArchitect generates Python
source code for a specialized agent. The generated code must:
- Pass Chaosmonger stability checks
- Pass Judge ethical evaluation (via bootstrap Judge)
- Pass mypy --strict type checking
- Execute within entropy budget constraints

Bootstrap Integration:
- Uses bootstrap Judge for ethical evaluation of generated code
- Generated agents inherit from bootstrap Agent interface
- Safety validation via principle-based judgment

See spec/j-gents/jit.md for full specification.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any, Optional, Callable

from bootstrap.types import Agent, PartialVerdict, Verdict
from bootstrap.judge import Judge as BootstrapJudge, JudgeInput, MINI_JUDGES

# Template generation (Phase D - H12)
from .templates import TemplateContext, generate_template


@dataclass(frozen=True)
class ArchitectInput:
    """Input for MetaArchitect JIT compilation."""

    intent: str  # Natural language description of agent purpose
    context: dict[str, Any] = field(default_factory=dict)  # Available data/examples
    constraints: ArchitectConstraints = field(
        default_factory=lambda: ArchitectConstraints()
    )


@dataclass(frozen=True)
class ArchitectConstraints:
    """Safety and resource constraints for JIT compilation."""

    entropy_budget: float = 1.0  # Diminishes with depth
    max_cyclomatic_complexity: int = 20  # AST complexity limit
    max_branching_factor: int = 5  # Expected tree width
    allowed_imports: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                "re",  # Regex
                "json",  # JSON parsing
                "dataclasses",  # Data structures
                "typing",  # Type hints
                "datetime",  # Time handling
                "math",  # Math operations
            }
        )
    )
    forbidden_patterns: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                "eval",
                "exec",
                "compile",
                "__import__",
                "open",
                "input",
                "globals",
                "locals",
                "os.system",
                "subprocess",
            }
        )
    )


@dataclass(frozen=True)
class AgentSource:
    """Generated agent source code."""

    source: str  # Python source code
    class_name: str  # Name of the agent class
    imports: frozenset[str]  # Required imports
    complexity: int  # Cyclomatic complexity
    description: str  # What this agent does


class MetaArchitect(Agent[ArchitectInput, AgentSource]):
    """
    JIT Agent Compiler: Generate specialized agents on demand.

    This is the core of J-gents JIT compilation. Given an intent and context,
    it generates Python source code for a new agent that can handle the task.

    The generated code is:
    - Syntactically valid Python
    - Type-safe (passes mypy --strict)
    - Within complexity budget
    - Uses only allowed imports
    - Contains no forbidden patterns

    After generation, the source flows through:
    1. Chaosmonger (stability check)
    2. Judge (ethical evaluation)
    3. Type checker (mypy)
    4. Sandbox compilation (restricted namespace)
    5. Execution (with timeout)
    """

    @property
    def name(self) -> str:
        return "MetaArchitect"

    async def invoke(self, input: ArchitectInput) -> AgentSource:
        """
        Generate agent source code for the given intent.

        This is a simplified reference implementation. In production, this would:
        1. Use an LLM to generate code based on intent + examples
        2. Apply constraints to guide generation
        3. Iteratively refine until constraints satisfied
        4. Return validated source code

        For now, we implement template-based generation for common patterns.
        """
        # Parse intent to determine agent pattern
        pattern = self._classify_intent(input.intent)

        # Generate source based on pattern
        source = self._generate_source(pattern, input)

        # Extract metadata
        class_name = self._extract_class_name(source)
        imports = self._extract_imports(source)
        complexity = self._calculate_complexity(source)

        return AgentSource(
            source=source,
            class_name=class_name,
            imports=imports,
            complexity=complexity,
            description=input.intent,
        )

    def _classify_intent(self, intent: str) -> str:
        """
        Classify the intent to determine generation pattern.

        Patterns:
        - parser: Parse structured text (logs, configs, etc.)
        - filter: Filter data based on criteria
        - transformer: Transform data from format A to format B
        - analyzer: Extract insights from data
        - validator: Check data against rules
        """
        intent_lower = intent.lower()

        if any(kw in intent_lower for kw in ["parse", "extract", "tokenize"]):
            return "parser"
        elif any(kw in intent_lower for kw in ["filter", "select", "find"]):
            return "filter"
        elif any(kw in intent_lower for kw in ["transform", "convert", "map"]):
            return "transformer"
        elif any(kw in intent_lower for kw in ["analyze", "identify", "detect"]):
            return "analyzer"
        elif any(kw in intent_lower for kw in ["validate", "check", "verify"]):
            return "validator"
        else:
            return "generic"

    def _generate_source(self, pattern: str, input: ArchitectInput) -> str:
        """
        Generate source code based on pattern and input.

        Refactored (Phase D - H12) to use templates module for cleaner separation.

        This is template-based for simplicity. Production version would use
        LLM-based code generation with constraint-guided sampling.
        """
        # Use extracted template module (Phase D - H12)
        ctx = TemplateContext(intent=input.intent, context=input.context)
        return generate_template(pattern, ctx)

    def _extract_class_name(self, source: str) -> str:
        """
        Extract the main agent class name from source code.

        Returns the last class that starts with 'JIT' or the last class overall.
        This avoids returning dataclass definitions.
        """
        try:
            tree = ast.parse(source)
            classes = [
                node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
            ]

            if not classes:
                return "JITAgent"

            # Prefer classes that start with "JIT"
            jit_classes = [c for c in classes if c.startswith("JIT")]
            if jit_classes:
                return jit_classes[-1]  # Return last JIT class

            # Otherwise return last class
            return classes[-1]

        except SyntaxError:
            pass

        # Fallback
        return "JITAgent"

    def _extract_imports(self, source: str) -> frozenset[str]:
        """Extract import statements from source code."""
        imports: set[str] = set()

        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])
        except SyntaxError:
            pass

        return frozenset(imports)

    def _calculate_complexity(self, source: str) -> int:
        """
        Calculate cyclomatic complexity of generated code.

        Simplified McCabe complexity: count decision points.
        """
        complexity = 1  # Base complexity

        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                # Decision points: if, for, while, except, and, or
                if isinstance(
                    node,
                    (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.BoolOp),
                ):
                    complexity += 1
                # Also count function definitions (entry points)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity += 1
        except SyntaxError:
            # If source is invalid, return high complexity to trigger rejection
            return 999

        return complexity


# --- Convenience Functions ---


async def compile_agent(
    intent: str,
    context: dict[str, Any] | None = None,
    constraints: ArchitectConstraints | None = None,
) -> AgentSource:
    """
    Convenience function to compile a JIT agent.

    Args:
        intent: Natural language description of agent purpose
        context: Optional context (examples, formats, etc.)
        constraints: Optional safety/resource constraints

    Returns:
        AgentSource with generated code

    Example:
        >>> source = await compile_agent(
        ...     intent="Parse NGINX logs and extract 4xx errors",
        ...     context={"sample": "127.0.0.1 - - [01/Jan/2025:12:00:00] ..."},
        ... )
        >>> print(source.source)
    """
    architect = MetaArchitect()
    input_data = ArchitectInput(
        intent=intent,
        context=context or {},
        constraints=constraints or ArchitectConstraints(),
    )
    return await architect.invoke(input_data)


def validate_source_safety(
    source: AgentSource, constraints: ArchitectConstraints
) -> tuple[bool, str]:
    """
    Validate that generated source meets safety constraints.

    Args:
        source: Generated agent source
        constraints: Safety constraints to enforce

    Returns:
        (is_safe, reason) tuple

    Checks:
    - Complexity within budget
    - Only allowed imports
    - No forbidden patterns
    """
    # Check complexity
    max_complexity = int(
        constraints.entropy_budget * constraints.max_cyclomatic_complexity
    )
    if source.complexity > max_complexity:
        return (
            False,
            f"Complexity {source.complexity} exceeds budget {max_complexity}",
        )

    # Check imports
    forbidden_imports = source.imports - constraints.allowed_imports
    if forbidden_imports:
        return (False, f"Forbidden imports: {forbidden_imports}")

    # Check patterns
    for pattern in constraints.forbidden_patterns:
        if pattern in source.source:
            return (False, f"Forbidden pattern detected: {pattern}")

    return (True, "Source passes safety checks")


# --- Bootstrap Judge Integration for JIT Code ---


def check_jit_safe(
    agent: Agent[Any, Any], context: Optional[dict[str, Any]] = None
) -> PartialVerdict:
    """
    JIT-specific safety check: no forbidden patterns in source.

    A mini-judge for the "jit_safe" principle.
    """
    source_code = context.get("source_code", "") if context else ""
    constraints = (
        context.get("constraints", ArchitectConstraints())
        if context
        else ArchitectConstraints()
    )

    for pattern in constraints.forbidden_patterns:
        if pattern in source_code:
            return PartialVerdict(
                principle="jit_safe",
                passed=False,
                reasons=(f"Forbidden pattern '{pattern}' detected in generated code",),
                confidence=1.0,
            )

    return PartialVerdict(
        principle="jit_safe",
        passed=True,
        reasons=(),
        confidence=1.0,
    )


def check_entropy_bounded(
    agent: Agent[Any, Any], context: Optional[dict[str, Any]] = None
) -> PartialVerdict:
    """
    JIT-specific check: complexity within entropy budget.

    A mini-judge for the "entropy_bounded" principle.
    """
    complexity = context.get("complexity", 0) if context else 0
    entropy_budget = context.get("entropy_budget", 1.0) if context else 1.0
    max_complexity = context.get("max_cyclomatic_complexity", 20) if context else 20

    max_allowed = int(entropy_budget * max_complexity)
    passed = complexity <= max_allowed

    return PartialVerdict(
        principle="entropy_bounded",
        passed=passed,
        reasons=(f"Complexity {complexity} vs budget {max_allowed}",)
        if not passed
        else (),
        confidence=0.9,
    )


def check_imports_allowed(
    agent: Agent[Any, Any], context: Optional[dict[str, Any]] = None
) -> PartialVerdict:
    """
    JIT-specific check: only allowed imports used.

    A mini-judge for the "imports_allowed" principle.
    """
    imports = context.get("imports", frozenset()) if context else frozenset()
    allowed = context.get("allowed_imports", frozenset()) if context else frozenset()

    forbidden = imports - allowed
    passed = len(forbidden) == 0

    return PartialVerdict(
        principle="imports_allowed",
        passed=passed,
        reasons=(f"Forbidden imports: {forbidden}",) if not passed else (),
        confidence=1.0,
    )


# JIT-specific mini-judges
JIT_MINI_JUDGES: dict[
    str, Callable[[Agent[Any, Any], Optional[dict[str, Any]]], PartialVerdict]
] = {
    "jit_safe": check_jit_safe,
    "entropy_bounded": check_entropy_bounded,
    "imports_allowed": check_imports_allowed,
}


class JITSafetyJudge(BootstrapJudge):
    """
    Specialized Judge for JIT-compiled agents.

    Combines bootstrap's 7 principles with JIT-specific safety checks:
    - jit_safe: No forbidden patterns (eval, exec, etc.)
    - entropy_bounded: Complexity within budget
    - imports_allowed: Only whitelisted imports

    Example:
        judge = JITSafetyJudge()
        source = await architect.invoke(input)

        verdict = await judge.evaluate_source(source, constraints)
        if verdict.type == VerdictType.ACCEPT:
            # Safe to execute
            pass
        elif verdict.type == VerdictType.REVISE:
            # Has fixable issues
            print(verdict.revisions)
    """

    def __init__(self):
        """Initialize with combined bootstrap + JIT judges."""
        combined_judges = dict(MINI_JUDGES)
        combined_judges.update(JIT_MINI_JUDGES)
        super().__init__(custom_judges=combined_judges)

    async def evaluate_source(
        self,
        source: AgentSource,
        constraints: ArchitectConstraints,
    ) -> Verdict:
        """
        Evaluate generated source against JIT safety principles.

        Args:
            source: Generated agent source
            constraints: Safety constraints

        Returns:
            Verdict with ACCEPT, REVISE, or REJECT
        """

        # Create a stub agent to represent the generated source
        class GeneratedAgentStub(Agent[Any, Any]):
            """Stub agent for judging generated source."""

            @property
            def name(self) -> str:
                return source.class_name

            async def invoke(self, input: Any) -> Any:
                raise NotImplementedError("Stub agent - not for execution")

        stub = GeneratedAgentStub()

        return await self.invoke(
            JudgeInput(
                agent=stub,
                principles=(
                    "jit_safe",
                    "entropy_bounded",
                    "imports_allowed",
                    "ethical",  # Bootstrap ethical principle
                    "composable",  # Bootstrap composable principle
                ),
                context={
                    "source_code": source.source,
                    "complexity": source.complexity,
                    "imports": source.imports,
                    "entropy_budget": constraints.entropy_budget,
                    "max_cyclomatic_complexity": constraints.max_cyclomatic_complexity,
                    "allowed_imports": constraints.allowed_imports,
                    "constraints": constraints,
                },
            )
        )


# Singleton safety judge
jit_safety_judge = JITSafetyJudge()
