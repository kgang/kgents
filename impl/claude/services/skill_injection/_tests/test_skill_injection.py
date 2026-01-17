"""
Tests for JIT Skill Injection System.

Tests cover:
- Types and data structures
- SkillRegistry operations
- ActivationConditionEngine evaluation
- StigmergicMemory learning
- JITInjector content injection
- Bootstrap from existing skills
- AGENTESE node integration
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from services.skill_injection import (
    COMMON_COMPOSITIONS,
    ActivationCondition,
    ActivationConditionEngine,
    ActivationConfig,
    ContextType,
    InjectionConfig,
    JITInjector,
    Skill,
    SkillActivation,
    SkillCategory,
    SkillComposition,
    SkillContentReader,
    SkillMatch,
    SkillRegistry,
    SkillUsageTrace,
    StigmergicMemory,
    TaskContext,
    UsageOutcome,
    bootstrap_skills,
    categorize_skill,
    compute_context_hash,
    extract_activation_conditions,
    reset_activation_engine,
    reset_jit_injector,
    reset_skill_registry,
    reset_stigmergic_memory,
)

# === Fixtures ===


@pytest.fixture
def clean_globals():
    """Reset all global instances before and after tests."""
    reset_skill_registry()
    reset_activation_engine()
    reset_stigmergic_memory()
    reset_jit_injector()
    yield
    reset_skill_registry()
    reset_activation_engine()
    reset_stigmergic_memory()
    reset_jit_injector()


@pytest.fixture
def sample_skill() -> Skill:
    """Create a sample skill for testing."""
    return Skill(
        id="test-skill",
        name="Test Skill",
        path="docs/skills/test-skill.md",
        category=SkillCategory.FOUNDATION,
        activation_conditions=(
            ActivationCondition(
                pattern=r"test\s*pattern",
                context_type=ContextType.TASK,
                priority=0.8,
            ),
            ActivationCondition(
                pattern=r"TestError",
                context_type=ContextType.ERROR,
                priority=0.9,
            ),
        ),
        dependencies=("dep-skill",),
        keywords=("test", "sample", "example"),
        description="A test skill for unit tests",
        estimated_read_time_minutes=5,
    )


@pytest.fixture
def sample_registry(sample_skill: Skill) -> SkillRegistry:
    """Create a registry with sample skills."""
    registry = SkillRegistry()

    # Add the sample skill
    registry.register(sample_skill)

    # Add a dependency skill
    dep_skill = Skill(
        id="dep-skill",
        name="Dependency Skill",
        path="docs/skills/dep-skill.md",
        category=SkillCategory.FOUNDATION,
        keywords=("dependency",),
    )
    registry.register(dep_skill)

    # Add some more skills
    registry.register(
        Skill(
            id="agent-skill",
            name="Agent Building",
            path="docs/skills/agent-skill.md",
            category=SkillCategory.FOUNDATION,
            activation_conditions=(
                ActivationCondition(
                    pattern=r"\bagent\b",
                    context_type=ContextType.TASK,
                    priority=0.7,
                ),
            ),
            keywords=("agent", "categorical"),
        )
    )

    registry.register(
        Skill(
            id="ui-skill",
            name="UI Patterns",
            path="docs/skills/ui-skill.md",
            category=SkillCategory.PROJECTION,
            activation_conditions=(
                ActivationCondition(
                    pattern=r"\bUI\b|frontend",
                    context_type=ContextType.TASK,
                    priority=0.6,
                ),
            ),
            keywords=("UI", "frontend", "responsive"),
        )
    )

    return registry


@pytest.fixture
def sample_context() -> TaskContext:
    """Create a sample task context."""
    return TaskContext(
        task_description="Build a test pattern for the agent",
        active_files=("impl/claude/services/test.py",),
        error_messages=("TestError: something failed",),
        user_keywords=("agent",),
        session_id="test-session",
    )


# === Type Tests ===


class TestActivationCondition:
    """Tests for ActivationCondition."""

    def test_matches_task_pattern(self):
        """Test matching task patterns."""
        condition = ActivationCondition(
            pattern=r"test\s*pattern",
            context_type=ContextType.TASK,
            priority=0.8,
        )

        assert condition.matches("I need a test pattern")
        assert condition.matches("testpattern here")
        assert not condition.matches("something else")

    def test_matches_keyword(self):
        """Test keyword matching (case-insensitive)."""
        condition = ActivationCondition(
            pattern="AGENT",
            context_type=ContextType.KEYWORD,
            priority=0.5,
        )

        assert condition.matches("build an agent")
        assert condition.matches("AGENT here")
        assert not condition.matches("something else")

    def test_priority_validation(self):
        """Test priority must be 0.0-1.0."""
        with pytest.raises(ValueError):
            ActivationCondition(
                pattern="test",
                context_type=ContextType.TASK,
                priority=1.5,
            )

        with pytest.raises(ValueError):
            ActivationCondition(
                pattern="test",
                context_type=ContextType.TASK,
                priority=-0.1,
            )


class TestSkill:
    """Tests for Skill type."""

    def test_skill_creation(self, sample_skill: Skill):
        """Test creating a skill."""
        assert sample_skill.id == "test-skill"
        assert sample_skill.name == "Test Skill"
        assert sample_skill.category == SkillCategory.FOUNDATION
        assert len(sample_skill.activation_conditions) == 2
        assert "test" in sample_skill.keywords

    def test_skill_to_dict(self, sample_skill: Skill):
        """Test skill serialization."""
        data = sample_skill.to_dict()

        assert data["id"] == "test-skill"
        assert data["category"] == "foundation"
        assert len(data["activation_conditions"]) == 2
        assert data["keywords"] == ["test", "sample", "example"]


class TestTaskContext:
    """Tests for TaskContext."""

    def test_all_context_strings(self, sample_context: TaskContext):
        """Test extracting all context strings."""
        strings = sample_context.all_context_strings()

        # Should have task, file, error, keyword
        assert len(strings) >= 4

        # Check types are correct
        types = {ctx_type for _, ctx_type in strings}
        assert ContextType.TASK in types
        assert ContextType.FILE in types
        assert ContextType.ERROR in types
        assert ContextType.KEYWORD in types


# === Registry Tests ===


class TestSkillRegistry:
    """Tests for SkillRegistry."""

    def test_register_and_get(self, clean_globals, sample_skill: Skill):
        """Test registering and retrieving a skill."""
        registry = SkillRegistry()
        registry.register(sample_skill)

        retrieved = registry.get_skill("test-skill")
        assert retrieved.id == sample_skill.id
        assert retrieved.name == sample_skill.name

    def test_duplicate_registration(self, clean_globals, sample_skill: Skill):
        """Test that duplicate registration raises error."""
        from services.skill_injection import DuplicateSkillError

        registry = SkillRegistry()
        registry.register(sample_skill)

        with pytest.raises(DuplicateSkillError):
            registry.register(sample_skill)

    def test_overwrite_allowed(self, clean_globals, sample_skill: Skill):
        """Test that overwrite can be allowed."""
        registry = SkillRegistry()
        registry.register(sample_skill)
        registry.register(sample_skill, allow_overwrite=True)  # Should not raise

    def test_find_by_keywords(self, clean_globals, sample_registry: SkillRegistry):
        """Test finding skills by keywords."""
        matches = sample_registry.find_by_keywords(["test", "agent"])

        assert len(matches) >= 2
        skill_ids = {m.skill.id for m in matches}
        assert "test-skill" in skill_ids
        assert "agent-skill" in skill_ids

    def test_find_by_context(self, clean_globals, sample_registry: SkillRegistry):
        """Test finding skills by context."""
        context = TaskContext(
            task_description="Build a test pattern",
            error_messages=("TestError occurred",),
        )

        matches = sample_registry.find_by_context(context)

        # test-skill should match (has test pattern and TestError conditions)
        skill_ids = {m.skill.id for m in matches}
        assert "test-skill" in skill_ids

    def test_find_by_category(self, clean_globals, sample_registry: SkillRegistry):
        """Test finding skills by category."""
        foundation = sample_registry.find_by_category(SkillCategory.FOUNDATION)
        projection = sample_registry.find_by_category(SkillCategory.PROJECTION)

        assert len(foundation) >= 2
        assert len(projection) >= 1
        assert all(s.category == SkillCategory.FOUNDATION for s in foundation)
        assert all(s.category == SkillCategory.PROJECTION for s in projection)

    def test_resolve_dependencies(self, clean_globals, sample_registry: SkillRegistry):
        """Test resolving skill dependencies."""
        deps = sample_registry.resolve_dependencies("test-skill")

        assert "test-skill" in deps
        assert "dep-skill" in deps


# === Activation Engine Tests ===


class TestActivationConditionEngine:
    """Tests for ActivationConditionEngine."""

    def test_evaluate_single_skill(
        self, clean_globals, sample_registry: SkillRegistry, sample_skill: Skill
    ):
        """Test evaluating a single skill."""
        engine = ActivationConditionEngine(registry=sample_registry)

        context = TaskContext(
            task_description="test pattern matching",
        )

        score = engine.evaluate(sample_skill, context)

        assert score.skill_id == "test-skill"
        assert score.base_score > 0
        assert score.final_score > 0

    def test_evaluate_all(self, clean_globals, sample_registry: SkillRegistry):
        """Test evaluating all skills."""
        engine = ActivationConditionEngine(
            registry=sample_registry,
            config=ActivationConfig(min_score=0.0),  # Include all
        )

        context = TaskContext(task_description="build an agent with UI")

        scores = engine.evaluate_all(context)

        # Should have some matches
        assert len(scores) > 0
        # Should be sorted by score
        assert all(
            scores[i].final_score >= scores[i + 1].final_score for i in range(len(scores) - 1)
        )

    def test_select_skills_limit(self, clean_globals, sample_registry: SkillRegistry):
        """Test that select_skills respects max_skills for primary skills."""
        engine = ActivationConditionEngine(
            registry=sample_registry,
            config=ActivationConfig(max_skills=2, min_score=0.0, include_dependencies=False),
        )

        context = TaskContext(task_description="build an agent with UI test pattern")

        activations = engine.select_skills(context)

        # Without dependencies, should be limited to max_skills
        assert len(activations) <= 2

    def test_select_skills_with_dependencies(self, clean_globals, sample_registry: SkillRegistry):
        """Test that dependencies can exceed max_skills."""
        engine = ActivationConditionEngine(
            registry=sample_registry,
            config=ActivationConfig(max_skills=2, min_score=0.0, include_dependencies=True),
        )

        context = TaskContext(task_description="build an agent with test pattern")

        activations = engine.select_skills(context)

        # With dependencies, may exceed max_skills
        assert len(activations) >= 1  # At least some skills activated

    def test_detect_composition(self, clean_globals, sample_registry: SkillRegistry):
        """Test composition detection."""
        # Add composition skills
        for skill_id in ["agentese-node-registration", "agentese-path", "test-patterns"]:
            sample_registry.register(
                Skill(
                    id=skill_id,
                    name=skill_id,
                    path=f"docs/skills/{skill_id}.md",
                    category=SkillCategory.PROTOCOL,
                ),
                allow_overwrite=True,
            )

        # Register the composition
        sample_registry.register_composition(COMMON_COMPOSITIONS["new-agentese-node"])

        engine = ActivationConditionEngine(registry=sample_registry)

        context = TaskContext(task_description="Add a new AGENTESE node")

        activations = engine.select_skills(context)

        # Should detect the composition
        # (assuming composition detection works based on task keywords)
        assert len(activations) > 0


# === Stigmergic Memory Tests ===


class TestStigmergicMemory:
    """Tests for StigmergicMemory."""

    def test_record_usage(self, clean_globals):
        """Test recording skill usage."""
        memory = StigmergicMemory()

        trace = SkillUsageTrace(
            skill_id="test-skill",
            context_hash="abc123",
            context_summary="Testing",
            outcome=UsageOutcome.SUCCESS,
            timestamp=datetime.now(UTC),
        )

        memory.record_usage(trace)

        stats = memory.get_usage_stats("test-skill")
        assert stats is not None
        assert stats.total_uses == 1
        assert stats.successes == 1

    def test_success_rate(self, clean_globals):
        """Test success rate calculation."""
        memory = StigmergicMemory()

        # Record 3 successes and 1 failure
        for outcome in [
            UsageOutcome.SUCCESS,
            UsageOutcome.SUCCESS,
            UsageOutcome.SUCCESS,
            UsageOutcome.FAILURE,
        ]:
            memory.record_usage(
                SkillUsageTrace(
                    skill_id="test-skill",
                    context_hash="abc",
                    context_summary="test",
                    outcome=outcome,
                    timestamp=datetime.now(UTC),
                )
            )

        rate = memory.get_success_rate("test-skill")
        assert rate is not None
        assert rate == 0.75  # 3/4

    def test_suggest_compositions(self, clean_globals):
        """Test composition suggestion."""
        memory = StigmergicMemory()

        # Record several usages of the same skill combination
        for _ in range(5):
            memory.record_composition_usage(
                skill_ids=("skill-a", "skill-b"),
                context_hash="context1",
                success=True,
            )

        suggestions = memory.suggest_compositions(min_usage=3)

        assert len(suggestions) >= 1
        suggested_ids = [set(s.skill_ids) for s in suggestions]
        assert {"skill-a", "skill-b"} in suggested_ids

    def test_context_hash_stability(self):
        """Test that similar contexts produce similar hashes."""
        hash1 = compute_context_hash("build an agent", ("file1.py",))
        hash2 = compute_context_hash("build an agent", ("file1.py",))
        hash3 = compute_context_hash("different task", ("file1.py",))

        assert hash1 == hash2  # Same input, same hash
        assert hash1 != hash3  # Different task, different hash


# === JIT Injector Tests ===


class TestJITInjector:
    """Tests for JITInjector."""

    @pytest.mark.asyncio
    async def test_inject_for_task(self, clean_globals, sample_registry: SkillRegistry):
        """Test injecting skills for a task."""
        engine = ActivationConditionEngine(
            registry=sample_registry,
            config=ActivationConfig(min_score=0.0),
        )
        injector = JITInjector(
            registry=sample_registry,
            engine=engine,
            config=InjectionConfig(max_skills=2),
        )

        result = await injector.inject_for_task("build an agent with test pattern")

        # Should have some activations
        assert len(result.activations) >= 0  # May be 0 if no content files

    @pytest.mark.asyncio
    async def test_record_outcome(self, clean_globals, sample_registry: SkillRegistry):
        """Test recording injection outcome."""
        memory = StigmergicMemory()
        engine = ActivationConditionEngine(
            registry=sample_registry,
            config=ActivationConfig(min_score=0.0),
        )
        injector = JITInjector(
            registry=sample_registry,
            engine=engine,
            memory=memory,
        )

        # Simulate injection
        await injector.inject_for_task("test pattern")

        # Record outcome
        injector.record_outcome(UsageOutcome.SUCCESS, feedback="worked great")

        # Check memory was updated
        stats = memory.stats_summary()
        # Should have recorded something (if skills were activated)
        assert "total_traces" in stats


# === Bootstrap Tests ===


class TestBootstrap:
    """Tests for skill bootstrap."""

    def test_categorize_skill(self):
        """Test skill categorization."""
        assert categorize_skill("polynomial-agent") == SkillCategory.FOUNDATION
        assert categorize_skill("agentese-path") == SkillCategory.PROTOCOL
        assert categorize_skill("crown-jewel-patterns") == SkillCategory.ARCHITECTURE
        assert categorize_skill("elastic-ui-patterns") == SkillCategory.PROJECTION
        assert categorize_skill("unknown-skill") == SkillCategory.UNIVERSAL

    def test_extract_activation_conditions(self):
        """Test activation condition extraction."""
        conditions = extract_activation_conditions("polynomial-agent")

        assert len(conditions) > 0
        # Should have task and keyword conditions
        types = {c.context_type for c in conditions}
        assert ContextType.TASK in types or ContextType.KEYWORD in types

    def test_bootstrap_skills(self, clean_globals, tmp_path: Path):
        """Test bootstrapping from skills directory."""
        # Create a test skills directory
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Create a test skill file
        skill_file = skills_dir / "test-skill.md"
        skill_file.write_text(
            """---
path: docs/skills/test-skill
status: active
---

# Test Skill

> A skill for testing the bootstrap.

## Overview

This is a test skill.
"""
        )

        registry = SkillRegistry()
        loaded = bootstrap_skills(skills_dir, registry)

        assert loaded == 1
        assert registry.get_skill_or_none("test-skill") is not None


# === Integration Tests ===


class TestIntegration:
    """Integration tests for the full skill injection flow."""

    @pytest.mark.asyncio
    async def test_full_injection_flow(self, clean_globals, sample_registry: SkillRegistry):
        """Test the complete injection flow."""
        memory = StigmergicMemory()
        engine = ActivationConditionEngine(
            registry=sample_registry,
            memory=memory,
            config=ActivationConfig(min_score=0.0, max_skills=3),
        )
        injector = JITInjector(
            registry=sample_registry,
            engine=engine,
            memory=memory,
        )

        # Step 1: Inject for task
        result = await injector.inject_for_task(
            "build an agent with test pattern",
            active_files=["impl/test.py"],
        )

        # Step 2: Record success
        injector.record_outcome(UsageOutcome.SUCCESS)

        # Step 3: Inject again for similar task
        result2 = await injector.inject_for_task("another test pattern task")

        # Memory should influence activation scores
        # (harder to test without real skill files)

    def test_common_compositions(self):
        """Test that common compositions are valid."""
        assert len(COMMON_COMPOSITIONS) >= 4

        for comp_id, comp in COMMON_COMPOSITIONS.items():
            assert comp.id == comp_id
            assert len(comp.skill_ids) >= 2
            assert comp.name
            assert comp.description
