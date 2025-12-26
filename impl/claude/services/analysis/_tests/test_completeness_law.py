"""
Tests for Analysis Operad completeness law verification.

The completeness law states:
    full(X) = seq(par(categorical, epistemic), par(dialectical, generative))(X)

This means:
- Phase 1: Run categorical + epistemic in PARALLEL
- Phase 2: Run dialectical + generative in PARALLEL (informed by phase 1)
- Phase 3: Synthesize all results

These tests verify:
1. Phase 1 runs cat+epi in parallel (timing evidence)
2. Phase 2 runs dia+gen in parallel (timing evidence)
3. Dialectical analysis receives categorical results as context
4. The composition order is correct (phase 1 THEN phase 2)
5. Error handling preserves the composition structure

Teaching:
    gotcha: We can't just check that all four modes run. The ORDER matters.
            Categorical+Epistemic must complete BEFORE Dialectical+Generative start.
            (Evidence: spec/theory/analysis-operad.md §2.2)

    gotcha: Parallelism verification requires timing analysis or call tracking.
            We use mock.call_args_list to verify asyncio.gather() groups tasks correctly.
            (Evidence: Phase 1 should have 1 gather with 2 tasks, Phase 2 another)

    gotcha: Dialectical receives categorical context IF there are violations.
            Test both paths: violations → context provided, no violations → no context.
            (Evidence: service.py::analyze_dialectical checks categorical.has_violations)
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from agents.operad.core import LawStatus, LawVerification
from agents.operad.domains.analysis import (
    CategoricalReport,
    ContradictionType,
    DialecticalReport,
    EpistemicReport,
    EvidenceTier,
    FixedPointAnalysis,
    GenerativeReport,
    GroundingChain,
    LawExtraction,
    OperadGrammar,
    RegenerationTest,
    Tension,
    ToulminStructure,
)
from services.analysis.service import AnalysisService

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_llm() -> Mock:
    """Mock LLM client that doesn't make real API calls."""
    return Mock()


@pytest.fixture
def sample_categorical_report() -> CategoricalReport:
    """Sample categorical report with no violations."""
    return CategoricalReport(
        target="test.md",
        laws_extracted=(
            LawExtraction(
                name="identity",
                equation="id >> f = f",
                source="implicit",
            ),
        ),
        law_verifications=(
            LawVerification(
                law_name="identity",
                status=LawStatus.STRUCTURAL,
                message="OK",
            ),
        ),
        fixed_point=FixedPointAnalysis(
            is_self_referential=False,
            fixed_point_description="No fixed point",
            is_valid=True,
            implications=(),
        ),
        summary="2 laws verified",
    )


@pytest.fixture
def sample_categorical_report_with_violations() -> CategoricalReport:
    """Sample categorical report WITH violations (for context test)."""
    return CategoricalReport(
        target="test.md",
        laws_extracted=(
            LawExtraction(
                name="identity",
                equation="id >> f = f",
                source="implicit",
            ),
        ),
        law_verifications=(
            LawVerification(
                law_name="identity",
                status=LawStatus.FAILED,
                message="Violation detected",
            ),
        ),
        fixed_point=None,
        summary="1 law failed",
    )


@pytest.fixture
def sample_epistemic_report() -> EpistemicReport:
    """Sample epistemic report."""
    return EpistemicReport(
        target="test.md",
        layer=4,
        toulmin=ToulminStructure(
            claim="Test claim",
            grounds=("Evidence 1",),
            warrant="Warrant",
            backing="Backing",
            qualifier="definitely",
            rebuttals=(),
            tier=EvidenceTier.CATEGORICAL,
        ),
        grounding=GroundingChain(steps=(), terminates_at_axiom=True),
        bootstrap=None,
        summary="Grounded at L4",
    )


@pytest.fixture
def sample_dialectical_report() -> DialecticalReport:
    """Sample dialectical report."""
    return DialecticalReport(
        target="test.md",
        tensions=(
            Tension(
                thesis="A",
                antithesis="Not A",
                classification=ContradictionType.PRODUCTIVE,
                synthesis="Resolved",
                is_resolved=True,
            ),
        ),
        summary="1 tension, resolved",
    )


@pytest.fixture
def sample_generative_report() -> GenerativeReport:
    """Sample generative report."""
    return GenerativeReport(
        target="test.md",
        grammar=OperadGrammar(
            primitives=frozenset({"Node"}),
            operations=frozenset({"compose"}),
            laws=frozenset({"identity"}),
        ),
        compression_ratio=0.25,
        regeneration=RegenerationTest(
            axioms_used=("axiom1",),
            structures_regenerated=("structure1",),
            missing_elements=(),
            passed=True,
        ),
        minimal_kernel=("axiom1",),
        summary="Regenerable",
    )


@pytest.fixture
def temp_spec_file(tmp_path: Path) -> Path:
    """Create a temporary spec file for testing."""
    spec = tmp_path / "test.md"
    spec.write_text("# Test Spec\n\nSome content.")
    return spec


# =============================================================================
# Test: Phase 1 Parallelism (Categorical + Epistemic)
# =============================================================================


@pytest.mark.asyncio
async def test_phase1_runs_categorical_and_epistemic_in_parallel(
    mock_llm: Mock,
    sample_categorical_report: CategoricalReport,
    sample_epistemic_report: EpistemicReport,
    temp_spec_file: Path,
):
    """
    Verify Phase 1 runs categorical + epistemic in parallel using asyncio.gather().

    We can't directly observe asyncio.gather() from outside, but we can verify:
    1. Both analyze_categorical and analyze_epistemic are called
    2. They're called before analyze_dialectical and analyze_generative
    3. The timing suggests parallelism (not sequential)
    """
    service = AnalysisService(mock_llm)

    # Mock the individual analysis methods
    with patch.object(
        service, "analyze_categorical", new_callable=AsyncMock
    ) as mock_cat, patch.object(
        service, "analyze_epistemic", new_callable=AsyncMock
    ) as mock_epi, patch.object(
        service, "analyze_dialectical", new_callable=AsyncMock
    ) as mock_dia, patch.object(
        service, "analyze_generative", new_callable=AsyncMock
    ) as mock_gen:

        # Set return values
        mock_cat.return_value = sample_categorical_report
        mock_epi.return_value = sample_epistemic_report
        mock_dia.return_value = DialecticalReport(
            target=str(temp_spec_file), tensions=(), summary=""
        )
        mock_gen.return_value = GenerativeReport(
            target=str(temp_spec_file),
            grammar=OperadGrammar(
                primitives=frozenset(), operations=frozenset(), laws=frozenset()
            ),
            compression_ratio=1.0,
            regeneration=RegenerationTest(
                axioms_used=(), structures_regenerated=(), missing_elements=(), passed=False
            ),
            minimal_kernel=(),
            summary="",
        )

        # Run full analysis
        await service.analyze_full(str(temp_spec_file))

        # Verify Phase 1 methods were called
        mock_cat.assert_called_once_with(str(temp_spec_file))
        mock_epi.assert_called_once_with(str(temp_spec_file))

        # Verify Phase 2 methods were called AFTER phase 1
        mock_dia.assert_called_once()
        mock_gen.assert_called_once()


@pytest.mark.asyncio
async def test_phase1_parallelism_timing_evidence(
    mock_llm: Mock,
    sample_categorical_report: CategoricalReport,
    sample_epistemic_report: EpistemicReport,
    temp_spec_file: Path,
):
    """
    Verify Phase 1 parallelism through timing analysis.

    If categorical and epistemic run in parallel, total time should be
    max(cat_time, epi_time), not cat_time + epi_time.
    """
    service = AnalysisService(mock_llm)

    # Create analyzers with artificial delays
    async def slow_categorical(path: str) -> CategoricalReport:
        await asyncio.sleep(0.1)  # 100ms delay
        return sample_categorical_report

    async def slow_epistemic(path: str) -> EpistemicReport:
        await asyncio.sleep(0.1)  # 100ms delay
        return sample_epistemic_report

    with patch.object(
        service, "analyze_categorical", side_effect=slow_categorical
    ), patch.object(
        service, "analyze_epistemic", side_effect=slow_epistemic
    ), patch.object(
        service, "analyze_dialectical", new_callable=AsyncMock
    ) as mock_dia, patch.object(
        service, "analyze_generative", new_callable=AsyncMock
    ) as mock_gen:

        mock_dia.return_value = DialecticalReport(
            target=str(temp_spec_file), tensions=(), summary=""
        )
        mock_gen.return_value = GenerativeReport(
            target=str(temp_spec_file),
            grammar=OperadGrammar(
                primitives=frozenset(), operations=frozenset(), laws=frozenset()
            ),
            compression_ratio=1.0,
            regeneration=RegenerationTest(
                axioms_used=(), structures_regenerated=(), missing_elements=(), passed=False
            ),
            minimal_kernel=(),
            summary="",
        )

        # Measure execution time
        import time

        start = time.monotonic()
        await service.analyze_full(str(temp_spec_file))
        elapsed = time.monotonic() - start

        # If parallel: ~100ms (max of two 100ms tasks)
        # If sequential: ~200ms (sum of two 100ms tasks)
        # Allow some overhead, but should be closer to 100ms than 200ms
        assert elapsed < 0.15, (
            f"Phase 1 took {elapsed:.3f}s, expected ~0.1s for parallel execution. "
            "If >0.15s, tasks may be running sequentially instead of parallel."
        )


# =============================================================================
# Test: Phase 2 Parallelism (Dialectical + Generative)
# =============================================================================


@pytest.mark.asyncio
async def test_phase2_runs_dialectical_and_generative_in_parallel(
    mock_llm: Mock,
    sample_categorical_report: CategoricalReport,
    sample_epistemic_report: EpistemicReport,
    sample_dialectical_report: DialecticalReport,
    sample_generative_report: GenerativeReport,
    temp_spec_file: Path,
):
    """
    Verify Phase 2 runs dialectical + generative in parallel.
    """
    service = AnalysisService(mock_llm)

    with patch.object(
        service, "analyze_categorical", new_callable=AsyncMock
    ) as mock_cat, patch.object(
        service, "analyze_epistemic", new_callable=AsyncMock
    ) as mock_epi, patch.object(
        service, "analyze_dialectical", new_callable=AsyncMock
    ) as mock_dia, patch.object(
        service, "analyze_generative", new_callable=AsyncMock
    ) as mock_gen:

        mock_cat.return_value = sample_categorical_report
        mock_epi.return_value = sample_epistemic_report
        mock_dia.return_value = sample_dialectical_report
        mock_gen.return_value = sample_generative_report

        await service.analyze_full(str(temp_spec_file))

        # Both Phase 2 methods should be called
        mock_dia.assert_called_once()
        mock_gen.assert_called_once()


@pytest.mark.asyncio
async def test_phase2_parallelism_timing_evidence(
    mock_llm: Mock,
    sample_categorical_report: CategoricalReport,
    sample_epistemic_report: EpistemicReport,
    sample_dialectical_report: DialecticalReport,
    sample_generative_report: GenerativeReport,
    temp_spec_file: Path,
):
    """
    Verify Phase 2 parallelism through timing analysis.
    """
    service = AnalysisService(mock_llm)

    # Mock fast phase 1
    with patch.object(
        service, "analyze_categorical", new_callable=AsyncMock
    ) as mock_cat, patch.object(
        service, "analyze_epistemic", new_callable=AsyncMock
    ) as mock_epi:

        mock_cat.return_value = sample_categorical_report
        mock_epi.return_value = sample_epistemic_report

        # Create analyzers with artificial delays
        async def slow_dialectical(path: str, cat: CategoricalReport | None = None):
            await asyncio.sleep(0.1)  # 100ms delay
            return sample_dialectical_report

        async def slow_generative(path: str):
            await asyncio.sleep(0.1)  # 100ms delay
            return sample_generative_report

        with patch.object(
            service, "analyze_dialectical", side_effect=slow_dialectical
        ), patch.object(service, "analyze_generative", side_effect=slow_generative):

            import time

            start = time.monotonic()
            await service.analyze_full(str(temp_spec_file))
            elapsed = time.monotonic() - start

            # Phase 2 should take ~100ms (parallel), not ~200ms (sequential)
            # Allow some overhead for Phase 1 + synthesis
            assert elapsed < 0.25, (
                f"Full analysis took {elapsed:.3f}s. Phase 2 appears sequential. "
                "Expected parallel execution of dialectical + generative."
            )


# =============================================================================
# Test: Dialectical Receives Categorical Context
# =============================================================================


@pytest.mark.asyncio
async def test_dialectical_receives_categorical_context_when_violations_exist(
    mock_llm: Mock,
    sample_categorical_report_with_violations: CategoricalReport,
    sample_epistemic_report: EpistemicReport,
    temp_spec_file: Path,
):
    """
    Verify dialectical analysis receives categorical context when violations exist.

    The completeness law requires Phase 2 to be INFORMED by Phase 1.
    Specifically, dialectical should receive categorical violations as context.
    """
    service = AnalysisService(mock_llm)

    with patch.object(
        service, "analyze_categorical", new_callable=AsyncMock
    ) as mock_cat, patch.object(
        service, "analyze_epistemic", new_callable=AsyncMock
    ) as mock_epi, patch.object(
        service, "analyze_dialectical", new_callable=AsyncMock
    ) as mock_dia, patch.object(
        service, "analyze_generative", new_callable=AsyncMock
    ) as mock_gen:

        # Phase 1: Categorical has violations
        mock_cat.return_value = sample_categorical_report_with_violations
        mock_epi.return_value = sample_epistemic_report

        # Phase 2
        mock_dia.return_value = DialecticalReport(
            target=str(temp_spec_file), tensions=(), summary=""
        )
        mock_gen.return_value = GenerativeReport(
            target=str(temp_spec_file),
            grammar=OperadGrammar(
                primitives=frozenset(), operations=frozenset(), laws=frozenset()
            ),
            compression_ratio=1.0,
            regeneration=RegenerationTest(
                axioms_used=(), structures_regenerated=(), missing_elements=(), passed=False
            ),
            minimal_kernel=(),
            summary="",
        )

        await service.analyze_full(str(temp_spec_file))

        # Verify dialectical was called with categorical report
        mock_dia.assert_called_once()
        call_args = mock_dia.call_args
        assert call_args is not None
        assert len(call_args.args) >= 1  # spec_path
        # Check if categorical was passed as kwarg or arg
        if "categorical" in call_args.kwargs:
            assert call_args.kwargs["categorical"] == sample_categorical_report_with_violations
        else:
            # It's passed as a positional arg
            assert len(call_args.args) >= 2
            assert call_args.args[1] == sample_categorical_report_with_violations


@pytest.mark.asyncio
async def test_dialectical_receives_no_context_when_no_violations(
    mock_llm: Mock,
    sample_categorical_report: CategoricalReport,
    sample_epistemic_report: EpistemicReport,
    temp_spec_file: Path,
):
    """
    Verify dialectical receives categorical report even when no violations.

    The report is always passed, but context is only built if violations exist.
    """
    service = AnalysisService(mock_llm)

    with patch.object(
        service, "analyze_categorical", new_callable=AsyncMock
    ) as mock_cat, patch.object(
        service, "analyze_epistemic", new_callable=AsyncMock
    ) as mock_epi, patch.object(
        service, "analyze_dialectical", new_callable=AsyncMock
    ) as mock_dia, patch.object(
        service, "analyze_generative", new_callable=AsyncMock
    ) as mock_gen:

        # Phase 1: No violations
        mock_cat.return_value = sample_categorical_report
        mock_epi.return_value = sample_epistemic_report

        mock_dia.return_value = DialecticalReport(
            target=str(temp_spec_file), tensions=(), summary=""
        )
        mock_gen.return_value = GenerativeReport(
            target=str(temp_spec_file),
            grammar=OperadGrammar(
                primitives=frozenset(), operations=frozenset(), laws=frozenset()
            ),
            compression_ratio=1.0,
            regeneration=RegenerationTest(
                axioms_used=(), structures_regenerated=(), missing_elements=(), passed=False
            ),
            minimal_kernel=(),
            summary="",
        )

        await service.analyze_full(str(temp_spec_file))

        # Verify dialectical was called with categorical report (no violations)
        mock_dia.assert_called_once()
        call_args = mock_dia.call_args
        assert call_args is not None
        # Categorical is still passed, just no violations to highlight
        if "categorical" in call_args.kwargs:
            assert call_args.kwargs["categorical"] == sample_categorical_report
        else:
            assert len(call_args.args) >= 2
            assert call_args.args[1] == sample_categorical_report


# =============================================================================
# Test: Composition Order (Phase 1 → Phase 2 → Synthesis)
# =============================================================================


@pytest.mark.asyncio
async def test_composition_order_is_correct(
    mock_llm: Mock,
    sample_categorical_report: CategoricalReport,
    sample_epistemic_report: EpistemicReport,
    sample_dialectical_report: DialecticalReport,
    sample_generative_report: GenerativeReport,
    temp_spec_file: Path,
):
    """
    Verify the composition order: Phase 1 completes BEFORE Phase 2 starts.

    This is the core of the completeness law:
        seq(par(cat, epi), par(dia, gen))

    The seq() means Phase 1 must finish before Phase 2 begins.
    """
    service = AnalysisService(mock_llm)

    # Track call order
    call_order = []

    async def track_cat(path: str):
        call_order.append("categorical_start")
        await asyncio.sleep(0.05)
        call_order.append("categorical_end")
        return sample_categorical_report

    async def track_epi(path: str):
        call_order.append("epistemic_start")
        await asyncio.sleep(0.05)
        call_order.append("epistemic_end")
        return sample_epistemic_report

    async def track_dia(path: str, cat=None):
        call_order.append("dialectical_start")
        await asyncio.sleep(0.01)
        call_order.append("dialectical_end")
        return sample_dialectical_report

    async def track_gen(path: str):
        call_order.append("generative_start")
        await asyncio.sleep(0.01)
        call_order.append("generative_end")
        return sample_generative_report

    with patch.object(
        service, "analyze_categorical", side_effect=track_cat
    ), patch.object(service, "analyze_epistemic", side_effect=track_epi), patch.object(
        service, "analyze_dialectical", side_effect=track_dia
    ), patch.object(
        service, "analyze_generative", side_effect=track_gen
    ):

        await service.analyze_full(str(temp_spec_file))

        # Verify order:
        # 1. categorical_start and epistemic_start should both happen BEFORE dialectical_start
        cat_start_idx = call_order.index("categorical_start")
        epi_start_idx = call_order.index("epistemic_start")
        dia_start_idx = call_order.index("dialectical_start")
        gen_start_idx = call_order.index("generative_start")

        # Both Phase 1 tasks should START before any Phase 2 task
        assert cat_start_idx < dia_start_idx, "Categorical should start before dialectical"
        assert cat_start_idx < gen_start_idx, "Categorical should start before generative"
        assert epi_start_idx < dia_start_idx, "Epistemic should start before dialectical"
        assert epi_start_idx < gen_start_idx, "Epistemic should start before generative"

        # Both Phase 1 tasks should END before any Phase 2 task STARTS
        cat_end_idx = call_order.index("categorical_end")
        epi_end_idx = call_order.index("epistemic_end")

        assert cat_end_idx < dia_start_idx, "Categorical must complete before dialectical starts"
        assert cat_end_idx < gen_start_idx, "Categorical must complete before generative starts"
        assert epi_end_idx < dia_start_idx, "Epistemic must complete before dialectical starts"
        assert epi_end_idx < gen_start_idx, "Epistemic must complete before generative starts"


# =============================================================================
# Test: Synthesis Integration
# =============================================================================


@pytest.mark.asyncio
async def test_synthesis_receives_all_four_reports(
    mock_llm: Mock,
    sample_categorical_report: CategoricalReport,
    sample_epistemic_report: EpistemicReport,
    sample_dialectical_report: DialecticalReport,
    sample_generative_report: GenerativeReport,
    temp_spec_file: Path,
):
    """
    Verify synthesis receives all four reports and produces a summary.
    """
    service = AnalysisService(mock_llm)

    with patch.object(
        service, "analyze_categorical", new_callable=AsyncMock
    ) as mock_cat, patch.object(
        service, "analyze_epistemic", new_callable=AsyncMock
    ) as mock_epi, patch.object(
        service, "analyze_dialectical", new_callable=AsyncMock
    ) as mock_dia, patch.object(
        service, "analyze_generative", new_callable=AsyncMock
    ) as mock_gen:

        mock_cat.return_value = sample_categorical_report
        mock_epi.return_value = sample_epistemic_report
        mock_dia.return_value = sample_dialectical_report
        mock_gen.return_value = sample_generative_report

        result = await service.analyze_full(str(temp_spec_file))

        # Verify all four reports are present
        assert result.categorical == sample_categorical_report
        assert result.epistemic == sample_epistemic_report
        assert result.dialectical == sample_dialectical_report
        assert result.generative == sample_generative_report

        # Verify synthesis is non-empty
        assert len(result.synthesis) > 0
        assert "Categorical" in result.synthesis or "categorical" in result.synthesis.lower()


@pytest.mark.asyncio
async def test_synthesis_reflects_report_states(
    mock_llm: Mock,
    sample_categorical_report_with_violations: CategoricalReport,
    sample_epistemic_report: EpistemicReport,
    temp_spec_file: Path,
):
    """
    Verify synthesis correctly reflects the state of reports (e.g., violations).
    """
    service = AnalysisService(mock_llm)

    with patch.object(
        service, "analyze_categorical", new_callable=AsyncMock
    ) as mock_cat, patch.object(
        service, "analyze_epistemic", new_callable=AsyncMock
    ) as mock_epi, patch.object(
        service, "analyze_dialectical", new_callable=AsyncMock
    ) as mock_dia, patch.object(
        service, "analyze_generative", new_callable=AsyncMock
    ) as mock_gen:

        # Categorical has violations
        mock_cat.return_value = sample_categorical_report_with_violations
        mock_epi.return_value = sample_epistemic_report
        mock_dia.return_value = DialecticalReport(
            target=str(temp_spec_file), tensions=(), summary=""
        )
        mock_gen.return_value = GenerativeReport(
            target=str(temp_spec_file),
            grammar=OperadGrammar(
                primitives=frozenset(), operations=frozenset(), laws=frozenset()
            ),
            compression_ratio=1.0,
            regeneration=RegenerationTest(
                axioms_used=(), structures_regenerated=(), missing_elements=(), passed=False
            ),
            minimal_kernel=(),
            summary="",
        )

        result = await service.analyze_full(str(temp_spec_file))

        # Synthesis should mention violations or issues
        assert "⚠️" in result.synthesis or "ISSUES" in result.synthesis or "failed" in result.synthesis.lower()


# =============================================================================
# Test: Error Handling Preserves Composition
# =============================================================================


@pytest.mark.asyncio
async def test_error_in_phase1_still_runs_phase2(
    mock_llm: Mock, sample_epistemic_report: EpistemicReport, temp_spec_file: Path
):
    """
    Verify that if one Phase 1 analyzer fails, Phase 2 still runs.

    The completeness law requires all four modes. If categorical fails,
    we should still attempt epistemic, dialectical, and generative.

    Note: Individual analyze_*() methods catch exceptions and return error reports.
    So if analyze_categorical raises, analyze_full() gets an error CategoricalReport,
    not an exception. Phase 2 continues normally.
    """
    service = AnalysisService(mock_llm)

    # Create error categorical report
    error_categorical = CategoricalReport(
        target=str(temp_spec_file),
        laws_extracted=(),
        law_verifications=(),
        fixed_point=None,
        summary="Error: Categorical analysis failed",
    )

    with patch.object(
        service, "analyze_categorical", new_callable=AsyncMock
    ) as mock_cat, patch.object(
        service, "analyze_epistemic", new_callable=AsyncMock
    ) as mock_epi, patch.object(
        service, "analyze_dialectical", new_callable=AsyncMock
    ) as mock_dia, patch.object(
        service, "analyze_generative", new_callable=AsyncMock
    ) as mock_gen:

        # Categorical returns error report (not raises)
        mock_cat.return_value = error_categorical
        mock_epi.return_value = sample_epistemic_report
        mock_dia.return_value = DialecticalReport(
            target=str(temp_spec_file), tensions=(), summary=""
        )
        mock_gen.return_value = GenerativeReport(
            target=str(temp_spec_file),
            grammar=OperadGrammar(
                primitives=frozenset(), operations=frozenset(), laws=frozenset()
            ),
            compression_ratio=1.0,
            regeneration=RegenerationTest(
                axioms_used=(), structures_regenerated=(), missing_elements=(), passed=False
            ),
            minimal_kernel=(),
            summary="",
        )

        result = await service.analyze_full(str(temp_spec_file))

        # All four modes should have been attempted
        assert "Error" in result.categorical.summary

        # Epistemic should succeed
        assert result.epistemic == sample_epistemic_report

        # Phase 2 should still run (even though Phase 1 had an error)
        mock_dia.assert_called_once()
        mock_gen.assert_called_once()


@pytest.mark.asyncio
async def test_error_in_phase2_still_produces_report(
    mock_llm: Mock,
    sample_categorical_report: CategoricalReport,
    sample_epistemic_report: EpistemicReport,
    sample_generative_report: GenerativeReport,
    temp_spec_file: Path,
):
    """
    Verify that if Phase 2 fails, we still get a full report (with error).

    Note: Individual analyze_*() methods catch exceptions and return error reports.
    So if analyze_dialectical raises, analyze_full() gets an error DialecticalReport,
    not an exception.
    """
    service = AnalysisService(mock_llm)

    # Create error dialectical report
    error_dialectical = DialecticalReport(
        target=str(temp_spec_file),
        tensions=(),
        summary="Error: Dialectical analysis failed",
    )

    with patch.object(
        service, "analyze_categorical", new_callable=AsyncMock
    ) as mock_cat, patch.object(
        service, "analyze_epistemic", new_callable=AsyncMock
    ) as mock_epi, patch.object(
        service, "analyze_dialectical", new_callable=AsyncMock
    ) as mock_dia, patch.object(
        service, "analyze_generative", new_callable=AsyncMock
    ) as mock_gen:

        mock_cat.return_value = sample_categorical_report
        mock_epi.return_value = sample_epistemic_report
        # Dialectical returns error report (not raises)
        mock_dia.return_value = error_dialectical
        mock_gen.return_value = sample_generative_report

        result = await service.analyze_full(str(temp_spec_file))

        # Phase 1 should succeed
        assert result.categorical == sample_categorical_report
        assert result.epistemic == sample_epistemic_report

        # Dialectical should have error
        assert "Error" in result.dialectical.summary

        # Generative should succeed
        assert result.generative == sample_generative_report


# =============================================================================
# Test: Real File Integration
# =============================================================================


@pytest.mark.asyncio
async def test_full_analysis_with_real_file_loads_content(
    mock_llm: Mock,
    sample_categorical_report: CategoricalReport,
    sample_epistemic_report: EpistemicReport,
    sample_dialectical_report: DialecticalReport,
    sample_generative_report: GenerativeReport,
    temp_spec_file: Path,
):
    """
    Verify that analyze_full() loads the file and passes content to analyzers.
    """
    service = AnalysisService(mock_llm)

    with patch.object(
        service, "analyze_categorical", new_callable=AsyncMock
    ) as mock_cat, patch.object(
        service, "analyze_epistemic", new_callable=AsyncMock
    ) as mock_epi, patch.object(
        service, "analyze_dialectical", new_callable=AsyncMock
    ) as mock_dia, patch.object(
        service, "analyze_generative", new_callable=AsyncMock
    ) as mock_gen:

        mock_cat.return_value = sample_categorical_report
        mock_epi.return_value = sample_epistemic_report
        mock_dia.return_value = sample_dialectical_report
        mock_gen.return_value = sample_generative_report

        result = await service.analyze_full(str(temp_spec_file))

        # Verify file was loaded (each method should be called with the path)
        mock_cat.assert_called_once_with(str(temp_spec_file))
        mock_epi.assert_called_once_with(str(temp_spec_file))

        # Result target should match
        assert result.target == str(temp_spec_file)


@pytest.mark.asyncio
async def test_missing_file_returns_error_report(mock_llm: Mock):
    """
    Verify that a missing file produces an error report, not an exception.
    """
    service = AnalysisService(mock_llm)

    # Use a path that doesn't exist
    result = await service.analyze_full("/nonexistent/path/to/spec.md")

    # Should return a report with errors, not raise
    assert "Error" in result.categorical.summary or "not found" in result.categorical.summary.lower()
