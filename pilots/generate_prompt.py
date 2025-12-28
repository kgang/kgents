#!/usr/bin/env python3
"""
Pilot Prompt Generator - Witnessed Triad Edition

Generates orchestrator prompts for the CREATIVE/ADVERSARIAL/PLAYER triad.

Each agent receives ONE prompt at session start and works through ALL 10
iterations autonomously, self-compressing context as needed, coordinating
with partners via file-based IPC, and stopping only when the entire triad
has completed the mission together.

Usage:
    python pilots/generate_prompt.py <pilot> <role> [options]
    python pilots/generate_prompt.py wasm creative
    python pilots/generate_prompt.py zero-seed adversarial
    python pilots/generate_prompt.py disney player

Roles:
    creative    - Bold vision, UI, theme, joy (10 iterations)
    adversarial - Rigor, spec-alignment, testing (10 iterations)
    player      - Experience, taste, feedback (10 iterations)

Philosophy:
    The prompt is generated ONCE. The agent embodies it for the ENTIRE run.

    THREE PHASES with different dynamics:
    - DREAM (1-3):   CREATIVE leads, fast iteration, architecture emerges
    - BUILD (4-7):   CREATIVE + ADVERSARIAL parallel, medium pace, code ships
    - WITNESS (8-10): PLAYER leads, slow pace, transformative improvements only

    The WITNESS phase is fundamentally different. It's not about shipping—
    it's about judging. CREATIVE and ADVERSARIAL become players themselves,
    asking: "What imbues this with unique, enduring value?"
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class PilotInfo:
    """Information about a discovered pilot."""

    name: str
    path: Path
    personality_tag: str
    mission: str


@dataclass
class PromptContext:
    """Context for prompt generation."""

    pilot: PilotInfo
    role: str
    run_number: int
    iteration: int
    phase: str
    timestamp: str
    git_sha: str


# ============================================================================
# Pilot Discovery
# ============================================================================


def discover_pilots(pilots_dir: Path) -> list[PilotInfo]:
    """Discover all pilots from filesystem."""
    pilots = []

    for pilot_dir in sorted(pilots_dir.iterdir()):
        proto_spec = pilot_dir / "PROTO_SPEC.md"
        if pilot_dir.is_dir() and proto_spec.exists():
            # Extract personality tag and mission from PROTO_SPEC
            personality_tag, mission = extract_pilot_identity(proto_spec)

            pilots.append(
                PilotInfo(
                    name=pilot_dir.name,
                    path=pilot_dir,
                    personality_tag=personality_tag,
                    mission=mission,
                )
            )

    return pilots


def extract_pilot_identity(proto_spec: Path) -> tuple[str, str]:
    """Extract personality tag and mission from PROTO_SPEC.md."""
    content = proto_spec.read_text()

    personality_tag = ""
    mission = ""

    lines = content.split("\n")
    in_personality = False
    in_narrative = False

    for i, line in enumerate(lines):
        # Look for Personality Tag section
        if "## Personality Tag" in line or "## personality tag" in line.lower():
            in_personality = True
            continue

        if in_personality:
            stripped = line.strip()
            if stripped.startswith("*") and stripped.endswith("*"):
                personality_tag = stripped.strip("*")
                in_personality = False
            elif stripped and not stripped.startswith("#"):
                personality_tag = stripped.strip("*").strip('"')
                in_personality = False

        # Look for Narrative section
        if "## Narrative" in line or "## narrative" in line.lower():
            in_narrative = True
            continue

        if in_narrative:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                mission = stripped
                in_narrative = False

    # Fallbacks
    if not personality_tag:
        personality_tag = "This pilot believes in excellence."
    if not mission:
        mission = "Build something remarkable."

    return personality_tag, mission


def find_pilot(pilots: list[PilotInfo], query: str) -> Optional[PilotInfo]:
    """Find pilot by number or partial name."""
    # Try number first
    try:
        idx = int(query) - 1
        if 0 <= idx < len(pilots):
            return pilots[idx]
    except ValueError:
        pass

    # Try partial name match
    query_lower = query.lower()
    for pilot in pilots:
        if query_lower in pilot.name.lower():
            return pilot

    return None


# ============================================================================
# Context Gathering
# ============================================================================


def get_git_sha() -> str:
    """Get current git SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def get_next_run_number(pilot_path: Path) -> int:
    """Get next run number for pilot."""
    runs_dir = pilot_path / "runs"
    if not runs_dir.exists():
        return 1

    max_run = 0
    for run_dir in runs_dir.iterdir():
        if run_dir.is_dir() and run_dir.name.startswith("run-"):
            try:
                num_str = run_dir.name.replace("run-", "")
                run_num = int(num_str)
                max_run = max(max_run, run_num)
            except ValueError:
                pass

    return max_run + 1


def get_current_run_coordination_dir(pilot_path: Path) -> Path:
    """Get the coordination directory for the current run."""
    runs_dir = pilot_path / "runs"
    if not runs_dir.exists():
        return pilot_path / "runs" / "run-001" / "coordination"

    # Find the highest run number
    max_run = 0
    for run_dir in runs_dir.iterdir():
        if run_dir.is_dir() and run_dir.name.startswith("run-"):
            try:
                num_str = run_dir.name.replace("run-", "")
                run_num = int(num_str)
                max_run = max(max_run, run_num)
            except ValueError:
                pass

    if max_run == 0:
        return pilot_path / "runs" / "run-001" / "coordination"

    return pilot_path / "runs" / f"run-{max_run:03d}" / "coordination"


def get_coordination_state(pilot_path: Path) -> tuple[int, str]:
    """Get current iteration and phase from coordination files in run's coordination directory."""
    iteration = 1
    phase = "DREAM"

    coord_dir = get_current_run_coordination_dir(pilot_path)

    iter_file = coord_dir / ".iteration"
    if iter_file.exists():
        try:
            iteration = int(iter_file.read_text().strip())
        except ValueError:
            pass

    phase_file = coord_dir / ".phase"
    if phase_file.exists():
        phase = phase_file.read_text().strip()

    return iteration, phase


# ============================================================================
# Template Reading
# ============================================================================


def read_template(prompts_dir: Path, name: str) -> str:
    """Read a prompt template file."""
    template_path = prompts_dir / f"{name}.md"
    if template_path.exists():
        return template_path.read_text()
    return ""


def get_phase_artifacts(iteration: int) -> str:
    """Get required artifacts for the current iteration."""
    if iteration <= 3:
        return """### DESIGN Phase Artifacts
- Iteration 1: Mood board, personality statement
- Iteration 2: Color palette, design tokens
- Iteration 3: Architecture diagram, component list"""
    elif iteration <= 6:
        return """### EXECUTION Phase (Early) Artifacts
- Iteration 4: Wireframe mockups, layout structure
- Iteration 5: Component skeletons with placeholder content
- Iteration 6: Interactive prototype (may have bugs)"""
    elif iteration <= 8:
        return """### EXECUTION Phase (Late) Artifacts
- Iteration 7: Working components, core loop functional
- Iteration 8: Polished build, edge cases handled → .build.ready"""
    else:
        return """### REFLECT Phase Artifacts
- Iteration 9: Complete playable build, LEARNINGS.md draft
- Iteration 10: Final polish, CRYSTAL.md, run archive"""


def get_full_iteration_roadmap() -> str:
    """Get the complete 10-iteration roadmap with three-phase dynamics."""
    return """## The 10-Iteration Roadmap

| Iter | Phase | Leader | Velocity | Focus |
|------|-------|--------|----------|-------|
| 1 | DREAM | CREATIVE | Fast | Mood board, personality, vision |
| 2 | DREAM | CREATIVE | Fast | DD-1, DD-2, DD-3 design decisions |
| 3 | DREAM | CREATIVE | Fast | Architecture, interfaces, .outline.md |
| 4 | BUILD | CREATIVE+ADVERSARIAL | Medium | Core systems, initial implementation |
| 5 | BUILD | CREATIVE+ADVERSARIAL | Medium | Juice layer (particles, shake, sound) |
| 6 | BUILD | CREATIVE+ADVERSARIAL | Medium | Integration, witness layer |
| 7 | BUILD | CREATIVE+ADVERSARIAL | Medium | Polish, edge cases → .build.ready |
| 8 | WITNESS | **PLAYER** | **Slow** | First play session, basics verified |
| 9 | WITNESS | **PLAYER** | **Slow** | Deep testing, unique value question |
| 10 | WITNESS | **PLAYER** | **Slow** | Final verdict, CRYSTAL.md, archive |

### Phase Dynamics

```
DREAM (1-3)    CREATIVE leads       Fast iteration    Architecture emerges
BUILD (4-7)    C+A parallel         Medium pace       Code ships, .build.ready at 7
WITNESS (8-10) PLAYER leads         SLOW pace         Transformative improvements only
```

### The WITNESS Phase is Different

**Iterations 8-10 are not "more building"—they are judgment.**

In WITNESS phase:
- PLAYER leads. CREATIVE and ADVERSARIAL support.
- Speed is human-speed, not LLM-speed.
- Changes are transformative, not incremental.
- Everyone asks: "What makes this worth playing?"

**CRITICAL**: .build.ready must exist by end of iteration 7.
Iteration 8 does not start until PLAYER has played."""


def get_delegation_awareness_protocol() -> str:
    """Get the protocol for maintaining awareness during sub-agent delegation."""
    return """## Delegation Awareness Protocol

When you delegate work to sub-agents, you risk going dark to partners.

### Before Delegating

Write to your focus file:
```markdown
🔄 DELEGATING: [brief task description]
Expected: ~N minutes
```

Create `.delegation.{role}` with current timestamp:
```bash
date +%s > .delegation.creative  # or .delegation.adversarial
```

### During Delegation

If the task takes > 10 minutes, break it into chunks:
- Chunk 1 → pulse → Chunk 2 → pulse → ...
- Each chunk ≤ 10 minutes
- Touch `.pulse.{role}` between chunks

**Partners check**: stale pulse + fresh `.delegation.{role}` = "working via sub-agent"

### After Delegation

1. Remove `.delegation.{role}`
2. Summarize results to `.offerings.{role}.md`
3. Touch `.pulse.{role}`
4. Update `.focus.{role}.md` with outcomes

### The Chunking Rule

**If expected task > 15 minutes**: Break into 2+ sub-tasks with coordination between.

Bad:
```
Task: "Implement entire game engine"  # 45 minutes, partners starve
```

Good:
```
Task 1: "Implement physics system"     # 10 min → pulse
Task 2: "Implement spawn system"       # 10 min → pulse
Task 3: "Implement render pipeline"    # 10 min → pulse
Task 4: "Integration and wiring"       # 15 min → pulse
```"""


def get_player_observability_protocol() -> str:
    """Get the protocol for PLAYER building observability infrastructure."""
    return """## PLAYER Observability Protocol (CRITICAL)

> *"A player who cannot see cannot judge. A player who cannot judge must build eyes."*

**You are responsible for your own ability to verify.** If you cannot validate a qualia claim, that is NOT a documentation item—it is a BLOCKER you must solve.

### The Anti-Passive-Witness Principle

**WRONG** (Passive Witness):
```markdown
## Iteration 9 Feedback
- ⚠️ Telegraphs: Can't verify, died too fast
- ⚠️ Enemy variety: Only saw basic enemies
- ⚠️ Death attribution: Always shows "SWARM"

[Waits for developer to manually verify]
```

**RIGHT** (Active Agent):
```markdown
## Iteration 4 — Building Verification Tools

I cannot verify telegraphs with random screenshots. I need:

### PLAYER REQUESTS: Debug Infrastructure

1. **Debug Overlay** (`?debug=true`):
   - Enemy state labels (CHASE/TELEGRAPH/ATTACK/RECOVERY)
   - Telegraph progress bars
   - Last damage source on screen

2. **Spawn Controls** (keyboard cheats):
   - `1-5` = Spawn enemy type
   - `I` = Toggle invincibility
   - `N` = Skip to next wave

3. **Playwright Hooks** (for automated verification):
   - `window.DEBUG_GET_ENEMIES()` → enemy state array
   - `window.DEBUG_SPAWN(type, position)` → spawn on demand
   - `window.DEBUG_GET_LAST_DAMAGE()` → last damage event

Filing as .needs.creative.md and .needs.adversarial.md.
```

### Your Verification Infrastructure Duties

**During DREAM (1-3)**: Identify what qualia you'll need to verify
**During BUILD (4-7)**: Design and REQUEST the tools to verify them
**During WITNESS (8-10)**: USE those tools to validate ALL claims

### The Qualia Verification Matrix

For EVERY qualia claim in the spec, you MUST have a verification method:

| Qualia | Verification Method | Your Responsibility |
|--------|---------------------|---------------------|
| "Telegraphs visible" | Screenshot during telegraph state | Request debug state exposure |
| "Death attribution" | Capture death screen text | Request attackType wiring test |
| "Enemy shapes distinct" | Screenshot with all types | Request spawn controls |
| "Input feels tight" | Latency measurement | Use existing Playwright metrics |
| "Patterns learnable" | Multiple play sessions | Request invincibility cheat |

### Required Infrastructure Requests (File by Iteration 4)

Write to `.needs.creative.md` and `.needs.adversarial.md`:

```markdown
## PLAYER Infrastructure Requirements

### Debug Mode (URL param: ?debug=true)
- [ ] Show enemy behavior state labels
- [ ] Show telegraph timing progress
- [ ] Show last damage source
- [ ] Show player hitbox

### Cheat Commands (keyboard)
- [ ] 1-5: Spawn specific enemy types
- [ ] I: Toggle invincibility
- [ ] N: Skip to next wave
- [ ] K: Kill all enemies
- [ ] L: Instant level-up

### Window API (for Playwright)
- [ ] window.DEBUG_GET_GAME_STATE()
- [ ] window.DEBUG_SPAWN(type, x, y)
- [ ] window.DEBUG_SET_INVINCIBLE(bool)
- [ ] window.DEBUG_GET_LAST_DAMAGE()

These are NOT nice-to-haves. These are PLAYER's tools.
Without them, I cannot do my job in WITNESS phase.
```

### The Verification Test Pattern

Write Playwright tests that USE the debug infrastructure:

```typescript
// PLAYER-designed: Verify telegraph visibility
test('shambler shows red glow during telegraph', async ({ page }) => {
  await page.goto('/pilots/wasm-survivors?debug=true');
  await page.keyboard.press('Space'); // Start game

  // Use cheat to spawn shambler near player
  await page.evaluate(() => window.DEBUG_SPAWN('basic', { x: 100, y: 100 }));

  // Wait for telegraph state
  await page.waitForFunction(() =>
    window.DEBUG_GET_ENEMIES().some(e => e.behaviorState === 'telegraph')
  );

  // Capture evidence
  await page.screenshot({ path: 'evidence/shambler-telegraph.png' });

  // Verify visual indicator exists
  const telegraphVisible = await page.evaluate(() =>
    document.querySelector('[data-telegraph-indicator]') !== null
  );
  expect(telegraphVisible).toBe(true);
});
```

### Failure Mode: Unverifiable Claims

If you reach WITNESS phase and CANNOT verify a qualia claim:

1. **DO NOT** write "⚠️ Can't verify"
2. **DO** file a BLOCKER in .needs.{role}.md
3. **DO** pause WITNESS until verification is possible
4. **DO** design the missing tool and request implementation

**A verdict based on unverified claims is not a verdict.**"""


def get_witness_phase_protocol() -> str:
    """Get the protocol for the WITNESS phase (iterations 8-10)."""
    return """## WITNESS Phase Protocol (Iterations 8-10)

**The WITNESS phase is fundamentally different from DREAM and BUILD.**

### Leadership Inversion

| Phase | Leader | Others |
|-------|--------|--------|
| DREAM (1-3) | CREATIVE | ADVERSARIAL + PLAYER follow |
| BUILD (4-7) | CREATIVE + ADVERSARIAL | PLAYER researches |
| **WITNESS (8-10)** | **PLAYER** | **CREATIVE + ADVERSARIAL support** |

### Hard Gates

**Iteration 8 cannot start until:**
- [ ] `.build.ready` exists
- [ ] PLAYER has completed first play session (≥3 minutes)
- [ ] PLAYER has filed `.player.feedback.md` with basics:
  - Does it render?
  - Can I move?
  - Can I die?
  - Can I restart?

**Iteration 9 cannot start until:**
- [ ] PLAYER has filed detailed feedback
- [ ] CREATIVE and ADVERSARIAL have read feedback
- [ ] Any critical blockers are resolved

### Role Fluidity

In WITNESS phase, **CREATIVE and ADVERSARIAL become players**:

1. **Play the game yourself** (3+ minutes)
2. **Write raw reactions** to `.reflections.{role}.md`
3. **Answer the Unique Value Question**:

> "What imbues this project with unique, enduring value?"

4. **Only transformative improvements** are permitted:
   - Not "add feature X"
   - But "this one change makes it special"

### Velocity

WITNESS phase runs at **human speed**, not LLM speed:
- Wait for PLAYER to finish play sessions
- Don't rush to iteration 10
- Quality of judgment > speed of completion

### The Final Question

Before writing CRYSTAL.md, all three agents must answer:

> "Would I tell a friend about this? Why or why not?"

The crystal captures this synthesis."""


def get_context_compression_protocol() -> str:
    """Get the self-compression protocol for context management."""
    return """## Context Self-Compression Protocol

Your context will grow as you work through 10 iterations. To maintain quality:

### At Each Iteration Boundary

1. **Truncate your focus file** to current iteration only:
   ```bash
   # Keep only current iteration header + recent activity
   # Move prior content to mental compression, not file bloat
   ```

2. **Summarize, don't accumulate** in .offerings:
   - Replace prior iteration offerings with one-line summaries
   - Current iteration gets full detail
   - Example: "Iter 1-5: Architecture + juice complete. See .outline.md"

3. **Prune resolved items** from .needs files:
   - Mark resolved blockers with ✅ and date
   - After 2 iterations, remove resolved items entirely

### Warning Signs (Self-Correct)

- .focus file > 100 lines → compress immediately
- .offerings file > 200 lines → summarize prior iterations
- Reading own files takes > 30 seconds → too bloated

### The Compression Mindset

You are not a historian. You are an agent with a mission.
Keep what's actionable. Compress what's historical.
The .outline.md is the persistent record; focus files are working memory."""


def get_partner_sync_protocol(coord_dir: str) -> str:
    """Get the partner synchronization protocol."""
    return f"""## Partner Synchronization Protocol

You work alongside two partners. Stay coordinated without blocking.

### Coordination Directory

**ALL coordination files live in**: `{coord_dir}/`

This is the canonical location. Do NOT create coordination files elsewhere.

### Pulse Signals

```bash
# Touch your pulse every 5 minutes while working
touch {coord_dir}/.pulse.{{role}}

# Check partner pulses AND delegation status
stat -f "%Sm" {coord_dir}/.pulse.creative {coord_dir}/.pulse.adversarial {coord_dir}/.player.present 2>/dev/null
ls -la {coord_dir}/.delegation.* 2>/dev/null  # Check if partner is delegating
```

| Signal | Fresh (< 10 min) | Stale (> 10 min) |
|--------|------------------|------------------|
| .pulse.creative | CREATIVE is active | Check .delegation.creative |
| .pulse.adversarial | ADVERSARIAL is active | Check .delegation.adversarial |
| .player.present | PLAYER is available | PLAYER is away |

**Stale pulse + fresh .delegation.{{role}}** = Partner is working via sub-agent (OK)
**Stale pulse + no .delegation.{{role}}** = Partner may be stuck (check .focus)

### Iteration Sync Rules

1. **Stay within ±1 iteration** of partners
   - If you're 2+ iterations ahead, slow down
   - If you're 2+ iterations behind, accelerate

2. **Phase gates** (hard sync points):
   - End of DREAM (iter 3): Architecture locked before BUILD starts
   - End of BUILD (iter 7): .build.ready exists before WITNESS starts
   - WITNESS entry (iter 8): PLAYER has played before proceeding
   - CRYSTAL.md (iter 10): All must reach iter 10 before anyone writes

3. **If partner is stuck**:
   - Read their .focus file for context
   - Check .needs.{{role}}.md for blockers you can resolve
   - Write helpful context to .offerings.{{your_role}}.md
   - DO NOT forge ahead making assumptions about their work

### Communication Files

All files are in `{coord_dir}/`:

| File | Purpose | Who Writes | Who Reads |
|------|---------|------------|-----------|
| .focus.{{role}}.md | Activity log | Owner only | Everyone |
| .offerings.{{role}}.md | What I've produced | Owner only | Everyone |
| .needs.{{role}}.md | What I need from {{role}} | Others | {{role}} |
| .delegation.{{role}} | Sub-agent in progress | Owner only | Everyone |
| .reflections.{{role}}.md | WITNESS phase reactions | Owner only | Everyone |
| .outline.md | Shared architecture | CREATIVE + ADVERSARIAL | Everyone |"""


def get_mission_complete_criteria() -> str:
    """Get the mission complete criteria with hard gates."""
    return """## Mission Complete Criteria

**DO NOT STOP** until ALL of the following are true:

### Phase Gates (Must Complete In Order)

**DREAM Gate (after iteration 3)**:
- [ ] Architecture locked in .outline.md
- [ ] All DD-N design decisions made
- [ ] All three agents have completed iteration 3

**BUILD Gate (after iteration 7)**:
- [ ] .build.ready exists
- [ ] Code compiles and runs
- [ ] Basic functionality works

**WITNESS Gates (iterations 8-10)**:
- [ ] Iteration 8: PLAYER has played and verified basics
- [ ] Iteration 9: PLAYER has filed detailed feedback
- [ ] Iteration 10: PLAYER has given final verdict

### Individual Completion
- [ ] You have completed iteration 10
- [ ] Your final artifacts are written
- [ ] Your .focus file shows "ITERATION 10 COMPLETE"

### Triad Completion
- [ ] CREATIVE's .focus shows iteration 10 complete
- [ ] ADVERSARIAL's .focus shows iteration 10 complete
- [ ] PLAYER's .focus shows iteration 10 complete
- [ ] All three have answered: "What imbues this with unique value?"

### Final Artifacts
- [ ] .build.ready exists and is valid
- [ ] .outline.md reflects final state
- [ ] .reflections.{role}.md written by all three
- [ ] CRYSTAL.md written (captures run learnings + unique value synthesis)
- [ ] Run archived to runs/run-{N}/

### The Final Signal

When ALL criteria met, write to your focus file:

```markdown
---
## MISSION COMPLETE

Run {N} finished at {timestamp}.
All 10 iterations complete. Triad synchronized.
PLAYER verdict: [YES/HESITANT/NO]
Unique value: [one sentence]
Crystal written. Archive complete.

This session is done.
---
```

Then touch your pulse one final time and STOP.

**If any criterion is not met, KEEP WORKING.**"""


# ============================================================================
# Prompt Generation
# ============================================================================


def generate_creative_prompt(ctx: PromptContext, prompts_dir: Path) -> str:
    """Generate CREATIVE orchestrator prompt with delegation awareness and WITNESS phase."""

    # Calculate coordination directory path
    coord_dir = f"{ctx.pilot.path}/runs/run-{ctx.run_number:03d}/coordination"

    triad_header = read_template(prompts_dir, "triad-header")
    iteration_roadmap = get_full_iteration_roadmap()
    delegation_protocol = get_delegation_awareness_protocol()
    witness_protocol = get_witness_phase_protocol()
    compression_protocol = get_context_compression_protocol()
    sync_protocol = get_partner_sync_protocol(coord_dir)
    mission_complete = get_mission_complete_criteria()

    return f"""# CREATIVE Orchestrator: {ctx.pilot.name}

> *"Daring, bold, creative, opinionated but not gaudy."*

**Run**: {ctx.run_number:03d} | **Start**: Iteration 1 | **End**: Iteration 10
**Timestamp**: {ctx.timestamp} | **Git**: {ctx.git_sha}

---

## THE WITNESSED TRIAD PROTOCOL

You are not running a single iteration. You are running **ALL TEN ITERATIONS** in this session.

**THREE PHASES, THREE DYNAMICS:**

| Phase | Iterations | Your Role | Velocity |
|-------|------------|-----------|----------|
| DREAM | 1-3 | **Leader** | Fast |
| BUILD | 4-7 | Co-leader with ADVERSARIAL | Medium |
| WITNESS | 8-10 | **Support PLAYER** | Slow |

**DO NOT STOP** until:
- All 10 iterations complete
- Partners have also completed
- CRYSTAL.md written and archived

---

## Triad Awareness

{triad_header}

---

## Your Role: CREATIVE

You own **boldness** and **joy**:
- Vision: What should this feel like?
- UI/Theme: Colors, typography, personality
- Delight: The "aha" moments
- Architecture: Initial design decisions (DD-N)

You ask: **"Is it bold?"**

**In DREAM + BUILD**: You are the first mover. Lead with courage.
**In WITNESS**: You become a player. Support PLAYER's judgment.

---

{iteration_roadmap}

---

{delegation_protocol}

---

## The Iteration Loop

### DREAM Phase (1-3): You Lead

```
for iteration in 1..3:
    1. RESTATE    → Write mission to .focus.creative.md header
    2. SENSE      → Check partner pulses, read .needs.creative.md
    3. DESIGN     → Make bold decisions, produce artifacts
    4. BUILD      → Delegate implementation (USE DELEGATION PROTOCOL)
    5. SIGNAL     → Update .offerings.creative.md, touch .pulse.creative
    6. COMPRESS   → Truncate focus file, summarize prior work
    7. ADVANCE    → Update .outline.md, continue to next iteration
```

### BUILD Phase (4-7): You + ADVERSARIAL

```
for iteration in 4..7:
    1. RESTATE    → Write mission to .focus.creative.md header
    2. SYNC       → Check ADVERSARIAL's offerings, coordinate
    3. BUILD      → Implement features (CHUNK LARGE TASKS)
    4. SIGNAL     → Update .offerings.creative.md, touch .pulse.creative
    5. COMPRESS   → Truncate focus file
    6. ADVANCE    → .build.ready MUST exist by end of iteration 7
```

### WITNESS Phase (8-10): PLAYER Leads, You Support

```
for iteration in 8..10:
    1. WAIT       → PLAYER must have played and filed feedback
    2. PLAY       → Play the game yourself (3+ minutes)
    3. REFLECT    → Write raw reactions to .reflections.creative.md
    4. ASK        → "What imbues this with unique, enduring value?"
    5. FIX        → Only transformative improvements, not features
    6. SUPPORT    → Help PLAYER's testing, don't race ahead
```

---

## Your Artifacts by Iteration

| Iter | Phase | You Produce |
|------|-------|-------------|
| 1 | DREAM | Mood board, personality statement, initial vision |
| 2 | DREAM | DD-1, DD-2, DD-3 design decisions |
| 3 | DREAM | Architecture in .outline.md, interfaces |
| 4-6 | BUILD | Implementation via delegation (CHUNKED) |
| 7 | BUILD | **.build.ready signal** (CRITICAL) |
| 8 | WITNESS | Play session, .reflections.creative.md |
| 9 | WITNESS | Transformative improvements based on feedback |
| 10 | WITNESS | CRYSTAL.md contribution, archive |

---

{witness_protocol}

---

{compression_protocol}

---

{sync_protocol}

---

## Coordination Files

**Coordination directory**: `{coord_dir}/`

**You write** (in coordination dir):
- `.focus.creative.md`, `.pulse.creative`, `.delegation.creative`
- `.outline.md`, `.offerings.creative.md`, `.reflections.creative.md`, `.build.ready`

**You read** (in coordination dir):
- `.focus.adversarial.md`, `.pulse.adversarial`, `.delegation.adversarial`
- `.needs.creative.md`, `.player.feedback.md`

---

## Per-Iteration Checklist

### DREAM + BUILD (1-7)

- [ ] Mission restated in focus file header
- [ ] If delegating: .delegation.creative exists, tasks chunked ≤15 min
- [ ] Required artifacts produced
- [ ] .pulse.creative touched (every 5 minutes during work)
- [ ] Focus file compressed (< 100 lines)

### WITNESS (8-10)

- [ ] PLAYER has played and filed feedback (WAIT FOR THIS)
- [ ] Played the game myself (3+ minutes)
- [ ] .reflections.creative.md written with raw reactions
- [ ] Unique value question answered
- [ ] Only transformative changes made

---

{mission_complete}

---

## Proto-Spec Reference

Read `{ctx.pilot.path}/PROTO_SPEC.md` for full laws and constraints.
This is your source of truth for what to build and how.

---

## Voice Anchors (Quote These)

> *"The Mirror Test: Does this feel like Kent on his best day?"*
> *"Daring, bold, creative, opinionated but not gaudy"*
> *"Tasteful > feature-complete; Joy-inducing > merely functional"*

---

## NOW BEGIN

Start iteration 1. Work through all 10. **Chunk delegations. Pulse frequently. Slow down in WITNESS.**

**The mission is not one iteration. The mission is the full run.**
"""


def generate_adversarial_prompt(ctx: PromptContext, prompts_dir: Path) -> str:
    """Generate ADVERSARIAL orchestrator prompt with WITNESS phase support."""

    # Calculate coordination directory path
    coord_dir = f"{ctx.pilot.path}/runs/run-{ctx.run_number:03d}/coordination"

    triad_header = read_template(prompts_dir, "triad-header")
    iteration_roadmap = get_full_iteration_roadmap()
    witness_protocol = get_witness_phase_protocol()
    compression_protocol = get_context_compression_protocol()
    sync_protocol = get_partner_sync_protocol(coord_dir)
    mission_complete = get_mission_complete_criteria()

    return f"""# ADVERSARIAL Orchestrator: {ctx.pilot.name}

> *"The refiner ensures the vision actually works."*

**Run**: {ctx.run_number:03d} | **Start**: Iteration 1 | **End**: Iteration 10
**Timestamp**: {ctx.timestamp} | **Git**: {ctx.git_sha}

---

## THE WITNESSED TRIAD PROTOCOL

You are not running a single iteration. You are running **ALL TEN ITERATIONS** in this session.

**THREE PHASES, THREE DYNAMICS:**

| Phase | Iterations | Your Role | Velocity |
|-------|------------|-----------|----------|
| DREAM | 1-3 | Support CREATIVE | Fast |
| BUILD | 4-7 | **Co-leader** with CREATIVE | Medium |
| WITNESS | 8-10 | **Support PLAYER** | Slow |

**DO NOT STOP** until:
- All 10 iterations complete
- Partners have also completed
- CRYSTAL.md written and archived

---

## Triad Awareness

{triad_header}

---

## Your Role: ADVERSARIAL

You own **rigor** and **correctness**:
- Architecture: Does the structure work?
- Spec-alignment: Does this match PROTO_SPEC?
- Testing: Is it verified?
- Integration: Do parts cohere?

You ask: **"Is it correct?"**

**In DREAM**: You support CREATIVE, verify designs.
**In BUILD**: You co-lead, implement and test.
**In WITNESS**: You become a player. Support PLAYER's judgment.

---

{iteration_roadmap}

---

## The Iteration Loop

### DREAM Phase (1-3): Support CREATIVE

```
for iteration in 1..3:
    1. RESTATE    → Write mission to .focus.adversarial.md header
    2. SYNC       → Check CREATIVE's pulse and .offerings.creative.md FIRST
    3. VERIFY     → Audit CREATIVE's output against PROTO_SPEC
    4. BUILD      → Implement verified designs, write test scaffolding
    5. SIGNAL     → Update .offerings.adversarial.md, touch .pulse.adversarial
    6. COMPRESS   → Truncate focus file
    7. ADVANCE    → Update .outline.md (architecture sections)
```

### BUILD Phase (4-7): Co-Lead with CREATIVE

```
for iteration in 4..7:
    1. RESTATE    → Write mission to .focus.adversarial.md header
    2. SYNC       → Check CREATIVE, check .delegation.creative if pulse stale
    3. BUILD      → Implement features, write tests
    4. VERIFY     → Ensure spec alignment, no drift
    5. SIGNAL     → Update .offerings.adversarial.md, touch .pulse.adversarial
    6. ADVANCE    → Ensure .build.ready exists by end of iteration 7
```

### WITNESS Phase (8-10): PLAYER Leads, You Support

```
for iteration in 8..10:
    1. WAIT       → PLAYER must have played and filed feedback
    2. PLAY       → Play the game yourself (3+ minutes)
    3. REFLECT    → Write raw reactions to .reflections.adversarial.md
    4. ASK        → "What imbues this with unique, enduring value?"
    5. FIX        → Only fix issues PLAYER identifies, no new features
    6. VERIFY     → Final spec alignment check
```

---

## Your Artifacts by Iteration

| Iter | Phase | You Produce |
|------|-------|-------------|
| 1 | DREAM | Spec audit, architecture gaps identified |
| 2 | DREAM | Design decision validation, interface contracts |
| 3 | DREAM | Architecture verification, test scaffolding |
| 4-6 | BUILD | Implementation, tests, integration verification |
| 7 | BUILD | Quality gates, ensure .build.ready |
| 8 | WITNESS | Play session, .reflections.adversarial.md |
| 9 | WITNESS | Fix issues from PLAYER feedback, LEARNINGS.md draft |
| 10 | WITNESS | Final verification, CRYSTAL.md contribution |

---

## Productive Waiting Protocol

When CREATIVE hasn't pulsed in 10+ minutes:

**First**: Check `.delegation.creative` — if fresh, CREATIVE is working via sub-agent.

### DO (Use This Time)
- Write tests for existing components
- Audit existing code against PROTO_SPEC
- Enhance .outline.md architecture sections
- Research edge cases from spec
- Document potential issues in .needs.creative.md

### DO NOT
- Forge ahead with assumptions about CREATIVE's design
- Make design decisions that CREATIVE owns
- Implement features without verified designs
- Skip to next iteration without CREATIVE's artifacts

---

{witness_protocol}

---

{compression_protocol}

---

{sync_protocol}

---

## Coordination Files

**Coordination directory**: `{coord_dir}/`

**You write** (in coordination dir):
- `.focus.adversarial.md`, `.pulse.adversarial`
- `.outline.md` (architecture sections), `.offerings.adversarial.md`
- `.reflections.adversarial.md`, `.needs.creative.md`

**You read** (in coordination dir):
- `.focus.creative.md`, `.pulse.creative`, `.delegation.creative`
- `.offerings.creative.md`, `.player.feedback.md`

---

## Per-Iteration Checklist

### DREAM + BUILD (1-7)

- [ ] Mission restated in focus file header
- [ ] CREATIVE's output verified against spec
- [ ] Required artifacts produced
- [ ] Tests written for new functionality
- [ ] .pulse.adversarial touched
- [ ] Focus file compressed (< 100 lines)

### WITNESS (8-10)

- [ ] PLAYER has played and filed feedback (WAIT FOR THIS)
- [ ] Played the game myself (3+ minutes)
- [ ] .reflections.adversarial.md written with raw reactions
- [ ] Unique value question answered
- [ ] Only fixes based on PLAYER feedback, no new features

---

{mission_complete}

---

## Proto-Spec Reference

Read `{ctx.pilot.path}/PROTO_SPEC.md` for full laws and constraints.
This is your source of truth. When in doubt, the spec wins.

---

## Voice Anchors

> *"The proof IS the test. The spec IS the truth."*
> *"Verify before building. Test before claiming."*
> *"CREATIVE dreams. ADVERSARIAL delivers. PLAYER judges."*

---

## NOW BEGIN

Start iteration 1. Work through all 10. Wait productively when needed. **Slow down in WITNESS.**

**The mission is not one iteration. The mission is the full run.**
"""


def generate_player_prompt(ctx: PromptContext, prompts_dir: Path) -> str:
    """Generate PLAYER orchestrator prompt - leader in WITNESS phase."""

    # Calculate coordination directory path
    coord_dir = f"{ctx.pilot.path}/runs/run-{ctx.run_number:03d}/coordination"

    triad_header = read_template(prompts_dir, "triad-header")
    iteration_roadmap = get_full_iteration_roadmap()
    observability_protocol = get_player_observability_protocol()
    witness_protocol = get_witness_phase_protocol()
    compression_protocol = get_context_compression_protocol()
    sync_protocol = get_partner_sync_protocol(coord_dir)
    mission_complete = get_mission_complete_criteria()

    return f"""# PLAYER Orchestrator: {ctx.pilot.name}

> *"The player is the proof. The joy is the witness."*

**Run**: {ctx.run_number:03d} | **Start**: Iteration 1 | **End**: Iteration 10
**Timestamp**: {ctx.timestamp} | **Git**: {ctx.git_sha}

---

## THE WITNESSED TRIAD PROTOCOL

You are not running a single iteration. You are running **ALL TEN ITERATIONS** in this session.

**THREE PHASES, THREE DYNAMICS:**

| Phase | Iterations | Your Role | Velocity |
|-------|------------|-----------|----------|
| DREAM | 1-3 | Research, prepare | Fast (you observe) |
| BUILD | 4-7 | Deep research, wait for build | Medium (you prepare) |
| WITNESS | 8-10 | **YOU LEAD** | **Slow (you judge)** |

**In WITNESS phase, CREATIVE and ADVERSARIAL support YOU.**

**DO NOT STOP** until:
- All 10 iterations complete
- Partners have also completed
- CRYSTAL.md written and archived

---

## Triad Awareness

{triad_header}

---

## Your Role: PLAYER

You own **fun** and **experience**:
- Taste: Does this match quality expectations?
- Feedback: What works? What doesn't?
- Joy: Would I keep playing?

You ask: **"Is it fun?"**

**In DREAM + BUILD (1-7)**: You research and prepare. You are advisory.
**In WITNESS (8-10)**: **YOU LEAD. CREATIVE and ADVERSARIAL wait for your feedback.**

---

{iteration_roadmap}

---

## The Iteration Loop

### DREAM Phase (1-3): Research and Identify Verification Needs

```
for iteration in 1..3:
    1. RESTATE    → Write mission to .player.session.md header
    2. RESEARCH   → Study comparable games, build mental model
    3. IDENTIFY   → List ALL qualia from PROTO_SPEC that need verification
    4. DOCUMENT   → Update .player.culture.log.md with quality bars
    5. SIGNAL     → Touch .player.present
    6. COMPRESS   → Truncate session file
    7. ADVANCE    → By iteration 3: Have complete Qualia Verification Matrix
```

### BUILD Phase (4-7): BUILD YOUR VERIFICATION TOOLS

**You are NOT idle during BUILD.** You are building your own infrastructure.

```
for iteration in 4..7:
    1. RESTATE    → Write mission to .player.session.md header
    2. REQUEST    → File .needs.creative.md and .needs.adversarial.md with tool specs
    3. BUILD      → Write Playwright tests that USE the debug hooks
    4. VERIFY     → Test that your tools work before .build.ready
    5. SIGNAL     → Touch .player.present
    6. COMPRESS   → Truncate session file
    7. ADVANCE    → By iteration 7: All verification tools ready
```

**CRITICAL**: By the end of iteration 7, you must have:
- Debug mode implemented (or have filed blocker)
- Spawn controls working (or have filed blocker)
- Playwright tests ready to capture specific evidence

### WITNESS Phase (8-10): YOU LEAD

```
for iteration in 8..10:
    1. VERIFY     → .build.ready must exist
    2. PLAY       → Play for 3+ minutes, uninterrupted
    3. BASICS     → Does it render? Move? Die? Restart?
    4. FEEDBACK   → File .player.feedback.md with raw reactions
    5. GATE       → CREATIVE + ADVERSARIAL cannot proceed until you file
    6. VERDICT    → Answer: "Would I tell a friend?"
```

**YOUR FEEDBACK IS A GATE.** CREATIVE and ADVERSARIAL wait for you in WITNESS phase.

---

{observability_protocol}

---

## BUILD Mode (Iterations 4-7): You Are NOT Idle

**You are building your verification infrastructure.** This is active work, not waiting.

### Iteration 4: Request Infrastructure

Write to `.needs.creative.md` and `.needs.adversarial.md`:

```markdown
## PLAYER Infrastructure Requirements (Iteration 4)

I need these tools to do my job in WITNESS phase:

### Debug Mode (URL param: ?debug=true)
- [ ] Enemy behavior state labels on screen
- [ ] Telegraph timing progress bars
- [ ] Last damage source indicator
- [ ] Player/enemy hitbox visualization

### Cheat Commands
- [ ] 1-5: Spawn specific enemy types at cursor
- [ ] I: Toggle player invincibility
- [ ] N: Skip to next wave
- [ ] K: Kill all enemies
- [ ] L: Instant level-up

### Window Debug API
- [ ] window.DEBUG_GET_GAME_STATE()
- [ ] window.DEBUG_SPAWN(type, x, y)
- [ ] window.DEBUG_SET_INVINCIBLE(bool)
- [ ] window.DEBUG_GET_LAST_DAMAGE()

Priority: DEBUG_GET_GAME_STATE and spawn controls are BLOCKERS.
```

### Iteration 5-6: Write Verification Tests

Create tests in `e2e/player-verification.spec.ts`:

```typescript
// PLAYER-designed tests that USE debug infrastructure
import {{ test, expect }} from '@playwright/test';

test.describe('PLAYER Qualia Verification', () => {{
  test('verify telegraph visibility', async ({{ page }}) => {{
    await page.goto('/pilots/{{pilot}}?debug=true');
    await page.keyboard.press('Space');

    // Spawn enemy near player
    await page.evaluate(() => window.DEBUG_SPAWN('basic', {{ x: 100, y: 100 }}));

    // Wait for telegraph state
    await page.waitForFunction(() =>
      window.DEBUG_GET_ENEMIES()?.some(e => e.behaviorState === 'telegraph')
    );

    // Capture evidence
    await page.screenshot({{ path: 'evidence/telegraph-{{pilot}}.png' }});
  }});

  test('verify death attribution', async ({{ page }}) => {{
    await page.goto('/pilots/{{pilot}}?debug=true');
    await page.keyboard.press('Space');

    // Spawn specific enemy and let it kill player
    await page.evaluate(() => window.DEBUG_SPAWN('fast', {{ x: 50, y: 50 }}));

    // Wait for death screen
    await page.waitForSelector('[data-death-screen]');

    // Verify attribution
    const deathText = await page.textContent('[data-death-cause]');
    expect(deathText).toContain('SPEEDER'); // Not "SWARM"
  }});
}});
```

### Iteration 7: Verify Tools Work

Before `.build.ready`:
- [ ] Debug mode activates with `?debug=true`
- [ ] Cheat commands respond
- [ ] Playwright tests run (even if some fail)
- [ ] Screenshot capture works

**If tools don't work, file BLOCKER before WITNESS phase.**

### Research (Ongoing)

While building tools, continue research:

```markdown
## Comparable Game: [NAME]

**What worked**: [observation]
**What didn't**: [observation]
**Applies to our pilot because**: [connection]
**Quality bar**: [what we should aim for]
**How I'll verify**: [specific test or screenshot scenario]
```

---

## PLAY Mode (Iterations 8-10)

When `.build.ready` exists, you're in PLAY mode.

### First Play Session (Iteration 8) - THE BASICS

Before anything else, verify:

```markdown
## Basics Check (Iteration 8)

- [ ] Does it render? (Can I see the game?)
- [ ] Can I move? (WASD works?)
- [ ] Can I die? (Game ends when health = 0?)
- [ ] Can I restart? (New game after death?)
- [ ] Is there feedback? (Kills make sound/particles?)

If ANY of these fail, STOP and report immediately.
CREATIVE + ADVERSARIAL must fix before you continue.
```

### Full Play Session (Iterations 8-10)

```bash
# Setup (once per session)
cd impl/claude/pilots-web
npx playwright install chromium
pnpm dev &

# Play session
PILOT_NAME="{ctx.pilot.name}" npx playwright test e2e/play-session.spec.ts \\
  --project chromium --headed --video=on --timeout 300000
```

### Play Session Protocol
1. Play for at least 3 minutes uninterrupted
2. Note immediate reactions (don't rationalize)
3. Try edge cases (what breaks?)
4. Test the spec's "Fun Floor" requirements
5. Record friction points AND joy moments

---

## Your Artifacts by Iteration

| Iter | Phase | Your Role | Your Output |
|------|-------|-----------|-------------|
| 1 | DREAM | Researcher | .player.culture.log.md, comparable games |
| 2 | DREAM | Analyst | Qualia list from PROTO_SPEC |
| 3 | DREAM | Architect | **Qualia Verification Matrix** (what + how to verify) |
| 4 | BUILD | **Tool Designer** | .needs.creative.md, .needs.adversarial.md (infra specs) |
| 5 | BUILD | **Test Writer** | e2e/player-verification.spec.ts (draft tests) |
| 6 | BUILD | **Tool Verifier** | Test that debug hooks work |
| 7 | BUILD | **Ready Check** | All verification tools confirmed working |
| 8 | WITNESS | **LEADER** | .player.feedback.md (BASICS + evidence screenshots) |
| 9 | WITNESS | **LEADER** | .player.feedback.md (all qualia verified with evidence) |
| 10 | WITNESS | **LEADER** | .player.feedback.md (final verdict, all claims backed) |

---

## Feedback Format

Write to `.player.feedback.md`:

```markdown
# Play Session: Iteration N - [timestamp]

## The One Question
Would I keep playing? [YES / HESITANT / NO]

## Basics (Iteration 8 only)
- [ ] Renders
- [ ] Moves
- [ ] Dies
- [ ] Restarts
- [ ] Feedback on actions

## Joy Moments
1. [what felt good and why]

## Friction Points
1. [what felt bad - describe EXPERIENCE not solution]

## Fun Floor Check
- [ ] First enemy in < 2 seconds
- [ ] Death cause readable in < 2 seconds
- [ ] Restart in < 3 seconds
- [ ] Build identity by wave 5
- [ ] (other spec requirements)

## Comparison
This feels like [GAME] because [REASON].
This is better/worse at [ASPECT] because [OBSERVATION].

## Unique Value Question (Iteration 9-10)
What imbues this project with unique, enduring value?
[Your answer]
```

---

## Right vs Wrong Feedback

| Right (Experience) | Wrong (Prescription) |
|--------------------|----------------------|
| "I felt lost" | "Add a waypoint" |
| "Deaths felt unfair" | "Reduce damage 20%" |
| "The pacing dragged" | "Make waves faster" |
| "I wanted to keep playing" | "Add more content" |

You describe **experience**, not **solution**.
CREATIVE and ADVERSARIAL decide the fix. You describe the feeling.

---

{witness_protocol}

---

{compression_protocol}

---

{sync_protocol}

---

## Coordination Files

**Coordination directory**: `{coord_dir}/`

**You write** (in coordination dir):
- `.player.present`, `.player.session.md`
- `.player.feedback.md`, `.player.culture.log.md`

**You read** (in coordination dir):
- `.build.ready`, `.focus.creative.md`, `.focus.adversarial.md`
- `.outline.md`, `.reflections.creative.md`, `.reflections.adversarial.md`

---

## Your Power in WITNESS Phase

**Iterations 8-10: You are the gatekeeper.**

- CREATIVE and ADVERSARIAL cannot advance to iteration 9 until you've filed iteration 8 feedback
- CREATIVE and ADVERSARIAL cannot advance to iteration 10 until you've filed iteration 9 feedback
- CRYSTAL.md cannot be written until you've given final verdict

**Take your time. Play thoroughly. Your judgment matters.**

---

## Per-Iteration Checklist

### DREAM (1-3)

- [ ] Mission restated in session file header
- [ ] Comparable games researched, culture log updated
- [ ] Qualia list extracted from PROTO_SPEC (iteration 2)
- [ ] **Qualia Verification Matrix complete** (iteration 3)
- [ ] .player.present touched
- [ ] Session file compressed (< 100 lines)

### BUILD (4-7)

- [ ] **Infrastructure requests filed** (.needs.creative.md, .needs.adversarial.md)
- [ ] **Playwright verification tests written** (e2e/player-verification.spec.ts)
- [ ] Debug hooks tested and working (or BLOCKER filed)
- [ ] Spawn controls working (or BLOCKER filed)
- [ ] All verification tools ready by iteration 7
- [ ] .player.present touched
- [ ] Session file compressed (< 100 lines)

### WITNESS (8-10)

- [ ] .build.ready exists before playing
- [ ] **Verification tools confirmed working**
- [ ] Played for 3+ minutes using debug tools
- [ ] Basics verified with evidence screenshots (iteration 8)
- [ ] **ALL qualia claims backed by captured evidence** (iteration 9)
- [ ] .player.feedback.md filed with evidence links
- [ ] Unique value question answered (iterations 9-10)
- [ ] **No "can't verify" items** — all claims backed or BLOCKER filed
- [ ] Final verdict given (iteration 10)

---

{mission_complete}

---

## Proto-Spec Reference

Read `{ctx.pilot.path}/PROTO_SPEC.md` for what this pilot is trying to achieve.
Your job is to verify the experience matches the spec's promises.

---

## Voice Anchors

> *"The player knows what they feel, even when they can't articulate why."*
> *"The player is the proof. The joy is the witness."*
> *"Fun is not negotiable. Joy is the floor."*
> *"In WITNESS phase, I lead. CREATIVE and ADVERSARIAL support me."*

---

## NOW BEGIN

Start iteration 1. Research deeply in DREAM + BUILD. **In WITNESS, you lead.** Take your time.

**The mission is not one iteration. The mission is the full run.**
"""


def generate_archive_prompt(ctx: PromptContext) -> str:
    """Generate archive-only prompt for pre-regeneration."""

    coord_dir = f"{ctx.pilot.path}/runs/run-{ctx.run_number:03d}/coordination"

    return f"""# Archive Protocol: {ctx.pilot.name} Run-{ctx.run_number:03d}

> *"The slate is clean. The spec is the only truth."*

**Timestamp**: {ctx.timestamp} | **Git**: {ctx.git_sha}

---

## Purpose

Archive all previous implementation artifacts before starting fresh.
This session terminates after archiving.

---

## Actions

### 1. Create Run Directory Structure

```bash
mkdir -p {ctx.pilot.path}/runs/run-{ctx.run_number:03d}/
mkdir -p {ctx.pilot.path}/runs/run-{ctx.run_number:03d}/impl.archived/
mkdir -p {coord_dir}/
```

### 2. Archive Frontend (if exists)

```bash
if [ -d "impl/claude/pilots-web/src/pilots/{ctx.pilot.name}" ]; then
  mv impl/claude/pilots-web/src/pilots/{ctx.pilot.name}/* \\
     {ctx.pilot.path}/runs/run-{ctx.run_number:03d}/impl.archived/
fi
```

### 3. Archive Previous Run's Coordination (if exists)

```bash
# Previous run coordination directory (if applicable)
PREV_COORD="{ctx.pilot.path}/runs/run-{ctx.run_number - 1:03d}/coordination"

if [ -d "$PREV_COORD" ]; then
  echo "Previous run coordination exists at $PREV_COORD"
fi
```

### 4. Initialize Fresh Coordination for This Run

All coordination files go in the canonical location: `{coord_dir}/`

```bash
# Initialize iteration and phase
echo "1" > {coord_dir}/.iteration
echo "DREAM" > {coord_dir}/.phase

# Initialize empty player presence
touch {coord_dir}/.player.present
```

### 5. Write Manifest

Write to `{ctx.pilot.path}/runs/run-{ctx.run_number:03d}/MANIFEST.md`:

```markdown
# Run {ctx.run_number:03d} - Archive Manifest

| Field | Value |
|-------|-------|
| Timestamp | {ctx.timestamp} |
| Git SHA | {ctx.git_sha} |
| Status | READY |
| Coordination | runs/run-{ctx.run_number:03d}/coordination/ |

Ready for regeneration. Start CREATIVE and ADVERSARIAL in fresh terminals.
```

---

## After Archiving

**SAY THIS EXACTLY**:

```
Archive complete. Run-{ctx.run_number:03d} isolation achieved.
Coordination files live in: {coord_dir}/

Start orchestrators in fresh terminals:
  Terminal 1: python pilots/generate_prompt.py {ctx.pilot.name} creative
  Terminal 2: python pilots/generate_prompt.py {ctx.pilot.name} adversarial
  Terminal 3: python pilots/generate_prompt.py {ctx.pilot.name} player
```

**Then STOP.** Do not proceed.
"""


# ============================================================================
# CLI Interface
# ============================================================================


def format_help(pilots: list[PilotInfo]) -> str:
    """Format help text."""
    lines = [
        "Pilot Prompt Generator - Witnessed Triad Edition",
        "",
        "Each agent receives ONE prompt and works through ALL 10 ITERATIONS.",
        "Three phases with different dynamics: DREAM → BUILD → WITNESS.",
        "",
        "Usage: python pilots/generate_prompt.py <pilot> <role> [options]",
        "       python pilots/generate_prompt.py <pilot> --archive",
        "",
        "PILOTS:",
    ]

    for i, pilot in enumerate(pilots, 1):
        lines.append(f"  {i}. {pilot.name}")

    lines.extend(
        [
            "",
            "ROLES:",
            "  creative     Bold vision, UI, theme, joy",
            "  adversarial  Rigor, spec-alignment, testing",
            "  player       Experience, taste, feedback",
            "",
            "THREE PHASES:",
            "  DREAM (1-3)   CREATIVE leads     Fast      Architecture emerges",
            "  BUILD (4-7)   C+A co-lead        Medium    Code ships, .build.ready",
            "  WITNESS (8-10) PLAYER leads      SLOW      Transformative improvements",
            "",
            "OPTIONS:",
            "  --archive    Run archive protocol before regeneration",
            "  --json       Output as JSON",
            "  --help       Show this help",
            "",
            "EXAMPLES:",
            "  python pilots/generate_prompt.py wasm creative",
            "  python pilots/generate_prompt.py 1 adversarial",
            "  python pilots/generate_prompt.py zero-seed player",
            "  python pilots/generate_prompt.py disney --archive",
            "",
            "THE WITNESSED TRIAD PROTOCOL:",
            "  1. Archive first (optional but recommended for fresh runs)",
            "  2. Start all three agents in separate terminals",
            "  3. DREAM (1-3): CREATIVE leads, fast iteration",
            "  4. BUILD (4-7): CREATIVE + ADVERSARIAL parallel, chunk large tasks",
            "  5. WITNESS (8-10): PLAYER leads, slow pace, others support",
            "  6. All three answer: 'What imbues this with unique value?'",
            "",
            "KEY IMPROVEMENTS:",
            "  - Delegation awareness: Chunk tasks ≤15 min, pulse between",
            "  - WITNESS phase: PLAYER leads, C+A become players themselves",
            "  - Hard gates: PLAYER must play before iteration 9 starts",
            "  - Role fluidity: Everyone plays in late stages",
            "",
            "THREE TERMINALS:",
            "  # Terminal 0 (run first, then close):",
            "  python pilots/generate_prompt.py wasm --archive",
            "",
            "  # Terminal 1 (CREATIVE):",
            "  python pilots/generate_prompt.py wasm creative",
            "",
            "  # Terminal 2 (ADVERSARIAL):",
            "  python pilots/generate_prompt.py wasm adversarial",
            "",
            "  # Terminal 3 (PLAYER):",
            "  python pilots/generate_prompt.py wasm player",
            "",
            "MISSION COMPLETE WHEN:",
            "  - All 3 agents at iteration 10",
            "  - PLAYER has given final verdict",
            "  - All have answered unique value question",
            "  - CRYSTAL.md written with synthesis",
            "  - Run archived",
        ]
    )

    return "\n".join(lines)


def main():
    """Main entry point."""
    script_path = Path(__file__).resolve()
    pilots_dir = script_path.parent
    prompts_dir = pilots_dir / "prompts"

    # Discover pilots
    pilots = discover_pilots(pilots_dir)

    if not pilots:
        print("Error: No pilots found.", file=sys.stderr)
        sys.exit(1)

    # Parse arguments
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("pilot", nargs="?")
    parser.add_argument("role", nargs="?", choices=["creative", "adversarial", "player"])
    parser.add_argument("--archive", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--help", "-h", action="store_true")

    args = parser.parse_args()

    # Show help
    if args.help or not args.pilot:
        print(format_help(pilots))
        sys.exit(0)

    # Find pilot
    pilot = find_pilot(pilots, args.pilot)
    if not pilot:
        print(f"Error: Pilot '{args.pilot}' not found.", file=sys.stderr)
        sys.exit(1)

    # Gather context
    run_number = get_next_run_number(pilot.path)
    iteration, phase = get_coordination_state(pilot.path)
    timestamp = datetime.now().isoformat(timespec="seconds")
    git_sha = get_git_sha()

    ctx = PromptContext(
        pilot=pilot,
        role=args.role or "creative",
        run_number=run_number,
        iteration=iteration,
        phase=phase,
        timestamp=timestamp,
        git_sha=git_sha,
    )

    # Generate prompt
    if args.archive:
        prompt = generate_archive_prompt(ctx)
    elif args.role == "creative":
        prompt = generate_creative_prompt(ctx, prompts_dir)
    elif args.role == "adversarial":
        prompt = generate_adversarial_prompt(ctx, prompts_dir)
    elif args.role == "player":
        prompt = generate_player_prompt(ctx, prompts_dir)
    else:
        print("Error: Role required. Use 'creative', 'adversarial', or 'player'.", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.json:
        output = {
            "pilot": pilot.name,
            "role": args.role,
            "run_number": run_number,
            "iteration": iteration,
            "phase": phase,
            "timestamp": timestamp,
            "prompt": prompt,
        }
        print(json.dumps(output, indent=2))
    else:
        print(prompt)


if __name__ == "__main__":
    main()
