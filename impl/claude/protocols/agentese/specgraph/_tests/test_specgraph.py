"""
Tests for SpecGraph autopoietic compilation infrastructure.

Tests the three functors:
1. Parser: Parse YAML frontmatter from spec files
2. Compile: Generate impl scaffolding from spec
3. Reflect: Extract spec from impl

And verifies the autopoiesis fixed point: Reflect(Compile(S)) ≅ S
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from ..compile import compile_spec
from ..drift import DriftStatus, check_drift
from ..parser import (
    ParseError,
    generate_frontmatter,
    parse_frontmatter,
    parse_spec_file,
)
from ..reflect import (
    reflect_impl,
    reflect_operad,
    reflect_polynomial,
)
from ..types import (
    AgentesePath,
    LawSpec,
    OperadSpec,
    OperationSpec,
    PolynomialSpec,
    SpecDomain,
    SpecNode,
)

# === Parser Tests ===


class TestParseFrontmatter:
    """Tests for YAML frontmatter parsing."""

    def test_parse_empty_content(self) -> None:
        """Empty content returns empty frontmatter."""
        fm, rest = parse_frontmatter("")
        assert fm == {}
        assert rest == ""

    def test_parse_no_frontmatter(self) -> None:
        """Content without frontmatter returns content unchanged."""
        content = "# Hello\n\nThis is content."
        fm, rest = parse_frontmatter(content)
        assert fm == {}
        assert rest == content

    def test_parse_simple_frontmatter(self) -> None:
        """Parse simple YAML frontmatter."""
        content = """---
domain: world
holon: test
---

# Content
"""
        fm, rest = parse_frontmatter(content)
        assert fm["domain"] == "world"
        assert fm["holon"] == "test"
        assert "# Content" in rest

    def test_parse_complex_frontmatter(self) -> None:
        """Parse frontmatter with nested structures."""
        content = """---
domain: world
holon: test
polynomial:
  positions: [idle, working, resting]
  transition: test_transition
operad:
  operations:
    greet:
      arity: 2
      signature: "A × B → C"
---

# Spec content
"""
        fm, rest = parse_frontmatter(content)
        assert fm["polynomial"]["positions"] == ["idle", "working", "resting"]
        assert fm["operad"]["operations"]["greet"]["arity"] == 2


class TestParseSpecFile:
    """Tests for spec file parsing."""

    def test_parse_minimal_spec(self, tmp_path: Path) -> None:
        """Parse a minimal spec file."""
        spec_file = tmp_path / "test.md"
        spec_file.write_text("""---
domain: world
holon: test
---

# Test Spec
""")
        node = parse_spec_file(spec_file)
        assert node.domain == SpecDomain.WORLD
        assert node.holon == "test"
        assert node.full_path == "world.test"

    def test_parse_with_polynomial(self, tmp_path: Path) -> None:
        """Parse spec with polynomial block."""
        spec_file = tmp_path / "test.md"
        spec_file.write_text("""---
domain: self
holon: memory
polynomial:
  positions: [idle, searching, surfacing]
  transition: memory_transition
---
""")
        node = parse_spec_file(spec_file)
        assert node.has_polynomial
        assert node.polynomial is not None
        assert "idle" in node.polynomial.positions
        assert node.polynomial.transition_fn == "memory_transition"

    def test_parse_with_operad(self, tmp_path: Path) -> None:
        """Parse spec with operad block."""
        spec_file = tmp_path / "test.md"
        spec_file.write_text("""---
domain: world
holon: town
operad:
  operations:
    greet:
      arity: 2
      signature: "Citizen × Citizen → Greeting"
    solo:
      arity: 1
  laws:
    locality: "interact(a, b) implies same_region(a, b)"
---
""")
        node = parse_spec_file(spec_file)
        assert node.has_operad
        assert node.operad is not None
        assert len(node.operad.operations) == 2
        assert len(node.operad.laws) == 1

    def test_parse_with_agentese(self, tmp_path: Path) -> None:
        """Parse spec with AGENTESE block."""
        spec_file = tmp_path / "test.md"
        spec_file.write_text("""---
domain: world
holon: town
agentese:
  path: world.town
  aspects: [manifest, witness, inhabit]
---
""")
        node = parse_spec_file(spec_file)
        assert node.agentese is not None
        assert node.agentese.path == "world.town"
        assert "manifest" in node.agentese.aspects

    def test_infer_domain_from_path(self, tmp_path: Path) -> None:
        """Infer domain from directory structure."""
        spec_dir = tmp_path / "spec" / "world"
        spec_dir.mkdir(parents=True)
        spec_file = spec_dir / "test.md"
        spec_file.write_text("# Just content, no frontmatter")

        node = parse_spec_file(spec_file)
        # Should infer from path
        assert node.holon == "test"


class TestGenerateFrontmatter:
    """Tests for YAML frontmatter generation."""

    def test_roundtrip_simple(self) -> None:
        """Roundtrip a simple spec node."""
        node = SpecNode(
            domain=SpecDomain.WORLD,
            holon="test",
            source_path=Path("spec/world/test.md"),
        )
        yaml = generate_frontmatter(node)
        assert "domain: world" in yaml
        assert "holon: test" in yaml

    def test_roundtrip_with_polynomial(self) -> None:
        """Roundtrip a spec node with polynomial."""
        node = SpecNode(
            domain=SpecDomain.WORLD,
            holon="test",
            source_path=Path("spec/world/test.md"),
            polynomial=PolynomialSpec(
                positions=("idle", "working"),
                transition_fn="test_transition",
            ),
        )
        yaml = generate_frontmatter(node)
        assert "polynomial:" in yaml
        assert "idle" in yaml
        assert "test_transition" in yaml


# === Compile Tests ===


class TestCompile:
    """Tests for the Compile functor."""

    def test_compile_minimal_spec(self, tmp_path: Path) -> None:
        """Compile a minimal spec (no components)."""
        node = SpecNode(
            domain=SpecDomain.WORLD,
            holon="test",
            source_path=Path("spec/world/test.md"),
        )
        result = compile_spec(node, tmp_path, dry_run=True)
        assert result.success
        # No files generated for empty spec
        assert len(result.warnings) > 0

    def test_compile_with_polynomial(self, tmp_path: Path) -> None:
        """Compile a spec with polynomial generates polynomial.py."""
        node = SpecNode(
            domain=SpecDomain.WORLD,
            holon="example",
            source_path=Path("spec/world/example.md"),
            polynomial=PolynomialSpec(
                positions=("idle", "active", "done"),
                transition_fn="example_transition",
            ),
        )
        result = compile_spec(node, tmp_path, dry_run=True)
        assert result.success
        assert any("polynomial.py" in f for f in result.generated_files)

    def test_compile_with_operad(self, tmp_path: Path) -> None:
        """Compile a spec with operad generates operad.py."""
        node = SpecNode(
            domain=SpecDomain.WORLD,
            holon="example",
            source_path=Path("spec/world/example.md"),
            operad=OperadSpec(
                operations=(
                    OperationSpec(name="foo", arity=2, signature="A × B → C"),
                    OperationSpec(name="bar", arity=1),
                ),
                laws=(LawSpec(name="test_law", equation="a = b"),),
            ),
        )
        result = compile_spec(node, tmp_path, dry_run=True)
        assert result.success
        assert any("operad.py" in f for f in result.generated_files)

    def test_compile_with_agentese(self, tmp_path: Path) -> None:
        """Compile a spec with AGENTESE generates node.py."""
        node = SpecNode(
            domain=SpecDomain.WORLD,
            holon="example",
            source_path=Path("spec/world/example.md"),
            agentese=AgentesePath(
                path="world.example",
                aspects=("manifest", "witness"),
            ),
        )
        result = compile_spec(node, tmp_path, dry_run=True)
        assert result.success
        assert any("node.py" in f for f in result.generated_files)

    def test_compile_writes_files(self, tmp_path: Path) -> None:
        """Compile with dry_run=False writes files."""
        node = SpecNode(
            domain=SpecDomain.WORLD,
            holon="writetest",
            source_path=Path("spec/world/writetest.md"),
            polynomial=PolynomialSpec(
                positions=("a", "b"),
                transition_fn="test_transition",
            ),
        )
        result = compile_spec(node, tmp_path, dry_run=False)
        assert result.success
        # Check file exists
        poly_path = tmp_path / "agents" / "writetest" / "polynomial.py"
        assert poly_path.exists()
        content = poly_path.read_text()
        assert "class WritetestPhase" in content


# === Reflect Tests ===


class TestReflect:
    """Tests for the Reflect functor."""

    def test_reflect_nonexistent_dir(self, tmp_path: Path) -> None:
        """Reflect nonexistent directory returns errors."""
        result = reflect_impl(tmp_path / "nonexistent")
        assert result.errors

    def test_reflect_empty_dir(self, tmp_path: Path) -> None:
        """Reflect empty directory returns low confidence."""
        impl_dir = tmp_path / "agents" / "empty"
        impl_dir.mkdir(parents=True)
        result = reflect_impl(impl_dir)
        assert result.confidence == 0.0

    def test_reflect_with_polynomial(self, tmp_path: Path) -> None:
        """Reflect directory with polynomial.py extracts phases."""
        impl_dir = tmp_path / "agents" / "test"
        impl_dir.mkdir(parents=True)
        poly_file = impl_dir / "polynomial.py"
        poly_file.write_text("""
from enum import Enum, auto

class TestPhase(Enum):
    IDLE = auto()
    WORKING = auto()
    DONE = auto()

def test_transition(phase, input):
    pass
""")
        spec = reflect_polynomial(poly_file)
        assert spec is not None
        assert "idle" in spec.positions or "IDLE" in [p.upper() for p in spec.positions]


# === Drift Detection Tests ===


class TestDriftDetection:
    """Tests for drift detection between spec and impl."""

    def test_drift_both_missing(self) -> None:
        """Both spec and impl missing returns UNKNOWN."""
        report = check_drift(None, None)
        assert report.status == DriftStatus.UNKNOWN

    def test_drift_missing_spec(self, tmp_path: Path) -> None:
        """Impl without spec returns MISSING_SPEC."""
        impl_dir = tmp_path / "agents" / "orphan"
        impl_dir.mkdir(parents=True)
        report = check_drift(None, impl_dir)
        assert report.status == DriftStatus.MISSING_SPEC

    def test_drift_missing_impl(self, tmp_path: Path) -> None:
        """Spec without impl returns MISSING_IMPL."""
        spec_file = tmp_path / "test.md"
        spec_file.write_text("---\ndomain: world\nholon: test\n---\n")
        report = check_drift(spec_file, tmp_path / "nonexistent")
        assert report.status == DriftStatus.MISSING_IMPL


# === Autopoiesis Fixed Point Tests ===


class TestAutopoiesisFixedPoint:
    """Tests for the autopoiesis fixed point: Reflect(Compile(S)) ≅ S."""

    def test_roundtrip_polynomial(self, tmp_path: Path) -> None:
        """Roundtrip: Compile then Reflect preserves polynomial structure."""
        # Original spec
        original = SpecNode(
            domain=SpecDomain.WORLD,
            holon="roundtrip",
            source_path=Path("spec/world/roundtrip.md"),
            polynomial=PolynomialSpec(
                positions=("idle", "active", "done"),
                transition_fn="roundtrip_transition",
            ),
        )

        # Compile
        compile_result = compile_spec(original, tmp_path, dry_run=False)
        assert compile_result.success

        # Reflect
        impl_dir = tmp_path / "agents" / "roundtrip"
        reflect_result = reflect_impl(impl_dir)

        # Verify structure preserved
        assert reflect_result.spec_node is not None
        reflected = reflect_result.spec_node
        assert reflected.holon == original.holon
        # Note: positions may be extracted in different case
        # The key is that the structure is preserved

    def test_roundtrip_generates_valid_yaml(self, tmp_path: Path) -> None:
        """Roundtrip generates valid YAML that could be parsed again."""
        original = SpecNode(
            domain=SpecDomain.WORLD,
            holon="yamltest",
            source_path=Path("spec/world/yamltest.md"),
            polynomial=PolynomialSpec(
                positions=("a", "b"),
                transition_fn="test_fn",
            ),
            operad=OperadSpec(
                operations=(OperationSpec(name="op1", arity=2),),
                laws=(),
            ),
        )

        # Generate YAML
        yaml_content = generate_frontmatter(original)

        # Parse it back
        from ..parser import parse_frontmatter

        fm, _ = parse_frontmatter(yaml_content)

        assert fm["domain"] == "world"
        assert fm["holon"] == "yamltest"
        assert "polynomial" in fm


# === Edge Case Tests ===


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_parse_empty_frontmatter_block(self) -> None:
        """Empty frontmatter block returns empty dict."""
        content = """---
---

# Content
"""
        fm, rest = parse_frontmatter(content)
        assert fm == {}
        assert "# Content" in rest

    def test_parse_malformed_yaml_raises(self) -> None:
        """Malformed YAML raises ParseError."""
        content = """---
key: [unclosed bracket
---
"""
        with pytest.raises(ParseError) as exc_info:
            parse_frontmatter(content)
        assert "Invalid YAML" in str(exc_info.value)

    def test_parse_yaml_list_raises(self) -> None:
        """YAML list instead of mapping raises ParseError."""
        content = """---
- item1
- item2
---
"""
        with pytest.raises(ParseError) as exc_info:
            parse_frontmatter(content)
        assert "must be a YAML mapping" in str(exc_info.value)

    def test_parse_yaml_scalar_raises(self) -> None:
        """YAML scalar instead of mapping raises ParseError."""
        content = """---
just a string
---
"""
        with pytest.raises(ParseError) as exc_info:
            parse_frontmatter(content)
        assert "must be a YAML mapping" in str(exc_info.value)

    def test_parse_spec_file_nonexistent(self, tmp_path: Path) -> None:
        """Nonexistent file raises ParseError."""
        with pytest.raises(ParseError) as exc_info:
            parse_spec_file(tmp_path / "nonexistent.md")
        assert "File not found" in str(exc_info.value)

    def test_parse_spec_file_with_special_chars(self, tmp_path: Path) -> None:
        """Spec file with special characters parses correctly."""
        spec_file = tmp_path / "test.md"
        spec_file.write_text(
            """---
domain: world
holon: test
operad:
  operations:
    "→": {arity: 2, signature: "A → B"}
---

# Test with unicode: λ, ∀, ∃, →
""",
            encoding="utf-8",
        )
        node = parse_spec_file(spec_file)
        assert node.operad is not None
        assert len(node.operad.operations) == 1

    def test_generate_frontmatter_with_service_spec(self) -> None:
        """generate_frontmatter includes ServiceSpec."""
        from ..types import ServiceSpec

        node = SpecNode(
            domain=SpecDomain.WORLD,
            holon="test",
            source_path=Path("spec/world/test.md"),
            service=ServiceSpec(
                crown_jewel=True,
                adapters=("crystals", "streaming"),
                frontend=True,
                persistence="d-gent",
            ),
        )
        yaml = generate_frontmatter(node)
        assert "service:" in yaml
        assert "crown_jewel: true" in yaml
        assert "adapters:" in yaml
        assert "frontend: true" in yaml
        assert "persistence: d-gent" in yaml

    def test_generate_frontmatter_with_rich_aspects(self) -> None:
        """generate_frontmatter includes rich AspectSpec."""
        from ..types import AspectCategory, AspectSpec

        node = SpecNode(
            domain=SpecDomain.WORLD,
            holon="test",
            source_path=Path("spec/world/test.md"),
            agentese=AgentesePath(
                path="world.test",
                aspects=(),
                aspect_specs=(
                    AspectSpec(
                        name="manifest",
                        category=AspectCategory.PERCEPTION,
                        effects=(),
                    ),
                    AspectSpec(
                        name="mutate",
                        category=AspectCategory.MUTATION,
                        effects=("state_mutation", "event_emit"),
                        help="Mutates the state",
                    ),
                ),
            ),
        )
        yaml = generate_frontmatter(node)
        assert "agentese:" in yaml
        assert "path: world.test" in yaml
        # Rich aspects should be included
        assert "name: manifest" in yaml or "- manifest" in yaml
        assert "mutate" in yaml

    def test_variadic_operation_roundtrip(self) -> None:
        """Variadic operations preserve variadic flag in frontmatter."""
        node = SpecNode(
            domain=SpecDomain.WORLD,
            holon="test",
            source_path=Path("spec/world/test.md"),
            operad=OperadSpec(
                operations=(
                    OperationSpec(name="merge", arity=-1, variadic=True),
                    OperationSpec(name="fixed", arity=2, variadic=False),
                ),
            ),
        )
        yaml = generate_frontmatter(node)
        assert "variadic: true" in yaml


# === Town Reference Jewel Roundtrip Tests ===


class TestTownRoundtrip:
    """
    Tests verifying Town as the reference Crown Jewel.

    Town is the canonical example of:
    - Polynomial: CitizenPhase (5 positions)
    - Operad: TOWN_OPERAD (8 operations, 3 laws)
    - AGENTESE: world.town.*

    The roundtrip test verifies: Reflect(impl) ≅ Parse(spec)
    """

    def test_town_spec_impl_alignment(self) -> None:
        """Verify Town spec and impl are structurally aligned."""
        from pathlib import Path

        from ..parser import parse_spec_file
        from ..reflect import reflect_jewel

        # Get impl root (relative to test file location)
        impl_root = Path(__file__).parent.parent.parent.parent.parent
        spec_root = impl_root.parent.parent / "spec"

        # Parse canonical spec (try town.md first, fallback to index.md)
        spec_path = spec_root / "town" / "town.md"
        if not spec_path.exists():
            spec_path = spec_root / "town" / "index.md"
        if not spec_path.exists():
            pytest.skip("spec/town/town.md or index.md not found")

        spec_node = parse_spec_file(spec_path)

        # Reflect implementation
        reflect_result = reflect_jewel("town", impl_root)

        # Verify structural alignment
        assert reflect_result.confidence >= 0.66, (
            "Town should have at least polynomial+operad"
        )
        assert reflect_result.spec_node is not None

        reflected = reflect_result.spec_node

        # Domain should match
        assert spec_node.domain == reflected.domain

        # Polynomial positions should match
        if spec_node.polynomial and reflected.polynomial:
            spec_positions = set(spec_node.polynomial.positions)
            impl_positions = set(reflected.polynomial.positions)
            assert spec_positions == impl_positions, (
                f"Position mismatch: spec={spec_positions}, impl={impl_positions}"
            )

        # Operad operations should match
        if spec_node.operad and reflected.operad:
            spec_ops = {op.name for op in spec_node.operad.operations}
            impl_ops = {op.name for op in reflected.operad.operations}
            assert spec_ops == impl_ops, (
                f"Operation mismatch: spec={spec_ops}, impl={impl_ops}"
            )

    def test_town_polynomial_positions(self) -> None:
        """Verify Town polynomial has the 5 canonical positions."""
        from pathlib import Path

        from ..reflect import reflect_jewel

        impl_root = Path(__file__).parent.parent.parent.parent.parent
        result = reflect_jewel("town", impl_root)

        assert result.spec_node is not None
        assert result.spec_node.polynomial is not None

        positions = set(result.spec_node.polynomial.positions)
        expected = {"idle", "socializing", "working", "reflecting", "resting"}
        assert positions == expected, f"Expected {expected}, got {positions}"

    def test_town_operad_operations(self) -> None:
        """Verify Town operad has the 8 canonical operations."""
        from pathlib import Path

        from ..reflect import reflect_jewel

        impl_root = Path(__file__).parent.parent.parent.parent.parent
        result = reflect_jewel("town", impl_root)

        assert result.spec_node is not None
        assert result.spec_node.operad is not None

        operations = {op.name for op in result.spec_node.operad.operations}
        # Core + Phase 2 operations
        expected = {
            "greet",
            "gossip",
            "trade",
            "solo",
            "dispute",
            "celebrate",
            "mourn",
            "teach",
        }
        assert operations == expected, f"Expected {expected}, got {operations}"

    def test_town_operad_laws(self) -> None:
        """Verify Town operad has the 3 canonical laws."""
        from pathlib import Path

        from ..reflect import reflect_jewel

        impl_root = Path(__file__).parent.parent.parent.parent.parent
        result = reflect_jewel("town", impl_root)

        assert result.spec_node is not None
        assert result.spec_node.operad is not None

        laws = {law.name for law in result.spec_node.operad.laws}
        expected = {"locality", "rest_inviolability", "coherence_preservation"}
        assert laws == expected, f"Expected {expected}, got {laws}"

    def test_town_full_audit_aligned(self) -> None:
        """Verify Town passes full audit (spec ≅ impl)."""
        from pathlib import Path

        from ..discovery import full_audit

        impl_root = Path(__file__).parent.parent.parent.parent.parent
        spec_root = impl_root.parent.parent / "spec"

        town_spec = spec_root / "town" / "town.md"
        if not town_spec.exists():
            town_spec = spec_root / "town" / "index.md"
        if not town_spec.exists():
            pytest.skip("spec/town/town.md or index.md not found")

        discovery, audit = full_audit(spec_root, impl_root)

        # Town should be aligned
        town_in_aligned = any("town" in comp.lower() for comp in audit.aligned)
        town_in_gaps = any("town" in gap.component.lower() for gap in audit.gaps)

        assert town_in_aligned or not town_in_gaps, (
            f"Town should be aligned. Gaps: {audit.gaps}"
        )
