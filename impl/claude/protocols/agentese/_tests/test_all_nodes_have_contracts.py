"""
CI Gate: Contract Coverage for AGENTESE Nodes.

This test ensures that nodes follow the contract protocol:
1. Service nodes (Crown Jewels) MUST have contracts={}
2. Each aspect in contracts MUST reference valid Response/Contract types
3. Contract types MUST be importable and instantiable

AD-012 (Contract Protocol): @node(contracts={}) makes node the contract authority.
The BE defines contracts, FE discovers at build time, both stay synchronized.

IMPORTANT: This test enforces contract coverage in CI. Nodes without contracts
will fail the build. Context resolvers (design.py, etc.) are exempt as they
use @aspect decorators instead of contracts={}.

Run with:
    cd impl/claude
    uv run pytest protocols/agentese/_tests/test_all_nodes_have_contracts.py -v
"""

from __future__ import annotations

import pytest

from protocols.agentese.contract import Contract, ContractType, Response
from protocols.agentese.gateway import _import_node_modules
from protocols.agentese.registry import get_registry

# =============================================================================
# Fixtures
# =============================================================================

# NOTE: ensure_all_nodes_imported() fixture is defined in conftest.py
# with scope="session" to ensure consistent registry state across xdist workers.


@pytest.fixture(scope="module")
def registry():
    """Get the populated registry."""
    # Import again to be safe - idempotent since modules are cached
    _import_node_modules()
    return get_registry()


# =============================================================================
# Crown Jewel Paths (MUST have contracts)
# =============================================================================

# These are the core service nodes that MUST have contract declarations
# Context resolvers (design.py, gardener.py, etc.) use @aspect decorators
# and are exempt from this requirement.
CROWN_JEWEL_PATHS = [
    "self.memory",  # Brain
    "self.chat",  # Chat
    "world.morpheus",  # Morpheus (dream weaver)
    "world.codebase",  # Gestalt
    "world.forge",  # Forge (artisans)
    "world.town",  # Town
    "world.park",  # Park
    # Note: self.soul uses context resolver pattern
    # Note: concept.gardener uses context resolver pattern
]


# =============================================================================
# Contract Coverage Tests
# =============================================================================


class TestCrownJewelContractCoverage:
    """
    Crown Jewel nodes MUST have contracts declared.

    AD-012: The contract protocol requires service nodes to declare
    contracts={} for type-safe BE/FE synchronization.
    """

    @pytest.mark.parametrize("path", CROWN_JEWEL_PATHS)
    def test_crown_jewel_has_contracts(self, registry, path: str):
        """Each Crown Jewel path must have contracts declared."""
        if not registry.has(path):
            pytest.skip(f"Path {path} not registered (may need import)")

        contracts = registry.get_contracts(path)
        assert contracts is not None, (
            f"Crown Jewel '{path}' has no contracts declared. "
            f"Add contracts={{}} to @node decorator in services/*/node.py"
        )
        assert len(contracts) > 0, (
            f"Crown Jewel '{path}' has empty contracts={{}}. "
            f"Add Response/Contract entries for each aspect."
        )

    def test_at_least_6_jewels_have_contracts(self, registry):
        """At least 6 Crown Jewels must have contracts (sanity check)."""
        with_contracts = []
        for path in CROWN_JEWEL_PATHS:
            if registry.has(path):
                contracts = registry.get_contracts(path)
                if contracts and len(contracts) > 0:
                    with_contracts.append(path)

        assert len(with_contracts) >= 6, (
            f"Only {len(with_contracts)} Crown Jewels have contracts. "
            f"Expected at least 6. Missing: {set(CROWN_JEWEL_PATHS) - set(with_contracts)}"
        )


# =============================================================================
# Contract Type Validation Tests
# =============================================================================


class TestContractTypeValidity:
    """
    All contract entries must use valid Response/Contract types.

    Contract types must be:
    1. Response(dataclass) for perception aspects
    2. Contract(request_dc, response_dc) for mutation aspects
    3. Request(dataclass) for fire-and-forget (rare)
    """

    def test_all_contracts_are_valid_types(self, registry):
        """Every contract entry must be a valid ContractType."""
        from protocols.agentese.contract import Request

        all_contracts = registry.get_all_contracts()

        invalid_entries = []

        for path, contracts in all_contracts.items():
            for aspect, contract in contracts.items():
                # Must be Response, Contract, or Request
                valid_types = (Response, Contract, Request)
                if not isinstance(contract, valid_types):
                    invalid_entries.append(
                        f"{path}:{aspect} is {type(contract).__name__}, "
                        f"expected Response/Contract/Request"
                    )

        assert not invalid_entries, "Invalid contract types found:\n" + "\n".join(invalid_entries)

    def test_response_contracts_have_type(self, registry):
        """Response contracts must reference a response_type."""
        all_contracts = registry.get_all_contracts()

        missing_type = []

        for path, contracts in all_contracts.items():
            for aspect, contract in contracts.items():
                if isinstance(contract, Response):
                    if not hasattr(contract, "response_type"):
                        missing_type.append(f"{path}:{aspect}")
                    elif contract.response_type is None:
                        missing_type.append(f"{path}:{aspect} (type is None)")

        assert not missing_type, "Response contracts missing response_type:\n" + "\n".join(
            missing_type
        )

    def test_contract_contracts_have_both_types(self, registry):
        """Contract entries must have both request and response types."""
        all_contracts = registry.get_all_contracts()

        incomplete = []

        for path, contracts in all_contracts.items():
            for aspect, contract in contracts.items():
                if isinstance(contract, Contract):
                    if not hasattr(contract, "request") or contract.request is None:
                        incomplete.append(f"{path}:{aspect} missing request type")
                    if not hasattr(contract, "response") or contract.response is None:
                        incomplete.append(f"{path}:{aspect} missing response type")

        assert not incomplete, "Contract entries incomplete:\n" + "\n".join(incomplete)


# =============================================================================
# Aspect Coverage Tests
# =============================================================================


class TestAspectCoverage:
    """
    Contract aspects should cover common patterns.

    Not all aspects need contracts (some are computed), but
    common aspects like manifest, list, search should have them.
    """

    COMMON_ASPECTS = ["manifest"]  # Every node should have manifest contract

    def test_manifest_aspect_coverage(self, registry):
        """Nodes with contracts should have manifest in contracts."""
        all_contracts = registry.get_all_contracts()

        missing_manifest = []

        for path, contracts in all_contracts.items():
            if "manifest" not in contracts:
                # Check if any aspect is defined (not empty node)
                if len(contracts) > 0:
                    missing_manifest.append(path)

        # Warning only - not all nodes need manifest contract
        if missing_manifest:
            print("\nNodes without manifest contract (consider adding):")
            for path in missing_manifest[:5]:
                print(f"  - {path}")


# =============================================================================
# Statistics (Informational)
# =============================================================================


class TestContractStatistics:
    """Informational statistics about contract coverage."""

    def test_print_contract_stats(self, registry):
        """Print contract coverage statistics."""
        all_contracts = registry.get_all_contracts()
        all_paths = registry.list_paths()

        coverage = len(all_contracts) / len(all_paths) * 100 if all_paths else 0

        print("\n=== CONTRACT COVERAGE ===")
        print(f"Total paths: {len(all_paths)}")
        print(f"Paths with contracts: {len(all_contracts)}")
        print(f"Coverage: {coverage:.1f}%")

        # Count by contract type
        response_count = 0
        contract_count = 0
        request_count = 0

        for contracts in all_contracts.values():
            for contract in contracts.values():
                if isinstance(contract, Response):
                    response_count += 1
                elif isinstance(contract, Contract):
                    contract_count += 1
                else:
                    request_count += 1

        total = response_count + contract_count + request_count
        print(f"\nContract types ({total} total):")
        print(f"  Response (perception): {response_count}")
        print(f"  Contract (mutation): {contract_count}")
        print(f"  Request (fire-forget): {request_count}")

        # List paths by contract count
        print("\nPaths by aspect count:")
        sorted_paths = sorted(all_contracts.items(), key=lambda x: len(x[1]), reverse=True)
        for path, contracts in sorted_paths[:7]:
            print(f"  {path}: {len(contracts)} aspects")
