"""
Prompt and Invocation schemas - L3 and L5 of the Zero Seed holarchy.

Prompts are witnessed derivations from values/specs.
Invocations are runtime executions of prompts with Galois loss tracking.

L3 (Prompt): HAS proof field - derived artifact
L5 (Invocation): HAS proof field - runtime trace

AGENTESE paths:
- concept.prompt.*
- concept.invocation.*

Spec: spec/protocols/zero-seed.md
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any

from .proof import GaloisWitnessedProof
from ..universe import DataclassSchema

__all__ = [
    # Contracts
    "PromptParam",
    "PromptCrystal",
    "InvocationCrystal",
    # Schemas
    "PROMPT_SCHEMA",
    "INVOCATION_SCHEMA",
]


# =============================================================================
# Prompt Parameter Definition
# =============================================================================


@dataclass(frozen=True)
class PromptParam:
    """
    Parameter definition for a prompt template.

    Defines the shape and constraints of a parameter that can be
    passed to a prompt at invocation time.

    Attributes:
        name: Parameter name (e.g., "task", "context", "constraints")
        type: Python type hint as string (e.g., "str", "list[str]", "int")
        constraints: Validation constraints (min/max, regex, enum, etc.)
        default: Default value if not provided (None = required)
        examples: Example values for documentation/testing
    """

    name: str
    """Parameter name."""

    type: str
    """Type annotation as string (e.g., 'str', 'list[str]')."""

    constraints: dict[str, Any] = field(default_factory=dict)
    """Validation constraints (min, max, regex, enum, etc.)."""

    default: Any | None = None
    """Default value (None means required parameter)."""

    examples: tuple[str, ...] = field(default_factory=tuple)
    """Example values for documentation and testing."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "name": self.name,
            "type": self.type,
            "constraints": self.constraints,
            "default": self.default,
            "examples": list(self.examples),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptParam":
        """Deserialize from dict."""
        return cls(
            name=data["name"],
            type=data["type"],
            constraints=data.get("constraints", {}),
            default=data.get("default"),
            examples=tuple(data.get("examples", [])),
        )


# =============================================================================
# L3: Prompt Crystal (Derived Prompts)
# =============================================================================


@dataclass(frozen=True)
class PromptCrystal:
    """
    L3: Prompt template derived from values/specs with witnessed proof.

    Prompts are the bridge between specification and execution. They:
    - HAVE proof field (derived artifact, not axiomatic)
    - Template with typed parameters
    - Trace derivation from values/specs
    - Are versioned for evolution tracking
    - Carry goal statements for intent preservation

    Example:
        template: "Given {context}, perform {task} following {constraints}"
        parameters: {"context": PromptParam(...), "task": ..., "constraints": ...}
        goal_statement: "Generate tasteful code that honors principles"
        derived_from: ["value:tasteful", "spec:code-generation"]

    Attributes:
        template: Prompt template with {param} placeholders
        parameters: Parameter definitions keyed by name
        goal_statement: What this prompt aims to achieve
        derived_from: IDs of values/specs this prompt derives from
        version: Monotonic version number for evolution
        created_by: Creator identifier (user, agent, system)
        proof: GaloisWitnessedProof of derivation
    """

    template: str
    """Prompt template with {param} placeholders."""

    parameters: dict[str, PromptParam]
    """Parameter definitions keyed by parameter name."""

    goal_statement: str
    """What this prompt aims to achieve (intent preservation)."""

    derived_from: tuple[str, ...]
    """IDs of values/specs/prompts this derives from (lineage)."""

    version: int
    """Monotonic version number (1, 2, 3...)."""

    created_by: str
    """Creator identifier (user ID, agent name, 'system')."""

    proof: GaloisWitnessedProof
    """Galois-witnessed proof of derivation from values/specs."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "template": self.template,
            "parameters": {k: v.to_dict() for k, v in self.parameters.items()},
            "goal_statement": self.goal_statement,
            "derived_from": list(self.derived_from),
            "version": self.version,
            "created_by": self.created_by,
            "proof": self.proof.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptCrystal":
        """Deserialize from dict."""
        return cls(
            template=data["template"],
            parameters={
                k: PromptParam.from_dict(v)
                for k, v in data["parameters"].items()
            },
            goal_statement=data["goal_statement"],
            derived_from=tuple(data["derived_from"]),
            version=data["version"],
            created_by=data["created_by"],
            proof=GaloisWitnessedProof.from_dict(data["proof"]),
        )


PROMPT_SCHEMA = DataclassSchema(
    name="concept.prompt",
    type_cls=PromptCrystal,
)
"""
Schema for concept.prompt v1.

L3 derived schema. Prompts HAVE proof field - they are witnessed
derivations from values and specifications.

AGENTESE path: concept.prompt.*
"""


# =============================================================================
# L5: Invocation Crystal (Runtime Execution)
# =============================================================================


@dataclass(frozen=True)
class InvocationCrystal:
    """
    L5: Invocation record - runtime execution of a prompt with loss tracking.

    Invocations capture the full execution trace:
    - HAVE proof field (runtime artifact)
    - Link to prompt template via prompt_id
    - Concrete parameter values
    - Success/failure status
    - Performance metrics (duration, tokens)
    - Galois loss for input coherence and output quality
    - Output artifact ID if generated

    This enables:
    - Audit trail for all LLM calls
    - Performance analysis
    - Galois loss tracking over time
    - Prompt effectiveness measurement

    Attributes:
        prompt_id: ID of the PromptCrystal being invoked
        parameters: Concrete parameter values for this invocation
        timestamp: When the invocation occurred
        executor: Who/what executed this (user, agent, system)
        output_id: ID of generated output artifact (if any)
        success: Whether invocation succeeded
        duration_ms: Execution time in milliseconds
        token_count: Total tokens (input + output)
        galois_loss_input: L(input) - coherence of input parameters
        galois_loss_output: L(output) - quality of generated output
        proof: GaloisWitnessedProof of execution
    """

    prompt_id: str
    """ID of the PromptCrystal being invoked."""

    parameters: dict[str, Any]
    """Concrete parameter values for this invocation."""

    timestamp: datetime
    """When the invocation occurred (UTC)."""

    executor: str
    """Who/what executed this (user ID, agent name, 'system')."""

    output_id: str | None
    """ID of generated output artifact (spec, code, etc.)."""

    success: bool
    """Whether invocation completed successfully."""

    duration_ms: int
    """Execution time in milliseconds."""

    token_count: int
    """Total tokens consumed (input + output)."""

    galois_loss_input: float
    """L(input) - coherence of input parameters with prompt."""

    galois_loss_output: float
    """L(output) - quality/coherence of generated output."""

    proof: GaloisWitnessedProof
    """Galois-witnessed proof of execution."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "prompt_id": self.prompt_id,
            "parameters": self.parameters,
            "timestamp": self.timestamp.isoformat(),
            "executor": self.executor,
            "output_id": self.output_id,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "token_count": self.token_count,
            "galois_loss_input": self.galois_loss_input,
            "galois_loss_output": self.galois_loss_output,
            "proof": self.proof.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InvocationCrystal":
        """Deserialize from dict."""
        return cls(
            prompt_id=data["prompt_id"],
            parameters=data["parameters"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            executor=data["executor"],
            output_id=data.get("output_id"),
            success=data["success"],
            duration_ms=data["duration_ms"],
            token_count=data["token_count"],
            galois_loss_input=data["galois_loss_input"],
            galois_loss_output=data["galois_loss_output"],
            proof=GaloisWitnessedProof.from_dict(data["proof"]),
        )


INVOCATION_SCHEMA = DataclassSchema(
    name="concept.invocation",
    type_cls=InvocationCrystal,
)
"""
Schema for concept.invocation v1.

L5 runtime schema. Invocations HAVE proof field - they are witnessed
execution traces with Galois loss quantification.

AGENTESE path: concept.invocation.*
"""
