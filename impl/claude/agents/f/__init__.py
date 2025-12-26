"""
F-gents: Flow Agents

The unified substrate for continuous agent interaction:
- Chat: Streaming conversation with context management
- Research: Tree of thought exploration
- Collaboration: Multi-agent blackboard patterns

See: spec/f-gents/README.md

ARCHITECTURE (2025-12-25):
===========================
F-gents implements Flow: streaming substrate with polynomial state machines.

FLOW API:
- Flow: Continuous stream processing with polynomial state machines
- ChatFlow, ResearchFlow, CollaborationFlow: Modalities built on Flow
- FlowConfig, FlowState: Configuration and state management
- See: impl/claude/agents/f/flow.py and impl/claude/agents/f/modalities/

REMOVED (2025-12-25):
- Forge API (Intent/Contract/Prototype/Validate/Crystallize) has been fully removed
- Integrations (C-gent/J-gent/G-gent) that depended on Forge have been removed
- See: brainstorming/FORGE_DEPRECATION.md for historical context
"""

# === Flow Implementation ===
from agents.f.config import (
    ChatConfig,
    CollaborationConfig,
    FlowConfig,
    ResearchConfig,
)
from agents.f.flow import (
    AgentProtocol,
    Flow,
    FlowAgent,
    FlowEvent,
)
from agents.f.j_integration import (
    BoundedComplexity,
    DeterministicOnly,
    EntropyAware,
    IntentFilter,
    RealityGate,
    admits_intent,
    create_safe_gate,
    create_strict_gate,
    gate_intent,
)
from agents.f.modalities import (
    ChatFlow,
    Message,
    SlidingContext,
    SummarizingContext,
    Turn,
    count_tokens,
)
from agents.f.operad import (
    CHAT_OPERAD,
    COLLABORATION_OPERAD,
    FLOW_OPERAD,
    RESEARCH_OPERAD,
    Law,
    Operad,
    Operation,
    get_operad,
)

# Alias for backward compatibility
OpLaw = Law
from agents.f.pipeline import FlowPipeline
from agents.f.polynomial import (
    CHAT_POLYNOMIAL,
    COLLABORATION_POLYNOMIAL,
    FLOW_POLYNOMIAL,
    RESEARCH_POLYNOMIAL,
    FlowPolynomial,
    get_polynomial,
)
from agents.f.state import (
    ContributionType,
    FlowState,
    HypothesisStatus,
    Permission,
)

__all__ = [
    # ============================================================================
    # FLOW API - Use these for all code
    # ============================================================================
    # Core Flow
    "Flow",
    "FlowAgent",
    "FlowEvent",
    "AgentProtocol",
    # State Management
    "FlowState",
    "HypothesisStatus",
    "ContributionType",
    "Permission",
    # Configuration
    "FlowConfig",
    "ChatConfig",
    "ResearchConfig",
    "CollaborationConfig",
    # Modalities - Chat
    "ChatFlow",
    "Turn",
    "Message",
    "SlidingContext",
    "SummarizingContext",
    "count_tokens",
    # Polynomial State Machines
    "FlowPolynomial",
    "FLOW_POLYNOMIAL",
    "CHAT_POLYNOMIAL",
    "RESEARCH_POLYNOMIAL",
    "COLLABORATION_POLYNOMIAL",
    "get_polynomial",
    # Composition Operads
    "Operation",
    "OpLaw",
    "Operad",
    "FLOW_OPERAD",
    "CHAT_OPERAD",
    "RESEARCH_OPERAD",
    "COLLABORATION_OPERAD",
    "get_operad",
    # Pipeline
    "FlowPipeline",
    # Reality contracts (J-gent integration)
    "RealityGate",
    "DeterministicOnly",
    "BoundedComplexity",
    "EntropyAware",
    "IntentFilter",
    "create_safe_gate",
    "create_strict_gate",
    "admits_intent",
    "gate_intent",
]
