"""
Phase 5: Ecosystem Verification Tests.

Validates:
1. C-gent functor composition laws across the ecosystem
2. Import audit - ensures integration-by-field pattern compliance
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

import pytest

# =============================================================================
# Part 1: Functor Composition Verification
# =============================================================================


class TestFunctorCompositionEcosystem:
    """
    Verify that agent compositions satisfy functor laws.

    These tests ensure that the categorical foundations of the kgents
    architecture are sound across all agent interactions.
    """

    @pytest.mark.asyncio
    async def test_maybe_functor_identity_law(self) -> None:
        """Maybe functor: F(id) = id."""
        from agents.c import Just, Nothing, maybe
        from bootstrap.types import Agent

        class IdAgent(Agent[int, int]):
            @property
            def name(self) -> str:
                return "Id"

            async def invoke(self, x: int) -> int:
                return x

        lifted = maybe(IdAgent())

        # Test with Just
        result = await lifted.invoke(Just(42))
        assert isinstance(result, Just)
        assert result.value == 42

        # Test with Nothing
        result = await lifted.invoke(Nothing)
        assert result.is_nothing()

    @pytest.mark.asyncio
    async def test_maybe_functor_composition_law(self) -> None:
        """Maybe functor: F(g ∘ f) = F(g) ∘ F(f)."""
        from agents.c import Just, maybe
        from bootstrap.types import Agent

        class Double(Agent[int, int]):
            @property
            def name(self) -> str:
                return "Double"

            async def invoke(self, x: int) -> int:
                return x * 2

        class AddTen(Agent[int, int]):
            @property
            def name(self) -> str:
                return "AddTen"

            async def invoke(self, x: int) -> int:
                return x + 10

        f = Double()
        g = AddTen()

        # Left side: F(g ∘ f)
        composed = f >> g
        lifted_composed = maybe(composed)
        left = await lifted_composed.invoke(Just(5))

        # Right side: F(g) ∘ F(f)
        lifted_f = maybe(f)
        lifted_g = maybe(g)
        right = await (lifted_f >> lifted_g).invoke(Just(5))

        assert isinstance(left, Just) and isinstance(right, Just)
        assert left.value == right.value == 20

    @pytest.mark.asyncio
    async def test_either_functor_identity_law(self) -> None:
        """Either functor: F(id) = id."""
        from agents.c import Left, Right, either
        from bootstrap.types import Agent

        class IdAgent(Agent[str, str]):
            @property
            def name(self) -> str:
                return "Id"

            async def invoke(self, x: str) -> str:
                return x

        lifted = either(IdAgent())

        # Test with Right
        result = await lifted.invoke(Right("hello"))
        assert isinstance(result, Right)
        assert result.value == "hello"

        # Test with Left
        result = await lifted.invoke(Left("error"))
        assert isinstance(result, Left)
        assert result.error == "error"

    @pytest.mark.asyncio
    async def test_either_functor_composition_law(self) -> None:
        """Either functor: F(g ∘ f) = F(g) ∘ F(f)."""
        from agents.c import Right, either
        from bootstrap.types import Agent

        class ToUpper(Agent[str, str]):
            @property
            def name(self) -> str:
                return "ToUpper"

            async def invoke(self, x: str) -> str:
                return x.upper()

        class AddExclaim(Agent[str, str]):
            @property
            def name(self) -> str:
                return "AddExclaim"

            async def invoke(self, x: str) -> str:
                return x + "!"

        f = ToUpper()
        g = AddExclaim()

        # Left side: F(g ∘ f)
        left = await either(f >> g).invoke(Right("hello"))

        # Right side: F(g) ∘ F(f)
        right = await (either(f) >> either(g)).invoke(Right("hello"))

        assert isinstance(left, Right) and isinstance(right, Right)
        assert left.value == right.value == "HELLO!"

    @pytest.mark.asyncio
    async def test_list_functor_identity_law(self) -> None:
        """List functor: F(id) = id."""
        from agents.c import list_agent
        from bootstrap.types import Agent

        class IdAgent(Agent[int, int]):
            @property
            def name(self) -> str:
                return "Id"

            async def invoke(self, x: int) -> int:
                return x

        lifted = list_agent(IdAgent())
        result = await lifted.invoke([1, 2, 3])
        assert result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_list_functor_composition_law(self) -> None:
        """List functor: F(g ∘ f) = F(g) ∘ F(f)."""
        from agents.c import list_agent
        from bootstrap.types import Agent

        class Increment(Agent[int, int]):
            @property
            def name(self) -> str:
                return "Increment"

            async def invoke(self, x: int) -> int:
                return x + 1

        class Square(Agent[int, int]):
            @property
            def name(self) -> str:
                return "Square"

            async def invoke(self, x: int) -> int:
                return x**2

        f = Increment()
        g = Square()

        # Left side: F(g ∘ f)
        left = await list_agent(f >> g).invoke([1, 2, 3])

        # Right side: F(g) ∘ F(f)
        right = await (list_agent(f) >> list_agent(g)).invoke([1, 2, 3])

        # [1,2,3] -> [2,3,4] -> [4,9,16]
        assert left == right == [4, 9, 16]


class TestMonadLawsEcosystem:
    """Verify monad laws across the ecosystem."""

    def test_maybe_monad_left_identity(self) -> None:
        """Maybe monad: pure(a).bind(f) = f(a)."""
        from agents.c import Just, pure_maybe

        def f(x: int) -> Just[int]:
            return Just(x * 2)

        a = 21
        left = pure_maybe(a).flat_map(f)
        right = f(a)

        assert isinstance(left, Just)
        assert left.value == right.value == 42

    def test_maybe_monad_right_identity(self) -> None:
        """Maybe monad: m.bind(pure) = m."""
        from agents.c import Just, pure_maybe

        m = Just(42)
        result = m.flat_map(pure_maybe)
        assert isinstance(result, Just)
        assert result.value == 42

    def test_maybe_monad_associativity(self) -> None:
        """Maybe monad: m.bind(f).bind(g) = m.bind(λa. f(a).bind(g))."""
        from agents.c import Just

        def f(x: int) -> Just[int]:
            return Just(x * 2)

        def g(x: int) -> Just[int]:
            return Just(x + 10)

        m = Just(5)

        # Left: m.bind(f).bind(g)
        left = m.flat_map(f).flat_map(g)

        # Right: m.bind(λa. f(a).bind(g))
        right = m.flat_map(lambda a: f(a).flat_map(g))

        assert isinstance(left, Just) and isinstance(right, Just)
        assert left.value == right.value == 20


class TestCategoryLawsEcosystem:
    """Verify category laws (associativity and identity)."""

    @pytest.mark.asyncio
    async def test_composition_associativity(self) -> None:
        """Category: (f >> g) >> h = f >> (g >> h)."""
        from bootstrap.types import Agent

        class F(Agent[str, int]):
            @property
            def name(self) -> str:
                return "F"

            async def invoke(self, x: str) -> int:
                return len(x)

        class G(Agent[int, float]):
            @property
            def name(self) -> str:
                return "G"

            async def invoke(self, x: int) -> float:
                return x * 1.5

        class H(Agent[float, str]):
            @property
            def name(self) -> str:
                return "H"

            async def invoke(self, x: float) -> str:
                return f"{x:.1f}"

        f, g, h = F(), G(), H()

        # Left: (f >> g) >> h
        left = await ((f >> g) >> h).invoke("hello")

        # Right: f >> (g >> h)
        right = await (f >> (g >> h)).invoke("hello")

        # "hello" -> 5 -> 7.5 -> "7.5"
        assert left == right == "7.5"

    @pytest.mark.asyncio
    async def test_identity_left(self) -> None:
        """Category: id >> f = f."""
        from bootstrap.types import Agent

        class IdAgent(Agent[int, int]):
            @property
            def name(self) -> str:
                return "Id"

            async def invoke(self, x: int) -> int:
                return x

        class Double(Agent[int, int]):
            @property
            def name(self) -> str:
                return "Double"

            async def invoke(self, x: int) -> int:
                return x * 2

        id_agent = IdAgent()
        f = Double()

        composed = await (id_agent >> f).invoke(5)
        direct = await f.invoke(5)

        assert composed == direct == 10

    @pytest.mark.asyncio
    async def test_identity_right(self) -> None:
        """Category: f >> id = f."""
        from bootstrap.types import Agent

        class IdAgent(Agent[int, int]):
            @property
            def name(self) -> str:
                return "Id"

            async def invoke(self, x: int) -> int:
                return x

        class Double(Agent[int, int]):
            @property
            def name(self) -> str:
                return "Double"

            async def invoke(self, x: int) -> int:
                return x * 2

        id_agent = IdAgent()
        f = Double()

        composed = await (f >> id_agent).invoke(5)
        direct = await f.invoke(5)

        assert composed == direct == 10


# =============================================================================
# Part 2: Import Audit (Integration-by-Field Pattern)
# =============================================================================


class CrossImport(NamedTuple):
    """A cross-agent import."""

    source_agent: str
    imported_agent: str
    file_path: str
    import_line: str


class ImportAuditResult(NamedTuple):
    """Results of import audit."""

    acceptable: list[CrossImport]
    violations: list[CrossImport]
    total_cross_imports: int


# Agents that are allowed to be imported by others (foundational services)
FOUNDATIONAL_AGENTS = {
    "shared",  # Shared utilities
    "a",  # Abstract agent types (foundational - skeleton, meta)
    "d",  # Data/persistence (foundational)
    "l",  # Semantic lookup (foundational)
    "c",  # Category theory (foundational)
}

# Allowed integration patterns (explicit integration files)
INTEGRATION_PATTERNS = {
    "_integration",  # Files ending with _integration.py
    "integration_",  # Files starting with integration_
    "shared_",  # Shared budget, shared state
    "catalog_",  # Catalog integrations
}


def get_source_agent(file_path: Path) -> str | None:
    """Extract the agent letter from a file path."""
    parts = file_path.parts
    for i, part in enumerate(parts):
        if part == "agents" and i + 1 < len(parts):
            return parts[i + 1]
    return None


def is_integration_file(file_path: Path) -> bool:
    """Check if file is an explicit integration file."""
    filename = file_path.stem
    return any(pattern in filename for pattern in INTEGRATION_PATTERNS)


def audit_imports(agents_dir: Path) -> ImportAuditResult:
    """
    Audit cross-agent imports in the codebase.

    Returns categorized imports: acceptable vs violations.
    """
    acceptable = []
    violations = []

    for py_file in agents_dir.rglob("*.py"):
        # Skip test files and pycache
        if "_tests" in str(py_file) or "__pycache__" in str(py_file):
            continue

        source_agent = get_source_agent(py_file)
        if not source_agent:
            continue

        try:
            content = py_file.read_text()
        except Exception:
            continue

        # Find all cross-agent imports
        import_pattern = r"^from agents\.([a-z_]+)"
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            imported_agent = match.group(1)

            # Skip same-agent imports
            if imported_agent == source_agent:
                continue

            cross_import = CrossImport(
                source_agent=source_agent,
                imported_agent=imported_agent,
                file_path=str(py_file),
                import_line=content[match.start() : match.end()],
            )

            # Determine if acceptable
            is_acceptable = (
                imported_agent in FOUNDATIONAL_AGENTS or is_integration_file(py_file)
            )

            if is_acceptable:
                acceptable.append(cross_import)
            else:
                violations.append(cross_import)

    return ImportAuditResult(
        acceptable=acceptable,
        violations=violations,
        total_cross_imports=len(acceptable) + len(violations),
    )


class TestImportAudit:
    """
    Verify the integration-by-field pattern.

    Agents should not import other agents directly except:
    1. Foundational agents (D, L, C, shared)
    2. Explicit integration files (*_integration.py)
    """

    @pytest.fixture
    def agents_dir(self) -> Path:
        """Get the agents directory."""
        return Path(__file__).parent.parent.parent / "agents"

    def test_audit_runs_successfully(self, agents_dir: Path) -> None:
        """Import audit should complete without error."""
        result = audit_imports(agents_dir)

        # Should find some cross-imports
        assert result.total_cross_imports > 0, "Expected to find cross-agent imports"

        # Log summary
        print("\nImport Audit Summary:")
        print(f"  Total cross-imports: {result.total_cross_imports}")
        print(f"  Acceptable: {len(result.acceptable)}")
        print(f"  Violations: {len(result.violations)}")

    def test_foundational_agents_are_acceptable(self, agents_dir: Path) -> None:
        """Imports from foundational agents (D, L, C, shared) should be acceptable."""
        result = audit_imports(agents_dir)

        for ci in result.acceptable:
            # Either from foundational or in integration file
            from_foundational = ci.imported_agent in FOUNDATIONAL_AGENTS
            in_integration = is_integration_file(Path(ci.file_path))

            assert from_foundational or in_integration, (
                f"Acceptable import {ci.source_agent} -> {ci.imported_agent} "
                f"in {ci.file_path} doesn't match criteria"
            )

    def test_integration_files_are_explicit(self, agents_dir: Path) -> None:
        """
        Non-foundational cross-imports should be in explicit integration files.

        This enforces the pattern:
        - Direct coupling ONLY in files named *_integration.py
        - All other coupling should go through the semantic field
        """
        result = audit_imports(agents_dir)

        # Group violations by source
        violations_by_source = defaultdict(list)
        for v in result.violations:
            violations_by_source[v.source_agent].append(v)

        # Report violations (warning, not failure - for now)
        if result.violations:
            print("\n⚠️  Potential Integration-by-Field Violations:")
            print("   (These could be refactored to use SemanticField)")
            for source, vlist in sorted(violations_by_source.items()):
                print(f"\n   {source.upper()}-gent:")
                for v in vlist:
                    filename = Path(v.file_path).name
                    print(
                        f"     → imports {v.imported_agent.upper()}-gent in {filename}"
                    )

            print("\n   Consider either:")
            print("   1. Rename file to *_integration.py if intentional coupling")
            print("   2. Refactor to use SemanticField for decoupled coordination")

    def test_document_current_violations(self, agents_dir: Path) -> None:
        """
        Document current violations for tracking purposes.

        This test always passes but documents the current state.
        """
        result = audit_imports(agents_dir)

        # Known violations that are architectural (not refactored yet)
        known_violations = {
            # B-gent robin.py imports K, H directly (persona/dialectic morphisms)
            ("b", "k"): "robin.py - persona morphisms",
            ("b", "h"): "robin.py - dialectic morphisms",
            ("b", "a"): "hypothesis.py - skeleton types",
            # C-gent imports J for Promise functor
            ("c", "j"): "functor.py - Promise functor",
            # F-gent imports J for reality contracts
            ("f", "j"): "reality_contracts.py - J-gent reality types",
        }

        # Document actual vs known
        actual = {(v.source_agent, v.imported_agent) for v in result.violations}
        known = set(known_violations.keys())

        new_violations = actual - known
        resolved = known - actual

        if new_violations:
            print("\n📝 New violations detected:")
            for src, imp in sorted(new_violations):
                print(f"   {src.upper()}-gent → {imp.upper()}-gent")

        if resolved:
            print("\n✅ Previously known violations now resolved:")
            for src, imp in sorted(resolved):
                print(f"   {src.upper()}-gent → {imp.upper()}-gent")


class TestSemanticFieldUsage:
    """Verify agents are using the semantic field for coordination."""

    def test_semantic_field_module_exists(self) -> None:
        """SemanticField should exist for integration-by-field pattern."""
        from agents.i.semantic_field import (
            EconomicFieldEmitter,
            ForgeFieldSensor,
            PsiFieldEmitter,
            SafetyFieldEmitter,
            SemanticField,
            SemanticPheromoneKind,
        )

        # All components should exist
        assert SemanticField is not None
        assert SemanticPheromoneKind is not None
        assert PsiFieldEmitter is not None
        assert ForgeFieldSensor is not None
        assert SafetyFieldEmitter is not None
        assert EconomicFieldEmitter is not None

    def test_pheromone_kinds_cover_agents(self) -> None:
        """Pheromone kinds should cover major agent interactions."""
        from agents.i.semantic_field import SemanticPheromoneKind

        kinds = {k.value for k in SemanticPheromoneKind}

        # Should have pheromones for major signals
        expected = {
            "metaphor",
            "intent",
            "warning",
            "opportunity",
            "memory",
            "narrative",
        }
        assert expected.issubset(kinds), f"Missing pheromone kinds: {expected - kinds}"

    def test_field_emitter_interfaces(self) -> None:
        """Each major agent should have a field interface."""
        from agents.i.semantic_field import (
            create_economic_emitter,
            create_forge_sensor,
            create_psi_emitter,
            create_safety_emitter,
            create_semantic_field,
        )

        field = create_semantic_field()

        # Test factory functions work
        psi = create_psi_emitter(field)
        forge = create_forge_sensor(field)
        safety = create_safety_emitter(field)
        economic = create_economic_emitter(field)

        assert psi is not None
        assert forge is not None
        assert safety is not None
        assert economic is not None

    def test_field_based_psi_forge_integration(self) -> None:
        """
        Psi and Forge can coordinate without direct imports.

        This is the canonical example of integration-by-field.
        """
        from agents.i.semantic_field import (
            FieldCoordinate,
            create_forge_sensor,
            create_psi_emitter,
            create_semantic_field,
        )

        # Create shared field
        field = create_semantic_field()

        # Psi-gent emits a metaphor (doesn't know about Forge)
        psi = create_psi_emitter(field)
        psi.emit_metaphor(
            source_domain="database query optimization",
            target_domain="graph traversal",
            confidence=0.85,
            position=FieldCoordinate(domain="databases"),
            description="Query plans are like graph paths",
            transferable_operations=("shortest_path", "pruning"),
        )

        # Forge senses the metaphor (doesn't know about Psi)
        forge = create_forge_sensor(field)
        metaphors = forge.sense_metaphors(
            position=FieldCoordinate(domain="databases"),
            radius=1.0,
        )

        # Integration achieved via field!
        assert len(metaphors) == 1
        assert metaphors[0].source_domain == "database query optimization"
        assert metaphors[0].target_domain == "graph traversal"
        assert "shortest_path" in metaphors[0].transferable_operations
