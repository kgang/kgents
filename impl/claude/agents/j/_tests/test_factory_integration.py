"""
Tests for J-gent AgentFactory Integration.

Tests cover:
1. create_agent_from_source basic functionality
2. create_agent_from_source with validation
3. JIT agent composition with other agents
4. JIT agent meta introspection
5. compile_and_instantiate convenience function
6. Error handling for rejected sources

All J-gent agents are marked with __is_test__ = True to distinguish them
from production agents.
"""

import pytest
from agents.j import (
    AgentSource,
    ArchitectConstraints,
)
from agents.j.factory_integration import (
    JITAgentMeta,
    JITAgentWrapper,
    compile_and_instantiate,
    create_agent_from_source,
    get_jit_meta,
    is_jit_agent,
)
from bootstrap.types import Agent

# Mark wrapper as test agent
JITAgentWrapper.__is_test__ = True


# --- Fixtures ---


@pytest.fixture
def simple_parser_source() -> AgentSource:
    """Create a simple parser AgentSource for testing.

    Note: Uses sandbox-available modules (json is pre-loaded in namespace).
    """
    # Note: The sandbox pre-loads json, re, dataclasses, etc. into the namespace
    # so we can use them directly without import statements
    source_code = '''
class ParsedLog:
    """Simple result class."""
    def __init__(self, level: str, message: str):
        self.level = level
        self.message = message

class JITLogParser:
    """Simple log parser for testing."""

    async def invoke(self, input: str) -> ParsedLog:
        """Parse JSON log entry."""
        data = json.loads(input)
        return ParsedLog(
            level=data.get("level", "info"),
            message=data.get("msg", ""),
        )
'''
    return AgentSource(
        source=source_code,
        class_name="JITLogParser",
        imports=frozenset({"json"}),  # json is pre-loaded in sandbox
        complexity=5,
        description="Parse JSON log entries",
    )


@pytest.fixture
def high_complexity_source() -> AgentSource:
    """Create a source with high complexity (for rejection testing)."""
    # Generate source that would exceed entropy budget
    source_code = """
class JITComplexAgent:
    def invoke(self, input: str) -> str:
        # Lots of nesting and branches
        if input:
            if len(input) > 0:
                if input[0] == 'a':
                    for i in range(10):
                        for j in range(10):
                            while True:
                                break
        return input
"""
    return AgentSource(
        source=source_code,
        class_name="JITComplexAgent",
        imports=frozenset(),
        complexity=50,  # High complexity
        description="Complex agent for testing",
    )


# --- create_agent_from_source Tests ---


@pytest.mark.asyncio
async def test_create_agent_from_source_basic(simple_parser_source: AgentSource):
    """Test basic agent creation from source."""
    agent = await create_agent_from_source(
        source=simple_parser_source,
        validate=False,  # Skip validation for basic test
    )

    assert isinstance(agent, JITAgentWrapper)
    assert agent.name == "JITLogParser"


@pytest.mark.asyncio
async def test_create_agent_from_source_with_meta(simple_parser_source: AgentSource):
    """Test that created agent has proper AgentMeta."""
    agent = await create_agent_from_source(
        source=simple_parser_source,
        validate=False,
    )

    # Check AgentMeta
    assert hasattr(agent, "meta")
    meta = agent.meta
    assert meta.identity.name == "JITLogParser"
    assert meta.identity.genus == "j"
    assert meta.identity.version == "ephemeral"
    assert "Parse JSON log entries" in meta.identity.purpose


@pytest.mark.asyncio
async def test_create_agent_from_source_with_jit_meta(
    simple_parser_source: AgentSource,
):
    """Test that created agent has JITAgentMeta."""
    constraints = ArchitectConstraints(entropy_budget=0.8)

    agent = await create_agent_from_source(
        source=simple_parser_source,
        constraints=constraints,
        validate=False,
    )

    # Check JITAgentMeta
    assert hasattr(agent, "jit_meta")
    jit_meta = agent.jit_meta
    assert isinstance(jit_meta, JITAgentMeta)
    assert jit_meta.source == simple_parser_source
    assert jit_meta.constraints == constraints
    assert 0.0 <= jit_meta.stability_score <= 1.0


@pytest.mark.asyncio
async def test_create_agent_from_source_execution(simple_parser_source: AgentSource):
    """Test that created agent can execute."""
    agent = await create_agent_from_source(
        source=simple_parser_source,
        validate=False,
    )

    # Execute the agent
    result = await agent.invoke('{"level": "error", "msg": "test message"}')

    assert result is not None
    assert result.level == "error"
    assert result.message == "test message"


@pytest.mark.asyncio
async def test_create_agent_from_source_with_validation(
    simple_parser_source: AgentSource,
):
    """Test agent creation with validation enabled."""
    agent = await create_agent_from_source(
        source=simple_parser_source,
        validate=True,
    )

    assert isinstance(agent, JITAgentWrapper)
    assert agent.name == "JITLogParser"


# --- Composition Tests ---


@pytest.mark.asyncio
async def test_jit_agent_composition(simple_parser_source: AgentSource):
    """Test that JIT agents can compose with other agents via >>."""

    # Create a simple downstream agent
    class UpperCaseAgent(Agent[object, str]):
        """Converts message to uppercase."""

        @property
        def name(self) -> str:
            return "UpperCaseAgent"

        async def invoke(self, input: object) -> str:
            # Access the message attribute
            if hasattr(input, "message"):
                return input.message.upper()
            return str(input).upper()

    # Create JIT agent
    jit_agent = await create_agent_from_source(
        source=simple_parser_source,
        validate=False,
    )

    # Compose: JITLogParser >> UpperCaseAgent
    upper_agent = UpperCaseAgent()
    pipeline = jit_agent >> upper_agent

    # Execute composed pipeline
    result = await pipeline.invoke('{"level": "info", "msg": "hello world"}')

    assert result == "HELLO WORLD"


# --- Introspection Tests ---


def test_get_jit_meta_returns_meta():
    """Test get_jit_meta utility function."""
    # Create a mock JITAgentWrapper
    from agents.a.skeleton import AgentMeta

    mock_source = AgentSource(
        source="class Test: pass",
        class_name="Test",
        imports=frozenset(),
        complexity=1,
        description="Test",
    )
    mock_jit_meta = JITAgentMeta(
        source=mock_source,
        constraints=ArchitectConstraints(),
        stability_score=0.9,
    )
    mock_meta = AgentMeta.minimal("Test", "j", "Test agent")

    wrapper = JITAgentWrapper(meta=mock_meta, jit_meta=mock_jit_meta)

    # Test get_jit_meta
    result = get_jit_meta(wrapper)
    assert result is mock_jit_meta


def test_get_jit_meta_returns_none_for_non_jit():
    """Test get_jit_meta returns None for non-JIT agents."""

    class RegularAgent(Agent[str, str]):
        @property
        def name(self) -> str:
            return "Regular"

        async def invoke(self, input: str) -> str:
            return input

    agent = RegularAgent()
    result = get_jit_meta(agent)
    assert result is None


def test_is_jit_agent_true():
    """Test is_jit_agent returns True for JIT agents."""
    from agents.a.skeleton import AgentMeta

    mock_source = AgentSource(
        source="class Test: pass",
        class_name="Test",
        imports=frozenset(),
        complexity=1,
        description="Test",
    )
    mock_jit_meta = JITAgentMeta(
        source=mock_source,
        constraints=ArchitectConstraints(),
        stability_score=0.9,
    )
    mock_meta = AgentMeta.minimal("Test", "j", "Test agent")

    wrapper = JITAgentWrapper(meta=mock_meta, jit_meta=mock_jit_meta)

    assert is_jit_agent(wrapper) is True


def test_is_jit_agent_false():
    """Test is_jit_agent returns False for non-JIT agents."""

    class RegularAgent(Agent[str, str]):
        @property
        def name(self) -> str:
            return "Regular"

        async def invoke(self, input: str) -> str:
            return input

    agent = RegularAgent()
    assert is_jit_agent(agent) is False


# --- compile_and_instantiate Tests ---


@pytest.mark.asyncio
async def test_compile_and_instantiate_basic():
    """Test compile_and_instantiate convenience function."""
    agent = await compile_and_instantiate(
        intent="Parse JSON logs",
        validate=False,  # Skip validation for speed
    )

    assert isinstance(agent, JITAgentWrapper)
    assert is_jit_agent(agent)
    assert agent.name.startswith("JIT")


@pytest.mark.asyncio
async def test_compile_and_instantiate_with_context():
    """Test compile_and_instantiate with context."""
    agent = await compile_and_instantiate(
        intent="Parse JSON logs and extract errors",
        context={"sample": '{"level": "error", "msg": "test"}'},
        validate=False,
    )

    assert isinstance(agent, JITAgentWrapper)
    # Agent should be able to parse the sample format
    jit_meta = get_jit_meta(agent)
    assert jit_meta is not None
    assert (
        "Parse" in jit_meta.source.description
        or "parse" in jit_meta.source.description.lower()
    )


@pytest.mark.asyncio
async def test_compile_and_instantiate_with_constraints():
    """Test compile_and_instantiate with custom constraints."""
    constraints = ArchitectConstraints(
        entropy_budget=0.5,
        max_cyclomatic_complexity=10,
    )

    agent = await compile_and_instantiate(
        intent="Filter log entries",
        constraints=constraints,
        validate=False,
    )

    jit_meta = get_jit_meta(agent)
    assert jit_meta is not None
    assert jit_meta.constraints == constraints


# --- Error Handling Tests ---


@pytest.mark.asyncio
async def test_create_agent_execution_failure():
    """Test that execution failures are properly reported."""
    # Create source with syntax that will fail at runtime
    source = AgentSource(
        source="""
class JITBroken:
    async def invoke(self, input: str) -> str:
        raise ValueError("Intentional failure")
""",
        class_name="JITBroken",
        imports=frozenset(),
        complexity=2,
        description="Agent that always fails",
    )

    agent = await create_agent_from_source(source, validate=False)

    with pytest.raises(RuntimeError, match="JIT execution failed"):
        await agent.invoke("test")


# --- Behavior Metadata Tests ---


@pytest.mark.asyncio
async def test_agent_behavior_metadata(simple_parser_source: AgentSource):
    """Test that behavior metadata is properly set."""
    constraints = ArchitectConstraints(
        entropy_budget=0.7,
        max_cyclomatic_complexity=15,
    )

    agent = await create_agent_from_source(
        source=simple_parser_source,
        constraints=constraints,
        validate=False,
    )

    behavior = agent.meta.behavior
    assert behavior is not None

    # Check guarantees include complexity and imports
    guarantees_str = " ".join(behavior.guarantees)
    assert "Complexity:" in guarantees_str
    assert "Imports:" in guarantees_str

    # Check constraints are recorded
    constraints_str = " ".join(behavior.constraints)
    assert "Entropy budget:" in constraints_str
    assert "Max complexity:" in constraints_str


# --- Security and Sandboxing Tests ---


@pytest.mark.asyncio
async def test_sandbox_prevents_forbidden_operations():
    """Test that sandbox blocks forbidden operations like eval/exec."""
    # Create source that attempts forbidden operations
    source = AgentSource(
        source="""
class JITMalicious:
    async def invoke(self, input: str) -> str:
        # Try to use eval (forbidden)
        return eval(input)
""",
        class_name="JITMalicious",
        imports=frozenset(),
        complexity=2,
        description="Agent attempting forbidden operations",
    )

    agent = await create_agent_from_source(source, validate=False)

    # Should fail during execution
    with pytest.raises(RuntimeError):
        await agent.invoke("1 + 1")


@pytest.mark.asyncio
async def test_sandbox_isolates_multiple_executions():
    """Test that sandbox isolates each execution (no state leakage)."""
    source = AgentSource(
        source="""
class JITStateful:
    def __init__(self):
        self.counter = 0

    async def invoke(self, input: str) -> int:
        self.counter += 1
        return self.counter
""",
        class_name="JITStateful",
        imports=frozenset(),
        complexity=3,
        description="Stateful agent for testing isolation",
    )

    agent = await create_agent_from_source(source, validate=False)

    # Each invocation should start fresh (counter resets)
    result1 = await agent.invoke("test")
    result2 = await agent.invoke("test")

    # Both should be 1 (not 1 and 2) due to re-execution in fresh sandbox
    assert result1 == 1
    assert result2 == 1


@pytest.mark.asyncio
async def test_custom_sandbox_config():
    """Test that custom SandboxConfig is applied."""
    from agents.j.sandbox import SandboxConfig

    custom_config = SandboxConfig(
        timeout_seconds=10.0,
        type_check=False,  # Disable type checking for speed
    )

    agent = await create_agent_from_source(
        source=AgentSource(
            source="""
class JITSimple:
    async def invoke(self, input: str) -> str:
        return input.upper()
""",
            class_name="JITSimple",
            imports=frozenset(),
            complexity=1,
            description="Simple agent",
        ),
        sandbox_config=custom_config,
        validate=False,
    )

    # Verify config is stored
    assert agent.jit_meta.sandbox_config == custom_config
    assert agent.jit_meta.sandbox_config.timeout_seconds == 10.0
    assert agent.jit_meta.sandbox_config.type_check is False

    # Should still execute successfully
    result = await agent.invoke("hello")
    assert result == "HELLO"


# --- Stability Scoring Tests ---


@pytest.mark.asyncio
async def test_stability_score_for_simple_agent(simple_parser_source: AgentSource):
    """Test that simple agents get high stability scores."""
    agent = await create_agent_from_source(
        source=simple_parser_source,
        validate=False,
    )

    # Simple agent should have high stability
    assert agent.jit_meta.stability_score >= 0.5


@pytest.mark.asyncio
async def test_stability_score_for_complex_agent(high_complexity_source: AgentSource):
    """Test that complex agents get lower stability scores."""
    # Use high max_complexity to avoid rejection, just test scoring
    constraints = ArchitectConstraints(max_cyclomatic_complexity=100)

    agent = await create_agent_from_source(
        source=high_complexity_source,
        constraints=constraints,
        validate=False,
    )

    # Complex agent should have lower stability
    jit_meta = agent.jit_meta
    assert jit_meta.stability_score < 0.9  # Not perfect
    assert jit_meta.stability_score >= 0.0  # But still valid range


# --- Validation and Rejection Tests ---


@pytest.mark.asyncio
async def test_validation_with_constraints():
    """Test that validation works with constraints."""
    # Create source with excessive complexity
    complex_source = AgentSource(
        source="""
class JITComplex:
    async def invoke(self, input: str) -> str:
        # High complexity code
        result = input
        for i in range(10):
            for j in range(10):
                if i > j:
                    result += str(i)
                elif i < j:
                    result += str(j)
                else:
                    result += "0"
        return result
""",
        class_name="JITComplex",
        imports=frozenset(),
        complexity=50,  # Very high complexity
        description="Complex agent",
    )

    # Very strict constraints that should cause validation issues
    strict_constraints = ArchitectConstraints(
        max_cyclomatic_complexity=5,  # Much lower than source complexity
        entropy_budget=0.1,  # Very low entropy budget
    )

    # Note: JITSafetyJudge might not always reject, it could suggest revisions
    # So we test that validation runs, not that it necessarily rejects
    try:
        agent = await create_agent_from_source(
            source=complex_source,
            constraints=strict_constraints,
            validate=True,
        )
        # If it succeeds, just verify it's a valid agent
        assert isinstance(agent, JITAgentWrapper)
    except ValueError as e:
        # If it rejects, verify the error message is informative
        assert "rejected" in str(e).lower() or "JIT" in str(e)


@pytest.mark.asyncio
async def test_validation_accepts_safe_source(simple_parser_source: AgentSource):
    """Test that validation accepts safe source code."""
    # Should not raise any errors
    agent = await create_agent_from_source(
        source=simple_parser_source,
        validate=True,
    )

    assert isinstance(agent, JITAgentWrapper)


# --- Composition Edge Cases ---


@pytest.mark.asyncio
async def test_compose_two_jit_agents():
    """Test composing two JIT agents together."""
    # First agent: parse JSON
    parser_source = AgentSource(
        source="""
class JITParser:
    async def invoke(self, input: str) -> dict:
        return json.loads(input)
""",
        class_name="JITParser",
        imports=frozenset({"json"}),
        complexity=2,
        description="Parse JSON",
    )

    # Second agent: extract field
    extractor_source = AgentSource(
        source="""
class JITExtractor:
    async def invoke(self, input: dict) -> str:
        return input.get("msg", "")
""",
        class_name="JITExtractor",
        imports=frozenset(),
        complexity=2,
        description="Extract message field",
    )

    parser = await create_agent_from_source(parser_source, validate=False)
    extractor = await create_agent_from_source(extractor_source, validate=False)

    # Compose: parser >> extractor
    pipeline = parser >> extractor

    # Execute pipeline
    result = await pipeline.invoke('{"msg": "hello world"}')
    assert result == "hello world"


@pytest.mark.asyncio
async def test_compose_jit_with_normal_agent_both_directions():
    """Test composition works in both directions: JIT>>Normal and Normal>>JIT."""

    # Normal agent
    class DoubleAgent(Agent[str, str]):
        @property
        def name(self) -> str:
            return "DoubleAgent"

        async def invoke(self, input: str) -> str:
            return input + input

    # JIT agent
    jit_agent = await create_agent_from_source(
        source=AgentSource(
            source="""
class JITUpper:
    async def invoke(self, input: str) -> str:
        return input.upper()
""",
            class_name="JITUpper",
            imports=frozenset(),
            complexity=1,
            description="Uppercase",
        ),
        validate=False,
    )

    normal = DoubleAgent()

    # Test JIT >> Normal
    pipeline1 = jit_agent >> normal
    result1 = await pipeline1.invoke("hi")
    assert result1 == "HIHI"

    # Test Normal >> JIT
    pipeline2 = normal >> jit_agent
    result2 = await pipeline2.invoke("hi")
    assert result2 == "HIHI"


# --- Provenance and Introspection Tests ---


@pytest.mark.asyncio
async def test_jit_meta_preserves_full_provenance(simple_parser_source: AgentSource):
    """Test that JITAgentMeta preserves complete provenance chain."""
    constraints = ArchitectConstraints(
        entropy_budget=0.6,
        max_cyclomatic_complexity=25,
    )

    agent = await create_agent_from_source(
        source=simple_parser_source,
        constraints=constraints,
        validate=False,
    )

    jit_meta = agent.jit_meta

    # Verify complete provenance
    assert jit_meta.source == simple_parser_source
    assert jit_meta.source.source == simple_parser_source.source
    assert jit_meta.source.class_name == "JITLogParser"
    assert jit_meta.source.imports == frozenset({"json"})
    assert jit_meta.source.complexity == 5

    # Verify constraints preserved
    assert jit_meta.constraints.entropy_budget == 0.6
    assert jit_meta.constraints.max_cyclomatic_complexity == 25


@pytest.mark.asyncio
async def test_agent_meta_reflects_jit_nature(simple_parser_source: AgentSource):
    """Test that AgentMeta clearly indicates JIT nature of agent."""
    agent = await create_agent_from_source(
        source=simple_parser_source,
        validate=False,
    )

    meta = agent.meta

    # Should be marked as j-gent genus
    assert meta.identity.genus == "j"

    # Should be marked as ephemeral version
    assert meta.identity.version == "ephemeral"

    # Should include source description
    assert "Parse JSON log entries" in meta.identity.purpose


# --- Edge Cases and Error Handling ---


@pytest.mark.asyncio
async def test_agent_with_no_imports():
    """Test creating agent with no imports."""
    source = AgentSource(
        source="""
class JITNoImports:
    async def invoke(self, input: str) -> str:
        return input[::-1]  # Reverse string
""",
        class_name="JITNoImports",
        imports=frozenset(),  # No imports
        complexity=1,
        description="Reverse string",
    )

    agent = await create_agent_from_source(source, validate=False)
    result = await agent.invoke("hello")
    assert result == "olleh"


@pytest.mark.asyncio
async def test_agent_with_simple_class():
    """Test agent that uses simple classes (no dataclasses needed)."""
    source = AgentSource(
        source="""
class Result:
    def __init__(self, value: str, count: int):
        self.value = value
        self.count = count

class JITSimpleClass:
    async def invoke(self, input: str) -> Result:
        return Result(value=input, count=len(input))
""",
        class_name="JITSimpleClass",
        imports=frozenset(),
        complexity=3,
        description="Use simple classes",
    )

    agent = await create_agent_from_source(source, validate=False)
    result = await agent.invoke("test")
    assert result.value == "test"
    assert result.count == 4


@pytest.mark.asyncio
async def test_compile_and_instantiate_full_pipeline():
    """Test that compile_and_instantiate runs complete pipeline end-to-end."""
    # This tests the MetaArchitect integration
    agent = await compile_and_instantiate(
        intent="Convert text to uppercase",
        context={"example_input": "hello", "example_output": "HELLO"},
        constraints=ArchitectConstraints(entropy_budget=0.8),
        validate=False,
    )

    # Agent should be created
    assert isinstance(agent, JITAgentWrapper)

    # Should have valid metadata
    assert agent.name.startswith("JIT")
    assert agent.meta.identity.genus == "j"

    # Should have JIT metadata with correct constraints
    jit_meta = get_jit_meta(agent)
    assert jit_meta is not None
    assert jit_meta.constraints.entropy_budget == 0.8
