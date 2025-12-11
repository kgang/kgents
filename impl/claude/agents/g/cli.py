"""
GrammarianCLI - CLI interface for G-gent (Grammarian).

Exposes G-gent capabilities via the Prism pattern:
- reify: Create Tongue artifacts from domain descriptions
- parse: Parse input using a Tongue
- evolve: Evolve Tongue from new examples
- list: List registered Tongues
- show: Show Tongue details
- validate: Validate Tongue with T-gent fuzzing
- infer: Infer grammar from observed patterns

See: spec/protocols/prism.md
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from protocols.cli.prism import CLICapable, expose

if TYPE_CHECKING:
    pass


class GrammarianCLI(CLICapable):
    """
    CLI interface for G-gent (Grammarian).

    The Grammarian synthesizes Domain Specific Languages (DSLs) from
    natural language intent + constraints.
    """

    @property
    def genus_name(self) -> str:
        return "grammar"

    @property
    def cli_description(self) -> str:
        return "G-gent Grammar/DSL operations"

    def get_exposed_commands(self) -> dict[str, Callable[..., Any]]:
        return {
            "reify": self.reify,
            "parse": self.parse,
            "evolve": self.evolve,
            "list": self.list_tongues,
            "show": self.show,
            "validate": self.validate,
            "infer": self.infer,
        }

    @expose(
        help="Reify domain into Tongue artifact",
        examples=[
            'kgents grammar reify "Calendar Management"',
            'kgents grammar reify "File Operations" --constraints="No deletes,Read-only"',
            'kgents grammar reify "Research Notes" --level=recursive',
        ],
    )
    async def reify(
        self,
        domain: str,
        level: str = "command",
        constraints: str | None = None,
        examples: str | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        """
        Reify a domain into a Tongue artifact.

        The domain string describes the conceptual space. Level controls
        grammar complexity (schema, command, recursive). Constraints are
        comma-separated semantic boundaries.
        """
        from agents.g import GrammarLevel, Grammarian

        # Map level string to enum
        level_map = {
            "schema": GrammarLevel.SCHEMA,
            "command": GrammarLevel.COMMAND,
            "recursive": GrammarLevel.RECURSIVE,
        }
        grammar_level = level_map.get(level, GrammarLevel.COMMAND)

        # Parse constraints
        constraint_list = []
        if constraints:
            constraint_list = [c.strip() for c in constraints.split(",")]

        # Load examples from file if path provided
        example_list: list[str] = []
        if examples:
            examples_path = Path(examples)
            if examples_path.exists():
                example_list = [
                    line.strip()
                    for line in examples_path.read_text().splitlines()
                    if line.strip()
                ]

        g_gent = Grammarian()
        tongue = await g_gent.reify(
            domain=domain,
            constraints=constraint_list,
            level=grammar_level,
            examples=example_list if example_list else None,
            name=name,
        )

        return {
            "name": tongue.name,
            "domain": tongue.domain,
            "level": tongue.level.value,
            "format": tongue.grammar_format.value
            if hasattr(tongue, "grammar_format")
            else "unknown",
            "grammar": tongue.grammar,
            "constraints": [p.constraint for p in tongue.proofs]
            if tongue.proofs
            else [],
            "examples": [e.input for e in tongue.examples] if tongue.examples else [],
            "version": tongue.version,
        }

    @expose(
        help="Parse input using a Tongue",
        examples=[
            'kgents grammar parse "CHECK 2024-12-15" --tongue=calendar',
            'kgents grammar parse "ADD meeting 2pm" --tongue=calendar',
        ],
    )
    async def parse(
        self,
        input_text: str,
        tongue: str,
    ) -> dict[str, Any]:
        """
        Parse input using a registered Tongue.

        The tongue must be registered in the L-gent catalog.
        Returns parse result with AST and confidence.
        """
        from agents.g import find_tongue
        from agents.l import Registry

        registry = Registry()
        tongue_obj = await find_tongue(registry, tongue)

        if tongue_obj is None:
            return {
                "success": False,
                "error": f"Tongue not found: {tongue}",
                "ast": None,
            }

        result = tongue_obj.parse(input_text)
        return {
            "success": result.success,
            "ast": str(result.ast) if result.ast else None,
            "error": result.error,
            "confidence": result.confidence,
        }

    @expose(
        help="Evolve Tongue from new examples",
        examples=[
            "kgents grammar evolve calendar --examples=new_commands.txt",
            "kgents grammar evolve calendar --refine",
        ],
    )
    async def evolve(
        self,
        tongue_name: str,
        examples: str | None = None,
        refine: bool = False,
    ) -> dict[str, Any]:
        """
        Evolve a Tongue with new examples.

        Loads the existing Tongue and uses pattern inference to
        extend or refine its grammar based on new examples.
        """
        from agents.g import PatternInferenceEngine, find_tongue
        from agents.l import Registry

        registry = Registry()
        tongue = await find_tongue(registry, tongue_name)

        if tongue is None:
            return {"error": f"Tongue not found: {tongue_name}"}

        # Load examples from file
        example_list: list[str] = []
        if examples:
            examples_path = Path(examples)
            if examples_path.exists():
                example_list = [
                    line.strip()
                    for line in examples_path.read_text().splitlines()
                    if line.strip()
                ]

        # Use pattern inference to evolve
        engine = PatternInferenceEngine()

        for example in example_list:
            engine.observe(example)

        hypothesis = engine.hypothesize()

        return {
            "new_patterns": len(hypothesis.rules) if hypothesis else 0,
            "grammar_updated": hypothesis is not None,
            "hypothesis_confidence": hypothesis.confidence if hypothesis else 0.0,
        }

    @expose(
        help="List registered Tongues",
        examples=["kgents grammar list"],
        aliases=["ls"],
    )
    async def list_tongues(self) -> dict[str, Any]:
        """
        List all registered Tongues.

        Shows name, level, and domain for each Tongue in the catalog.
        """
        from agents.l import EntityType, Registry

        registry = Registry()
        entries = await registry.find(entity_type=EntityType.TONGUE)

        tongues = [
            {
                "name": e.name,
                "domain": e.description or "unknown",
                "level": e.tongue_level or "command",
            }
            for e in entries
        ]

        return {"tongues": tongues, "count": len(tongues)}

    @expose(
        help="Show Tongue details",
        examples=["kgents grammar show calendar"],
    )
    async def show(self, name: str) -> dict[str, Any] | None:
        """
        Show detailed information about a Tongue.

        Displays grammar, constraints, examples, and version.
        """
        from agents.g import find_tongue
        from agents.l import Registry

        registry = Registry()
        tongue = await find_tongue(registry, name)

        if tongue is None:
            return {"error": f"Tongue not found: {name}"}

        return {
            "name": tongue.name,
            "domain": tongue.domain,
            "level": tongue.level.value,
            "format": tongue.grammar_format.value
            if hasattr(tongue, "grammar_format")
            else "unknown",
            "grammar": tongue.grammar,
            "constraints": [p.constraint for p in tongue.proofs]
            if tongue.proofs
            else [],
            "examples": [e.input for e in tongue.examples] if tongue.examples else [],
            "version": tongue.version,
        }

    @expose(
        help="Validate Tongue with T-gent fuzzing",
        examples=[
            "kgents grammar validate calendar",
            "kgents grammar validate calendar --iterations=500",
        ],
    )
    async def validate(
        self,
        name: str,
        iterations: int = 100,
    ) -> dict[str, Any]:
        """
        Validate a Tongue using T-gent fuzzing.

        Generates random inputs and tests the Tongue's parser,
        reporting success rate and any failures.
        """
        from agents.g import find_tongue, fuzz_tongue
        from agents.l import Registry

        registry = Registry()
        tongue = await find_tongue(registry, name)

        if tongue is None:
            return {"error": f"Tongue not found: {name}"}

        report = await fuzz_tongue(tongue, iterations=iterations)

        return {
            "iterations": report.total_inputs,
            "valid_count": report.valid_count,
            "invalid_count": report.invalid_count,
            "success_rate": report.valid_count / max(1, report.total_inputs),
            "failures": [r.input_text for r in report.results if not r.valid][:10],
        }

    @expose(
        help="Infer grammar from observed patterns",
        examples=[
            'kgents grammar infer "CHECK date, ADD event, LIST all"',
            "kgents grammar infer --file=observations.txt",
        ],
    )
    async def infer(
        self,
        patterns: str | None = None,
        file: str | None = None,
        min_confidence: float = 0.5,
    ) -> dict[str, Any]:
        """
        Infer grammar from observed patterns.

        Takes comma-separated patterns or a file with one pattern per line.
        Returns inferred grammar rules with confidence scores.
        """
        from agents.g import PatternInferenceEngine

        pattern_list: list[str] = []

        # Parse inline patterns
        if patterns:
            pattern_list.extend([p.strip() for p in patterns.split(",")])

        # Load from file
        if file:
            file_path = Path(file)
            if file_path.exists():
                pattern_list.extend(
                    [
                        line.strip()
                        for line in file_path.read_text().splitlines()
                        if line.strip()
                    ]
                )

        if not pattern_list:
            return {"error": "No patterns provided"}

        engine = PatternInferenceEngine()

        for pattern in pattern_list:
            engine.observe(pattern)

        hypothesis = engine.hypothesize()

        if hypothesis is None or hypothesis.confidence < min_confidence:
            return {
                "pattern_count": len(pattern_list),
                "rule_count": 0,
                "confidence": 0.0,
                "grammar": "",
            }

        return {
            "pattern_count": len(pattern_list),
            "rule_count": len(hypothesis.rules),
            "confidence": hypothesis.confidence,
            "grammar": hypothesis.to_bnf()
            if hasattr(hypothesis, "to_bnf")
            else str(hypothesis),
            "level": hypothesis.level.value
            if hasattr(hypothesis, "level")
            else "unknown",
        }
