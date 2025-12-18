"""Tests for DialogueService - LLM-backed dialogue generation."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.town.dialogue_service import (
    ARCHETYPE_SYSTEM_PROMPTS,
    TEMPLATE_DIALOGUES,
    CitizenBudget,
    DialogueBudgetConfig,
    DialogueContext,
    DialogueResult,
    DialogueService,
    DialogueTier,
    create_dialogue_service,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_citizen():
    """Create a mock Citizen."""
    citizen = MagicMock()
    citizen.id = "citizen-1"
    citizen.name = "Alice"
    citizen.archetype = "Builder"
    citizen.region = "workshop"
    citizen.eigenvectors = MagicMock(
        warmth=0.7,
        curiosity=0.6,
        trust=0.8,
        creativity=0.5,
        patience=0.9,
        resilience=0.7,
        ambition=0.6,
    )
    citizen.memory = MagicMock()
    citizen.memory.query = AsyncMock(return_value=MagicMock(state={}))
    citizen.get_relationship = MagicMock(return_value=0.5)
    return citizen


@pytest.fixture
def mock_listener():
    """Create a mock listener Citizen."""
    citizen = MagicMock()
    citizen.id = "citizen-2"
    citizen.name = "Bob"
    citizen.archetype = "Trader"
    citizen.region = "market"
    citizen.eigenvectors = MagicMock(
        warmth=0.5,
        curiosity=0.8,
        trust=0.4,
        creativity=0.3,
        patience=0.5,
        resilience=0.6,
        ambition=0.9,
    )
    citizen.memory = MagicMock()
    citizen.memory.query = AsyncMock(return_value=MagicMock(state={}))
    citizen.get_relationship = MagicMock(return_value=0.2)
    return citizen


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = MagicMock()
    response = MagicMock()
    response.text = "Hello, Bob! How goes the trading?"
    response.tokens_used = 15
    response.model = "haiku-test"
    client.generate = AsyncMock(return_value=response)
    return client


# =============================================================================
# DialogueTier Tests
# =============================================================================


class TestDialogueTier:
    """Tests for DialogueTier enum."""

    def test_all_tiers_exist(self) -> None:
        """All expected tiers should exist."""
        assert DialogueTier.TEMPLATE
        assert DialogueTier.CACHED
        assert DialogueTier.HAIKU
        assert DialogueTier.SONNET

    def test_tier_values(self) -> None:
        """Tier values should be correct."""
        assert DialogueTier.TEMPLATE.value == "template"
        assert DialogueTier.CACHED.value == "cached"
        assert DialogueTier.HAIKU.value == "haiku"
        assert DialogueTier.SONNET.value == "sonnet"


# =============================================================================
# DialogueContext Tests
# =============================================================================


class TestDialogueContext:
    """Tests for DialogueContext."""

    def test_default_values(self) -> None:
        """Default context should have empty lists."""
        ctx = DialogueContext()
        assert ctx.focal_memories == []
        assert ctx.peripheral_memories == []
        assert ctx.relationship == 0.0
        assert ctx.phase_name == ""

    def test_to_context_string_empty(self) -> None:
        """Empty context should return empty string."""
        ctx = DialogueContext()
        assert ctx.to_context_string() == ""

    def test_to_context_string_with_memories(self) -> None:
        """Context with memories should format properly."""
        ctx = DialogueContext(
            focal_memories=["Memory 1", "Memory 2"],
            peripheral_memories=["Memory 3"],
            recent_events=["Event happened"],
        )
        result = ctx.to_context_string()
        assert "Memory 1" in result
        assert "Memory 3" in result
        assert "Event happened" in result

    def test_to_context_string_with_coalition(self) -> None:
        """Context with coalition should include it."""
        ctx = DialogueContext(shared_coalition="Builders Guild")
        result = ctx.to_context_string()
        assert "Builders Guild" in result


# =============================================================================
# DialogueResult Tests
# =============================================================================


class TestDialogueResult:
    """Tests for DialogueResult."""

    def test_basic_result(self) -> None:
        """Basic result should store all fields."""
        result = DialogueResult(
            text="Hello!",
            tokens_used=10,
            model="haiku",
            speaker_id="s1",
            listener_id="l1",
            operation="greet",
        )
        assert result.text == "Hello!"
        assert result.tokens_used == 10
        assert result.was_template is False

    def test_template_result(self) -> None:
        """Template result should mark was_template."""
        result = DialogueResult(
            text="Hello!",
            tokens_used=0,
            model="template",
            was_template=True,
        )
        assert result.was_template is True
        assert result.tokens_used == 0


# =============================================================================
# CitizenBudget Tests
# =============================================================================


class TestCitizenBudget:
    """Tests for CitizenBudget."""

    def test_tokens_remaining(self) -> None:
        """Should calculate remaining tokens."""
        budget = CitizenBudget(
            citizen_id="c1",
            tier="evolving",
            daily_limit=1000,
            tokens_used_today=300,
        )
        assert budget.tokens_remaining == 700

    def test_tokens_remaining_floor(self) -> None:
        """Remaining should never be negative."""
        budget = CitizenBudget(
            citizen_id="c1",
            tier="evolving",
            daily_limit=100,
            tokens_used_today=200,
        )
        assert budget.tokens_remaining == 0

    def test_can_afford(self) -> None:
        """Should check affordability."""
        budget = CitizenBudget(
            citizen_id="c1",
            tier="evolving",
            daily_limit=100,
            tokens_used_today=50,
        )
        assert budget.can_afford(50) is True
        assert budget.can_afford(51) is False

    def test_spend(self) -> None:
        """Should track spending."""
        budget = CitizenBudget(
            citizen_id="c1",
            tier="evolving",
            daily_limit=100,
        )
        budget.spend(30)
        assert budget.tokens_used_today == 30
        budget.spend(20)
        assert budget.tokens_used_today == 50

    def test_reset_if_new_day(self) -> None:
        """Should reset on new day."""
        budget = CitizenBudget(
            citizen_id="c1",
            tier="evolving",
            daily_limit=100,
            tokens_used_today=50,
            last_reset=datetime.now() - timedelta(days=1),
        )
        budget.reset_if_new_day()
        assert budget.tokens_used_today == 0

    def test_no_reset_same_day(self) -> None:
        """Should not reset on same day."""
        budget = CitizenBudget(
            citizen_id="c1",
            tier="evolving",
            daily_limit=100,
            tokens_used_today=50,
        )
        budget.reset_if_new_day()
        assert budget.tokens_used_today == 50  # Unchanged


# =============================================================================
# DialogueBudgetConfig Tests
# =============================================================================


class TestDialogueBudgetConfig:
    """Tests for DialogueBudgetConfig."""

    def test_default_config(self) -> None:
        """Default config should have sensible defaults."""
        config = DialogueBudgetConfig()
        assert "greet" in config.model_routing
        assert "evolving" in config.tier_budgets
        assert config.tier_budgets["evolving"] > config.tier_budgets["standard"]

    def test_model_for_operation(self) -> None:
        """Should return correct model for operations."""
        config = DialogueBudgetConfig()
        assert config.model_for_operation("greet") == "haiku"
        assert config.model_for_operation("council") == "sonnet"
        assert config.model_for_operation("unknown") == "haiku"  # Default

    def test_estimate_tokens(self) -> None:
        """Should estimate tokens for operations."""
        config = DialogueBudgetConfig()
        assert config.estimate_tokens("greet") == 50
        assert config.estimate_tokens("trade") == 200
        assert config.estimate_tokens("unknown") == 100  # Default

    def test_budget_for_tier(self) -> None:
        """Should return budget for tier."""
        config = DialogueBudgetConfig()
        assert config.budget_for_tier("evolving") == 2000
        assert config.budget_for_tier("unknown") == 100  # Default


# =============================================================================
# DialogueService Tests
# =============================================================================


class TestDialogueServiceInit:
    """Tests for DialogueService initialization."""

    def test_default_init(self) -> None:
        """Should initialize with defaults."""
        service = DialogueService()
        assert service._llm is None
        assert service._config is not None
        assert not service.has_llm

    def test_with_llm_client(self, mock_llm_client) -> None:
        """Should accept LLM client."""
        service = DialogueService(llm_client=mock_llm_client)
        assert service.has_llm

    def test_with_custom_config(self) -> None:
        """Should accept custom config."""
        config = DialogueBudgetConfig()
        config.tier_budgets["evolving"] = 5000
        service = DialogueService(budget_config=config)
        assert service._config.budget_for_tier("evolving") == 5000


class TestDialogueServiceBudgets:
    """Tests for budget management."""

    def test_register_citizen(self) -> None:
        """Should register citizen for tracking."""
        service = DialogueService()
        budget = service.register_citizen("c1", "evolving")
        assert budget.citizen_id == "c1"
        assert budget.tier == "evolving"
        assert budget.daily_limit == 2000

    def test_get_budget(self) -> None:
        """Should retrieve registered budget."""
        service = DialogueService()
        service.register_citizen("c1", "evolving")
        budget = service.get_budget("c1")
        assert budget is not None
        assert budget.citizen_id == "c1"

    def test_get_budget_unknown(self) -> None:
        """Should return None for unknown citizen."""
        service = DialogueService()
        assert service.get_budget("unknown") is None

    def test_get_tier_evolving(self, mock_citizen) -> None:
        """Evolving citizen should get SONNET/HAIKU."""
        service = DialogueService()
        service.register_citizen(mock_citizen.id, "evolving")

        tier = service.get_tier(mock_citizen)
        assert tier in (DialogueTier.SONNET, DialogueTier.HAIKU)

    def test_get_tier_no_budget(self, mock_citizen) -> None:
        """Unregistered citizen should get TEMPLATE."""
        service = DialogueService()
        tier = service.get_tier(mock_citizen)
        assert tier == DialogueTier.TEMPLATE


class TestDialogueServiceGeneration:
    """Tests for dialogue generation."""

    @pytest.mark.asyncio
    async def test_generate_template_no_llm(self, mock_citizen, mock_listener) -> None:
        """Without LLM, should use template."""
        service = DialogueService()
        result = await service.generate(mock_citizen, mock_listener, "greet")

        assert result.was_template is True
        assert result.tokens_used == 0
        assert result.model == "template"
        assert mock_listener.name in result.text

    @pytest.mark.asyncio
    async def test_generate_with_llm(self, mock_citizen, mock_listener, mock_llm_client) -> None:
        """With LLM and budget, should generate."""
        service = DialogueService(llm_client=mock_llm_client)
        service.register_citizen(mock_citizen.id, "evolving")

        result = await service.generate(mock_citizen, mock_listener, "greet")

        assert result.was_template is False
        assert result.tokens_used > 0
        mock_llm_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_tracks_budget(
        self, mock_citizen, mock_listener, mock_llm_client
    ) -> None:
        """Should track token usage."""
        service = DialogueService(llm_client=mock_llm_client)
        service.register_citizen(mock_citizen.id, "evolving")

        await service.generate(mock_citizen, mock_listener, "greet")

        budget = service.get_budget(mock_citizen.id)
        assert budget.tokens_used_today == 15  # From mock response


class TestDialogueServiceTemplates:
    """Tests for template generation."""

    def test_template_per_archetype(self, mock_citizen, mock_listener) -> None:
        """Each archetype should have templates."""
        service = DialogueService()

        for archetype in TEMPLATE_DIALOGUES.keys():
            mock_citizen.archetype = archetype
            result = service._generate_template(mock_citizen, mock_listener, "greet")
            assert result.text  # Should produce text

    def test_template_substitutes_name(self, mock_citizen, mock_listener) -> None:
        """Template should substitute listener name."""
        service = DialogueService()
        result = service._generate_template(mock_citizen, mock_listener, "greet")
        assert mock_listener.name in result.text

    def test_template_fallback_for_unknown_operation(self, mock_citizen, mock_listener) -> None:
        """Unknown operation should use greet fallback."""
        service = DialogueService()
        result = service._generate_template(mock_citizen, mock_listener, "unknown_operation")
        assert result.text  # Should still produce something


class TestDialogueServiceCaching:
    """Tests for dialogue caching."""

    def test_cache_stores_dialogue(self, mock_citizen, mock_listener) -> None:
        """Should cache generated dialogue."""
        service = DialogueService()
        service._cache[("Builder", "Trader", "greet")] = (
            "Hello [LISTENER]!",
            datetime.now(),
        )

        assert service._has_cached(mock_citizen)

    def test_cache_expires(self, mock_citizen, mock_listener) -> None:
        """Cache should expire after TTL."""
        service = DialogueService(cache_ttl_seconds=1)
        service._cache[("Builder", "Trader", "greet")] = (
            "Hello!",
            datetime.now() - timedelta(seconds=10),
        )

        assert not service._has_cached(mock_citizen)

    def test_try_cache_personalizes(self, mock_citizen, mock_listener) -> None:
        """Cache retrieval should personalize with listener name."""
        service = DialogueService()
        service._cache[("Builder", "Trader", "greet")] = (
            "Hello [LISTENER]!",
            datetime.now(),
        )

        result = service._try_cache(mock_citizen, mock_listener, "greet")

        assert result is not None
        assert mock_listener.name in result.text


class TestDialogueServicePromptBuilding:
    """Tests for prompt building."""

    def test_build_system_prompt(self, mock_citizen) -> None:
        """Should build archetype-specific system prompt."""
        service = DialogueService()
        prompt = service._build_system_prompt(mock_citizen, "greet")

        assert mock_citizen.name in prompt
        assert "Builder" in prompt
        assert "greet" in prompt

    def test_build_system_prompt_unknown_archetype(self, mock_citizen) -> None:
        """Unknown archetype should fallback to Builder."""
        service = DialogueService()
        mock_citizen.archetype = "UnknownType"
        prompt = service._build_system_prompt(mock_citizen, "greet")

        # Should use fallback
        assert prompt  # Should produce something

    def test_temperature_varies_by_archetype(self) -> None:
        """Different archetypes should have different temperatures."""
        service = DialogueService()
        builder_temp = service._temperature_for_archetype("Builder")
        scholar_temp = service._temperature_for_archetype("Scholar")

        assert builder_temp != scholar_temp


class TestDialogueServiceStats:
    """Tests for service statistics."""

    def test_get_stats(self, mock_llm_client) -> None:
        """Should return comprehensive stats."""
        service = DialogueService(llm_client=mock_llm_client)
        service.register_citizen("c1", "evolving")
        service._cache[("Builder", "Trader", "greet")] = ("Hi", datetime.now())

        stats = service.get_stats()

        assert stats["has_llm"] is True
        assert stats["registered_citizens"] == 1
        assert stats["cache_size"] == 1
        assert "c1" in stats["budgets"]


# =============================================================================
# Factory Tests
# =============================================================================


class TestCreateDialogueService:
    """Tests for create_dialogue_service factory."""

    def test_create_with_mock(self) -> None:
        """use_mock should create MockLLMClient."""
        service = create_dialogue_service(use_mock=True)
        assert service.has_llm

    def test_create_without_credentials(self) -> None:
        """Without credentials should return service with no LLM."""
        with patch(
            "services.town.dialogue_service.has_llm_credentials",
            return_value=False,
        ):
            service = create_dialogue_service(use_mock=False)
            assert not service.has_llm


# =============================================================================
# Template Constants Tests
# =============================================================================


class TestTemplateConstants:
    """Tests for template constants."""

    def test_all_archetypes_have_prompts(self) -> None:
        """All archetypes should have system prompts."""
        expected = {"Builder", "Trader", "Healer", "Scholar", "Watcher"}
        assert set(ARCHETYPE_SYSTEM_PROMPTS.keys()) == expected

    def test_all_archetypes_have_dialogues(self) -> None:
        """All archetypes should have template dialogues."""
        expected = {"Builder", "Trader", "Healer", "Scholar", "Watcher"}
        assert set(TEMPLATE_DIALOGUES.keys()) == expected

    def test_all_operations_have_templates(self) -> None:
        """Core operations should have templates for all archetypes."""
        operations = {"greet", "gossip", "trade"}
        for archetype, templates in TEMPLATE_DIALOGUES.items():
            for op in operations:
                assert op in templates, f"{archetype} missing {op} template"

    def test_template_format_strings(self) -> None:
        """Templates should have proper format strings."""
        for archetype, ops in TEMPLATE_DIALOGUES.items():
            for op, templates in ops.items():
                for template in templates:
                    # Should be able to format without errors
                    try:
                        template.format(
                            listener_name="Test",
                            speaker_name="Speaker",
                            subject_name="Subject",
                        )
                    except KeyError as e:
                        pytest.fail(f"{archetype}/{op}: Missing key {e}")
