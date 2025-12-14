"""
Streaming infrastructure for kgents SaaS.

Provides NATS JetStream integration for real-time event streaming.
"""

from protocols.streaming.nats_bridge import (
    NATSBridge,
    NATSBridgeConfig,
    NATSConnectionError,
)

__all__ = [
    "NATSBridge",
    "NATSBridgeConfig",
    "NATSConnectionError",
]
