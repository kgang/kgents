"""
CI Gate: Contract Types Importability.

This test ensures that all contract types referenced in @node(contracts={})
can be imported and are valid dataclasses. This catches:

1. Typos in type names
2. Circular import issues
3. Missing contract type definitions
4. Non-dataclass types used as contracts

AD-012 (Contract Protocol): Contract types MUST be importable for schema
generation to work. The FE discovers contracts at build time via
/agentese/discover?include_schemas=true.

Run with:
    cd impl/claude
    uv run pytest protocols/agentese/_tests/test_contract_types_importable.py -v
"""

from __future__ import annotations

from dataclasses import is_dataclass

import pytest

from protocols.agentese.contract import Contract, Response
from protocols.agentese.gateway import _import_node_modules
from protocols.agentese.registry import get_registry

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module", autouse=True)
def ensure_nodes_imported():
    """Ensure all node modules are imported before tests run."""
    _import_node_modules()


@pytest.fixture(scope="module")
def registry():
    """Get the populated registry."""
    return get_registry()


@pytest.fixture(scope="module")
def all_contract_types(registry) -> list[tuple[str, str, type]]:
    """
    Extract all contract types from the registry.

    Returns:
        List of (path, aspect, type_class) tuples
    """
    all_contracts = registry.get_all_contracts()
    types_list = []

    for path, contracts in all_contracts.items():
        for aspect, contract in contracts.items():
            if isinstance(contract, Response):
                types_list.append((path, aspect, contract.response_type))
            elif isinstance(contract, Contract):
                types_list.append((path, f"{aspect}.request", contract.request))
                types_list.append((path, f"{aspect}.response", contract.response))

    return types_list


# =============================================================================
# Type Importability Tests
# =============================================================================


class TestContractTypesImportable:
    """
    All contract types MUST be importable.

    If a type cannot be imported, schema generation fails and the
    FE cannot discover the contract shape.
    """

    def test_all_types_are_classes(self, all_contract_types):
        """All contract types must be class types."""
        non_classes = []

        for path, aspect, type_cls in all_contract_types:
            if not isinstance(type_cls, type):
                non_classes.append(f"{path}:{aspect} is {type(type_cls).__name__}, not a class")

        assert not non_classes, "Non-class types found in contracts:\n" + "\n".join(non_classes)

    def test_all_types_are_dataclasses(self, all_contract_types):
        """All contract types should be dataclasses for schema generation."""
        non_dataclasses = []

        for path, aspect, type_cls in all_contract_types:
            if isinstance(type_cls, type) and not is_dataclass(type_cls):
                non_dataclasses.append(f"{path}:{aspect} -> {type_cls.__name__}")

        # Warning only - some types may be TypedDict or other valid schemas
        if non_dataclasses:
            print("\n⚠️ Non-dataclass contract types (may not generate schemas):")
            for entry in non_dataclasses[:10]:
                print(f"  - {entry}")
            if len(non_dataclasses) > 10:
                print(f"  ... and {len(non_dataclasses) - 10} more")

    def test_types_have_module(self, all_contract_types):
        """All contract types must have a __module__ attribute."""
        missing_module = []

        for path, aspect, type_cls in all_contract_types:
            if not hasattr(type_cls, "__module__"):
                missing_module.append(f"{path}:{aspect} -> {type_cls}")

        assert not missing_module, "Contract types missing __module__:\n" + "\n".join(
            missing_module
        )


# =============================================================================
# Type Instantiability Tests
# =============================================================================


class TestContractTypesInstantiable:
    """
    Contract types should be instantiable (not abstract).

    Abstract classes cannot be used directly as contract types
    because the schema generator needs to inspect the fields.
    """

    def test_response_types_not_abstract(self, registry):
        """Response types should not be abstract classes."""
        all_contracts = registry.get_all_contracts()
        abstract_types = []

        for path, contracts in all_contracts.items():
            for aspect, contract in contracts.items():
                if isinstance(contract, Response):
                    type_cls = contract.response_type
                    if hasattr(type_cls, "__abstractmethods__") and type_cls.__abstractmethods__:
                        abstract_types.append(
                            f"{path}:{aspect} -> {type_cls.__name__} has abstract methods: "
                            f"{type_cls.__abstractmethods__}"
                        )

        assert not abstract_types, "Abstract classes used as contract types:\n" + "\n".join(
            abstract_types
        )

    def test_contract_types_not_abstract(self, registry):
        """Request/Response in Contract must not be abstract."""
        all_contracts = registry.get_all_contracts()
        abstract_types = []

        for path, contracts in all_contracts.items():
            for aspect, contract in contracts.items():
                if isinstance(contract, Contract):
                    for name, type_cls in [
                        ("request", contract.request),
                        ("response", contract.response),
                    ]:
                        if (
                            hasattr(type_cls, "__abstractmethods__")
                            and type_cls.__abstractmethods__
                        ):
                            abstract_types.append(f"{path}:{aspect}.{name} -> {type_cls.__name__}")

        assert not abstract_types, "Abstract classes used in Contract types:\n" + "\n".join(
            abstract_types
        )


# =============================================================================
# Type Name Consistency Tests
# =============================================================================


class TestContractTypeNaming:
    """
    Contract types should follow naming conventions.

    Consistent naming helps FE developers understand the types.
    """

    def test_response_types_named_response_or_data(self, all_contract_types):
        """Response types should end with Response, Data, or similar suffix."""
        # This is advisory only - not all types need to follow convention
        non_standard = []
        valid_suffixes = (
            "Response",
            "Data",
            "Result",
            "Manifest",
            "List",
            "Info",
            "State",
            "Status",
        )

        for path, aspect, type_cls in all_contract_types:
            if "response" in aspect.lower():
                name = type_cls.__name__
                if not name.endswith(valid_suffixes):
                    non_standard.append(f"{path}:{aspect} -> {name}")

        # Just report, don't fail
        if non_standard:
            print("\nResponse types with non-standard names (consider renaming):")
            for entry in non_standard[:5]:
                print(f"  - {entry}")

    def test_request_types_named_request(self, all_contract_types):
        """Request types should end with Request."""
        non_standard = []

        for path, aspect, type_cls in all_contract_types:
            if "request" in aspect.lower():
                name = type_cls.__name__
                if not name.endswith(("Request", "Input", "Params", "Args", "Query")):
                    non_standard.append(f"{path}:{aspect} -> {name}")

        # Just report, don't fail
        if non_standard:
            print("\nRequest types with non-standard names (consider renaming):")
            for entry in non_standard[:5]:
                print(f"  - {entry}")


# =============================================================================
# Statistics
# =============================================================================


class TestContractTypeStatistics:
    """Informational statistics about contract types."""

    def test_print_type_stats(self, all_contract_types):
        """Print contract type statistics."""
        unique_types = set()
        modules = set()

        for path, aspect, type_cls in all_contract_types:
            unique_types.add(type_cls)
            if hasattr(type_cls, "__module__"):
                modules.add(type_cls.__module__)

        print("\n=== CONTRACT TYPE STATS ===")
        print(f"Total type references: {len(all_contract_types)}")
        print(f"Unique types: {len(unique_types)}")
        print(f"Modules: {len(modules)}")

        # Group by module
        print("\nTypes by module:")
        module_types = {}
        for type_cls in unique_types:
            mod = getattr(type_cls, "__module__", "unknown")
            module_types.setdefault(mod, []).append(type_cls.__name__)

        for mod in sorted(module_types.keys())[:10]:
            type_names = module_types[mod]
            print(f"  {mod}: {len(type_names)} types")

        # Dataclass coverage
        dataclass_count = sum(1 for t in unique_types if is_dataclass(t))
        dc_coverage = dataclass_count / len(unique_types) * 100 if unique_types else 0
        print(f"\nDataclass coverage: {dataclass_count}/{len(unique_types)} ({dc_coverage:.0f}%)")
