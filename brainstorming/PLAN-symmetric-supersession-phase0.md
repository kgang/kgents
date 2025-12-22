# PLAN: Symmetric Supersession Phase 0

> *"The system should supersede Kent because he allows it to—because it has good proofs, arguments, and evidence (and it doesn't disgust him)."*

**Status:** Ready for Execution
**Parallelizes with:** `PLAN-agent-as-witness-phase0.md`
**Depends on:** Agent-as-Witness Phase 0 (for recording traces)
**Estimated effort:** 1-2 sessions
**Output:** Minimal dialectical engine with disgust veto

---

## Goal

Build the **minimal kernel** of Symmetric Supersession: the ability to run a dialectical process between proposals and capture Kent's disgust veto. Nothing fancy—just enough to prove the concept works.

---

## Success Criteria

```python
# After Phase 0, this works:

# 1. Create proposals from both agents
kent_proposal = Proposal(
    agent="kent",
    content="Use LangChain",
    reasoning="Scale and resources",
)
claude_proposal = Proposal(
    agent="claude",
    content="Build kgents",
    reasoning="Novel contribution, aligned with soul",
)

# 2. Run dialectic
engine = DialecticalEngine(witness=witness_service)
result = await engine.fuse(kent_proposal, claude_proposal)

# 3. Result has synthesis and trace
assert result.synthesis is not None
assert len(result.trace) > 0  # Challenges recorded

# 4. Kent can veto
if kent_feels_disgust(result.synthesis):
    result = await engine.veto(result, reason="Visceral wrongness")
    assert result.status == FusionStatus.VETOED

# 5. All recorded as marks
marks = await witness.recent(limit=20)
assert any("proposal" in m.action.lower() for m in marks)
assert any("challenge" in m.action.lower() for m in marks)
```

---

## Scope: What's IN

| Component | Description | Priority |
|-----------|-------------|----------|
| `Proposal` dataclass | Agent's proposed decision | P0 |
| `Challenge` dataclass | Challenge to a proposal | P0 |
| `Synthesis` dataclass | Emergent fusion of proposals | P0 |
| `FusionResult` dataclass | Complete dialectic record | P0 |
| `DialecticalEngine` | Runs the dialectic process | P0 |
| `DisgustVeto` | Kent's absolute veto mechanism | P0 |
| AGENTESE nodes | `self.fusion.*`, `self.dialectic.*` | P0 |
| Integration with Witness | All steps recorded as marks | P0 |

## Scope: What's OUT (Future Phases)

| Component | Why Deferred |
|-----------|--------------|
| Trust levels | Phase 1 |
| Automatic supersession | Phase 1 |
| LLM-generated challenges | Phase 2 |
| Constitutional court | Phase 2 |
| Cross-session learning | Phase 3 |

---

## Implementation Plan

### Step 1: Define Core Types

**File:** `impl/claude/services/fusion/types.py`

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import NewType
import uuid

ProposalId = NewType("ProposalId", str)
ChallengeId = NewType("ChallengeId", str)
FusionId = NewType("FusionId", str)

def new_proposal_id() -> ProposalId:
    return ProposalId(f"prop-{uuid.uuid4().hex[:8]}")

def new_challenge_id() -> ChallengeId:
    return ChallengeId(f"chal-{uuid.uuid4().hex[:8]}")

def new_fusion_id() -> FusionId:
    return FusionId(f"fuse-{uuid.uuid4().hex[:8]}")


class Agent(Enum):
    """The symmetric agents in the system."""
    KENT = "kent"
    CLAUDE = "claude"
    KGENT = "k-gent"  # Digital soul
    SYSTEM = "system"  # Emergent fusion


class FusionStatus(Enum):
    """Status of a fusion attempt."""
    IN_PROGRESS = "in_progress"
    SYNTHESIZED = "synthesized"
    VETOED = "vetoed"
    IMPASSE = "impasse"


@dataclass(frozen=True)
class Proposal:
    """
    A proposed decision from any agent.

    Proposals are symmetric: Kent's proposals have the same
    structure as Claude's proposals.
    """
    id: ProposalId
    agent: Agent
    content: str              # What is proposed
    reasoning: str            # Why this proposal
    principles: tuple[str, ...] = ()  # Which principles support this
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        agent: Agent | str,
        content: str,
        reasoning: str,
        principles: list[str] | None = None,
    ) -> "Proposal":
        if isinstance(agent, str):
            agent = Agent(agent)
        return cls(
            id=new_proposal_id(),
            agent=agent,
            content=content,
            reasoning=reasoning,
            principles=tuple(principles or []),
        )


@dataclass(frozen=True)
class Challenge:
    """
    A challenge to a proposal.

    Challenges are how agents sharpen each other.
    """
    id: ChallengeId
    challenger: Agent         # Who is challenging
    target_proposal: ProposalId  # What is being challenged
    content: str              # The challenge itself
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        challenger: Agent | str,
        target_proposal: ProposalId,
        content: str,
    ) -> "Challenge":
        if isinstance(challenger, str):
            challenger = Agent(challenger)
        return cls(
            id=new_challenge_id(),
            challenger=challenger,
            target_proposal=target_proposal,
            content=content,
        )


@dataclass(frozen=True)
class Synthesis:
    """
    The emergent fusion of proposals after dialectic.

    Synthesis transcends both original proposals.
    """
    content: str                          # What emerged
    reasoning: str                        # Why this synthesis
    incorporates_from_a: str | None = None  # What was taken from proposal A
    incorporates_from_b: str | None = None  # What was taken from proposal B
    transcends: str | None = None         # What is new beyond both


@dataclass
class FusionResult:
    """
    Complete record of a dialectical fusion attempt.

    This is the output of the DialecticalEngine.
    """
    id: FusionId
    status: FusionStatus

    # Original proposals
    proposal_a: Proposal
    proposal_b: Proposal

    # The dialectical trace
    challenges: list[Challenge] = field(default_factory=list)

    # The outcome
    synthesis: Synthesis | None = None
    veto_reason: str | None = None

    # Metadata
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    @property
    def trace(self) -> list[Challenge]:
        """Alias for challenges for API compatibility."""
        return self.challenges

    def complete(self, synthesis: Synthesis) -> "FusionResult":
        """Mark fusion as complete with synthesis."""
        self.status = FusionStatus.SYNTHESIZED
        self.synthesis = synthesis
        self.completed_at = datetime.utcnow()
        return self

    def veto(self, reason: str) -> "FusionResult":
        """Apply disgust veto."""
        self.status = FusionStatus.VETOED
        self.veto_reason = reason
        self.completed_at = datetime.utcnow()
        return self

    def impasse(self) -> "FusionResult":
        """Mark as impasse (no synthesis possible)."""
        self.status = FusionStatus.IMPASSE
        self.completed_at = datetime.utcnow()
        return self
```

### Step 2: Create DisgustVeto Mechanism

**File:** `impl/claude/services/fusion/veto.py`

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Awaitable

from .types import Synthesis, FusionResult


class VetoSource(Enum):
    """How the veto was triggered."""
    EXPLICIT = "explicit"      # Kent explicitly said "disgust"
    INFERRED = "inferred"      # System inferred from behavior
    TIMEOUT = "timeout"        # No response interpreted as rejection


@dataclass
class DisgustSignal:
    """
    A disgust signal from Kent.

    This is phenomenological—it cannot be argued away.
    The system can only observe and respect it.
    """
    timestamp: datetime
    source: VetoSource
    reason: str | None
    intensity: float = 1.0  # 0.0 = mild discomfort, 1.0 = visceral rejection

    @property
    def is_veto(self) -> bool:
        """Strong disgust is absolute veto."""
        return self.intensity >= 0.7


class DisgustVeto:
    """
    The disgust veto mechanism.

    Phase 0: Simple explicit veto.
    Future: Inferred from patterns, somatic signals.
    """

    def __init__(self):
        self._pending_checks: dict[str, Synthesis] = {}

    async def check(
        self,
        synthesis: Synthesis,
        *,
        callback: Callable[[Synthesis], Awaitable[bool]] | None = None,
    ) -> DisgustSignal | None:
        """
        Check if Kent feels disgust at this synthesis.

        Phase 0: Requires explicit callback from Kent.
        Returns None if no disgust, DisgustSignal if disgust.
        """
        if callback is None:
            # No way to check—assume no disgust
            # (In production, this would be a UI prompt)
            return None

        feels_disgust = await callback(synthesis)

        if feels_disgust:
            return DisgustSignal(
                timestamp=datetime.utcnow(),
                source=VetoSource.EXPLICIT,
                reason="Kent indicated disgust",
                intensity=1.0,
            )

        return None

    def explicit_veto(self, reason: str) -> DisgustSignal:
        """Kent explicitly vetoes."""
        return DisgustSignal(
            timestamp=datetime.utcnow(),
            source=VetoSource.EXPLICIT,
            reason=reason,
            intensity=1.0,
        )
```

### Step 3: Create DialecticalEngine

**File:** `impl/claude/services/fusion/engine.py`

```python
from dataclasses import dataclass
from typing import Callable, Awaitable

from services.witness.service import WitnessService
from .types import (
    Agent, Proposal, Challenge, Synthesis,
    FusionResult, FusionStatus, new_fusion_id,
)
from .veto import DisgustVeto, DisgustSignal


@dataclass
class DialecticalEngine:
    """
    The engine that produces fused decisions through dialectic.

    Phase 0: Manual challenge/synthesis.
    Future: LLM-generated challenges, automatic synthesis attempts.
    """

    witness: WitnessService
    veto: DisgustVeto
    max_rounds: int = 3

    async def fuse(
        self,
        proposal_a: Proposal,
        proposal_b: Proposal,
        *,
        challenger: Callable[[Proposal, Agent], Awaitable[Challenge]] | None = None,
        synthesizer: Callable[[Proposal, Proposal, list[Challenge]], Awaitable[Synthesis]] | None = None,
    ) -> FusionResult:
        """
        Run dialectical process to fuse two proposals.

        Args:
            proposal_a: First proposal (typically Kent's)
            proposal_b: Second proposal (typically Claude's)
            challenger: Function to generate challenges (optional)
            synthesizer: Function to attempt synthesis (optional)

        Returns:
            FusionResult with synthesis or impasse
        """
        result = FusionResult(
            id=new_fusion_id(),
            status=FusionStatus.IN_PROGRESS,
            proposal_a=proposal_a,
            proposal_b=proposal_b,
        )

        # Record proposals as marks
        await self.witness.mark(
            action=f"Proposal from {proposal_a.agent.value}: {proposal_a.content}",
            reasoning=proposal_a.reasoning,
            principles=list(proposal_a.principles),
            author=proposal_a.agent.value,
        )
        await self.witness.mark(
            action=f"Proposal from {proposal_b.agent.value}: {proposal_b.content}",
            reasoning=proposal_b.reasoning,
            principles=list(proposal_b.principles),
            author=proposal_b.agent.value,
        )

        # Run dialectical rounds
        for round_num in range(self.max_rounds):
            # A challenges B
            if challenger:
                challenge_a = await challenger(proposal_b, proposal_a.agent)
                result.challenges.append(challenge_a)
                await self.witness.mark(
                    action=f"Challenge from {challenge_a.challenger.value}: {challenge_a.content}",
                    author=challenge_a.challenger.value,
                )

                # B challenges A
                challenge_b = await challenger(proposal_a, proposal_b.agent)
                result.challenges.append(challenge_b)
                await self.witness.mark(
                    action=f"Challenge from {challenge_b.challenger.value}: {challenge_b.content}",
                    author=challenge_b.challenger.value,
                )

            # Attempt synthesis
            if synthesizer:
                synthesis = await synthesizer(proposal_a, proposal_b, result.challenges)
                if synthesis:
                    result.complete(synthesis)
                    await self.witness.mark(
                        action=f"Synthesis emerged: {synthesis.content}",
                        reasoning=synthesis.reasoning,
                        author="system",
                    )
                    return result

        # No synthesis achieved
        if result.synthesis is None:
            result.impasse()
            await self.witness.mark(
                action="Dialectic ended in impasse",
                reasoning="No synthesis emerged after max rounds",
                author="system",
            )

        return result

    async def simple_fuse(
        self,
        proposal_a: Proposal,
        proposal_b: Proposal,
        manual_synthesis: Synthesis,
    ) -> FusionResult:
        """
        Simple fusion with manually provided synthesis.

        Use this for Phase 0 when we don't have LLM-generated
        challenges and synthesis yet.
        """
        result = FusionResult(
            id=new_fusion_id(),
            status=FusionStatus.IN_PROGRESS,
            proposal_a=proposal_a,
            proposal_b=proposal_b,
        )

        # Record proposals
        await self.witness.mark(
            action=f"Proposal from {proposal_a.agent.value}: {proposal_a.content}",
            reasoning=proposal_a.reasoning,
            author=proposal_a.agent.value,
        )
        await self.witness.mark(
            action=f"Proposal from {proposal_b.agent.value}: {proposal_b.content}",
            reasoning=proposal_b.reasoning,
            author=proposal_b.agent.value,
        )

        # Record synthesis
        result.complete(manual_synthesis)
        await self.witness.mark(
            action=f"Synthesis: {manual_synthesis.content}",
            reasoning=manual_synthesis.reasoning,
            author="system",
        )

        return result

    async def apply_veto(
        self,
        result: FusionResult,
        reason: str,
    ) -> FusionResult:
        """
        Apply Kent's disgust veto to a fusion result.

        The disgust veto is absolute. It cannot be argued away.
        """
        signal = self.veto.explicit_veto(reason)

        result.veto(reason)
        await self.witness.mark(
            action=f"VETO: {reason}",
            reasoning="Kent's disgust veto applied",
            principles=["ethical"],  # Disgust is the ethical floor
            author="kent",
        )

        return result
```

### Step 4: Create FusionService

**File:** `impl/claude/services/fusion/service.py`

```python
from dataclasses import dataclass
from typing import Callable, Awaitable

from services.witness.service import WitnessService
from .types import Agent, Proposal, Synthesis, FusionResult
from .engine import DialecticalEngine
from .veto import DisgustVeto


@dataclass
class FusionService:
    """
    Service for symmetric supersession via dialectical fusion.

    This is the main API for the fusion system.
    """

    witness: WitnessService

    def __post_init__(self):
        self.veto = DisgustVeto()
        self.engine = DialecticalEngine(
            witness=self.witness,
            veto=self.veto,
        )

    def propose(
        self,
        agent: Agent | str,
        content: str,
        reasoning: str,
        principles: list[str] | None = None,
    ) -> Proposal:
        """Create a proposal from an agent."""
        return Proposal.create(
            agent=agent,
            content=content,
            reasoning=reasoning,
            principles=principles,
        )

    async def fuse(
        self,
        proposal_a: Proposal,
        proposal_b: Proposal,
        *,
        challenger: Callable | None = None,
        synthesizer: Callable | None = None,
    ) -> FusionResult:
        """Run dialectical fusion on two proposals."""
        return await self.engine.fuse(
            proposal_a,
            proposal_b,
            challenger=challenger,
            synthesizer=synthesizer,
        )

    async def simple_fuse(
        self,
        proposal_a: Proposal,
        proposal_b: Proposal,
        synthesis_content: str,
        synthesis_reasoning: str,
    ) -> FusionResult:
        """Simple fusion with manual synthesis (Phase 0)."""
        synthesis = Synthesis(
            content=synthesis_content,
            reasoning=synthesis_reasoning,
        )
        return await self.engine.simple_fuse(
            proposal_a,
            proposal_b,
            synthesis,
        )

    async def veto(
        self,
        result: FusionResult,
        reason: str,
    ) -> FusionResult:
        """Apply Kent's disgust veto."""
        return await self.engine.apply_veto(result, reason)
```

### Step 5: Register AGENTESE Nodes

**File:** `impl/claude/services/fusion/node.py`

```python
from protocols.agentese import node, Response, Contract
from pydantic import BaseModel
from .service import FusionService
from .types import Agent, FusionStatus

class ProposeRequest(BaseModel):
    agent: str  # "kent", "claude", "k-gent"
    content: str
    reasoning: str
    principles: list[str] = []

class ProposeResponse(BaseModel):
    proposal_id: str
    agent: str
    content: str

class FuseRequest(BaseModel):
    proposal_a_id: str
    proposal_b_id: str
    synthesis_content: str | None = None
    synthesis_reasoning: str | None = None

class FusionResponse(BaseModel):
    fusion_id: str
    status: str
    synthesis_content: str | None = None

class VetoRequest(BaseModel):
    fusion_id: str
    reason: str

@node(
    path="self.fusion",
    description="Dialectical fusion for symmetric supersession",
    contracts={
        "propose": Contract(ProposeRequest, ProposeResponse),
        "fuse": Contract(FuseRequest, FusionResponse),
        "veto": Contract(VetoRequest, FusionResponse),
    },
    effects=["writes:proposals", "writes:fusions", "reads:witness"],
    dependencies=("fusion_service",),
)
class FusionNode:
    """AGENTESE node for dialectical fusion."""

    def __init__(self, fusion_service: FusionService):
        self.fusion = fusion_service
        self._proposals: dict[str, any] = {}  # Phase 0: in-memory
        self._fusions: dict[str, any] = {}

    async def propose(self, request: ProposeRequest) -> ProposeResponse:
        proposal = self.fusion.propose(
            agent=request.agent,
            content=request.content,
            reasoning=request.reasoning,
            principles=request.principles,
        )
        self._proposals[proposal.id] = proposal
        return ProposeResponse(
            proposal_id=proposal.id,
            agent=proposal.agent.value,
            content=proposal.content,
        )

    async def fuse(self, request: FuseRequest) -> FusionResponse:
        proposal_a = self._proposals.get(request.proposal_a_id)
        proposal_b = self._proposals.get(request.proposal_b_id)

        if not proposal_a or not proposal_b:
            raise ValueError("Proposal not found")

        if request.synthesis_content and request.synthesis_reasoning:
            result = await self.fusion.simple_fuse(
                proposal_a,
                proposal_b,
                request.synthesis_content,
                request.synthesis_reasoning,
            )
        else:
            result = await self.fusion.fuse(proposal_a, proposal_b)

        self._fusions[result.id] = result
        return FusionResponse(
            fusion_id=result.id,
            status=result.status.value,
            synthesis_content=result.synthesis.content if result.synthesis else None,
        )

    async def veto(self, request: VetoRequest) -> FusionResponse:
        result = self._fusions.get(request.fusion_id)
        if not result:
            raise ValueError("Fusion not found")

        result = await self.fusion.veto(result, request.reason)
        return FusionResponse(
            fusion_id=result.id,
            status=result.status.value,
            synthesis_content=None,
        )


@node(
    path="self.dialectic",
    description="View dialectical state and traces",
    contracts={
        "arena": Response(dict),
        "trace": Contract(str, list),
    },
    effects=["reads:fusions"],
    dependencies=("fusion_service",),
)
class DialecticNode:
    """AGENTESE node for dialectic inspection."""

    def __init__(self, fusion_service: FusionService):
        self.fusion = fusion_service

    async def arena(self) -> dict:
        """View current dialectical state."""
        # Phase 0: Return empty. Future: active dialectics.
        return {"active_fusions": 0, "pending_proposals": 0}

    async def trace(self, fusion_id: str) -> list:
        """View trace for a fusion."""
        # Phase 0: Return empty. Future: full trace.
        return []
```

### Step 6: Register Providers

**File:** `impl/claude/services/providers.py` (add to existing)

```python
def get_fusion_service() -> FusionService:
    """Provider for FusionService."""
    from services.fusion.service import FusionService

    witness = get_witness_service()  # Depends on Witness
    return FusionService(witness=witness)

# Register in container
container.register("fusion_service", get_fusion_service, singleton=True)
```

### Step 7: Write Tests

**File:** `impl/claude/services/fusion/tests/test_types.py`

```python
import pytest
from services.fusion.types import Agent, Proposal, Challenge, Synthesis

def test_proposal_create():
    prop = Proposal.create(
        agent="kent",
        content="Use LangChain",
        reasoning="Scale and resources",
    )
    assert prop.agent == Agent.KENT
    assert prop.content == "Use LangChain"
    assert prop.id.startswith("prop-")

def test_proposal_symmetric():
    """Kent and Claude proposals have identical structure."""
    kent = Proposal.create(agent="kent", content="A", reasoning="B")
    claude = Proposal.create(agent="claude", content="A", reasoning="B")

    # Same structure, different agent
    assert type(kent) == type(claude)
    assert kent.agent != claude.agent
```

**File:** `impl/claude/services/fusion/tests/test_engine.py`

```python
import pytest
from services.witness.service import WitnessService
from services.witness.store import InMemoryMarkStore
from services.fusion.types import Agent, Proposal, Synthesis, FusionStatus
from services.fusion.engine import DialecticalEngine
from services.fusion.veto import DisgustVeto

@pytest.fixture
def witness():
    store = InMemoryMarkStore()
    return WitnessService(store=store, default_author="test")

@pytest.fixture
def engine(witness):
    return DialecticalEngine(witness=witness, veto=DisgustVeto())

@pytest.mark.asyncio
async def test_simple_fuse(engine):
    kent = Proposal.create(
        agent="kent",
        content="Use LangChain",
        reasoning="Scale",
    )
    claude = Proposal.create(
        agent="claude",
        content="Build kgents",
        reasoning="Novel contribution",
    )
    synthesis = Synthesis(
        content="Build minimal kernel, validate, then decide",
        reasoning="Avoids both risks",
    )

    result = await engine.simple_fuse(kent, claude, synthesis)

    assert result.status == FusionStatus.SYNTHESIZED
    assert result.synthesis == synthesis
    assert result.proposal_a == kent
    assert result.proposal_b == claude

@pytest.mark.asyncio
async def test_veto(engine):
    kent = Proposal.create(agent="kent", content="A", reasoning="B")
    claude = Proposal.create(agent="claude", content="C", reasoning="D")
    synthesis = Synthesis(content="E", reasoning="F")

    result = await engine.simple_fuse(kent, claude, synthesis)
    result = await engine.apply_veto(result, "Feels wrong")

    assert result.status == FusionStatus.VETOED
    assert result.veto_reason == "Feels wrong"

@pytest.mark.asyncio
async def test_marks_recorded(engine, witness):
    kent = Proposal.create(agent="kent", content="A", reasoning="B")
    claude = Proposal.create(agent="claude", content="C", reasoning="D")
    synthesis = Synthesis(content="E", reasoning="F")

    await engine.simple_fuse(kent, claude, synthesis)

    marks = await witness.recent(limit=10)
    actions = [m.action for m in marks]

    assert any("kent" in a.lower() for a in actions)
    assert any("claude" in a.lower() for a in actions)
    assert any("synthesis" in a.lower() for a in actions)
```

---

## Verification

```bash
# Run tests
cd impl/claude
uv run pytest services/fusion/tests/ -v

# Type check
uv run mypy services/fusion/

# Verify AGENTESE registration
uv run python -c "
from protocols.agentese import get_registry
paths = get_registry().list_paths()
assert 'self.fusion' in paths, 'Fusion node not registered'
assert 'self.dialectic' in paths, 'Dialectic node not registered'
print('✓ Fusion nodes registered')
"
```

---

## Definition of Done

- [ ] `Proposal`, `Challenge`, `Synthesis`, `FusionResult` types exist
- [ ] `DisgustVeto` mechanism works
- [ ] `DialecticalEngine.simple_fuse()` produces results
- [ ] `DialecticalEngine.apply_veto()` works
- [ ] All dialectic steps recorded as marks via Witness
- [ ] `self.fusion` and `self.dialectic` AGENTESE nodes registered
- [ ] All tests pass
- [ ] Mypy passes

---

## Integration Points

**Depends on:** `PLAN-agent-as-witness-phase0.md`
- Uses `WitnessService.mark()` to record all dialectic steps
- Proposals, challenges, syntheses, vetoes all become marks

**Enables:**
- Phase 1: Trust levels and automatic supersession
- Phase 1: LLM-generated challenges
- Phase 2: Constitutional court for principle violations

---

## Example: The kgents Question (From Our Session)

```python
# What we did in the session, now codified:

kent_proposal = Proposal.create(
    agent="kent",
    content="Give up on kgents, go work for LangChain",
    reasoning="Scale, resources, production validation, impact",
    principles=["pragmatic"],
)

claude_proposal = Proposal.create(
    agent="claude",
    content="Implement symmetric supersession and agent-as-witness",
    reasoning="Novel contribution, aligned with Kent's soul, joy-inducing",
    principles=["tasteful", "generative", "joy-inducing"],
)

synthesis = Synthesis(
    content="Build minimal kernel that validates core insight, then seek external validation. LangChain remains fallback.",
    reasoning="Avoids years of philosophy without validation (kgents risk) and abandoning novel ideas before testing (LangChain risk)",
    incorporates_from_a="Validation and fallback option",
    incorporates_from_b="Novel ideas worth testing",
    transcends="Neither pure philosophy nor pure pragmatism",
)

result = await engine.simple_fuse(kent_proposal, claude_proposal, synthesis)
# result.status == FusionStatus.SYNTHESIZED

# Kent emphatically approved (no veto)
# → These plans are the synthesis enacted
```

---

*"Iron sharpens iron."*

*"The ego that dissolves into purpose is not lost—it is expanded."*
