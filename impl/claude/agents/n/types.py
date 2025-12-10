"""
N-gent Core Types: SemanticTrace and related data structures.

The Crystal is the fundamental unit of N-gent recording - pure data, no prose.

Philosophy:
    The event is the stone. The story is the shadow.
    Collect stones. Cast shadows only when the sun is out.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Determinism(Enum):
    """
    Classification of trace reproducibility.

    Critical for the Echo Chamber to know what can be replayed exactly.
    """

    DETERMINISTIC = "deterministic"  # Math, lookups: exact replay possible
    PROBABILISTIC = "probabilistic"  # LLM calls: similar but not identical
    CHAOTIC = "chaotic"  # External APIs: no replay guarantee


@dataclass(frozen=True)
class SemanticTrace:
    """
    The Crystal. Pure, compressed reality. No prose.

    This is the fundamental unit of N-gent recording.
    NOT narrative, NOT prose - just semantic atoms that can be
    projected into any story at read-time.

    Design decisions:
    - frozen=True: Crystals are immutable once created
    - No "content" or "thought_type" strings: pure data
    - Binary serialization via input_snapshot, not JSON prose
    - Optional vector for L-gent semantic retrieval
    """

    # Identity
    trace_id: str
    parent_id: str | None  # For nested calls
    timestamp: datetime

    # The Agent
    agent_id: str
    agent_genus: str  # "B", "G", "J", etc.

    # The Action (semantic atom, not narrative)
    action: str  # "INVOKE", "GENERATE", "DECIDE", "LOOKUP", etc.

    # The Data (structured, not prose)
    inputs: dict[str, Any]
    outputs: dict[str, Any] | None

    # Reproducibility
    input_hash: str  # For deduplication
    input_snapshot: bytes  # Serialized for echo replay
    output_hash: str | None

    # Economics (B-gent integration)
    gas_consumed: int  # Tokens used
    duration_ms: int

    # Embedding (L-gent integration)
    vector: tuple[float, ...] | None = None  # Immutable sequence for frozen dataclass

    # Classification
    determinism: Determinism = Determinism.PROBABILISTIC
    metadata: dict[str, Any] = field(default_factory=dict)

    def with_vector(self, vector: list[float]) -> SemanticTrace:
        """Create a new trace with the given vector (for L-gent indexing)."""
        return SemanticTrace(
            trace_id=self.trace_id,
            parent_id=self.parent_id,
            timestamp=self.timestamp,
            agent_id=self.agent_id,
            agent_genus=self.agent_genus,
            action=self.action,
            inputs=self.inputs,
            outputs=self.outputs,
            input_hash=self.input_hash,
            input_snapshot=self.input_snapshot,
            output_hash=self.output_hash,
            gas_consumed=self.gas_consumed,
            duration_ms=self.duration_ms,
            vector=tuple(vector),
            determinism=self.determinism,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "agent_genus": self.agent_genus,
            "action": self.action,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "gas_consumed": self.gas_consumed,
            "duration_ms": self.duration_ms,
            "vector": list(self.vector) if self.vector else None,
            "determinism": self.determinism.value,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], input_snapshot: bytes = b""
    ) -> SemanticTrace:
        """Create from dictionary."""
        vector = data.get("vector")
        return cls(
            trace_id=data["trace_id"],
            parent_id=data.get("parent_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            agent_id=data["agent_id"],
            agent_genus=data["agent_genus"],
            action=data["action"],
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs"),
            input_hash=data["input_hash"],
            input_snapshot=input_snapshot,
            output_hash=data.get("output_hash"),
            gas_consumed=data.get("gas_consumed", 0),
            duration_ms=data.get("duration_ms", 0),
            vector=tuple(vector) if vector else None,
            determinism=Determinism(data.get("determinism", "probabilistic")),
            metadata=data.get("metadata", {}),
        )


@dataclass
class TraceContext:
    """
    Context for an in-progress trace.

    Created by Historian.begin_trace(), completed by end_trace().
    """

    trace_id: str
    parent_id: str | None
    agent_id: str
    agent_genus: str
    input_snapshot: bytes
    input_hash: str
    start_time: datetime


class Action:
    """
    Standard action vocabulary.

    Actions are semantic atoms, not narrative prose.
    These are conventions, not requirements.
    """

    # Core actions
    INVOKE = "INVOKE"  # Agent invocation
    COMPOSE = "COMPOSE"  # Agent composition
    DECIDE = "DECIDE"  # Decision point
    LOOKUP = "LOOKUP"  # Data retrieval
    TRANSFORM = "TRANSFORM"  # Data transformation
    GENERATE = "GENERATE"  # LLM generation
    PARSE = "PARSE"  # Parsing operation
    VALIDATE = "VALIDATE"  # Validation check
    ERROR = "ERROR"  # Error occurrence

    # External
    CALL_API = "CALL_API"  # External API call
    CALL_TOOL = "CALL_TOOL"  # Tool invocation

    # Memory operations
    REMEMBER = "REMEMBER"  # Store to memory
    RECALL = "RECALL"  # Retrieve from memory
    FORGET = "FORGET"  # Remove from memory

    @classmethod
    def classify_determinism(cls, action: str) -> Determinism:
        """Classify the determinism of an action."""
        deterministic = {
            cls.COMPOSE,
            cls.LOOKUP,
            cls.TRANSFORM,
            cls.PARSE,
            cls.VALIDATE,
            cls.RECALL,
        }
        chaotic = {
            cls.CALL_API,
            cls.CALL_TOOL,
            cls.ERROR,
        }

        if action in deterministic:
            return Determinism.DETERMINISTIC
        if action in chaotic:
            return Determinism.CHAOTIC
        return Determinism.PROBABILISTIC
