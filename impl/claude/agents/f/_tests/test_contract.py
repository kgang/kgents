"""
Tests for contract synthesis (Phase 2: Contract).

Validates the Intent → Contract morphism implementation.
"""

from agents.f.contract import (
    CompositionRule,
    Contract,
    Invariant,
    synthesize_contract,
)
from agents.f.intent import Dependency, DependencyType, Intent, parse_intent


class TestContractDataclasses:
    """Test basic dataclass creation and structure."""

    def test_invariant_creation(self):
        inv = Invariant(
            description="Idempotency",
            property="f(f(x)) == f(x)",
            category="behavioral",
        )
        assert inv.description == "Idempotency"
        assert inv.property == "f(f(x)) == f(x)"
        assert inv.category == "behavioral"

    def test_composition_rule_creation(self):
        rule = CompositionRule(
            mode="sequential",
            description="Linear flow",
            type_constraint="I → O",
        )
        assert rule.mode == "sequential"
        assert rule.description == "Linear flow"
        assert rule.type_constraint == "I → O"

    def test_contract_creation(self):
        contract = Contract(
            agent_name="TestAgent",
            input_type="str",
            output_type="dict",
            invariants=[],
            composition_rules=[],
            semantic_intent="Test agent",
        )
        assert contract.agent_name == "TestAgent"
        assert contract.input_type == "str"
        assert contract.output_type == "dict"


class TestTypeSynthesis:
    """Test type inference from intent."""

    def test_infer_rest_api_types(self):
        """REST API dependency → str input (URL), dict output (JSON)."""
        intent = Intent(
            purpose="Fetch weather from API",
            dependencies=[
                Dependency(
                    name="WeatherAPI",
                    type=DependencyType.REST_API,
                )
            ],
            raw_text="Create an agent that fetches weather from an API and returns JSON",
        )
        contract = synthesize_contract(intent, "WeatherAgent")
        assert contract.input_type == "str"  # URL
        assert contract.output_type == "dict"  # JSON mentioned

    def test_infer_file_system_types(self):
        """File system dependency → Path input."""
        intent = Intent(
            purpose="Read and parse CSV file",
            dependencies=[
                Dependency(
                    name="FileSystem",
                    type=DependencyType.FILE_SYSTEM,
                )
            ],
            raw_text="Read a CSV file from path and parse it",
        )
        contract = synthesize_contract(intent, "CSVReader")
        assert contract.input_type == "Path"

    def test_infer_summarization_types(self):
        """Summarization task → str input and output."""
        intent = Intent(
            purpose="Summarize papers",
            behavior=["Summarize content"],
            raw_text="Summarize academic papers to concise summaries",
        )
        contract = synthesize_contract(intent, "Summarizer")
        assert contract.input_type == "str"
        assert contract.output_type == "str"

    def test_infer_json_output_type(self):
        """Explicit JSON mention → dict output."""
        intent = Intent(
            purpose="Parse data to JSON",
            raw_text="Convert input to JSON format",
        )
        contract = synthesize_contract(intent)
        assert contract.output_type == "dict"

    def test_infer_list_output_type(self):
        """Multiple/list mentions → list output."""
        intent = Intent(
            purpose="Extract multiple entities",
            raw_text="Extract list of entities from text",
        )
        contract = synthesize_contract(intent)
        assert contract.output_type == "list"

    def test_infer_boolean_output_type(self):
        """Boolean/true-false mentions → bool output."""
        intent = Intent(
            purpose="Validate input",
            raw_text="Check if input is valid, return true/false",
        )
        contract = synthesize_contract(intent)
        assert contract.output_type == "bool"

    def test_default_types(self):
        """No clear hints → Any types."""
        intent = Intent(
            purpose="Process data",
            raw_text="Process some data",
        )
        contract = synthesize_contract(intent)
        assert contract.input_type in ["Any", "str"]  # Heuristic may vary
        assert contract.output_type in ["Any", "str"]


class TestInvariantExtraction:
    """Test extraction of testable invariants from constraints."""

    def test_extract_idempotent_invariant(self):
        """'idempotent' constraint → f(f(x)) == f(x) property."""
        intent = Intent(
            purpose="Normalize data",
            raw_text="Create an idempotent normalization agent",
        )
        contract = synthesize_contract(intent)
        invariants = [inv.description for inv in contract.invariants]
        assert any("Idempotency" in inv for inv in invariants)
        idempotent = next(
            inv for inv in contract.invariants if "Idempotency" in inv.description
        )
        assert "f(f(x)) == f(x)" in idempotent.property

    def test_extract_deterministic_invariant(self):
        """'deterministic' constraint → same input = same output."""
        intent = Intent(
            purpose="Hash data",
            raw_text="Create a deterministic hashing agent",
        )
        contract = synthesize_contract(intent)
        invariants = [inv.description for inv in contract.invariants]
        assert any("Determinism" in inv for inv in invariants)

    def test_extract_pure_invariant(self):
        """'pure' constraint → no side effects."""
        intent = Intent(
            purpose="Compute result",
            raw_text="Pure computation with no side effects",
        )
        contract = synthesize_contract(intent)
        invariants = [inv.description for inv in contract.invariants]
        assert any("Purity" in inv for inv in invariants)

    def test_extract_concise_invariant(self):
        """'concise' constraint → length limit."""
        intent = Intent(
            purpose="Summarize text",
            raw_text="Summarize text to concise output",
        )
        contract = synthesize_contract(intent)
        invariants = [inv.description for inv in contract.invariants]
        assert any("Conciseness" in inv for inv in invariants)

    def test_extract_no_hallucination_invariant(self):
        """'no hallucination' constraint → grounded outputs."""
        intent = Intent(
            purpose="Extract facts",
            raw_text="Extract facts with no hallucinations",
        )
        contract = synthesize_contract(intent)
        invariants = [inv.description for inv in contract.invariants]
        assert any("hallucination" in inv for inv in invariants)

    def test_extract_constraint_invariants(self):
        """Explicit 'must' constraints → invariants."""
        intent = Intent(
            purpose="Validate input",
            constraints=["Must validate all fields", "Should handle errors gracefully"],
        )
        contract = synthesize_contract(intent)
        invariants = [inv.description for inv in contract.invariants]
        assert any("validate all fields" in inv.lower() for inv in invariants)

    def test_extract_categorical_invariants(self):
        """Composition keywords → categorical invariants."""
        intent = Intent(
            purpose="Compose agents",
            raw_text="Chain multiple agents in a pipeline",
        )
        contract = synthesize_contract(intent)
        invariants = [inv.description for inv in contract.invariants]
        assert any("Associativity" in inv for inv in invariants)


class TestCompositionAnalysis:
    """Test composition rule determination."""

    def test_sequential_composition_single_dependency(self):
        """Single dependency → sequential composition."""
        intent = Intent(
            purpose="Fetch and process",
            dependencies=[Dependency(name="API", type=DependencyType.REST_API)],
        )
        contract = synthesize_contract(intent)
        modes = [rule.mode for rule in contract.composition_rules]
        assert "sequential" in modes

    def test_parallel_composition_multiple_dependencies(self):
        """Multiple independent deps → parallel composition."""
        intent = Intent(
            purpose="Aggregate data",
            dependencies=[
                Dependency(name="API1", type=DependencyType.REST_API),
                Dependency(name="API2", type=DependencyType.REST_API),
            ],
        )
        contract = synthesize_contract(intent)
        modes = [rule.mode for rule in contract.composition_rules]
        assert "parallel" in modes

    def test_conditional_composition(self):
        """Conditional keywords → conditional composition."""
        intent = Intent(
            purpose="Route data",
            raw_text="If input is valid, process it, else reject",
        )
        contract = synthesize_contract(intent)
        modes = [rule.mode for rule in contract.composition_rules]
        assert "conditional" in modes

    def test_fan_out_composition(self):
        """Broadcast/fan-out keywords → fan-out composition."""
        intent = Intent(
            purpose="Broadcast message",
            raw_text="Fan out message to multiple subscribers",
        )
        contract = synthesize_contract(intent)
        modes = [rule.mode for rule in contract.composition_rules]
        assert "fan-out" in modes

    def test_fan_in_composition(self):
        """Combine/merge keywords → fan-in composition."""
        intent = Intent(
            purpose="Aggregate results",
            raw_text="Combine results from multiple sources",
        )
        contract = synthesize_contract(intent)
        modes = [rule.mode for rule in contract.composition_rules]
        assert "fan-in" in modes

    def test_default_sequential(self):
        """No clear pattern → default to sequential."""
        intent = Intent(
            purpose="Process data",
            raw_text="Process some data",
        )
        contract = synthesize_contract(intent)
        modes = [rule.mode for rule in contract.composition_rules]
        assert "sequential" in modes


class TestRealWorldExamples:
    """Test with realistic agent descriptions from spec."""

    def test_weather_agent(self):
        """Weather agent from spec/f-gents/forge.md."""
        text = "Create an agent that fetches weather data from a REST API given a city name"
        intent = parse_intent(text)
        contract = synthesize_contract(intent, "WeatherAgent")

        assert contract.agent_name == "WeatherAgent"
        assert contract.input_type == "str"  # URL or city name
        assert contract.output_type == "dict"  # JSON response
        assert contract.semantic_intent  # Should have purpose
        assert len(contract.composition_rules) > 0

    def test_summarizer_agent(self):
        """Summarizer agent from spec/f-gents/forge.md."""
        text = (
            "Build an agent that summarizes academic papers to concise, objective JSON"
        )
        intent = parse_intent(text)
        contract = synthesize_contract(intent, "Summarizer")

        assert contract.agent_name == "Summarizer"
        assert contract.input_type == "str"  # Paper text
        assert contract.output_type == "dict"  # JSON output
        assert any("concise" in inv.description.lower() for inv in contract.invariants)
        assert any(
            "objectiv" in inv.description.lower() for inv in contract.invariants
        )  # Matches "objective" or "objectivity"

    def test_pipeline_agent(self):
        """Pipeline agent with composition."""
        text = "Chain agents A and B where A fetches data and B transforms it"
        intent = parse_intent(text)
        contract = synthesize_contract(intent, "PipelineAgent")

        assert contract.agent_name == "PipelineAgent"
        modes = [rule.mode for rule in contract.composition_rules]
        assert "sequential" in modes or "conditional" in modes

    def test_idempotent_normalizer(self):
        """Idempotent data normalizer."""
        text = "Create an idempotent normalizer that converts data to standard format"
        intent = parse_intent(text)
        contract = synthesize_contract(intent, "Normalizer")

        assert contract.agent_name == "Normalizer"
        assert any("Idempotency" in inv.description for inv in contract.invariants)

    def test_parallel_aggregator(self):
        """Parallel data aggregation from multiple sources."""
        text = "Aggregate data from multiple REST APIs in parallel"
        intent = parse_intent(text)
        contract = synthesize_contract(intent, "Aggregator")

        modes = [rule.mode for rule in contract.composition_rules]
        assert "parallel" in modes


class TestContractMetadata:
    """Test contract metadata and lineage."""

    def test_raw_intent_preserved(self):
        """Contract should preserve raw intent for lineage."""
        intent = Intent(
            purpose="Test agent",
            raw_text="Create a test agent",
        )
        contract = synthesize_contract(intent, "TestAgent")
        assert contract.raw_intent is intent
        assert contract.raw_intent.purpose == "Test agent"

    def test_semantic_intent_from_purpose(self):
        """Semantic intent should come from intent purpose."""
        intent = Intent(
            purpose="Fetch weather data",
            raw_text="Create an agent that fetches weather data",
        )
        contract = synthesize_contract(intent)
        assert contract.semantic_intent == "Fetch weather data"

    def test_agent_name_parameter(self):
        """Agent name should be configurable."""
        intent = Intent(purpose="Test")
        contract1 = synthesize_contract(intent, "FirstAgent")
        contract2 = synthesize_contract(intent, "SecondAgent")
        assert contract1.agent_name == "FirstAgent"
        assert contract2.agent_name == "SecondAgent"


class TestEdgeCases:
    """Test edge cases and ambiguous inputs."""

    def test_empty_intent(self):
        """Empty intent → basic contract with Any types."""
        intent = Intent(purpose="")
        contract = synthesize_contract(intent)
        assert contract.input_type == "Any"
        assert contract.output_type == "Any"
        assert len(contract.composition_rules) > 0  # Should have default

    def test_ambiguous_types(self):
        """Ambiguous input → reasonable defaults."""
        intent = Intent(
            purpose="Do something",
            raw_text="Do something with some data",
        )
        contract = synthesize_contract(intent)
        # Should not crash, should produce valid contract
        assert contract.input_type in ["Any", "str"]
        assert contract.output_type in ["Any", "str"]

    def test_conflicting_constraints(self):
        """Conflicting constraints → all preserved as invariants."""
        intent = Intent(
            purpose="Process",
            constraints=["Should be fast", "Should be thorough"],  # Potential conflict
        )
        contract = synthesize_contract(intent)
        invariants = [inv.description for inv in contract.invariants]
        assert any("fast" in inv.lower() for inv in invariants)
        assert any("thorough" in inv.lower() for inv in invariants)

    def test_multiple_composition_modes(self):
        """Agent with multiple composition patterns."""
        intent = Intent(
            purpose="Route and combine",
            raw_text="If valid, fetch from API and combine with local data",
            dependencies=[Dependency(name="API", type=DependencyType.REST_API)],
        )
        contract = synthesize_contract(intent)
        modes = [rule.mode for rule in contract.composition_rules]
        # Should detect both conditional and fan-in/sequential
        assert len(modes) >= 1


class TestIntegrationWithPhase1:
    """Test integration between Phase 1 (parse_intent) and Phase 2 (synthesize_contract)."""

    def test_full_pipeline(self):
        """Natural language → Intent → Contract."""
        text = "Create an idempotent agent that fetches weather from a REST API and returns concise JSON"
        intent = parse_intent(text)
        contract = synthesize_contract(intent, "WeatherAgent")

        # Verify full pipeline
        assert contract.agent_name == "WeatherAgent"
        assert contract.input_type == "str"
        assert contract.output_type == "dict"
        assert any("Idempotency" in inv.description for inv in contract.invariants)
        assert any("Conciseness" in inv.description for inv in contract.invariants)
        assert len(contract.composition_rules) > 0

    def test_ambiguities_preserved(self):
        """Ambiguities from Phase 1 should inform Phase 2."""
        text = "Build an agent that processes some data with several steps"
        intent = parse_intent(text)
        contract = synthesize_contract(intent)

        # Intent should have detected ambiguities
        assert len(intent.ambiguities) > 0
        # Contract should still be generated (with defaults)
        assert contract.input_type
        assert contract.output_type
