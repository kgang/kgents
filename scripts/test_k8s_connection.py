#!/usr/bin/env python3
"""
Test Kubernetes Connection Script

Quick test script to verify Kubernetes collector connectivity.
Use this to validate your local development setup or production deployment.

Usage:
    # Test with default development config
    python scripts/test_k8s_connection.py

    # Test with specific context
    KUBE_CONTEXT=kind-kgents-triad python scripts/test_k8s_connection.py

    # Test production config
    KGENTS_ENV=production python scripts/test_k8s_connection.py

    # Test mock mode
    GESTALT_USE_MOCK=true python scripts/test_k8s_connection.py

@see plans/_continuations/gestalt-live-real-k8s.md
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Add impl/claude to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "impl" / "claude"))


async def test_connection() -> bool:
    """Test Kubernetes collector connection."""
    from agents.infra.collectors.config import (
        get_collector_config,
        get_environment,
        should_use_mock,
    )
    from agents.infra.collectors.kubernetes import (
        KubernetesCollector,
        MockKubernetesCollector,
    )

    print("=" * 60)
    print("Kubernetes Collector Connection Test")
    print("=" * 60)
    print()

    # Show environment
    env = get_environment()
    use_mock = should_use_mock()
    print(f"Environment: {env}")
    print(f"Use Mock: {use_mock}")
    print()

    # Get config
    config = get_collector_config()
    print("Configuration:")
    print(f"  Namespaces: {config.namespaces}")
    print(f"  Collect Pods: {config.collect_pods}")
    print(f"  Collect Services: {config.collect_services}")
    print(f"  Collect Deployments: {config.collect_deployments}")
    print(f"  Collect Metrics: {config.collect_metrics}")
    if hasattr(config, "kubeconfig") and config.kubeconfig:
        print(f"  Kubeconfig: {config.kubeconfig}")
    if hasattr(config, "context") and config.context:
        print(f"  Context: {config.context}")
    print()

    # Create collector
    if use_mock:
        collector = MockKubernetesCollector()
        print("Using: MockKubernetesCollector")
    else:
        collector = KubernetesCollector(config)
        print("Using: KubernetesCollector")
    print()

    # Connect
    print("Connecting...")
    try:
        await collector.connect()
        print("  Connected!")
    except Exception as e:
        print(f"  Connection FAILED: {e}")
        return False

    # Health check
    print("Health check...")
    try:
        healthy = await collector.health_check()
        print(f"  Healthy: {healthy}")
        if not healthy:
            print("  WARNING: Health check returned false")
            await collector.disconnect()
            return False
    except Exception as e:
        print(f"  Health check FAILED: {e}")
        await collector.disconnect()
        return False

    # Collect topology
    print("Collecting topology...")
    try:
        topology = await collector.collect_topology()
        print(f"  Found {len(topology.entities)} entities:")

        # Count by kind
        by_kind: dict[str, int] = {}
        for entity in topology.entities:
            kind = entity.kind.value
            by_kind[kind] = by_kind.get(kind, 0) + 1

        for kind, count in sorted(by_kind.items()):
            print(f"    - {kind}: {count}")

        # Count by namespace
        print("  By namespace:")
        by_ns: dict[str, int] = {}
        for entity in topology.entities:
            ns = entity.namespace or "(none)"
            by_ns[ns] = by_ns.get(ns, 0) + 1

        for ns, count in sorted(by_ns.items()):
            print(f"    - {ns}: {count}")

        # Health summary
        print("  Health summary:")
        print(f"    - Overall: {topology.overall_health:.1%}")
        print(f"    - Healthy: {topology.healthy_count}")
        print(f"    - Warning: {topology.warning_count}")
        print(f"    - Critical: {topology.critical_count}")

        # Connection count
        print(f"  Connections: {len(topology.connections)}")

    except Exception as e:
        print(f"  Topology collection FAILED: {e}")
        import traceback

        traceback.print_exc()
        await collector.disconnect()
        return False

    # Disconnect
    print("Disconnecting...")
    await collector.disconnect()
    print("  Done!")

    print()
    print("=" * 60)
    print("CONNECTION TEST PASSED")
    print("=" * 60)
    return True


async def test_streaming(duration: float = 5.0) -> None:
    """Test event streaming (optional)."""
    from agents.infra.collectors.config import (
        get_collector_config,
        should_use_mock,
    )
    from agents.infra.collectors.kubernetes import (
        KubernetesCollector,
        MockKubernetesCollector,
    )

    print()
    print("=" * 60)
    print(f"Event Streaming Test ({duration}s)")
    print("=" * 60)
    print()

    config = get_collector_config()
    if should_use_mock():
        collector = MockKubernetesCollector()
    else:
        collector = KubernetesCollector(config)

    await collector.connect()

    print("Streaming events for a few seconds...")
    event_count = 0

    try:
        async for event in collector.stream_events():
            event_count += 1
            print(f"  [{event.severity.value}] {event.reason}: {event.message[:50]}...")

            if event_count >= 5:  # Limit for quick test
                break
    except asyncio.CancelledError:
        pass
    finally:
        await collector.disconnect()

    print(f"Received {event_count} events")


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Test Kubernetes collector connection")
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Also test event streaming",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force mock mode",
    )
    args = parser.parse_args()

    if args.mock:
        os.environ["GESTALT_USE_MOCK"] = "true"

    success = asyncio.run(test_connection())

    if success and args.stream:
        asyncio.run(test_streaming())

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
