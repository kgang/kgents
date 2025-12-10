"""
Tests for G-gent Phase 5: F-gent (Forge) Integration

Tests the bridge between G-gent tongue synthesis and F-gent artifact forging.
"""

import pytest

from agents.g.types import (
    Tongue,
    GrammarLevel,
    GrammarFormat,
    ConstraintProof,
    Example,
    ParserConfig,
    InterpreterConfig,
)
from agents.g.forge_integration import (
    InterfaceTongue,
    TongueEmbedding,
    create_artifact_interface,
    embed_tongue_in_contract,
    create_invocation_handler,
    bind_handlers,
    forge_with_interface,
    FGENT_AVAILABLE,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_tongue() -> Tongue:
    """Create a sample tongue for testing."""
    grammar = '<command> ::= <verb> <noun>\n<verb> ::= "CHECK" | "ADD"\n<noun> ::= <date> | <event>'
    return Tongue(
        name="CalendarTongue",
        version="1.0.0",
        lexicon=frozenset(["CHECK", "ADD", "date", "event"]),
        grammar=grammar,
        mime_type="application/vnd.kgents.calendar-dsl",
        level=GrammarLevel.COMMAND,
        format=GrammarFormat.BNF,
        parser_config=ParserConfig(
            strategy="regex",
            grammar_format=GrammarFormat.BNF,
            grammar_spec=grammar,
        ),
        interpreter_config=InterpreterConfig(
            runtime="python",
        ),
        domain="Calendar Management",
        constraints=("No deletes",),
        examples=(
            Example(text="CHECK 2024-12-15"),
            Example(text="ADD meeting"),
        ),
        constraint_proofs=(
            ConstraintProof(
                constraint="No deletes",
                mechanism="verb DELETE not in lexicon - grammatically impossible",
            ),
        ),
    )


@pytest.fixture
def sample_interface(sample_tongue: Tongue) -> InterfaceTongue:
    """Create a sample interface tongue."""
    return InterfaceTongue(
        tongue=sample_tongue,
        artifact_name="CalendarAgent",
        operations={"CHECK": "View calendar entries", "ADD": "Create new entry"},
        handlers={},
        examples=["CHECK 2024-12-15", "ADD meeting"],
    )


@pytest.fixture
def calendar_handlers() -> dict:
    """Sample handlers for calendar operations."""
    return {
        "CHECK": lambda noun, ctx: {"action": "check", "target": noun},
        "ADD": lambda noun, ctx: {"action": "add", "target": noun},
    }


# =============================================================================
# InterfaceTongue Tests
# =============================================================================


class TestInterfaceTongue:
    """Tests for InterfaceTongue class."""

    def test_interface_tongue_creation(self, sample_tongue: Tongue):
        """Test creating an InterfaceTongue."""
        interface = InterfaceTongue(
            tongue=sample_tongue,
            artifact_name="TestAgent",
            operations={"TEST": "Test operation"},
        )

        assert interface.tongue == sample_tongue
        assert interface.artifact_name == "TestAgent"
        assert "TEST" in interface.operations
        assert interface.handlers == {}

    def test_interface_tongue_with_handlers(self, sample_tongue: Tongue):
        """Test InterfaceTongue with bound handlers."""

        def handler(noun, ctx):
            return f"handled: {noun}"

        interface = InterfaceTongue(
            tongue=sample_tongue,
            artifact_name="TestAgent",
            operations={},
            handlers={"CHECK": handler},
        )

        assert "CHECK" in interface.handlers
        assert interface.handlers["CHECK"]("test", {}) == "handled: test"

    def test_interface_tongue_examples(self, sample_interface: InterfaceTongue):
        """Test that examples are preserved."""
        assert len(sample_interface.examples) == 2
        assert "CHECK 2024-12-15" in sample_interface.examples


# =============================================================================
# TongueEmbedding Tests
# =============================================================================


class TestTongueEmbedding:
    """Tests for TongueEmbedding serialization."""

    def test_embedding_from_tongue(self, sample_tongue: Tongue):
        """Test creating embedding from tongue."""
        embedding = TongueEmbedding.from_tongue(sample_tongue)

        assert embedding.tongue_name == "CalendarTongue"
        assert embedding.tongue_domain == "Calendar Management"
        assert embedding.tongue_level == "COMMAND"
        assert embedding.tongue_format == "BNF"
        assert "No deletes" in embedding.constraints

    def test_embedding_to_dict(self, sample_tongue: Tongue):
        """Test serializing embedding to dict."""
        embedding = TongueEmbedding.from_tongue(sample_tongue)
        data = embedding.to_dict()

        assert isinstance(data, dict)
        assert data["tongue_name"] == "CalendarTongue"
        assert data["tongue_domain"] == "Calendar Management"
        assert "grammar_spec" in data

    def test_embedding_from_dict(self, sample_tongue: Tongue):
        """Test deserializing embedding from dict."""
        embedding = TongueEmbedding.from_tongue(sample_tongue)
        data = embedding.to_dict()
        restored = TongueEmbedding.from_dict(data)

        assert restored.tongue_name == embedding.tongue_name
        assert restored.tongue_domain == embedding.tongue_domain
        assert restored.tongue_level == embedding.tongue_level
        assert restored.constraints == embedding.constraints

    def test_embedding_round_trip(self, sample_tongue: Tongue):
        """Test round-trip serialization."""
        original = TongueEmbedding.from_tongue(sample_tongue)
        data = original.to_dict()
        restored = TongueEmbedding.from_dict(data)

        assert original.tongue_name == restored.tongue_name
        assert original.grammar_spec == restored.grammar_spec
        assert original.operations == restored.operations

    def test_embedding_extracts_operations(self, sample_tongue: Tongue):
        """Test that operations are extracted from BNF grammar."""
        embedding = TongueEmbedding.from_tongue(sample_tongue)

        # Should extract CHECK and ADD from the grammar
        assert "CHECK" in embedding.operations or "ADD" in embedding.operations

    def test_embedding_extracts_examples(self, sample_tongue: Tongue):
        """Test that examples are extracted from tongue."""
        embedding = TongueEmbedding.from_tongue(sample_tongue)

        assert len(embedding.examples) == 2
        assert "CHECK 2024-12-15" in embedding.examples


# =============================================================================
# create_artifact_interface Tests
# =============================================================================


class TestCreateArtifactInterface:
    """Tests for create_artifact_interface function."""

    @pytest.mark.asyncio
    async def test_create_basic_interface(self):
        """Test creating a basic artifact interface."""
        interface = await create_artifact_interface(
            domain="File Operations",
            constraints=["No deletes"],
        )

        assert interface.tongue is not None
        assert interface.tongue.domain == "File Operations"
        assert interface.artifact_name is not None

    @pytest.mark.asyncio
    async def test_create_interface_with_operations(self):
        """Test creating interface with explicit operations."""
        interface = await create_artifact_interface(
            domain="Task Management",
            operations={"CREATE": "Create a task", "LIST": "List all tasks"},
        )

        assert "CREATE" in interface.operations or "LIST" in interface.operations

    @pytest.mark.asyncio
    async def test_create_interface_with_constraints(self):
        """Test that constraints are passed to tongue."""
        interface = await create_artifact_interface(
            domain="Database",
            constraints=["Read-only", "No DROP statements"],
        )

        # Constraints should be in tongue (constraints are plain strings)
        constraint_descs = list(interface.tongue.constraints)
        assert (
            "Read-only" in constraint_descs or "No DROP statements" in constraint_descs
        )

    @pytest.mark.asyncio
    async def test_create_interface_with_examples(self):
        """Test creating interface with example commands."""
        examples = ["GET user/123", "LIST users"]
        interface = await create_artifact_interface(
            domain="API Client",
            examples=examples,
        )

        assert interface.examples == examples

    @pytest.mark.asyncio
    async def test_create_interface_custom_artifact_name(self):
        """Test specifying custom artifact name."""
        interface = await create_artifact_interface(
            domain="Weather",
            artifact_name="WeatherBot",
        )

        assert interface.artifact_name == "WeatherBot"

    @pytest.mark.asyncio
    async def test_create_schema_interface(self):
        """Test creating a schema-level interface."""
        interface = await create_artifact_interface(
            domain="User Profile",
            level=GrammarLevel.SCHEMA,
        )

        assert interface.tongue.level == GrammarLevel.SCHEMA


# =============================================================================
# bind_handlers Tests
# =============================================================================


class TestBindHandlers:
    """Tests for bind_handlers function."""

    def test_bind_single_handler(self, sample_interface: InterfaceTongue):
        """Test binding a single handler."""

        def handler(noun, ctx):
            return f"handled: {noun}"

        result = bind_handlers(sample_interface, {"CHECK": handler})

        assert "CHECK" in result.handlers
        assert result.handlers["CHECK"]("test", {}) == "handled: test"

    def test_bind_multiple_handlers(self, sample_interface: InterfaceTongue):
        """Test binding multiple handlers."""
        handlers = {
            "CHECK": lambda noun, ctx: f"checked: {noun}",
            "ADD": lambda noun, ctx: f"added: {noun}",
        }
        result = bind_handlers(sample_interface, handlers)

        assert "CHECK" in result.handlers
        assert "ADD" in result.handlers

    def test_bind_handlers_returns_same_instance(
        self, sample_interface: InterfaceTongue
    ):
        """Test that bind_handlers modifies and returns same instance."""
        result = bind_handlers(sample_interface, {"TEST": lambda n, c: n})

        assert result is sample_interface


# =============================================================================
# create_invocation_handler Tests
# =============================================================================


class TestCreateInvocationHandler:
    """Tests for create_invocation_handler function."""

    def test_create_handler(
        self, sample_interface: InterfaceTongue, calendar_handlers: dict
    ):
        """Test creating an invocation handler."""
        invoke = create_invocation_handler(sample_interface, calendar_handlers)

        assert callable(invoke)

    def test_handler_is_callable(
        self, sample_interface: InterfaceTongue, calendar_handlers: dict
    ):
        """Test that created handler is callable."""
        invoke = create_invocation_handler(sample_interface, calendar_handlers)

        # Should be callable with command and optional context
        assert callable(invoke)


# =============================================================================
# embed_tongue_in_contract Tests (requires F-gent)
# =============================================================================


@pytest.mark.skipif(not FGENT_AVAILABLE, reason="F-gent not available")
class TestEmbedTongueInContract:
    """Tests for embed_tongue_in_contract function."""

    def test_embed_creates_new_contract(self, sample_interface: InterfaceTongue):
        """Test that embedding creates a new contract."""
        from agents.f.contract import Contract

        original = Contract(
            agent_name="TestAgent",
            input_type="str",
            output_type="dict",
        )

        result = embed_tongue_in_contract(original, sample_interface)

        # Should be different object
        assert result is not original
        assert result.agent_name == original.agent_name

    def test_embed_sets_interface_tongue(self, sample_interface: InterfaceTongue):
        """Test that embedding sets interface_tongue field."""
        from agents.f.contract import Contract

        original = Contract(
            agent_name="TestAgent",
            input_type="str",
            output_type="dict",
        )

        result = embed_tongue_in_contract(original, sample_interface)

        assert result.interface_tongue is not None
        assert isinstance(result.interface_tongue, dict)
        assert result.interface_tongue["tongue_name"] == "CalendarTongue"

    def test_embed_updates_input_type(self, sample_interface: InterfaceTongue):
        """Test that embedding updates input type to DSL."""
        from agents.f.contract import Contract

        original = Contract(
            agent_name="TestAgent",
            input_type="str",
            output_type="dict",
        )

        result = embed_tongue_in_contract(original, sample_interface)

        assert "DSL<" in result.input_type
        assert sample_interface.tongue.domain in result.input_type

    def test_embed_adds_tongue_invariants(self, sample_interface: InterfaceTongue):
        """Test that embedding adds tongue-related invariants."""
        from agents.f.contract import Contract

        original = Contract(
            agent_name="TestAgent",
            input_type="str",
            output_type="dict",
            invariants=[],
        )

        result = embed_tongue_in_contract(original, sample_interface)

        # Should have at least one invariant about the interface
        assert len(result.invariants) > 0
        interface_invariants = [
            inv for inv in result.invariants if "Interface" in inv.description
        ]
        assert len(interface_invariants) > 0

    def test_embed_preserves_original_invariants(
        self, sample_interface: InterfaceTongue
    ):
        """Test that original invariants are preserved."""
        from agents.f.contract import Contract, Invariant

        original = Contract(
            agent_name="TestAgent",
            input_type="str",
            output_type="dict",
            invariants=[
                Invariant(
                    description="Original invariant",
                    property="test",
                    category="behavioral",
                )
            ],
        )

        result = embed_tongue_in_contract(original, sample_interface)

        # Original invariant should still be there
        original_invariants = [
            inv for inv in result.invariants if inv.description == "Original invariant"
        ]
        assert len(original_invariants) == 1


# =============================================================================
# forge_with_interface Tests (requires F-gent)
# =============================================================================


@pytest.mark.skipif(not FGENT_AVAILABLE, reason="F-gent not available")
class TestForgeWithInterface:
    """Tests for forge_with_interface function."""

    @pytest.mark.asyncio
    async def test_forge_returns_contract_and_interface(self):
        """Test that forge returns both contract and interface."""
        contract, interface = await forge_with_interface(
            intent_text="Create a calendar agent that can check and add events",
            domain="Calendar",
        )

        assert contract is not None
        assert interface is not None

    @pytest.mark.asyncio
    async def test_forge_contract_has_tongue(self):
        """Test that forged contract has interface tongue."""
        contract, interface = await forge_with_interface(
            intent_text="Create a task manager",
            domain="Task Management",
        )

        assert contract.interface_tongue is not None

    @pytest.mark.asyncio
    async def test_forge_with_constraints(self):
        """Test forging with constraints."""
        contract, interface = await forge_with_interface(
            intent_text="Create a read-only database viewer",
            domain="Database",
            constraints=["Read-only", "No modifications"],
        )

        # Constraints should be reflected in interface (constraints are plain strings)
        constraint_descs = list(interface.tongue.constraints)
        assert any(
            "Read-only" in c or "modification" in c.lower() for c in constraint_descs
        )

    @pytest.mark.asyncio
    async def test_forge_with_handlers(self, calendar_handlers: dict):
        """Test forging with bound handlers."""
        contract, interface = await forge_with_interface(
            intent_text="Create a calendar assistant",
            domain="Calendar",
            handlers=calendar_handlers,
        )

        assert "CHECK" in interface.handlers or "ADD" in interface.handlers


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete workflow from interface creation to execution."""
        # 1. Create interface
        interface = await create_artifact_interface(
            domain="Simple Commands",
            constraints=["Safe operations only"],
            examples=["RUN task1"],
        )

        # 2. Bind handlers
        handlers = {
            "RUN": lambda noun, ctx: {"executed": noun},
        }
        interface = bind_handlers(interface, handlers)

        # 3. Create invocation handler
        invoke = create_invocation_handler(interface)

        # Should be callable
        assert callable(invoke)

    @pytest.mark.asyncio
    async def test_embedding_round_trip(self, sample_tongue: Tongue):
        """Test that tongue embedding can be restored."""
        # Create embedding
        embedding = TongueEmbedding.from_tongue(sample_tongue)

        # Serialize
        data = embedding.to_dict()

        # Deserialize
        restored = TongueEmbedding.from_dict(data)

        # Verify
        assert restored.tongue_name == sample_tongue.name
        assert restored.tongue_domain == sample_tongue.domain
        assert restored.grammar_spec == sample_tongue.grammar

    @pytest.mark.skipif(not FGENT_AVAILABLE, reason="F-gent not available")
    @pytest.mark.asyncio
    async def test_artifact_with_interface_workflow(self):
        """Test complete artifact creation with interface workflow."""
        from agents.f.contract import Contract

        # 1. Create interface
        interface = await create_artifact_interface(
            domain="File Operations",
            constraints=["No deletes"],
            artifact_name="FileAgent",
        )

        # 2. Create base contract
        base_contract = Contract(
            agent_name="FileAgent",
            input_type="str",
            output_type="dict",
            semantic_intent="Perform file operations safely",
        )

        # 3. Embed tongue
        enhanced_contract = embed_tongue_in_contract(base_contract, interface)

        # 4. Verify
        assert enhanced_contract.interface_tongue is not None
        assert (
            enhanced_contract.interface_tongue["tongue_name"] == interface.tongue.name
        )
        assert "DSL<" in enhanced_contract.input_type


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_constraints(self):
        """Test interface with no constraints."""
        interface = await create_artifact_interface(
            domain="Unconstrained",
            constraints=[],
        )

        assert interface.tongue is not None

    @pytest.mark.asyncio
    async def test_empty_operations(self):
        """Test interface with no explicit operations."""
        interface = await create_artifact_interface(
            domain="Simple",
            operations={},
        )

        # Should still have tongue
        assert interface.tongue is not None

    def test_embedding_missing_fields(self):
        """Test deserializing embedding with minimal fields."""
        minimal_data = {
            "tongue_name": "Test",
            "tongue_domain": "Test Domain",
            "tongue_level": "COMMAND",
            "tongue_format": "BNF",
            "grammar_spec": "<test>",
        }

        embedding = TongueEmbedding.from_dict(minimal_data)

        assert embedding.constraints == []
        assert embedding.operations == []
        assert embedding.examples == []

    def test_interface_tongue_without_handlers(self, sample_tongue: Tongue):
        """Test InterfaceTongue without any handlers."""
        interface = InterfaceTongue(
            tongue=sample_tongue,
            artifact_name="NoHandlerAgent",
            operations={},
            handlers={},
        )

        # Should create successfully
        assert interface.handlers == {}
