"""
.tongue File Parser: Declarative integration specifications.

Phase 3 of Cross-Pollination: Integrations as configuration, not code.

A .tongue file declares:
- Which agents participate (emitter -> receiver)
- What pheromone types they use
- The semantic context (domain, tags)
- Trigger conditions

Example .tongue file:

```tongue
# Psi×F Integration - Metaphor discovery enhances forging
integration psi_forge {
    emitter: psi
    receiver: forge

    pheromone: METAPHOR

    context {
        domain: "software"
        tags: ["problem-solving", "creative"]
    }

    trigger {
        on: "metaphor_discovered"
        condition: "confidence > 0.7"
    }

    decay: 0.1
    radius: 0.5
}
```

See: docs/agent-cross-pollination-final-proposal.md (Phase 3)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TongueParseError(Exception):
    """Error parsing a .tongue file."""

    def __init__(self, message: str, line: int | None = None):
        self.line = line
        super().__init__(f"Line {line}: {message}" if line else message)


class TriggerType(Enum):
    """Types of integration triggers."""

    EVENT = "event"  # On specific event
    SCHEDULE = "schedule"  # Periodic
    THRESHOLD = "threshold"  # When metric exceeds threshold
    PRESENCE = "presence"  # When pheromone present


@dataclass
class TongueContext:
    """Context specification for an integration."""

    domain: str | None = None
    tags: tuple[str, ...] = ()
    embedding_dim: int | None = None


@dataclass
class TongueTrigger:
    """Trigger specification for an integration."""

    trigger_type: TriggerType = TriggerType.EVENT
    on: str = ""  # Event name
    condition: str = ""  # Optional condition expression

    # For schedule triggers
    interval_ticks: int | None = None

    # For threshold triggers
    metric: str | None = None
    threshold: float | None = None


@dataclass
class TongueIntegration:
    """
    A parsed integration specification.

    Describes how two agents coordinate via the stigmergic field.
    """

    name: str
    emitter: str
    receiver: str

    pheromone: str

    context: TongueContext = field(default_factory=TongueContext)
    trigger: TongueTrigger = field(default_factory=TongueTrigger)

    # Pheromone parameters
    decay: float = 0.1
    radius: float = 0.5
    intensity: float = 1.0

    # Metadata
    description: str = ""
    source_file: str | None = None


@dataclass
class TongueDocument:
    """
    A complete .tongue document.

    Can contain multiple integrations.
    """

    integrations: list[TongueIntegration] = field(default_factory=list)
    version: str = "1.0"
    metadata: dict[str, Any] = field(default_factory=dict)
    source: str | None = None


class TongueParser:
    """
    Parser for .tongue files.

    Grammar (simplified):

    document := integration*
    integration := "integration" name "{" body "}"
    body := (property | block)*
    property := key ":" value
    block := key "{" body "}"
    """

    def __init__(self) -> None:
        self._lines: list[str] = []
        self._current_line = 0
        self._current_char = 0

    def parse(self, content: str, source: str | None = None) -> TongueDocument:
        """
        Parse a .tongue file.

        Args:
            content: The file content
            source: Optional source file path

        Returns:
            Parsed TongueDocument

        Raises:
            TongueParseError: If parsing fails
        """
        self._lines = content.split("\n")
        self._current_line = 0

        document = TongueDocument(source=source)

        while self._current_line < len(self._lines):
            line = self._current_stripped_line()

            if not line or line.startswith("#"):
                self._current_line += 1
                continue

            if line.startswith("integration"):
                integration = self._parse_integration()
                integration.source_file = source
                document.integrations.append(integration)
            elif line.startswith("version"):
                document.version = self._parse_property_value(line, "version")
            else:
                raise TongueParseError(
                    f"Unexpected token: {line.split()[0] if line.split() else 'empty'}",
                    self._current_line + 1,
                )

            self._current_line += 1

        return document

    def _current_stripped_line(self) -> str:
        """Get current line, stripped of whitespace."""
        if self._current_line >= len(self._lines):
            return ""
        return self._lines[self._current_line].strip()

    def _parse_integration(self) -> TongueIntegration:
        """Parse an integration block."""
        line = self._current_stripped_line()

        # Extract name: "integration name {" or "integration name"
        match = re.match(r"integration\s+(\w+)\s*\{?", line)
        if not match:
            raise TongueParseError(
                "Invalid integration declaration", self._current_line + 1
            )

        name = match.group(1)
        integration = TongueIntegration(
            name=name, emitter="", receiver="", pheromone=""
        )

        # If no opening brace on this line, expect it on next
        if "{" not in line:
            self._current_line += 1
            if self._current_stripped_line() != "{":
                raise TongueParseError("Expected '{'", self._current_line + 1)

        self._current_line += 1

        # Parse body until closing brace
        while self._current_line < len(self._lines):
            line = self._current_stripped_line()

            if not line or line.startswith("#"):
                self._current_line += 1
                continue

            if line == "}":
                break

            if line.startswith("context"):
                integration.context = self._parse_context_block()
            elif line.startswith("trigger"):
                integration.trigger = self._parse_trigger_block()
            else:
                # Simple property
                key, value = self._parse_property(line)
                self._set_integration_property(integration, key, value)

            self._current_line += 1

        return integration

    def _parse_property(self, line: str) -> tuple[str, str]:
        """Parse a key: value property."""
        if ":" not in line:
            raise TongueParseError(
                f"Invalid property (missing ':'): {line}", self._current_line + 1
            )

        parts = line.split(":", 1)
        key = parts[0].strip()
        value = parts[1].strip().strip('"').strip("'")

        return key, value

    def _parse_property_value(self, line: str, key: str) -> str:
        """Parse the value of a specific property."""
        if ":" not in line:
            raise TongueParseError(f"Invalid {key} declaration", self._current_line + 1)

        return line.split(":", 1)[1].strip().strip('"').strip("'")

    def _parse_context_block(self) -> TongueContext:
        """Parse a context block."""
        context = TongueContext()

        # Skip to opening brace
        line = self._current_stripped_line()
        if "{" not in line:
            self._current_line += 1
            if self._current_stripped_line() != "{":
                raise TongueParseError(
                    "Expected '{' after context", self._current_line + 1
                )

        self._current_line += 1

        while self._current_line < len(self._lines):
            line = self._current_stripped_line()

            if not line or line.startswith("#"):
                self._current_line += 1
                continue

            if line == "}":
                break

            key, value = self._parse_property(line)

            if key == "domain":
                context.domain = value
            elif key == "tags":
                context.tags = self._parse_list(value)
            elif key == "embedding_dim":
                context.embedding_dim = int(value)

            self._current_line += 1

        return context

    def _parse_trigger_block(self) -> TongueTrigger:
        """Parse a trigger block."""
        trigger = TongueTrigger()

        # Skip to opening brace
        line = self._current_stripped_line()
        if "{" not in line:
            self._current_line += 1
            if self._current_stripped_line() != "{":
                raise TongueParseError(
                    "Expected '{' after trigger", self._current_line + 1
                )

        self._current_line += 1

        while self._current_line < len(self._lines):
            line = self._current_stripped_line()

            if not line or line.startswith("#"):
                self._current_line += 1
                continue

            if line == "}":
                break

            key, value = self._parse_property(line)

            if key == "type":
                trigger.trigger_type = TriggerType(value)
            elif key == "on":
                trigger.on = value
            elif key == "condition":
                trigger.condition = value
            elif key == "interval":
                trigger.interval_ticks = int(value)
            elif key == "metric":
                trigger.metric = value
            elif key == "threshold":
                trigger.threshold = float(value)

            self._current_line += 1

        return trigger

    def _parse_list(self, value: str) -> tuple[str, ...]:
        """Parse a list value like ["a", "b", "c"]."""
        value = value.strip()
        if not (value.startswith("[") and value.endswith("]")):
            return (value,)

        inner = value[1:-1]
        items = [item.strip().strip('"').strip("'") for item in inner.split(",")]
        return tuple(item for item in items if item)

    def _set_integration_property(
        self,
        integration: TongueIntegration,
        key: str,
        value: str,
    ) -> None:
        """Set a property on an integration."""
        if key == "emitter":
            integration.emitter = value
        elif key == "receiver":
            integration.receiver = value
        elif key == "pheromone":
            integration.pheromone = value
        elif key == "decay":
            integration.decay = float(value)
        elif key == "radius":
            integration.radius = float(value)
        elif key == "intensity":
            integration.intensity = float(value)
        elif key == "description":
            integration.description = value


# =============================================================================
# Validation
# =============================================================================


@dataclass
class ValidationError:
    """A validation error."""

    message: str
    integration: str | None = None
    field: str | None = None


def validate_document(document: TongueDocument) -> list[ValidationError]:
    """
    Validate a parsed .tongue document.

    Returns list of validation errors (empty if valid).
    """
    errors: list[ValidationError] = []

    for integration in document.integrations:
        # Required fields
        if not integration.name:
            errors.append(
                ValidationError(
                    message="Integration missing name",
                )
            )
            continue

        if not integration.emitter:
            errors.append(
                ValidationError(
                    message="Missing emitter",
                    integration=integration.name,
                    field="emitter",
                )
            )

        if not integration.receiver:
            errors.append(
                ValidationError(
                    message="Missing receiver",
                    integration=integration.name,
                    field="receiver",
                )
            )

        if not integration.pheromone:
            errors.append(
                ValidationError(
                    message="Missing pheromone type",
                    integration=integration.name,
                    field="pheromone",
                )
            )

        # Range validations
        if not 0.0 <= integration.decay <= 1.0:
            errors.append(
                ValidationError(
                    message=f"Decay must be 0.0-1.0, got {integration.decay}",
                    integration=integration.name,
                    field="decay",
                )
            )

        if integration.radius <= 0:
            errors.append(
                ValidationError(
                    message=f"Radius must be positive, got {integration.radius}",
                    integration=integration.name,
                    field="radius",
                )
            )

        if integration.intensity <= 0:
            errors.append(
                ValidationError(
                    message=f"Intensity must be positive, got {integration.intensity}",
                    integration=integration.name,
                    field="intensity",
                )
            )

    return errors


# =============================================================================
# Code Generation
# =============================================================================


def generate_integration_code(integration: TongueIntegration) -> str:
    """
    Generate Python code for an integration.

    This creates the boilerplate for setting up emitter and receiver.
    """
    code = f'''
# Generated from {integration.source_file or "tongue spec"}
# Integration: {integration.name}
# {integration.emitter} -> {integration.receiver} via {integration.pheromone}

from agents.i.semantic_field import (
    SemanticField,
    SemanticPheromoneKind,
    FieldCoordinate,
)

def setup_{integration.name}(field: SemanticField):
    """Set up {integration.name} integration."""

    # Emitter: {integration.emitter}
    def emit_{integration.pheromone.lower()}(payload, position=None):
        """Emit a {integration.pheromone} pheromone."""
        if position is None:
            position = FieldCoordinate(
                domain="{integration.context.domain or "default"}",
                tags={integration.context.tags!r},
            )

        return field.emit(
            emitter="{integration.emitter}",
            kind=SemanticPheromoneKind.{integration.pheromone},
            payload=payload,
            position=position,
            intensity={integration.intensity},
        )

    # Receiver: {integration.receiver}
    def sense_{integration.pheromone.lower()}(position=None):
        """Sense {integration.pheromone} pheromones."""
        if position is None:
            position = FieldCoordinate(
                domain="{integration.context.domain or "default"}",
                tags={integration.context.tags!r},
            )

        return field.sense(
            position=position,
            radius={integration.radius},
            kind=SemanticPheromoneKind.{integration.pheromone},
        )

    return emit_{integration.pheromone.lower()}, sense_{integration.pheromone.lower()}
'''
    return code


# =============================================================================
# Factory Functions
# =============================================================================


def create_parser() -> TongueParser:
    """Create a .tongue parser."""
    return TongueParser()


def parse_tongue(content: str, source: str | None = None) -> TongueDocument:
    """Parse a .tongue file."""
    parser = create_parser()
    return parser.parse(content, source)


def load_tongue_file(path: str) -> TongueDocument:
    """Load and parse a .tongue file."""
    with open(path) as f:
        content = f.read()
    return parse_tongue(content, source=path)
