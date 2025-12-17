"""
Tests for CLI Command Dimension System.

These tests verify the dimension types and derivation rules
from spec/protocols/cli.md Part II.
"""

from __future__ import annotations

import pytest

from protocols.agentese.affordances import (
    AspectCategory,
    AspectMetadata,
    DeclaredEffect,
    Effect,
)
from protocols.cli.dimensions import (
    Backend,
    CommandDimensions,
    Execution,
    Intent,
    Interactivity,
    Seriousness,
    Statefulness,
    derive_backend,
    derive_dimensions,
    derive_from_category,
    derive_intent,
    derive_interactivity,
    derive_seriousness,
    DEFAULT_DIMENSIONS,
    PROTECTED_RESOURCES,
)


# === Dimension Type Tests ===


class TestExecutionEnum:
    """Test Execution dimension enum."""

    def test_has_sync(self) -> None:
        assert Execution.SYNC is not None

    def test_has_async(self) -> None:
        assert Execution.ASYNC is not None

    def test_values_distinct(self) -> None:
        assert Execution.SYNC != Execution.ASYNC


class TestStatefulnessEnum:
    """Test Statefulness dimension enum."""

    def test_has_stateless(self) -> None:
        assert Statefulness.STATELESS is not None

    def test_has_stateful(self) -> None:
        assert Statefulness.STATEFUL is not None


class TestBackendEnum:
    """Test Backend dimension enum."""

    def test_has_pure(self) -> None:
        assert Backend.PURE is not None

    def test_has_llm(self) -> None:
        assert Backend.LLM is not None

    def test_has_external(self) -> None:
        assert Backend.EXTERNAL is not None


class TestSeriousnessEnum:
    """Test Seriousness dimension enum."""

    def test_has_sensitive(self) -> None:
        assert Seriousness.SENSITIVE is not None

    def test_has_playful(self) -> None:
        assert Seriousness.PLAYFUL is not None

    def test_has_neutral(self) -> None:
        assert Seriousness.NEUTRAL is not None


class TestInteractivityEnum:
    """Test Interactivity dimension enum."""

    def test_has_oneshot(self) -> None:
        assert Interactivity.ONESHOT is not None

    def test_has_streaming(self) -> None:
        assert Interactivity.STREAMING is not None

    def test_has_interactive(self) -> None:
        assert Interactivity.INTERACTIVE is not None


class TestCommandDimensions:
    """Test CommandDimensions composite type."""

    def test_frozen(self) -> None:
        """CommandDimensions should be immutable."""
        dims = CommandDimensions(
            execution=Execution.SYNC,
            statefulness=Statefulness.STATELESS,
            backend=Backend.PURE,
            intent=Intent.FUNCTIONAL,
            seriousness=Seriousness.NEUTRAL,
            interactivity=Interactivity.ONESHOT,
        )
        with pytest.raises(AttributeError):
            dims.execution = Execution.ASYNC  # type: ignore[misc]

    def test_equality(self) -> None:
        """Same dimensions should be equal."""
        dims1 = CommandDimensions(
            execution=Execution.SYNC,
            statefulness=Statefulness.STATELESS,
            backend=Backend.PURE,
            intent=Intent.FUNCTIONAL,
            seriousness=Seriousness.NEUTRAL,
            interactivity=Interactivity.ONESHOT,
        )
        dims2 = CommandDimensions(
            execution=Execution.SYNC,
            statefulness=Statefulness.STATELESS,
            backend=Backend.PURE,
            intent=Intent.FUNCTIONAL,
            seriousness=Seriousness.NEUTRAL,
            interactivity=Interactivity.ONESHOT,
        )
        assert dims1 == dims2

    def test_inequality(self) -> None:
        """Different dimensions should not be equal."""
        dims1 = CommandDimensions(
            execution=Execution.SYNC,
            statefulness=Statefulness.STATELESS,
            backend=Backend.PURE,
            intent=Intent.FUNCTIONAL,
            seriousness=Seriousness.NEUTRAL,
            interactivity=Interactivity.ONESHOT,
        )
        dims2 = CommandDimensions(
            execution=Execution.ASYNC,  # Different!
            statefulness=Statefulness.STATELESS,
            backend=Backend.PURE,
            intent=Intent.FUNCTIONAL,
            seriousness=Seriousness.NEUTRAL,
            interactivity=Interactivity.ONESHOT,
        )
        assert dims1 != dims2

    def test_str_format(self) -> None:
        """String representation should be compact."""
        dims = CommandDimensions(
            execution=Execution.ASYNC,
            statefulness=Statefulness.STATEFUL,
            backend=Backend.LLM,
            intent=Intent.FUNCTIONAL,
            seriousness=Seriousness.SENSITIVE,
            interactivity=Interactivity.STREAMING,
        )
        assert str(dims) == "ASYNC/STATEFUL/LLM/FUNCTIONAL/SENSITIVE/STREAMING"

    def test_convenience_properties(self) -> None:
        """Test convenience boolean properties."""
        dims = CommandDimensions(
            execution=Execution.ASYNC,
            statefulness=Statefulness.STATEFUL,
            backend=Backend.LLM,
            intent=Intent.FUNCTIONAL,
            seriousness=Seriousness.SENSITIVE,
            interactivity=Interactivity.STREAMING,
        )
        assert dims.is_async is True
        assert dims.needs_state is True
        assert dims.needs_budget_display is True
        assert dims.needs_confirmation is True
        assert dims.is_streaming is True
        assert dims.is_interactive is False

    def test_convenience_properties_negative(self) -> None:
        """Test convenience properties return False appropriately."""
        dims = CommandDimensions(
            execution=Execution.SYNC,
            statefulness=Statefulness.STATELESS,
            backend=Backend.PURE,
            intent=Intent.FUNCTIONAL,
            seriousness=Seriousness.NEUTRAL,
            interactivity=Interactivity.ONESHOT,
        )
        assert dims.is_async is False
        assert dims.needs_state is False
        assert dims.needs_budget_display is False
        assert dims.needs_confirmation is False
        assert dims.is_streaming is False
        assert dims.is_interactive is False


# === Derivation Rule Tests ===


class TestDeriveFromCategory:
    """Test derive_from_category() function."""

    def test_perception_is_sync_stateless(self) -> None:
        """PERCEPTION -> sync, stateless."""
        execution, statefulness = derive_from_category(AspectCategory.PERCEPTION)
        assert execution == Execution.SYNC
        assert statefulness == Statefulness.STATELESS

    def test_mutation_is_async_stateful(self) -> None:
        """MUTATION -> async, stateful."""
        execution, statefulness = derive_from_category(AspectCategory.MUTATION)
        assert execution == Execution.ASYNC
        assert statefulness == Statefulness.STATEFUL

    def test_generation_is_async_stateful(self) -> None:
        """GENERATION -> async, stateful."""
        execution, statefulness = derive_from_category(AspectCategory.GENERATION)
        assert execution == Execution.ASYNC
        assert statefulness == Statefulness.STATEFUL

    def test_composition_is_sync_stateless(self) -> None:
        """COMPOSITION -> sync, stateless."""
        execution, statefulness = derive_from_category(AspectCategory.COMPOSITION)
        assert execution == Execution.SYNC
        assert statefulness == Statefulness.STATELESS

    def test_introspection_is_sync_stateless(self) -> None:
        """INTROSPECTION -> sync, stateless."""
        execution, statefulness = derive_from_category(AspectCategory.INTROSPECTION)
        assert execution == Execution.SYNC
        assert statefulness == Statefulness.STATELESS

    def test_entropy_is_sync_stateless(self) -> None:
        """ENTROPY -> sync, stateless."""
        execution, statefulness = derive_from_category(AspectCategory.ENTROPY)
        assert execution == Execution.SYNC
        assert statefulness == Statefulness.STATELESS


class TestDeriveBackend:
    """Test derive_backend() function."""

    def test_no_effects_is_pure(self) -> None:
        """No effects -> PURE backend."""
        assert derive_backend([]) == Backend.PURE

    def test_reads_effect_is_pure(self) -> None:
        """READS effect -> PURE backend (not a call)."""
        effects = [Effect.READS("memory")]
        assert derive_backend(effects) == Backend.PURE

    def test_calls_llm_is_llm(self) -> None:
        """CALLS("llm") -> LLM backend."""
        effects = [Effect.CALLS("llm")]
        assert derive_backend(effects) == Backend.LLM

    def test_calls_model_is_llm(self) -> None:
        """CALLS containing 'model' -> LLM backend."""
        effects = [Effect.CALLS("gpt-4-model")]
        assert derive_backend(effects) == Backend.LLM

    def test_calls_api_is_external(self) -> None:
        """CALLS to API -> EXTERNAL backend."""
        effects = [Effect.CALLS("stripe_api")]
        assert derive_backend(effects) == Backend.EXTERNAL

    def test_calls_service_is_external(self) -> None:
        """CALLS to service -> EXTERNAL backend."""
        effects = [Effect.CALLS("email_service")]
        assert derive_backend(effects) == Backend.EXTERNAL


class TestDeriveSeriousness:
    """Test derive_seriousness() function."""

    def test_void_path_is_playful(self) -> None:
        """void.* paths -> PLAYFUL."""
        assert derive_seriousness("void.entropy.sip", []) == Seriousness.PLAYFUL
        assert derive_seriousness("void.random.thank", []) == Seriousness.PLAYFUL

    def test_forces_effect_is_sensitive(self) -> None:
        """FORCES effect -> SENSITIVE."""
        effects = [Effect.FORCES("user_consent")]
        assert derive_seriousness("self.soul.transform", effects) == Seriousness.SENSITIVE

    def test_writes_protected_is_sensitive(self) -> None:
        """WRITES to protected resource -> SENSITIVE."""
        for resource in ["soul", "memory", "forest", "config", "credentials"]:
            effects = [Effect.WRITES(resource)]
            assert derive_seriousness("self.test.path", effects) == Seriousness.SENSITIVE

    def test_writes_unprotected_is_neutral(self) -> None:
        """WRITES to unprotected resource -> NEUTRAL."""
        effects = [Effect.WRITES("temp_data")]
        assert derive_seriousness("self.test.path", effects) == Seriousness.NEUTRAL

    def test_no_special_conditions_is_neutral(self) -> None:
        """Default -> NEUTRAL."""
        assert derive_seriousness("self.test.path", []) == Seriousness.NEUTRAL


class TestDeriveIntent:
    """Test derive_intent() function."""

    def test_introspection_is_instructional(self) -> None:
        """INTROSPECTION -> INSTRUCTIONAL."""
        assert derive_intent(AspectCategory.INTROSPECTION) == Intent.INSTRUCTIONAL

    def test_perception_is_functional(self) -> None:
        """PERCEPTION -> FUNCTIONAL."""
        assert derive_intent(AspectCategory.PERCEPTION) == Intent.FUNCTIONAL

    def test_mutation_is_functional(self) -> None:
        """MUTATION -> FUNCTIONAL."""
        assert derive_intent(AspectCategory.MUTATION) == Intent.FUNCTIONAL

    def test_generation_is_functional(self) -> None:
        """GENERATION -> FUNCTIONAL."""
        assert derive_intent(AspectCategory.GENERATION) == Intent.FUNCTIONAL


class TestDeriveInteractivity:
    """Test derive_interactivity() function."""

    def test_default_is_oneshot(self) -> None:
        """No flags -> ONESHOT."""
        assert derive_interactivity() == Interactivity.ONESHOT

    def test_streaming_flag(self) -> None:
        """streaming=True -> STREAMING."""
        assert derive_interactivity(streaming=True) == Interactivity.STREAMING

    def test_interactive_flag(self) -> None:
        """interactive=True -> INTERACTIVE."""
        assert derive_interactivity(interactive=True) == Interactivity.INTERACTIVE

    def test_interactive_takes_precedence(self) -> None:
        """If both set, interactive wins (per spec they're exclusive)."""
        assert derive_interactivity(streaming=True, interactive=True) == Interactivity.INTERACTIVE


# === Full Derivation Tests ===


class TestDeriveDimensions:
    """Test derive_dimensions() - the single source of truth."""

    @pytest.fixture
    def perception_meta(self) -> AspectMetadata:
        """Simple perception aspect metadata."""
        return AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[Effect.READS("state")],
            requires_archetype=(),
            idempotent=True,
            description="Read something",
            help="Read something from state",
        )

    @pytest.fixture
    def mutation_meta(self) -> AspectMetadata:
        """Mutation aspect with writes."""
        return AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[Effect.WRITES("memory")],
            requires_archetype=(),
            idempotent=False,
            description="Change memory",
            help="Modify memory state",
        )

    @pytest.fixture
    def llm_generation_meta(self) -> AspectMetadata:
        """LLM-backed generation aspect."""
        return AspectMetadata(
            category=AspectCategory.GENERATION,
            effects=[Effect.WRITES("memory"), Effect.CALLS("llm")],
            requires_archetype=(),
            idempotent=False,
            description="Generate with LLM",
            help="Generate content using LLM",
            budget_estimate="~200 tokens",
        )

    def test_perception_derives_sync_stateful(self, perception_meta: AspectMetadata) -> None:
        """Perception with READS -> sync but stateful."""
        dims = derive_dimensions("self.forest.manifest", perception_meta)
        assert dims.execution == Execution.SYNC
        # READS effect overrides to stateful
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE
        assert dims.seriousness == Seriousness.NEUTRAL

    def test_mutation_derives_async_stateful(self, mutation_meta: AspectMetadata) -> None:
        """Mutation with WRITES(memory) -> async, stateful, sensitive."""
        dims = derive_dimensions("self.memory.transform", mutation_meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE
        # WRITES(memory) is protected
        assert dims.seriousness == Seriousness.SENSITIVE

    def test_llm_generation_derives_correctly(self, llm_generation_meta: AspectMetadata) -> None:
        """LLM-backed generation -> async, stateful, LLM backend."""
        dims = derive_dimensions("self.memory.capture", llm_generation_meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.LLM
        # WRITES(memory) is protected
        assert dims.seriousness == Seriousness.SENSITIVE

    def test_void_path_is_playful(self) -> None:
        """void.* paths derive PLAYFUL seriousness."""
        meta = AspectMetadata(
            category=AspectCategory.ENTROPY,
            effects=[],
            requires_archetype=(),
            idempotent=True,
            description="Draw entropy",
            help="Draw from the accursed share",
        )
        dims = derive_dimensions("void.entropy.sip", meta)
        assert dims.seriousness == Seriousness.PLAYFUL
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATELESS

    def test_introspection_is_instructional(self) -> None:
        """INTROSPECTION aspects derive INSTRUCTIONAL intent."""
        meta = AspectMetadata(
            category=AspectCategory.INTROSPECTION,
            effects=[],
            requires_archetype=(),
            idempotent=True,
            description="Show help",
            help="Display help information",
        )
        dims = derive_dimensions("self.forest.affordances", meta)
        assert dims.intent == Intent.INSTRUCTIONAL

    def test_streaming_flag_propagates(self) -> None:
        """streaming=True in metadata -> STREAMING interactivity."""
        meta = AspectMetadata(
            category=AspectCategory.GENERATION,
            effects=[Effect.CALLS("llm")],
            requires_archetype=(),
            idempotent=False,
            description="Stream content",
            help="Generate streaming content",
            streaming=True,
            budget_estimate="~500 tokens",
        )
        dims = derive_dimensions("self.soul.stream", meta)
        assert dims.interactivity == Interactivity.STREAMING

    def test_interactive_flag_propagates(self) -> None:
        """interactive=True in metadata -> INTERACTIVE interactivity."""
        meta = AspectMetadata(
            category=AspectCategory.GENERATION,
            effects=[Effect.CALLS("llm")],
            requires_archetype=(),
            idempotent=False,
            description="Chat",
            help="Interactive chat mode",
            interactive=True,
            budget_estimate="~500 tokens/turn",
        )
        dims = derive_dimensions("self.soul.chat", meta)
        assert dims.interactivity == Interactivity.INTERACTIVE

    def test_calls_effect_forces_async(self) -> None:
        """CALLS effect overrides category to async."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,  # Would be sync
            effects=[Effect.CALLS("llm")],  # But CALLS forces async
            requires_archetype=(),
            idempotent=True,
            description="LLM-backed perception",
            help="Perceive with LLM assistance",
            budget_estimate="~100 tokens",
        )
        dims = derive_dimensions("self.soul.sense", meta)
        assert dims.execution == Execution.ASYNC  # Overridden by CALLS


class TestDefaultDimensions:
    """Test DEFAULT_DIMENSIONS constant."""

    def test_default_is_safe(self) -> None:
        """Default dimensions should be the safest possible."""
        assert DEFAULT_DIMENSIONS.execution == Execution.SYNC
        assert DEFAULT_DIMENSIONS.statefulness == Statefulness.STATELESS
        assert DEFAULT_DIMENSIONS.backend == Backend.PURE
        assert DEFAULT_DIMENSIONS.intent == Intent.FUNCTIONAL
        assert DEFAULT_DIMENSIONS.seriousness == Seriousness.NEUTRAL
        assert DEFAULT_DIMENSIONS.interactivity == Interactivity.ONESHOT


class TestProtectedResources:
    """Test PROTECTED_RESOURCES constant."""

    def test_includes_soul(self) -> None:
        assert "soul" in PROTECTED_RESOURCES

    def test_includes_memory(self) -> None:
        assert "memory" in PROTECTED_RESOURCES

    def test_includes_forest(self) -> None:
        assert "forest" in PROTECTED_RESOURCES

    def test_includes_config(self) -> None:
        assert "config" in PROTECTED_RESOURCES

    def test_includes_credentials(self) -> None:
        assert "credentials" in PROTECTED_RESOURCES


# === Crown Jewel Dimension Tests ===


class TestBrainDimensions:
    """
    Test dimension derivation for Brain Crown Jewel paths.

    Brain (self.memory.*) paths should derive:
    - self.memory.manifest: SYNC, STATEFUL (READS), PURE, NEUTRAL
    - self.memory.capture: ASYNC, STATEFUL, LLM (CALLS), SENSITIVE (WRITES memory)
    - self.memory.search: ASYNC, STATEFUL, LLM (CALLS), NEUTRAL
    - self.memory.surface (void.*): SYNC, STATELESS, PURE, PLAYFUL (void context)
    """

    def test_brain_manifest_dimensions(self) -> None:
        """self.memory.manifest should be sync, stateful, pure, neutral."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[Effect.READS("brain_crystals")],
            requires_archetype=(),
            idempotent=True,
            description="Display brain status",
            help="Display brain status and health metrics",
        )
        dims = derive_dimensions("self.memory.manifest", meta)
        assert dims.execution == Execution.SYNC
        # READS effect implies state dependency
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE
        assert dims.seriousness == Seriousness.NEUTRAL
        assert dims.interactivity == Interactivity.ONESHOT

    def test_brain_capture_dimensions(self) -> None:
        """self.memory.capture should be async, stateful, llm, sensitive."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[
                Effect.WRITES("brain_crystals"),
                Effect.CALLS("llm"),  # For embeddings
            ],
            requires_archetype=(),
            idempotent=False,
            description="Capture content",
            help="Capture content to holographic memory",
            budget_estimate="low",
        )
        dims = derive_dimensions("self.memory.capture", meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.LLM
        # Note: brain_crystals is not in PROTECTED_RESOURCES, so NEUTRAL
        # If we want SENSITIVE, we'd add "brain" to PROTECTED_RESOURCES
        assert dims.seriousness == Seriousness.NEUTRAL

    def test_brain_search_dimensions(self) -> None:
        """self.memory.search should be async (CALLS), stateful, llm."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[
                Effect.READS("brain_crystals"),
                Effect.CALLS("llm"),
            ],
            requires_archetype=(),
            idempotent=True,
            description="Search memories",
            help="Semantic search for similar memories",
            budget_estimate="low",
        )
        dims = derive_dimensions("self.memory.search", meta)
        # CALLS effect forces async even for PERCEPTION
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.LLM
        assert dims.seriousness == Seriousness.NEUTRAL

    def test_brain_surface_void_dimensions(self) -> None:
        """void.memory.surface should be sync, stateless, pure, playful."""
        meta = AspectMetadata(
            category=AspectCategory.ENTROPY,
            effects=[Effect.READS("brain_crystals")],
            requires_archetype=(),
            idempotent=True,
            description="Surface serendipity",
            help="Surface a serendipitous memory from the void",
        )
        dims = derive_dimensions("void.memory.surface", meta)
        assert dims.execution == Execution.SYNC
        # READS implies stateful
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE
        # void.* paths are PLAYFUL
        assert dims.seriousness == Seriousness.PLAYFUL

    def test_brain_chat_dimensions(self) -> None:
        """self.memory.chat.* should be interactive."""
        meta = AspectMetadata(
            category=AspectCategory.GENERATION,
            effects=[
                Effect.READS("brain_crystals"),
                Effect.CALLS("llm"),
            ],
            requires_archetype=(),
            idempotent=False,
            description="Chat with brain",
            help="Interactive chat with holographic memory",
            interactive=True,
            budget_estimate="~500 tokens/turn",
        )
        dims = derive_dimensions("self.memory.chat.send", meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.LLM
        assert dims.interactivity == Interactivity.INTERACTIVE


class TestSoulDimensions:
    """
    Test dimension derivation for Soul Crown Jewel paths.

    Soul (self.soul.*) paths should derive:
    - self.soul.manifest: SYNC, STATEFUL, PURE, NEUTRAL
    - self.soul.challenge: ASYNC, STATEFUL, LLM, NEUTRAL
    - self.soul.chat.*: ASYNC, STATEFUL, LLM, INTERACTIVE
    """

    def test_soul_manifest_dimensions(self) -> None:
        """self.soul.manifest should be sync, stateful, pure."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[Effect.READS("soul_state")],
            requires_archetype=(),
            idempotent=True,
            description="Show soul state",
            help="Show current soul state and eigenvectors",
        )
        dims = derive_dimensions("self.soul.manifest", meta)
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE

    def test_soul_challenge_dimensions(self) -> None:
        """self.soul.challenge should be async, stateful, llm."""
        meta = AspectMetadata(
            category=AspectCategory.GENERATION,
            effects=[Effect.CALLS("llm")],
            requires_archetype=(),
            idempotent=False,
            description="Challenge idea",
            help="Challenge an idea through dialectics",
            budget_estimate="medium",
        )
        dims = derive_dimensions("self.soul.challenge", meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.LLM

    def test_soul_transform_is_sensitive(self) -> None:
        """self.soul.transform with WRITES(soul) should be sensitive."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[
                Effect.WRITES("soul"),
                Effect.CALLS("llm"),
            ],
            requires_archetype=(),
            idempotent=False,
            description="Transform soul",
            help="Transform soul eigenvectors",
            budget_estimate="high",
        )
        dims = derive_dimensions("self.soul.transform", meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.LLM
        # WRITES(soul) triggers SENSITIVE
        assert dims.seriousness == Seriousness.SENSITIVE


# === Wave 2: Forest, Joy, Soul Extension Dimension Tests ===


class TestForestDimensions:
    """
    Test dimension derivation for Forest Protocol paths.

    Forest (self.forest.*) paths should derive:
    - self.forest.manifest: SYNC, STATEFUL (READS), PURE, NEUTRAL
    - self.forest.reconcile: ASYNC, STATEFUL, PURE, SENSITIVE (WRITES forest)
    - self.forest.tithe: SYNC (ENTROPY), STATEFUL (WRITES), PURE, SENSITIVE (WRITES forest)
    - void.forest.sip: SYNC, STATELESS, PURE, PLAYFUL (void.* path)
    """

    def test_forest_manifest_dimensions(self) -> None:
        """self.forest.manifest should be sync, stateful, pure, neutral."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[Effect.READS("plans")],
            requires_archetype=(),
            idempotent=True,
            description="View forest canopy",
            help="Show summary of all plans in the forest",
        )
        dims = derive_dimensions("self.forest.manifest", meta)
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATEFUL  # READS implies state
        assert dims.backend == Backend.PURE
        assert dims.seriousness == Seriousness.NEUTRAL

    def test_forest_reconcile_dimensions(self) -> None:
        """self.forest.reconcile should be async, stateful, pure, sensitive."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[Effect.WRITES("forest"), Effect.WRITES("git")],
            requires_archetype=(),
            idempotent=False,
            description="Regenerate _forest.md",
            help="Full reconciliation and optionally commit",
        )
        dims = derive_dimensions("self.forest.reconcile", meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE
        # WRITES(forest) is protected
        assert dims.seriousness == Seriousness.SENSITIVE

    def test_forest_tithe_dimensions(self) -> None:
        """self.forest.tithe should be entropy-derived (sync/stateless) but WRITES makes stateful."""
        meta = AspectMetadata(
            category=AspectCategory.ENTROPY,
            effects=[Effect.WRITES("forest")],
            requires_archetype=(),
            idempotent=False,
            description="Archive stale plans",
            help="Move dormant plans to archive",
        )
        dims = derive_dimensions("self.forest.tithe", meta)
        # ENTROPY is sync, but WRITES effect creates statefulness
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE
        # WRITES(forest) is protected
        assert dims.seriousness == Seriousness.SENSITIVE

    def test_forest_sip_void_dimensions(self) -> None:
        """void.forest.sip should be playful (void.* path)."""
        meta = AspectMetadata(
            category=AspectCategory.ENTROPY,
            effects=[Effect.READS("plans")],
            requires_archetype=(),
            idempotent=True,
            description="Select dormant plan",
            help="Randomly select a dormant plan for attention",
        )
        dims = derive_dimensions("void.forest.sip", meta)
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATEFUL  # READS
        assert dims.backend == Backend.PURE
        # void.* paths are PLAYFUL
        assert dims.seriousness == Seriousness.PLAYFUL


class TestJoyDimensions:
    """
    Test dimension derivation for Joy paths.

    Joy (void.joy.*) paths should all derive:
    - SYNC (ENTROPY category)
    - STATELESS (no WRITES)
    - PURE (no CALLS)
    - PLAYFUL (void.* path)
    """

    def test_joy_oblique_dimensions(self) -> None:
        """void.joy.oblique should be sync, stateless, pure, playful."""
        meta = AspectMetadata(
            category=AspectCategory.ENTROPY,
            effects=[],  # No state effects for oblique
            requires_archetype=(),
            idempotent=True,
            description="Draw an Oblique Strategy",
            help="Get a Brian Eno / Peter Schmidt Oblique Strategy card",
        )
        dims = derive_dimensions("void.joy.oblique", meta)
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATELESS
        assert dims.backend == Backend.PURE
        assert dims.seriousness == Seriousness.PLAYFUL

    def test_joy_surprise_dimensions(self) -> None:
        """void.joy.surprise should be playful."""
        meta = AspectMetadata(
            category=AspectCategory.ENTROPY,
            effects=[],
            requires_archetype=(),
            idempotent=True,
            description="Get surprise prompt",
            help="Get a creative surprise prompt",
        )
        dims = derive_dimensions("void.joy.surprise", meta)
        assert dims.seriousness == Seriousness.PLAYFUL
        assert dims.backend == Backend.PURE

    def test_joy_flinch_dimensions(self) -> None:
        """void.joy.flinch should be playful despite probing discomfort."""
        meta = AspectMetadata(
            category=AspectCategory.ENTROPY,
            effects=[],
            requires_archetype=(),
            idempotent=True,
            description="Surface avoidance",
            help="What are you avoiding?",
        )
        dims = derive_dimensions("void.joy.flinch", meta)
        assert dims.seriousness == Seriousness.PLAYFUL
        assert dims.backend == Backend.PURE

    def test_joy_challenge_dimensions(self) -> None:
        """void.joy.challenge should be playful (not to be confused with self.soul.challenge)."""
        meta = AspectMetadata(
            category=AspectCategory.ENTROPY,
            effects=[],
            requires_archetype=(),
            idempotent=True,
            description="Get creative challenge",
            help="Get a constraint-based creative challenge",
        )
        dims = derive_dimensions("void.joy.challenge", meta)
        assert dims.seriousness == Seriousness.PLAYFUL


class TestSoulExtensionDimensions:
    """
    Test dimension derivation for new Soul extension aspects (why, tension).

    These should derive similar to challenge/reflect:
    - ASYNC (CALLS llm)
    - STATEFUL
    - LLM backend
    - NEUTRAL (not WRITES(soul))
    """

    def test_soul_why_dimensions(self) -> None:
        """self.soul.why should be async, llm-backed."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[Effect.CALLS("llm"), Effect.CHARGES("tokens")],
            requires_archetype=(),
            idempotent=False,
            description="Explore purpose",
            help="Keep asking 'why' until reaching first principles",
            budget_estimate="~600 tokens",
        )
        dims = derive_dimensions("self.soul.why", meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.LLM
        assert dims.seriousness == Seriousness.NEUTRAL

    def test_soul_tension_dimensions(self) -> None:
        """self.soul.tension should be async, llm-backed."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[Effect.CALLS("llm"), Effect.CHARGES("tokens")],
            requires_archetype=(),
            idempotent=False,
            description="Surface tensions",
            help="Name opposing forces without resolving",
            budget_estimate="~600 tokens",
        )
        dims = derive_dimensions("self.soul.tension", meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.LLM
        assert dims.seriousness == Seriousness.NEUTRAL


# === Wave 2.5: Gardener, Garden, Tend Dimension Tests ===


class TestGardenerDimensions:
    """
    Test dimension derivation for Gardener (concept.gardener.*) paths.

    Gardener paths should derive:
    - concept.gardener.session.manifest: SYNC, STATEFUL, PURE, NEUTRAL
    - concept.gardener.session.define: ASYNC, STATEFUL, PURE, NEUTRAL
    - concept.gardener.session.advance: ASYNC, STATEFUL, PURE, NEUTRAL
    - concept.gardener.session.chat: ASYNC, STATEFUL, LLM, INTERACTIVE
    """

    def test_gardener_session_manifest_dimensions(self) -> None:
        """concept.gardener.session.manifest should be sync, stateful."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[Effect.READS("session_state")],
            requires_archetype=(),
            idempotent=True,
            description="View session status",
            help="Show current session including phase, counts, and intent",
        )
        dims = derive_dimensions("concept.gardener.session.manifest", meta)
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE
        assert dims.seriousness == Seriousness.NEUTRAL

    def test_gardener_session_define_dimensions(self) -> None:
        """concept.gardener.session.define should be async, stateful."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[Effect.WRITES("session_state")],
            requires_archetype=(),
            idempotent=False,
            description="Start new session",
            help="Create a new polynomial session",
        )
        dims = derive_dimensions("concept.gardener.session.define", meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE
        # WRITES(session_state) is not protected like soul/forest
        assert dims.seriousness == Seriousness.NEUTRAL

    def test_gardener_session_advance_dimensions(self) -> None:
        """concept.gardener.session.advance should be async, stateful."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[Effect.WRITES("session_state")],
            requires_archetype=(),
            idempotent=False,
            description="Advance phase",
            help="Advance SENSE->ACT->REFLECT",
        )
        dims = derive_dimensions("concept.gardener.session.advance", meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE

    def test_gardener_session_chat_dimensions(self) -> None:
        """concept.gardener.session.chat should be async, llm, interactive."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[Effect.CALLS("llm"), Effect.CHARGES("tokens")],
            requires_archetype=(),
            idempotent=False,
            description="Interactive tending chat",
            help="Chat mode for tending gestures",
            interactive=True,
            budget_estimate="~500 tokens/turn",
        )
        dims = derive_dimensions("concept.gardener.session.chat", meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.LLM
        assert dims.interactivity == Interactivity.INTERACTIVE


class TestGardenStateDimensions:
    """
    Test dimension derivation for Garden State (self.garden.*) paths.

    Garden paths should derive:
    - self.garden.manifest: SYNC, STATEFUL, PURE, NEUTRAL
    - self.garden.season: SYNC, STATEFUL, PURE, NEUTRAL
    - self.garden.health: SYNC, STATEFUL, PURE, NEUTRAL
    - self.garden.transition: ASYNC, STATEFUL, PURE, SENSITIVE (WRITES)
    - self.garden.suggest: SYNC, STATEFUL, PURE, NEUTRAL
    """

    def test_garden_manifest_dimensions(self) -> None:
        """self.garden.manifest should be sync, stateful."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[Effect.READS("garden_state")],
            requires_archetype=(),
            idempotent=True,
            description="View garden status",
            help="Show garden overview with plots, season, and health",
        )
        dims = derive_dimensions("self.garden.manifest", meta)
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE
        assert dims.seriousness == Seriousness.NEUTRAL

    def test_garden_season_dimensions(self) -> None:
        """self.garden.season should be sync, stateful."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[Effect.READS("garden_state")],
            requires_archetype=(),
            idempotent=True,
            description="Show season info",
            help="Show current season details",
        )
        dims = derive_dimensions("self.garden.season", meta)
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE

    def test_garden_transition_dimensions(self) -> None:
        """self.garden.transition should be async, stateful, sensitive."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[Effect.WRITES("garden_state")],
            requires_archetype=(),
            idempotent=False,
            description="Transition season",
            help="Transition garden to a new season",
        )
        dims = derive_dimensions("self.garden.transition", meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE
        # Season transitions affect garden state
        assert dims.seriousness == Seriousness.NEUTRAL

    def test_garden_suggest_dimensions(self) -> None:
        """self.garden.suggest should be sync, stateful (auto-inducer)."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[Effect.READS("garden_state")],
            requires_archetype=(),
            idempotent=True,
            description="Check auto-inducer",
            help="Check for season transition suggestion",
        )
        dims = derive_dimensions("self.garden.suggest", meta)
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE


class TestTendDimensions:
    """
    Test dimension derivation for Tend (self.garden.tend.*) paths.

    Tend paths (six gestures) should derive:
    - self.garden.tend.observe: SYNC (PERCEPTION), STATEFUL, PURE, NEUTRAL
    - self.garden.tend.prune: ASYNC (MUTATION), STATEFUL, PURE, NEUTRAL
    - self.garden.tend.graft: ASYNC (MUTATION), STATEFUL, PURE, NEUTRAL
    - self.garden.tend.water: ASYNC (MUTATION), STATEFUL, PURE, NEUTRAL
    - self.garden.tend.rotate: SYNC (PERCEPTION), STATEFUL, PURE, NEUTRAL
    - self.garden.tend.wait: SYNC (ENTROPY), STATELESS, PURE, NEUTRAL
    """

    def test_tend_observe_dimensions(self) -> None:
        """self.garden.tend.observe should be sync, stateful (reads)."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[Effect.READS("garden_state")],
            requires_archetype=(),
            idempotent=True,
            description="Observe without changing",
            help="Perceive without changing (nearly free)",
        )
        dims = derive_dimensions("self.garden.tend.observe", meta)
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATEFUL  # READS
        assert dims.backend == Backend.PURE
        assert dims.seriousness == Seriousness.NEUTRAL

    def test_tend_prune_dimensions(self) -> None:
        """self.garden.tend.prune should be async, stateful (writes)."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[Effect.WRITES("garden_state")],
            requires_archetype=(),
            idempotent=False,
            description="Remove what no longer serves",
            help="Mark for removal (requires reason)",
        )
        dims = derive_dimensions("self.garden.tend.prune", meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE

    def test_tend_graft_dimensions(self) -> None:
        """self.garden.tend.graft should be async, stateful (writes)."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[Effect.WRITES("garden_state")],
            requires_archetype=(),
            idempotent=False,
            description="Add something new",
            help="Add new element (requires reason)",
        )
        dims = derive_dimensions("self.garden.tend.graft", meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE

    def test_tend_water_dimensions(self) -> None:
        """self.garden.tend.water should be async, stateful (writes)."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[Effect.WRITES("garden_state")],
            requires_archetype=(),
            idempotent=False,
            description="Nurture via TextGRAD",
            help="Nurture via TextGRAD (requires feedback)",
        )
        dims = derive_dimensions("self.garden.tend.water", meta)
        assert dims.execution == Execution.ASYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE

    def test_tend_rotate_dimensions(self) -> None:
        """self.garden.tend.rotate should be sync, stateful (reads)."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[Effect.READS("garden_state")],
            requires_archetype=(),
            idempotent=True,
            description="Change perspective",
            help="Change perspective (cheap)",
        )
        dims = derive_dimensions("self.garden.tend.rotate", meta)
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATEFUL  # READS
        assert dims.backend == Backend.PURE

    def test_tend_wait_dimensions(self) -> None:
        """self.garden.tend.wait should be sync, stateless (no effects)."""
        meta = AspectMetadata(
            category=AspectCategory.ENTROPY,
            effects=[],  # No effects - waiting is free
            requires_archetype=(),
            idempotent=True,
            description="Allow time to pass",
            help="Intentional pause (free)",
        )
        dims = derive_dimensions("self.garden.tend.wait", meta)
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATELESS
        assert dims.backend == Backend.PURE
        assert dims.seriousness == Seriousness.NEUTRAL
