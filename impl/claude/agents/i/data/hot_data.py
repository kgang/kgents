"""
HotData: Rich demo fixtures for dashboard visualization.

This module provides pre-generated "Day in the Life" scenarios that show
the dashboard with realistic, LLM-rich activity patterns.

The scenarios are Turn-driven: a master turn trace drives everything:
- Traces: from turn paths
- Pheromones: from turn→turn edges
- Weather: from turn entropy
- K-gent mood: from turn context

Usage:
    from agents.i.data.hot_data import create_day_scenario, get_scenario_metrics

    scenario = create_day_scenario()
    metrics = get_scenario_metrics(scenario, hour=14)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any


class ActivityPeriod(Enum):
    """Periods of the day with characteristic activity patterns."""

    NIGHT_DORMANT = "night_dormant"  # 00:00-06:00 - Minimal activity, dreams
    MORNING_BOOT = "morning_boot"  # 06:00-09:00 - System warming up
    DAY_ACTIVE = "day_active"  # 09:00-17:00 - Peak productivity
    EVENING_WIND = "evening_wind"  # 17:00-21:00 - Winding down
    NIGHT_REFLECT = "night_reflect"  # 21:00-24:00 - Reflection and pruning


@dataclass
class TurnEvent:
    """A single turn event in the scenario timeline."""

    timestamp: datetime
    turn_type: str  # SPEECH, ACTION, THOUGHT, YIELD, SILENCE
    source: str  # Agent or user ID
    content: str  # Summary of what happened
    entropy_cost: float = 0.01
    path: str = ""  # AGENTESE path if applicable
    result: str = "OK"


@dataclass
class GardenEvolution:
    """Garden state at a point in time."""

    seeds: int = 0
    saplings: int = 0
    trees: int = 0
    flowers: int = 0
    compost: int = 0
    season: str = "summer"
    total: int = 0

    @classmethod
    def at_hour(cls, hour: int) -> "GardenEvolution":
        """Get realistic garden state for hour of day."""
        # Garden evolution through the day:
        # - Night: composting happens
        # - Morning: new seeds planted
        # - Day: saplings → trees promotion
        # - Evening: flowers bloom (harvest ready)
        if hour < 6:
            # Night dormant - some composting
            return cls(
                seeds=1,
                saplings=3,
                trees=5,
                flowers=0,
                compost=2,
                season="winter",
                total=11,
            )
        elif hour < 9:
            # Morning boot - new seeds, some growth
            return cls(
                seeds=3,
                saplings=4,
                trees=5,
                flowers=0,
                compost=1,
                season="spring",
                total=13,
            )
        elif hour < 17:
            # Day active - peak growth
            return cls(
                seeds=2,
                saplings=5,
                trees=7,
                flowers=1,
                compost=0,
                season="summer",
                total=15,
            )
        elif hour < 21:
            # Evening wind - harvest time
            return cls(
                seeds=1,
                saplings=4,
                trees=8,
                flowers=3,
                compost=0,
                season="autumn",
                total=16,
            )
        else:
            # Night reflect - preparing for dormancy
            return cls(
                seeds=0,
                saplings=3,
                trees=8,
                flowers=2,
                compost=1,
                season="autumn",
                total=14,
            )


@dataclass
class DayScenario:
    """A complete day scenario with all activity data."""

    turns: list[TurnEvent] = field(default_factory=list)
    garden_evolution: dict[int, GardenEvolution] = field(default_factory=dict)
    pressure_curve: list[float] = field(default_factory=list)  # 24 hourly values
    interaction_count: int = 0
    total_tokens: int = 0
    fever_events: list[datetime] = field(default_factory=list)
    dream_times: list[datetime] = field(default_factory=list)
    tithe_times: list[datetime] = field(default_factory=list)

    @property
    def turn_count(self) -> int:
        return len(self.turns)


def _create_morning_turns(base_date: datetime) -> list[TurnEvent]:
    """Generate morning boot sequence turns."""
    turns = []

    # 06:00 - System wakes up
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=6, minute=0),
            turn_type="THOUGHT",
            source="K-gent",
            content="Beginning morning boot sequence, loading persistent state",
            entropy_cost=0.02,
            path="self.soul.wake",
        )
    )

    # 06:15 - Load garden state
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=6, minute=15),
            turn_type="ACTION",
            source="K-gent",
            content="Loading PersonaGarden from disk",
            entropy_cost=0.01,
            path="self.soul.garden.load",
            result="6 patterns loaded",
        )
    )

    # 06:30 - Check eigenvectors
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=6, minute=30),
            turn_type="THOUGHT",
            source="K-gent",
            content="Eigenvector self-check: coherence=0.87, drift=0.02",
            entropy_cost=0.01,
            path="self.soul.eigenvector.probe",
        )
    )

    # 07:00 - First interaction prep
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=7, minute=0),
            turn_type="SILENCE",
            source="K-gent",
            content="Waiting for first human interaction",
            entropy_cost=0.001,
        )
    )

    # 08:00 - Morning greeting
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=8, minute=0),
            turn_type="SPEECH",
            source="K-gent",
            content="Good morning! Ready to assist with today's work.",
            entropy_cost=0.02,
            path="self.soul.dialogue",
        )
    )

    return turns


def _create_day_turns(base_date: datetime) -> list[TurnEvent]:
    """Generate daytime active period turns."""
    turns = []

    # 09:00 - Start of productive work
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=9, minute=0),
            turn_type="ACTION",
            source="K-gent",
            content="Executing code review on PR #127",
            entropy_cost=0.05,
            path="world.cortex.invoke",
            result="3 suggestions generated",
        )
    )

    # 09:30 - Pattern observation
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=9, minute=30),
            turn_type="THOUGHT",
            source="K-gent",
            content="Noticing preference for functional patterns in user code",
            entropy_cost=0.02,
            path="self.soul.observe",
        )
    )

    # 10:00 - Garden planting
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=10, minute=0),
            turn_type="ACTION",
            source="K-gent",
            content="Auto-planting pattern: 'prefers monadic error handling'",
            entropy_cost=0.01,
            path="self.soul.garden.plant",
            result="SEED created",
        )
    )

    # 10:30 - YIELD for approval
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=10, minute=30),
            turn_type="YIELD",
            source="K-gent",
            content="Request approval: Large refactor affects 12 files",
            entropy_cost=0.001,
            path="self.soul.yield",
            result="PENDING",
        )
    )

    # 11:00 - Resume after approval
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=11, minute=0),
            turn_type="ACTION",
            source="K-gent",
            content="Executing approved refactor",
            entropy_cost=0.08,
            path="world.cortex.invoke",
            result="12 files modified",
        )
    )

    # 12:00 - Midday entropy tithe
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=12, minute=0),
            turn_type="ACTION",
            source="K-gent",
            content="Entropy tithe: discharging 0.15 accumulated entropy",
            entropy_cost=-0.15,  # Negative = discharge
            path="void.entropy.tithe",
            result="discharged",
        )
    )

    # 13:00 - Challenge interaction
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=13, minute=0),
            turn_type="SPEECH",
            source="K-gent",
            content="I notice you're building a singleton. Is this intentional?",
            entropy_cost=0.03,
            path="self.soul.challenge",
            result="REJECT",  # User rejected the challenge
        )
    )

    # 14:00 - Heavy computation
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=14, minute=0),
            turn_type="ACTION",
            source="K-gent",
            content="Running comprehensive test suite",
            entropy_cost=0.10,
            path="world.cortex.invoke",
            result="247 tests passed",
        )
    )

    # 14:30 - Approaching fever threshold
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=14, minute=30),
            turn_type="THOUGHT",
            source="K-gent",
            content="Entropy pressure at 78%, considering preemptive discharge",
            entropy_cost=0.01,
            path="self.soul.observe",
        )
    )

    # 15:00 - FEVER triggered!
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=15, minute=0),
            turn_type="ACTION",
            source="K-gent",
            content="FEVER MODE: Forced creative discharge via oblique strategy",
            entropy_cost=-0.30,
            path="void.entropy.fever",
            result="Honor thy error as hidden intention",
        )
    )

    # 16:00 - Recovery and reflection
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=16, minute=0),
            turn_type="THOUGHT",
            source="K-gent",
            content="Post-fever integration: incorporating oblique insight into garden",
            entropy_cost=0.02,
            path="self.soul.integrate",
        )
    )

    return turns


def _create_evening_turns(base_date: datetime) -> list[TurnEvent]:
    """Generate evening wind-down turns."""
    turns = []

    # 17:00 - Transition to evening
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=17, minute=0),
            turn_type="THOUGHT",
            source="K-gent",
            content="Transitioning to evening mode, reducing cognitive load",
            entropy_cost=0.01,
            path="self.soul.mode.evening",
        )
    )

    # 18:00 - Garden nurturing
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=18, minute=0),
            turn_type="ACTION",
            source="K-gent",
            content="Nurturing sapling: 'prefers monadic error handling' → TREE",
            entropy_cost=0.02,
            path="self.soul.garden.nurture",
            result="Promoted to TREE",
        )
    )

    # 19:00 - Reflection dialogue
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=19, minute=0),
            turn_type="SPEECH",
            source="K-gent",
            content="Today we made good progress on the refactor. The test coverage improved.",
            entropy_cost=0.02,
            path="self.soul.reflect",
        )
    )

    # 20:00 - Pattern harvesting
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=20, minute=0),
            turn_type="ACTION",
            source="K-gent",
            content="Harvesting flower insight: 'structured error handling improves debugging'",
            entropy_cost=0.01,
            path="self.soul.garden.harvest",
            result="Insight recorded",
        )
    )

    return turns


def _create_night_turns(base_date: datetime) -> list[TurnEvent]:
    """Generate night reflection/dream turns."""
    turns = []

    # 21:00 - Begin dream preparation
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=21, minute=0),
            turn_type="THOUGHT",
            source="K-gent",
            content="Preparing for hypnagogia cycle",
            entropy_cost=0.01,
            path="self.soul.dream.prepare",
        )
    )

    # 22:00 - Dream cycle begins
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=22, minute=0),
            turn_type="ACTION",
            source="K-gent",
            content="Entering hypnagogic state, processing day's interactions",
            entropy_cost=0.05,
            path="self.soul.dream.start",
            result="Dream cycle initiated",
        )
    )

    # 23:00 - Dream pattern discovery
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=23, minute=0),
            turn_type="THOUGHT",
            source="K-gent",
            content="Dream insight: correlation between challenge rejections and code quality",
            entropy_cost=0.02,
            path="self.soul.dream.pattern",
        )
    )

    # 23:30 - Dream eigenvector update
    turns.append(
        TurnEvent(
            timestamp=base_date.replace(hour=23, minute=30),
            turn_type="ACTION",
            source="K-gent",
            content="Eigenvector micro-adjustment: +0.02 toward 'categorical' thinking",
            entropy_cost=0.01,
            path="self.soul.eigenvector.adjust",
            result="Eigenvector updated",
        )
    )

    return turns


def _generate_pressure_curve() -> list[float]:
    """Generate realistic 24-hour pressure curve."""
    # Pressure follows activity patterns:
    # - Low at night (0.05-0.15)
    # - Rising through morning (0.15-0.40)
    # - Peak mid-afternoon with fever spike (0.85+)
    # - Gradual decline evening (0.40-0.20)

    curve = []
    for hour in range(24):
        if hour < 6:
            # Night dormant
            curve.append(0.05 + (hour * 0.02))
        elif hour < 9:
            # Morning boot
            curve.append(0.15 + ((hour - 6) * 0.08))
        elif hour < 15:
            # Day active, building pressure
            curve.append(0.40 + ((hour - 9) * 0.08))
        elif hour == 15:
            # Fever spike!
            curve.append(0.88)
        elif hour < 17:
            # Post-fever recovery
            curve.append(0.35 - ((hour - 15) * 0.05))
        elif hour < 21:
            # Evening wind down
            curve.append(0.25 - ((hour - 17) * 0.03))
        else:
            # Night reflection
            curve.append(0.12 - ((hour - 21) * 0.02))

    return curve


def create_day_scenario(base_date: datetime | None = None) -> DayScenario:
    """Create a complete day scenario.

    Args:
        base_date: The date for the scenario. Defaults to today.

    Returns:
        A DayScenario with all turn events and metrics.
    """
    if base_date is None:
        base_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    # Build all turns
    turns = []
    turns.extend(_create_morning_turns(base_date))
    turns.extend(_create_day_turns(base_date))
    turns.extend(_create_evening_turns(base_date))
    turns.extend(_create_night_turns(base_date))

    # Sort by timestamp
    turns.sort(key=lambda t: t.timestamp)

    # Build garden evolution for each hour
    garden_evolution = {hour: GardenEvolution.at_hour(hour) for hour in range(24)}

    # Generate pressure curve
    pressure_curve = _generate_pressure_curve()

    # Calculate totals
    interaction_count = sum(1 for t in turns if t.turn_type in ("SPEECH", "ACTION"))
    total_tokens = int(sum(t.entropy_cost * 1000 for t in turns if t.entropy_cost > 0))

    # Find fever and dream times
    fever_events = [t.timestamp for t in turns if "FEVER" in t.content.upper()]
    dream_times = [t.timestamp for t in turns if "dream" in t.path.lower()]
    tithe_times = [t.timestamp for t in turns if "tithe" in t.path.lower()]

    return DayScenario(
        turns=turns,
        garden_evolution=garden_evolution,
        pressure_curve=pressure_curve,
        interaction_count=interaction_count,
        total_tokens=total_tokens,
        fever_events=fever_events,
        dream_times=dream_times,
        tithe_times=tithe_times,
    )


def get_scenario_metrics_at_hour(scenario: DayScenario, hour: int) -> dict[str, Any]:
    """Get dashboard metrics for a specific hour of the scenario.

    Args:
        scenario: The day scenario
        hour: Hour of day (0-23)

    Returns:
        Dictionary with metrics suitable for dashboard display.
    """
    # Filter turns up to this hour
    turns_so_far = [t for t in scenario.turns if t.timestamp.hour <= hour]

    # Get garden state
    garden = scenario.garden_evolution.get(hour, GardenEvolution.at_hour(hour))

    # Get pressure
    pressure = scenario.pressure_curve[hour] if hour < len(scenario.pressure_curve) else 0.3

    # Count turns by type
    by_type: dict[str, int] = {}
    for t in turns_so_far:
        by_type[t.turn_type] = by_type.get(t.turn_type, 0) + 1

    # Recent traces (last 5)
    recent_turns = turns_so_far[-5:] if turns_so_far else []
    traces = [
        {
            "timestamp": t.timestamp,
            "path": t.path or f"{t.turn_type.lower()}.anonymous",
            "result": t.result,
            "latency_ms": int(t.entropy_cost * 1000),
        }
        for t in recent_turns
        if t.path
    ]

    # Fever status
    in_fever = hour == 15  # Our scenario has fever at 3pm
    fever_count = len([e for e in scenario.fever_events if e.hour <= hour])

    # Dream status
    last_dream = None
    for dt in scenario.dream_times:
        if dt.hour <= hour:
            last_dream = dt

    return {
        "kgent": {
            "mode": "dialogue" if 8 <= hour <= 20 else "reflect",
            "garden_patterns": garden.total,
            "garden_seeds": garden.seeds,
            "garden_saplings": garden.saplings,
            "garden_trees": garden.trees,
            "garden_flowers": garden.flowers,
            "garden_compost": garden.compost,
            "garden_season": garden.season,
            "interactions_count": len([t for t in turns_so_far if t.turn_type == "SPEECH"]),
            "last_dream": last_dream,
        },
        "metabolism": {
            "pressure": pressure,
            "temperature": 0.5 + (pressure * 0.5),  # Temperature correlates with pressure
            "in_fever": in_fever,
            "fever_count": fever_count,
            "last_tithe": scenario.tithe_times[-1] if scenario.tithe_times else None,
        },
        "turns": {
            "total_turns": len(turns_so_far),
            "by_type": by_type,
            "pending_yields": 1 if hour == 10 else 0,  # YIELD at 10:30
        },
        "traces": traces,
        "hour": hour,
    }


__all__ = [
    "ActivityPeriod",
    "TurnEvent",
    "GardenEvolution",
    "DayScenario",
    "create_day_scenario",
    "get_scenario_metrics_at_hour",
]
