# TREE: Agent CLI Crown Jewel — ACT Phase

> *"The agent does not describe work. The agent DOES work."*

## Phase: ACT (condensed: DEVELOP + STRATEGIZE + IMPLEMENT)

**AGENTESE clause**: `concept.forest.manifest[phase=ACT][condensed=true]@span=agent_cli_act`

**Prior**: PLAN + RESEARCH complete. File map built, gaps identified.

---

## Research Summary (From SENSE Phase)

### Key Files
- `protocols/cli/hollow.py` — Command registry with lazy loading
- `protocols/cli/handlers/a_gent.py` — Current Alethic Architecture (K8s focus)
- `protocols/cli/handlers/soul.py` — K-gent CLI (reference implementation)
- `agents/k/session.py` — SoulSession cross-session identity pattern
- `agents/flux/__init__.py` — Flux functor for streaming

### Gap: Current `kg a` is deployment-focused, not dialogue-focused

```
Current:  kg a run soul --input "hello"   # K8s projector style
Desired:  kg a soul "hello"               # Direct dialogue
Desired:  kg a soul --repl                # Interactive mode
```

---

## Implementation Plan

### 1. Add Dialogue Mode to `a_gent.py`

**File**: `impl/claude/protocols/cli/handlers/a_gent.py`

Extend `cmd_a` to support direct dialogue:

```python
# New commands (add to match statement)
case agent_name if agent_name not in ("inspect", "manifest", "run", "list", "new"):
    # Direct dialogue: kg a soul "prompt"
    return asyncio.run(_handle_dialogue(agent_name, prompt, json_mode, ctx))
```

### 2. Agent Registry (Dynamic Discovery)

Add to `a_gent.py`:

```python
DIALOGUE_AGENTS: dict[str, str] = {
    "soul": "agents.k:KgentSoul",
    "kgent": "agents.k:KgentSoul",  # alias
}

def _resolve_dialogue_agent(name: str) -> Any:
    """Resolve agent name to dialogue-capable agent instance."""
    if name in DIALOGUE_AGENTS:
        module_path, class_name = DIALOGUE_AGENTS[name].rsplit(":", 1)
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        return cls()
    return None
```

### 3. Dialogue Handler

```python
async def _handle_dialogue(
    agent_name: str,
    prompt: str | None,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle direct dialogue with an agent."""
    agent = _resolve_dialogue_agent(agent_name)
    if agent is None:
        _emit_output(f"[A] Unknown agent: {agent_name}", {"error": "unknown"}, ctx)
        return 1

    if prompt is None:
        # Enter REPL mode
        return await _handle_repl(agent, agent_name, json_mode, ctx)

    # Single dialogue turn
    if hasattr(agent, "dialogue"):
        output = await agent.dialogue(prompt)
        response = output.response if hasattr(output, "response") else str(output)
    else:
        output = await agent.invoke(prompt)
        response = str(output)

    _emit_output(response, {"agent": agent_name, "response": response}, ctx)
    return 0
```

### 4. REPL Handler

```python
async def _handle_repl(
    agent: Any,
    agent_name: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Interactive REPL for an agent."""
    _emit_output(f"[A] {agent_name} REPL (type 'q' to quit)", {}, ctx)

    while True:
        try:
            user_input = input(f"[{agent_name}] > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[A] Goodbye.")
            return 0

        if user_input.lower() in ("q", "quit", "exit"):
            return 0

        if not user_input:
            continue

        if hasattr(agent, "dialogue"):
            output = await agent.dialogue(user_input)
            response = output.response if hasattr(output, "response") else str(output)
        else:
            output = await agent.invoke(user_input)
            response = str(output)

        _emit_output(response, {"response": response}, ctx)

    return 0
```

---

## Exit Criteria (ACT Phase)

- [ ] `kg a soul "prompt"` works (direct dialogue)
- [ ] `kg a soul` enters REPL mode
- [ ] `kg a --list` shows dialogue-capable agents
- [ ] Tests pass: `uv run pytest impl/claude/protocols/cli/handlers/_tests/test_a_gent.py -v`
- [ ] Mypy clean: `uv run mypy impl/claude/protocols/cli/handlers/a_gent.py`

---

## Execution Instructions

1. Read current `a_gent.py`
2. Add `DIALOGUE_AGENTS` registry
3. Add `_resolve_dialogue_agent` function
4. Add `_handle_dialogue` and `_handle_repl` handlers
5. Modify `cmd_a` match statement to route to dialogue
6. Add/update tests
7. Run tests and mypy
8. If all pass, commit with message referencing this plan

---

## After ACT: REFLECT Phase

Write epilogue to `plans/_epilogues/2025-12-14-agent-cli-act.md`:
- What worked
- What was harder than expected
- Learnings for meta.md

---

## Commands to Execute

```bash
# After implementation
cd /Users/kentgang/git/kgents/impl/claude
uv run pytest protocols/cli/handlers/_tests/test_a_gent.py -v
uv run mypy protocols/cli/handlers/a_gent.py

# Manual test
kg a soul "What should I focus on today?"
kg a soul  # Should enter REPL
```

---

*"SENSE is complete. Now we ACT."*
