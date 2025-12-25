"""
Comprehensive tests for Zero Seed Crystal taxonomy schemas.

Tests verify:
1. Schema creation - Can we create instances of each Crystal type?
2. Serialization - Do to_dict/from_dict round-trip correctly?
3. Layer validation - Are layers enforced correctly?
4. Proof requirements - L3+ requires proof, L1-L2 doesn't
5. Derivation chains - Can we trace derivation lineages?
6. Specialized behaviors - Layer-specific features work correctly

Coverage:
- L1: AxiomCrystal (no proof)
- L2: ValueCrystal (no proof, axiom lineage)
- L3: PromptCrystal (proof required, parameters)
- L4: SpecCrystal (proof required, AST hash)
- L5: FunctionCrystal, TestCrystal (proof required, call graph)
- L5: KBlockCrystal (proof required, hierarchy, coherence metrics)
- L5: InvocationCrystal (proof required, Galois loss tracking)
- L6: ReflectionCrystal (proof optional, synthesis)
- L7: InterpretationCrystal (proof optional, pattern detection)
- Infrastructure: GaloisWitnessedProof, LLMInvocationMark, StateChange
"""

from __future__ import annotations

import pytest
from datetime import datetime, UTC, timedelta

# Import all Crystal schemas
try:
    from ..schemas.axiom import AxiomCrystal, ValueCrystal, AXIOM_SCHEMA, VALUE_SCHEMA
except ImportError:
    AxiomCrystal = None  # type: ignore
    ValueCrystal = None  # type: ignore

try:
    from ..schemas.prompt import PromptCrystal, PromptParam, InvocationCrystal
except ImportError:
    PromptCrystal = None  # type: ignore
    PromptParam = None  # type: ignore
    InvocationCrystal = None  # type: ignore

try:
    from ..schemas.spec import SpecCrystal
except ImportError:
    SpecCrystal = None  # type: ignore

try:
    from ..schemas.code import FunctionCrystal, ParamInfo, TestCrystal, FUNCTION_CRYSTAL_SCHEMA, TEST_CRYSTAL_SCHEMA
except ImportError:
    FunctionCrystal = None  # type: ignore
    ParamInfo = None  # type: ignore
    TestCrystal = None  # type: ignore

try:
    from ..schemas.kblock import KBlockCrystal, KBLOCK_SIZE_HEURISTICS, KBLOCK_CRYSTAL_SCHEMA
except ImportError:
    KBlockCrystal = None  # type: ignore
    KBLOCK_SIZE_HEURISTICS = None  # type: ignore

try:
    from ..schemas.reflection import ReflectionCrystal, InterpretationCrystal
except ImportError:
    ReflectionCrystal = None  # type: ignore
    InterpretationCrystal = None  # type: ignore

try:
    from ..schemas.invocation import LLMInvocationMark, StateChange
except ImportError:
    LLMInvocationMark = None  # type: ignore
    StateChange = None  # type: ignore

try:
    from ..schemas.proof import GaloisWitnessedProof, PROOF_SCHEMA
except ImportError:
    GaloisWitnessedProof = None  # type: ignore


# =============================================================================
# Helper Fixtures
# =============================================================================


@pytest.fixture
def sample_proof() -> GaloisWitnessedProof:
    """Sample proof for testing crystals that require proofs."""
    if GaloisWitnessedProof is None:
        pytest.skip("GaloisWitnessedProof not available")

    return GaloisWitnessedProof(
        data="Implementation matches spec section 3.2",
        warrant="Spec defines behavior, implementation follows spec",
        claim="Function is correctly derived from spec",
        backing="Spec review by Kent + Claude",
        qualifier="definitely",
        rebuttals=("Could have edge cases not covered by spec",),
        tier="EMPIRICAL",
        principles=("Tasteful", "Composable"),
        galois_loss=0.05,
        loss_decomposition={"data": 0.02, "warrant": 0.03},
    )


# =============================================================================
# L0: Proof Infrastructure Tests
# =============================================================================


@pytest.mark.skipif(GaloisWitnessedProof is None, reason="GaloisWitnessedProof not available")
class TestGaloisWitnessedProof:
    """Tests for GaloisWitnessedProof base infrastructure."""

    def test_create_minimal_proof(self) -> None:
        """Can create proof with minimal fields."""
        proof = GaloisWitnessedProof(
            data="Evidence",
            warrant="Reasoning",
            claim="Conclusion",
            backing="Support",
        )

        assert proof.data == "Evidence"
        assert proof.warrant == "Reasoning"
        assert proof.claim == "Conclusion"
        assert proof.backing == "Support"
        assert proof.qualifier == "probably"  # Default
        assert proof.galois_loss == 0.0  # Default

    def test_coherence_property(self) -> None:
        """Coherence = 1 - galois_loss."""
        proof = GaloisWitnessedProof(
            data="Test", warrant="Test", claim="Test", backing="Test",
            galois_loss=0.3,
        )

        assert proof.coherence == pytest.approx(0.7)

    def test_proof_serialization(self) -> None:
        """Proof to_dict/from_dict roundtrips correctly."""
        original = GaloisWitnessedProof(
            data="Data",
            warrant="Warrant",
            claim="Claim",
            backing="Backing",
            qualifier="certainly",
            rebuttals=("Rebuttal 1", "Rebuttal 2"),
            tier="CATEGORICAL",
            principles=("Tasteful", "Composable"),
            galois_loss=0.1,
            loss_decomposition={"data": 0.05, "warrant": 0.05},
        )

        d = original.to_dict()
        restored = GaloisWitnessedProof.from_dict(d)

        assert restored.data == original.data
        assert restored.warrant == original.warrant
        assert restored.claim == original.claim
        assert restored.backing == original.backing
        assert restored.qualifier == original.qualifier
        assert restored.rebuttals == original.rebuttals
        assert restored.tier == original.tier
        assert restored.principles == original.principles
        assert restored.galois_loss == original.galois_loss
        assert restored.loss_decomposition == original.loss_decomposition


# =============================================================================
# L1: Axiom Crystal Tests (No Proof Required)
# =============================================================================


@pytest.mark.skipif(AxiomCrystal is None, reason="AxiomCrystal not available")
class TestAxiomCrystal:
    """Tests for L1 AxiomCrystal - foundational truths."""

    def test_create_axiom(self) -> None:
        """Can create axiom without proof."""
        axiom = AxiomCrystal(
            content="Everything composes",
            domain="constitution",
            tags=frozenset({"composability", "foundation"}),
        )

        assert axiom.content == "Everything composes"
        assert axiom.domain == "constitution"
        assert "composability" in axiom.tags

    def test_axiom_serialization(self) -> None:
        """Round-trip serialization works."""
        original = AxiomCrystal(
            content="Tasteful > feature-complete",
            domain="design",
            tags=frozenset({"taste", "curation"}),
        )

        d = original.to_dict()
        restored = AxiomCrystal.from_dict(d)

        assert restored.content == original.content
        assert restored.domain == original.domain
        assert restored.tags == original.tags

    def test_axiom_immutability(self) -> None:
        """Axioms are immutable (frozen dataclass)."""
        axiom = AxiomCrystal(
            content="Test axiom",
            domain="test",
        )

        with pytest.raises(AttributeError):
            axiom.content = "Modified"  # type: ignore

    def test_axiom_tags_are_frozenset(self) -> None:
        """Tags field is frozenset for immutability."""
        axiom = AxiomCrystal(
            content="Test",
            domain="test",
            tags=frozenset({"tag1", "tag2"}),
        )

        assert isinstance(axiom.tags, frozenset)


# =============================================================================
# L2: Value Crystal Tests (No Proof, Axiom Lineage)
# =============================================================================


@pytest.mark.skipif(ValueCrystal is None, reason="ValueCrystal not available")
class TestValueCrystal:
    """Tests for L2 ValueCrystal - derived principles."""

    def test_create_value(self) -> None:
        """Can create value linked to axioms."""
        value = ValueCrystal(
            principle="Depth over breadth",
            axiom_ids=("axiom-001", "axiom-002"),
            tags=frozenset({"curation", "taste"}),
        )

        assert value.principle == "Depth over breadth"
        assert value.axiom_ids == ("axiom-001", "axiom-002")

    def test_value_links_to_axioms(self) -> None:
        """Value references axiom IDs for lineage."""
        value = ValueCrystal(
            principle="Tool transparency builds trust",
            axiom_ids=("axiom-transparency", "axiom-joy"),
        )

        assert len(value.axiom_ids) == 2
        assert "axiom-transparency" in value.axiom_ids

    def test_value_serialization(self) -> None:
        """Round-trip serialization preserves axiom lineage."""
        original = ValueCrystal(
            principle="Test principle",
            axiom_ids=("ax-1", "ax-2", "ax-3"),
            tags=frozenset({"tag"}),
        )

        d = original.to_dict()
        restored = ValueCrystal.from_dict(d)

        assert restored.principle == original.principle
        assert restored.axiom_ids == original.axiom_ids
        assert restored.tags == original.tags

    def test_value_empty_axiom_ids(self) -> None:
        """Value can have empty axiom_ids (though unusual)."""
        value = ValueCrystal(
            principle="Orphan value",
            axiom_ids=(),
        )

        assert value.axiom_ids == ()


# =============================================================================
# L3: Prompt Crystal Tests (Proof Required, Parameters)
# =============================================================================


@pytest.mark.skipif(PromptCrystal is None or PromptParam is None, reason="PromptCrystal not available")
class TestPromptParam:
    """Tests for PromptParam parameter definitions."""

    def test_create_prompt_param(self) -> None:
        """Can create parameter definition."""
        param = PromptParam(
            name="context",
            type="str",
            constraints={"min_length": 10, "max_length": 1000},
            default=None,
            examples=("Example 1", "Example 2"),
        )

        assert param.name == "context"
        assert param.type == "str"
        assert param.constraints["min_length"] == 10

    def test_param_serialization(self) -> None:
        """PromptParam roundtrips correctly."""
        original = PromptParam(
            name="task",
            type="str",
            constraints={"enum": ["analyze", "generate", "refactor"]},
            default="analyze",
            examples=("analyze code", "generate tests"),
        )

        d = original.to_dict()
        restored = PromptParam.from_dict(d)

        assert restored.name == original.name
        assert restored.type == original.type
        assert restored.constraints == original.constraints
        assert restored.default == original.default
        assert restored.examples == original.examples


@pytest.mark.skipif(PromptCrystal is None, reason="PromptCrystal not available")
class TestPromptCrystal:
    """Tests for L3 PromptCrystal - derived prompts with proofs."""

    def test_create_prompt_with_proof(self, sample_proof: GaloisWitnessedProof) -> None:
        """L3 requires proof field."""
        prompt = PromptCrystal(
            template="Given {context}, perform {task} following {constraints}",
            parameters={
                "context": PromptParam(name="context", type="str"),
                "task": PromptParam(name="task", type="str"),
                "constraints": PromptParam(name="constraints", type="str"),
            },
            goal_statement="Generate tasteful code",
            derived_from=("value:tasteful", "spec:code-gen"),
            version=1,
            created_by="kent",
            proof=sample_proof,
        )

        assert prompt.template.startswith("Given {context}")
        assert "context" in prompt.parameters
        assert prompt.version == 1
        assert prompt.proof.claim == sample_proof.claim

    def test_prompt_serialization(self, sample_proof: GaloisWitnessedProof) -> None:
        """Prompt roundtrips with nested parameters."""
        original = PromptCrystal(
            template="Test {param}",
            parameters={"param": PromptParam(name="param", type="int", default=42)},
            goal_statement="Test goal",
            derived_from=("val-1",),
            version=2,
            created_by="system",
            proof=sample_proof,
        )

        d = original.to_dict()
        restored = PromptCrystal.from_dict(d)

        assert restored.template == original.template
        assert "param" in restored.parameters
        assert restored.parameters["param"].default == 42
        assert restored.version == original.version
        assert restored.proof.claim == original.proof.claim

    def test_prompt_version_monotonic(self, sample_proof: GaloisWitnessedProof) -> None:
        """Version field enables evolution tracking."""
        v1 = PromptCrystal(
            template="Version 1",
            parameters={},
            goal_statement="Goal",
            derived_from=(),
            version=1,
            created_by="kent",
            proof=sample_proof,
        )

        v2 = PromptCrystal(
            template="Version 2",
            parameters={},
            goal_statement="Goal",
            derived_from=(),
            version=2,
            created_by="kent",
            proof=sample_proof,
        )

        assert v2.version > v1.version


# =============================================================================
# L4: Spec Crystal Tests (Proof Required, AST Hash)
# =============================================================================


@pytest.mark.skipif(SpecCrystal is None, reason="SpecCrystal not available")
class TestSpecCrystal:
    """Tests for L4 SpecCrystal - formal specifications."""

    def test_create_interface_spec(self, sample_proof: GaloisWitnessedProof) -> None:
        """Can create interface specification."""
        spec = SpecCrystal(
            spec_type="interface",
            language="python",
            content="def process(data: str) -> Result: ...",
            ast_hash="abc123def456",
            dependencies=("spec:result-type",),
            goal_prompt_id="prompt:data-processing",
            proof=sample_proof,
        )

        assert spec.spec_type == "interface"
        assert spec.language == "python"
        assert spec.ast_hash == "abc123def456"

    def test_create_markdown_spec(self, sample_proof: GaloisWitnessedProof) -> None:
        """Can create markdown documentation spec (no AST hash)."""
        spec = SpecCrystal(
            spec_type="behavior",
            language="markdown",
            content="## Processing Flow\n1. Validate\n2. Transform",
            ast_hash=None,
            dependencies=(),
            goal_prompt_id="prompt:system-design",
            proof=sample_proof,
        )

        assert spec.spec_type == "behavior"
        assert spec.ast_hash is None

    def test_spec_serialization(self, sample_proof: GaloisWitnessedProof) -> None:
        """Spec roundtrips with dependencies."""
        original = SpecCrystal(
            spec_type="constraint",
            language="python",
            content="assert x > 0",
            ast_hash="hash123",
            dependencies=("spec:x-definition", "spec:invariants"),
            goal_prompt_id="prompt:validation",
            proof=sample_proof,
        )

        d = original.to_dict()
        restored = SpecCrystal.from_dict(d)

        assert restored.spec_type == original.spec_type
        assert restored.language == original.language
        assert restored.content == original.content
        assert restored.ast_hash == original.ast_hash
        assert restored.dependencies == original.dependencies
        assert restored.goal_prompt_id == original.goal_prompt_id


# =============================================================================
# L5: Function Crystal Tests (Proof Required, Call Graph)
# =============================================================================


@pytest.mark.skipif(ParamInfo is None, reason="ParamInfo not available")
class TestParamInfo:
    """Tests for ParamInfo function parameter metadata."""

    def test_create_param_info(self) -> None:
        """Can create parameter metadata."""
        param = ParamInfo(
            name="x",
            type_annotation="int",
            default="42",
            is_variadic=False,
            is_keyword=False,
        )

        assert param.name == "x"
        assert param.type_annotation == "int"
        assert param.default == "42"

    def test_variadic_param(self) -> None:
        """Can represent *args."""
        param = ParamInfo(
            name="args",
            type_annotation="Any",
            is_variadic=True,
        )

        assert param.is_variadic is True

    def test_keyword_param(self) -> None:
        """Can represent **kwargs."""
        param = ParamInfo(
            name="kwargs",
            type_annotation="Any",
            is_keyword=True,
        )

        assert param.is_keyword is True

    def test_param_serialization(self) -> None:
        """ParamInfo roundtrips correctly."""
        original = ParamInfo(
            name="value",
            type_annotation="str | None",
            default="None",
        )

        d = original.to_dict()
        restored = ParamInfo.from_dict(d)

        assert restored.name == original.name
        assert restored.type_annotation == original.type_annotation
        assert restored.default == original.default


@pytest.mark.skipif(FunctionCrystal is None, reason="FunctionCrystal not available")
class TestFunctionCrystal:
    """Tests for L5 FunctionCrystal - code tracking."""

    def test_create_function_crystal(self, sample_proof: GaloisWitnessedProof) -> None:
        """Can create function crystal with full metadata."""
        func = FunctionCrystal(
            id="func-001",
            qualified_name="agents.d.galois.compute_loss",
            file_path="impl/claude/agents/d/galois.py",
            line_range=(10, 30),
            signature="def compute_loss(data: str) -> float",
            docstring="Compute Galois loss for data.",
            body_hash="abc123",
            parameters=(
                ParamInfo(name="data", type_annotation="str"),
            ),
            return_type="float",
            imports=frozenset({"math.log", "typing.Any"}),
            calls=frozenset({"extract_terms", "normalize"}),
            called_by=frozenset({"services.witness.save_with_loss"}),
            layer=5,
            spec_id="spec/protocols/galois.md#compute-loss",
            derived_from=(),
            kblock_id="kblock-galois-core",
            is_ghost=False,
            proof=sample_proof,
        )

        assert func.qualified_name == "agents.d.galois.compute_loss"
        assert func.layer == 5
        assert "extract_terms" in func.calls
        assert func.is_ghost is False

    def test_ghost_function(self, sample_proof: GaloisWitnessedProof) -> None:
        """Ghost functions mark implied/missing functions."""
        ghost = FunctionCrystal(
            id="ghost-001",
            qualified_name="missing.function",
            file_path="",
            line_range=(0, 0),
            signature="def missing() -> None",
            is_ghost=True,
            ghost_reason="Called but not yet implemented",
            proof=sample_proof,
        )

        assert ghost.is_ghost is True
        assert ghost.ghost_reason is not None

    def test_function_call_graph(self, sample_proof: GaloisWitnessedProof) -> None:
        """Call graph fields capture dependencies."""
        func = FunctionCrystal(
            id="func-002",
            qualified_name="test.func",
            file_path="test.py",
            line_range=(1, 10),
            signature="def func() -> None",
            calls=frozenset({"helper_a", "helper_b"}),
            called_by=frozenset({"main", "entrypoint"}),
            proof=sample_proof,
        )

        assert len(func.calls) == 2
        assert len(func.called_by) == 2
        assert "helper_a" in func.calls
        assert "main" in func.called_by

    def test_function_serialization(self, sample_proof: GaloisWitnessedProof) -> None:
        """Function crystal roundtrips correctly."""
        original = FunctionCrystal(
            id="func-003",
            qualified_name="test.function",
            file_path="/path/to/file.py",
            line_range=(5, 15),
            signature="def function(x: int) -> str",
            docstring="Test function.",
            body_hash="hash123",
            parameters=(ParamInfo(name="x", type_annotation="int"),),
            return_type="str",
            imports=frozenset({"os", "sys"}),
            calls=frozenset(),
            called_by=frozenset(),
            layer=5,
            spec_id="spec.md",
            kblock_id="kb-1",
            proof=sample_proof,
        )

        d = original.to_dict()
        restored = FunctionCrystal.from_dict(d)

        assert restored.qualified_name == original.qualified_name
        assert restored.line_range == original.line_range
        assert restored.parameters[0].name == "x"
        assert restored.layer == original.layer


@pytest.mark.skipif(TestCrystal is None, reason="TestCrystal not available")
class TestTestCrystal:
    """Tests for L5 TestCrystal - test tracking."""

    def test_create_test_crystal(self, sample_proof: GaloisWitnessedProof) -> None:
        """Can create test crystal linked to function."""
        test = TestCrystal(
            id="test-001",
            path="impl/claude/agents/d/_tests/test_galois.py",
            test_name="test_compute_loss",
            target_id="func-001",
            test_type="unit",
            last_result="pass",
            assertion_count=5,
            spec_id="spec/galois.md",
            proof=sample_proof,
        )

        assert test.test_name == "test_compute_loss"
        assert test.target_id == "func-001"
        assert test.test_type == "unit"

    def test_test_result_properties(self, sample_proof: GaloisWitnessedProof) -> None:
        """Test result convenience properties work."""
        passing = TestCrystal(
            id="test-pass",
            path="test.py",
            test_name="test_pass",
            target_id="func",
            last_result="pass",
            proof=sample_proof,
        )

        failing = TestCrystal(
            id="test-fail",
            path="test.py",
            test_name="test_fail",
            target_id="func",
            last_result="fail",
            proof=sample_proof,
        )

        assert passing.is_passing is True
        assert passing.is_failing is False
        assert failing.is_passing is False
        assert failing.is_failing is True

    def test_test_types(self, sample_proof: GaloisWitnessedProof) -> None:
        """Different test types are captured."""
        for test_type in ["unit", "integration", "property", "chaos"]:
            test = TestCrystal(
                id=f"test-{test_type}",
                path="test.py",
                test_name=f"test_{test_type}",
                target_id="func",
                test_type=test_type,
                proof=sample_proof,
            )
            assert test.test_type == test_type

    def test_test_serialization(self, sample_proof: GaloisWitnessedProof) -> None:
        """Test crystal roundtrips correctly."""
        original = TestCrystal(
            id="test-002",
            path="/path/to/test.py",
            test_name="test_function",
            target_id="func-002",
            test_type="integration",
            last_result="skip",
            assertion_count=3,
            spec_id="spec.md",
            proof=sample_proof,
        )

        d = original.to_dict()
        restored = TestCrystal.from_dict(d)

        assert restored.test_name == original.test_name
        assert restored.target_id == original.target_id
        assert restored.test_type == original.test_type
        assert restored.last_result == original.last_result


# =============================================================================
# L5: K-Block Crystal Tests (Proof Required, Hierarchy, Coherence)
# =============================================================================


@pytest.mark.skipif(KBlockCrystal is None, reason="KBlockCrystal not available")
class TestKBlockSizeHeuristics:
    """Tests for K-block size heuristics."""

    def test_heuristics_values(self) -> None:
        """Heuristics have expected values."""
        if KBLOCK_SIZE_HEURISTICS is None:
            pytest.skip("KBLOCK_SIZE_HEURISTICS not available")

        assert KBLOCK_SIZE_HEURISTICS["target_tokens"] == 2000
        assert KBLOCK_SIZE_HEURISTICS["min_tokens"] == 500
        assert KBLOCK_SIZE_HEURISTICS["max_tokens"] == 5000
        assert KBLOCK_SIZE_HEURISTICS["chars_per_token"] == 4


@pytest.mark.skipif(KBlockCrystal is None, reason="KBlockCrystal not available")
class TestKBlockCrystal:
    """Tests for L5 KBlockCrystal - coherence windows."""

    def test_create_kblock(self, sample_proof: GaloisWitnessedProof) -> None:
        """Can create K-block with functions."""
        kblock = KBlockCrystal(
            id="kb-001",
            name="galois_core",
            path="impl/claude/agents/d/galois.py",
            function_ids=frozenset({"func-001", "func-002", "func-003"}),
            boundary_type="file",
            function_count=3,
            total_lines=150,
            estimated_tokens=600,
            internal_coherence=0.9,
            external_coupling=0.2,
            dominant_layer=5,
            layer_distribution={5: 3},
            proof=sample_proof,
        )

        assert kblock.name == "galois_core"
        assert len(kblock.function_ids) == 3
        assert kblock.boundary_type == "file"

    def test_kblock_hierarchy(self, sample_proof: GaloisWitnessedProof) -> None:
        """K-blocks can nest (child/parent)."""
        parent = KBlockCrystal(
            id="kb-module",
            name="services.witness",
            path="impl/claude/services/witness/",
            boundary_type="module",
            child_kblock_ids=frozenset({"kb-store", "kb-persistence"}),
            proof=sample_proof,
        )

        child = KBlockCrystal(
            id="kb-store",
            name="witness.store",
            path="impl/claude/services/witness/store.py",
            boundary_type="file",
            parent_kblock_id="kb-module",
            proof=sample_proof,
        )

        assert "kb-store" in parent.child_kblock_ids
        assert child.parent_kblock_id == "kb-module"

    def test_kblock_size_properties(self, sample_proof: GaloisWitnessedProof) -> None:
        """K-block size checks work correctly."""
        undersized = KBlockCrystal(
            id="kb-small",
            name="small",
            path="small.py",
            estimated_tokens=300,  # < 500 min
            proof=sample_proof,
        )

        optimal = KBlockCrystal(
            id="kb-optimal",
            name="optimal",
            path="optimal.py",
            estimated_tokens=2000,  # Target
            proof=sample_proof,
        )

        oversized = KBlockCrystal(
            id="kb-large",
            name="large",
            path="large.py",
            estimated_tokens=6000,  # > 5000 max
            proof=sample_proof,
        )

        assert undersized.is_undersized is True
        assert undersized.needs_split is False

        assert optimal.is_optimal_size is True
        assert optimal.needs_split is False

        assert oversized.needs_split is True
        assert oversized.is_optimal_size is False

    def test_kblock_coherence_metrics(self, sample_proof: GaloisWitnessedProof) -> None:
        """Coherence and coupling metrics captured."""
        kblock = KBlockCrystal(
            id="kb-002",
            name="test",
            path="test.py",
            internal_coherence=0.95,
            external_coupling=0.1,
            proof=sample_proof,
        )

        assert kblock.internal_coherence == pytest.approx(0.95)
        assert kblock.external_coupling == pytest.approx(0.1)

    def test_kblock_serialization(self, sample_proof: GaloisWitnessedProof) -> None:
        """K-block roundtrips with hierarchy."""
        original = KBlockCrystal(
            id="kb-003",
            name="test_block",
            path="/path/to/module",
            function_ids=frozenset({"f1", "f2"}),
            child_kblock_ids=frozenset({"kb-child"}),
            parent_kblock_id="kb-parent",
            boundary_type="feature",
            boundary_confidence=0.85,
            function_count=2,
            total_lines=100,
            estimated_tokens=400,
            internal_coherence=0.8,
            external_coupling=0.3,
            dominant_layer=5,
            layer_distribution={5: 2},
            proof=sample_proof,
        )

        d = original.to_dict()
        restored = KBlockCrystal.from_dict(d)

        assert restored.name == original.name
        assert restored.function_ids == original.function_ids
        assert restored.child_kblock_ids == original.child_kblock_ids
        assert restored.parent_kblock_id == original.parent_kblock_id
        assert restored.boundary_type == original.boundary_type
        assert restored.internal_coherence == original.internal_coherence


# =============================================================================
# L5: Invocation Crystal Tests (Proof Required, Galois Loss)
# =============================================================================


@pytest.mark.skipif(InvocationCrystal is None, reason="InvocationCrystal not available")
class TestInvocationCrystal:
    """Tests for L5 InvocationCrystal - runtime execution tracking."""

    def test_create_invocation(self, sample_proof: GaloisWitnessedProof) -> None:
        """Can create invocation with metrics."""
        invocation = InvocationCrystal(
            prompt_id="prompt-001",
            parameters={"context": "test", "task": "analyze"},
            timestamp=datetime.now(UTC),
            executor="kent",
            output_id="spec-001",
            success=True,
            duration_ms=250,
            token_count=150,
            galois_loss_input=0.05,
            galois_loss_output=0.03,
            proof=sample_proof,
        )

        assert invocation.prompt_id == "prompt-001"
        assert invocation.success is True
        assert invocation.token_count == 150

    def test_invocation_galois_loss(self, sample_proof: GaloisWitnessedProof) -> None:
        """Galois loss tracked for input and output."""
        invocation = InvocationCrystal(
            prompt_id="prompt-002",
            parameters={},
            timestamp=datetime.now(UTC),
            executor="system",
            output_id=None,
            success=True,
            duration_ms=100,
            token_count=50,
            galois_loss_input=0.1,
            galois_loss_output=0.2,
            proof=sample_proof,
        )

        assert invocation.galois_loss_input == pytest.approx(0.1)
        assert invocation.galois_loss_output == pytest.approx(0.2)

    def test_invocation_serialization(self, sample_proof: GaloisWitnessedProof) -> None:
        """Invocation roundtrips with timestamp."""
        ts = datetime.now(UTC)
        original = InvocationCrystal(
            prompt_id="prompt-003",
            parameters={"key": "value"},
            timestamp=ts,
            executor="claude",
            output_id="output-001",
            success=False,
            duration_ms=500,
            token_count=200,
            galois_loss_input=0.15,
            galois_loss_output=0.25,
            proof=sample_proof,
        )

        d = original.to_dict()
        restored = InvocationCrystal.from_dict(d)

        assert restored.prompt_id == original.prompt_id
        assert restored.parameters == original.parameters
        assert restored.timestamp == original.timestamp
        assert restored.executor == original.executor
        assert restored.success == original.success
        assert restored.galois_loss_input == original.galois_loss_input


# =============================================================================
# L6: Reflection Crystal Tests (Proof Optional, Synthesis)
# =============================================================================


@pytest.mark.skipif(ReflectionCrystal is None, reason="ReflectionCrystal not available")
class TestReflectionCrystal:
    """Tests for L6 ReflectionCrystal - artifact reflection."""

    def test_create_synthesis_reflection(self, sample_proof: GaloisWitnessedProof) -> None:
        """Can create synthesis reflection."""
        reflection = ReflectionCrystal(
            id="refl-001",
            target_ids=("spec-001", "spec-002", "spec-003"),
            reflection_type="synthesis",
            insight="All specs converge on same interface pattern",
            recommendations=("Unify interfaces", "Extract common base"),
            derived_from=("spec-001", "spec-002", "spec-003"),
            layer=6,
            proof=sample_proof,
        )

        assert reflection.reflection_type == "synthesis"
        assert reflection.layer == 6
        assert len(reflection.target_ids) == 3

    def test_create_comparison_reflection(self) -> None:
        """Can create comparison reflection without proof."""
        reflection = ReflectionCrystal(
            id="refl-002",
            target_ids=("impl-v1", "impl-v2"),
            reflection_type="comparison",
            insight="V2 has 30% less coupling",
            recommendations=("Migrate to v2",),
            derived_from=("impl-v1", "impl-v2"),
            proof=None,  # Optional for L6
        )

        assert reflection.reflection_type == "comparison"
        assert reflection.proof is None

    def test_reflection_types(self, sample_proof: GaloisWitnessedProof) -> None:
        """All reflection types work."""
        for rtype in ["synthesis", "comparison", "delta", "audit"]:
            refl = ReflectionCrystal(
                id=f"refl-{rtype}",
                target_ids=("target",),
                reflection_type=rtype,
                insight=f"{rtype} insight",
                recommendations=(),
                derived_from=("target",),
                proof=sample_proof,
            )
            assert refl.reflection_type == rtype

    def test_reflection_serialization(self, sample_proof: GaloisWitnessedProof) -> None:
        """Reflection roundtrips correctly."""
        original = ReflectionCrystal(
            id="refl-003",
            target_ids=("t1", "t2"),
            reflection_type="delta",
            insight="Changed significantly",
            recommendations=("Review changes", "Update docs"),
            derived_from=("t1", "t2"),
            layer=6,
            proof=sample_proof,
        )

        d = original.to_dict()
        restored = ReflectionCrystal.from_dict(d)

        assert restored.id == original.id
        assert restored.target_ids == original.target_ids
        assert restored.reflection_type == original.reflection_type
        assert restored.insight == original.insight
        assert restored.recommendations == original.recommendations


# =============================================================================
# L7: Interpretation Crystal Tests (Proof Optional, Patterns)
# =============================================================================


@pytest.mark.skipif(InterpretationCrystal is None, reason="InterpretationCrystal not available")
class TestInterpretationCrystal:
    """Tests for L7 InterpretationCrystal - pattern detection."""

    def test_create_trend_interpretation(self, sample_proof: GaloisWitnessedProof) -> None:
        """Can create trend interpretation."""
        start = datetime.now(UTC) - timedelta(days=30)
        end = datetime.now(UTC)

        interp = InterpretationCrystal(
            id="interp-001",
            artifact_pattern="impl/claude/agents/**/*.py",
            time_range=(start, end),
            insight_type="trend",
            content="Galois loss decreasing 5% per week",
            confidence=0.85,
            supporting_ids=("inv-001", "inv-002", "inv-003"),
            layer=7,
            proof=sample_proof,
        )

        assert interp.insight_type == "trend"
        assert interp.layer == 7
        assert interp.confidence == pytest.approx(0.85)

    def test_create_pattern_interpretation(self) -> None:
        """Can create pattern interpretation without proof."""
        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 12, 31, tzinfo=UTC)

        interp = InterpretationCrystal(
            id="interp-002",
            artifact_pattern="**/*.md",
            time_range=(start, end),
            insight_type="pattern",
            content="Specs follow common structure",
            confidence=0.95,
            supporting_ids=("spec-001", "spec-002"),
            proof=None,  # Optional for L7
        )

        assert interp.insight_type == "pattern"
        assert interp.proof is None

    def test_interpretation_time_range(self, sample_proof: GaloisWitnessedProof) -> None:
        """Time range captures analysis window."""
        start = datetime(2025, 6, 1, tzinfo=UTC)
        end = datetime(2025, 6, 30, tzinfo=UTC)

        interp = InterpretationCrystal(
            id="interp-003",
            artifact_pattern="*.py",
            time_range=(start, end),
            insight_type="prediction",
            content="Will reach target by end of Q3",
            confidence=0.7,
            supporting_ids=(),
            proof=sample_proof,
        )

        assert interp.time_range[0] == start
        assert interp.time_range[1] == end

    def test_interpretation_serialization(self, sample_proof: GaloisWitnessedProof) -> None:
        """Interpretation roundtrips with time range."""
        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 12, 31, tzinfo=UTC)

        original = InterpretationCrystal(
            id="interp-004",
            artifact_pattern="impl/**/*.py",
            time_range=(start, end),
            insight_type="trend",
            content="Quality improving",
            confidence=0.9,
            supporting_ids=("s1", "s2"),
            layer=7,
            proof=sample_proof,
        )

        d = original.to_dict()
        restored = InterpretationCrystal.from_dict(d)

        assert restored.id == original.id
        assert restored.artifact_pattern == original.artifact_pattern
        assert restored.time_range == original.time_range
        assert restored.insight_type == original.insight_type
        assert restored.confidence == original.confidence


# =============================================================================
# Infrastructure: LLM Invocation Mark Tests
# =============================================================================


@pytest.mark.skipif(StateChange is None, reason="StateChange not available")
class TestStateChange:
    """Tests for StateChange ripple tracking."""

    def test_create_state_change(self) -> None:
        """Can create state change record."""
        change = StateChange(
            entity_type="crystal",
            entity_id="crystal-001",
            change_type="created",
            before_hash=None,
            after_hash="abc123",
        )

        assert change.entity_type == "crystal"
        assert change.change_type == "created"
        assert change.before_hash is None

    def test_state_change_serialization(self) -> None:
        """StateChange roundtrips correctly."""
        original = StateChange(
            entity_type="kblock",
            entity_id="kb-001",
            change_type="updated",
            before_hash="old123",
            after_hash="new456",
        )

        d = original.to_dict()
        restored = StateChange.from_dict(d)

        assert restored.entity_type == original.entity_type
        assert restored.entity_id == original.entity_id
        assert restored.change_type == original.change_type
        assert restored.before_hash == original.before_hash
        assert restored.after_hash == original.after_hash


@pytest.mark.skipif(LLMInvocationMark is None, reason="LLMInvocationMark not available")
class TestLLMInvocationMark:
    """Tests for LLMInvocationMark comprehensive tracking."""

    def test_create_invocation_mark(self) -> None:
        """Can create LLM invocation with full causality."""
        mark = LLMInvocationMark(
            id="inv-001",
            action="Generate analysis",
            reasoning="User requested spec analysis",
            model="claude-opus-4-5",
            prompt_tokens=500,
            completion_tokens=300,
            latency_ms=1200,
            temperature=0.7,
            system_prompt_hash="sys123",
            user_prompt="Analyze spec.md",
            response="Analysis complete.",
            causal_parent_id=None,
            triggered_by="user_input",
            state_changes=(
                StateChange("crystal", "c1", "created", None, "hash1"),
            ),
            crystals_created=("c1",),
            crystals_modified=(),
            galois_loss=0.08,
            invocation_type="analysis",
        )

        assert mark.action == "Generate analysis"
        assert mark.model == "claude-opus-4-5"
        assert mark.is_root is True

    def test_invocation_causal_chain(self) -> None:
        """Causal parent/children tracked."""
        root = LLMInvocationMark(
            id="inv-root",
            action="Root action",
            reasoning="User input",
            model="claude",
            prompt_tokens=100,
            completion_tokens=50,
            latency_ms=500,
            temperature=0.7,
            system_prompt_hash="sys",
            user_prompt="prompt",
            response="response",
            causal_parent_id=None,
            triggered_by="user_input",
            state_changes=(),
            crystals_created=(),
            crystals_modified=(),
            galois_loss=0.05,
            invocation_type="generation",
        )

        child = LLMInvocationMark(
            id="inv-child",
            action="Child action",
            reasoning="Cascade from root",
            model="claude",
            prompt_tokens=50,
            completion_tokens=25,
            latency_ms=300,
            temperature=0.7,
            system_prompt_hash="sys",
            user_prompt="child prompt",
            response="child response",
            causal_parent_id="inv-root",
            triggered_by="cascade",
            state_changes=(),
            crystals_created=(),
            crystals_modified=(),
            galois_loss=0.03,
            invocation_type="generation",
        )

        assert root.is_root is True
        assert root.is_cascade is False
        assert child.is_root is False
        assert child.is_cascade is True
        assert child.causal_parent_id == "inv-root"

    def test_invocation_ripple_magnitude(self) -> None:
        """Ripple magnitude counts total effects."""
        mark = LLMInvocationMark(
            id="inv-002",
            action="Action",
            reasoning="Reasoning",
            model="claude",
            prompt_tokens=100,
            completion_tokens=50,
            latency_ms=500,
            temperature=0.7,
            system_prompt_hash="sys",
            user_prompt="prompt",
            response="response",
            causal_parent_id=None,
            triggered_by="user_input",
            state_changes=(
                StateChange("crystal", "c1", "created", None, "h1"),
                StateChange("crystal", "c2", "created", None, "h2"),
            ),
            crystals_created=("c1", "c2"),
            crystals_modified=("c3",),
            galois_loss=0.05,
            invocation_type="generation",
        )

        # 2 state_changes + 2 created + 1 modified = 5
        assert mark.ripple_magnitude == 5

    def test_invocation_metrics(self) -> None:
        """Performance metrics calculated correctly."""
        mark = LLMInvocationMark(
            id="inv-003",
            action="Action",
            reasoning="Reasoning",
            model="claude",
            prompt_tokens=400,
            completion_tokens=600,
            latency_ms=2000,
            temperature=0.7,
            system_prompt_hash="sys",
            user_prompt="prompt",
            response="response",
            causal_parent_id=None,
            triggered_by="user_input",
            state_changes=(),
            crystals_created=(),
            crystals_modified=(),
            galois_loss=0.2,
            invocation_type="generation",
        )

        assert mark.total_tokens == 1000
        assert mark.tokens_per_second == pytest.approx(300.0)  # 600 / 2.0
        assert mark.coherence == pytest.approx(0.8)  # 1 - 0.2

    def test_invocation_serialization(self) -> None:
        """LLMInvocationMark roundtrips correctly."""
        ts = datetime.now(UTC)
        original = LLMInvocationMark(
            id="inv-004",
            action="Test action",
            reasoning="Test reasoning",
            model="test-model",
            prompt_tokens=10,
            completion_tokens=20,
            latency_ms=100,
            temperature=0.5,
            system_prompt_hash="hash",
            user_prompt="prompt",
            response="response",
            causal_parent_id="parent",
            triggered_by="cascade",
            state_changes=(
                StateChange("crystal", "c1", "created", None, "h1"),
            ),
            crystals_created=("c1",),
            crystals_modified=(),
            galois_loss=0.1,
            invocation_type="analysis",
            timestamp=ts,
            tags=frozenset({"test", "cascade"}),
        )

        d = original.to_dict()
        restored = LLMInvocationMark.from_dict(d)

        assert restored.id == original.id
        assert restored.action == original.action
        assert restored.model == original.model
        assert restored.causal_parent_id == original.causal_parent_id
        assert len(restored.state_changes) == 1
        assert restored.galois_loss == original.galois_loss
        assert restored.tags == original.tags


# =============================================================================
# Layer Enforcement Tests
# =============================================================================


class TestLayerEnforcement:
    """Tests for layer-based proof requirements."""

    @pytest.mark.skipif(AxiomCrystal is None, reason="AxiomCrystal not available")
    def test_l1_no_proof_required(self) -> None:
        """L1 (Axiom) doesn't have proof field."""
        axiom = AxiomCrystal(
            content="Test axiom",
            domain="test",
        )

        # AxiomCrystal has no 'proof' attribute
        assert not hasattr(axiom, 'proof')

    @pytest.mark.skipif(ValueCrystal is None, reason="ValueCrystal not available")
    def test_l2_no_proof_required(self) -> None:
        """L2 (Value) doesn't have proof field."""
        value = ValueCrystal(
            principle="Test principle",
            axiom_ids=(),
        )

        # ValueCrystal has no 'proof' attribute
        assert not hasattr(value, 'proof')

    @pytest.mark.skipif(PromptCrystal is None, reason="PromptCrystal not available")
    def test_l3_requires_proof(self, sample_proof: GaloisWitnessedProof) -> None:
        """L3 (Prompt) requires proof field."""
        prompt = PromptCrystal(
            template="Test",
            parameters={},
            goal_statement="Goal",
            derived_from=(),
            version=1,
            created_by="test",
            proof=sample_proof,
        )

        assert hasattr(prompt, 'proof')
        assert prompt.proof is not None

    @pytest.mark.skipif(FunctionCrystal is None, reason="FunctionCrystal not available")
    def test_l5_requires_proof(self, sample_proof: GaloisWitnessedProof) -> None:
        """L5 (Function) requires proof field."""
        func = FunctionCrystal(
            id="f",
            qualified_name="test",
            file_path="test.py",
            line_range=(1, 1),
            signature="def test() -> None",
            proof=sample_proof,
        )

        assert hasattr(func, 'proof')
        assert func.proof is not None

    @pytest.mark.skipif(ReflectionCrystal is None, reason="ReflectionCrystal not available")
    def test_l6_proof_optional(self) -> None:
        """L6 (Reflection) has optional proof field."""
        refl = ReflectionCrystal(
            id="r",
            target_ids=(),
            reflection_type="synthesis",
            insight="Test",
            recommendations=(),
            derived_from=(),
            proof=None,
        )

        assert hasattr(refl, 'proof')
        assert refl.proof is None

    @pytest.mark.skipif(InterpretationCrystal is None, reason="InterpretationCrystal not available")
    def test_l7_proof_optional(self) -> None:
        """L7 (Interpretation) has optional proof field."""
        start = datetime.now(UTC)
        end = datetime.now(UTC)

        interp = InterpretationCrystal(
            id="i",
            artifact_pattern="*",
            time_range=(start, end),
            insight_type="trend",
            content="Test",
            confidence=0.5,
            supporting_ids=(),
            proof=None,
        )

        assert hasattr(interp, 'proof')
        assert interp.proof is None


# =============================================================================
# Derivation Chain Tests
# =============================================================================


class TestDerivationChains:
    """Tests for tracing derivation lineages across layers."""

    @pytest.mark.skipif(
        AxiomCrystal is None or ValueCrystal is None or PromptCrystal is None,
        reason="Required crystals not available"
    )
    def test_axiom_to_value_to_prompt(self, sample_proof: GaloisWitnessedProof) -> None:
        """Can trace L1 → L2 → L3 derivation."""
        # L1: Axiom
        axiom = AxiomCrystal(
            content="Tasteful > feature-complete",
            domain="design",
            tags=frozenset({"taste"}),
        )
        axiom_id = "axiom-taste"

        # L2: Value derived from axiom
        value = ValueCrystal(
            principle="Depth over breadth",
            axiom_ids=(axiom_id,),
            tags=frozenset({"curation"}),
        )
        value_id = "value-depth"

        # L3: Prompt derived from value
        prompt = PromptCrystal(
            template="Generate {artifact} with depth",
            parameters={"artifact": PromptParam(name="artifact", type="str")},
            goal_statement="Generate tasteful artifacts",
            derived_from=(value_id,),
            version=1,
            created_by="kent",
            proof=sample_proof,
        )

        # Trace lineage
        assert axiom_id in value.axiom_ids
        assert value_id in prompt.derived_from

    @pytest.mark.skipif(
        PromptCrystal is None or SpecCrystal is None or FunctionCrystal is None,
        reason="Required crystals not available"
    )
    def test_prompt_to_spec_to_function(self, sample_proof: GaloisWitnessedProof) -> None:
        """Can trace L3 → L4 → L5 derivation."""
        # L3: Prompt
        prompt_id = "prompt-001"

        # L4: Spec from prompt
        spec = SpecCrystal(
            spec_type="interface",
            language="python",
            content="def process() -> None: ...",
            ast_hash="hash123",
            dependencies=(),
            goal_prompt_id=prompt_id,
            proof=sample_proof,
        )
        spec_id = "spec-001"

        # L5: Function from spec
        func = FunctionCrystal(
            id="func-001",
            qualified_name="module.process",
            file_path="module.py",
            line_range=(1, 10),
            signature="def process() -> None",
            spec_id=spec_id,
            proof=sample_proof,
        )

        # Trace lineage
        assert spec.goal_prompt_id == prompt_id
        assert func.spec_id == spec_id
