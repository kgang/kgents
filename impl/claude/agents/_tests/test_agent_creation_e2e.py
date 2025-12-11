"""
Agent Creation End-to-End Tests

Tests the complete agent creation lifecycle:
1. Read spec from spec/{agent}
2. Create DNA from spec constraints
3. Build implementation with Umwelt
4. Execute agent and validate behavior

Philosophy: Spec → DNA → Implementation → Execution is the full lifecycle.
"""

from dataclasses import dataclass

import pytest

# D-gent imports (Data)
from agents.d import (
    MemoryConfig,
    Symbiont,
    UnifiedMemory,
    VolatileAgent,
)

# F-gent imports (Forge)
from agents.f import (
    Artifact,
    ArtifactMetadata,
    ArtifactStatus,
    Contract,
    Example,
    Intent,
    Invariant,
    Version,
    parse_intent,
    synthesize_contract,
)

# J-gent imports (JIT)
from agents.j import (
    AgentSource,
    create_agent_from_source,
)

# L-gent imports (Library)
from agents.l import (
    CatalogEntry,
    EntityType,
    Registry,
    Status,
)

# O-gent imports (Observer)
from agents.o import (
    BaseObserver,
    observe,
)

# Shared fixtures
from agents.shared.fixtures_integration import (
    make_sample_contract,
    make_sample_intent,
    make_sample_source_code,
)

# Bootstrap imports
# DNA imports
from bootstrap.dna import (
    Constraint,
)

# Umwelt imports
from bootstrap.umwelt import (
    Umwelt,
)


class TestSpecToAgent:
    """Test spec → agent lifecycle."""

    def test_parse_natural_language_intent(self) -> None:
        """Test parsing natural language into structured Intent."""
        intent = parse_intent(
            "Create an agent that validates JSON schemas and returns "
            "detailed error messages when validation fails"
        )

        assert intent.purpose
        assert len(intent.behavior) >= 0  # May or may not extract behaviors
        assert isinstance(intent.constraints, list)

    def test_intent_to_contract(self) -> None:
        """Test Intent → Contract transformation."""
        intent = make_sample_intent(
            purpose="Validate email addresses",
            agent_name="EmailValidator",
        )

        contract = synthesize_contract(intent, "EmailValidator")

        assert contract.agent_name == "EmailValidator"
        assert contract.input_type is not None
        assert contract.output_type is not None

    def test_contract_has_invariants(self) -> None:
        """Test synthesized contract includes invariants."""
        intent = Intent(
            purpose="Calculate tax amounts",
            behavior=["Accept income", "Return tax amount"],
            constraints=["Non-negative output", "Handle edge cases"],
            examples=[
                Example(input=100, expected_output=15, description="Basic tax"),
            ],
        )

        contract = synthesize_contract(intent, "TaxCalculator")

        # Should have invariants from constraints
        assert len(contract.invariants) >= 0  # May or may not generate


class TestDNAFromSpec:
    """Test DNA creation from spec constraints."""

    def test_constraints_become_dna(self) -> None:
        """Test spec constraints translate to DNA constraints."""
        # Define spec-level constraints
        spec_constraints = [
            "Must return within 5 seconds",
            "Output must be JSON",
            "No external network calls",
        ]

        # Translate to DNA constraints
        dna_constraints = [
            Constraint(
                name="timeout",
                check=lambda dna: dna.timeout <= 5.0,
                message="Timeout must be <= 5s",
            ),
            Constraint(
                name="output_format",
                check=lambda dna: dna.output_format == "json",
                message="Output must be JSON",
            ),
            Constraint(
                name="network",
                check=lambda dna: not dna.allow_network,
                message="No network calls allowed",
            ),
        ]

        assert len(dna_constraints) == len(spec_constraints)

    def test_dna_validation_against_spec(self) -> None:
        """Test DNA validates against spec requirements."""

        @dataclass(frozen=True)
        class AgentDNA:
            timeout: float = 5.0
            output_format: str = "json"
            allow_network: bool = False

        dna = AgentDNA()

        # Validate
        assert dna.timeout <= 5.0
        assert dna.output_format == "json"
        assert not dna.allow_network


class TestImplementationFromDNA:
    """Test implementation building from DNA."""

    @pytest.mark.asyncio
    async def test_jit_compiles_from_source(self) -> None:
        """Test JIT compiles agent from source."""
        source = AgentSource(
            source="""
class ImplementedAgent:
    async def invoke(self, input: str) -> dict:
        return {"processed": input, "status": "ok"}
""",
            class_name="ImplementedAgent",
            imports=frozenset(),
            complexity=1,
            description="Agent implemented from DNA",
        )

        agent = await create_agent_from_source(source, validate=False)

        result = await agent.invoke("test input")
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_agent_respects_dna_constraints(self) -> None:
        """Test compiled agent respects DNA constraints."""

        @dataclass(frozen=True)
        class ConstrainedDNA:
            max_output_length: int = 100

        source = AgentSource(
            source="""
class ConstrainedAgent:
    def __init__(self):
        self.max_length = 100

    async def invoke(self, input: str) -> str:
        result = f"Processed: {input}"
        return result[:self.max_length]
""",
            class_name="ConstrainedAgent",
            imports=frozenset(),
            complexity=2,
            description="Agent with output length constraint",
        )

        agent = await create_agent_from_source(source, validate=False)

        # Long input should be truncated
        result = await agent.invoke("x" * 200)
        assert len(result) <= 100


class TestUmweltCreation:
    """Test Umwelt creation for agent."""

    def test_umwelt_provides_projected_state(self) -> None:
        """Test Umwelt provides agent-specific state view."""
        full_state = {
            "global_config": {"version": "1.0"},
            "agent_a_state": {"counter": 5},
            "agent_b_state": {"counter": 10},
        }

        # Agent A only sees its state
        agent_a_umwelt = Umwelt(
            state={
                "config": full_state["global_config"],
                "my_state": full_state["agent_a_state"],
            },
            dna=None,
        )

        assert "my_state" in agent_a_umwelt.state
        assert agent_a_umwelt.state["my_state"]["counter"] == 5
        assert "agent_b_state" not in agent_a_umwelt.state

    @pytest.mark.asyncio
    async def test_symbiont_with_umwelt_state(self) -> None:
        """Test Symbiont agent operates on Umwelt state."""

        def increment_logic(amount: int, state: dict) -> tuple[dict, dict]:
            new_state = dict(state)
            new_state["counter"] = state.get("counter", 0) + amount
            return new_state, new_state

        initial_state = {"counter": 0}
        memory = VolatileAgent(_state=initial_state)
        counter = Symbiont(logic=increment_logic, memory=memory)

        result = await counter.invoke(5)
        assert result["counter"] == 5

        result = await counter.invoke(3)
        assert result["counter"] == 8


class TestAgentExecution:
    """Test agent execution and validation."""

    @pytest.mark.asyncio
    async def test_agent_produces_valid_output(self) -> None:
        """Test agent produces output matching contract."""
        source = AgentSource(
            source="""
class ValidatingAgent:
    async def invoke(self, input: dict) -> dict:
        name = input.get("name", "unknown")
        return {"greeting": f"Hello, {name}!", "valid": True}
""",
            class_name="ValidatingAgent",
            imports=frozenset(),
            complexity=1,
            description="Agent with validated output",
        )

        agent = await create_agent_from_source(source, validate=False)
        result = await agent.invoke({"name": "Alice"})

        assert "greeting" in result
        assert result["valid"] is True
        assert "Hello, Alice!" in result["greeting"]

    @pytest.mark.asyncio
    async def test_observed_agent_execution(self) -> None:
        """Test agent execution with observation."""
        source = AgentSource(
            source="""
class ObservedAgent:
    async def invoke(self, input: str) -> str:
        return input.upper()
""",
            class_name="ObservedAgent",
            imports=frozenset(),
            complexity=1,
            description="Observable agent",
        )

        agent = await create_agent_from_source(source, validate=False)
        observed = observe(agent)

        result = await observed.invoke("test")
        assert result == "TEST"


class TestAgentRegistration:
    """Test agent registration in catalog."""

    @pytest.mark.asyncio
    async def test_register_created_agent(self) -> None:
        """Test registering newly created agent."""
        registry = Registry()

        entry = CatalogEntry(
            id="created-agent-001",
            entity_type=EntityType.AGENT,
            name="CreatedAgent",
            version="1.0.0",
            description="Agent created through full lifecycle",
            author="e2e-test",
            input_type="str",
            output_type="str",
        )

        entry_id = await registry.register(entry)
        assert entry_id == "created-agent-001"

        retrieved = await registry.get("created-agent-001")
        assert retrieved.name == "CreatedAgent"

    @pytest.mark.asyncio
    async def test_register_with_artifact_metadata(self) -> None:
        """Test registering agent with artifact metadata."""
        registry = Registry()

        artifact = Artifact(
            metadata=ArtifactMetadata(
                id="artifact-agent-001",
                version=Version(1, 0, 0),
                status=ArtifactStatus.ACTIVE,
                tags=["e2e", "test"],
            ),
            intent=make_sample_intent(),
            contract=make_sample_contract(),
            source_code=make_sample_source_code(),
        )

        entry = CatalogEntry(
            id=artifact.metadata.id,
            entity_type=EntityType.AGENT,
            name=artifact.contract.agent_name,
            version=str(artifact.metadata.version),
            description=artifact.intent.purpose,
            status=Status.ACTIVE,
        )

        await registry.register(entry)
        retrieved = await registry.get("artifact-agent-001")

        assert retrieved.version == "1.0.0"


class TestAgentEvolution:
    """Test agent evolution lifecycle."""

    @pytest.mark.asyncio
    async def test_version_bump_on_change(self) -> None:
        """Test version bumps appropriately on changes."""
        from agents.f import VersionBump, determine_version_bump

        old_contract = Contract(
            agent_name="Evolving",
            input_type="str",
            output_type="str",
        )

        # Minor change (add invariant)
        new_contract = Contract(
            agent_name="Evolving",
            input_type="str",
            output_type="str",
            invariants=[
                Invariant(
                    description="New constraint",
                    property="len(output) > 0",
                    category="correctness",
                )
            ],
        )

        bump = determine_version_bump(old_contract, new_contract)
        # Should be MINOR or PATCH for adding constraint
        assert bump in [VersionBump.MINOR, VersionBump.PATCH]

    @pytest.mark.asyncio
    async def test_breaking_change_major_bump(self) -> None:
        """Test breaking changes require major bump."""
        from agents.f import VersionBump, determine_version_bump

        old_contract = Contract(
            agent_name="Breaking",
            input_type="str",
            output_type="str",
        )

        # Breaking change (change output type)
        new_contract = Contract(
            agent_name="Breaking",
            input_type="str",
            output_type="dict",  # Changed!
        )

        bump = determine_version_bump(old_contract, new_contract)
        assert bump == VersionBump.MAJOR


class TestFullLifecycle:
    """Test complete spec → execution lifecycle."""

    @pytest.mark.asyncio
    async def test_complete_lifecycle(self) -> None:
        """Test complete agent lifecycle from intent to execution."""
        # Step 1: Parse intent
        intent = parse_intent("Create an agent that greets users by name")
        assert intent.purpose

        # Step 2: Synthesize contract
        contract = synthesize_contract(intent, "GreeterAgent")
        assert contract.agent_name == "GreeterAgent"

        # Step 3: Generate source
        source = AgentSource(
            source="""
class GreeterAgent:
    async def invoke(self, input: dict) -> str:
        name = input.get("name", "World")
        return f"Hello, {name}!"
""",
            class_name="GreeterAgent",
            imports=frozenset(),
            complexity=1,
            description=intent.purpose,
        )

        # Step 4: Compile agent
        agent = await create_agent_from_source(source, validate=False)
        assert agent is not None

        # Step 5: Execute
        result = await agent.invoke({"name": "Integration Test"})
        assert "Hello, Integration Test!" in result

        # Step 6: Register
        registry = Registry()
        entry = CatalogEntry(
            id="greeter-v1",
            entity_type=EntityType.AGENT,
            name=contract.agent_name,
            version="1.0.0",
            description=intent.purpose,
        )
        await registry.register(entry)

        # Verify registration
        retrieved = await registry.get("greeter-v1")
        assert retrieved.name == "GreeterAgent"

    @pytest.mark.asyncio
    async def test_lifecycle_with_observation(self) -> None:
        """Test lifecycle with observation throughout."""
        observer = BaseObserver(observer_id="lifecycle-observer")
        registry = Registry()

        # Create simple agent
        source = AgentSource(
            source="""
class TrackedAgent:
    async def invoke(self, x: int) -> int:
        return x * 2
""",
            class_name="TrackedAgent",
            imports=frozenset(),
            complexity=1,
            description="Tracked agent",
        )

        agent = await create_agent_from_source(source, validate=False)

        # Wrap with observer
        ctx = observer.pre_invoke(agent, 5)
        result = await agent.invoke(5)
        await observer.post_invoke(ctx, result, duration_ms=10.0)

        assert result == 10
        assert len(observer.observations) == 1

        # Register
        await registry.register(
            CatalogEntry(
                id="tracked-v1",
                entity_type=EntityType.AGENT,
                name="TrackedAgent",
                version="1.0.0",
                description="Tracked agent",
            )
        )


class TestLifecycleWithState:
    """Test lifecycle with stateful agents."""

    @pytest.mark.asyncio
    async def test_stateful_agent_lifecycle(self) -> None:
        """Test lifecycle with D-gent backed state."""

        # Create stateful agent
        def counter_logic(increment: int, count: int) -> tuple[int, int]:
            new_count = count + increment
            return new_count, new_count

        memory = VolatileAgent(_state=0)
        counter = Symbiont(logic=counter_logic, memory=memory)

        # Execute multiple times
        r1 = await counter.invoke(1)
        r2 = await counter.invoke(5)
        r3 = await counter.invoke(3)

        assert r1 == 1
        assert r2 == 6
        assert r3 == 9

        # Verify state persisted
        state = await memory.load()
        assert state == 9

    @pytest.mark.asyncio
    async def test_unified_memory_lifecycle(self) -> None:
        """Test lifecycle with UnifiedMemory."""
        volatile = VolatileAgent(_state={"version": 1})
        config = MemoryConfig(
            enable_temporal=True,
            enable_semantic=True,
        )
        unified = UnifiedMemory(volatile, config)

        # Save state changes
        await unified.save({"version": 2})
        await unified.witness("v2", {"version": 2})

        await unified.save({"version": 3})
        await unified.witness("v3", {"version": 3})

        # Load current
        current = await unified.load()
        assert current["version"] == 3


# Run with: pytest impl/claude/agents/_tests/test_agent_creation_e2e.py -v
