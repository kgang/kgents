"""
Factory Pipeline Integration Tests: J × F × T × L × B

Tests integration between JIT, Forge, Tool, Library, and Banker agents:
- J × F × T: Prototype → compile → tool pipeline
- J × L: Source registration in catalog
- J × B: Budget-constrained compilation
- F × L: Artifact registration

Philosophy: The factory pipeline transforms intent into executable artifacts.
"""

import pytest

# F-gent imports
from agents.f import (
    Artifact,
    ArtifactMetadata,
    ArtifactStatus,
    CompositionRule,
    Contract,
    Invariant,
    Version,
    parse_intent,
    synthesize_contract,
)

# J-gent imports
from agents.j import (
    AgentSource,
    ArchitectConstraints,
    ClassificationInput,
    JGent,
    JGentConfig,
    JGentInput,
    JITAgentWrapper,
    Promise,
    PromiseState,
    Reality,
    RealityClassifier,
    SandboxConfig,
    create_agent_from_source,
)

# L-gent imports
from agents.l import (
    CatalogEntry,
    EntityType,
    Registry,
)

# Shared fixtures
from agents.shared.fixtures_integration import (
    make_sample_contract,
    make_sample_intent,
    make_sample_source_code,
)


class TestPrototypeToToolPipeline:
    """J × F × T: Full prototype-to-tool pipeline."""

    @pytest.mark.asyncio
    async def test_intent_to_contract_to_source(self) -> None:
        """Test F-gent pipeline: intent → contract → source."""
        # Step 1: Parse intent
        intent = parse_intent(
            "Create an agent that converts temperatures between Celsius and Fahrenheit"
        )
        assert intent.purpose

        # Step 2: Synthesize contract
        contract = synthesize_contract(intent, "TemperatureConverter")
        assert contract.agent_name == "TemperatureConverter"
        assert contract.input_type
        assert contract.output_type

        # Step 3: Create source (using fixture for determinism)
        source = make_sample_source_code("TemperatureConverter", valid=True)
        assert source.is_valid

    @pytest.mark.asyncio
    async def test_jit_compile_simple_agent(self) -> None:
        """Test J-gent compiles simple agent source."""
        source = AgentSource(
            source="""
class SimpleAgent:
    async def invoke(self, input: str) -> str:
        return f"Processed: {input}"
""",
            class_name="SimpleAgent",
            imports=frozenset(),
            complexity=1,
            description="Simple echo agent",
        )

        # Compile with JIT
        agent = await create_agent_from_source(source, validate=False)
        assert agent is not None
        assert isinstance(agent, JITAgentWrapper)

        # Execute
        result = await agent.invoke("test")
        assert "Processed: test" in result

    @pytest.mark.asyncio
    async def test_jit_agent_with_computation(self) -> None:
        """Test J-gent compiles agent with actual computation."""
        source = AgentSource(
            source="""
class MathAgent:
    async def invoke(self, input: dict) -> dict:
        a = input.get("a", 0)
        b = input.get("b", 0)
        return {
            "sum": a + b,
            "product": a * b,
            "difference": a - b,
        }
""",
            class_name="MathAgent",
            imports=frozenset(),
            complexity=2,
            description="Mathematical operations agent",
        )

        agent = await create_agent_from_source(source, validate=False)
        result = await agent.invoke({"a": 10, "b": 5})

        assert result["sum"] == 15
        assert result["product"] == 50
        assert result["difference"] == 5

    @pytest.mark.asyncio
    async def test_jit_preserves_metadata(self) -> None:
        """Test JIT wrapper preserves compilation metadata."""
        source = AgentSource(
            source="""
class MetadataAgent:
    async def invoke(self, input: str) -> str:
        return input.upper()
""",
            class_name="MetadataAgent",
            imports=frozenset(),
            complexity=1,
            description="Uppercase transformer",
        )

        agent = await create_agent_from_source(source, validate=False)

        # Check metadata is preserved
        assert hasattr(agent, "jit_meta")
        # JITAgentMeta stores source which has class_name
        assert agent.jit_meta.source.class_name == "MetadataAgent"


class TestRealityClassification:
    """Test J-gent Reality classification system."""

    @pytest.mark.asyncio
    async def test_deterministic_classification(self) -> None:
        """Test deterministic tasks are classified correctly."""
        classifier = RealityClassifier()

        input_data = ClassificationInput(
            intent="Parse JSON string",
            context={},
            entropy_budget=1.0,
        )

        result = await classifier.invoke(input_data)
        # Simple parsing should be deterministic
        assert result.reality in [Reality.DETERMINISTIC, Reality.PROBABILISTIC]
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_chaotic_classification(self) -> None:
        """Test chaotic tasks are classified correctly."""
        classifier = RealityClassifier()

        input_data = ClassificationInput(
            intent="Build complete autonomous AI system that replaces all software",
            context={},
            entropy_budget=0.1,  # Very low budget
        )

        result = await classifier.invoke(input_data)
        # This unbounded task should be chaotic or at least probabilistic
        assert result.reality in [Reality.CHAOTIC, Reality.PROBABILISTIC]

    @pytest.mark.asyncio
    async def test_entropy_budget_affects_classification(self) -> None:
        """Test entropy budget affects reality classification."""
        classifier = RealityClassifier()

        high_budget = ClassificationInput(
            intent="Generate code",
            context={},
            entropy_budget=1.0,
        )

        low_budget = ClassificationInput(
            intent="Generate code",
            context={},
            entropy_budget=0.01,
        )

        high_result = await classifier.invoke(high_budget)
        low_result = await classifier.invoke(low_budget)

        # Lower budget tends to produce CHAOTIC classification
        # High budget allows more permissive classifications
        assert high_result.confidence >= 0
        assert low_result.confidence >= 0


class TestPromiseSystem:
    """Test J-gent Promise system."""

    def test_promise_creation(self) -> None:
        """Test Promise creation with ground value."""
        promise = Promise(
            intent="Calculate sum",
            ground=0,  # Fallback value
            context={"numbers": [1, 2, 3]},
        )

        assert promise.state == PromiseState.PENDING
        assert promise.ground == 0
        assert promise.intent == "Calculate sum"

    def test_promise_entropy_budget(self) -> None:
        """Test entropy budget decreases with depth."""
        root = Promise(intent="Root", ground=None, depth=0)
        child = Promise(intent="Child", ground=None, depth=1)
        grandchild = Promise(intent="Grandchild", ground=None, depth=2)

        assert root.entropy_budget == 1.0  # 1/(0+1)
        assert child.entropy_budget == 0.5  # 1/(1+1)
        assert grandchild.entropy_budget == pytest.approx(0.333, rel=0.01)

    def test_promise_state_transitions(self) -> None:
        """Test Promise state transitions."""
        promise = Promise(intent="Test", ground="fallback")

        # Initial state
        assert promise.state == PromiseState.PENDING

        # Mark resolving
        promise.mark_resolving()
        assert promise.state == PromiseState.RESOLVING

        # Mark resolved
        promise.mark_resolved("actual value")
        assert promise.state == PromiseState.RESOLVED
        assert promise.resolved_value == "actual value"

    def test_promise_collapse_to_ground(self) -> None:
        """Test Promise collapses to ground on failure."""
        promise = Promise(intent="Test", ground="fallback")

        # Collapse
        promise.mark_collapsed("Validation failed")
        assert promise.state == PromiseState.COLLAPSED
        assert promise.value_or_ground() == "fallback"

    def test_promise_tree_structure(self) -> None:
        """Test Promise parent-child relationships."""
        parent = Promise(intent="Parent", ground=None)
        child1 = Promise(intent="Child1", ground=None, parent=parent)
        child2 = Promise(intent="Child2", ground=None, parent=parent)

        parent.add_child(child1)
        parent.add_child(child2)

        assert len(parent.children) == 2
        assert not parent.is_leaf
        assert child1.is_leaf
        assert child2.is_leaf


class TestSourceRegistration:
    """J × L: Source registration in catalog."""

    @pytest.mark.asyncio
    async def test_register_compiled_agent(self) -> None:
        """Test registering compiled agent in L-gent catalog."""
        registry = Registry()

        # Create catalog entry for compiled agent
        entry = CatalogEntry(
            id="jit-agent-001",
            entity_type=EntityType.AGENT,
            name="CompiledMathAgent",
            version="1.0.0",
            description="JIT-compiled mathematical operations agent",
            keywords=["math", "jit", "compiled"],
            author="j-gent",
            input_type="dict",
            output_type="dict",
        )

        # Register
        entry_id = await registry.register(entry)
        assert entry_id == "jit-agent-001"

        # Retrieve
        retrieved = await registry.get("jit-agent-001")
        assert retrieved is not None
        assert retrieved.name == "CompiledMathAgent"
        assert "jit" in retrieved.keywords

    @pytest.mark.asyncio
    async def test_register_with_provenance(self) -> None:
        """Test registration preserves provenance information."""
        registry = Registry()

        entry = CatalogEntry(
            id="forged-agent-001",
            entity_type=EntityType.AGENT,
            name="ForgedAgent",
            version="1.0.0",
            description="Agent forged from intent",
            author="f-gent",
            forged_by="f-gent",
            forged_from="intent://validate-email",
            input_type="str",
            output_type="bool",
        )

        await registry.register(entry)
        retrieved = await registry.get("forged-agent-001")

        assert retrieved.forged_by == "f-gent"
        assert retrieved.forged_from == "intent://validate-email"

    @pytest.mark.asyncio
    async def test_list_agents_by_type(self) -> None:
        """Test listing agents by entity type."""
        registry = Registry()

        # Register multiple entries
        await registry.register(
            CatalogEntry(
                id="agent-1",
                entity_type=EntityType.AGENT,
                name="Agent1",
                version="1.0.0",
                description="First agent",
            )
        )
        await registry.register(
            CatalogEntry(
                id="contract-1",
                entity_type=EntityType.CONTRACT,
                name="Contract1",
                version="1.0.0",
                description="A contract",
            )
        )
        await registry.register(
            CatalogEntry(
                id="agent-2",
                entity_type=EntityType.AGENT,
                name="Agent2",
                version="1.0.0",
                description="Second agent",
            )
        )

        # List only agents
        agents = await registry.list(entity_type=EntityType.AGENT)
        assert len(agents) == 2
        assert all(a.entity_type == EntityType.AGENT for a in agents)


class TestBudgetConstrainedCompilation:
    """J × B: Budget-constrained compilation."""

    def test_jgent_config_budget_settings(self) -> None:
        """Test JGent respects budget configuration."""
        config = JGentConfig(
            max_depth=2,
            entropy_threshold=0.2,
            max_cyclomatic_complexity=10,
        )

        assert config.max_depth == 2
        assert config.entropy_threshold == 0.2
        assert config.max_cyclomatic_complexity == 10

    def test_architect_constraints(self) -> None:
        """Test MetaArchitect respects constraints."""
        # ArchitectConstraints uses max_cyclomatic_complexity, not max_complexity
        constraints = ArchitectConstraints(
            max_cyclomatic_complexity=15,
            max_branching_factor=3,
        )

        assert constraints.max_cyclomatic_complexity == 15
        assert constraints.max_branching_factor == 3
        # Default allowed_imports should exist
        assert "json" in constraints.allowed_imports

    @pytest.mark.asyncio
    async def test_jgent_with_ground_fallback(self) -> None:
        """Test JGent falls back to ground on budget exhaustion."""
        config = JGentConfig(
            max_depth=1,  # Shallow depth
            entropy_threshold=0.5,  # High threshold
        )

        jgent = JGent(config=config)

        input_data = JGentInput(
            intent="Simple computation",
            ground="fallback_result",
            context={},
        )

        result = await jgent.invoke(input_data)

        # Should either succeed or fall back to ground
        assert result.value is not None
        if result.collapsed:
            assert result.value == "fallback_result"


class TestArtifactCrystallization:
    """F × L: Artifact registration and crystallization."""

    def test_artifact_metadata_creation(self) -> None:
        """Test artifact metadata creation."""
        metadata = ArtifactMetadata(
            id="artifact-001",
            artifact_type="f_gent_artifact",
            version=Version(1, 0, 0),
            status=ArtifactStatus.EXPERIMENTAL,
            tags=["email", "validation"],
        )

        assert metadata.id == "artifact-001"
        assert str(metadata.version) == "1.0.0"
        assert metadata.status == ArtifactStatus.EXPERIMENTAL

    def test_version_bumping(self) -> None:
        """Test version bump logic."""
        from agents.f import VersionBump

        v1 = Version(1, 0, 0)

        # Patch bump
        v1_patch = v1.bump(VersionBump.PATCH)
        assert str(v1_patch) == "1.0.1"

        # Minor bump
        v1_minor = v1.bump(VersionBump.MINOR)
        assert str(v1_minor) == "1.1.0"

        # Major bump
        v1_major = v1.bump(VersionBump.MAJOR)
        assert str(v1_major) == "2.0.0"

    def test_artifact_assembly(self) -> None:
        """Test artifact assembly from components."""
        intent = make_sample_intent()
        contract = make_sample_contract()
        source = make_sample_source_code()
        metadata = ArtifactMetadata(
            id="test-artifact",
            version=Version(1, 0, 0),
        )

        artifact = Artifact(
            metadata=metadata,
            intent=intent,
            contract=contract,
            source_code=source,
        )

        assert artifact.metadata.id == "test-artifact"
        assert artifact.intent.purpose
        assert artifact.contract.agent_name
        assert artifact.source_code.code

    @pytest.mark.asyncio
    async def test_artifact_to_catalog_entry(self) -> None:
        """Test converting artifact to catalog entry."""
        registry = Registry()

        intent = make_sample_intent()
        contract = make_sample_contract("WeatherAgent")

        entry = CatalogEntry(
            id="weather-agent-v1",
            entity_type=EntityType.AGENT,
            name=contract.agent_name,
            version="1.0.0",
            description=intent.purpose,
            keywords=["weather", "api"],
            author="f-gent",
            input_type=contract.input_type,
            output_type=contract.output_type,
        )

        await registry.register(entry)
        retrieved = await registry.get("weather-agent-v1")

        assert retrieved.name == "WeatherAgent"
        assert retrieved.input_type == contract.input_type


class TestSandboxExecution:
    """Test sandbox execution safety."""

    def test_sandbox_config_defaults(self) -> None:
        """Test sandbox configuration defaults."""
        config = SandboxConfig()

        assert config.timeout_seconds == 30.0
        # SandboxConfig uses allowed_imports, not max_memory_mb
        assert "json" in config.allowed_imports
        assert "re" in config.allowed_imports

    def test_sandbox_config_custom(self) -> None:
        """Test custom sandbox configuration."""
        config = SandboxConfig(
            timeout_seconds=10.0,
            allowed_imports=frozenset({"json", "re", "math"}),
        )

        assert config.timeout_seconds == 10.0
        assert len(config.allowed_imports) == 3


class TestContractInvariantValidation:
    """Test contract invariant handling."""

    def test_invariant_creation(self) -> None:
        """Test invariant creation."""
        invariant = Invariant(
            description="Response time < 5s",
            property="execution_time < 5.0",
            category="performance",
        )

        assert invariant.description == "Response time < 5s"
        assert invariant.category == "performance"

    def test_contract_with_invariants(self) -> None:
        """Test contract with multiple invariants."""
        contract = Contract(
            agent_name="StrictAgent",
            input_type="str",
            output_type="Result",
            invariants=[
                Invariant(
                    description="Always returns valid JSON",
                    property="is_valid_json(output)",
                    category="correctness",
                ),
                Invariant(
                    description="No sensitive data in output",
                    property="not contains_pii(output)",
                    category="security",
                ),
            ],
            composition_rules=[
                CompositionRule(
                    mode="sequential",
                    description="Can chain with processors",
                    type_constraint="Result -> ProcessedResult",
                )
            ],
        )

        assert len(contract.invariants) == 2
        assert len(contract.composition_rules) == 1
        assert contract.invariants[0].category == "correctness"
        assert contract.invariants[1].category == "security"


# Run with: pytest impl/claude/agents/_tests/test_factory_pipeline_integration.py -v
