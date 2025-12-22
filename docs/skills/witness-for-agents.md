# Witness for Agents

> *"An agent that witnesses is an agent that learns."*

This skill teaches agents (subagents, pipelines, scripts) how to use the Witness protocol programmatically.

---

## Why Agents Should Witness

1. **Traceability** — Every action has a mark_id that can be referenced
2. **Context** — Query what happened before starting work
3. **Coordination** — Multiple agents can see each other's marks
4. **Learning** — Patterns emerge from accumulated marks

---

## Core Commands (Agent Mode)

### Creating Marks

```bash
# Basic mark with JSON output
km "Completed task X" --json
# → {"mark_id": "mark-abc123", "action": "Completed task X", "reasoning": null, "principles": [], "timestamp": "...", "author": "kent"}

# With reasoning
km "Chose approach A" -w "Simpler than B" --json
# → {"mark_id": "...", "action": "Chose approach A", "reasoning": "Simpler than B", ...}

# With principles
km "Used Crown Jewel pattern" -p composable,generative --json
```

### Querying Marks

```bash
# Recent marks as JSON array
kg witness show --json
# → [{"id": "...", "action": "...", "reasoning": "...", "principles": [...], "timestamp": "...", "author": "..."}, ...]

# Today's marks only
kg witness show --today --json

# Search by content
kg witness show --grep "extinction" --json

# Filter by principle tag
kg witness show --tag composable --json

# Combine filters
kg witness show --today --grep "audit" --limit 5 --json
```

### Recording Decisions

```bash
# Quick decision
kg decide --fast "Use SSE over WebSockets" --reasoning "Simpler for unidirectional" --json
# → {"fusion_id": "fuse-xyz789", "status": "synthesized", "synthesis_content": "...", "is_genuine_fusion": false, ...}

# Full dialectic
kg decide --kent "Approach A" --kent-reasoning "Familiar" \
          --claude "Approach B" --claude-reasoning "Simpler" \
          --synthesis "Use B with A's naming" --why "Best of both" --json
```

---

## Agent Protocol

### Before Starting Work

```bash
# Get context from recent marks
RECENT=$(kg witness show --today --json)

# Check for relevant decisions
DECISIONS=$(kg witness show --grep "architecture" --json)
```

### During Work

```bash
# Mark significant actions
km "Started audit of X" --json
km "Found issue in Y" -w "Missing validation" --json
km "Fixed issue in Y" -p ethical --json
```

### After Completing Work

```bash
# Record the decision/conclusion
kg decide --fast "Completed audit successfully" \
          --reasoning "All issues resolved" --json
```

---

## Integration Patterns

### Python (subprocess)

```python
import json
import subprocess

def create_mark(action: str, reasoning: str | None = None) -> dict:
    """Create a mark and return the result."""
    cmd = ["km", action, "--json"]
    if reasoning:
        cmd.extend(["-w", reasoning])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def get_recent_marks(limit: int = 10) -> list[dict]:
    """Get recent marks as structured data."""
    cmd = ["kg", "witness", "show", "--json", "-l", str(limit)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)
```

### Shell Script

```bash
#!/bin/bash
# Example: Audit script with witnessing

# Mark start
START_MARK=$(km "Started security audit" --json | jq -r .mark_id)

# Do work...
run_audit

# Mark completion
km "Completed security audit" -w "Found 3 issues, all resolved" --json

# Record decision
kg decide --fast "Security audit passed" --reasoning "All critical issues fixed" --json
```

### AGENTESE Integration

```python
# Via AGENTESE protocol (programmatic)
await logos.invoke("world.witness.mark", umwelt, action="Completed task")
await logos.invoke("self.witness.marks", umwelt, limit=10)
```

---

## Output Schemas

### Mark Result

```json
{
  "mark_id": "mark-abc123def456",
  "action": "The action that was taken",
  "reasoning": "Why this action was taken (optional)",
  "principles": ["composable", "generative"],
  "timestamp": "2025-12-22T10:30:00+00:00",
  "author": "kent"
}
```

### Decision Result

```json
{
  "fusion_id": "fuse-xyz789abc",
  "status": "synthesized",
  "synthesis_content": "The synthesis",
  "synthesis_reasoning": "Why the synthesis works",
  "is_genuine_fusion": true,
  "kent_proposal_id": "prop-...",
  "claude_proposal_id": "prop-..."
}
```

### Marks Query Result

```json
[
  {
    "id": "mark-abc123",
    "action": "...",
    "reasoning": "...",
    "principles": [],
    "timestamp": "2025-12-22T10:30:00+00:00",
    "author": "kent"
  }
]
```

---

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Do This Instead |
|--------------|--------------|-----------------|
| Marking every line of code | Noise drowns signal | Mark significant actions only |
| Forgetting `--json` | Can't parse Rich output | Always use `--json` for agents |
| Not querying before work | Missing context | Check `--today --json` first |
| Verbose mark actions | Hard to grep | Keep actions concise |

---

## Context Budget Protocol

Subagents need situational awareness without overflowing context windows. The context budget system provides compressed, relevant crystals within a token budget.

### Getting Context

```bash
# Default budget (2000 tokens)
kg witness context --json
# → {"items": [...], "total_tokens": 1847, "budget": 2000, "budget_remaining": 153, ...}

# Tighter budget for resource-constrained agents
kg witness context --budget 1000 --json

# Relevance-weighted by topic
kg witness context --query "architecture refactoring" --json

# Adjust recency vs relevance weighting
kg witness context --query "DI" --recency-weight 0.3 --json  # Favor relevance
```

### Context Item Schema

```json
{
  "items": [
    {
      "id": "crystal-abc123",
      "level": "SESSION",
      "insight": "Completed extinction audit, removed 52K lines",
      "significance": "Codebase is leaner, focus is sharper",
      "topics": ["extinction", "audit", "cleanup"],
      "score": 0.85,
      "recency_score": 0.92,
      "relevance_score": 0.70,
      "tokens": 150,
      "cumulative_tokens": 150,
      "crystallized_at": "2025-12-22T10:30:00+00:00"
    }
  ],
  "total_tokens": 1847,
  "budget": 2000,
  "budget_remaining": 153,
  "query": "extinction",
  "recency_weight": 0.7
}
```

### Subagent Startup Protocol

```python
import json
import subprocess

def get_agent_context(budget: int = 1500, query: str | None = None) -> list[dict]:
    """Get compressed context for subagent startup."""
    cmd = ["kg", "witness", "context", "--budget", str(budget), "--json"]
    if query:
        cmd.extend(["--query", query])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

# In subagent initialization
context = get_agent_context(budget=1500, query="my-task-topic")
for item in context["items"]:
    # Inject crystal insights into prompt
    prompt += f"\n[Context L{item['level']}] {item['insight']}"
```

### Shell Script Integration

```bash
#!/bin/bash
# Subagent with context injection

# Get context
CONTEXT=$(kg witness context --budget 1000 --json)

# Extract insights for prompt
INSIGHTS=$(echo "$CONTEXT" | jq -r '.items[] | "[L\(.level)] \(.insight)"')

# Pass to LLM or downstream agent
run_agent --context "$INSIGHTS"
```

### Budget Sizing Guidelines

| Agent Type | Budget | Rationale |
|------------|--------|-----------|
| Quick task | 500 | Minimal context needed |
| Standard subagent | 1500 | Room for 10-15 crystals |
| Research agent | 3000 | Broader context helpful |
| Coordinator | 5000 | Needs full situational awareness |

### Scoring Algorithm

Crystals are ranked by: `score = recency_weight × recency + (1 - recency_weight) × relevance`

- **Recency**: Exponential decay with 7-day half-life
- **Relevance**: Keyword matching against insight, significance, topics
- **Default weight**: 0.7 recency, 0.3 relevance

---

## Composability

Marks compose across agents:

```
Agent A: km "Started pipeline" --json → mark-aaa
  └── Agent B: km "Processing step 1" --json → mark-bbb
  └── Agent C: km "Processing step 2" --json → mark-ccc
Agent A: km "Pipeline complete" --json → mark-ddd
```

Query the pipeline's work:
```bash
kg witness show --grep "pipeline" --json
```

---

## Crystal Context vs Raw Marks

| Approach | Use Case | Tokens |
|----------|----------|--------|
| `kg witness show --today --json` | Recent raw marks | High (unbounded) |
| `kg witness context --budget N` | Compressed insights | Bounded by N |
| `kg witness crystals --json` | All crystals (no budget) | Medium |

**Recommendation**: For agents, prefer `context --budget N` over raw marks. You get executive summaries instead of logs.

---

*"The proof IS the decision. The mark IS the witness."*
*"Budget forces compression. Compression reveals essence."*
