"""
Terrarium configuration.

Server and protocol settings for the web gateway.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TerrariumConfig:
    """
    Configuration for the Terrarium web gateway.

    Attributes:
        host: Server bind address
        port: Server port
        mirror_history_size: Events kept in HolographicBuffer history
        mirror_broadcast_timeout: Timeout for broadcasting to slow observers
        perturb_auth_required: Whether /perturb endpoint requires auth
        perturb_rate_limit: Max perturbations per second per client
        observer_max_lag: Max lag (events) before disconnecting slow observer
    """

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080

    # Mirror Protocol settings
    mirror_history_size: int = 100
    mirror_broadcast_timeout: float = 0.1  # Fire-and-forget, short timeout

    # Perturb endpoint settings
    perturb_auth_required: bool = True
    perturb_rate_limit: float = 10.0  # Max 10 perturbations/second

    # Observer settings
    observer_max_lag: int = 1000  # Disconnect if >1000 events behind

    # Agent registry settings
    agent_timeout: float = 30.0  # Timeout for agent operations

    # Metadata
    title: str = "kgents Terrarium"
    version: str = "0.1.0"

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.mirror_history_size < 1:
            raise ValueError("mirror_history_size must be >= 1")
        if self.perturb_rate_limit <= 0:
            raise ValueError("perturb_rate_limit must be > 0")
        if self.observer_max_lag < 1:
            raise ValueError("observer_max_lag must be >= 1")
