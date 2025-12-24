"""
Tests for LLM-backed async analysis functions.

Tests cover:
- Successful LLM analysis (mocked service)
- Fallback to structural when ImportError
- Fallback to structural when LLM error
- Report types are correct
- File not found handling
- Self-analysis (meta-applicability)
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.operad.core import LawStatus, LawVerification
from agents.operad.domains.analysis import (
    BootstrapAnalysis,
    CategoricalReport,
    ContradictionType,
    DialecticalReport,
    EpistemicReport,
    EvidenceTier,
    FixedPointAnalysis,
    FullAnalysisReport,
    GenerativeReport,
    GroundingChain,
    LawExtraction,
    OperadGrammar,
    RegenerationTest,
    Tension,
    ToulminStructure,
    analyze_categorical_llm,
    analyze_dialectical_llm,
    analyze_epistemic_llm,
    analyze_full_llm,
    analyze_generative_llm,
    self_analyze_llm,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_categorical_report():
    """Mock CategoricalReport from LLM analysis."""
    return CategoricalReport(
        target="spec/test.md",
        laws_extracted=(
            LawExtraction(
                name="identity",
                equation="Id >> f = f",
                source="Section 2.1",
                tier=EvidenceTier.CATEGORICAL,
            ),
            LawExtraction(
                name="associativity",
                equation="(f >> g) >> h = f >> (g >> h)",
                source="Section 2.2",
                tier=EvidenceTier.CATEGORICAL,
            ),
        ),
        law_verifications=(
            LawVerification(
                law_name="identity",
                status=LawStatus.PASSED,
                message="Identity law holds",
            ),
            LawVerification(
                law_name="associativity",
                status=LawStatus.PASSED,
                message="Associativity law holds",
            ),
        ),
        fixed_point=FixedPointAnalysis(
            is_self_referential=True,
            fixed_point_description="Spec defines its own analysis framework",
            is_valid=True,
            implications=("Valid Lawvere fixed point",),
        ),
        summary="LLM analysis: 2/2 laws passed, valid fixed point",
    )


@pytest.fixture
def mock_epistemic_report():
    """Mock EpistemicReport from LLM analysis."""
    return EpistemicReport(
        target="spec/test.md",
        layer=4,
        toulmin=ToulminStructure(
            claim="The spec is grounded in category theory",
            grounds=("Explicit category axioms", "Composition laws"),
            warrant="Category theory provides rigorous foundation",
            backing="Established mathematical framework",
            qualifier="definitely",
            rebuttals=(),
            tier=EvidenceTier.CATEGORICAL,
        ),
        grounding=GroundingChain(
            steps=((1, "axioms", "defines"), (4, "spec", "implements")),
            terminates_at_axiom=True,
        ),
        bootstrap=BootstrapAnalysis(
            is_self_describing=True,
            layer_described=4,
            layer_occupied=4,
            is_valid=True,
            explanation="Spec describes its own layer validly",
        ),
        summary="LLM analysis: grounded in axioms, valid bootstrap",
    )


@pytest.fixture
def mock_dialectical_report():
    """Mock DialecticalReport from LLM analysis."""
    return DialecticalReport(
        target="spec/test.md",
        tensions=(
            Tension(
                thesis="Specs should be minimal",
                antithesis="Specs should be complete",
                classification=ContradictionType.PRODUCTIVE,
                synthesis="Minimal kernel with maximal regenerability",
                is_resolved=True,
            ),
        ),
        summary="LLM analysis: 1 productive tension resolved",
    )


@pytest.fixture
def mock_generative_report():
    """Mock GenerativeReport from LLM analysis."""
    return GenerativeReport(
        target="spec/test.md",
        grammar=OperadGrammar(
            primitives=frozenset({"agent", "operad", "composition"}),
            operations=frozenset({">>", "||", "**"}),
            laws=frozenset({"identity", "associativity"}),
        ),
        compression_ratio=0.25,
        regeneration=RegenerationTest(
            axioms_used=("identity", "associativity"),
            structures_regenerated=("sequential composition", "parallel composition"),
            missing_elements=(),
            passed=True,
        ),
        minimal_kernel=("identity", "associativity"),
        summary="LLM analysis: spec is compressed (0.25) and regenerable",
    )


@pytest.fixture
def mock_full_report(
    mock_categorical_report,
    mock_epistemic_report,
    mock_dialectical_report,
    mock_generative_report,
):
    """Mock FullAnalysisReport from LLM analysis."""
    return FullAnalysisReport(
        target="spec/test.md",
        categorical=mock_categorical_report,
        epistemic=mock_epistemic_report,
        dialectical=mock_dialectical_report,
        generative=mock_generative_report,
        synthesis="LLM synthesis: spec is valid, grounded, compressed, and regenerable",
    )


@pytest.fixture
def temp_spec_file(tmp_path):
    """Create a temporary spec file."""
    spec_file = tmp_path / "test_spec.md"
    spec_file.write_text(
        """
# Test Spec

## Category Laws

- Identity: Id >> f = f
- Associativity: (f >> g) >> h = f >> (g >> h)
"""
    )
    return str(spec_file)


# =============================================================================
# Categorical Analysis Tests
# =============================================================================


@pytest.mark.asyncio
async def test_categorical_llm_success(mock_categorical_report, temp_spec_file):
    """Test successful LLM-backed categorical analysis."""
    # Create mock service that returns our report
    mock_service = MagicMock()
    mock_service.analyze_categorical = AsyncMock(return_value=mock_categorical_report)

    # Mock the imports that happen inside the function
    mock_llm = MagicMock()

    with patch("services.analysis.AnalysisService", return_value=mock_service) as mock_service_cls, \
         patch("agents.k.soul.create_llm_client", return_value=mock_llm):

        result = await analyze_categorical_llm(temp_spec_file)

        # Verify service was instantiated with LLM
        mock_service_cls.assert_called_once_with(mock_llm)

        # Verify service method was called
        mock_service.analyze_categorical.assert_called_once_with(temp_spec_file)

        # Verify result is correct type and content
        assert isinstance(result, CategoricalReport)
        assert result.target == "spec/test.md"
        assert result.laws_passed == 2
        assert result.laws_total == 2
        assert not result.has_violations
        assert result.fixed_point is not None
        assert result.fixed_point.is_valid


@pytest.mark.asyncio
async def test_categorical_llm_import_error_fallback(temp_spec_file):
    """Test fallback to structural when AnalysisService import fails."""
    # Simulate ImportError by making the import fail
    with patch.dict(sys.modules, {"services.analysis": None}):
        result = await analyze_categorical_llm(temp_spec_file)

        # Should fall back to structural analysis
        assert isinstance(result, CategoricalReport)
        assert result.target == temp_spec_file
        # Structural analysis returns basic category axioms
        assert len(result.laws_extracted) == 2
        assert result.laws_extracted[0].name == "identity"
        assert result.laws_extracted[1].name == "associativity"
        assert "structural" in result.summary.lower() or "construction" in result.summary.lower()


@pytest.mark.asyncio
async def test_categorical_llm_error_fallback(temp_spec_file):
    """Test fallback to structural when LLM raises error."""
    mock_service = MagicMock()
    mock_service.analyze_categorical = AsyncMock(
        side_effect=ValueError("LLM API error")
    )
    mock_llm = MagicMock()

    with patch("services.analysis.AnalysisService", return_value=mock_service), \
         patch("agents.k.soul.create_llm_client", return_value=mock_llm):

        result = await analyze_categorical_llm(temp_spec_file)

        # Should fall back to structural with error message
        assert isinstance(result, CategoricalReport)
        assert "LLM error" in result.summary
        assert "fell back to structural" in result.summary


@pytest.mark.asyncio
async def test_categorical_llm_file_not_found():
    """Test categorical analysis with non-existent file."""
    nonexistent = "/path/to/nonexistent/file.md"

    # The service itself handles file not found, so we need to mock it returning an error report
    error_report = CategoricalReport(
        target=nonexistent,
        laws_extracted=(),
        law_verifications=(
            LawVerification(
                law_name="file_exists",
                status=LawStatus.FAILED,
                message=f"File not found: {nonexistent}",
            ),
        ),
        fixed_point=None,
        summary=f"Error: Spec not found: {nonexistent}",
    )

    mock_service = MagicMock()
    mock_service.analyze_categorical = AsyncMock(return_value=error_report)
    mock_llm = MagicMock()

    with patch("services.analysis.AnalysisService", return_value=mock_service), \
         patch("agents.k.soul.create_llm_client", return_value=mock_llm):

        result = await analyze_categorical_llm(nonexistent)

        assert isinstance(result, CategoricalReport)
        assert result.target == nonexistent
        assert len(result.law_verifications) == 1
        assert result.law_verifications[0].status == LawStatus.FAILED
        assert "not found" in result.law_verifications[0].message.lower()


# =============================================================================
# Epistemic Analysis Tests
# =============================================================================


@pytest.mark.asyncio
async def test_epistemic_llm_success(mock_epistemic_report, temp_spec_file):
    """Test successful LLM-backed epistemic analysis."""
    mock_service = MagicMock()
    mock_service.analyze_epistemic = AsyncMock(return_value=mock_epistemic_report)
    mock_llm = MagicMock()

    with patch("services.analysis.AnalysisService", return_value=mock_service), \
         patch("agents.k.soul.create_llm_client", return_value=mock_llm):

        result = await analyze_epistemic_llm(temp_spec_file)

        mock_service.analyze_epistemic.assert_called_once_with(temp_spec_file)

        assert isinstance(result, EpistemicReport)
        assert result.target == "spec/test.md"
        assert result.is_grounded
        assert result.has_valid_bootstrap
        assert result.layer == 4


@pytest.mark.asyncio
async def test_epistemic_llm_import_error_fallback(temp_spec_file):
    """Test epistemic fallback to structural on ImportError."""
    with patch.dict(sys.modules, {"services.analysis": None}):
        result = await analyze_epistemic_llm(temp_spec_file)

        assert isinstance(result, EpistemicReport)
        assert result.layer == 4  # Assumed L4
        assert "structural" in result.summary.lower()


@pytest.mark.asyncio
async def test_epistemic_llm_error_fallback(temp_spec_file):
    """Test epistemic fallback to structural on LLM error."""
    mock_service = MagicMock()
    mock_service.analyze_epistemic = AsyncMock(side_effect=RuntimeError("API timeout"))
    mock_llm = MagicMock()

    with patch("services.analysis.AnalysisService", return_value=mock_service), \
         patch("agents.k.soul.create_llm_client", return_value=mock_llm):

        result = await analyze_epistemic_llm(temp_spec_file)

        assert isinstance(result, EpistemicReport)
        assert "LLM error" in result.summary
        assert "API timeout" in result.summary


# =============================================================================
# Dialectical Analysis Tests
# =============================================================================


@pytest.mark.asyncio
async def test_dialectical_llm_success(mock_dialectical_report, temp_spec_file):
    """Test successful LLM-backed dialectical analysis."""
    mock_service = MagicMock()
    mock_service.analyze_dialectical = AsyncMock(return_value=mock_dialectical_report)
    mock_llm = MagicMock()

    with patch("services.analysis.AnalysisService", return_value=mock_service), \
         patch("agents.k.soul.create_llm_client", return_value=mock_llm):

        result = await analyze_dialectical_llm(temp_spec_file)

        mock_service.analyze_dialectical.assert_called_once_with(temp_spec_file)

        assert isinstance(result, DialecticalReport)
        assert result.target == "spec/test.md"
        assert len(result.tensions) == 1
        assert result.resolved_count == 1
        assert result.problematic_count == 0


@pytest.mark.asyncio
async def test_dialectical_llm_import_error_fallback(temp_spec_file):
    """Test dialectical fallback to structural on ImportError."""
    with patch.dict(sys.modules, {"services.analysis": None}):
        result = await analyze_dialectical_llm(temp_spec_file)

        assert isinstance(result, DialecticalReport)
        # Structural mode cannot detect tensions
        assert len(result.tensions) == 0
        assert "structural" in result.summary.lower()


@pytest.mark.asyncio
async def test_dialectical_llm_error_fallback(temp_spec_file):
    """Test dialectical fallback to structural on LLM error."""
    mock_service = MagicMock()
    mock_service.analyze_dialectical = AsyncMock(
        side_effect=Exception("Rate limit exceeded")
    )
    mock_llm = MagicMock()

    with patch("services.analysis.AnalysisService", return_value=mock_service), \
         patch("agents.k.soul.create_llm_client", return_value=mock_llm):

        result = await analyze_dialectical_llm(temp_spec_file)

        assert isinstance(result, DialecticalReport)
        assert "LLM error" in result.summary
        assert "Rate limit" in result.summary


# =============================================================================
# Generative Analysis Tests
# =============================================================================


@pytest.mark.asyncio
async def test_generative_llm_success(mock_generative_report, temp_spec_file):
    """Test successful LLM-backed generative analysis."""
    mock_service = MagicMock()
    mock_service.analyze_generative = AsyncMock(return_value=mock_generative_report)
    mock_llm = MagicMock()

    with patch("services.analysis.AnalysisService", return_value=mock_service), \
         patch("agents.k.soul.create_llm_client", return_value=mock_llm):

        result = await analyze_generative_llm(temp_spec_file)

        mock_service.analyze_generative.assert_called_once_with(temp_spec_file)

        assert isinstance(result, GenerativeReport)
        assert result.target == "spec/test.md"
        assert result.is_compressed
        assert result.is_regenerable
        assert len(result.minimal_kernel) == 2


@pytest.mark.asyncio
async def test_generative_llm_import_error_fallback(temp_spec_file):
    """Test generative fallback to structural on ImportError."""
    with patch.dict(sys.modules, {"services.analysis": None}):
        result = await analyze_generative_llm(temp_spec_file)

        assert isinstance(result, GenerativeReport)
        # Structural mode computes compression but cannot test regenerability
        assert not result.is_regenerable
        assert "structural" in result.summary.lower()


@pytest.mark.asyncio
async def test_generative_llm_error_fallback(temp_spec_file):
    """Test generative fallback to structural on LLM error."""
    mock_service = MagicMock()
    mock_service.analyze_generative = AsyncMock(
        side_effect=KeyError("Missing analysis key")
    )
    mock_llm = MagicMock()

    with patch("services.analysis.AnalysisService", return_value=mock_service), \
         patch("agents.k.soul.create_llm_client", return_value=mock_llm):

        result = await analyze_generative_llm(temp_spec_file)

        assert isinstance(result, GenerativeReport)
        assert "LLM error" in result.summary
        assert "Missing analysis key" in result.summary


# =============================================================================
# Full Analysis Tests
# =============================================================================


@pytest.mark.asyncio
async def test_full_llm_success(mock_full_report, temp_spec_file):
    """Test successful LLM-backed full four-mode analysis."""
    mock_service = MagicMock()
    mock_service.analyze_full = AsyncMock(return_value=mock_full_report)
    mock_llm = MagicMock()

    with patch("services.analysis.AnalysisService", return_value=mock_service), \
         patch("agents.k.soul.create_llm_client", return_value=mock_llm):

        result = await analyze_full_llm(temp_spec_file)

        mock_service.analyze_full.assert_called_once_with(temp_spec_file)

        assert isinstance(result, FullAnalysisReport)
        assert result.target == "spec/test.md"
        assert isinstance(result.categorical, CategoricalReport)
        assert isinstance(result.epistemic, EpistemicReport)
        assert isinstance(result.dialectical, DialecticalReport)
        assert isinstance(result.generative, GenerativeReport)
        assert result.is_valid


@pytest.mark.asyncio
async def test_full_llm_import_error_fallback(temp_spec_file):
    """Test full analysis fallback to structural on ImportError."""
    with patch.dict(sys.modules, {"services.analysis": None}):
        result = await analyze_full_llm(temp_spec_file)

        assert isinstance(result, FullAnalysisReport)
        assert isinstance(result.categorical, CategoricalReport)
        assert isinstance(result.epistemic, EpistemicReport)
        assert isinstance(result.dialectical, DialecticalReport)
        assert isinstance(result.generative, GenerativeReport)
        assert "structural" in result.synthesis.lower()


@pytest.mark.asyncio
async def test_full_llm_error_fallback(temp_spec_file):
    """Test full analysis fallback to structural on LLM error."""
    mock_service = MagicMock()
    mock_service.analyze_full = AsyncMock(side_effect=ConnectionError("Network error"))
    mock_llm = MagicMock()

    with patch("services.analysis.AnalysisService", return_value=mock_service), \
         patch("agents.k.soul.create_llm_client", return_value=mock_llm):

        result = await analyze_full_llm(temp_spec_file)

        assert isinstance(result, FullAnalysisReport)
        assert "LLM error" in result.synthesis
        assert "Network error" in result.synthesis
        assert "fell back to structural" in result.synthesis


@pytest.mark.asyncio
async def test_full_llm_validation(temp_spec_file):
    """Test is_valid property on FullAnalysisReport."""
    # Create a report with violations
    invalid_categorical = CategoricalReport(
        target="spec/test.md",
        laws_extracted=(),
        law_verifications=(
            LawVerification(
                law_name="identity",
                status=LawStatus.FAILED,
                message="Identity law violated",
            ),
        ),
        fixed_point=None,
        summary="Has violations",
    )

    invalid_report = FullAnalysisReport(
        target="spec/test.md",
        categorical=invalid_categorical,
        epistemic=EpistemicReport(
            target="spec/test.md",
            layer=4,
            toulmin=ToulminStructure(
                claim="", grounds=(), warrant="", backing="", qualifier="", rebuttals=(), tier=EvidenceTier.EMPIRICAL
            ),
            grounding=GroundingChain(steps=(), terminates_at_axiom=True),
            bootstrap=None,
            summary="",
        ),
        dialectical=DialecticalReport(target="spec/test.md", tensions=(), summary=""),
        generative=GenerativeReport(
            target="spec/test.md",
            grammar=OperadGrammar(frozenset(), frozenset(), frozenset()),
            compression_ratio=0.5,
            regeneration=RegenerationTest((), (), (), True),
            minimal_kernel=(),
            summary="",
        ),
        synthesis="Invalid",
    )

    mock_service = MagicMock()
    mock_service.analyze_full = AsyncMock(return_value=invalid_report)
    mock_llm = MagicMock()

    with patch("services.analysis.AnalysisService", return_value=mock_service), \
         patch("agents.k.soul.create_llm_client", return_value=mock_llm):

        result = await analyze_full_llm(temp_spec_file)

        assert not result.is_valid  # Should be invalid due to violations


# =============================================================================
# Self-Analysis Tests (Meta-Applicability)
# =============================================================================


@pytest.mark.asyncio
async def test_self_analyze_llm(mock_full_report):
    """Test self-analysis (Analysis Operad analyzing itself)."""
    # Update target to be the analysis operad spec
    self_report = FullAnalysisReport(
        target="spec/theory/analysis-operad.md",
        categorical=mock_full_report.categorical,
        epistemic=mock_full_report.epistemic,
        dialectical=mock_full_report.dialectical,
        generative=mock_full_report.generative,
        synthesis="Self-analysis successful: Analysis Operad is valid",
    )

    mock_service = MagicMock()
    mock_service.analyze_full = AsyncMock(return_value=self_report)
    mock_llm = MagicMock()

    with patch("services.analysis.AnalysisService", return_value=mock_service), \
         patch("agents.k.soul.create_llm_client", return_value=mock_llm):

        result = await self_analyze_llm()

        # Should call analyze_full with the analysis operad spec
        mock_service.analyze_full.assert_called_once_with(
            "spec/theory/analysis-operad.md"
        )

        assert isinstance(result, FullAnalysisReport)
        assert result.target == "spec/theory/analysis-operad.md"


@pytest.mark.asyncio
async def test_self_analyze_llm_fallback():
    """Test self-analysis fallback to structural on ImportError."""
    with patch.dict(sys.modules, {"services.analysis": None}):
        result = await self_analyze_llm()

        assert isinstance(result, FullAnalysisReport)
        assert result.target == "spec/theory/analysis-operad.md"
        # Should use structural fallback
        assert "structural" in result.synthesis.lower() or "construction" in result.synthesis.lower()


# =============================================================================
# Report Type Property Tests
# =============================================================================


def test_categorical_report_properties():
    """Test CategoricalReport computed properties."""
    report = CategoricalReport(
        target="test.md",
        laws_extracted=(),
        law_verifications=(
            LawVerification("law1", LawStatus.PASSED, "ok"),
            LawVerification("law2", LawStatus.FAILED, "fail"),
            LawVerification("law3", LawStatus.PASSED, "ok"),
        ),
        fixed_point=None,
        summary="",
    )

    assert report.laws_passed == 2
    assert report.laws_total == 3
    assert report.has_violations


def test_epistemic_report_properties():
    """Test EpistemicReport computed properties."""
    report = EpistemicReport(
        target="test.md",
        layer=4,
        toulmin=ToulminStructure(
            claim="", grounds=(), warrant="", backing="", qualifier="", rebuttals=(), tier=EvidenceTier.CATEGORICAL
        ),
        grounding=GroundingChain(steps=(), terminates_at_axiom=True),
        bootstrap=BootstrapAnalysis(
            is_self_describing=True,
            layer_described=4,
            layer_occupied=4,
            is_valid=True,
            explanation="",
        ),
        summary="",
    )

    assert report.is_grounded
    assert report.has_valid_bootstrap


def test_dialectical_report_properties():
    """Test DialecticalReport computed properties."""
    report = DialecticalReport(
        target="test.md",
        tensions=(
            Tension("t1", "a1", ContradictionType.PRODUCTIVE, "s1", True),
            Tension("t2", "a2", ContradictionType.PROBLEMATIC, None, False),
            Tension("t3", "a3", ContradictionType.PARACONSISTENT, "s3", True),
        ),
        summary="",
    )

    assert report.resolved_count == 2
    assert report.problematic_count == 1
    assert report.paraconsistent_count == 1


def test_generative_report_properties():
    """Test GenerativeReport computed properties."""
    report = GenerativeReport(
        target="test.md",
        grammar=OperadGrammar(frozenset(), frozenset(), frozenset()),
        compression_ratio=0.3,
        regeneration=RegenerationTest((), (), (), True),
        minimal_kernel=(),
        summary="",
    )

    assert report.is_compressed
    assert report.is_regenerable

    report_uncompressed = GenerativeReport(
        target="test.md",
        grammar=OperadGrammar(frozenset(), frozenset(), frozenset()),
        compression_ratio=1.5,
        regeneration=RegenerationTest((), (), ("missing",), False),
        minimal_kernel=(),
        summary="",
    )

    assert not report_uncompressed.is_compressed
    assert not report_uncompressed.is_regenerable


def test_full_report_is_valid():
    """Test FullAnalysisReport.is_valid property."""
    # Valid report
    valid_report = FullAnalysisReport(
        target="test.md",
        categorical=CategoricalReport(
            "test.md",
            (),
            (LawVerification("law", LawStatus.PASSED, "ok"),),
            None,
            "",
        ),
        epistemic=EpistemicReport(
            "test.md",
            4,
            ToulminStructure("", (), "", "", "", (), EvidenceTier.CATEGORICAL),
            GroundingChain((), True),
            None,
            "",
        ),
        dialectical=DialecticalReport("test.md", (), ""),
        generative=GenerativeReport(
            "test.md",
            OperadGrammar(frozenset(), frozenset(), frozenset()),
            0.5,
            RegenerationTest((), (), (), True),
            (),
            "",
        ),
        synthesis="Valid",
    )

    assert valid_report.is_valid

    # Invalid: has violations
    invalid_violations = FullAnalysisReport(
        target="test.md",
        categorical=CategoricalReport(
            "test.md",
            (),
            (LawVerification("law", LawStatus.FAILED, "fail"),),
            None,
            "",
        ),
        epistemic=valid_report.epistemic,
        dialectical=valid_report.dialectical,
        generative=valid_report.generative,
        synthesis="Invalid",
    )

    assert not invalid_violations.is_valid

    # Invalid: not grounded
    invalid_grounding = FullAnalysisReport(
        target="test.md",
        categorical=valid_report.categorical,
        epistemic=EpistemicReport(
            "test.md",
            4,
            ToulminStructure("", (), "", "", "", (), EvidenceTier.CATEGORICAL),
            GroundingChain((), False),  # Not grounded
            None,
            "",
        ),
        dialectical=valid_report.dialectical,
        generative=valid_report.generative,
        synthesis="Invalid",
    )

    assert not invalid_grounding.is_valid

    # Invalid: problematic tensions
    invalid_dialectical = FullAnalysisReport(
        target="test.md",
        categorical=valid_report.categorical,
        epistemic=valid_report.epistemic,
        dialectical=DialecticalReport(
            "test.md",
            (Tension("t", "a", ContradictionType.PROBLEMATIC, None, False),),
            "",
        ),
        generative=valid_report.generative,
        synthesis="Invalid",
    )

    assert not invalid_dialectical.is_valid

    # Invalid: not regenerable
    invalid_generative = FullAnalysisReport(
        target="test.md",
        categorical=valid_report.categorical,
        epistemic=valid_report.epistemic,
        dialectical=valid_report.dialectical,
        generative=GenerativeReport(
            "test.md",
            OperadGrammar(frozenset(), frozenset(), frozenset()),
            0.5,
            RegenerationTest((), (), ("missing",), False),  # Not regenerable
            (),
            "",
        ),
        synthesis="Invalid",
    )

    assert not invalid_generative.is_valid
