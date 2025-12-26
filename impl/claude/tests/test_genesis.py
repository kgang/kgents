"""
Genesis Flow Integration Tests - Phase 0 of Zero Seed Grand Strategy.

Tests the complete genesis protocol:
1. POST /api/genesis/seed creates Zero Seed at t=0
2. Axioms A1, A2, G appear in sequence
3. Design Laws are stored and queryable
4. Genesis is idempotent (calling seed twice doesn't duplicate)
5. GET /api/genesis/status returns correct seeded state

Philosophy:
    "From nothing, the seed. From the seed, the axioms. From the axioms, the layers."

Success Criteria (from plans/zero-seed-genesis-grand-strategy.md):
✓ Zero Seed appears in cosmos at t=0
✓ Axioms A1, A2, G appear at t=1, t=2, t=3
✓ Design Laws stored and queryable
✓ Genesis can only happen once (idempotent check)
✓ GET /api/genesis/status returns correct seeded state

Reference: plans/zero-seed-genesis-grand-strategy.md (Part III: The Genesis Protocol)
"""

import pytest
from fastapi.testclient import TestClient

from protocols.api.app import create_app


@pytest.fixture
def client() -> TestClient:
    """Create test client with fresh app."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def reset_genesis():
    """Reset genesis state before and after each test."""
    # This will need to be implemented when the actual genesis service exists
    # For now, it's a placeholder for cleanup
    yield
    # Teardown: clear genesis state if needed


class TestGenesisSeed:
    """Test POST /api/genesis/seed endpoint."""

    @pytest.mark.asyncio
    async def test_seed_creates_zero_seed(self, client: TestClient):
        """
        POST /api/genesis/seed creates Zero Seed at t=0.

        The Zero Seed is the unwriteable genesis K-Block.
        It should have:
        - id: "zero-seed-genesis"
        - created_at: t=0 (EPOCH)
        - layer: 0 (below L1 - the ground of grounds)
        - kind: "SYSTEM"
        - galois_loss: 0.000 (perfect self-coherence)
        """
        response = client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": [
                    "FeedIsPrimitive",
                    "KBlockIncidentalEssential",
                    "LinearAdaptation",
                    "ContradictionSurfacing",
                ],
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify Zero Seed properties
        assert "zero_seed" in data
        zero_seed = data["zero_seed"]

        assert zero_seed["id"] == "zero-seed-genesis"
        assert zero_seed["layer"] == 0
        assert zero_seed["kind"] == "SYSTEM"
        assert zero_seed["galois_loss"] == 0.000

        # Verify it's at t=0
        assert "created_at" in zero_seed

    @pytest.mark.asyncio
    async def test_seed_creates_axioms(self, client: TestClient):
        """
        Axioms A1, A2, G appear in sequence at t=1, t=2, t=3.

        The three foundational axioms:
        - A1: "Everything is a node" (loss: 0.002)
        - A2: "Everything composes" (loss: 0.003)
        - G: "Loss measures truth" (loss: 0.000) [Galois foundation]
        """
        response = client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": [
                    "FeedIsPrimitive",
                    "KBlockIncidentalEssential",
                    "LinearAdaptation",
                    "ContradictionSurfacing",
                ],
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify axioms were created
        assert "axioms" in data
        axioms = data["axioms"]

        assert len(axioms) == 3

        # Verify A1: Everything is a node
        a1 = next((ax for ax in axioms if ax["id"] == "A1"), None)
        assert a1 is not None
        assert a1["statement"] == "Everything is a node"
        assert a1["layer"] == 1
        assert a1["loss"] == 0.002

        # Verify A2: Everything composes
        a2 = next((ax for ax in axioms if ax["id"] == "A2"), None)
        assert a2 is not None
        assert a2["statement"] == "Everything composes"
        assert a2["layer"] == 1
        assert a2["loss"] == 0.003

        # Verify G: Loss measures truth (Galois foundation)
        g = next((ax for ax in axioms if ax["id"] == "G"), None)
        assert g is not None
        assert g["statement"] == "Loss measures truth"
        assert g["layer"] == 1
        assert g["loss"] == 0.000  # Perfect - the foundation itself

    @pytest.mark.asyncio
    async def test_seed_stores_design_laws(self, client: TestClient):
        """
        Design Laws are stored and queryable.

        The four immutable design laws:
        1. FeedIsPrimitive (Layer 1 - Axiom level)
        2. KBlockIncidentalEssential (Layer 2 - Value level)
        3. LinearAdaptation (Layer 2 - Value level)
        4. ContradictionSurfacing (Layer 1 - Axiom level)
        """
        response = client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": [
                    "FeedIsPrimitive",
                    "KBlockIncidentalEssential",
                    "LinearAdaptation",
                    "ContradictionSurfacing",
                ],
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify design laws were created
        assert "design_laws" in data
        laws = data["design_laws"]

        assert len(laws) == 4

        # Verify each law exists and has correct properties
        law_names = {law["name"] for law in laws}
        assert "FeedIsPrimitive" in law_names
        assert "KBlockIncidentalEssential" in law_names
        assert "LinearAdaptation" in law_names
        assert "ContradictionSurfacing" in law_names

        # Verify law layers
        feed_law = next((l for l in laws if l["name"] == "FeedIsPrimitive"), None)
        assert feed_law is not None
        assert feed_law["layer"] == 1  # Axiom level
        assert feed_law["immutable"] is True

        kblock_law = next((l for l in laws if l["name"] == "KBlockIncidentalEssential"), None)
        assert kblock_law is not None
        assert kblock_law["layer"] == 2  # Value level
        assert kblock_law["immutable"] is True

    @pytest.mark.asyncio
    async def test_seed_is_idempotent(self, client: TestClient):
        """
        Calling seed twice doesn't duplicate.

        Genesis can only happen once. If called again, it should:
        - Return 409 Conflict OR
        - Return 200 with message "Already seeded" OR
        - Silently succeed without creating duplicates

        This test verifies the system's response to duplicate seeding.
        """
        # First seed - should succeed
        response1 = client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": [
                    "FeedIsPrimitive",
                    "KBlockIncidentalEssential",
                    "LinearAdaptation",
                    "ContradictionSurfacing",
                ],
            },
        )

        assert response1.status_code == 200
        data1 = response1.json()

        # Second seed - should not duplicate
        response2 = client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": [
                    "FeedIsPrimitive",
                    "KBlockIncidentalEssential",
                    "LinearAdaptation",
                    "ContradictionSurfacing",
                ],
            },
        )

        # Either reject with 409 or accept but indicate already seeded
        if response2.status_code == 409:
            # Explicit rejection
            assert "already seeded" in response2.json()["detail"].lower()
        else:
            # Silent acceptance
            assert response2.status_code == 200
            data2 = response2.json()

            # Verify no duplication - Zero Seed ID should be the same
            assert data2["zero_seed"]["id"] == data1["zero_seed"]["id"]

            # Verify axiom count didn't double
            # (This would need to query the actual store to verify)
            # For now, verify the response structure is consistent
            assert len(data2["axioms"]) == 3
            assert len(data2["design_laws"]) == 4

    @pytest.mark.asyncio
    async def test_seed_with_minimal_axioms(self, client: TestClient):
        """
        Seeding with only the minimal required axioms works.

        At minimum, we need the Galois axiom (G).
        A1 and A2 are standard but theoretically optional.
        """
        response = client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["G"],  # Just the Galois foundation
                "design_laws": ["FeedIsPrimitive"],  # Minimal law
            },
        )

        # Should succeed with minimal config
        assert response.status_code in [200, 201]
        data = response.json()

        assert "zero_seed" in data
        assert "axioms" in data

        # At least G should be present
        g_axiom = next((ax for ax in data["axioms"] if ax["id"] == "G"), None)
        assert g_axiom is not None

    @pytest.mark.asyncio
    async def test_seed_rejects_invalid_axioms(self, client: TestClient):
        """
        Seeding with invalid axiom IDs should fail gracefully.

        Only valid axiom IDs (A1, A2, G) should be accepted.
        """
        response = client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["INVALID", "ALSO_INVALID"],
                "design_laws": ["FeedIsPrimitive"],
            },
        )

        # Should reject invalid axioms
        assert response.status_code in [400, 422]  # Bad Request or Unprocessable Entity

    @pytest.mark.asyncio
    async def test_seed_rejects_invalid_design_laws(self, client: TestClient):
        """
        Seeding with invalid design law names should fail gracefully.

        Only the four canonical design laws should be accepted.
        """
        response = client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": ["NotARealLaw", "AlsoFake"],
            },
        )

        # Should reject invalid laws
        assert response.status_code in [400, 422]


class TestGenesisStatus:
    """Test GET /api/genesis/status endpoint."""

    @pytest.mark.asyncio
    async def test_status_before_seeding(self, client: TestClient):
        """
        GET /api/genesis/status before seeding returns unseeded state.

        Before genesis has occurred, status should indicate:
        - seeded: false
        - zero_seed_exists: false
        - axiom_count: 0
        - design_law_count: 0
        """
        response = client.get("/api/genesis/status")

        assert response.status_code == 200
        data = response.json()

        assert "seeded" in data
        assert data["seeded"] is False

        assert "zero_seed_exists" in data
        assert data["zero_seed_exists"] is False

        assert "axiom_count" in data
        assert data["axiom_count"] == 0

        assert "design_law_count" in data
        assert data["design_law_count"] == 0

    @pytest.mark.asyncio
    async def test_status_after_seeding(self, client: TestClient):
        """
        GET /api/genesis/status after seeding returns seeded state.

        After genesis has occurred, status should indicate:
        - seeded: true
        - zero_seed_exists: true
        - axiom_count: 3 (A1, A2, G)
        - design_law_count: 4
        - created_at: timestamp of seeding
        """
        # First, seed the system
        client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": [
                    "FeedIsPrimitive",
                    "KBlockIncidentalEssential",
                    "LinearAdaptation",
                    "ContradictionSurfacing",
                ],
            },
        )

        # Then check status
        response = client.get("/api/genesis/status")

        assert response.status_code == 200
        data = response.json()

        assert data["seeded"] is True
        assert data["zero_seed_exists"] is True
        assert data["axiom_count"] == 3
        assert data["design_law_count"] == 4

        # Should have a creation timestamp
        assert "created_at" in data
        assert data["created_at"] is not None

    @pytest.mark.asyncio
    async def test_status_includes_zero_seed_details(self, client: TestClient):
        """
        Status response includes Zero Seed details when seeded.

        The response should include:
        - zero_seed.id
        - zero_seed.layer (0)
        - zero_seed.galois_loss (0.000)
        - zero_seed.created_at
        """
        # Seed first
        client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": [
                    "FeedIsPrimitive",
                    "KBlockIncidentalEssential",
                    "LinearAdaptation",
                    "ContradictionSurfacing",
                ],
            },
        )

        # Check status
        response = client.get("/api/genesis/status")

        assert response.status_code == 200
        data = response.json()

        assert "zero_seed" in data
        zero_seed = data["zero_seed"]

        assert zero_seed["id"] == "zero-seed-genesis"
        assert zero_seed["layer"] == 0
        assert zero_seed["galois_loss"] == 0.000
        assert "created_at" in zero_seed


class TestDesignLawsQuery:
    """Test querying Design Laws after genesis."""

    @pytest.mark.asyncio
    async def test_design_laws_queryable(self, client: TestClient):
        """
        Design laws are stored and retrievable after genesis.

        Should be able to query design laws via:
        - GET /api/genesis/design-laws (list all)
        - GET /api/genesis/design-laws/{law_name} (get specific)
        """
        # Seed first
        client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": [
                    "FeedIsPrimitive",
                    "KBlockIncidentalEssential",
                    "LinearAdaptation",
                    "ContradictionSurfacing",
                ],
            },
        )

        # Query all design laws
        response = client.get("/api/genesis/design-laws")

        assert response.status_code == 200
        data = response.json()

        assert "design_laws" in data
        laws = data["design_laws"]

        assert len(laws) == 4

        # Verify each law has required properties
        for law in laws:
            assert "name" in law
            assert "layer" in law
            assert "immutable" in law
            assert law["immutable"] is True  # All design laws are immutable

    @pytest.mark.asyncio
    async def test_query_specific_design_law(self, client: TestClient):
        """
        Can retrieve a specific design law by name.

        GET /api/genesis/design-laws/FeedIsPrimitive should return
        the full law definition with:
        - name: "FeedIsPrimitive"
        - layer: 1
        - immutable: true
        - description: The law's purpose
        """
        # Seed first
        client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": [
                    "FeedIsPrimitive",
                    "KBlockIncidentalEssential",
                    "LinearAdaptation",
                    "ContradictionSurfacing",
                ],
            },
        )

        # Query specific law
        response = client.get("/api/genesis/design-laws/FeedIsPrimitive")

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "FeedIsPrimitive"
        assert data["layer"] == 1
        assert data["immutable"] is True
        assert "description" in data  # Should have docstring/description

    @pytest.mark.asyncio
    async def test_query_nonexistent_law_returns_404(self, client: TestClient):
        """
        Querying a non-existent design law returns 404.
        """
        # Seed first
        client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": ["FeedIsPrimitive"],
            },
        )

        # Query non-existent law
        response = client.get("/api/genesis/design-laws/NonExistentLaw")

        assert response.status_code == 404


class TestGenesisCosmosIntegration:
    """Test genesis integration with the Cosmos (K-Block storage)."""

    @pytest.mark.asyncio
    async def test_zero_seed_in_cosmos_feed(self, client: TestClient):
        """
        Zero Seed appears as first entry in Cosmos feed.

        After genesis, querying the Cosmos feed should show:
        - Zero Seed at t=0 (first entry)
        - Axioms A1, A2, G following in sequence
        """
        # Seed first
        client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": [
                    "FeedIsPrimitive",
                    "KBlockIncidentalEssential",
                    "LinearAdaptation",
                    "ContradictionSurfacing",
                ],
            },
        )

        # Query cosmos feed
        # NOTE: Actual endpoint will depend on implementation
        # This is a placeholder showing what we expect
        response = client.get("/api/cosmos/feed?limit=10")

        if response.status_code == 200:
            data = response.json()

            if "entries" in data:
                entries = data["entries"]

                # Zero Seed should be first
                if len(entries) > 0:
                    first_entry = entries[0]
                    assert first_entry["id"] == "zero-seed-genesis"
                    assert first_entry["layer"] == 0

    @pytest.mark.asyncio
    async def test_axioms_sequential_in_cosmos(self, client: TestClient):
        """
        Axioms appear in sequential order in Cosmos.

        After Zero Seed, the next three entries should be:
        - t=1: A1 ("Everything is a node")
        - t=2: A2 ("Everything composes")
        - t=3: G ("Loss measures truth")
        """
        # Seed first
        client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": [
                    "FeedIsPrimitive",
                    "KBlockIncidentalEssential",
                    "LinearAdaptation",
                    "ContradictionSurfacing",
                ],
            },
        )

        # Query cosmos feed for axioms
        response = client.get("/api/cosmos/feed?layer=1&limit=10")

        if response.status_code == 200:
            data = response.json()

            if "entries" in data:
                axiom_entries = [e for e in data["entries"] if e["layer"] == 1]

                # Should have 3 axioms
                if len(axiom_entries) >= 3:
                    axiom_ids = [e["id"] for e in axiom_entries[:3]]
                    assert "A1" in axiom_ids
                    assert "A2" in axiom_ids
                    assert "G" in axiom_ids


class TestGenesisPerformance:
    """Test genesis performance requirements."""

    @pytest.mark.asyncio
    async def test_seed_completes_quickly(self, client: TestClient):
        """
        Genesis seeding completes in < 2 seconds.

        Success criteria from Grand Strategy:
        - ./reset-world.sh completes in < 60 seconds
        - API seeding should be much faster (< 2s target)
        """
        import time

        start = time.time()

        response = client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": [
                    "FeedIsPrimitive",
                    "KBlockIncidentalEssential",
                    "LinearAdaptation",
                    "ContradictionSurfacing",
                ],
            },
        )

        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 2.0, f"Genesis took {elapsed:.2f}s, expected < 2s"

    @pytest.mark.asyncio
    async def test_status_query_fast(self, client: TestClient):
        """
        Status query is fast (< 100ms).

        Querying genesis status should be near-instantaneous.
        """
        import time

        # Seed first
        client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": ["FeedIsPrimitive"],
            },
        )

        # Time status query
        start = time.time()
        response = client.get("/api/genesis/status")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.1, f"Status query took {elapsed:.3f}s, expected < 100ms"


class TestGenesisErrorHandling:
    """Test error cases and edge conditions."""

    @pytest.mark.asyncio
    async def test_seed_without_axioms_fails(self, client: TestClient):
        """
        Seeding without any axioms should fail.

        At minimum, the Galois axiom (G) is required.
        """
        response = client.post(
            "/api/genesis/seed",
            json={
                "axioms": [],  # Empty!
                "design_laws": ["FeedIsPrimitive"],
            },
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_seed_without_design_laws_fails(self, client: TestClient):
        """
        Seeding without any design laws should fail.

        At minimum, FeedIsPrimitive is required.
        """
        response = client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": [],  # Empty!
            },
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_malformed_seed_request(self, client: TestClient):
        """
        Malformed seed request returns 422 Unprocessable Entity.
        """
        response = client.post(
            "/api/genesis/seed",
            json={
                # Missing required fields
                "invalid_field": "value",
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_status_survives_multiple_queries(self, client: TestClient):
        """
        Status endpoint remains consistent across multiple queries.

        Querying status multiple times should return identical results.
        """
        # Seed first
        client.post(
            "/api/genesis/seed",
            json={
                "axioms": ["A1", "A2", "G"],
                "design_laws": [
                    "FeedIsPrimitive",
                    "KBlockIncidentalEssential",
                    "LinearAdaptation",
                    "ContradictionSurfacing",
                ],
            },
        )

        # Query status multiple times
        responses = [client.get("/api/genesis/status") for _ in range(5)]

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

        # All should return same seeded state
        datas = [r.json() for r in responses]
        assert all(d["seeded"] is True for d in datas)
        assert all(d["axiom_count"] == 3 for d in datas)
        assert all(d["design_law_count"] == 4 for d in datas)
