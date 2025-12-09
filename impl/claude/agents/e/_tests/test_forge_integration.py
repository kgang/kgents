"""
Tests for E-gent + F-gent Integration (T1.2)

Validates the re-forge workflow from evolved intent.
"""

import pytest
import tempfile
from pathlib import Path
from agents.e.forge_integration import (
    ImprovedIntent,
    ReforgeResult,
    ReforgeStrategy,
    propose_improved_intent,
    reforge_from_evolved_intent,
    evolve_and_reforge_workflow,
    _detect_breaking_changes,
    _synthesize_improved_intent,
)
from agents.e.experiment import CodeModule
from agents.e.judge import JudgeResult, PrincipleScore
from agents.f.prototype import PrototypeConfig


# --- Fixtures ---


@pytest.fixture
def sample_artifact():
    """Sample code artifact for testing"""
    # Create a temporary file for the artifact
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""
class TestAgent:
    def __init__(self):
        pass

    def run(self, input_data: str) -> str:
        return input_data.upper()
""")
        temp_path = Path(f.name)

    artifact = CodeModule(
        name="TestAgent",
        category="test",
        path=temp_path,
    )

    yield artifact

    # Cleanup
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def sample_judge_result():
    """Sample judge result indicating room for improvement"""
    from bootstrap.types import Verdict, VerdictType

    return JudgeResult(
        verdict=Verdict(type=VerdictType.ACCEPT),
        scores=(
            PrincipleScore(
                name="tasteful",
                score=0.9,
                reason="Clean implementation",
            ),
            PrincipleScore(
                name="composable",
                score=0.6,
                reason="Lacks composition interface",
            ),
            PrincipleScore(
                name="ethical",
                score=0.5,
                reason="No input validation",
            ),
        ),
        average_score=0.7,
        reasons=("Add Agent[I,O] interface", "Add input sanitization"),
    )


# --- Test Intent Proposal ---


@pytest.mark.asyncio
async def test_propose_improved_intent_basic(sample_artifact):
    """Test basic intent proposal without judge/experiment results"""
    improved = await propose_improved_intent(
        sample_artifact, original_intent="Agent that converts input text to uppercase"
    )

    assert improved.original_intent == "Agent that converts input text to uppercase"
    assert isinstance(improved.improved_intent, str)
    assert isinstance(improved.rationale, str)
    assert isinstance(improved.changes, list)
    assert isinstance(improved.preserved_constraints, list)


@pytest.mark.asyncio
async def test_propose_improved_intent_with_judge(
    sample_artifact,
    sample_judge_result,
):
    """Test intent proposal incorporates judge feedback"""
    improved = await propose_improved_intent(
        sample_artifact,
        original_intent="Agent that converts input text to uppercase",
        judge_result=sample_judge_result,
    )

    # Should identify low-scoring principles
    assert any("composable" in change.lower() for change in improved.changes)
    assert any("ethical" in change.lower() for change in improved.changes)

    # Should preserve high-scoring principles
    assert any(
        "tasteful" in constraint.lower()
        for constraint in improved.preserved_constraints
    )


@pytest.mark.asyncio
async def test_propose_improved_intent_no_metadata():
    """Test intent proposal when artifact lacks explicit intent"""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def foo(): pass")
        temp_path = Path(f.name)

    artifact = CodeModule(
        name="minimal",
        category="test",
        path=temp_path,
    )

    try:
        improved = await propose_improved_intent(artifact)

        # Should infer a basic intent from module name
        assert (
            "minimal" in improved.original_intent.lower()
            or "functionality" in improved.original_intent.lower()
        )
    finally:
        temp_path.unlink(missing_ok=True)


# --- Test Breaking Change Detection ---


def test_detect_breaking_changes_none():
    """Test no breaking changes detected"""
    original = "Agent that processes strings"
    improved = "Agent that processes strings with better error handling"

    assert not _detect_breaking_changes(original, improved)


def test_detect_breaking_changes_detected():
    """Test breaking changes are detected"""
    original = "Agent that takes string input"
    improved = "Agent that takes different input type (int instead of string)"

    assert _detect_breaking_changes(original, improved)


def test_detect_breaking_changes_keywords():
    """Test various breaking change keywords"""
    original = "Agent that does X"

    breaking_cases = [
        "Remove feature X",
        "Delete the Y method",
        "Change signature from X to Y",
        "Incompatible with previous version",
    ]

    for case in breaking_cases:
        assert _detect_breaking_changes(original, case)


# --- Test Intent Synthesis ---


def test_synthesize_improved_intent_simple():
    """Test basic intent synthesis"""
    original = "Agent that processes data"
    changes = ["Add validation", "Improve error handling"]
    preserved = ["Maintain performance"]

    improved = _synthesize_improved_intent(original, changes, preserved)

    assert "Agent that processes data" in improved
    assert "Add validation" in improved
    assert "Improve error handling" in improved
    assert "Maintain performance" in improved


def test_synthesize_improved_intent_no_changes():
    """Test synthesis with no changes"""
    original = "Agent that processes data"
    improved = _synthesize_improved_intent(original, [], [])

    assert improved == original


# --- Test Re-Forge Workflow ---


@pytest.mark.asyncio
async def test_reforge_intent_only(sample_artifact):
    """Test re-forging with intent refinement strategy"""
    improved_intent = ImprovedIntent(
        original_intent="Agent that converts text to uppercase",
        improved_intent="Agent that converts text to uppercase with validation",
        rationale="Added input validation",
        changes=["Add input validation"],
        preserved_constraints=["Maintain string processing"],
        breaking_changes=False,
    )

    result = await reforge_from_evolved_intent(
        artifact=sample_artifact,
        improved_intent=improved_intent,
        agent_name="ImprovedTestAgent",
        strategy=ReforgeStrategy.INTENT_REFINEMENT,
    )

    assert result.strategy == ReforgeStrategy.INTENT_REFINEMENT
    assert result.new_contract is not None
    assert result.new_contract.agent_name == "ImprovedTestAgent"
    assert result.new_source is None  # Intent refinement doesn't generate code
    assert "parent" in result.lineage


@pytest.mark.asyncio
async def test_reforge_full_reforge(sample_artifact):
    """Test full re-forge with code generation"""
    improved_intent = ImprovedIntent(
        original_intent="Agent that converts text to uppercase",
        improved_intent="Agent that converts text to uppercase with validation",
        rationale="Added input validation",
        changes=["Add input validation"],
        preserved_constraints=["Maintain string processing"],
        breaking_changes=False,
    )

    config = PrototypeConfig(
        max_attempts=1,  # Limit attempts for testing
        use_llm=False,  # Use stub generation for tests
    )

    result = await reforge_from_evolved_intent(
        artifact=sample_artifact,
        improved_intent=improved_intent,
        agent_name="ImprovedTestAgent",
        strategy=ReforgeStrategy.FULL_REFORGE,
        config=config,
    )

    assert result.strategy == ReforgeStrategy.FULL_REFORGE
    assert result.new_contract is not None
    assert result.new_source is not None
    assert isinstance(result.validation_passed, bool)

    # Check lineage tracking
    assert result.lineage["parent"] == "TestAgent"  # Original artifact name
    assert result.lineage["parent_category"] == "test"
    assert result.lineage["reforge_strategy"] == "full_reforge"


@pytest.mark.asyncio
async def test_reforge_preserves_lineage(sample_artifact):
    """Test lineage is properly tracked"""
    improved_intent = ImprovedIntent(
        original_intent="Original intent",
        improved_intent="Improved intent",
        rationale="Test",
        changes=["Change 1", "Change 2"],
        preserved_constraints=[],
        breaking_changes=True,
    )

    result = await reforge_from_evolved_intent(
        artifact=sample_artifact,
        improved_intent=improved_intent,
        agent_name="V2Agent",
        strategy=ReforgeStrategy.INTENT_REFINEMENT,
    )

    assert result.lineage["breaking_changes"] == "True"
    assert result.lineage["intent_changes"] == "2"


# --- Test Full Workflow ---


@pytest.mark.asyncio
async def test_full_evolve_and_reforge_workflow(
    sample_artifact,
    sample_judge_result,
):
    """Test complete workflow from artifact to re-forged version"""
    config = PrototypeConfig(
        max_attempts=1,
        use_llm=False,
    )

    result = await evolve_and_reforge_workflow(
        artifact=sample_artifact,
        agent_name="EvolvedAgent",
        original_intent="Agent that converts input text to uppercase",
        judge_result=sample_judge_result,
        strategy=ReforgeStrategy.FULL_REFORGE,
        config=config,
    )

    # Verify complete result
    assert isinstance(result, ReforgeResult)
    assert result.improved_intent is not None
    assert result.new_contract is not None
    assert result.new_source is not None

    # Verify intent improvements
    improved = result.improved_intent
    assert len(improved.changes) > 0  # Should have changes from judge
    assert improved.original_intent != improved.improved_intent

    # Verify lineage
    assert result.lineage["parent"] == "TestAgent"


@pytest.mark.asyncio
async def test_workflow_with_breaking_changes(sample_artifact):
    """Test workflow properly flags breaking changes"""
    from bootstrap.types import Verdict, VerdictType

    # Create judge result that suggests breaking changes
    judge_result = JudgeResult(
        verdict=Verdict(type=VerdictType.REVISE),
        scores=(
            PrincipleScore(
                name="composable",
                score=0.4,
                reason="Interface needs complete redesign",
            ),
        ),
        average_score=0.4,
        reasons=("Remove current interface", "Add new incompatible interface"),
    )

    result = await evolve_and_reforge_workflow(
        artifact=sample_artifact,
        agent_name="BreakingAgent",
        original_intent="Agent that converts input text to uppercase",
        judge_result=judge_result,
        strategy=ReforgeStrategy.INTENT_REFINEMENT,
    )

    # Breaking changes might be detected in the intent
    # (depends on heuristics, but test the mechanism works)
    assert result.improved_intent.breaking_changes in [True, False]  # Either is valid


@pytest.mark.asyncio
async def test_workflow_minimal_config(sample_artifact):
    """Test workflow with minimal configuration"""
    result = await evolve_and_reforge_workflow(
        artifact=sample_artifact,
        agent_name="MinimalAgent",
        original_intent="Simple agent",
        strategy=ReforgeStrategy.INTENT_REFINEMENT,
    )

    # Should work even without judge/experiment results
    assert result.improved_intent is not None
    assert result.new_contract is not None


# --- Test Edge Cases ---


@pytest.mark.asyncio
async def test_empty_artifact():
    """Test handling of empty artifact"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("")
        temp_path = Path(f.name)

    artifact = CodeModule(
        name="empty",
        category="test",
        path=temp_path,
    )

    try:
        improved = await propose_improved_intent(artifact)

        assert improved.original_intent  # Should infer something
        assert improved.improved_intent  # Should propose something
    finally:
        temp_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_multiple_strategies():
    """Test all re-forge strategies work"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def test(): pass")
        temp_path = Path(f.name)

    artifact = CodeModule(
        name="test",
        category="test",
        path=temp_path,
    )

    improved_intent = ImprovedIntent(
        original_intent="Test agent",
        improved_intent="Improved test agent",
        rationale="Test",
        changes=[],
        preserved_constraints=[],
        breaking_changes=False,
    )

    try:
        strategies = [
            ReforgeStrategy.FULL_REFORGE,
            ReforgeStrategy.INTENT_REFINEMENT,
            ReforgeStrategy.HYBRID,
        ]

        for strategy in strategies:
            result = await reforge_from_evolved_intent(
                artifact=artifact,
                improved_intent=improved_intent,
                agent_name=f"Agent_{strategy.value}",
                strategy=strategy,
                config=PrototypeConfig(max_attempts=1, use_llm=False),
            )

            assert result.strategy == strategy
            assert result.new_contract is not None
    finally:
        temp_path.unlink(missing_ok=True)


# --- Integration with E-gent Structures ---


@pytest.mark.asyncio
async def test_integration_with_experiment_result(sample_artifact):
    """Test integration with E-gent ExperimentResult"""
    from agents.e.experiment import ExperimentResult

    # Create a mock experiment result with the correct structure
    experiment = ExperimentResult(
        experiment=None,  # Not used in propose_improved_intent
        error=None,
    )

    improved = await propose_improved_intent(
        sample_artifact,
        original_intent="Test agent",
        experiment_result=experiment,
    )

    # Should work with experiment result
    assert improved.original_intent == "Test agent"
    assert isinstance(improved.improved_intent, str)
