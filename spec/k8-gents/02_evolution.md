# K8-gents Evolution: Safe Autopoiesis

> *"The cell that cannot repair itself dies. The cell that repairs without restraint becomes cancer."*

Agents evolve via **Proposals**—declarative requests to modify their own configuration. The system validates proposals via dry-run before merging.

---

## The Proposal Pattern

Agents **never** edit Deployments directly. They write Proposals.

```
Agent wants change  →  Creates Proposal CR  →  Dry-run validation  →  Risk assessment
                                                                           ↓
                                              ← Human review ← High risk ←┤
                                              ← T-gent review ← Med risk ←┤
                                              ← Auto-merge ← Low risk ←───┘
```

---

## Proposal CRD

```yaml
apiVersion: kgents.io/v1
kind: Proposal
metadata:
  name: b-gent-scale-up
spec:
  target: Deployment/b-gent          # Resource to modify
  patchType: strategic               # json | strategic | merge
  patch: |
    spec:
      replicas: 3
  reason: "High load. Queue depth: 47"
  proposer: b-gent
  urgency: MEDIUM                    # LOW | MEDIUM | HIGH | CRITICAL
  evidence:
    error_rate: 0.15
    resource_pressure: 0.92
status:
  phase: PASSED                      # PENDING → VALIDATING → PASSED/FAILED → APPROVED → MERGED
  risk_score: 0.25
  validation_result: "Dry-run successful"
  reviewed_by: auto-trust-gate
```

---

## Trust Gates

| Risk Score | Action | Rationale |
|------------|--------|-----------|
| < 0.3 | Auto-merge | Safe changes: small scale-up, memory increase ≤2x |
| 0.3 - 0.6 | T-gent review | Medium changes: larger resource changes |
| > 0.6 | Human review | Dangerous: image changes, scale-down, env vars |
| CRITICAL urgency | Human review | Always requires human regardless of risk |

### Risk Calculation

```python
def calculate_risk(current, proposed) -> float:
    risk = 0.0

    # Resource changes
    if changes_resources(current, proposed):
        risk += 0.2
        if resource_increase_factor(current, proposed) > 2.0:
            risk += 0.3

    # Replica changes
    if changes_replicas(current, proposed):
        if new_replicas < old_replicas:  # Scale-down
            risk += 0.4
        elif new_replicas > old_replicas * 2:
            risk += 0.2

    # High-risk changes
    if changes_image(current, proposed):
        risk += 0.5
    if changes_env(current, proposed):
        risk += 0.3
    if changes_volumes(current, proposed):
        risk += 0.4

    return min(risk, 1.0)
```

### Configuration

```yaml
# ConfigMap: proposal-trust-gates
auto_merge:
  max_risk_score: 0.3
  allowed_changes:
    - replicas_increase_factor: 2.0
    - memory_increase_factor: 2.0
  blocked_changes:
    - image
    - volumes
    - service_account

review_required:
  min_risk_score: 0.3
  approvers:
    - kind: User
      name: platform-team
    - kind: Agent
      name: t-gent
```

---

## T-gent: The Immune System

T-gent reviews medium-risk proposals:

```python
class ProposalReviewer:
    async def review(self, proposal: Proposal) -> ReviewDecision:
        # 1. Check composition laws
        if violations := await self.check_laws(proposal):
            return reject(f"Law violations: {violations}")

        # 2. Check historical patterns
        similar = await self.find_similar(proposal)
        if failure_rate(similar) > 0.3:
            return reject(f"Similar proposals fail {failure_rate:.0%}")

        # 3. Check resources
        if not await self.can_afford(proposal):
            return reject("Exceeds resource budget")

        return approve("Passed immune system checks")
```

---

## ProposalOperator

```python
@kopf.on.create("proposals.kgents.io")
async def handle_proposal(spec, patch, **_):
    patch.status["phase"] = "VALIDATING"

    # 1. Parse target
    kind, name = spec["target"].split("/")
    current = await get_resource(kind, name)

    # 2. Apply patch (dry-run)
    patched = apply_patch(current, spec["patch"])
    result = await kubectl_apply(patched, dry_run="server")

    if not result.success:
        patch.status["phase"] = "FAILED"
        patch.status["validation_result"] = result.error
        return

    # 3. Calculate risk
    risk = calculate_risk(current, patched)
    patch.status["phase"] = "PASSED"
    patch.status["risk_score"] = risk

    # 4. Auto-merge if safe
    if risk < TRUST_THRESHOLD:
        await apply_patch_for_real(patched)
        patch.status["phase"] = "MERGED"
        patch.status["reviewed_by"] = "auto-trust-gate"
```

---

## CLI

```bash
# Create proposal
kgents propose b-gent --replicas 3 --reason "High load"

# List proposals
kgents proposals list
# NAME              TARGET          PHASE   RISK   PROPOSER
# b-gent-scale      Deployment/b    PASSED  0.25   b-gent

# Approve/reject
kgents proposals approve b-gent-scale
kgents proposals reject b-gent-scale --reason "Not during deploy window"

# Details
kgents proposals describe b-gent-scale
```

---

## GitOps Integration

Proposals don't bypass GitOps—they feed into it.

1. Low-risk proposals auto-merge to cluster
2. ProposalOperator creates PR to sync manifest repo
3. ArgoCD detects drift, syncs from PR

```python
@kopf.on.field("proposals.kgents.io", field="status.phase", new="MERGED")
async def sync_to_git(spec, **_):
    if was_auto_merged(spec):
        await create_pr(
            repo="kgents/manifests",
            title=f"[Auto] {spec['reason'][:50]}",
            files={f"agents/{spec['target']}.yaml": patched_manifest}
        )
```

---

## Principle Alignment

| Principle | Manifestation |
|-----------|---------------|
| **Ethical** | Human in loop for high-risk changes |
| **Transparent** | `kgents proposals list` makes autopoiesis visible |
| **Heterarchical** | Any agent can propose; T-gent reviews as peer |
| **Graceful** | Failed proposals stay PENDING (safe default) |

---

## Anti-Patterns

| Anti-Pattern | Why Wrong |
|--------------|-----------|
| Direct Deployment edits | Bypasses safety |
| Auto-merge everything | Invites disaster |
| Block everything | Prevents adaptation |
| Proposals without evidence | No basis for trust |

---

*"Safe autopoiesis is the narrow path between death and cancer."*
