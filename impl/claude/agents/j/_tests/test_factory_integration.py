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

from bootstrap.types import Agent

from agents.j import (
    AgentSource,
    ArchitectConstraints,
)
from agents.j.factory_integration import (
    JITAgentMeta,
    JITAgentWrapper,
    create_agent_from_source,
    compile_and_instantiate,
    get_jit_meta,
    is_jit_agent,
)

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
