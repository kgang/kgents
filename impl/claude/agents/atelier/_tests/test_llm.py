"""
Tests for the LLM backing module.

Tests ClaudeCLIRuntime integration for artisan work.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.atelier.llm import (
    ArtisanLLMAgent,
    ArtisanRequest,
    ArtisanResponse,
    get_runtime,
    reset_runtime,
)


class TestArtisanResponse:
    """Tests for ArtisanResponse dataclass."""

    def test_create(self):
        """Basic response creation."""
        response = ArtisanResponse(
            interpretation="understood as a greeting",
            considerations=["warmth", "brevity"],
            content="Hello, friend",
            form="greeting",
        )
        assert response.interpretation == "understood as a greeting"
        assert response.form == "greeting"

    def test_empty_considerations(self):
        """Response with no considerations."""
        response = ArtisanResponse(
            interpretation="",
            considerations=[],
            content="test",
            form="test",
        )
        assert response.considerations == []


class TestArtisanRequest:
    """Tests for ArtisanRequest dataclass."""

    def test_create(self):
        """Basic request creation."""
        request = ArtisanRequest(
            prompt="write a haiku",
            artisan_name="The Calligrapher",
            artisan_personality="gentle wordsmith",
        )
        assert request.prompt == "write a haiku"
        assert request.artisan_name == "The Calligrapher"


class TestArtisanLLMAgent:
    """Tests for the ArtisanLLMAgent."""

    @pytest.fixture
    def agent(self):
        return ArtisanLLMAgent()

    def test_name(self, agent):
        """Agent has expected name."""
        assert agent.name == "ArtisanAgent"

    def test_build_prompt(self, agent):
        """build_prompt returns proper context."""
        request = ArtisanRequest(
            prompt="write something",
            artisan_name="Test Artisan",
            artisan_personality="creative",
        )
        context = agent.build_prompt(request)

        assert "creative" in context.system_prompt
        assert "Test Artisan" in context.system_prompt
        assert context.messages[0]["content"] == "write something"
        assert context.temperature == 0.8

    def test_parse_response_valid_json(self, agent):
        """Parse valid JSON response."""
        response = agent.parse_response(
            '{"interpretation": "test", "considerations": ["a"], "content": "hi", "form": "note"}'
        )
        assert response.interpretation == "test"
        assert response.content == "hi"
        assert response.form == "note"

    def test_parse_response_with_markdown(self, agent):
        """Parse JSON wrapped in markdown."""
        response = agent.parse_response(
            '```json\n{"interpretation": "test", "considerations": [], "content": "hi", "form": "note"}\n```'
        )
        assert response.content == "hi"

    def test_parse_response_with_extra_text(self, agent):
        """Parse JSON with surrounding text."""
        response = agent.parse_response(
            'Here is my response:\n{"interpretation": "test", "considerations": [], "content": "hi", "form": "note"}\nThank you!'
        )
        assert response.content == "hi"

    def test_parse_response_fallback(self, agent):
        """Invalid JSON falls back to raw text."""
        response = agent.parse_response("just some text without json")
        assert response.content == "just some text without json"
        assert response.form == "reflection"
        assert response.interpretation == "Created from request"

    def test_parse_response_partial_json(self, agent):
        """Partial JSON with missing fields."""
        response = agent.parse_response('{"content": "hi", "form": "note"}')
        assert response.content == "hi"
        assert response.interpretation == ""  # Defaults to empty


class TestRuntimeSingleton:
    """Tests for runtime singleton management."""

    def test_reset_runtime(self):
        """reset_runtime clears singleton."""
        reset_runtime()
        # Import after reset to get fresh state
        import agents.atelier.llm as mod

        assert mod._runtime is None

    @patch("shutil.which")
    def test_get_runtime_missing_cli(self, mock_which):
        """get_runtime raises if claude CLI not found."""
        mock_which.return_value = None
        reset_runtime()

        with pytest.raises(RuntimeError, match="Claude CLI not found"):
            get_runtime()

    @patch("shutil.which")
    @patch("agents.atelier.llm.ClaudeCLIRuntime")
    def test_get_runtime_creates_instance(self, mock_runtime_cls, mock_which):
        """get_runtime creates ClaudeCLIRuntime."""
        mock_which.return_value = "/usr/local/bin/claude"
        mock_runtime_cls.return_value = MagicMock()
        reset_runtime()

        runtime = get_runtime()

        mock_runtime_cls.assert_called_once()
        assert runtime is not None


class TestJSONExtraction:
    """Tests for JSON extraction edge cases."""

    @pytest.fixture
    def agent(self):
        return ArtisanLLMAgent()

    def test_nested_json(self, agent):
        """Handle nested JSON objects."""
        response = agent.parse_response(
            '{"interpretation": "test", "considerations": [], "content": "has {nested} braces", "form": "note"}'
        )
        assert "nested" in response.content

    def test_json_with_newlines(self, agent):
        """Handle JSON with newlines."""
        response = agent.parse_response(
            """{
  "interpretation": "test",
  "considerations": ["a", "b"],
  "content": "multi\\nline",
  "form": "note"
}"""
        )
        assert response.interpretation == "test"

    def test_multiple_code_blocks(self, agent):
        """Handle multiple code blocks (take first JSON)."""
        response = agent.parse_response(
            """Some text
```json
{"interpretation": "first", "considerations": [], "content": "a", "form": "x"}
```
More text
```json
{"interpretation": "second", "considerations": [], "content": "b", "form": "y"}
```
"""
        )
        # Should get first valid JSON
        assert response.interpretation == "first"
