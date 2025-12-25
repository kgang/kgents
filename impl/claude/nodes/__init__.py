"""
AGENTESE Nodes Package.

Central location for @node decorated classes that expose AGENTESE paths.

Node Organization:
- code_node.py - world.code.* (L5 code artifacts)
- void_node.py - void.* (L1-L2 axioms and values)
- concept_node.py - concept.* (L3-L4 prompts and specs)

Teaching:
    gotcha: Importing this module triggers @node decorator registration.
            The gateway imports this to ensure all nodes are discoverable.
            (Evidence: gateway.py::_import_node_modules())
"""

from agents.d.schemas.axiom import AXIOM_SCHEMA, VALUE_SCHEMA
from agents.d.schemas.prompt import INVOCATION_SCHEMA, PROMPT_SCHEMA
from agents.d.universe import get_universe

# Import all node modules to trigger @node registration
from . import code_node, concept_node, void_node  # noqa: F401


def register_crystal_schemas() -> None:
    """
    Register Zero Seed crystal schemas with Universe.

    Called by bootstrap to ensure void.* and concept.* schemas are available.
    """
    universe = get_universe()

    # Register L1-L2 schemas (void.*)
    universe.register_schema(AXIOM_SCHEMA)
    universe.register_schema(VALUE_SCHEMA)

    # Register L3 schema (concept.*)
    universe.register_schema(PROMPT_SCHEMA)
    universe.register_schema(INVOCATION_SCHEMA)


__all__ = ["code_node", "void_node", "concept_node", "register_crystal_schemas"]
