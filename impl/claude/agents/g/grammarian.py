"""
Grammarian Agent (G-gent)

The Grammarian synthesizes Domain Specific Languages (DSLs) from natural
language intent + constraints.

Key capability: reify() - Transform domain intent into a Tongue artifact
(reified DSL with grammar, parser config, interpreter config, and proofs).

The G-gent embodies "Constraint is Liberation" - constraints become
structurally enforced in the grammar, making forbidden operations
grammatically impossible rather than runtime-checked.
"""

from typing import Any

from agents.g.types import (
    Tongue,
    GrammarLevel,
    GrammarFormat,
    Example,
)
from agents.g.synthesis import (
    analyze_domain,
    synthesize_grammar,
    generate_parser_config,
    generate_interpreter_config,
)
from agents.g.validation import (
    generate_constraint_proofs,
    validate_tongue_comprehensive,
    ValidationReport,
)
from agents.g.tongue import TongueBuilder


# ============================================================================
# Grammarian Agent
# ============================================================================


class Grammarian:
    """
    G-gent: The Grammarian agent.

    Synthesizes Domain Specific Languages that encode constraints
    structurally, making forbidden operations grammatically impossible.

    Primary capability: reify() - Create Tongue artifact from intent.
    """

    def __init__(self, name: str = "G-gent"):
        self.name = name

    async def reify(
        self,
        domain: str,
        constraints: list[str],
        level: GrammarLevel = GrammarLevel.COMMAND,
        examples: list[str] | None = None,
        intent: str | None = None,
        validate: bool = True,
        name: str | None = None,
        version: str = "1.0.0",
    ) -> Tongue:
        """
        Reify a domain into a Tongue artifact.

        This is the primary G-gent capability: Transform natural language
        intent + constraints into a formal DSL with structural guarantees.

        Process:
        1. Analyze domain (extract entities, operations, relationships)
        2. Synthesize grammar (BNF/EBNF/Pydantic based on level)
        3. Generate configuration (parser + interpreter configs)
        4. Verify constraints (ensure structural encoding)
        5. Create Tongue artifact

        Args:
            domain: Domain description (e.g., "Calendar Management")
            constraints: List of constraints (e.g., ["No deletes", "Read-only"])
            level: Grammar level (SCHEMA, COMMAND, RECURSIVE)
            examples: Optional example inputs to guide synthesis
            intent: Optional detailed intent description (uses domain if not provided)
            validate: Whether to validate the resulting Tongue
            name: Tongue name (inferred from domain if not provided)
            version: Version string (default "1.0.0")

        Returns:
            Tongue artifact with grammar, configs, and proofs

        Example:
            tongue = await g_gent.reify(
                domain="Calendar Management",
                constraints=["No deletes", "No overwrites"],
                level=GrammarLevel.COMMAND,
                examples=["CHECK 2024-12-15", "ADD meeting tomorrow 2pm"],
            )
        """
        # Use domain as intent if not provided
        if intent is None:
            intent = domain

        # Infer name from domain if not provided
        if name is None:
            name = self._generate_tongue_name(domain)

        # Step 1: Analyze domain
        analysis = await analyze_domain(
            intent=intent,
            constraints=constraints,
            examples=examples or [],
        )

        # Step 2: Synthesize grammar
        grammar = await synthesize_grammar(
            analysis=analysis,
            level=level,
        )

        # Step 3: Generate configurations
        format = self._infer_format(level)
        parser_config = generate_parser_config(grammar, level, format)
        interpreter_config = generate_interpreter_config(level)

        # Step 4: Generate constraint proofs
        constraint_proofs = generate_constraint_proofs(
            constraints=constraints,
            grammar=grammar,
            analysis=analysis,
        )

        # Step 5: Extract lexicon from analysis
        lexicon = analysis.lexicon

        # Step 6: Create examples
        example_objects = [
            Example(text=ex, description=f"Example from domain: {domain}")
            for ex in (examples or [])
        ]

        # Step 7: Build Tongue
        tongue = (
            TongueBuilder(name, version)
            .with_domain(domain)
            .with_level(level)
            .with_format(format)
            .with_grammar(grammar)
            .with_lexicon(*lexicon)
            .with_parser_config(parser_config)
            .with_interpreter_config(interpreter_config)
        )

        # Add constraints
        for constraint in constraints:
            tongue.with_constraint(constraint)

        # Add examples
        for example in example_objects:
            tongue.with_example(example.text, example.expected_ast, example.description)

        # Add proofs
        for proof in constraint_proofs:
            tongue.with_proof(proof)

        # Mark as validated if requested
        if validate:
            tongue.validated(True)

        result = tongue.build()

        # Step 8: Validate if requested
        if validate:
            validation_report = await validate_tongue_comprehensive(result)
            if not validation_report.is_valid:
                # Log validation issues but don't fail
                # (Production would retry synthesis with refinement)
                print(f"Validation warnings for {name}:")
                for error in validation_report.errors:
                    print(f"  - {error}")
                for ambiguity in validation_report.ambiguities:
                    print(f"  - Ambiguity: {ambiguity.description}")
                for violation in validation_report.violations:
                    print(f"  - Violation: {violation.description}")

        return result

    async def refine(
        self,
        tongue: Tongue,
        feedback: str | None = None,
        validation_report: ValidationReport | None = None,
    ) -> Tongue:
        """
        Refine a Tongue based on feedback or validation failures.

        Strategies:
        1. Eliminate ambiguities (add priority rules, lookahead)
        2. Strengthen constraints (add structural checks)
        3. Expand examples (improve coverage)

        Args:
            tongue: The Tongue to refine
            feedback: Optional human feedback
            validation_report: Optional validation report with issues

        Returns:
            Refined Tongue (new version)

        Note:
            In production, this would use LLM to iteratively improve grammar.
            For now, it's a placeholder that increments version.
        """
        # Placeholder - production would use LLM-based refinement
        from agents.g.tongue import evolve_tongue

        new_version = self._increment_version(tongue.version)
        return evolve_tongue(
            tongue,
            version=new_version,
            validated=False,  # Need to re-validate after refinement
        )

    def _generate_tongue_name(self, domain: str) -> str:
        """Generate a Tongue name from domain."""
        # Convert "Calendar Management" -> "CalendarTongue"
        words = domain.split()
        name = "".join(word.capitalize() for word in words)
        if not name.endswith("Tongue"):
            name += "Tongue"
        return name

    def _infer_format(self, level: GrammarLevel) -> GrammarFormat:
        """Infer grammar format from level."""
        match level:
            case GrammarLevel.SCHEMA:
                return GrammarFormat.PYDANTIC
            case GrammarLevel.COMMAND:
                return GrammarFormat.BNF
            case GrammarLevel.RECURSIVE:
                return GrammarFormat.LARK

    def _increment_version(self, version: str) -> str:
        """Increment semantic version (patch level)."""
        try:
            major, minor, patch = version.split(".")
            new_patch = int(patch) + 1
            return f"{major}.{minor}.{new_patch}"
        except ValueError:
            # If version doesn't parse, just append .1
            return f"{version}.1"


# ============================================================================
# Convenience Functions
# ============================================================================


async def reify(
    domain: str,
    constraints: list[str],
    level: GrammarLevel = GrammarLevel.COMMAND,
    **kwargs: Any,
) -> Tongue:
    """
    Convenience function for creating a Tongue.

    Equivalent to:
        g_gent = Grammarian()
        tongue = await g_gent.reify(domain, constraints, level, **kwargs)

    Example:
        tongue = await reify(
            domain="Safe File Operations",
            constraints=["No deletes", "No overwrites"],
            level=GrammarLevel.COMMAND,
        )
    """
    g_gent = Grammarian()
    return await g_gent.reify(domain, constraints, level, **kwargs)


async def reify_schema(
    domain: str,
    constraints: list[str] | None = None,
    **kwargs: Any,
) -> Tongue:
    """
    Convenience function for creating a SCHEMA-level Tongue.

    Example:
        tongue = await reify_schema(
            domain="User Profile",
            constraints=["Name required", "Age must be positive"],
        )
    """
    return await reify(
        domain=domain,
        constraints=constraints or [],
        level=GrammarLevel.SCHEMA,
        **kwargs,
    )


async def reify_command(
    domain: str,
    constraints: list[str],
    **kwargs: Any,
) -> Tongue:
    """
    Convenience function for creating a COMMAND-level Tongue.

    Example:
        tongue = await reify_command(
            domain="Calendar Commands",
            constraints=["No deletes"],
            examples=["CHECK 2024-12-15", "ADD meeting"],
        )
    """
    return await reify(
        domain=domain,
        constraints=constraints,
        level=GrammarLevel.COMMAND,
        **kwargs,
    )


async def reify_recursive(
    domain: str,
    constraints: list[str],
    **kwargs: Any,
) -> Tongue:
    """
    Convenience function for creating a RECURSIVE-level Tongue.

    Example:
        tongue = await reify_recursive(
            domain="Query Language",
            constraints=["No mutations", "Pure functions only"],
        )
    """
    return await reify(
        domain=domain,
        constraints=constraints,
        level=GrammarLevel.RECURSIVE,
        **kwargs,
    )
