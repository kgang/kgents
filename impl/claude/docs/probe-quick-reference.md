# kg probe - Quick Reference

Fast categorical law checks and health probes for kgents infrastructure.

## Philosophy

> "The laws hold, or they don't. No middle ground."

Probes are FAST. No LLM calls for basic checks. Only emit witness marks on FAILURE. Exit code 0 = pass, 1 = fail (CI-friendly).

---

## Health Probes

Check Crown Jewel and infrastructure health.

### Check All Components

```bash
kg probe health --all
```

**Output:**
```
✓ health:brain
  Brain service importable; Storage provider accessible
  Duration: 0.0ms

✓ health:witness
  Witness service healthy
  Duration: 0.0ms

✓ health:kblock
  K-Block service healthy
  Duration: 9.2ms

✓ health:sovereign
  Sovereign service healthy
  Duration: 0.0ms

✓ health:llm
  LLM client accessible
  Duration: 0.0ms
```

### Check Specific Component

```bash
kg probe health --jewel brain
kg probe health --jewel witness
kg probe health --jewel kblock
kg probe health --jewel sovereign
kg probe health --jewel llm
```

### JSON Output

```bash
kg probe health --all --json
```

**Output:**
```json
[
  {
    "name": "health:brain",
    "probe_type": "health",
    "status": "passed",
    "passed": true,
    "details": "Brain service importable; Storage provider accessible",
    "duration_ms": 0.001,
    "timestamp": "2025-12-23T22:58:47.366827+00:00",
    "mark_id": null
  },
  ...
]
```

---

## Law Probes

Verify categorical laws on tools and compositions.

### Identity Law

Test: `Id >> f == f == f >> Id`

```bash
kg probe identity
```

**What it checks:**
- Identity morphism is a no-op
- Left identity: `Id >> tool` equals `tool`
- Right identity: `tool >> Id` equals `tool`

**Test tool:** `AddOneTool` (x → x+1)

### Associativity Law

Test: `(f >> g) >> h == f >> (g >> h)`

```bash
kg probe associativity
```

**What it checks:**
- Tool composition is associative
- Grouping doesn't matter, only order

**Test tools:**
- `AddOneTool`: x → x+1
- `MultiplyTwoTool`: x → x*2
- `SquareTool`: x → x²

**Example:**
```
input: 3
(3+1)*2)² = 8² = 64
3+1)*(2)²... wait, composition is sequential!
f(3)=4, g(4)=8, h(8)=64
Both groupings yield 64 ✓
```

### Coherence Check

Test: Sheaf gluing conditions

```bash
kg probe coherence
```

**What it checks:**
- Local views agree on overlaps
- Sheaf conditions hold

**Test sheaf:** Simple sheaf with `check_coherence()` method

---

## Edge Cases

### Invalid Component

```bash
$ kg probe health --jewel nonexistent
⚠ health:nonexistent
  Unknown component: nonexistent
  Duration: 0.0ms
```

Exit code: 1

### Unknown Probe Type

```bash
$ kg probe invalid_type
Error: unknown probe type: invalid_type
```

Exit code: 1

### Help

```bash
kg probe --help
```

Shows comprehensive usage and examples.

---

## For Agents (Programmatic Use)

Always use `--json` flag for machine-readable output:

```bash
# Check health before operation
HEALTH=$(kg probe health --all --json 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -v "^\[kgents\]" | grep -v "^2025")
if echo "$HEALTH" | jq -e 'all(.passed)' >/dev/null; then
    echo "All systems healthy"
else
    echo "Health check failed"
    exit 1
fi

# Check identity law
kg probe identity --json

# Check associativity law
kg probe associativity --json

# Check coherence
kg probe coherence --json
```

**Note:** Filter log output to extract clean JSON:
```bash
kg probe health --all --json 2>&1 | \
  sed 's/\x1b\[[0-9;]*m//g' | \
  grep -v "^\[kgents\]" | \
  grep -v "^2025" | \
  grep -v "^Warning"
```

---

## Witness Integration

Probes emit marks on **failure only** to keep overhead low.

### Example: Failed Identity Law

```bash
$ kg probe identity  # Assume it fails
✗ identity:tool_name
  Identity law violated: left=5, direct=6, right=5
  Duration: 0.5ms
  Mark: mark_abc123
```

Check the mark:

```bash
kg witness show --grep "identity" --today
```

---

## Performance Baselines

All probes should complete in < 10ms:

| Probe | Expected Duration |
|-------|-------------------|
| health:brain | < 1ms |
| health:witness | < 1ms |
| health:kblock | < 15ms |
| health:sovereign | < 1ms |
| health:llm | < 1ms |
| identity | < 1ms |
| associativity | < 1ms |
| coherence | < 1ms |

If probes take longer, investigate:
- Database connectivity issues
- Import-time initialization overhead
- Network calls (should never happen in basic probes)

---

## Battle Test Suite

Run comprehensive test suite:

```bash
./impl/claude/scripts/test_probe_battle.sh
```

**Coverage:**
- All health checks (5 tests)
- All law probes (3 tests)
- Edge cases (4 tests)

Total: 12 tests, all should pass.

---

## Future Extensions

### Custom Tool Testing

```bash
# Not yet implemented
kg probe identity --tool file.read
kg probe associativity --pipeline "file.read >> grep >> edit"
```

### Real Sheaf Testing

```bash
# Not yet implemented
kg probe coherence --sheaf witness --context "trace_123"
```

### Budget Probes

```bash
# Not yet implemented
kg probe budget --harness void
kg probe budget --harness exploration
```

---

## Troubleshooting

### "Unknown component: X"

You specified an invalid component name. Valid components:
- brain
- witness
- kblock (or k-block, k_block)
- sovereign
- llm

### "Probe not yet implemented"

You tried to use an advanced feature (custom tools, pipelines, sheaves) that isn't implemented yet. Use default test tools:

```bash
kg probe identity        # Uses default AddOneTool
kg probe associativity   # Uses default pipeline
kg probe coherence       # Uses default test sheaf
```

### JSON Output Mixed with Logs

Use the filtering pipeline:

```bash
kg probe health --all --json 2>&1 | \
  sed 's/\x1b\[[0-9;]*m//g' | \
  grep -v "^\[kgents\]" | \
  grep -v "^2025" | \
  grep -v "^Warning" | \
  jq .
```

---

## See Also

- `docs/probe-battle-test-report.md` - Detailed test report
- `services/probe/health.py` - Health probe implementation
- `services/probe/laws.py` - Law probe implementation
- `spec/services/tooling.md` - Category theory foundation

---

*"Category laws are rationality constraints. If they fail, something is wrong."*
