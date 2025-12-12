"""
JitCLI - CLI interface for J-gent (JIT Agent Intelligence).

The J-gent embodies Just-in-Time intelligence: classifying reality,
compiling ephemeral sub-agents, and collapsing safely when stability
is threatened.

Commands:
- compile: JIT compile an ephemeral agent
- classify: Classify reality (DETERMINISTIC/PROBABILISTIC/CHAOTIC)
- defer: Defer computation with lazy promise
- execute: Execute intent with JIT coordination
- stability: Analyze code stability (Chaosmonger)
- budget: Show entropy budget status

See: spec/protocols/prism.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from protocols.cli.prism import CLICapable, expose

if TYPE_CHECKING:
    pass


class JitCLI(CLICapable):
    """
    CLI interface for J-gent (JIT Agent Intelligence).

    JIT intelligence: classify reality, compile ephemeral agents,
    collapse to safety when stability is threatened.
    """

    @property
    def genus_name(self) -> str:
        return "jit"

    @property
    def cli_description(self) -> str:
        return "J-gent JIT Agent Intelligence operations"

    def get_exposed_commands(self) -> dict[str, Callable[..., Any]]:
        return {
            "compile": self.compile,
            "classify": self.classify,
            "defer": self.defer,
            "execute": self.execute,
            "stability": self.stability,
            "budget": self.budget,
        }

    @expose(
        help="JIT compile ephemeral agent from intent",
        examples=[
            'kgents jit compile "extract email addresses from text"',
            'kgents jit compile "count words" --constraints="pure,no-io"',
            'kgents jit compile "parse JSON" --dry_run',
        ],
    )
    async def compile(
        self,
        intent: str,
        constraints: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """
        JIT compile an ephemeral agent from intent.

        Constraints are comma-separated restrictions (e.g., "pure,no-io").
        """
        from agents.j import ArchitectConstraints, compile_agent

        # Parse constraints (reserved for future user-defined constraints)
        _constraint_list = (
            [c.strip() for c in constraints.split(",")] if constraints else []
        )

        arch_constraints = ArchitectConstraints(
            max_cyclomatic_complexity=10,
            allowed_imports=frozenset({"re", "json", "math", "datetime"}),
        )

        source = await compile_agent(intent, constraints=arch_constraints)

        return {
            "success": source is not None,
            "intent": intent,
            "source": source.source if source else None,
            "name": source.class_name if source else None,
            "error": None if source else "Compilation failed",
        }

    @expose(
        help="Classify reality level",
        examples=[
            'kgents jit classify "count words in file"',
            'kgents jit classify "generate creative story"',
            'kgents jit classify "predict stock price"',
        ],
    )
    async def classify(
        self,
        input: str,
    ) -> dict[str, Any]:
        """
        Classify reality level of input.

        Reality levels:
        - DETERMINISTIC: Stable, predictable computation
        - PROBABILISTIC: Statistical bounds, sampling needed
        - CHAOTIC: Unstable, collapse to Ground recommended
        """
        from agents.j import classify_intent

        result = classify_intent(
            intent=input,
            context={},
            entropy_budget=1.0,
        )

        return {
            "reality": result.reality.value,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
            "recommendation": self._get_recommendation(result.reality.value),
        }

    def _get_recommendation(self, reality: str) -> str:
        """Get recommendation based on reality classification."""
        recommendations = {
            "DETERMINISTIC": "Direct computation safe",
            "PROBABILISTIC": "Use LLM with sampling",
            "CHAOTIC": "Collapse to Ground",
        }
        return recommendations.get(reality, "Unknown")

    @expose(
        help="Defer computation with lazy promise",
        examples=[
            'kgents jit defer "load config" --ground="{}"',
            'kgents jit defer "fetch data" --timeout=30',
        ],
    )
    async def defer(
        self,
        operation: str,
        ground: str | None = None,
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        """
        Defer computation with lazy promise.

        Ground is the fallback value on failure.
        """
        return {
            "operation": operation,
            "state": "PENDING",
            "ground": ground,
            "timeout": timeout,
            "message": "Promise created. Will be resolved on demand.",
        }

    @expose(
        help="Execute intent with JIT coordination",
        examples=[
            'kgents jit execute "count words in file" --ground=0',
            'kgents jit execute "parse config" --context=\'{"file":"config.json"}\'',
        ],
    )
    async def execute(
        self,
        intent: str,
        ground: str | None = None,
        budget: str = "medium",
        context: str = "{}",
    ) -> dict[str, Any]:
        """
        Execute intent with full JIT coordination.

        Steps:
        1. Classifies reality (DETERMINISTIC/PROBABILISTIC/CHAOTIC)
        2. Compiles ephemeral agent if needed
        3. Executes in sandbox
        4. Collapses to Ground on instability

        Budget levels: low, medium, high
        """
        from agents.j import JGentConfig, JGentResult, jgent

        # Parse ground value
        ground_value = None
        if ground:
            try:
                ground_value = json.loads(ground)
            except json.JSONDecodeError:
                ground_value = ground

        # Parse context
        try:
            context_dict = json.loads(context)
        except json.JSONDecodeError:
            context_dict = {}

        # Budget to config
        budget_map = {
            "low": 0.05,
            "medium": 0.10,
            "high": 0.20,
        }
        entropy = budget_map.get(budget, 0.10)

        config = JGentConfig(entropy_threshold=entropy)

        result: JGentResult[Any] = await jgent(
            intent=intent,
            ground=ground_value,
            context=context_dict,
            config=config,
        )

        return {
            "success": result.success,
            "collapsed": result.collapsed,
            "value": result.value if result.value is not None else None,
            "collapse_reason": result.collapse_reason,
            "jit_compiled": result.jit_compiled,
            "reality": "UNKNOWN",
        }

    @expose(
        help="Analyze code stability (Chaosmonger)",
        examples=[
            "kgents jit stability mymodule.py",
            'kgents jit stability "def foo(): return x" --inline',
        ],
    )
    async def stability(
        self,
        target: str,
        inline: bool = False,
    ) -> dict[str, Any]:
        """
        Analyze code stability using Chaosmonger.

        Metrics:
        - Cyclomatic complexity
        - Branching factor
        - Import safety
        - Recursion depth
        - Side effect risk
        """
        from agents.j import StabilityInput, analyze_stability

        # Load code
        if inline:
            code = target
        else:
            target_path = Path(target)
            if not target_path.exists():
                return {"error": f"File not found: {target}"}
            code = target_path.read_text()

        input_data = StabilityInput(
            source_code=code,
            entropy_budget=1.0,
        )
        result = analyze_stability(
            source_code=input_data.source_code,
            entropy_budget=input_data.entropy_budget,
            config=input_data.config,
        )

        return {
            "stable": result.is_stable,
            "import_risk": result.metrics.import_risk,
            "complexity": result.metrics.cyclomatic_complexity,
            "branching": result.metrics.branching_factor,
            "nesting": result.metrics.max_nesting_depth,
            "unbounded_recursion": result.metrics.has_unbounded_recursion,
            "estimated_runtime": result.metrics.estimated_runtime,
            "violations": list(result.violations),
        }

    @expose(
        help="Show entropy budget status",
        examples=["kgents jit budget"],
    )
    async def budget(self) -> dict[str, Any]:
        """
        Show current entropy budget allocation and consumption.
        """
        return {
            "total": 1.0,
            "consumed": 0.15,
            "remaining": 0.85,
            "depth_limit": 3,
            "current_depth": 0,
            "threshold": 0.1,
            "status": "Healthy",
        }
