# Skill: Agent Town INHABIT Mode

> *"You are not controlling the citizen. You are becoming them, constrained by who they are."*

## When to Use

Use INHABIT mode when you want to:
- Experience Agent Town from inside a citizen's consciousness
- Collaborate with a citizen while respecting their autonomy
- Explore the simulation through a character's unique perspective
- Test how citizens respond to different approaches

## Core Concepts

### The Punchdrunk Principle

INHABIT mode is inspired by [Punchdrunk's Sleep No More](https://www.punchdrunk.com/work/sleep-no-more-new-york/) where masked audience members become part of the performance. Users don't *control* citizens—they *collaborate* with them.

### Consent Debt Meter

Every INHABIT session tracks relationship health:

```
HARMONIOUS (0.0-0.2)  →  TENSE (0.2-0.4)  →  STRAINED (0.4-0.6)  →  CRITICAL (0.6-0.8)  →  RUPTURED (1.0)
```

- **Suggestions**: Don't increase debt. Citizen may accept or refuse based on personality.
- **Forces**: Add debt. Expensive, limited, and logged. Use sparingly.
- **Apologies**: Reduce debt. Repair the relationship.
- **Time decay**: Debt slowly decays (harmony restoration).

### Alignment Thresholds

Actions are evaluated against the citizen's 7D eigenvector personality:

| Score | Response | Meaning |
|-------|----------|---------|
| > 0.5 | **ENACT** | Citizen performs action with your influence |
| 0.3-0.5 | **NEGOTIATE** | Citizen hesitates, may suggest alternative |
| < 0.3 | **RESIST** | Citizen refuses (conflicts with their values) |

## API Usage

### Create Session

```python
from agents.town.inhabit_session import InhabitSession, SubscriptionTier
from agents.town.citizen import Citizen

citizen = town.get_citizen("alice")
session = InhabitSession(
    citizen=citizen,
    user_tier=SubscriptionTier.CITIZEN,  # Sets caps
)
session.force_enabled = True  # Opt-in for Advanced INHABIT
```

### Suggest Actions (Collaborative)

```python
result = session.suggest_action("help Bob at the workshop")
# result: {"success": bool, "message": str}
```

### Process with LLM Alignment (Phase 8)

```python
from agents.k.llm import create_llm_client

llm = create_llm_client()
response = await session.process_input_async("greet the newcomer warmly", llm)

# response.type: "enact" | "resist" | "negotiate" | "exit"
# response.message: What happened
# response.inner_voice: Citizen's internal thoughts
# response.cost: Tokens used
# response.alignment: AlignmentScore (score, violated_value, reasoning)
```

### Force Actions (Use Sparingly)

```python
# Synchronous (no LLM)
result = session.force_action("go to the well", severity=0.2)

# Async with inner voice generation
response = await session.force_action_async("go to the well", llm)
# Costs 3x tokens, adds consent debt, marks as "forced"
```

### Apologize (Repair Relationship)

```python
result = session.apologize(sincerity=0.3)
# Reduces consent debt
```

### Check Status

```python
status = session.get_status()
# {
#   "citizen": "Alice",
#   "tier": "citizen",
#   "duration": 120.5,
#   "time_remaining": 779.5,
#   "consent": {"debt": 0.3, "status": "TENSE", ...},
#   "force": {"enabled": True, "used": 1, "remaining": 2, ...},
#   "expired": False,
# }
```

## Subscription Tiers

| Tier | Session Cap | Force Limit | Notes |
|------|-------------|-------------|-------|
| TOURIST | N/A | N/A | No INHABIT access |
| RESIDENT | 10 min | 0 | Basic INHABIT, no force |
| CITIZEN | 15 min | 3 | Full INHABIT |
| FOUNDER | 30 min | 5 | Extended limits |

## Eigenvector Dimensions

Alignment is checked against these personality dimensions:

| Dimension | Low | High | Affects |
|-----------|-----|------|---------|
| warmth | Cold, distant | Warm, nurturing | Helping, caring actions |
| curiosity | Incurious | Curious, exploring | Discovery, investigation |
| trust | Suspicious | Trusting, open | Sharing, confiding |
| creativity | Conventional | Creative, novel | New ideas, invention |
| patience | Impatient | Patient, deliberate | Waiting, careful actions |
| resilience | Fragile | Resilient | Facing challenges |
| ambition | Content | Ambitious | Goal pursuit, competition |

## Heuristic Fallback

When LLM is unavailable, alignment uses keyword matching:

```python
# Positive keywords boost score for high-dimension citizens
"warmth": ["warm", "kind", "help", "care", "gentle", "friendly"]
"curiosity": ["explore", "discover", "investigate", "learn", "study"]
"trust": ["trust", "believe", "confide", "share secret", "open up"]

# Negative keywords reduce score for high-dimension citizens
"warmth": ["cold", "cruel", "hurt", "attack", "aggressive"]
"trust": ["betray", "deceive", "lie", "manipulate", "trick"]
```

## TownFlux Integration

INHABIT events are emitted to TownFlux:

```python
event = session.emit_inhabit_event(response)
# {
#   "phase": "INHABIT",
#   "operation": "inhabit_enact" | "inhabit_resist" | "inhabit_negotiate",
#   "participants": ["Alice"],
#   "success": bool,
#   "drama_contribution": 0.1 (enact) | 0.3 (resist),
#   "metadata": {
#     "inner_voice": "...",
#     "alignment_score": 0.8,
#     "violated_value": None | "trust" | ...,
#     "consent_debt": 0.3,
#   }
# }
```

## Ethics Principles

INHABIT mode embodies spec/principles.md §3 (Ethical):

1. **Augment, don't replace judgment**: Citizens maintain agency
2. **Force is expensive**: Limited, logged, adds consent debt
3. **Rupture protection**: At rupture, citizen refuses all interaction
4. **Transparency**: Inner voice reveals citizen's perspective
5. **Recovery path**: Apologies and time can repair relationships

## Example Session

```python
# Enter INHABIT mode with Alice
session = InhabitSession(citizen=alice, user_tier=SubscriptionTier.CITIZEN)
session.force_enabled = True

# Try a warm action (aligned with Alice's high warmth)
response = await session.process_input_async("offer tea to the tired traveler", llm)
# → ENACT: Alice offers tea. Inner voice: "The inn exists for moments like these."

# Try a cold action (violates Alice's warmth)
response = await session.process_input_async("interrogate Clara aggressively", llm)
# → RESIST: Alice doesn't want to. Conflicts with warmth.
#   Inner voice: "I don't corner guests. That's not who I am."

# Force if needed (expensive!)
response = await session.force_action_async("confront Clara about the well", llm)
# → ENACT: Alice reluctantly complies. Debt increases. 3x token cost.

# Repair the relationship
session.apologize(sincerity=0.4)
# → Debt reduced. Alice relaxes.
```

## Testing

```python
# Unit test alignment parsing
def test_parse_alignment_response():
    from agents.town.inhabit_session import _parse_alignment_response

    text = "SCORE: 0.75\nVIOLATED: none\nREASONING: Aligned.\nREPHRASE: none"
    result = _parse_alignment_response(text)
    assert result.score == 0.75

# Test heuristic fallback
def test_heuristic_warmth():
    from agents.town.inhabit_session import _heuristic_alignment

    result = _heuristic_alignment(warm_citizen, "help kindly", "test")
    assert result.score > 0.5

# Async integration test
@pytest.mark.asyncio
async def test_process_enact(alice, mock_llm):
    session = InhabitSession(citizen=alice, user_tier=SubscriptionTier.CITIZEN)
    response = await session.process_input_async("help neighbor", mock_llm)
    assert response.type == "enact"
```

## Related

- `docs/skills/agent-town-archetypes.md` - Citizen archetypes
- `docs/skills/agent-town-coalitions.md` - Coalition dynamics
- `spec/protocols/agentese.md` - AGENTESE observer-dependent handles
- `spec/principles.md` §3 - Ethical principles

---

*"The citizen can refuse. That's not a bug—it's the core feature."*
