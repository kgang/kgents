#!/usr/bin/env python3
"""
I-gents Demo: The Living Codex Garden

Demonstrates the fractal visualization scales:
1. Glyph (atom) - minimal phase indicator
2. Card (molecule) - agent with metadata
3. Page (composition) - agent relationships
4. Garden (ecosystem) - full system state
"""

from datetime import datetime, timedelta

from agents.i import (
    AgentState,
    CardRenderer,
    GardenRenderer,
    GardenState,
    Glyph,
    GlyphRenderer,
    MarginNote,
    NoteSource,
    PageRenderer,
    Phase,
)

print("=" * 70)
print(" " * 20 + "I-GENTS: THE LIVING CODEX GARDEN")
print("=" * 70)
print()

# ============================================================================
# SCALE 1: GLYPH (The Atom)
# ============================================================================
print("┌─ SCALE 1: GLYPH (The Atom) " + "─" * 40 + "┐")
print("│ The smallest unit: phase + identity" + " " * 31 + "│")
print("└" + "─" * 69 + "┘")
print()

phases = [
    (Phase.DORMANT, "robin-dormant", "Defined but sleeping"),
    (Phase.WAKING, "robin-waking", "Initializing or paused"),
    (Phase.ACTIVE, "robin-active", "Fully alive and ready"),
    (Phase.WANING, "robin-waning", "Completing or fading"),
    (Phase.EMPTY, "robin-error", "Error state or void"),
]

for phase, agent_id, description in phases:
    glyph = Glyph(agent_id=agent_id, phase=phase)
    renderer = GlyphRenderer(glyph)
    rendered = renderer.render()
    print(f"  {rendered:20s} # {description}")

print()

# ============================================================================
# SCALE 2: CARD (The Molecule)
# ============================================================================
print("┌─ SCALE 2: CARD (The Molecule) " + "─" * 36 + "┐")
print("│ Glyph + metadata (joy, ethics)" + " " * 36 + "│")
print("└" + "─" * 69 + "┘")
print()

# Create a few agent states with different metrics
now = datetime.now()
birth_time = now - timedelta(hours=2, minutes=34, seconds=12)

robin_state = AgentState(
    agent_id="B-robin",
    phase=Phase.ACTIVE,
    birth_time=birth_time,
    current_time=now,
    joy=0.9,
    ethics=0.85,
)

hegel_state = AgentState(
    agent_id="H-hegel",
    phase=Phase.WAKING,
    birth_time=now - timedelta(hours=1, minutes=15),
    current_time=now,
    joy=0.7,
    ethics=0.95,
)

robin_card = CardRenderer(robin_state)
print(robin_card.render())
print()
hegel_card = CardRenderer(hegel_state)
print(hegel_card.render())
print()

# ============================================================================
# SCALE 3: PAGE (Composition)
# ============================================================================
print("┌─ SCALE 3: PAGE (Composition) " + "─" * 37 + "┐")
print("│ Agent with margin notes and context" + " " * 31 + "│")
print("└" + "─" * 69 + "┘")
print()

robin_with_notes = AgentState(
    agent_id="B-robin",
    phase=Phase.ACTIVE,
    birth_time=birth_time,
    current_time=now,
    joy=0.9,
    ethics=0.85,
)

# Add margin notes (like a codex annotation)
notes = [
    MarginNote(
        timestamp=now - timedelta(minutes=5),
        source=NoteSource.SYSTEM,
        content="Morphism: Domain × Query → Narrative",
        agent_id="B-robin",
    ),
    MarginNote(
        timestamp=now - timedelta(minutes=2),
        source=NoteSource.SYSTEM,
        content="Composes: Persona >> Hypothesis >> Hegel",
        agent_id="B-robin",
    ),
    MarginNote(
        timestamp=now,
        source=NoteSource.SYSTEM,
        content="Last invoked: 2025-12-08 14:23:11",
        agent_id="B-robin",
    ),
]

# Add notes to the agent
robin_with_notes.margin_notes = notes

page_renderer = PageRenderer(robin_with_notes)
print(page_renderer.render())
print()

# ============================================================================
# SCALE 4: GARDEN (The Ecosystem)
# ============================================================================
print("┌─ SCALE 4: GARDEN (The Ecosystem) " + "─" * 33 + "┐")
print("│ All agents visible at once" + " " * 40 + "│")
print("└" + "─" * 69 + "┘")
print()

# Create a garden state with multiple agents
session_start = now - timedelta(hours=3)

agents = [
    # Bootstrap agents (always active)
    AgentState("Ground", Phase.ACTIVE, session_start, now, joy=1.0, ethics=1.0),
    AgentState("Contradict", Phase.ACTIVE, session_start, now, joy=0.9, ethics=0.95),
    AgentState("Sublate", Phase.ACTIVE, session_start, now, joy=0.95, ethics=0.95),
    # Genus implementations
    AgentState("A-abstract", Phase.ACTIVE, session_start, now, joy=0.8, ethics=0.9),
    AgentState("B-robin", Phase.ACTIVE, birth_time, now, joy=0.9, ethics=0.85),
    AgentState("C-functor", Phase.WAKING, session_start, now, joy=0.7, ethics=0.9),
    AgentState("D-volatile", Phase.ACTIVE, session_start, now, joy=0.85, ethics=0.8),
    AgentState("E-evolve", Phase.DORMANT, session_start, now, joy=0.6, ethics=0.9),
    AgentState("F-forge", Phase.WAKING, session_start, now, joy=0.8, ethics=0.85),
    AgentState("H-hegel", Phase.ACTIVE, session_start, now, joy=0.9, ethics=0.95),
    AgentState("J-jit", Phase.DORMANT, session_start, now, joy=0.7, ethics=0.75),
    AgentState("K-kent", Phase.WANING, session_start, now, joy=0.85, ethics=0.8),
    AgentState("L-library", Phase.ACTIVE, session_start, now, joy=0.8, ethics=0.9),
]

garden_state = GardenState(
    name="kgents-demo",
    session_start=session_start,
    current_time=now,
    agents={agent.agent_id: agent for agent in agents},
)

garden_renderer = GardenRenderer(garden_state)
print(garden_renderer.render())
print()

# ============================================================================
# AESTHETIC: BREATH CYCLE
# ============================================================================
print("┌─ AESTHETIC: BREATH CYCLE " + "─" * 41 + "┐")
print("│ Contemplative pacing for interface updates" + " " * 24 + "│")
print("└" + "─" * 69 + "┘")
print()

# The garden renderer includes breath visualization in real-time
print("The BreathCycle manages UI update timing:")
print("  - Inhale: Reading/loading phase")
print("  - Hold: Contemplation pause")
print("  - Exhale: Rendering/fading phase")
print()
print("This prevents interface violence—updates breathe, don't flash.")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 70)
print(" " * 25 + "FRACTAL SCALES SUMMARY")
print("=" * 70)
print()
print("  ● Glyph   (atom)       → Single character phase indicator")
print("  ● Card    (molecule)   → Glyph + metadata bars")
print("  ● Page    (document)   → Card + margin notes + composition")
print("  ● Garden  (ecosystem)  → All agents visible simultaneously")
print("  ● Library (archive)    → Historical snapshots + evolution")
print()
print("The same grammar visualizes atoms and galaxies.")
print()
print("=" * 70)
print(" " * 15 + '"The garden is the book; the book is the garden."')
print("=" * 70)
