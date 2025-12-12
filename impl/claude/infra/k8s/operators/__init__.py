"""K8s Operators for kgents primitives.

Operators manage the lifecycle of kgents custom resources:
- AgentOperator: Create Deployment + Service + Memory from Agent CR
- PheromoneOperator: Decay pheromone intensity over time
- ProposalOperator: Risk-aware change governance with T-gent integration
- MemoryOperator: Manage PVC lifecycle, backup/restore (TODO)
- UmweltOperator: Generate ConfigMaps and validate Secrets (TODO)

Uses kopf (Kubernetes Operator Pythonic Framework).
"""

from .agent_operator import (
    MockAgent,
    MockAgentRegistry,
    generate_memory_cr,
    get_mock_registry,
    parse_agent_spec,
    reset_mock_registry,
)
from .pheromone_operator import (
    MockPheromone,
    MockPheromoneField,
    calculate_intensity,  # v2.0: Passive Stigmergy
    get_mock_field,
    reset_mock_field,
    should_evaporate,  # v2.0: Renamed from should_delete
)
from .proposal_operator import (
    # Mock classes
    MockProposal,
    MockProposalRegistry,
    # Enums
    ProposalPhase,
    ProposalSpec,
    # Data classes
    RiskAssessment,
    RiskLevel,
    calculate_magnitude_factor,
    calculate_risk,
    calculate_test_coverage_factor,
    generate_review_pheromone,
    # Functions
    get_base_risk,
    get_risk_level,
    parse_proposal_spec,
)
from .proposal_operator import (
    get_mock_registry as get_mock_proposal_registry,
)
from .proposal_operator import (
    reset_mock_registry as reset_mock_proposal_registry,
)

__all__ = [
    # Pheromone operator
    "MockPheromone",
    "MockPheromoneField",
    "get_mock_field",
    "reset_mock_field",
    "calculate_intensity",  # v2.0: Passive Stigmergy
    "should_evaporate",  # v2.0: Renamed from should_delete
    # Agent operator
    "MockAgent",
    "MockAgentRegistry",
    "get_mock_registry",
    "reset_mock_registry",
    "parse_agent_spec",
    "generate_memory_cr",
    # Proposal operator
    "ProposalPhase",
    "RiskLevel",
    "RiskAssessment",
    "ProposalSpec",
    "get_base_risk",
    "calculate_magnitude_factor",
    "calculate_test_coverage_factor",
    "get_risk_level",
    "calculate_risk",
    "parse_proposal_spec",
    "generate_review_pheromone",
    "MockProposal",
    "MockProposalRegistry",
    "get_mock_proposal_registry",
    "reset_mock_proposal_registry",
]
