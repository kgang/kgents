"""
API Signature Database: Prevent hallucination by providing known API signatures.

This module provides a curated database of actual API signatures from kgents modules
to include in code generation prompts. This prevents the LLM from inventing APIs.

Usage:
    from .api_signatures import get_api_signatures

    sigs = get_api_signatures(["agents.e.experiment", "agents.b.hypothesis"])
    # Returns dict of module -> {name: signature}
"""

from __future__ import annotations

import inspect

# ============================================================================
# Curated API Signature Database
# ============================================================================

# Core kgents APIs that are frequently used and often hallucinated
CORE_APIS = {
    "CodeModule": """
@dataclass
class CodeModule:
    name: str
    path: Path
    category: str

    # CORRECT: Read code via path
    content = path.read_text()

    # WRONG: CodeModule.content (attribute doesn't exist)
    # WRONG: CodeModule.code (attribute doesn't exist)
""",
    "ImprovementMemory": """
class ImprovementMemory:
    def was_rejected(self, module: str, hypothesis: str) -> Optional[ImprovementRecord]
    def was_recently_accepted(self, module: str, hypothesis: str, days: int = 7) -> bool
    def record(self, module: str, hypothesis: str, description: str, outcome: str, ...) -> ImprovementRecord

    # CORRECT: memory.was_rejected(module, hypothesis)
    # WRONG: memory.is_rejected() (method doesn't exist)
""",
    "HypothesisEngine": """
class HypothesisEngine(Agent[HypothesisInput, HypothesisResult]):
    def __init__(self):  # No parameters
        ...

    # CORRECT: HypothesisEngine()
    # WRONG: HypothesisEngine(runtime=...) (doesn't accept runtime)
""",
    "HegelAgent": """
class HegelAgent(Agent[DialecticInput, DialecticOutput]):
    def __init__(self, contradict: Optional[Contradict] = None, sublate: Optional[Sublate] = None):
        ...

    # CORRECT: HegelAgent()
    # WRONG: HegelAgent(runtime=...) (doesn't accept runtime)
""",
    "Sublate": """
class Sublate(Agent[SublateInput, Synthesis | HoldTension]):
    def __init__(self):  # No parameters
        ...

    # CORRECT: Sublate()
    # WRONG: Sublate(runtime=...) (doesn't accept runtime)
""",
    "Agent": """
class Agent(Protocol[A, B]):
    @property
    def name(self) -> str: ...

    async def invoke(self, input: A) -> B: ...

    # CORRECT: await agent.invoke(input)
    # WRONG: agent.run() (method doesn't exist)
    # WRONG: agent.execute() (method doesn't exist)
""",
    "ASTAnalysisInput": """
@dataclass(frozen=True)
class ASTAnalysisInput:
    path: Path

    # CORRECT: ASTAnalysisInput(path=module.path)
    # WRONG: ASTAnalysisInput(content=...) (field doesn't exist)
    # WRONG: ASTAnalysisInput(category=...) (field doesn't exist)
""",
    "HypothesisInput": """
@dataclass(frozen=True)
class HypothesisInput:
    observations: list[str]
    domain: str
    question: str
    constraints: list[str] = field(default_factory=list)

    # CORRECT: HypothesisInput(observations=[...], domain="...", question="...")
    # WRONG: HypothesisInput(context=...) (field doesn't exist)
    # WRONG: HypothesisInput(count=...) (field doesn't exist)
""",
    "AgentContext": """
@dataclass
class AgentContext:
    system_prompt: str
    messages: list[dict[str, str]]
    temperature: float = 0.7
    max_tokens: int = 4000

    # CORRECT: AgentContext(system_prompt="...", messages=[...])
    # WRONG: AgentContext(agent_id=...) (field doesn't exist)
    # WRONG: AgentContext(parent_id=...) (field doesn't exist)
    # WRONG: AgentContext(request_id=...) (field doesn't exist)
""",
    "ExperimentStatus": """
class ExperimentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    HELD = "held"

    # CORRECT: ExperimentStatus.PASSED
    # WRONG: ExperimentStatus.REJECTED (doesn't exist)
    # WRONG: ExperimentStatus.ACCEPTED (doesn't exist)
""",
}

# Method signatures for common patterns
COMMON_PATTERNS = {
    "file_operations": """
# File operations (CORRECT patterns):
content = module.path.read_text()  # Read file
module.path.write_text(content)    # Write file

# WRONG patterns (don't use):
# module.content  (attribute doesn't exist)
# module.read()   (method doesn't exist)
""",
    "agent_invocation": """
# Agent invocation (CORRECT patterns):
result = await agent.invoke(input)
output = result.output  # If wrapped in ExecutionResult

# WRONG patterns (don't use):
# agent.run(input)       (method doesn't exist)
# agent.execute(input)   (method doesn't exist)
# await runtime.execute(agent, input)  # This IS correct for wrapped execution
""",
    "memory_operations": """
# Memory operations (CORRECT patterns):
rejection = memory.was_rejected(module_name, hypothesis)
accepted = memory.was_recently_accepted(module_name, hypothesis)
record = memory.record(module=..., hypothesis=..., description=..., outcome=...)

# WRONG patterns (don't use):
# memory.is_rejected()     (method doesn't exist)
# memory.check_rejected()  (method doesn't exist)
""",
}


def get_core_api_reference() -> str:
    """
    Get formatted API reference for core kgents APIs.

    Returns formatted string ready to include in prompt.
    """
    sections = []

    sections.append("## CORE API REFERENCE (USE EXACT SIGNATURES)\n")
    sections.append("The following are REAL APIs with their ACTUAL signatures.\n")
    sections.append("DO NOT invent variations or guess parameters.\n\n")

    for api_name, signature in CORE_APIS.items():
        sections.append(f"### {api_name}\n")
        sections.append("```python\n")
        sections.append(signature.strip())
        sections.append("\n```\n\n")

    sections.append("## COMMON PATTERNS\n\n")
    for pattern_name, pattern in COMMON_PATTERNS.items():
        sections.append(f"### {pattern_name}\n")
        sections.append("```python\n")
        sections.append(pattern.strip())
        sections.append("\n```\n\n")

    return "".join(sections)


def extract_class_signature(cls: type) -> str:
    """Extract signature for a class (constructor + key methods)."""
    lines = []

    # Get __init__ signature
    try:
        init_sig = inspect.signature(cls.__init__)
        lines.append(f"def __init__{init_sig}:")
    except (ValueError, TypeError):
        lines.append("def __init__(self, ...):")

    # Get key methods (invoke for Agent subclasses)
    if hasattr(cls, "invoke"):
        try:
            invoke_sig = inspect.signature(cls.invoke)
            lines.append(f"async def invoke{invoke_sig}:")
        except (ValueError, TypeError):
            lines.append("async def invoke(self, input) -> output:")

    return "\n    ".join(lines)


def extract_dataclass_signature(cls: type) -> str:
    """Extract signature for a dataclass."""
    if not hasattr(cls, "__dataclass_fields__"):
        return str(cls)

    lines = ["@dataclass", f"class {cls.__name__}:"]
    for field_name, field in cls.__dataclass_fields__.items():
        field_type = field.type
        if hasattr(field_type, "__name__"):
            type_name = field_type.__name__
        else:
            type_name = str(field_type)

        if field.default is not field.default_factory:
            lines.append(f"    {field_name}: {type_name} = {field.default!r}")
        elif field.default_factory is not inspect._empty:  # type: ignore
            lines.append(f"    {field_name}: {type_name} = field(default_factory=...)")
        else:
            lines.append(f"    {field_name}: {type_name}")

    return "\n".join(lines)


def get_api_signatures(module_names: list[str]) -> dict[str, dict[str, str]]:
    """
    Extract API signatures from specified modules.

    Args:
        module_names: List of module names to extract from

    Returns:
        Dict of module_name -> {symbol_name: signature}
    """
    signatures: dict[str, dict[str, str]] = {}

    for module_name in module_names:
        try:
            module = __import__(module_name, fromlist=[""])
            module_sigs = {}

            for name in dir(module):
                if name.startswith("_"):
                    continue

                obj = getattr(module, name)

                # Extract signature based on type
                if inspect.isclass(obj):
                    if hasattr(obj, "__dataclass_fields__"):
                        module_sigs[name] = extract_dataclass_signature(obj)
                    else:
                        module_sigs[name] = extract_class_signature(obj)
                elif inspect.isfunction(obj):
                    try:
                        sig = inspect.signature(obj)
                        module_sigs[name] = f"def {name}{sig}:"
                    except (ValueError, TypeError):
                        pass

            if module_sigs:
                signatures[module_name] = module_sigs

        except (ImportError, AttributeError):
            pass

    return signatures


# Convenience function for common use case
def get_kgents_api_reference() -> str:
    """
    Get comprehensive API reference for common kgents modules.

    Returns formatted string ready to include in prompts.
    """
    return get_core_api_reference()
