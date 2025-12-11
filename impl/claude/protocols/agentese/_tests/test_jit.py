"""
Phase 4: JIT Compilation Tests

Tests for AGENTESE JIT compilation:
- SpecParser: Parse spec files
- SpecCompiler: Generate Python source
- JITCompiler: Full compilation pipeline
- JITPromoter: Promotion to permanent impl
- Logos integration: define_concept, promote_concept
"""

from __future__ import annotations

import ast
import textwrap
from dataclasses import dataclass
from pathlib import Path

import pytest

from .. import (
    AffordanceError,
    JITLogosNode,
    Logos,
    PathNotFoundError,
    PathSyntaxError,
    TastefulnessError,
    create_logos,
)
from ..jit import (
    JITCompiler,
    JITPromoter,
    SpecCompiler,
    SpecParser,
    compile_spec,
    create_jit_compiler,
)

# === Fixtures ===


@pytest.fixture
def sample_spec() -> str:
    """A minimal valid spec."""
    return textwrap.dedent("""
        ---
        entity: garden
        context: world
        version: 1.0
        ---

        # world.garden

        A space for growing things.

        ## Affordances

        ```yaml
        affordances:
          architect:
            - blueprint
            - measure
          poet:
            - describe
            - contemplate
          default:
            - inspect
        ```

        ## Manifest

        ```yaml
        manifest:
          architect:
            type: blueprint
            fields:
              - layout
              - dimensions
          poet:
            type: poetic
            fields:
              - description
              - mood
          default:
            type: basic
            fields:
              - summary
        ```
    """).strip()


@pytest.fixture
def library_spec(tmp_path: Path) -> Path:
    """Create the library spec file in a temp directory."""
    spec_dir = tmp_path / "spec" / "world"
    spec_dir.mkdir(parents=True)

    spec_content = textwrap.dedent("""
        ---
        entity: library
        context: world
        version: 1.0
        ---

        # world.library

        A collection of knowledge artifacts.

        ## Affordances

        ```yaml
        affordances:
          architect:
            - blueprint
            - measure
            - renovate
          developer:
            - query
            - index
            - deploy
          scientist:
            - analyze
            - experiment
          poet:
            - describe
            - inhabit
          default:
            - inspect
        ```

        ## Manifest

        ```yaml
        manifest:
          architect:
            type: blueprint
            fields:
              - sections
              - capacity
          poet:
            type: poetic
            fields:
              - description
              - atmosphere
          default:
            type: basic
            fields:
              - summary
              - item_count
        ```
    """).strip()

    spec_path = spec_dir / "library.md"
    spec_path.write_text(spec_content)
    return tmp_path / "spec"


@dataclass
class MockDNA:
    """Mock DNA for testing."""

    name: str = "test-agent"
    archetype: str = "default"
    capabilities: tuple[str, ...] = ()


@dataclass
class MockUmwelt:
    """Mock Umwelt for testing."""

    dna: MockDNA


# === SpecParser Tests ===


class TestSpecParser:
    """Tests for SpecParser."""

    def test_parse_basic_spec(self, sample_spec: str) -> None:
        """Parse a basic spec file."""
        parser = SpecParser()
        parsed = parser.parse(sample_spec)

        assert parsed.entity == "garden"
        assert parsed.context == "world"
        assert str(parsed.version) == "1.0"  # YAML may parse as float
        assert "A space for growing things" in parsed.description

    def test_parse_affordances(self, sample_spec: str) -> None:
        """Extract affordances from spec."""
        parser = SpecParser()
        parsed = parser.parse(sample_spec)

        assert "architect" in parsed.affordances
        assert "blueprint" in parsed.affordances["architect"]
        assert "measure" in parsed.affordances["architect"]

        assert "poet" in parsed.affordances
        assert "describe" in parsed.affordances["poet"]

        assert "default" in parsed.affordances
        assert "inspect" in parsed.affordances["default"]

    def test_parse_manifest(self, sample_spec: str) -> None:
        """Extract manifest configuration from spec."""
        parser = SpecParser()
        parsed = parser.parse(sample_spec)

        assert "architect" in parsed.manifest
        assert parsed.manifest["architect"]["type"] == "blueprint"

        assert "poet" in parsed.manifest
        assert parsed.manifest["poet"]["type"] == "poetic"

    def test_parse_missing_front_matter_raises(self) -> None:
        """Spec without front matter raises TastefulnessError."""
        parser = SpecParser()
        bad_spec = "# Just Markdown\n\nNo front matter here."

        with pytest.raises(TastefulnessError) as exc_info:
            parser.parse(bad_spec)

        assert "front matter" in str(exc_info.value).lower()

    def test_parse_missing_entity_raises(self) -> None:
        """Spec without entity field raises TastefulnessError."""
        parser = SpecParser()
        bad_spec = textwrap.dedent("""
            ---
            context: world
            version: 1.0
            ---

            # Missing entity
        """).strip()

        with pytest.raises(TastefulnessError) as exc_info:
            parser.parse(bad_spec)

        assert "entity" in str(exc_info.value).lower()

    def test_parse_invalid_yaml_front_matter(self) -> None:
        """Invalid YAML in front matter raises TastefulnessError."""
        parser = SpecParser()
        bad_spec = textwrap.dedent("""
            ---
            entity: test
            bad_yaml: [unclosed
            ---

            # Content
        """).strip()

        with pytest.raises(TastefulnessError) as exc_info:
            parser.parse(bad_spec)

        assert "yaml" in str(exc_info.value).lower()


# === SpecCompiler Tests ===


class TestSpecCompiler:
    """Tests for SpecCompiler."""

    def test_compile_generates_valid_python(self, sample_spec: str) -> None:
        """Compiled source is valid Python."""
        parser = SpecParser()
        compiler = SpecCompiler()

        parsed = parser.parse(sample_spec)
        source = compiler.compile(parsed)

        # Should parse without syntax errors
        ast.parse(source)

    def test_compile_generates_class(self, sample_spec: str) -> None:
        """Compiled source contains a JIT class."""
        parser = SpecParser()
        compiler = SpecCompiler()

        parsed = parser.parse(sample_spec)
        source = compiler.compile(parsed)

        assert "class JIT" in source
        assert "GardenNode" in source or "gardenNode" in source.lower()

    def test_compile_includes_handle(self, sample_spec: str) -> None:
        """Compiled source includes correct handle."""
        parser = SpecParser()
        compiler = SpecCompiler()

        parsed = parser.parse(sample_spec)
        source = compiler.compile(parsed)

        assert "world.garden" in source

    def test_compile_includes_affordances(self, sample_spec: str) -> None:
        """Compiled source includes affordance mapping."""
        parser = SpecParser()
        compiler = SpecCompiler()

        parsed = parser.parse(sample_spec)
        source = compiler.compile(parsed)

        assert "AFFORDANCES" in source
        assert '"architect"' in source
        assert '"blueprint"' in source

    def test_compile_includes_manifest_method(self, sample_spec: str) -> None:
        """Compiled source includes manifest method."""
        parser = SpecParser()
        compiler = SpecCompiler()

        parsed = parser.parse(sample_spec)
        source = compiler.compile(parsed)

        assert "async def manifest" in source


# === JITCompiler Tests ===


class TestJITCompiler:
    """Tests for JITCompiler."""

    def test_compile_from_content(self, sample_spec: str) -> None:
        """Compile from spec content string."""
        compiler = JITCompiler()
        jit_node = compiler.compile_from_content(sample_spec)

        assert isinstance(jit_node, JITLogosNode)
        assert jit_node.handle == "world.garden"
        assert jit_node.source  # Non-empty source
        assert jit_node.spec == sample_spec

    def test_compile_from_path(self, library_spec: Path) -> None:
        """Compile from spec file path."""
        compiler = JITCompiler(spec_root=library_spec)
        spec_path = library_spec / "world" / "library.md"

        jit_node = compiler.compile_from_path(spec_path)

        assert isinstance(jit_node, JITLogosNode)
        assert jit_node.handle == "world.library"

    def test_compile_nonexistent_path_raises(self, tmp_path: Path) -> None:
        """Compile from nonexistent path raises PathNotFoundError."""
        compiler = JITCompiler(spec_root=tmp_path)
        bad_path = tmp_path / "nonexistent.md"

        with pytest.raises(PathNotFoundError):
            compiler.compile_from_path(bad_path)

    def test_compile_and_instantiate(self, library_spec: Path) -> None:
        """Compile and instantiate a LogosNode."""
        compiler = JITCompiler(spec_root=library_spec)
        spec_path = library_spec / "world" / "library.md"

        node = compiler.compile_and_instantiate(spec_path)

        assert node.handle == "world.library"
        # Should be able to call affordances
        from ..node import AgentMeta

        meta = AgentMeta(name="test", archetype="architect")
        affordances = node.affordances(meta)
        assert "manifest" in affordances


# === JITPromoter Tests ===


class TestJITPromoter:
    """Tests for JITPromoter."""

    def test_should_promote_below_threshold(self, sample_spec: str) -> None:
        """Node below threshold should not promote."""
        compiler = JITCompiler()
        jit_node = compiler.compile_from_content(sample_spec)

        promoter = JITPromoter(threshold=100)
        assert not promoter.should_promote(jit_node)

    def test_should_promote_meets_threshold(self, sample_spec: str) -> None:
        """Node meeting threshold should promote."""
        compiler = JITCompiler()
        jit_node = compiler.compile_from_content(sample_spec)

        # Simulate usage
        jit_node.usage_count = 150
        jit_node.success_count = 140

        promoter = JITPromoter(threshold=100, success_threshold=0.8)
        assert promoter.should_promote(jit_node)

    def test_should_promote_low_success_rate(self, sample_spec: str) -> None:
        """Node with low success rate should not promote."""
        compiler = JITCompiler()
        jit_node = compiler.compile_from_content(sample_spec)

        # Simulate usage with low success
        jit_node.usage_count = 150
        jit_node.success_count = 50  # 33% success rate

        promoter = JITPromoter(threshold=100, success_threshold=0.8)
        assert not promoter.should_promote(jit_node)

    def test_promote_success(self, tmp_path: Path, sample_spec: str) -> None:
        """Successful promotion writes impl file."""
        compiler = JITCompiler()
        jit_node = compiler.compile_from_content(sample_spec)

        # Meet criteria
        jit_node.usage_count = 150
        jit_node.success_count = 140

        impl_root = tmp_path / "impl" / "generated"
        promoter = JITPromoter(
            impl_root=impl_root,
            threshold=100,
            success_threshold=0.8,
        )

        result = promoter.promote(jit_node)

        assert result.success
        assert result.impl_path is not None
        assert result.impl_path.exists()
        assert "garden.py" in str(result.impl_path)

    def test_promote_failure_not_ready(self, sample_spec: str) -> None:
        """Promotion fails if criteria not met."""
        compiler = JITCompiler()
        jit_node = compiler.compile_from_content(sample_spec)

        promoter = JITPromoter(threshold=100)
        result = promoter.promote(jit_node)

        assert not result.success
        assert "not ready" in result.reason.lower()


# === Logos Integration Tests ===


class TestLogosJITIntegration:
    """Tests for Logos JIT integration."""

    def test_resolve_from_spec(self, library_spec: Path) -> None:
        """Logos resolves path from spec file."""
        logos = create_logos(spec_root=library_spec)

        node = logos.resolve("world.library")

        assert node is not None
        assert node.handle == "world.library"

    def test_jit_node_cached(self, library_spec: Path) -> None:
        """JIT nodes are cached after first resolution."""
        logos = create_logos(spec_root=library_spec)

        node1 = logos.resolve("world.library")
        node2 = logos.resolve("world.library")

        assert node1 is node2

    def test_jit_node_tracked_via_define(
        self, tmp_path: Path, sample_spec: str
    ) -> None:
        """JIT nodes created via define_concept are tracked for promotion."""
        logos = create_logos(spec_root=tmp_path)

        # Use an architect to define a new concept
        architect = MockUmwelt(dna=MockDNA(name="architect", archetype="architect"))
        import asyncio

        asyncio.get_event_loop().run_until_complete(
            logos.define_concept("world.garden", sample_spec, architect)
        )

        assert "world.garden" in logos._jit_nodes

    def test_get_jit_status_via_define(self, tmp_path: Path, sample_spec: str) -> None:
        """Get JIT node status for defined concept."""
        logos = create_logos(spec_root=tmp_path)

        # Use an architect to define a new concept
        architect = MockUmwelt(dna=MockDNA(name="architect", archetype="architect"))
        import asyncio

        asyncio.get_event_loop().run_until_complete(
            logos.define_concept("world.garden", sample_spec, architect)
        )

        status = logos.get_jit_status("world.garden")

        assert status is not None
        assert status["handle"] == "world.garden"
        assert status["usage_count"] >= 0

    def test_list_jit_nodes_via_define(self, tmp_path: Path, sample_spec: str) -> None:
        """List all JIT nodes after defining concepts."""
        logos = create_logos(spec_root=tmp_path)

        # Use an architect to define a new concept
        architect = MockUmwelt(dna=MockDNA(name="architect", archetype="architect"))
        import asyncio

        asyncio.get_event_loop().run_until_complete(
            logos.define_concept("world.garden", sample_spec, architect)
        )

        nodes = logos.list_jit_nodes()

        assert len(nodes) >= 1
        handles = [n["handle"] for n in nodes]
        assert "world.garden" in handles


class TestDefineConceptAutopoiesis:
    """Tests for define_concept() autopoiesis."""

    @pytest.fixture
    def architect_umwelt(self) -> MockUmwelt:
        """Create an architect observer."""
        return MockUmwelt(dna=MockDNA(name="architect", archetype="architect"))

    @pytest.fixture
    def poet_umwelt(self) -> MockUmwelt:
        """Create a poet observer (cannot define)."""
        return MockUmwelt(dna=MockDNA(name="poet", archetype="poet"))

    @pytest.fixture
    def simple_spec(self) -> str:
        """A simple spec for defining a new entity."""
        return textwrap.dedent("""
            ---
            entity: fountain
            context: world
            version: 1.0
            ---

            # world.fountain

            A water feature in a garden.

            ## Affordances

            ```yaml
            affordances:
              architect:
                - blueprint
                - measure
              poet:
                - describe
              default:
                - inspect
            ```

            ## Manifest

            ```yaml
            manifest:
              default:
                type: basic
                fields:
                  - summary
            ```
        """).strip()

    @pytest.mark.asyncio
    async def test_define_concept_success(
        self,
        tmp_path: Path,
        architect_umwelt: MockUmwelt,
        simple_spec: str,
    ) -> None:
        """Architect can define new concepts."""
        logos = create_logos(spec_root=tmp_path)

        node = await logos.define_concept(
            handle="world.fountain",
            spec=simple_spec,
            observer=architect_umwelt,
        )

        assert node is not None
        assert node.handle == "world.fountain"
        assert "world.fountain" in logos._jit_nodes

    @pytest.mark.asyncio
    async def test_define_concept_unauthorized(
        self,
        tmp_path: Path,
        poet_umwelt: MockUmwelt,
        simple_spec: str,
    ) -> None:
        """Poet cannot define new concepts."""
        logos = create_logos(spec_root=tmp_path)

        with pytest.raises(AffordanceError) as exc_info:
            await logos.define_concept(
                handle="world.fountain",
                spec=simple_spec,
                observer=poet_umwelt,
            )

        assert "cannot define" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_define_concept_invalid_handle(
        self,
        tmp_path: Path,
        architect_umwelt: MockUmwelt,
        simple_spec: str,
    ) -> None:
        """Invalid handle raises PathSyntaxError."""
        logos = create_logos(spec_root=tmp_path)

        with pytest.raises(PathSyntaxError):
            await logos.define_concept(
                handle="invalid",  # Missing context
                spec=simple_spec,
                observer=architect_umwelt,
            )

    @pytest.mark.asyncio
    async def test_define_concept_invalid_context(
        self,
        tmp_path: Path,
        architect_umwelt: MockUmwelt,
        simple_spec: str,
    ) -> None:
        """Invalid context raises PathSyntaxError."""
        logos = create_logos(spec_root=tmp_path)

        with pytest.raises(PathSyntaxError):
            await logos.define_concept(
                handle="invalid_context.fountain",
                spec=simple_spec,
                observer=architect_umwelt,
            )

    @pytest.mark.asyncio
    async def test_defined_concept_is_resolvable(
        self,
        tmp_path: Path,
        architect_umwelt: MockUmwelt,
        simple_spec: str,
    ) -> None:
        """Defined concept can be resolved."""
        logos = create_logos(spec_root=tmp_path)

        await logos.define_concept(
            handle="world.fountain",
            spec=simple_spec,
            observer=architect_umwelt,
        )

        # Should now be resolvable
        node = logos.resolve("world.fountain")
        assert node is not None


class TestPromoteConcept:
    """Tests for promote_concept()."""

    @pytest.fixture
    def ready_logos(self, tmp_path: Path, sample_spec: str) -> Logos:
        """Create Logos with a JIT node ready for promotion."""
        logos = create_logos(spec_root=tmp_path)

        # Define a concept to get a JIT node
        architect = MockUmwelt(dna=MockDNA(name="architect", archetype="architect"))
        import asyncio

        asyncio.get_event_loop().run_until_complete(
            logos.define_concept("world.garden", sample_spec, architect)
        )

        # Simulate usage to meet promotion criteria
        jit_node = logos._jit_nodes["world.garden"]
        jit_node.usage_count = 150
        jit_node.success_count = 140

        return logos

    @pytest.mark.asyncio
    async def test_promote_concept_success(
        self,
        ready_logos: Logos,
    ) -> None:
        """Successfully promote a JIT concept."""
        result = await ready_logos.promote_concept(
            handle="world.garden",
            threshold=100,
            success_threshold=0.8,
        )

        assert result.success
        assert "world.garden" not in ready_logos._jit_nodes

    @pytest.mark.asyncio
    async def test_promote_concept_not_jit(self, tmp_path: Path) -> None:
        """Promoting non-JIT handle fails."""
        logos = create_logos(spec_root=tmp_path)

        result = await logos.promote_concept("world.nonexistent")

        assert not result.success
        assert "not a JIT node" in result.reason

    @pytest.mark.asyncio
    async def test_promote_concept_not_ready(
        self,
        tmp_path: Path,
        sample_spec: str,
    ) -> None:
        """Promoting node that doesn't meet criteria fails."""
        logos = create_logos(spec_root=tmp_path)

        # Define a concept to get a JIT node
        architect = MockUmwelt(dna=MockDNA(name="architect", archetype="architect"))
        await logos.define_concept("world.garden", sample_spec, architect)

        # Don't simulate usage - node not ready

        result = await logos.promote_concept(
            handle="world.garden",
            threshold=100,
        )

        assert not result.success
        assert "not ready" in result.reason.lower()


# === Factory Function Tests ===


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_jit_compiler(self, tmp_path: Path) -> None:
        """Create JIT compiler with custom spec root."""
        compiler = create_jit_compiler(spec_root=tmp_path)

        assert compiler.spec_root == tmp_path

    def test_compile_spec_function(self, library_spec: Path) -> None:
        """Compile spec using convenience function."""
        spec_path = library_spec / "world" / "library.md"

        jit_node = compile_spec(spec_path)

        assert isinstance(jit_node, JITLogosNode)
        assert jit_node.handle == "world.library"


# === Edge Cases ===


class TestJITEdgeCases:
    """Edge case tests for JIT compilation."""

    def test_empty_affordances(self) -> None:
        """Spec with no affordances works."""
        parser = SpecParser()
        compiler = SpecCompiler()

        spec = textwrap.dedent("""
            ---
            entity: empty
            context: world
            version: 1.0
            ---

            # world.empty

            An entity with no extra affordances.
        """).strip()

        parsed = parser.parse(spec)
        source = compiler.compile(parsed)

        # Should still compile
        ast.parse(source)

    def test_special_characters_in_entity_name(self) -> None:
        """Entity names with underscores work."""
        parser = SpecParser()
        compiler = SpecCompiler()

        spec = textwrap.dedent("""
            ---
            entity: my_special_entity
            context: world
            version: 1.0
            ---

            # world.my_special_entity

            An entity with underscores.

            ## Affordances

            ```yaml
            affordances:
              default:
                - inspect
            ```
        """).strip()

        parsed = parser.parse(spec)
        source = compiler.compile(parsed)

        ast.parse(source)
        assert "my_special_entity" in source.lower()

    def test_long_description_truncated(self) -> None:
        """Long descriptions are truncated in generated code."""
        parser = SpecParser()
        compiler = SpecCompiler()

        long_desc = "A" * 500
        spec = textwrap.dedent(f"""
            ---
            entity: verbose
            context: world
            version: 1.0
            ---

            # world.verbose

            {long_desc}

            ## Affordances

            ```yaml
            affordances:
              default:
                - inspect
            ```
        """).strip()

        parsed = parser.parse(spec)
        source = compiler.compile(parsed)

        # Description should be truncated with ellipsis
        assert "..." in source

    def test_multiple_yaml_blocks(self) -> None:
        """Parse spec with multiple YAML blocks."""
        parser = SpecParser()

        spec = textwrap.dedent("""
            ---
            entity: multi
            context: world
            version: 1.0
            ---

            # world.multi

            Multiple YAML blocks.

            ## Affordances

            ```yaml
            affordances:
              architect:
                - blueprint
            ```

            ## State

            ```yaml
            state:
              created_at: datetime
              name: str
            ```

            ## Relations

            ```yaml
            relations:
              contains:
                - world.item
            ```
        """).strip()

        parsed = parser.parse(spec)

        assert "architect" in parsed.affordances
        assert "created_at" in parsed.state_schema
        assert "contains" in parsed.relations
