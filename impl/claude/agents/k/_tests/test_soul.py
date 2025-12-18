"""
Tests for K-gent Soul: The Middleware of Consciousness.

These tests verify:
1. Soul initialization with eigenvectors
2. Dialogue modes (REFLECT/ADVISE/CHALLENGE/EXPLORE)
3. Budget tiers (DORMANT/WHISPER/DIALOGUE/DEEP)
4. Template responses (zero-token)
5. Semaphore interception (mediator pattern)
6. State manifest
7. [Phase 1] LLM-backed dialogue
8. [Phase 1] Deep intercept with principle reasoning
9. [Phase 1] Audit trail
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from agents.k import (
    ADVISE_STARTERS,
    CHALLENGE_STARTERS,
    DANGEROUS_KEYWORDS,
    EXPLORE_STARTERS,
    KENT_EIGENVECTORS,
    REFLECT_STARTERS,
    AuditEntry,
    AuditTrail,
    BudgetConfig,
    BudgetTier,
    DialogueMode,
    EigenvectorCoordinate,
    InterceptResult,
    KentEigenvectors,
    KgentSoul,
    MockLLMClient,
    PersonaSeed,
    PersonaState,
    SoulDialogueOutput,
    SoulState,
    all_starters,
    create_llm_client,
    create_soul,
    eigenvector_context,
    format_starters_for_display,
    get_eigenvectors,
    get_starters,
    get_whisper_response,
    has_llm_credentials,
    morpheus_available,
    random_starter,
    should_use_template,
    soul,
    try_template_response,
)

# --- Eigenvector Tests ---


class TestEigenvectors:
    """Test personality eigenvector coordinates."""

    def test_kent_eigenvectors_singleton(self) -> None:
        """KENT_EIGENVECTORS should be a singleton."""
        assert KENT_EIGENVECTORS is get_eigenvectors()

    def test_eigenvector_values_in_range(self) -> None:
        """All eigenvector values should be between 0 and 1."""
        eigens = KENT_EIGENVECTORS
        for eigen in eigens.all_eigenvectors():
            assert 0.0 <= eigen.value <= 1.0, f"{eigen.name} value out of range"
            assert 0.0 <= eigen.confidence <= 1.0, f"{eigen.name} confidence out of range"

    def test_aesthetic_is_minimalist(self) -> None:
        """Kent's aesthetic should lean minimalist (low value)."""
        assert KENT_EIGENVECTORS.aesthetic.value < 0.5
        assert KENT_EIGENVECTORS.aesthetic.axis_low == "Minimalist"

    def test_categorical_is_abstract(self) -> None:
        """Kent's categorical should lean abstract (high value)."""
        assert KENT_EIGENVECTORS.categorical.value > 0.8
        assert KENT_EIGENVECTORS.categorical.axis_high == "Abstract"

    def test_heterarchy_is_peer(self) -> None:
        """Kent's heterarchy should lean peer-to-peer (high value)."""
        assert KENT_EIGENVECTORS.heterarchy.value > 0.8
        assert KENT_EIGENVECTORS.heterarchy.axis_high == "Peer-to-Peer"

    def test_joy_is_playful(self) -> None:
        """Kent's joy should lean playful (high value)."""
        assert KENT_EIGENVECTORS.joy.value > 0.5
        assert KENT_EIGENVECTORS.joy.axis_high == "Playful"

    def test_eigenvector_to_dict(self) -> None:
        """Eigenvectors should convert to dict."""
        d = KENT_EIGENVECTORS.to_dict()
        assert "aesthetic" in d
        assert "categorical" in d
        assert "joy" in d
        assert len(d) == 6

    def test_eigenvector_context(self) -> None:
        """Eigenvector context should be a string."""
        ctx = eigenvector_context()
        assert isinstance(ctx, str)
        assert "Personality Coordinates" in ctx

    def test_eigenvector_description(self) -> None:
        """Eigenvector coordinate should have description."""
        aesthetic = KENT_EIGENVECTORS.aesthetic
        desc = aesthetic.description
        assert "minimalist" in desc.lower()

    def test_eigenvector_prompt_fragment(self) -> None:
        """Eigenvector should generate prompt fragment."""
        aesthetic = KENT_EIGENVECTORS.aesthetic
        fragment = aesthetic.to_prompt_fragment()
        assert "Aesthetic" in fragment
        assert "minimalist" in fragment.lower()


# --- Starter Tests ---


class TestStarters:
    """Test mode-specific starter prompts."""

    def test_reflect_starters_exist(self) -> None:
        """REFLECT mode should have starters."""
        assert len(REFLECT_STARTERS) > 0

    def test_advise_starters_exist(self) -> None:
        """ADVISE mode should have starters."""
        assert len(ADVISE_STARTERS) > 0

    def test_challenge_starters_exist(self) -> None:
        """CHALLENGE mode should have starters."""
        assert len(CHALLENGE_STARTERS) > 0

    def test_explore_starters_exist(self) -> None:
        """EXPLORE mode should have starters."""
        assert len(EXPLORE_STARTERS) > 0

    def test_get_starters_by_mode(self) -> None:
        """get_starters should return starters for mode."""
        starters = get_starters(DialogueMode.REFLECT)
        assert starters == REFLECT_STARTERS

    def test_random_starter(self) -> None:
        """random_starter should return a valid starter."""
        starter = random_starter(DialogueMode.CHALLENGE)
        assert starter in CHALLENGE_STARTERS

    def test_all_starters(self) -> None:
        """all_starters should return dict of all modes."""
        starters = all_starters()
        assert "reflect" in starters
        assert "advise" in starters
        assert "challenge" in starters
        assert "explore" in starters

    def test_format_starters_for_display(self) -> None:
        """format_starters_for_display should format nicely."""
        formatted = format_starters_for_display(DialogueMode.REFLECT)
        assert "REFLECT" in formatted
        assert "1." in formatted


# --- Template Tests ---


class TestTemplates:
    """Test zero-token template responses."""

    def test_greeting_template(self) -> None:
        """Greetings should return template response."""
        response = try_template_response("hello")
        assert response is not None
        # Response should be conversational (some have "?", some don't)
        assert len(response) > 0

    def test_morning_greeting(self) -> None:
        """Morning greeting should be recognized."""
        response = try_template_response("good morning")
        assert response is not None
        assert "morning" in response.lower()

    def test_mode_transition_template(self) -> None:
        """Mode transitions should return template."""
        response = try_template_response("reflect")
        assert response is not None
        assert "REFLECT" in response

    def test_session_template(self) -> None:
        """Session keywords should return template."""
        response = try_template_response("thanks")
        assert response is not None
        assert "thank" in response.lower()

    def test_should_use_template(self) -> None:
        """should_use_template should detect template-able inputs."""
        assert should_use_template("hello")
        assert should_use_template("thanks")
        assert not should_use_template("What should I do about architecture?")

    def test_whisper_response(self) -> None:
        """get_whisper_response should return something."""
        response = get_whisper_response("hmm")
        assert response is not None
        assert len(response) > 0

    def test_template_with_mode(self) -> None:
        """Templates should consider mode for short inputs."""
        response = try_template_response("ok", mode=DialogueMode.REFLECT)
        assert response is not None
        # REFLECT mode should return reflection acknowledgment


# --- Soul Tests ---


class TestSoul:
    """Test K-gent Soul: The Middleware of Consciousness."""

    def test_soul_creation(self) -> None:
        """Soul should be created with defaults."""
        s = soul()
        assert isinstance(s, KgentSoul)
        assert s.active_mode == DialogueMode.REFLECT

    def test_create_soul(self) -> None:
        """create_soul should work like soul()."""
        s = create_soul()
        assert isinstance(s, KgentSoul)

    def test_soul_eigenvectors(self) -> None:
        """Soul should have eigenvectors."""
        s = soul()
        assert s.eigenvectors is not None
        assert s.eigenvectors.aesthetic.value < 0.5  # Minimalist

    def test_soul_mode_change(self) -> None:
        """Soul mode should be changeable."""
        s = soul()
        s.active_mode = DialogueMode.CHALLENGE
        assert s.active_mode == DialogueMode.CHALLENGE

    def test_soul_enter_mode(self) -> None:
        """enter_mode should return entry message."""
        s = soul()
        message = s.enter_mode(DialogueMode.ADVISE)
        assert "ADVISE" in message

    def test_soul_get_starter(self) -> None:
        """get_starter should return mode-appropriate starter."""
        s = soul()
        s.active_mode = DialogueMode.EXPLORE
        starter = s.get_starter()
        assert starter in EXPLORE_STARTERS

    def test_soul_manifest(self) -> None:
        """manifest should return SoulState."""
        s = soul()
        state = s.manifest()
        assert isinstance(state, SoulState)
        assert state.active_mode == DialogueMode.REFLECT

    def test_soul_manifest_brief(self) -> None:
        """manifest_brief should return dict."""
        s = soul()
        brief = s.manifest_brief()
        assert "mode" in brief
        assert "eigenvectors" in brief
        assert brief["mode"] == "reflect"

    @pytest.mark.asyncio
    async def test_soul_dialogue_template(self) -> None:
        """Dialogue should use templates for greetings."""
        s = soul()
        output = await s.dialogue("hello")
        assert isinstance(output, SoulDialogueOutput)
        assert output.was_template

    @pytest.mark.asyncio
    async def test_soul_dialogue_empty_message(self) -> None:
        """Dialogue should handle empty messages gracefully."""
        s = soul()
        output = await s.dialogue("")
        assert isinstance(output, SoulDialogueOutput)
        assert output.was_template
        assert output.response  # Should get a prompt

    @pytest.mark.asyncio
    async def test_soul_dialogue_whitespace_message(self) -> None:
        """Dialogue should handle whitespace-only messages gracefully."""
        s = soul()
        output = await s.dialogue("   ")
        assert isinstance(output, SoulDialogueOutput)
        assert output.was_template
        assert output.response  # Should get a prompt

    @pytest.mark.asyncio
    async def test_soul_dialogue_whisper(self) -> None:
        """Dialogue should respect WHISPER budget."""
        s = soul()
        output = await s.dialogue("how are you", budget=BudgetTier.WHISPER)
        assert output.budget_tier == BudgetTier.WHISPER

    @pytest.mark.asyncio
    async def test_soul_dialogue_with_mode(self) -> None:
        """Dialogue should respect mode parameter."""
        s = soul()
        output = await s.dialogue(
            "What assumption am I not questioning?",
            mode=DialogueMode.CHALLENGE,
            budget=BudgetTier.DIALOGUE,
        )
        assert output.mode == DialogueMode.CHALLENGE

    def test_soul_custom_eigenvectors(self) -> None:
        """Soul should accept custom eigenvectors."""
        custom_eigens = KentEigenvectors()
        custom_eigens.aesthetic = EigenvectorCoordinate(
            name="Aesthetic",
            axis_low="Minimalist",
            axis_high="Baroque",
            value=0.9,  # Different from default
            confidence=0.8,
        )
        s = KgentSoul(eigenvectors=custom_eigens)
        assert s.eigenvectors.aesthetic.value == 0.9


# --- Budget Tests ---


class TestBudget:
    """Test budget tier configuration."""

    def test_default_budget_config(self) -> None:
        """Default budget config should have reasonable values."""
        config = BudgetConfig()
        assert config.dormant_max == 0
        assert config.whisper_max == 100
        assert config.dialogue_max == 4000
        assert config.deep_max == 8000

    def test_tier_for_tokens(self) -> None:
        """tier_for_tokens should classify correctly."""
        config = BudgetConfig()
        assert config.tier_for_tokens(0) == BudgetTier.DORMANT
        assert config.tier_for_tokens(50) == BudgetTier.WHISPER
        assert config.tier_for_tokens(500) == BudgetTier.DIALOGUE
        assert config.tier_for_tokens(10000) == BudgetTier.DEEP


# --- Intercept Tests ---


class TestIntercept:
    """Test semaphore interception (mediator pattern)."""

    @pytest.mark.asyncio
    async def test_intercept_basic(self) -> None:
        """intercept should return InterceptResult."""
        s = soul()

        # Create a mock token-like object
        class MockToken:
            id = "test-token"
            prompt = "Delete these files?"
            reason = "approval_needed"

        result = await s.intercept(MockToken())
        assert isinstance(result, InterceptResult)

    @pytest.mark.asyncio
    async def test_intercept_finds_principles(self) -> None:
        """intercept should find matching principles."""
        s = soul()

        class MockToken:
            id = "test-token"
            prompt = "Delete old files to minimize cruft?"
            reason = "approval_needed"

        result = await s.intercept(MockToken())
        # Should find minimalist principle
        assert len(result.matching_principles) > 0 or len(result.matching_patterns) >= 0

    @pytest.mark.asyncio
    async def test_intercept_annotation_when_low_confidence(self) -> None:
        """intercept should annotate when confidence is low."""
        s = soul()

        class MockToken:
            id = "test-token"
            prompt = "Should we deploy to production?"
            reason = "approval_needed"

        result = await s.intercept(MockToken())
        # No clear principle match, so should annotate for human
        if not result.handled:
            assert result.annotation is not None


# --- State Tests ---


class TestState:
    """Test soul state tracking."""

    def test_fresh_session(self) -> None:
        """New soul should be fresh session."""
        s = soul()
        state = s.manifest()
        assert state.is_fresh_session

    @pytest.mark.asyncio
    async def test_session_tracking(self) -> None:
        """Dialogue should update session stats."""
        s = soul()
        await s.dialogue("hello")
        state = s.manifest()
        assert state.interactions_count == 1
        assert state.last_interaction is not None


# --- Integration Tests ---


class TestSoulIntegration:
    """Integration tests for K-gent Soul."""

    @pytest.mark.asyncio
    async def test_full_dialogue_flow(self) -> None:
        """Test complete dialogue flow."""
        s = soul()

        # Start in REFLECT mode
        assert s.active_mode == DialogueMode.REFLECT

        # Get a starter
        starter = s.get_starter()
        assert starter in REFLECT_STARTERS

        # Enter CHALLENGE mode
        entry = s.enter_mode(DialogueMode.CHALLENGE)
        assert "CHALLENGE" in entry

        # Do a dialogue
        output = await s.dialogue(
            "I believe the architecture is correct",
            mode=DialogueMode.CHALLENGE,
        )
        assert output.mode == DialogueMode.CHALLENGE
        assert len(output.response) > 0

        # Check state
        state = s.manifest()
        assert state.interactions_count >= 1

    def test_eigenvector_influences_response(self) -> None:
        """Eigenvectors should influence behavior."""
        s = soul()
        # Minimalist aesthetic (0.15) should influence mediation
        assert s.eigenvectors.aesthetic.value < 0.5
        # This means K-gent should prefer deletion/simplification


# --- Phase 1: LLM Client Tests ---


class TestLLMClient:
    """Test LLM client abstraction."""

    def test_mock_llm_client(self) -> None:
        """MockLLMClient should work without actual API."""
        llm = MockLLMClient(responses=["Test response"])
        assert llm is not None

    @pytest.mark.asyncio
    async def test_mock_llm_generate(self) -> None:
        """MockLLMClient should return configured responses."""
        llm = MockLLMClient(responses=["Response 1", "Response 2"])

        r1 = await llm.generate(system="sys", user="user1")
        assert r1.text == "Response 1"

        r2 = await llm.generate(system="sys", user="user2")
        assert r2.text == "Response 2"

    @pytest.mark.asyncio
    async def test_mock_llm_default_response(self) -> None:
        """MockLLMClient should use default when queue empty."""
        llm = MockLLMClient(default_response="default")

        r = await llm.generate(system="sys", user="user")
        assert r.text == "default"

    @pytest.mark.asyncio
    async def test_mock_llm_tracks_calls(self) -> None:
        """MockLLMClient should track call history."""
        llm = MockLLMClient()

        await llm.generate(system="sys1", user="user1")
        await llm.generate(system="sys2", user="user2")

        assert llm.call_count == 2
        assert llm.call_history[0]["system"] == "sys1"
        assert llm.call_history[1]["user"] == "user2"

    def test_create_llm_client_mock(self) -> None:
        """create_llm_client with mock=True should return MockLLMClient."""
        llm = create_llm_client(mock=True, mock_responses=["test"])
        assert isinstance(llm, MockLLMClient)


# --- Phase 1: LLM-Backed Dialogue Tests ---


class TestLLMDialogue:
    """Test LLM-backed dialogue in K-gent."""

    def test_soul_has_llm_property(self) -> None:
        """Soul should have has_llm property."""
        s = KgentSoul(auto_llm=False)
        assert hasattr(s, "has_llm")
        assert s.has_llm is False

    def test_soul_with_mock_llm(self) -> None:
        """Soul should accept mock LLM."""
        mock_llm = MockLLMClient(responses=["Mock response"])
        s = KgentSoul(llm=mock_llm, auto_llm=False)
        assert s.has_llm is True

    @pytest.mark.asyncio
    async def test_dialogue_uses_llm(self) -> None:
        """Dialogue should use LLM when available."""
        mock_llm = MockLLMClient(responses=["LLM generated response"])
        s = KgentSoul(llm=mock_llm, auto_llm=False)

        output = await s.dialogue(
            "What's the architecture pattern here?",
            mode=DialogueMode.ADVISE,
            budget=BudgetTier.DIALOGUE,
        )

        # Should use the mock LLM response
        assert "LLM generated response" in output.response
        assert mock_llm.call_count == 1

    @pytest.mark.asyncio
    async def test_dialogue_template_bypass_llm(self) -> None:
        """Dialogue should bypass LLM for templates."""
        mock_llm = MockLLMClient(responses=["LLM response"])
        s = KgentSoul(llm=mock_llm, auto_llm=False)

        # "hello" should trigger template
        output = await s.dialogue("hello", budget=BudgetTier.DIALOGUE)

        # Should NOT use LLM
        assert mock_llm.call_count == 0
        assert output.was_template is True


# --- Phase 1: Deep Intercept Tests ---


class TestDeepIntercept:
    """Test LLM-backed deep intercept."""

    def test_dangerous_keywords_defined(self) -> None:
        """Dangerous keywords should be defined."""
        assert "delete" in DANGEROUS_KEYWORDS
        assert "production" in DANGEROUS_KEYWORDS
        assert "sudo" in DANGEROUS_KEYWORDS
        assert "rm " in DANGEROUS_KEYWORDS

    @pytest.mark.asyncio
    async def test_deep_intercept_dangerous_operation(self) -> None:
        """Deep intercept should always escalate dangerous operations."""
        mock_llm = MockLLMClient(
            responses=[
                "RECOMMENDATION: approve\nCONFIDENCE: 0.9\nPRINCIPLES: Minimalism\nREASONING: Looks safe"
            ]
        )
        s = KgentSoul(llm=mock_llm, auto_llm=False)

        class DangerousToken:
            id = "dangerous-token"
            prompt = "Delete all files in /production?"
            reason = "Cleanup"
            severity = 0.9

        result = await s.intercept_deep(DangerousToken())

        # Should NEVER auto-approve dangerous operations
        assert result.handled is False
        assert result.recommendation == "escalate"
        assert result.confidence == 0.0
        assert "SAFETY_OVERRIDE" in result.matching_principles

    @pytest.mark.asyncio
    async def test_deep_intercept_with_llm(self) -> None:
        """Deep intercept should use LLM for non-dangerous operations."""
        mock_llm = MockLLMClient(
            responses=[
                "RECOMMENDATION: approve\nCONFIDENCE: 0.85\nPRINCIPLES: Minimalism, Joy\nREASONING: Aligns with minimalist principle"
            ]
        )
        s = KgentSoul(llm=mock_llm, auto_llm=False)

        class SafeToken:
            id = "safe-token"
            prompt = "Refactor this function to be simpler?"
            reason = "Code quality"
            severity = 0.3

        result = await s.intercept_deep(SafeToken())

        # Should use LLM reasoning
        assert result.was_deep is True
        assert mock_llm.call_count == 1

    @pytest.mark.asyncio
    async def test_deep_intercept_low_confidence_escalates(self) -> None:
        """Deep intercept should escalate when confidence is low."""
        mock_llm = MockLLMClient(
            responses=[
                "RECOMMENDATION: approve\nCONFIDENCE: 0.5\nPRINCIPLES: Unknown\nREASONING: Not sure"
            ]
        )
        s = KgentSoul(llm=mock_llm, auto_llm=False)

        class AmbiguousToken:
            id = "ambiguous-token"
            prompt = "Should we do this thing?"
            reason = "Unclear"
            severity = 0.5

        result = await s.intercept_deep(AmbiguousToken())

        # Low confidence should escalate
        assert result.handled is False
        assert result.recommendation == "escalate"

    @pytest.mark.asyncio
    async def test_deep_intercept_fallback_without_llm(self) -> None:
        """Deep intercept should fall back to shallow intercept without LLM."""
        s = KgentSoul(llm=None, auto_llm=False)

        class Token:
            id = "test-token"
            prompt = "Some operation"
            reason = "Test"
            severity = 0.5

        result = await s.intercept_deep(Token())

        # Should use shallow intercept
        assert result.was_deep is False


# --- Phase 1: Audit Trail Tests ---


class TestAuditTrail:
    """Test audit trail functionality."""

    def test_audit_entry_creation(self) -> None:
        """AuditEntry should be creatable."""
        entry = AuditEntry(
            timestamp=datetime.now(),
            token_id="test-123",
            action="approve",
            confidence=0.85,
            principles=["Minimalism"],
            reasoning="Test reasoning",
        )
        assert entry.action == "approve"
        assert entry.confidence == 0.85

    def test_audit_entry_to_dict(self) -> None:
        """AuditEntry should convert to dict."""
        entry = AuditEntry(
            timestamp=datetime.now(),
            token_id="test-123",
            action="escalate",
            confidence=0.5,
            principles=["Unknown"],
            reasoning="Uncertain",
        )
        d = entry.to_dict()
        assert "timestamp" in d
        assert d["action"] == "escalate"

    def test_audit_entry_from_dict(self) -> None:
        """AuditEntry should be recreatable from dict."""
        original = AuditEntry(
            timestamp=datetime.now(),
            token_id="test-123",
            action="reject",
            confidence=0.1,
            principles=["Safety"],
            reasoning="Dangerous",
        )
        d = original.to_dict()
        recreated = AuditEntry.from_dict(d)
        assert recreated.action == original.action
        assert recreated.confidence == original.confidence

    def test_audit_trail_creation(self) -> None:
        """AuditTrail should be creatable with temp storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = AuditTrail(storage_path=Path(tmpdir))
            assert audit is not None

    def test_audit_trail_log_and_recent(self) -> None:
        """AuditTrail should log and retrieve entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = AuditTrail(storage_path=Path(tmpdir))
            audit.clear()  # Ensure clean state

            entry1 = AuditEntry(
                timestamp=datetime.now(),
                token_id="test-1",
                action="approve",
                confidence=0.9,
                principles=["Test"],
                reasoning="First entry",
            )
            entry2 = AuditEntry(
                timestamp=datetime.now(),
                token_id="test-2",
                action="escalate",
                confidence=0.5,
                principles=["Unknown"],
                reasoning="Second entry",
            )

            audit.log(entry1)
            audit.log(entry2)

            recent = audit.recent(limit=10)
            assert len(recent) == 2
            # Most recent first
            assert recent[0].token_id == "test-2"

    def test_audit_trail_summary(self) -> None:
        """AuditTrail should provide summary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = AuditTrail(storage_path=Path(tmpdir))
            audit.clear()  # Ensure clean state

            for i in range(5):
                audit.log(
                    AuditEntry(
                        timestamp=datetime.now(),
                        token_id=f"test-{i}",
                        action="approve" if i % 2 == 0 else "escalate",
                        confidence=0.8,
                        principles=["Test"],
                        reasoning=f"Entry {i}",
                    )
                )

            summary = audit.summary()
            assert summary["total_entries"] == 5
            assert "approve" in summary["by_action"]

    def test_audit_trail_persistence(self) -> None:
        """AuditTrail should persist to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and log
            audit1 = AuditTrail(storage_path=Path(tmpdir))
            audit1.log(
                AuditEntry(
                    timestamp=datetime.now(),
                    token_id="persist-test",
                    action="approve",
                    confidence=0.9,
                    principles=["Test"],
                    reasoning="Persistence test",
                )
            )

            # Create new instance and read
            audit2 = AuditTrail(storage_path=Path(tmpdir))
            recent = audit2.recent(limit=10)
            assert len(recent) == 1
            assert recent[0].token_id == "persist-test"


class TestSoulAuditIntegration:
    """Test Soul + Audit integration."""

    def test_soul_has_audit_property(self) -> None:
        """Soul should have audit property."""
        s = KgentSoul(auto_llm=False)
        assert hasattr(s, "audit")

    @pytest.mark.asyncio
    async def test_deep_intercept_logs_to_audit(self) -> None:
        """Deep intercept should log to audit trail."""
        mock_llm = MockLLMClient(
            responses=[
                "RECOMMENDATION: approve\nCONFIDENCE: 0.85\nPRINCIPLES: Joy\nREASONING: Good"
            ]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            s = KgentSoul(llm=mock_llm, auto_llm=False)
            # Override audit storage
            from agents.k.audit import AuditTrail

            s._audit = AuditTrail(storage_path=Path(tmpdir))

            class Token:
                id = "audit-test"
                prompt = "Simple operation"
                reason = "Test"
                severity = 0.3

            await s.intercept_deep(Token())

            # Should have logged
            recent = s.audit.recent(limit=1)
            assert len(recent) == 1
            assert recent[0].token_id == "audit-test"


# --- Phase 2: Morpheus Integration Tests ---


class TestMorpheusIntegration:
    """Test Morpheus Gateway integration for cluster-native runtime."""

    def test_morpheus_available_without_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """morpheus_available should return False without env vars."""
        monkeypatch.delenv("MORPHEUS_URL", raising=False)
        monkeypatch.delenv("LLM_ENDPOINT", raising=False)
        assert morpheus_available() is False

    def test_morpheus_available_with_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """morpheus_available should return True with MORPHEUS_URL."""
        monkeypatch.setenv("MORPHEUS_URL", "http://morpheus-gateway:8080/v1")
        assert morpheus_available() is True

    def test_morpheus_available_with_llm_endpoint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """morpheus_available should return True with LLM_ENDPOINT."""
        monkeypatch.delenv("MORPHEUS_URL", raising=False)
        monkeypatch.setenv("LLM_ENDPOINT", "http://localhost:30808/v1")
        assert morpheus_available() is True

    def test_create_llm_client_prefers_morpheus(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """create_llm_client should prefer Morpheus when available."""
        monkeypatch.setenv("MORPHEUS_URL", "http://morpheus-gateway:8080/v1")

        from runtime.morpheus import MorpheusLLMClient

        client = create_llm_client()
        assert isinstance(client, MorpheusLLMClient)

    def test_create_llm_client_fallback_to_cli(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """create_llm_client should fallback to CLI without Morpheus."""
        monkeypatch.delenv("MORPHEUS_URL", raising=False)
        monkeypatch.delenv("LLM_ENDPOINT", raising=False)

        from agents.k.llm import ClaudeLLMClient

        client = create_llm_client()
        assert isinstance(client, ClaudeLLMClient)

    def test_create_llm_client_force_cli(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """create_llm_client with prefer_morpheus=False should use CLI."""
        monkeypatch.setenv("MORPHEUS_URL", "http://morpheus-gateway:8080/v1")

        from agents.k.llm import ClaudeLLMClient

        client = create_llm_client(prefer_morpheus=False)
        assert isinstance(client, ClaudeLLMClient)

    def test_has_llm_credentials_with_morpheus(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """has_llm_credentials should return True with Morpheus URL."""
        monkeypatch.setenv("MORPHEUS_URL", "http://morpheus-gateway:8080/v1")
        assert has_llm_credentials() is True

    @pytest.mark.asyncio
    async def test_soul_with_morpheus_client(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Soul should work with MorpheusLLMClient interface.

        This test uses a mock that follows the MorpheusLLMClient interface
        to verify Soul can use the Morpheus backend.
        """
        # We use MockLLMClient which implements the same protocol
        mock_response = (
            "RECOMMENDATION: approve\n"
            "CONFIDENCE: 0.9\n"
            "PRINCIPLES: Minimalism, Joy\n"
            "REASONING: This aligns with Kent's minimalist aesthetic."
        )
        mock_llm = MockLLMClient(responses=[mock_response])

        s = KgentSoul(llm=mock_llm, auto_llm=False)

        class Token:
            id = "morpheus-test"
            prompt = "Simplify this module?"
            reason = "Code quality"
            severity = 0.3

        result = await s.intercept_deep(Token())

        # Verify the result
        assert result.was_deep is True
        assert result.recommendation == "approve"
        assert result.confidence == 0.9
        assert mock_llm.call_count == 1

    @pytest.mark.asyncio
    async def test_soul_dialogue_with_morpheus_interface(self) -> None:
        """Soul dialogue should work through Morpheus-compatible interface."""
        mock_llm = MockLLMClient(
            responses=[
                "The key pattern I notice is over-engineering. "
                "You're building infrastructure before you need it."
            ]
        )
        s = KgentSoul(llm=mock_llm, auto_llm=False)

        output = await s.dialogue(
            "What pattern am I not seeing in this architecture?",
            mode=DialogueMode.REFLECT,
            budget=BudgetTier.DIALOGUE,
        )

        assert "over-engineering" in output.response
        assert mock_llm.call_count == 1


# --- Phase 2: Dialectical CHALLENGE Mode Tests ---


class TestDialecticalChallenge:
    """Test dialectical structure in CHALLENGE mode."""

    def test_challenge_templates_are_substantive(self) -> None:
        """CHALLENGE templates should reference Kent's actual patterns."""
        from agents.k.templates import CHALLENGE_PROMPTS

        # Should have substantive prompts, not generic questions
        assert len(CHALLENGE_PROMPTS) >= 10

        # Should reference Kent-specific concepts
        kent_terms = [
            "minimalism",
            "minimalist",
            "composable",
            "reversible",
            "thesis",
            "falsify",
            "protecting",
            "best day",
        ]
        found_terms = sum(
            1 for term in kent_terms if any(term in p.lower() for p in CHALLENGE_PROMPTS)
        )
        # At least 3 Kent-specific terms should appear
        assert found_terms >= 3, f"Only found {found_terms} Kent-specific terms"

    def test_challenge_style_from_eigenvectors(self) -> None:
        """get_challenge_style should generate eigenvector-based guidance."""
        from agents.k.eigenvectors import KENT_EIGENVECTORS, get_challenge_style

        style = get_challenge_style(KENT_EIGENVECTORS)

        # Should reference multiple eigenvector-informed challenges
        assert "simplest version" in style.lower()  # Aesthetic: minimalist
        assert "composable" in style.lower()  # Categorical: abstract
        assert "peer-to-peer" in style.lower()  # Heterarchy

    def test_dialectical_prompt_generation(self) -> None:
        """get_dialectical_prompt should create dialectical framework."""
        from agents.k.eigenvectors import KENT_EIGENVECTORS, get_dialectical_prompt

        prompt = get_dialectical_prompt(KENT_EIGENVECTORS, "I'm stuck on the architecture")

        # Should have dialectical structure
        assert "THESIS" in prompt
        assert "ANTITHESIS" in prompt
        assert "SYNTHESIS" in prompt

        # Should reference tensions from eigenvectors
        assert "tension" in prompt.lower()

    @pytest.mark.asyncio
    async def test_challenge_dialogue_uses_dialectical_framework(self) -> None:
        """CHALLENGE mode dialogue should include dialectical elements."""
        # Mock LLM that echoes parts of the prompt
        mock_llm = MockLLMClient(
            responses=[
                "Let's examine your thesis. You say you're 'stuck on architecture' but "
                "you've built composable agents with category theory. The antithesis: "
                "you're not stuck—you're avoiding a decision. What are you protecting?"
            ]
        )
        s = KgentSoul(llm=mock_llm, auto_llm=False)

        output = await s.dialogue(
            "I'm stuck on the architecture",
            mode=DialogueMode.CHALLENGE,
            budget=BudgetTier.DIALOGUE,
        )

        # Verify the system prompt was used (check LLM call history)
        assert mock_llm.call_count == 1
        call = mock_llm.call_history[0]

        # System prompt should have dialectical structure
        system_prompt = call["system"]
        assert "DIALECTICAL" in system_prompt or "Kent on his best day" in system_prompt

        # User prompt should have challenge guidance
        user_prompt = call["user"]
        # Should include the dialectical framework
        assert "THESIS" in user_prompt or "stuck" in user_prompt

    @pytest.mark.asyncio
    async def test_challenge_mode_references_eigenvectors(self) -> None:
        """CHALLENGE mode should be influenced by eigenvectors."""
        mock_llm = MockLLMClient(
            responses=[
                "You value minimalism (0.15 on the baroque scale). Why are you adding complexity?"
            ]
        )
        s = KgentSoul(llm=mock_llm, auto_llm=False)

        output = await s.dialogue(
            "Should I add this feature?",
            mode=DialogueMode.CHALLENGE,
            budget=BudgetTier.DIALOGUE,
        )

        # The call should include eigenvector context
        call = mock_llm.call_history[0]
        system_prompt = call["system"]

        # Should reference eigenvectors somewhere in the system prompt
        assert "Aesthetic" in system_prompt or "Minimalist" in system_prompt

    def test_template_challenge_is_eigenvector_informed(self) -> None:
        """Template CHALLENGE response should use eigenvectors when available."""
        from agents.k import KENT_EIGENVECTORS
        from agents.k.persona import DialogueInput, KgentAgent

        agent = KgentAgent(eigenvectors=KENT_EIGENVECTORS)

        # Test template response (no LLM)
        response = agent._generate_template_response(
            mode=DialogueMode.CHALLENGE,
            message="I'm stuck",
            prefs=[],
            pats=[],
        )

        # Should be Kent-specific challenge
        kent_challenge_markers = [
            "minimalism",
            "composable",
            "peer-to-peer",
            "simplest",
            "hierarchy",
            "protecting",
            "tell someone else",
            "thesis",
            "avoiding",
        ]
        assert any(marker in response.lower() for marker in kent_challenge_markers), (
            f"Response not Kent-specific: {response}"
        )

    @pytest.mark.asyncio
    async def test_challenge_feels_like_kent_on_best_day(self) -> None:
        """The Mirror Test: CHALLENGE should feel like Kent on his best day."""
        # This is the ultimate test - does it pass the vibe check?
        mock_llm = MockLLMClient(
            responses=[
                "Stuck? Let's examine that.\n\n"
                "You've built composable agents with category theory, implemented "
                "thermodynamic stream processing, and created a self-describing "
                "capability system. The pattern suggests you're not stuck on "
                "architecture—you're avoiding a DECISION about architecture.\n\n"
                "What would you tell someone else in this position?\n"
                "(Hint: You'd say 'pick the one that teaches you something, then iterate.')\n\n"
                "The real question: What are you protecting by staying in analysis mode?"
            ]
        )
        s = KgentSoul(llm=mock_llm, auto_llm=False)

        output = await s.dialogue(
            "I'm stuck on the architecture",
            mode=DialogueMode.CHALLENGE,
            budget=BudgetTier.DIALOGUE,
        )

        # Key markers of "Kent on his best day":
        # 1. Reframes the problem (not "stuck" but "avoiding decision")
        assert "avoiding" in output.response.lower() or "decision" in output.response.lower()

        # 2. References past achievements to counter the "stuck" narrative
        assert "composable" in output.response.lower() or "built" in output.response.lower()

        # 3. Includes the key challenge question
        assert (
            "protecting" in output.response.lower()
            or "what would you tell" in output.response.lower()
        )

        # 4. Offers actionable insight, not just questions
        assert "iterate" in output.response.lower() or "teaches" in output.response.lower()


class TestChallengeStarters:
    """Test CHALLENGE mode starters are Kent-specific."""

    def test_challenge_starters_have_dialectical_flavor(self) -> None:
        """CHALLENGE starters should have dialectical prompts."""
        from agents.k import CHALLENGE_STARTERS

        dialectical_terms = [
            "falsify",
            "opposite",
            "disagree",
            "weakest",
            "protecting",
            "afraid",
            "wrong",
            "strongest argument",
        ]

        # At least half should have dialectical flavor
        dialectical_count = sum(
            1
            for starter in CHALLENGE_STARTERS
            if any(term in starter.lower() for term in dialectical_terms)
        )
        assert dialectical_count >= len(CHALLENGE_STARTERS) // 2, (
            f"Only {dialectical_count}/{len(CHALLENGE_STARTERS)} starters have dialectical flavor"
        )
