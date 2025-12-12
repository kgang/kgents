"""
The Accursed Share: Exploratory and chaos testing.

Philosophy: We cherish and express gratitude for slop.
10% of test budget goes to unpredictable exploration.

Phase 5 of test evolution plan:
- Chaotic composition tests
- Boundary exploration
- Discovery feedback loop
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# =============================================================================
# Discovery Types
# =============================================================================


@dataclass
class Discovery:
    """
    A serendipitous discovery from chaos testing.

    Discoveries are unexpected behaviors, successful compositions,
    or boundary cases worth documenting.
    """

    test_name: str
    discovery_type: str  # "composition_success", "boundary_case", "unexpected_behavior"
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    actionable: bool = False
    fed_back_to_spec: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "test_name": self.test_name,
            "discovery_type": self.discovery_type,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "input_data": str(self.input_data) if self.input_data else None,
            "output_data": str(self.output_data) if self.output_data else None,
            "actionable": self.actionable,
            "fed_back_to_spec": self.fed_back_to_spec,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Discovery":
        """Deserialize from dictionary."""
        return cls(
            test_name=data["test_name"],
            discovery_type=data["discovery_type"],
            description=data["description"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            input_data=data.get("input_data"),
            output_data=data.get("output_data"),
            actionable=data.get("actionable", False),
            fed_back_to_spec=data.get("fed_back_to_spec", False),
        )


class DiscoveryLog:
    """
    Persistent log of discoveries from chaos testing.

    Philosophy: Failed experiments are offerings, not waste.
    """

    def __init__(self, log_path: Path = Path(".discoveries.json")):
        self.log_path = log_path
        self.discoveries: list[Discovery] = []
        self._load()

    def _load(self) -> None:
        """Load discoveries from file."""
        if self.log_path.exists():
            try:
                data = json.loads(self.log_path.read_text())
                self.discoveries = [Discovery.from_dict(d) for d in data]
            except (json.JSONDecodeError, KeyError):
                # Corrupted file, start fresh
                self.discoveries = []

    def _save(self) -> None:
        """Save discoveries to file."""
        data = [d.to_dict() for d in self.discoveries]
        self.log_path.write_text(json.dumps(data, indent=2))

    def record(self, discovery: Discovery) -> None:
        """Record a new discovery."""
        self.discoveries.append(discovery)
        self._save()

    def record_composition_success(
        self,
        test_name: str,
        agents: list[str],
        input_val: Any,
        output_val: Any,
    ) -> Discovery:
        """Record a successful composition discovery."""
        discovery = Discovery(
            test_name=test_name,
            discovery_type="composition_success",
            description=f"Successful composition: {' >> '.join(agents)}",
            input_data=input_val,
            output_data=output_val,
        )
        self.record(discovery)
        return discovery

    def record_boundary_case(
        self,
        test_name: str,
        description: str,
        input_val: Any,
        behavior: str,
    ) -> Discovery:
        """Record a boundary case discovery."""
        discovery = Discovery(
            test_name=test_name,
            discovery_type="boundary_case",
            description=f"{description}: {behavior}",
            input_data=input_val,
            actionable=True,  # Boundary cases often actionable
        )
        self.record(discovery)
        return discovery

    def record_unexpected_behavior(
        self,
        test_name: str,
        description: str,
        expected: Any,
        actual: Any,
    ) -> Discovery:
        """Record an unexpected behavior discovery."""
        discovery = Discovery(
            test_name=test_name,
            discovery_type="unexpected_behavior",
            description=description,
            input_data=expected,
            output_data=actual,
            actionable=True,
        )
        self.record(discovery)
        return discovery

    def get_actionable(self) -> list[Discovery]:
        """Get discoveries that should feed back to spec."""
        return [d for d in self.discoveries if d.actionable and not d.fed_back_to_spec]

    def mark_fed_back(self, discovery: Discovery) -> None:
        """Mark a discovery as fed back to spec."""
        discovery.fed_back_to_spec = True
        self._save()

    def get_by_type(self, discovery_type: str) -> list[Discovery]:
        """Get discoveries by type."""
        return [d for d in self.discoveries if d.discovery_type == discovery_type]

    def summary(self) -> dict[str, Any]:
        """Get summary statistics."""
        by_type: dict[str, int] = {}
        for d in self.discoveries:
            by_type[d.discovery_type] = by_type.get(d.discovery_type, 0) + 1
        return {
            "total": len(self.discoveries),
            "actionable": len(self.get_actionable()),
            "by_type": by_type,
        }


# =============================================================================
# Chaos Test Utilities
# =============================================================================


def generate_weird_inputs() -> list[Any]:
    """
    Generate weird inputs for boundary testing.

    These inputs are designed to stress test agents
    and discover unexpected behaviors.
    """
    return [
        # Empty values
        "",
        [],
        {},
        None,
        # Large values
        "a" * 10000,
        list(range(10000)),
        {f"key_{i}": i for i in range(1000)},
        # Boundary numbers
        0,
        -1,
        1,
        2**31 - 1,  # Max int32
        2**31,  # Overflow int32
        2**63 - 1,  # Max int64
        float("inf"),
        float("-inf"),
        # Special strings
        "\x00\x01\x02",  # Null bytes
        "🎭" * 100,  # Unicode
        '{"key": "value"}',  # JSON in string
        "<script>alert('xss')</script>",  # XSS attempt
        "'; DROP TABLE users; --",  # SQL injection
        # Recursive structures (careful with these)
        {"self": None},  # Can be made circular
    ]


async def chaos_compose(agents: list[Any], input_val: Any, log: DiscoveryLog) -> Any:
    """
    Attempt to compose and invoke agents, logging discoveries.

    Args:
        agents: List of agents to compose
        input_val: Input value for the chain
        log: Discovery log for recording results

    Returns:
        Result of composition, or None if failed
    """
    from functools import reduce

    try:
        from bootstrap import compose

        composed = reduce(compose, agents)
        result = await composed.invoke(input_val)

        # Log success
        agent_names = [getattr(a, "name", type(a).__name__) for a in agents]
        log.record_composition_success(
            test_name="chaos_compose",
            agents=agent_names,
            input_val=input_val,
            output_val=result,
        )

        return result

    except Exception as e:
        # Log failure as potential discovery
        agent_names = [getattr(a, "name", type(a).__name__) for a in agents]
        log.record_unexpected_behavior(
            test_name="chaos_compose",
            description=f"Composition failed: {' >> '.join(agent_names)}",
            expected="successful composition",
            actual=str(e),
        )
        return None
