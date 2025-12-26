"""
Tests for K-Block boundary detection.

Test Coverage:
- FILE strategy groups correctly
- CLASS strategy separates classes
- IMPORT strategy clusters by similarity
- CALLGRAPH strategy finds SCCs
- HYBRID respects size heuristics
- Split suggestions for oversized blocks
- Merge suggestions for coupled small blocks
- Token estimation accuracy
- Coherence and coupling metrics
"""

import pytest

from ..boundary import (
    BoundaryDetector,
    BoundaryStrategy,
    FunctionCrystal,
    KBlockCandidate,
    MergeSuggestion,
    SplitSuggestion,
)

# Fixtures


@pytest.fixture
def detector():
    """Default boundary detector."""
    return BoundaryDetector(min_tokens=500, max_tokens=5000, target_tokens=2000)


@pytest.fixture
def sample_functions():
    """Sample function crystals for testing."""
    return [
        # File 1: service.py - Class A
        FunctionCrystal(
            id="service.py:ClassA.method1",
            name="method1",
            file_path="service.py",
            line_range=(10, 20),
            signature="def method1(self) -> None",
            docstring="Method 1 docs",
            class_name="ClassA",
            imports=frozenset(["os", "sys"]),
            calls=frozenset(["service.py:ClassA.method2"]),
            called_by=frozenset(),
        ),
        FunctionCrystal(
            id="service.py:ClassA.method2",
            name="method2",
            file_path="service.py",
            line_range=(22, 32),
            signature="def method2(self) -> str",
            docstring="Method 2 docs",
            class_name="ClassA",
            imports=frozenset(["os", "sys"]),
            calls=frozenset(["service.py:ClassA.method1"]),  # Cycle!
            called_by=frozenset(["service.py:ClassA.method1"]),
        ),
        # File 1: service.py - Class B
        FunctionCrystal(
            id="service.py:ClassB.method1",
            name="method1",
            file_path="service.py",
            line_range=(40, 50),
            signature="def method1(self) -> int",
            docstring="Class B method",
            class_name="ClassB",
            imports=frozenset(["json", "pathlib"]),
            calls=frozenset(),
            called_by=frozenset(),
        ),
        # File 1: service.py - Standalone
        FunctionCrystal(
            id="service.py:helper",
            name="helper",
            file_path="service.py",
            line_range=(60, 70),
            signature="def helper(x: int) -> str",
            docstring="Standalone helper",
            class_name=None,
            imports=frozenset(["os"]),
            calls=frozenset(),
            called_by=frozenset(),
        ),
        # File 2: utils.py
        FunctionCrystal(
            id="utils.py:util1",
            name="util1",
            file_path="utils.py",
            line_range=(5, 15),
            signature="def util1() -> None",
            docstring="Utility 1",
            class_name=None,
            imports=frozenset(["os", "sys"]),
            calls=frozenset(["utils.py:util2"]),
            called_by=frozenset(),
        ),
        FunctionCrystal(
            id="utils.py:util2",
            name="util2",
            file_path="utils.py",
            line_range=(17, 27),
            signature="def util2() -> int",
            docstring="Utility 2",
            class_name=None,
            imports=frozenset(["os", "sys"]),
            calls=frozenset(),
            called_by=frozenset(["utils.py:util1"]),
        ),
    ]


# FILE Strategy Tests


@pytest.mark.asyncio
async def test_file_strategy_groups_by_file(detector, sample_functions):
    """FILE strategy creates one candidate per file."""
    candidates = await detector.detect_boundaries(sample_functions, BoundaryStrategy.FILE)

    assert len(candidates) == 2  # service.py and utils.py

    # Check service.py candidate
    service_candidate = next(c for c in candidates if "service.py" in c.rationale)
    assert len(service_candidate.function_ids) == 4  # ClassA.method1, ClassA.method2, ClassB.method1, helper
    assert service_candidate.boundary_type == "FILE"
    assert service_candidate.confidence == 1.0

    # Check utils.py candidate
    utils_candidate = next(c for c in candidates if "utils.py" in c.rationale)
    assert len(utils_candidate.function_ids) == 2  # util1, util2
    assert utils_candidate.boundary_type == "FILE"


@pytest.mark.asyncio
async def test_file_strategy_empty_input(detector):
    """FILE strategy handles empty input."""
    candidates = await detector.detect_boundaries([], BoundaryStrategy.FILE)
    assert candidates == []


# CLASS Strategy Tests


@pytest.mark.asyncio
async def test_class_strategy_separates_classes(detector, sample_functions):
    """CLASS strategy creates separate candidates for each class."""
    candidates = await detector.detect_boundaries(sample_functions, BoundaryStrategy.CLASS)

    # Should have: ClassA, ClassB, helper, util1, util2 (5 total)
    # (standalone functions get individual candidates)
    assert len(candidates) == 5

    # Check ClassA
    class_a = next(c for c in candidates if "ClassA" in c.rationale)
    assert len(class_a.function_ids) == 2
    assert class_a.boundary_type == "CLASS"

    # Check ClassB
    class_b = next(c for c in candidates if "ClassB" in c.rationale)
    assert len(class_b.function_ids) == 1
    assert class_b.boundary_type == "CLASS"

    # Check standalone functions
    standalone = [c for c in candidates if "Standalone" in c.rationale]
    assert len(standalone) >= 1


@pytest.mark.asyncio
async def test_class_strategy_standalone_functions(detector):
    """CLASS strategy handles standalone functions correctly."""
    funcs = [
        FunctionCrystal(
            id="test.py:func1",
            name="func1",
            file_path="test.py",
            line_range=(1, 10),
            signature="def func1() -> None",
            docstring=None,
            class_name=None,
            imports=frozenset(),
            calls=frozenset(),
            called_by=frozenset(),
        ),
        FunctionCrystal(
            id="test.py:func2",
            name="func2",
            file_path="test.py",
            line_range=(12, 20),
            signature="def func2() -> None",
            docstring=None,
            class_name=None,
            imports=frozenset(),
            calls=frozenset(),
            called_by=frozenset(),
        ),
    ]

    candidates = await detector.detect_boundaries(funcs, BoundaryStrategy.CLASS)
    assert len(candidates) == 2  # Each function gets its own candidate


# IMPORT Strategy Tests


@pytest.mark.asyncio
async def test_import_strategy_clusters_similar(detector, sample_functions):
    """IMPORT strategy clusters functions with similar imports."""
    candidates = await detector.detect_boundaries(sample_functions, BoundaryStrategy.IMPORT)

    # Functions with {os, sys} should cluster together
    # ClassA.method1, ClassA.method2, utils.util1, utils.util2 all have os/sys
    # ClassB.method1 has {json, pathlib}
    # helper has {os}

    assert len(candidates) > 0
    for c in candidates:
        assert c.boundary_type == "IMPORT_CLUSTER"


@pytest.mark.asyncio
async def test_import_strategy_no_imports(detector):
    """IMPORT strategy handles functions with no imports."""
    funcs = [
        FunctionCrystal(
            id="test.py:func",
            name="func",
            file_path="test.py",
            line_range=(1, 10),
            signature="def func() -> None",
            docstring=None,
            class_name=None,
            imports=frozenset(),  # No imports
            calls=frozenset(),
            called_by=frozenset(),
        )
    ]

    candidates = await detector.detect_boundaries(funcs, BoundaryStrategy.IMPORT)
    assert len(candidates) == 1


# CALLGRAPH Strategy Tests


@pytest.mark.asyncio
async def test_callgraph_strategy_finds_cycles(detector, sample_functions):
    """CALLGRAPH strategy identifies strongly connected components."""
    candidates = await detector.detect_boundaries(sample_functions, BoundaryStrategy.CALLGRAPH)

    # ClassA.method1 ↔ ClassA.method2 form a cycle (SCC)
    # utils.util1 → utils.util2 (not a cycle, separate SCCs)

    assert len(candidates) > 0

    # Find the SCC containing the cycle
    cycle_scc = None
    for c in candidates:
        if "service.py:ClassA.method1" in c.function_ids and "service.py:ClassA.method2" in c.function_ids:
            cycle_scc = c
            break

    assert cycle_scc is not None
    assert cycle_scc.boundary_type == "SCC"
    assert len(cycle_scc.function_ids) == 2  # method1 and method2


@pytest.mark.asyncio
async def test_callgraph_strategy_no_calls(detector):
    """CALLGRAPH strategy handles functions with no calls."""
    funcs = [
        FunctionCrystal(
            id="test.py:func1",
            name="func1",
            file_path="test.py",
            line_range=(1, 10),
            signature="def func1() -> None",
            docstring=None,
            class_name=None,
            imports=frozenset(),
            calls=frozenset(),  # No calls
            called_by=frozenset(),
        ),
        FunctionCrystal(
            id="test.py:func2",
            name="func2",
            file_path="test.py",
            line_range=(12, 20),
            signature="def func2() -> None",
            docstring=None,
            class_name=None,
            imports=frozenset(),
            calls=frozenset(),  # No calls
            called_by=frozenset(),
        ),
    ]

    candidates = await detector.detect_boundaries(funcs, BoundaryStrategy.CALLGRAPH)
    # Each function is its own SCC
    assert len(candidates) == 2


# HYBRID Strategy Tests


@pytest.mark.asyncio
async def test_hybrid_respects_size_heuristics(detector):
    """HYBRID strategy splits oversized candidates and keeps good ones."""
    # Create a large file with multiple classes
    funcs = []
    for class_idx in range(3):
        for method_idx in range(10):
            funcs.append(
                FunctionCrystal(
                    id=f"big.py:Class{class_idx}.method{method_idx}",
                    name=f"method{method_idx}",
                    file_path="big.py",
                    line_range=(class_idx * 200 + method_idx * 20, class_idx * 200 + method_idx * 20 + 18),
                    signature=f"def method{method_idx}(self) -> None",
                    docstring="A" * 100,  # Large docstring
                    class_name=f"Class{class_idx}",
                    imports=frozenset(["os"]),
                    calls=frozenset(),
                    called_by=frozenset(),
                )
            )

    candidates = await detector.detect_boundaries(funcs, BoundaryStrategy.HYBRID)

    # Should split by class since file is too large
    assert len(candidates) == 3  # One per class
    for c in candidates:
        assert c.boundary_type == "HYBRID"


@pytest.mark.asyncio
async def test_hybrid_keeps_small_files(detector):
    """HYBRID keeps small files as single K-blocks."""
    funcs = [
        FunctionCrystal(
            id="small.py:func",
            name="func",
            file_path="small.py",
            line_range=(1, 10),
            signature="def func() -> None",
            docstring="Small function",
            class_name=None,
            imports=frozenset(),
            calls=frozenset(),
            called_by=frozenset(),
        )
    ]

    candidates = await detector.detect_boundaries(funcs, BoundaryStrategy.HYBRID)
    assert len(candidates) == 1
    assert candidates[0].boundary_type == "HYBRID"


# Token Estimation Tests


def test_token_estimation_empty(detector):
    """Token estimation handles empty input."""
    assert detector.estimate_tokens([]) == 0


def test_token_estimation_single_function(detector):
    """Token estimation for a single function."""
    func = FunctionCrystal(
        id="test.py:func",
        name="func",
        file_path="test.py",
        line_range=(1, 20),  # 20 lines
        signature="def func(x: int) -> str",  # ~24 chars
        docstring="This is a docstring",  # 19 chars
        class_name=None,
        imports=frozenset(),
        calls=frozenset(),
        called_by=frozenset(),
    )

    tokens = detector.estimate_tokens([func])
    # Signature: 24 chars
    # Docstring: 19 chars
    # Body: 20 lines * 40 chars/line = 800 chars
    # Total: ~843 chars / 4 = ~210 tokens
    assert 200 <= tokens <= 250


def test_token_estimation_multiple_functions(detector, sample_functions):
    """Token estimation for multiple functions."""
    tokens = detector.estimate_tokens(sample_functions)
    assert tokens > 0


# Coherence Tests


def test_coherence_single_function(detector):
    """Single function has perfect coherence."""
    func = FunctionCrystal(
        id="test.py:func",
        name="func",
        file_path="test.py",
        line_range=(1, 10),
        signature="def func() -> None",
        docstring=None,
        class_name=None,
        imports=frozenset(),
        calls=frozenset(),
        called_by=frozenset(),
    )

    coherence = detector.compute_coherence([func])
    assert coherence == 1.0


def test_coherence_no_calls(detector):
    """Functions with no calls have zero coherence."""
    funcs = [
        FunctionCrystal(
            id="test.py:func1",
            name="func1",
            file_path="test.py",
            line_range=(1, 10),
            signature="def func1() -> None",
            docstring=None,
            class_name=None,
            imports=frozenset(),
            calls=frozenset(),
            called_by=frozenset(),
        ),
        FunctionCrystal(
            id="test.py:func2",
            name="func2",
            file_path="test.py",
            line_range=(12, 20),
            signature="def func2() -> None",
            docstring=None,
            class_name=None,
            imports=frozenset(),
            calls=frozenset(),
            called_by=frozenset(),
        ),
    ]

    coherence = detector.compute_coherence(funcs)
    assert coherence == 0.0


def test_coherence_with_calls(detector):
    """Functions that call each other have high coherence."""
    funcs = [
        FunctionCrystal(
            id="test.py:func1",
            name="func1",
            file_path="test.py",
            line_range=(1, 10),
            signature="def func1() -> None",
            docstring=None,
            class_name=None,
            imports=frozenset(),
            calls=frozenset(["test.py:func2"]),
            called_by=frozenset(),
        ),
        FunctionCrystal(
            id="test.py:func2",
            name="func2",
            file_path="test.py",
            line_range=(12, 20),
            signature="def func2() -> None",
            docstring=None,
            class_name=None,
            imports=frozenset(),
            calls=frozenset(["test.py:func1"]),
            called_by=frozenset(["test.py:func1"]),
        ),
    ]

    coherence = detector.compute_coherence(funcs)
    # 2 internal calls / (2 * 1) = 1.0
    assert coherence == 1.0


# Coupling Tests


def test_coupling_no_calls(detector):
    """Functions with no cross calls have zero coupling."""
    inside = [
        FunctionCrystal(
            id="a.py:func1",
            name="func1",
            file_path="a.py",
            line_range=(1, 10),
            signature="def func1() -> None",
            docstring=None,
            class_name=None,
            imports=frozenset(),
            calls=frozenset(),
            called_by=frozenset(),
        )
    ]

    outside = [
        FunctionCrystal(
            id="b.py:func2",
            name="func2",
            file_path="b.py",
            line_range=(1, 10),
            signature="def func2() -> None",
            docstring=None,
            class_name=None,
            imports=frozenset(),
            calls=frozenset(),
            called_by=frozenset(),
        )
    ]

    coupling = detector.compute_coupling(inside, outside)
    assert coupling == 0.0


def test_coupling_with_calls(detector):
    """Functions with cross calls have non-zero coupling."""
    inside = [
        FunctionCrystal(
            id="a.py:func1",
            name="func1",
            file_path="a.py",
            line_range=(1, 10),
            signature="def func1() -> None",
            docstring=None,
            class_name=None,
            imports=frozenset(),
            calls=frozenset(["b.py:func2"]),  # Calls outside
            called_by=frozenset(),
        )
    ]

    outside = [
        FunctionCrystal(
            id="b.py:func2",
            name="func2",
            file_path="b.py",
            line_range=(1, 10),
            signature="def func2() -> None",
            docstring=None,
            class_name=None,
            imports=frozenset(),
            calls=frozenset(),
            called_by=frozenset(["a.py:func1"]),
        )
    ]

    coupling = detector.compute_coupling(inside, outside)
    # 1 cross call / (1 * 1 * 2) = 0.5
    assert coupling == 0.5


# Split Suggestion Tests


@pytest.mark.asyncio
async def test_suggest_splits_oversized(detector):
    """Suggest splits for oversized K-blocks."""
    # Create an oversized block
    funcs = []
    for i in range(20):
        funcs.append(
            FunctionCrystal(
                id=f"big.py:Class.method{i}",
                name=f"method{i}",
                file_path="big.py",
                line_range=(i * 50, i * 50 + 48),
                signature=f"def method{i}(self) -> None",
                docstring="A" * 200,  # Large docstring
                class_name="Class",
                imports=frozenset(),
                calls=frozenset(),
                called_by=frozenset(),
            )
        )

    suggestions = await detector.suggest_splits("kb_oversized", funcs)
    assert len(suggestions) > 0
    assert suggestions[0].current_size > detector.max_tokens


@pytest.mark.asyncio
async def test_suggest_splits_not_needed(detector):
    """No split suggestions for appropriately-sized K-blocks."""
    funcs = [
        FunctionCrystal(
            id="small.py:func",
            name="func",
            file_path="small.py",
            line_range=(1, 10),
            signature="def func() -> None",
            docstring="Small",
            class_name=None,
            imports=frozenset(),
            calls=frozenset(),
            called_by=frozenset(),
        )
    ]

    suggestions = await detector.suggest_splits("kb_small", funcs)
    assert len(suggestions) == 0


# Merge Suggestion Tests


@pytest.mark.asyncio
async def test_suggest_merges_high_coupling(detector):
    """Suggest merges for highly-coupled small blocks."""
    block_a_funcs = [
        FunctionCrystal(
            id="a.py:func1",
            name="func1",
            file_path="a.py",
            line_range=(1, 10),
            signature="def func1() -> None",
            docstring="Small",
            class_name=None,
            imports=frozenset(),
            calls=frozenset(["b.py:func2"]),  # Calls b
            called_by=frozenset(),
        )
    ]

    block_b_funcs = [
        FunctionCrystal(
            id="b.py:func2",
            name="func2",
            file_path="b.py",
            line_range=(1, 10),
            signature="def func2() -> None",
            docstring="Small",
            class_name=None,
            imports=frozenset(),
            calls=frozenset(["a.py:func1"]),  # Calls a
            called_by=frozenset(["a.py:func1"]),
        )
    ]

    kblocks = [("kb_a", block_a_funcs), ("kb_b", block_b_funcs)]

    suggestions = await detector.suggest_merges(kblocks)
    # Should suggest merge due to high coupling
    assert len(suggestions) > 0
    assert suggestions[0].coupling_score > 0.3


@pytest.mark.asyncio
async def test_suggest_merges_no_coupling(detector):
    """No merge suggestions for uncoupled blocks."""
    block_a_funcs = [
        FunctionCrystal(
            id="a.py:func1",
            name="func1",
            file_path="a.py",
            line_range=(1, 10),
            signature="def func1() -> None",
            docstring="Small",
            class_name=None,
            imports=frozenset(),
            calls=frozenset(),  # No calls
            called_by=frozenset(),
        )
    ]

    block_b_funcs = [
        FunctionCrystal(
            id="b.py:func2",
            name="func2",
            file_path="b.py",
            line_range=(1, 10),
            signature="def func2() -> None",
            docstring="Small",
            class_name=None,
            imports=frozenset(),
            calls=frozenset(),  # No calls
            called_by=frozenset(),
        )
    ]

    kblocks = [("kb_a", block_a_funcs), ("kb_b", block_b_funcs)]

    suggestions = await detector.suggest_merges(kblocks)
    # No merge due to zero coupling
    assert len(suggestions) == 0


# KBlockCandidate Property Tests


def test_kblock_candidate_size_properties():
    """KBlockCandidate size heuristic properties work correctly."""
    too_small = KBlockCandidate(
        function_ids=frozenset(["f1"]),
        boundary_type="TEST",
        confidence=1.0,
        rationale="Test",
        estimated_tokens=300,  # Below 500
    )
    assert too_small.is_too_small
    assert not too_small.within_size_heuristic
    assert not too_small.is_too_large

    just_right = KBlockCandidate(
        function_ids=frozenset(["f2"]),
        boundary_type="TEST",
        confidence=1.0,
        rationale="Test",
        estimated_tokens=2000,  # Within 500-5000
    )
    assert not just_right.is_too_small
    assert just_right.within_size_heuristic
    assert not just_right.is_too_large

    too_large = KBlockCandidate(
        function_ids=frozenset(["f3"]),
        boundary_type="TEST",
        confidence=1.0,
        rationale="Test",
        estimated_tokens=6000,  # Above 5000
    )
    assert not too_large.is_too_small
    assert not too_large.within_size_heuristic
    assert too_large.is_too_large
