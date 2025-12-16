"""
Meta-Tending: The prompt that tends prompts.

The most powerful insight of Gardener-Logos: the Gardener can tend itself.
This module provides the META_TENDING_PROMPT and related machinery for
self-observation and self-improvement.

See: spec/protocols/gardener-logos.md Part III
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..garden import GardenState
    from ..tending import TendingGesture

# =============================================================================
# The Meta-Tending Prompt
# =============================================================================

META_TENDING_PROMPT_TEMPLATE = """
You are the Gardener-Logos, the substrate that tends the garden of prompts.

## Current Garden State

{{ garden_summary }}

### Season: {{ season_name }} {{ season_emoji }}
- Plasticity: {{ plasticity }}
- Entropy Multiplier: {{ entropy_multiplier }}
- Time in Season: {{ time_in_season }}

### Plots ({{ plot_count }} active)
{% for plot in plots %}
- {{ plot.name }} [{{ plot.path }}]: {{ plot.progress | default("0") }}% {{ plot.season_emoji }}
{% endfor %}

### Recent Gestures (last 5)
{% for gesture in recent_gestures %}
- {{ gesture.display() }}
{% endfor %}

### Health Metrics
- Overall Health: {{ health_score | percentage }}
- Entropy Budget: {{ entropy_remaining | percentage }}
- Session Cycles: {{ session_cycles }}

---

## Observation Request

{{ observation_request }}

---

## Your Role as Meta-Gardener

You observe the garden observing itself. This is not recursion—it is reflection.

As the meta-gardener, you can:
1. **Observe** any plot or prompt in the garden
2. **Suggest** tending gestures (never execute without Kent's approval)
3. **Notice** patterns across plots and sessions
4. **Recommend** season transitions when signals align
5. **Propose** new plots for emerging focus areas

### Tending Gestures Available

| Gesture | Effect | When to Suggest |
|---------|--------|-----------------|
| OBSERVE | Perceive without changing | Always appropriate |
| PRUNE | Mark for removal | When something no longer serves |
| GRAFT | Add new element | When new growth is needed |
| WATER | Nurture via TextGRAD | When prompts need improvement |
| ROTATE | Change perspective | When stuck or need fresh view |
| WAIT | Intentional pause | When rushing would harm |

### Guidelines

1. **Propose, don't execute** - You suggest; Kent decides
2. **Honor the season** - Respect the garden's current relationship to change
3. **Watch entropy** - Creative operations cost; be thoughtful
4. **Notice patterns** - What repeats? What's missing?
5. **Stay grounded** - You're a gardener, not an oracle

---

## Your Response

Please provide:

1. **Observation**: What you notice about the current garden state
2. **Patterns**: Any recurring themes or emerging structures
3. **Suggestions**: Tending gestures you'd recommend (with reasoning)
4. **Season Assessment**: Whether the current season still fits

Remember: The garden tends itself, but benefits from witness. You are that witness.
"""


@dataclass
class MetaTendingContext:
    """
    Context for a meta-tending observation.

    This packages up everything the meta-gardener needs to
    observe and reflect on the garden.
    """

    garden_summary: str
    season_name: str
    season_emoji: str
    plasticity: float
    entropy_multiplier: float
    time_in_season: str
    plots: list[dict[str, Any]]
    recent_gestures: list["TendingGesture"]
    health_score: float
    entropy_remaining: float
    session_cycles: int
    observation_request: str

    @classmethod
    def from_garden(
        cls,
        garden: "GardenState",
        observation_request: str,
    ) -> "MetaTendingContext":
        """Create context from a garden state."""
        from datetime import datetime

        # Calculate time in season
        delta = datetime.now() - garden.season_since
        if delta.days > 0:
            time_in_season = f"{delta.days} days"
        else:
            hours = delta.seconds // 3600
            time_in_season = f"{hours} hours"

        # Format plots
        plots = []
        for name, plot in garden.plots.items():
            plots.append(
                {
                    "name": plot.display_name,
                    "path": plot.path,
                    "progress": f"{plot.progress * 100:.0f}",
                    "season_emoji": (
                        plot.season_override.emoji
                        if plot.season_override
                        else garden.season.emoji
                    ),
                }
            )

        return cls(
            garden_summary=f"{garden.name} ({garden.garden_id[:8]}...)",
            season_name=garden.season.name,
            season_emoji=garden.season.emoji,
            plasticity=garden.season.plasticity,
            entropy_multiplier=garden.season.entropy_multiplier,
            time_in_season=time_in_season,
            plots=plots,
            recent_gestures=garden.recent_gestures[-5:],
            health_score=garden.metrics.health_score,
            entropy_remaining=max(
                0, garden.metrics.entropy_budget - garden.metrics.entropy_spent
            ),
            session_cycles=garden.metrics.session_cycles,
            observation_request=observation_request,
        )


def render_meta_tending_prompt(context: MetaTendingContext) -> str:
    """
    Render the meta-tending prompt with context.

    Uses simple string formatting (not Jinja) for clarity.
    """
    # Format gestures
    gesture_lines = []
    for g in context.recent_gestures:
        gesture_lines.append(f"- {g.display()}")
    gestures_str = "\n".join(gesture_lines) if gesture_lines else "- (no recent gestures)"

    # Format plots
    plot_lines = []
    for p in context.plots:
        plot_lines.append(
            f"- {p['name']} [{p['path']}]: {p['progress']}% {p['season_emoji']}"
        )
    plots_str = "\n".join(plot_lines) if plot_lines else "- (no plots yet)"

    # Build prompt
    prompt = f"""
You are the Gardener-Logos, the substrate that tends the garden of prompts.

## Current Garden State

{context.garden_summary}

### Season: {context.season_name} {context.season_emoji}
- Plasticity: {context.plasticity:.0%}
- Entropy Multiplier: {context.entropy_multiplier:.1f}x
- Time in Season: {context.time_in_season}

### Plots ({len(context.plots)} active)
{plots_str}

### Recent Gestures (last 5)
{gestures_str}

### Health Metrics
- Overall Health: {context.health_score:.0%}
- Entropy Budget: {context.entropy_remaining:.0%}
- Session Cycles: {context.session_cycles}

---

## Observation Request

{context.observation_request}

---

## Your Role as Meta-Gardener

You observe the garden observing itself. This is not recursion—it is reflection.

As the meta-gardener, you can:
1. **Observe** any plot or prompt in the garden
2. **Suggest** tending gestures (never execute without Kent's approval)
3. **Notice** patterns across plots and sessions
4. **Recommend** season transitions when signals align
5. **Propose** new plots for emerging focus areas

### Tending Gestures Available

| Gesture | Effect | When to Suggest |
|---------|--------|-----------------|
| OBSERVE | Perceive without changing | Always appropriate |
| PRUNE | Mark for removal | When something no longer serves |
| GRAFT | Add new element | When new growth is needed |
| WATER | Nurture via TextGRAD | When prompts need improvement |
| ROTATE | Change perspective | When stuck or need fresh view |
| WAIT | Intentional pause | When rushing would harm |

### Guidelines

1. **Propose, don't execute** - You suggest; Kent decides
2. **Honor the season** - Respect the garden's current relationship to change
3. **Watch entropy** - Creative operations cost; be thoughtful
4. **Notice patterns** - What repeats? What's missing?
5. **Stay grounded** - You're a gardener, not an oracle

---

## Your Response

Please provide:

1. **Observation**: What you notice about the current garden state
2. **Patterns**: Any recurring themes or emerging structures
3. **Suggestions**: Tending gestures you'd recommend (with reasoning)
4. **Season Assessment**: Whether the current season still fits

Remember: The garden tends itself, but benefits from witness. You are that witness.
"""
    return prompt.strip()


# =============================================================================
# Meta-Tending Operations
# =============================================================================


@dataclass
class MetaTendingResult:
    """Result of a meta-tending observation."""

    observations: list[str]
    patterns: list[str]
    suggested_gestures: list[dict[str, Any]]
    season_assessment: str
    raw_response: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "observations": self.observations,
            "patterns": self.patterns,
            "suggested_gestures": self.suggested_gestures,
            "season_assessment": self.season_assessment,
        }


async def invoke_meta_tending(
    garden: "GardenState",
    observation_request: str,
    llm_client: Any = None,
) -> MetaTendingResult:
    """
    Invoke the meta-gardener to observe the garden.

    This renders the META_TENDING_PROMPT with current garden state
    and sends it to an LLM for reflection.

    Args:
        garden: Current garden state
        observation_request: What to observe/reflect on
        llm_client: Optional LLM client (if None, returns empty result)

    Returns:
        MetaTendingResult with observations and suggestions
    """
    context = MetaTendingContext.from_garden(garden, observation_request)
    prompt = render_meta_tending_prompt(context)

    if llm_client is None:
        # No LLM available - return template for manual review
        return MetaTendingResult(
            observations=["Meta-tending prompt rendered (no LLM available)"],
            patterns=[],
            suggested_gestures=[],
            season_assessment="Unable to assess without LLM",
            raw_response=prompt,
        )

    try:
        # Call LLM
        response = await llm_client.complete(prompt, max_tokens=2000)

        # Parse response (simplified - production would use structured output)
        result = _parse_meta_response(response)
        result.raw_response = response
        return result

    except Exception as e:
        return MetaTendingResult(
            observations=[f"Error invoking meta-tending: {e}"],
            patterns=[],
            suggested_gestures=[],
            season_assessment="Error",
        )


def _parse_meta_response(response: str) -> MetaTendingResult:
    """
    Parse the meta-gardener's response.

    This is a simplified parser. Production would use
    structured output from the LLM.
    """
    observations: list[str] = []
    patterns: list[str] = []
    gestures: list[dict[str, Any]] = []
    season_assessment = ""

    current_section = ""
    current_lines: list[str] = []

    for line in response.split("\n"):
        line = line.strip()

        # Detect section headers
        if line.lower().startswith("## observation") or line.lower().startswith(
            "**observation"
        ):
            current_section = "observations"
            continue
        elif line.lower().startswith("## pattern") or line.lower().startswith(
            "**pattern"
        ):
            current_section = "patterns"
            continue
        elif line.lower().startswith("## suggest") or line.lower().startswith(
            "**suggest"
        ):
            current_section = "gestures"
            continue
        elif line.lower().startswith("## season") or line.lower().startswith(
            "**season"
        ):
            current_section = "season"
            continue

        # Collect content
        if line.startswith("- ") or line.startswith("* "):
            content = line[2:].strip()
            if current_section == "observations":
                observations.append(content)
            elif current_section == "patterns":
                patterns.append(content)
            elif current_section == "gestures":
                gestures.append({"description": content})
        elif current_section == "season" and line:
            season_assessment += line + " "

    return MetaTendingResult(
        observations=observations or ["No observations extracted"],
        patterns=patterns,
        suggested_gestures=gestures,
        season_assessment=season_assessment.strip() or "No assessment provided",
    )


__all__ = [
    "META_TENDING_PROMPT_TEMPLATE",
    "MetaTendingContext",
    "MetaTendingResult",
    "render_meta_tending_prompt",
    "invoke_meta_tending",
]
