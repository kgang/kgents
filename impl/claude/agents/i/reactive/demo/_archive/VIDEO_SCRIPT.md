# Reactive Substrate Demo Video Script

**Duration**: 3 minutes
**Target Audience**: Developers building agent visualizations

---

## Scene 1: The Problem (0:00 - 0:30)

**[Screen: Split view showing the same dashboard mockup in 4 different formats]**

**Narration**:
> "You've built a dashboard widget. Now you need it in the terminal, a TUI app, a Jupyter notebook, and as a JSON API response.
>
> Four targets means four rewrites. Four bugs to fix. Four codebases to maintain.
>
> ...or does it?"

**[Show code snippets of duplicated rendering logic]**

---

## Scene 2: The Solution (0:30 - 1:30)

**[Screen: Show the project() functor diagram]**

```
project : KgentsWidget[S] -> Target -> Renderable[Target]
```

**Narration**:
> "The reactive substrate uses a functor pattern. Define your widget once with a state dataclass and a project method. The functor handles the rest."

**[Screen: Show AgentCardWidget code]**

```python
from agents.i.reactive import AgentCardWidget, AgentCardState

# Define once
card = AgentCardWidget(AgentCardState(
    name="My Agent",
    phase="active",
    activity=(0.3, 0.5, 0.7, 0.9),
    capability=0.85,
))

# Render anywhere
print(card.to_cli())    # Terminal
card.to_tui()           # Textual app
card.to_marimo()        # Notebook
card.to_json()          # API
```

**Narration**:
> "Same widget. Four targets. Zero rewrites.
>
> The state is immutable - a frozen dataclass. The widget knows how to project that state to any target. And because it's a functor, composition preserves this property."

**[Screen: Show composition diagram - AgentCard contains Glyph + Sparkline + Bar]**

---

## Scene 3: Live Demo (1:30 - 2:30)

### Part A: TUI Dashboard (1:30 - 2:00)

**[Screen: Terminal]**

```bash
kg dashboard --demo
```

**Narration**:
> "Here's a live dashboard showing agent health. Same widgets we just defined, projected to a Textual TUI."

**[Show the dashboard running with multiple agent cards, sparklines, and bars]**

> "Three agent cards, each composed of glyphs, sparklines, and bars. All responding to the same reactive signals."

### Part B: Notebook (2:00 - 2:30)

**[Screen: Switch to browser with marimo notebook]**

```bash
marimo run impl/claude/agents/i/reactive/demo/tutorial.py
```

**Narration**:
> "Same widgets, notebook target. The tutorial walks through each concept interactively."

**[Show the tutorial notebook running, highlight the interactive cells]**

> "And if you want JSON for an API? Just call `to_json()`. It's all the same widget underneath."

---

## Scene 4: Call to Action (2:30 - 3:00)

**[Screen: Installation command and documentation links]**

**Narration**:
> "The reactive substrate ships with 45+ exports, 1460 tests, and performance of 4,000+ renders per second on all targets."

```bash
pip install kgents
```

**[Show key documentation links]**

- Tutorial: `marimo run tutorial.py`
- API Reference: `impl/claude/agents/i/reactive/README.md`
- Live Dashboard: `kg dashboard --demo`

**Narration**:
> "Define once. Render anywhere. Start building."

**[Fade to logo/end screen]**

---

## B-Roll Suggestions

1. Terminal showing ASCII art widgets (0:15)
2. Split-screen comparison: CLI vs TUI vs HTML (0:45)
3. Code editor with syntax highlighting (1:00)
4. Textual dashboard with real-time updates (1:45)
5. Marimo notebook with interactive cells (2:15)
6. Performance benchmark output (2:40)

## Audio Notes

- Keep narration pace moderate - technical audience
- Music: Subtle, low-key electronic (not distracting)
- Sound effects: Terminal keystroke sounds optional

## Recording Checklist

- [ ] Terminal font: Fira Code or JetBrains Mono
- [ ] Terminal theme: Dark (matches TUI)
- [ ] Screen resolution: 1920x1080
- [ ] Browser zoom: 125% for readability
- [ ] Close unnecessary applications
- [ ] Mute notifications

---

*Script version: 1.0*
*Last updated: 2025-12-14*
