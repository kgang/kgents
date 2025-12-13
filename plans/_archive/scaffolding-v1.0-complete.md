---
path: devex/scaffolding
status: complete
progress: 100
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Plan created from strategic recommendations.
  Priority 2 of 6 DevEx improvements.

  2025-12-13: Implemented!
  - Jinja2 templates in _templates/agent/
  - Agent scaffolding: __init__.py, agent.py, _tests/
  - Templates: minimal (Lambda), default (Lambda), full (Kappa)
  - Integrated into existing `kgents new agent` command
  - Tests with pytest.importorskip for optional jinja2
  - mypy strict clean
---

# Agent Scaffolding: `kgents new`

> *"Zero-to-working-agent in 2 minutes."*

**Goal**: Interactive scaffolding that generates a complete agent with tests from a template.
**Priority**: 2 (high impact, low effort)

---

## The Problem

Creating a new agent requires understanding archetypes, halos, and projectors. Too much upfront knowledge before writing any code.

---

## The Solution

```bash
$ kgents new weather-agent

Creating weather-agent...

[?] Archetype:
    > Kappa (full-stack: stateful + soulful + observable + streamable)
      Lambda (minimal: observable only)
      Delta (data: stateful + observable)

[?] Input type: str
[?] Output type: WeatherData (custom)
[?] Add K-gent governance? [Y/n]

Generated:
  impl/claude/agents/weather_agent/
    ├── __init__.py
    ├── agent.py        # Your agent logic goes here
    ├── types.py        # WeatherData definition
    └── _tests/
        └── test_agent.py

Next steps:
  1. Edit agent.py to implement your logic
  2. Run: kgents dev weather-agent
  3. Test: pytest impl/claude/agents/weather_agent/
```

---

## Research & References

### Scaffolding Tools Comparison

| Tool | Pros | Cons |
|------|------|------|
| **Cookiecutter** | 6000+ templates, mature, hooks | No update support |
| **Copier** | Updates to generated projects, modern UX | Smaller community |
| **Custom** | Perfect fit for kgents, no dependencies | Maintenance burden |

- Source: [Cookiecutter vs Copier](https://www.saashub.com/compare-cookiecutter-vs-copier)
- Source: [Scaffolding Tools Overview](https://www.resourcely.io/post/12-scaffolding-tools)

### Best Practices
- Keep templates versioned
- Automated testing of templates
- Simple Jinja2 logic (avoid complexity)
- Source: [Python Podcast on Copier](https://www.pythonpodcast.com/episodepage/project-scaffolding-that-evolves-with-your-software-using-copier)

### Decision: Custom Implementation
Given kgents' specific needs (archetypes, halos, AGENTESE paths), a custom implementation is simpler than adapting Cookiecutter/Copier templates.

---

## Implementation Outline

### Phase 1: Template Files (~100 LOC total)
```
_templates/agent/
├── __init__.py.j2
├── agent.py.j2
├── types.py.j2
└── _tests/
    └── test_agent.py.j2
```

Example `agent.py.j2`:
```python
"""{{ agent_name }} agent."""

from agents.a import {{ archetype }}

{% if custom_output_type %}
from .types import {{ output_type }}
{% endif %}


class {{ agent_class }}({{ archetype }}[{{ input_type }}, {{ output_type }}]):
    """{{ description }}"""

    async def invoke(self, input: {{ input_type }}) -> {{ output_type }}:
        # TODO: Implement your logic here
        raise NotImplementedError("Implement me!")
```

### Phase 2: Interactive Prompts (~100 LOC)
```python
# protocols/cli/handlers/new.py
from rich.prompt import Prompt, Confirm

@expose(help="Create a new agent")
async def new(self, ctx: CommandContext, name: str) -> None:
    archetype = Prompt.ask(
        "Archetype",
        choices=["Kappa", "Lambda", "Delta"],
        default="Lambda",
    )
    input_type = Prompt.ask("Input type", default="str")
    output_type = Prompt.ask("Output type", default="str")
    add_soul = Confirm.ask("Add K-gent governance?", default=False)

    await self._generate(name, archetype, input_type, output_type, add_soul)
```

### Phase 3: Generator Engine (~100 LOC)
```python
class AgentGenerator:
    """Generate agent from template."""

    def __init__(self, template_dir: Path):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    async def generate(self, config: AgentConfig, output_dir: Path) -> None:
        for template_path in self.env.list_templates():
            output_path = self._resolve_output_path(template_path, config)
            content = self.env.get_template(template_path).render(config.dict())
            output_path.write_text(content)
```

### Phase 4: Minimal Mode (~20 LOC)
```bash
# Quick creation without prompts
kgents new my-agent --minimal
# Creates Lambda archetype with str -> str
```

---

## File Structure

```
impl/claude/
├── _templates/
│   └── agent/
│       ├── __init__.py.j2
│       ├── agent.py.j2
│       ├── types.py.j2
│       └── _tests/
│           └── test_agent.py.j2
└── protocols/cli/handlers/
    └── new.py
```

---

## Generated Agent Structure

```
agents/{{ name }}/
├── __init__.py          # Exports agent class
├── agent.py             # Main agent implementation
├── types.py             # Custom types (if any)
└── _tests/
    ├── __init__.py
    └── test_agent.py    # Basic test scaffold
```

---

## Success Criteria

| Criterion | Metric |
|-----------|--------|
| Time to generated agent | < 30 seconds |
| Generated code runs | First try |
| Generated tests pass | First try |
| Kent's approval | "This saves me time" |

---

## Testing Strategy

| Test Type | Coverage |
|-----------|----------|
| Unit | Template rendering |
| Integration | Full generation flow |
| Smoke | Generated agent imports |
| Regression | Generated tests pass |

---

## Dependencies

- `jinja2` (already installed) — Template engine
- `rich` (already installed) — Interactive prompts
- Existing archetypes in `agents/a/`

---

## Cross-References

- **Strategic Recommendations**: `plans/ideas/strategic-recommendations-2025-12-13.md`
- **Archetypes**: `agents/a/archetypes.py`
- **CLI Patterns**: `plans/skills/cli-command.md`
- **Building Agents**: `plans/skills/building-agent.md`

---

*"The fastest agent is the one that writes itself."*
