"""
E2E Tests: Full AGENTESE Flow from HTTP to Response.

This test exercises the complete AGENTESE stack:
    HTTP Request → Gateway → Node Resolution → Aspect Invocation → Response

These are **tier2 integration tests** that verify:
1. Gateway routes requests correctly
2. Nodes resolve with DI container
3. Aspects return valid responses

**DI Bootstrap Behavior**:
Tests dynamically skip if the DI container doesn't have services bootstrapped.
This is expected in CI without full infrastructure. When running locally with
`uv run uvicorn ...`, these tests will pass.

AD-011 (REPL Reliability): Every path in discover MUST be invokable.
AD-016 (Fail-Fast): Unregistered paths return 404, not JIT fallback.

Run with:
    cd impl/claude
    uv run pytest protocols/agentese/_tests/test_e2e_agentese_flow.py -v
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, AsyncIterator

import pytest
import pytest_asyncio

if TYPE_CHECKING:
    from httpx import AsyncClient


# Fixtures


@pytest.fixture(scope="function")
def anyio_backend():
    """Use asyncio backend for httpx."""
    return "asyncio"


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncIterator["AsyncClient"]:
    """
    Create async HTTP client with test app.

    Uses the actual application factory for true E2E testing.
    Note: function scope required for pytest-asyncio 1.x compatibility.

    IMPORTANT: ASGITransport does NOT trigger FastAPI lifespan events.
    We must manually call setup_providers() to register DI dependencies
    before the app handles requests.
    """
    from httpx import ASGITransport, AsyncClient

    from protocols.api.app import create_app

    # CRITICAL: ASGITransport doesn't trigger lifespan events.
    # We must manually bootstrap service providers to register with the DI container.
    try:
        from services.providers import setup_providers

        await setup_providers()

        # Create database tables (production uses Alembic migrations instead)
        from models.base import Base
        from services.bootstrap import get_registry

        registry = get_registry()
        session_factory = registry.session_factory
        engine = session_factory.kw.get("bind")
        if engine is not None:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(f"setup_providers/init_db failed: {e}")

    app = create_app()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# E2E Tests: Active Crown Jewels
#
# Post-extinction (2025-12-21): Only Brain, Witness, Atelier, Liminal remain.
# Town, Park, Forge, Gestalt, etc. were archived.


@pytest.mark.integration
class TestBrainE2E:
    """End-to-end tests for Brain (self.memory)."""

    @pytest.mark.anyio
    async def test_brain_manifest_e2e(self, client: "AsyncClient"):
        """Brain manifest returns valid response (or DI error if not bootstrapped)."""
        response = await client.get("/agentese/self/memory/manifest")

        if response.status_code == 500:
            error_text = response.text
            if "persistence" in error_text or "missing" in error_text:
                pytest.skip("Service not bootstrapped (DI dependency missing)")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"


@pytest.mark.integration
class TestGraphE2E:
    """End-to-end tests for WitnessedGraph (concept.graph)."""

    @pytest.mark.anyio
    async def test_graph_manifest_e2e(self, client: "AsyncClient"):
        """Graph manifest returns valid response."""
        response = await client.get("/agentese/concept/graph/manifest")

        if response.status_code == 500:
            error_text = response.text
            if "persistence" in error_text or "missing" in error_text:
                pytest.skip("Service not bootstrapped (DI dependency missing)")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"


# E2E Tests: Discovery


@pytest.mark.integration
class TestDiscoveryE2E:
    """End-to-end tests for AGENTESE discovery."""

    @pytest.mark.anyio
    async def test_discover_returns_paths(self, client: "AsyncClient"):
        """Discovery endpoint returns registered paths."""
        response = await client.get("/agentese/discover")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "paths" in data or isinstance(data, list), f"Expected paths in response: {data}"

        paths = data.get("paths", data) if isinstance(data, dict) else data
        assert len(paths) >= 20, f"Expected at least 20 paths, got {len(paths)}"

    @pytest.mark.anyio
    async def test_discover_includes_active_jewels(self, client: "AsyncClient"):
        """Discovery includes active Crown Jewel paths."""
        response = await client.get("/agentese/discover")

        assert response.status_code == 200

        data = response.json()
        paths = data.get("paths", []) if isinstance(data, dict) else data

        if paths and isinstance(paths[0], dict):
            path_strings = [p.get("path", "") for p in paths]
        else:
            path_strings = paths

        # Active Crown Jewels post-extinction
        expected = ["self.memory", "concept.graph"]

        for expected_path in expected:
            assert any(expected_path in p for p in path_strings), (
                f"'{expected_path}' not in discovery. Found: {path_strings[:10]}"
            )


# Performance Baseline Tests


# Performance baselines in seconds
# Post-extinction: Only test active, registered paths
PERFORMANCE_BASELINES = {
    "/agentese/self/memory/manifest": 1.0,
    "/agentese/concept/graph/manifest": 1.0,
    "/agentese/discover": 0.5,
}


@pytest.mark.integration
class TestPerformanceBaselines:
    """
    Performance baseline tests.

    These tests ensure endpoints respond within acceptable time limits.
    AD-011: Performance is part of reliability.
    """

    @pytest.mark.anyio
    @pytest.mark.parametrize("path,max_seconds", list(PERFORMANCE_BASELINES.items()))
    async def test_performance_baseline(self, client: "AsyncClient", path: str, max_seconds: float):
        """Endpoint responds within baseline time."""
        start = time.time()
        response = await client.get(path)
        elapsed = time.time() - start

        if response.status_code in [200, 404, 500]:
            assert elapsed < max_seconds, (
                f"{path} took {elapsed:.3f}s, exceeds {max_seconds}s baseline"
            )

    @pytest.mark.anyio
    async def test_discovery_is_fast(self, client: "AsyncClient"):
        """Discovery endpoint is particularly fast (<300ms)."""
        start = time.time()
        response = await client.get("/agentese/discover")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.3, f"Discovery took {elapsed:.3f}s, should be <0.3s"


# Error Handling Tests


@pytest.mark.integration
class TestErrorHandlingE2E:
    """End-to-end tests for error handling."""

    @pytest.mark.anyio
    async def test_invalid_path_returns_404(self, client: "AsyncClient"):
        """Invalid paths return 404, not 500 (AD-016: fail-fast)."""
        response = await client.get("/agentese/nonexistent/path/manifest")

        assert response.status_code in [404, 400], (
            f"Expected 404/400 for invalid path, got {response.status_code}"
        )

    @pytest.mark.anyio
    async def test_error_response_has_message(self, client: "AsyncClient"):
        """Error responses include helpful message (AD-016)."""
        response = await client.get("/agentese/nonexistent/path/manifest")

        if response.status_code != 200:
            data = response.json()
            assert "error" in data or "detail" in data or "message" in data, (
                f"Error response missing message: {data}"
            )

    @pytest.mark.anyio
    async def test_error_includes_similar_paths(self, client: "AsyncClient"):
        """Error responses include similar paths for typo correction (AD-016)."""
        response = await client.get("/agentese/self/memroy/manifest")  # typo: memroy

        if response.status_code == 404:
            data = response.json()
            detail = data.get("detail", {})
            # Should suggest similar paths
            similar = detail.get("similar_paths", [])
            assert len(similar) > 0, "Expected similar paths in error response"


# Script Runner


if __name__ == "__main__":
    import asyncio

    async def main():
        """Run basic E2E tests manually."""
        from httpx import ASGITransport, AsyncClient

        from protocols.api.app import create_app

        print("=== AGENTESE E2E Test Runner ===\n")

        app = create_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            print("Testing /agentese/discover...")
            response = await client.get("/agentese/discover")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                paths = data.get("paths", data)
                print(f"  Paths: {len(paths)}")

            # Test active Crown Jewels
            jewels = [
                ("Brain", "/agentese/self/memory/manifest"),
                ("Graph", "/agentese/concept/graph/manifest"),
            ]

            print("\nTesting Active Crown Jewels:")
            for name, path in jewels:
                start = time.time()
                response = await client.get(path)
                elapsed = time.time() - start
                status = "✓" if response.status_code == 200 else "✗"
                print(f"  {status} {name}: {response.status_code} ({elapsed:.3f}s)")

        print("\n=== Done ===")

    asyncio.run(main())
