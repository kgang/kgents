# K-Terrarium Phase 2: Q-gent Implementation

**Date**: 2025-12-10
**Status**: Complete
**Tests**: 64 passing

## What Was Built

Q-gent (Quartermaster) - a resource provisioning agent for disposable code execution.

### Core Components

| File | Purpose |
|------|---------|
| `agents/q/job_builder.py` | Fluent API for K8s Job specs |
| `agents/q/quartermaster.py` | Provision + execute ephemeral jobs |
| `protocols/cli/handlers/exec.py` | `kgents exec` CLI command |

### Key Design Decisions

1. **Dual Execution Modes**
   - KUBERNETES: Full K8s Job in `kgents-ephemeral` namespace
   - SUBPROCESS: Local fallback when cluster unavailable
   - DRY_RUN: Preview Job spec without execution

2. **Fluent JobBuilder API**
   ```python
   spec = (
       JobBuilder("exec")
       .with_code("print('hello')")
       .with_limits(cpu="200m", memory="256Mi")
       .with_timeout(30)
       .build()
   )
   ```

3. **Security Hardening** (all Jobs):
   - runAsNonRoot: true
   - readOnlyRootFilesystem: true
   - allowPrivilegeEscalation: false
   - capabilities.drop: ALL
   - Network isolated by default

4. **TTL Cleanup**: Jobs auto-delete 60s after completion

### CLI Usage

```bash
kgents exec --code "print('hello')"         # Python (default)
kgents exec --code "echo hi" --lang shell   # Shell
kgents exec --file script.py                # From file
kgents exec --timeout 60 --cpu 200m --code "..."  # With limits
kgents exec --dry-run --code "..."          # Preview Job spec
kgents exec --network --code "..."          # Enable network
```

### Test Coverage

- `test_job_builder.py`: 29 tests (types, builder, convenience functions)
- `test_quartermaster.py`: 21 tests (config, modes, execution)
- `test_exec_cli.py`: 14 tests (argument parsing)

---

## Instructions for Next Session

### Phase 3: Agent Operator

The next phase is building a Kubernetes Operator to manage agent deployments via CRDs.

**Priority Tasks**:
1. Define `Agent` CRD schema (`apiVersion: kgents.io/v1`)
2. Implement operator reconciliation loop
3. Generate CRD from agent specs
4. Add `kgents infra apply <agent>` command

**Key Files to Create**:
```
impl/claude/infra/k8s/
├── crd/
│   └── agent_crd.yaml      # Agent CRD definition
├── operator.py             # Reconciliation loop
└── spec_to_crd.py          # Convert spec/*.md → CRD
```

**Reference**: See `docs/k-terrarium-plan.md` Section 5 (Agent Operator Pattern)

### Quick Start Commands

```bash
# Verify cluster running
kgents infra status

# Test Q-gent
kgents exec --code "print('Phase 2 complete!')"

# Run Q-gent tests
pytest impl/claude/agents/q/_tests/ -v

# Full test suite
pytest -m "not slow" -q
```

### Open Questions for Phase 3

1. Should operator run in-cluster or as local process?
2. How to watch for spec file changes (fswatch vs git hooks)?
3. CRD versioning strategy (v1alpha1 → v1)?
