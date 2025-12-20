"""
Research Flow: Tree of Thought exploration.

ResearchFlow wraps FlowAgent to provide tree-of-thought exploration
with branching, pruning, and merging strategies.

See: spec/f-gents/research.md
"""

from __future__ import annotations

import asyncio
import heapq
from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, AsyncIterator, Literal

from agents.f.config import FlowConfig
from agents.f.flow import AgentProtocol, Flow, FlowAgent
from agents.f.modalities.hypothesis import (
    Evidence,
    Hypothesis,
    HypothesisTree,
    Insight,
    Synthesis,
)
from agents.f.state import HypothesisStatus

if TYPE_CHECKING:
    from typing import Any


BranchStrategy = Literal["uncertainty", "contradiction", "explicit"]
MergeStrategy = Literal["best_first", "weighted_vote", "synthesis"]
ExploreStrategy = Literal["depth_first", "breadth_first", "best_first"]


@dataclass
class ResearchStats:
    """Statistics for research exploration."""

    hypotheses_generated: int = 0
    """Total hypotheses created."""

    hypotheses_pruned: int = 0
    """Hypotheses eliminated."""

    max_depth_reached: int = 0
    """Deepest exploration level."""

    insights_discovered: int = 0
    """Total insights yielded."""

    explorations_performed: int = 0
    """Number of hypothesis explorations."""

    @property
    def branch_factor(self) -> float:
        """Average children per node."""
        if self.hypotheses_generated <= 1:
            return 0.0
        # Root doesn't count toward branch factor
        return (self.hypotheses_generated - 1) / max(
            1, self.hypotheses_generated - self.hypotheses_pruned - 1
        )

    @property
    def exploration_efficiency(self) -> float:
        """Insights per hypothesis explored."""
        if self.explorations_performed == 0:
            return 0.0
        return self.insights_discovered / self.explorations_performed


@dataclass
class ResearchResult:
    """Final result of research exploration."""

    question: str
    """The research question."""

    answer: Synthesis | None
    """Final synthesized answer."""

    confidence: float
    """Confidence in the answer."""

    tree: HypothesisTree
    """Full exploration tree."""

    insights: list[Insight]
    """All insights discovered."""

    statistics: ResearchStats
    """Exploration metrics."""


class ResearchFlow:
    """
    Research Flow wrapper for FlowAgent.

    Provides tree-of-thought exploration with:
    - Hypothesis generation (branching)
    - Promise-based pruning
    - Multiple exploration strategies
    - Synthesis and merging
    """

    def __init__(
        self,
        agent: AgentProtocol[str, str] | FlowAgent[str, str],
        config: FlowConfig | None = None,
    ) -> None:
        """
        Initialize research flow.

        Args:
            agent: The agent to use for exploration
            config: Flow configuration (will be set to research modality)
        """
        if config is None:
            config = FlowConfig(modality="research")
        elif config.modality != "research":
            # Override modality
            config = FlowConfig(**{**config.__dict__, "modality": "research"})

        # If agent is already a FlowAgent, use it; otherwise lift it
        if isinstance(agent, FlowAgent):
            self.flow = agent
            self.flow.config = config
        else:
            self.flow = Flow.lift(agent, config)

        self.config = config
        self.tree: HypothesisTree | None = None
        self.insights: list[Insight] = []
        self.stats = ResearchStats()

    async def explore(
        self,
        question: str,
        strategy: ExploreStrategy | None = None,
    ) -> ResearchResult:
        """
        Explore a research question.

        Args:
            question: The question to explore
            strategy: Exploration strategy (defaults to config)

        Returns:
            ResearchResult with answer and exploration tree
        """
        if strategy is None:
            strategy = self.config.exploration_strategy

        # Initialize tree
        self.tree = HypothesisTree(question)
        self.insights = []
        self.stats = ResearchStats()
        self.stats.hypotheses_generated = 1  # Root counts

        # Run exploration based on strategy
        if strategy == "depth_first":
            async for insight in self.explore_depth_first(self.tree.root):
                self.insights.append(insight)
                self.stats.insights_discovered += 1
        elif strategy == "breadth_first":
            async for insight in self.explore_breadth_first(self.tree.root):
                self.insights.append(insight)
                self.stats.insights_discovered += 1
        elif strategy == "best_first":
            async for insight in self.explore_best_first(self.tree.root):
                self.insights.append(insight)
                self.stats.insights_discovered += 1

        # Generate final synthesis
        leaves = [h for h in self.tree.get_leaves() if h.status != HypothesisStatus.PRUNED]

        if leaves:
            answer = await self.merge(leaves, self.config.merge_strategy)
        else:
            answer = None

        return ResearchResult(
            question=question,
            answer=answer,
            confidence=answer.confidence if answer else 0.0,
            tree=self.tree,
            insights=self.insights,
            statistics=self.stats,
        )

    async def explore_depth_first(
        self,
        root: Hypothesis,
    ) -> AsyncIterator[Insight]:
        """
        Explore using depth-first search.

        Fully explores one branch before moving to siblings.
        """
        stack = [root]

        while stack and not self._should_stop():
            current = stack.pop()

            # Explore this hypothesis
            async for insight in self._explore_hypothesis(current):
                yield insight

            # Check if we should branch
            if self._should_branch(current):
                children = await self.branch(current)
                # Add in reverse order so first child is explored first
                stack.extend(reversed(children))

    async def explore_breadth_first(
        self,
        root: Hypothesis,
    ) -> AsyncIterator[Insight]:
        """
        Explore using breadth-first search.

        Explores all hypotheses at each depth level before going deeper.
        """
        queue = deque([root])

        while queue and not self._should_stop():
            current = queue.popleft()

            # Explore this hypothesis
            async for insight in self._explore_hypothesis(current):
                yield insight

            # Check if we should branch
            if self._should_branch(current):
                children = await self.branch(current)
                queue.extend(children)

    async def explore_best_first(
        self,
        root: Hypothesis,
    ) -> AsyncIterator[Insight]:
        """
        Explore using best-first search.

        Always explores highest-promise hypothesis next.
        """
        # Use negative promise for max-heap behavior
        heap: list[tuple[float, int, Hypothesis]] = [(-root.promise, 0, root)]
        counter = 1  # For tie-breaking

        while heap and not self._should_stop():
            _, _, current = heapq.heappop(heap)

            # Skip if already explored
            if current.status == HypothesisStatus.EXPANDED:
                continue

            # Explore this hypothesis
            async for insight in self._explore_hypothesis(current):
                yield insight

            # Check if we should branch
            if self._should_branch(current):
                children = await self.branch(current)
                for child in children:
                    heapq.heappush(heap, (-child.promise, counter, child))
                    counter += 1

    async def _explore_hypothesis(
        self,
        hypothesis: Hypothesis,
    ) -> AsyncIterator[Insight]:
        """
        Explore a single hypothesis.

        Invokes the agent and extracts insights from the response.
        """
        self.stats.explorations_performed += 1

        # Invoke agent with hypothesis
        try:
            response = await self.flow.invoke(hypothesis.content)

            # For now, treat response as evidence
            evidence = Evidence(
                content=str(response),
                supports=True,
                strength=0.7,  # Default strength
                source="agent",
            )
            hypothesis.add_evidence(evidence)

            # Yield insight
            yield Insight(
                type="evidence",
                content=str(response),
                confidence=hypothesis.confidence,
                hypothesis_id=hypothesis.id,
                depth=hypothesis.depth,
            )

        except Exception as e:
            # Record as contradicting evidence
            evidence = Evidence(
                content=f"Error: {e}",
                supports=False,
                strength=0.8,
                source="error",
            )
            hypothesis.add_evidence(evidence)

        # Update max depth
        self.stats.max_depth_reached = max(self.stats.max_depth_reached, hypothesis.depth)

    def _should_branch(self, hypothesis: Hypothesis) -> bool:
        """
        Check if we should branch from this hypothesis.

        Branching criteria:
        - Confidence below threshold (uncertainty)
        - Depth within limit
        - Node budget not exhausted
        """
        if hypothesis.status != HypothesisStatus.EXPLORING:
            return False

        if hypothesis.depth >= self.config.depth_limit:
            return False

        if self.tree and len(self.tree._nodes) >= self.config.max_nodes:
            return False

        # Strategy-specific branching
        if self.config.branching_strategy == "uncertainty":
            return hypothesis.confidence < self.config.branching_threshold

        return False

    def _should_stop(self) -> bool:
        """Check if exploration should stop."""
        # Check exploration budget
        if self.stats.explorations_performed >= self.config.exploration_budget:
            return True

        # Check insight target
        if (
            self.config.insight_target is not None
            and self.stats.insights_discovered >= self.config.insight_target
        ):
            return True

        # Check if we have high-confidence answer
        if self.tree:
            leaves = self.tree.get_leaves()
            if any(h.confidence >= self.config.confidence_threshold for h in leaves):
                return True

        return False

    async def branch(self, hypothesis: Hypothesis) -> list[Hypothesis]:
        """
        Generate alternative hypotheses.

        Creates child hypotheses by invoking the agent with a branching prompt.

        Args:
            hypothesis: The hypothesis to branch from

        Returns:
            List of newly created child hypotheses
        """
        if not self.tree:
            return []

        # Create branching prompt
        prompt = f"""
Given hypothesis: {hypothesis.content}
Evidence so far: {[e.content for e in hypothesis.evidence]}

Generate {self.config.max_branches} alternative hypotheses that:
1. Address the same question from different angles
2. Are consistent with the evidence
3. Could plausibly be true

Return alternatives as numbered list.
"""

        try:
            response = await self.flow.invoke(prompt)
            # Parse response to extract alternatives (simplified)
            alternatives = self._parse_alternatives(str(response))

            children = []
            for alt_content in alternatives[: self.config.max_branches]:
                # Estimate initial promise
                promise = self._estimate_promise(hypothesis, alt_content)

                child = self.tree.add_node(
                    content=alt_content,
                    parent_id=hypothesis.id,
                    confidence=0.5,  # Neutral initial confidence
                    promise=promise,
                )

                children.append(child)
                self.stats.hypotheses_generated += 1

            # Mark parent as expanded
            hypothesis.status = HypothesisStatus.EXPANDED

            # Prune low-promise children if needed
            if hypothesis.depth >= self.config.prune_after_depth:
                children = await self.prune(children)

            return children

        except Exception:
            # Branching failed, mark as explored
            hypothesis.status = HypothesisStatus.EXPANDED
            return []

    def _parse_alternatives(self, response: str) -> list[str]:
        """Parse alternative hypotheses from agent response."""
        # Simple parsing: split by newlines and extract numbered items
        lines = response.strip().split("\n")
        alternatives = []

        for line in lines:
            line = line.strip()
            # Look for numbered items like "1. ...", "1) ...", etc.
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                # Remove numbering
                content = line.lstrip("0123456789.-*) ")
                if content:
                    alternatives.append(content)

        return alternatives if alternatives else [response]

    def _estimate_promise(
        self,
        parent: Hypothesis,
        content: str,
    ) -> float:
        """
        Estimate promise of a hypothesis.

        Factors:
        - Parent confidence (higher parent = higher promise)
        - Depth (deeper = lower promise, exploration cost increases)
        - Content length (very short/long = lower promise)
        """
        # Base promise on parent's confidence
        base_promise = parent.confidence

        # Depth penalty (exponential decay)
        depth_factor = 0.9**parent.depth

        # Content quality (simple heuristic)
        content_length = len(content)
        if content_length < 10 or content_length > 500:
            quality_factor = 0.5
        else:
            quality_factor = 1.0

        return base_promise * depth_factor * quality_factor

    async def prune(self, hypotheses: list[Hypothesis]) -> list[Hypothesis]:
        """
        Remove low-promise hypotheses.

        Args:
            hypotheses: List of hypotheses to consider for pruning

        Returns:
            List of hypotheses that survived pruning
        """
        survivors = []

        for hyp in hypotheses:
            if hyp.promise >= self.config.pruning_threshold:
                survivors.append(hyp)
            else:
                hyp.status = HypothesisStatus.PRUNED
                self.stats.hypotheses_pruned += 1

                # Emit pruning insight
                self.insights.append(
                    Insight(
                        type="evidence",
                        content=f"Pruned low-promise hypothesis: {hyp.content}",
                        confidence=0.0,
                        hypothesis_id=hyp.id,
                        depth=hyp.depth,
                        metadata={"reason": "low_promise"},
                    )
                )

        return survivors

    async def merge(
        self,
        hypotheses: list[Hypothesis],
        strategy: MergeStrategy,
    ) -> Synthesis:
        """
        Merge multiple hypotheses into a synthesis.

        Args:
            hypotheses: Hypotheses to merge
            strategy: Merge strategy to use

        Returns:
            Synthesized result
        """
        if not hypotheses:
            return Synthesis(
                content="No hypotheses to merge",
                confidence=0.0,
                sources=[],
                method=strategy,
            )

        if strategy == "best_first":
            # Take highest-confidence hypothesis
            winner = max(hypotheses, key=lambda h: h.confidence)
            return Synthesis(
                content=winner.content,
                confidence=winner.confidence,
                sources=[winner.id],
                method="best_first",
            )

        elif strategy == "weighted_vote":
            # Confidence-weighted combination
            total_conf = sum(h.confidence for h in hypotheses)
            if total_conf == 0:
                return Synthesis(
                    content=hypotheses[0].content,
                    confidence=0.0,
                    sources=[h.id for h in hypotheses],
                    method="weighted_vote",
                )

            # For now, just take weighted average of confidences
            # In full implementation, would combine content too
            avg_confidence = total_conf / len(hypotheses)
            combined_content = "; ".join(
                h.content for h in sorted(hypotheses, key=lambda h: h.confidence, reverse=True)[:3]
            )

            return Synthesis(
                content=combined_content,
                confidence=avg_confidence,
                sources=[h.id for h in hypotheses],
                method="weighted_vote",
            )

        elif strategy == "synthesis":
            # LLM synthesizes (for now, simple combination)
            prompt = f"""
Synthesize these hypotheses into a unified answer:

{chr(10).join(f"- {h.content} (confidence: {h.confidence:.2f})" for h in hypotheses)}

Provide a coherent synthesis that:
1. Reconciles different viewpoints
2. Identifies common themes
3. Notes unresolved tensions
"""

            try:
                response = await self.flow.invoke(prompt)
                # Average confidence of inputs
                avg_confidence = sum(h.confidence for h in hypotheses) / len(hypotheses)

                return Synthesis(
                    content=str(response),
                    confidence=avg_confidence,
                    sources=[h.id for h in hypotheses],
                    method="synthesis",
                )
            except Exception as e:
                # Fallback to best_first
                winner = max(hypotheses, key=lambda h: h.confidence)
                return Synthesis(
                    content=winner.content,
                    confidence=winner.confidence,
                    sources=[winner.id],
                    method="best_first",
                    metadata={"synthesis_error": str(e)},
                )

        # Fallback
        return Synthesis(
            content=hypotheses[0].content,
            confidence=hypotheses[0].confidence,
            sources=[hypotheses[0].id],
            method=strategy,
        )


__all__ = [
    "ResearchFlow",
    "ResearchStats",
    "ResearchResult",
    "BranchStrategy",
    "MergeStrategy",
    "ExploreStrategy",
]
