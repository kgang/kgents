"""
Tests for F-gents intent parsing (Phase 1: Understand).

Validates the NaturalLanguage → Intent morphism from spec/f-gents/forge.md.
"""

from agents.f.intent import (
    Dependency,
    DependencyType,
    Example,
    Intent,
    parse_intent,
)


class TestIntentDataclasses:
    """Test the basic dataclass structures."""

    def test_dependency_creation(self) -> None:
        """Dependency can be instantiated with minimal fields."""
        dep = Dependency(name="WeatherAPI", type=DependencyType.REST_API)
        assert dep.name == "WeatherAPI"
        assert dep.type == DependencyType.REST_API
        assert dep.required is True

    def test_dependency_optional_fields(self) -> None:
        """Dependency accepts optional fields."""
        dep = Dependency(
            name="PostgreSQL",
            type=DependencyType.DATABASE,
            description="User data storage",
            required=False,
        )
        assert dep.description == "User data storage"
        assert dep.required is False

    def test_example_creation(self) -> None:
        """Example can be created with test case data."""
        example = Example(
            input="Seattle, WA",
            expected_output={"temp": 55, "condition": "cloudy"},
            description="Test Seattle weather query",
        )
        assert example.input == "Seattle, WA"
        assert example.expected_output["temp"] == 55

    def test_intent_minimal(self) -> None:
        """Intent can be created with just a purpose."""
        intent = Intent(purpose="Summarize papers")
        assert intent.purpose == "Summarize papers"
        assert intent.behavior == []
        assert intent.constraints == []
        assert intent.tone is None


class TestPurposeExtraction:
    """Test _extract_purpose logic."""

    def test_simple_purpose(self) -> None:
        """Extract purpose from simple description."""
        text = "Summarize technical papers for executive reading."
        intent = parse_intent(text)
        assert "summarize" in intent.purpose.lower()

    def test_remove_agent_prefix(self) -> None:
        """Remove 'Create an agent that' prefix."""
        text = "Create an agent that fetches weather data"
        intent = parse_intent(text)
        assert not intent.purpose.lower().startswith("create an agent")
        assert "fetch" in intent.purpose.lower()

    def test_i_need_prefix(self) -> None:
        """Remove 'I need an agent that' prefix."""
        text = "I need an agent that processes CSV files"
        intent = parse_intent(text)
        assert not intent.purpose.lower().startswith("i need")
        assert "process" in intent.purpose.lower()

    def test_first_sentence_extraction(self) -> None:
        """Extract first sentence as purpose from multi-sentence input."""
        text = "Fetch weather data and return JSON. It should be fast and reliable."
        intent = parse_intent(text)
        assert "fetch weather data" in intent.purpose.lower()


class TestBehaviorExtraction:
    """Test behavior/capability detection."""

    def test_fetch_behavior(self) -> None:
        """Detect 'fetch' action."""
        text = "Fetch weather data from API"
        intent = parse_intent(text)
        assert any("fetch" in b.lower() for b in intent.behavior)

    def test_summarize_behavior(self) -> None:
        """Detect 'summarize' action."""
        text = "Summarize technical papers"
        intent = parse_intent(text)
        assert any("summarize" in b.lower() for b in intent.behavior)

    def test_multiple_behaviors(self) -> None:
        """Detect multiple behaviors in one description."""
        text = "Fetch data, analyze patterns, and generate reports"
        intent = parse_intent(text)
        assert len(intent.behavior) >= 2  # Should detect fetch, analyze, generate

    def test_transform_behavior(self) -> None:
        """Detect 'transform' action."""
        text = "Transform CSV to JSON format"
        intent = parse_intent(text)
        assert any("transform" in b.lower() for b in intent.behavior)


class TestConstraintExtraction:
    """Test constraint/requirement detection."""

    def test_concise_constraint(self) -> None:
        """Detect 'concise' constraint."""
        text = "Summarize papers. Output should be concise."
        intent = parse_intent(text)
        assert any("concise" in c.lower() for c in intent.constraints)

    def test_objective_constraint(self) -> None:
        """Detect 'objective' constraint."""
        text = "Summarize with an objective tone"
        intent = parse_intent(text)
        assert any("objective" in c.lower() for c in intent.constraints)

    def test_must_constraint(self) -> None:
        """Extract explicit 'must' constraints."""
        text = "The agent must handle network errors gracefully"
        intent = parse_intent(text)
        # Should capture the sentence containing 'must'
        assert len(intent.constraints) > 0

    def test_multiple_constraints(self) -> None:
        """Detect multiple constraints."""
        text = "Agent should be fast, secure, and idempotent"
        intent = parse_intent(text)
        assert len(intent.constraints) >= 2


class TestToneExtraction:
    """Test tone/personality detection."""

    def test_friendly_tone(self) -> None:
        """Detect 'friendly' tone."""
        text = "Create a friendly agent that greets users"
        intent = parse_intent(text)
        assert intent.tone == "friendly"

    def test_formal_tone(self) -> None:
        """Detect 'formal' tone."""
        text = "Use a formal tone for legal documents"
        intent = parse_intent(text)
        assert intent.tone == "formal"

    def test_no_tone(self) -> None:
        """Return None when no tone specified."""
        text = "Fetch weather data"
        intent = parse_intent(text)
        assert intent.tone is None


class TestDependencyAnalysis:
    """Test external dependency detection."""

    def test_api_dependency(self) -> None:
        """Detect API dependency."""
        text = "Fetch data from REST API"
        intent = parse_intent(text)
        assert any(d.type == DependencyType.REST_API for d in intent.dependencies)

    def test_database_dependency(self) -> None:
        """Detect database dependency."""
        text = "Store results in PostgreSQL database"
        intent = parse_intent(text)
        assert any(d.type == DependencyType.DATABASE for d in intent.dependencies)

    def test_file_dependency(self) -> None:
        """Detect file system dependency."""
        text = "Read data from CSV file and process it"
        intent = parse_intent(text)
        assert any(d.type == DependencyType.FILE_SYSTEM for d in intent.dependencies)

    def test_network_dependency(self) -> None:
        """Detect network dependency."""
        text = "Download files from remote server"
        intent = parse_intent(text)
        assert any(d.type == DependencyType.NETWORK for d in intent.dependencies)

    def test_multiple_dependencies(self) -> None:
        """Detect multiple dependencies."""
        text = "Fetch from API, store in database, and export to CSV"
        intent = parse_intent(text)
        assert len(intent.dependencies) >= 2


class TestAmbiguityDetection:
    """Test ambiguity detection for H-gent escalation."""

    def test_vague_quantifier(self) -> None:
        """Detect vague quantifiers."""
        text = "Process some files from the directory"
        intent = parse_intent(text)
        assert any("vague" in a.lower() for a in intent.ambiguities)

    def test_missing_error_handling(self) -> None:
        """Detect missing error handling specification."""
        text = "Fetch weather data"
        intent = parse_intent(text)
        assert any("error" in a.lower() for a in intent.ambiguities)

    def test_missing_performance_spec(self) -> None:
        """Detect missing performance requirements."""
        text = "Summarize papers"
        intent = parse_intent(text)
        assert any("performance" in a.lower() for a in intent.ambiguities)

    def test_no_ambiguities_when_complete(self) -> None:
        """No ambiguities when description is complete."""
        text = "Fetch data with fast timeout and robust error handling"
        intent = parse_intent(text)
        # Should have fewer ambiguities than incomplete descriptions
        assert len(intent.ambiguities) < 3  # Still may have some


class TestRealWorldExamples:
    """Test with realistic agent descriptions from spec."""

    def test_weather_agent(self) -> None:
        """Parse weather fetcher agent description."""
        text = "Create an agent that fetches weather data and returns JSON."
        intent = parse_intent(text)

        assert "weather" in intent.purpose.lower()
        assert any("fetch" in b.lower() for b in intent.behavior)
        assert any(
            d.type in [DependencyType.REST_API, DependencyType.NETWORK] for d in intent.dependencies
        )

    def test_summarizer_agent(self) -> None:
        """Parse summarizer agent description from spec."""
        text = (
            "I need an agent that summarizes technical papers for executive reading. "
            "Concise, objective, no jargon. Output JSON with title, key findings, confidence score."
        )
        intent = parse_intent(text)

        assert "summarize" in intent.purpose.lower()
        assert any("concise" in c.lower() for c in intent.constraints)
        assert any("objective" in c.lower() for c in intent.constraints)
        assert intent.tone == "concise"

    def test_complex_pipeline_agent(self) -> None:
        """Parse complex multi-stage agent."""
        text = (
            "Build an agent that fetches data from REST API, "
            "validates it, transforms to JSON, and stores in database. "
            "Must be idempotent and handle errors gracefully."
        )
        intent = parse_intent(text)

        assert len(intent.behavior) >= 3  # fetch, validate, transform
        assert len(intent.dependencies) >= 2  # API + database
        assert any("idempotent" in c.lower() for c in intent.constraints)


class TestIntentMetadata:
    """Test metadata preservation."""

    def test_raw_text_preserved(self) -> None:
        """Original text is preserved in raw_text field."""
        text = "Fetch weather data"
        intent = parse_intent(text)
        assert intent.raw_text == text

    def test_examples_empty_by_default(self) -> None:
        """Examples list is empty (added separately)."""
        intent = parse_intent("Fetch data")
        assert intent.examples == []


# Integration test
class TestParseIntentIntegration:
    """End-to-end integration tests."""

    def test_full_pipeline(self) -> None:
        """Complete parse_intent pipeline."""
        text = (
            "Create an agent that fetches weather data from API, "
            "analyzes patterns, and exports results to CSV. "
            "Must be fast, secure, and handle network errors. "
            "Use a professional tone."
        )

        intent = parse_intent(text)

        # Verify all components populated
        assert intent.purpose
        assert len(intent.behavior) > 0
        assert len(intent.constraints) > 0
        assert intent.tone == "professional"
        assert len(intent.dependencies) > 0
        assert intent.raw_text == text
        # May have some ambiguities detected

    def test_minimal_input(self) -> None:
        """Handle minimal input gracefully."""
        text = "Process data"
        intent = parse_intent(text)

        assert intent.purpose == "Process data"
        # Should still work, just with fewer extracted fields
        assert isinstance(intent.behavior, list)
        assert isinstance(intent.constraints, list)
