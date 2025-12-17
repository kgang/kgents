"""
Example usage of Collaboration Flow.

This demonstrates how to use the multi-agent blackboard collaboration modality.
"""

import asyncio

from agents.f.config import FlowConfig
from agents.f.flow import Flow
from agents.f.modalities.blackboard import AgentRole
from agents.f.modalities.collaboration import CollaborationFlow
from agents.f.state import Permission

# ============================================================================
# Mock Agents for Example
# ============================================================================


class ExampleAgent:
    """Example agent that generates contributions based on role."""

    def __init__(self, agent_id: str, role_name: str):
        self.agent_id = agent_id
        self.role_name = role_name
        self.name = f"{role_name}Agent"

    async def invoke(self, input):
        """Generate a contribution based on role."""
        # In production, this would call an LLM
        if isinstance(input, dict) or hasattr(input, "problem"):
            problem = getattr(input, "problem", input.get("problem", ""))
            context_count = len(getattr(input, "context", input.get("context", [])))

            if self.role_name == "Analyst":
                return f"Analyzing '{problem}': Based on {context_count} prior contributions, I propose approach A."
            elif self.role_name == "Critic":
                return "Critique: Approach A has risks. Consider alternatives."
            elif self.role_name == "Synthesizer":
                return f"Synthesis: Combining all {context_count} contributions, the recommended solution is..."
            else:
                return f"Contribution from {self.role_name}"
        return "No input provided"


# ============================================================================
# Example Usage
# ============================================================================


async def example_basic_collaboration():
    """Example: Basic multi-agent collaboration."""
    print("\n=== Example: Basic Multi-Agent Collaboration ===\n")

    # Define agent roles
    roles = [
        AgentRole(
            id="analyst",
            name="Analyst",
            description="Generates ideas and analysis",
            permissions={Permission.READ_ALL, Permission.POST, Permission.PROPOSE},
            priority=1,
        ),
        AgentRole(
            id="critic",
            name="Critic",
            description="Challenges and improves ideas",
            permissions={Permission.READ_ALL, Permission.CRITIQUE, Permission.VOTE},
            priority=2,
        ),
        AgentRole(
            id="synthesizer",
            name="Synthesizer",
            description="Combines insights into conclusions",
            permissions={Permission.READ_ALL, Permission.POST, Permission.DECIDE},
            priority=3,
        ),
    ]

    # Create agents
    agents = {
        "analyst": ExampleAgent("analyst", "Analyst"),
        "critic": ExampleAgent("critic", "Critic"),
        "synthesizer": ExampleAgent("synthesizer", "Synthesizer"),
    }

    # Configure collaboration
    config = FlowConfig(
        modality="collaboration",
        consensus_threshold=0.67,
        conflict_strategy="vote",
        round_limit=3,
        max_contributions_per_round=10,
    )

    # Create collaboration flow
    flow_agent = Flow.lift_multi(agents, config)
    collab = CollaborationFlow(flow_agent, agents, roles, config)

    # Start collaboration
    problem = "How should we approach building a new AI agent system?"
    await collab.start(problem)
    print(f"Problem: {problem}\n")

    # Run collaboration rounds
    for round_num in range(1, 4):
        print(f"--- Round {round_num} ---")
        async for contribution in collab.run_round():
            print(
                f"[{contribution.agent_role}] {contribution.content} "
                f"(confidence: {contribution.confidence:.2f})"
            )
        print()

    # Build consensus (if there are proposals)
    if collab.blackboard and collab.blackboard.proposals:
        print("--- Building Consensus ---")
        async for decision in collab.build_consensus():
            print(
                f"Decision on {decision.proposal_id}: {decision.outcome} "
                f"(method: {decision.method})"
            )
        print()

    # Harvest results
    result = await collab.harvest()
    print("--- Final Results ---")
    print(f"Rounds completed: {result.rounds_completed}")
    print(f"Total contributions: {len(result.contributions)}")
    print(f"Decisions made: {len(result.decisions)}")
    if result.final_synthesis:
        print(f"\nFinal synthesis:\n{result.final_synthesis}")


async def example_round_robin_order():
    """Example: Round-robin contribution order."""
    print("\n=== Example: Round-Robin Order ===\n")

    roles = [
        AgentRole(
            id="agent1",
            name="Agent 1",
            permissions={Permission.READ_ALL, Permission.POST},
            priority=1,
        ),
        AgentRole(
            id="agent2",
            name="Agent 2",
            permissions={Permission.READ_ALL, Permission.POST},
            priority=2,
        ),
    ]

    agents = {
        "agent1": ExampleAgent("agent1", "Agent 1"),
        "agent2": ExampleAgent("agent2", "Agent 2"),
    }

    config = FlowConfig(
        modality="collaboration",
        contribution_order="round_robin",
    )

    flow_agent = Flow.lift_multi(agents, config)
    collab = CollaborationFlow(flow_agent, agents, roles, config)

    await collab.start("Test problem")

    print("Round 1:")
    async for contrib in collab.run_round():
        print(f"  - {contrib.agent_role}: {contrib.content}")

    print("\nRound 2 (same order):")
    async for contrib in collab.run_round():
        print(f"  - {contrib.agent_role}: {contrib.content}")


async def example_priority_order():
    """Example: Priority-based contribution order."""
    print("\n=== Example: Priority Order ===\n")

    roles = [
        AgentRole(
            id="expert",
            name="Expert",
            permissions={Permission.READ_ALL, Permission.POST},
            priority=1,
        ),
        AgentRole(
            id="novice",
            name="Novice",
            permissions={Permission.READ_ALL, Permission.POST},
            priority=2,
        ),
    ]

    agents = {
        "expert": ExampleAgent("expert", "Expert"),
        "novice": ExampleAgent("novice", "Novice"),
    }

    config = FlowConfig(
        modality="collaboration",
        contribution_order="priority",
    )

    flow_agent = Flow.lift_multi(agents, config)
    collab = CollaborationFlow(flow_agent, agents, roles, config)

    # Set dynamic priorities
    from agents.f.modalities.collaboration import PriorityOrder

    if isinstance(collab.order, PriorityOrder):
        collab.order.set_priority("expert", 0.9)
        collab.order.set_priority("novice", 0.2)

    await collab.start("Test problem")

    print("Contributions (expert has higher priority):")
    async for contrib in collab.run_round():
        print(f"  - {contrib.agent_role}: {contrib.content}")


# ============================================================================
# Main
# ============================================================================


async def main():
    """Run all examples."""
    await example_basic_collaboration()
    await example_round_robin_order()
    await example_priority_order()


if __name__ == "__main__":
    asyncio.run(main())
