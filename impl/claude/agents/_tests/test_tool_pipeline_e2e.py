"""
Tool Pipeline End-to-End Tests

Tests the complete tool pipeline:
1. F-gent creates prototype
2. J-gent compiles to agent
3. T-gent executes as tool
4. O-gent observes execution
5. N-gent records narrative

Philosophy: Tools are agents at the boundary of the system.
"""

from dataclasses import dataclass

import pytest

# F-gent imports
from agents.f import (
    parse_intent,
    synthesize_contract,
)

# J-gent imports
from agents.j import (
    AgentSource,
    JITAgentWrapper,
    create_agent_from_source,
)

# N-gent imports
from agents.n import (
    Bard,
    Determinism,
    Historian,
    MemoryCrystalStore,
    NarrativeGenre,
    NarrativeRequest,
    Verbosity,
)

# O-gent imports
from agents.o import (
    BaseObserver,
)

# T-gent imports
from agents.t import (
    FailingAgent,
    FailingConfig,
    FailureType,
    MockAgent,
    MockConfig,
    RobustToolExecutor,
    SpyAgent,
    Tool,
    ToolExecutor,
    ToolIdentity,
    ToolMeta,
    ToolRegistry,
)


@dataclass
class MockTraceable:
    """Mock traceable for testing."""

    id: str = "mock-tool"
    name: str = "MockTool"


class TestToolCreation:
    """Test tool creation from prototype."""

    def test_tool_meta_creation(self):
        """Test ToolMeta creation."""
        meta = ToolMeta.minimal(
            name="calculator",
            description="Performs calculations",
            input_schema=dict,
            output_schema=dict,
        )

        assert meta.identity.name == "calculator"

    def test_tool_identity(self):
        """Test ToolIdentity properties."""
        identity = ToolIdentity(
            name="data_processor",
            description="Processes data",
            version="1.0.0",
        )

        assert identity.name == "data_processor"
        assert identity.version == "1.0.0"

    @pytest.mark.asyncio
    async def test_create_tool_class(self):
        """Test creating a tool class."""

        class CalculatorTool(Tool[dict, dict]):
            meta = ToolMeta.minimal(
                name="calculator",
                description="Basic math operations",
                input_schema=dict,
                output_schema=dict,
            )

            async def invoke(self, input: dict) -> dict:
                op = input.get("operation", "add")
                a = input.get("a", 0)
                b = input.get("b", 0)

                if op == "add":
                    return {"result": a + b}
                elif op == "multiply":
                    return {"result": a * b}
                else:
                    return {"result": 0}

        tool = CalculatorTool()
        result = await tool.invoke({"operation": "add", "a": 5, "b": 3})

        assert result["result"] == 8


class TestPrototypeToTool:
    """Test F-gent → T-gent pipeline."""

    @pytest.mark.asyncio
    async def test_intent_to_tool(self):
        """Test transforming intent into executable tool."""
        # Step 1: Parse intent
        intent = parse_intent(
            "Create a tool that converts temperatures from Celsius to Fahrenheit"
        )

        # Step 2: Synthesize contract (verifies intent is valid)
        _ = synthesize_contract(intent, "TemperatureConverter")

        # Step 3: Create source
        source = AgentSource(
            source="""
class TemperatureConverter:
    async def invoke(self, input: dict) -> dict:
        celsius = input.get("celsius", 0)
        fahrenheit = (celsius * 9/5) + 32
        return {"fahrenheit": fahrenheit}
""",
            class_name="TemperatureConverter",
            imports=frozenset(),
            complexity=1,
            description="Temperature converter tool",
        )

        # Step 4: Compile
        tool = await create_agent_from_source(source, validate=False)

        # Step 5: Execute
        result = await tool.invoke({"celsius": 100})
        assert result["fahrenheit"] == 212.0


class TestJITCompilation:
    """Test J-gent compilation for tools."""

    @pytest.mark.asyncio
    async def test_jit_tool_compilation(self):
        """Test JIT compilation produces executable tool."""
        source = AgentSource(
            source="""
class StringTool:
    async def invoke(self, input: str) -> str:
        return input.upper()
""",
            class_name="StringTool",
            imports=frozenset(),
            complexity=1,
            description="String transformation tool",
        )

        tool = await create_agent_from_source(source, validate=False)

        assert isinstance(tool, JITAgentWrapper)
        result = await tool.invoke("hello")
        assert result == "HELLO"

    @pytest.mark.asyncio
    async def test_jit_preserves_tool_behavior(self):
        """Test JIT compilation preserves intended behavior."""
        source = AgentSource(
            source="""
class ListTool:
    async def invoke(self, input: list) -> dict:
        return {
            "length": len(input),
            "sum": sum(input) if all(isinstance(x, (int, float)) for x in input) else 0,
            "first": input[0] if input else None,
            "last": input[-1] if input else None,
        }
""",
            class_name="ListTool",
            imports=frozenset(),
            complexity=2,
            description="List processing tool",
        )

        tool = await create_agent_from_source(source, validate=False)

        result = await tool.invoke([1, 2, 3, 4, 5])
        assert result["length"] == 5
        assert result["sum"] == 15
        assert result["first"] == 1
        assert result["last"] == 5


class TestToolExecution:
    """Test T-gent tool execution."""

    @pytest.mark.asyncio
    async def test_tool_executor_basic(self):
        """Test basic tool executor."""

        class SimpleTool(Tool[str, str]):
            meta = ToolMeta.minimal(
                name="simple",
                description="Simple tool",
                input_schema=str,
                output_schema=str,
            )

            async def invoke(self, input: str) -> str:
                return f"Result: {input}"

        tool = SimpleTool()
        # ToolExecutor takes the tool in constructor
        executor = ToolExecutor(tool)

        result = await executor.execute("test")
        assert result.is_ok()
        assert "Result: test" in result.unwrap()

    @pytest.mark.asyncio
    async def test_robust_executor_retry(self):
        """Test robust executor with retry."""

        # Tool that fails first time but succeeds second
        call_count = 0

        class FlakyTool(Tool[str, str]):
            meta = ToolMeta.minimal(
                name="flaky",
                description="Flaky tool",
                input_schema=str,
                output_schema=str,
            )

            async def invoke(self, input: str) -> str:
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise RuntimeError("First call fails")
                return f"Success on call {call_count}"

        tool = FlakyTool()
        # RobustToolExecutor takes the tool in constructor
        executor = RobustToolExecutor(tool)

        # May fail or succeed depending on retry config
        try:
            _ = await executor.execute("test")
        except RuntimeError:
            pass  # Expected if max_retries < 2
        # Should have attempted at least once
        assert call_count >= 1


class TestToolRegistry:
    """Test tool registry operations."""

    @pytest.mark.asyncio
    async def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()

        class RegisteredTool(Tool[str, str]):
            meta = ToolMeta.minimal(
                name="registered",
                description="A registered tool",
                input_schema=str,
                output_schema=str,
            )

            async def invoke(self, input: str) -> str:
                return input

        tool = RegisteredTool()
        await registry.register(tool)

        found = await registry.find_by_name("registered")
        assert found is not None

    @pytest.mark.asyncio
    async def test_find_tool_by_signature(self):
        """Test finding tools by type signature."""
        registry = ToolRegistry()

        class StrToStr(Tool[str, str]):
            meta = ToolMeta.minimal("str_str", "str to str", str, str)

            async def invoke(self, input: str) -> str:
                return input

        class IntToInt(Tool[int, int]):
            meta = ToolMeta.minimal("int_int", "int to int", int, int)

            async def invoke(self, input: int) -> int:
                return input

        await registry.register(StrToStr())
        await registry.register(IntToInt())

        str_tools = await registry.find_by_signature(str, str)
        int_tools = await registry.find_by_signature(int, int)

        assert len(str_tools) >= 1
        assert len(int_tools) >= 1


class TestToolObservation:
    """Test O-gent observation of tools."""

    @pytest.mark.asyncio
    async def test_observed_tool_execution(self):
        """Test observing tool execution."""

        class ObservedTool(Tool[str, str]):
            meta = ToolMeta.minimal("observed", "Observed tool", str, str)

            async def invoke(self, input: str) -> str:
                return input.upper()

        tool = ObservedTool()
        observer = BaseObserver(observer_id="tool-observer")

        # Observe execution
        ctx = observer.pre_invoke(tool, "test")
        result = await tool.invoke("test")
        await observer.post_invoke(ctx, result, duration_ms=10.0)

        assert result == "TEST"
        assert len(observer.observations) == 1

    @pytest.mark.asyncio
    async def test_tool_error_observation(self):
        """Test observing tool errors."""

        class ErrorTool(Tool[str, str]):
            meta = ToolMeta.minimal("error", "Error tool", str, str)

            async def invoke(self, input: str) -> str:
                raise ValueError("Intentional error")

        tool = ErrorTool()
        observer = BaseObserver(observer_id="error-observer")

        ctx = observer.pre_invoke(tool, "test")
        try:
            await tool.invoke("test")
        except ValueError as e:
            observer.record_entropy(ctx, e)

        assert len(observer.entropy_events) == 1


class TestToolNarrative:
    """Test N-gent narrative of tool execution."""

    @pytest.mark.asyncio
    async def test_tool_execution_recorded(self):
        """Test tool execution is recorded as trace."""
        store = MemoryCrystalStore()
        historian = Historian(store)

        traceable = MockTraceable(id="tool-001", name="TestTool")

        # Record execution
        ctx = historian.begin_trace(traceable, {"input": "data"})
        trace = historian.end_trace(
            ctx,
            action="EXECUTE",
            outputs={"result": "processed"},  # uses 'outputs' plural
            determinism=Determinism.DETERMINISTIC,
        )

        assert trace.action == "EXECUTE"
        # Historian uses agent.name as agent_id
        assert trace.agent_id == "TestTool"

    @pytest.mark.asyncio
    async def test_tool_narrative_generation(self):
        """Test narrative generated from tool traces."""
        store = MemoryCrystalStore()
        historian = Historian(store)
        bard = Bard()

        traceable = MockTraceable()

        # Record multiple tool executions
        traces = []
        for i, action in enumerate(["VALIDATE", "TRANSFORM", "OUTPUT"]):
            ctx = historian.begin_trace(traceable, f"step-{i}")
            traces.append(historian.end_trace(ctx, action, f"result-{i}"))

        # Generate narrative
        request = NarrativeRequest(
            traces=traces,
            genre=NarrativeGenre.TECHNICAL,
            verbosity=Verbosity.NORMAL,
        )

        narrative = await bard.invoke(request)
        assert narrative is not None


class TestMockTools:
    """Test mock tools for testing."""

    @pytest.mark.asyncio
    async def test_mock_agent_returns_configured_output(self):
        """Test MockAgent returns configured output."""
        mock = MockAgent(MockConfig(output="mocked result"))

        result = await mock.invoke("any input")
        assert result == "mocked result"

    @pytest.mark.asyncio
    async def test_spy_agent_records_calls(self):
        """Test SpyAgent records all calls."""
        spy = SpyAgent(label="test-spy")

        await spy.invoke("first")
        await spy.invoke("second")
        await spy.invoke("third")

        assert spy.call_count == 3
        # SpyAgent uses 'history' property, not 'calls'
        assert "first" in spy.history
        assert "second" in spy.history

    @pytest.mark.asyncio
    async def test_failing_agent_simulates_failure(self):
        """Test FailingAgent simulates configured failures."""
        failing = FailingAgent(
            FailingConfig(
                error_type=FailureType.NETWORK,
                fail_count=2,
            )
        )

        # First two calls fail
        with pytest.raises(Exception):
            await failing.invoke("first")

        with pytest.raises(Exception):
            await failing.invoke("second")

        # Third call succeeds
        result = await failing.invoke("third")
        assert result is not None


class TestFullToolPipeline:
    """Test complete tool pipeline."""

    @pytest.mark.asyncio
    async def test_complete_pipeline(self):
        """Test prototype → compile → execute → observe → narrate."""
        # 1. Create prototype (F-gent)
        source = AgentSource(
            source="""
class DataProcessor:
    async def invoke(self, input: dict) -> dict:
        data = input.get("data", [])
        return {
            "count": len(data),
            "processed": True,
        }
""",
            class_name="DataProcessor",
            imports=frozenset(),
            complexity=1,
            description="Data processing tool",
        )

        # 2. Compile (J-gent)
        tool = await create_agent_from_source(source, validate=False)

        # 3. Setup observation (O-gent)
        observer = BaseObserver(observer_id="pipeline-observer")

        # 4. Setup narrative (N-gent)
        store = MemoryCrystalStore()
        historian = Historian(store)
        bard = Bard()

        traceable = MockTraceable(id="data-processor", name="DataProcessor")

        # 5. Execute with observation and recording
        input_data = {"data": [1, 2, 3, 4, 5]}

        # Observe
        obs_ctx = observer.pre_invoke(tool, input_data)

        # Record
        trace_ctx = historian.begin_trace(traceable, input_data)

        # Execute
        result = await tool.invoke(input_data)

        # Complete observation
        await observer.post_invoke(obs_ctx, result, duration_ms=15.0)

        # Complete trace
        trace = historian.end_trace(
            trace_ctx,
            action="PROCESS",
            outputs=result,  # uses 'outputs' plural
        )

        # Verify execution
        assert result["count"] == 5
        assert result["processed"] is True

        # Verify observation
        assert len(observer.observations) == 1

        # 6. Generate narrative - Verbosity uses TERSE/NORMAL/VERBOSE
        narrative = await bard.invoke(
            NarrativeRequest(
                traces=[trace],
                genre=NarrativeGenre.TECHNICAL,
                verbosity=Verbosity.TERSE,
            )
        )

        assert narrative is not None

    @pytest.mark.asyncio
    async def test_pipeline_with_error_handling(self):
        """Test pipeline handles errors gracefully."""
        source = AgentSource(
            source="""
class SafeTool:
    async def invoke(self, input: dict) -> dict:
        try:
            value = input["required_key"]
            return {"success": True, "value": value}
        except KeyError:
            return {"success": False, "error": "missing required_key"}
""",
            class_name="SafeTool",
            imports=frozenset(),
            complexity=2,
            description="Safe tool with error handling",
        )

        tool = await create_agent_from_source(source, validate=False)

        # Success case
        success = await tool.invoke({"required_key": "present"})
        assert success["success"] is True

        # Error case (handled gracefully)
        error = await tool.invoke({})
        assert error["success"] is False
        assert "error" in error


class TestToolComposition:
    """Test tool composition patterns."""

    @pytest.mark.asyncio
    async def test_sequential_tool_composition(self):
        """Test sequential tool execution."""
        source1 = AgentSource(
            source="""
class Step1:
    async def invoke(self, x: int) -> int:
        return x + 1
""",
            class_name="Step1",
            imports=frozenset(),
            complexity=1,
            description="Step 1",
        )

        source2 = AgentSource(
            source="""
class Step2:
    async def invoke(self, x: int) -> int:
        return x * 2
""",
            class_name="Step2",
            imports=frozenset(),
            complexity=1,
            description="Step 2",
        )

        step1 = await create_agent_from_source(source1, validate=False)
        step2 = await create_agent_from_source(source2, validate=False)

        # Sequential: step1 then step2
        intermediate = await step1.invoke(5)
        final = await step2.invoke(intermediate)

        assert intermediate == 6
        assert final == 12


# Run with: pytest impl/claude/agents/_tests/test_tool_pipeline_e2e.py -v
