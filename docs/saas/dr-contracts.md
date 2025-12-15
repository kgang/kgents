# Disaster Recovery Contracts

> Testable RPO/RTO assertions for kgents SaaS infrastructure.

## Overview

This document defines disaster recovery contracts as **testable assertions**. Each contract specifies:
- **RTO** (Recovery Time Objective): Maximum acceptable downtime
- **RPO** (Recovery Point Objective): Maximum acceptable data loss
- **Validation**: How to test the assertion
- **Owner**: Responsible party for meeting the contract

---

## Recovery Targets Summary

| Component | RTO | RPO | Priority | Owner |
|-----------|-----|-----|----------|-------|
| API | < 5 min | N/A (stateless) | P0 | ops |
| NATS Streams | < 15 min | < 5 min | P0 | ops |
| Secrets/Config | < 30 min | < 1 hour | P0 | ops |
| Observability | < 1 hour | N/A | P2 | ops |
| Grafana Dashboards | < 2 hours | N/A | P3 | ops |

---

## Contract 1: API Recovery

### Targets

```python
# dr_contracts.py - Testable assertions

from datetime import timedelta

class APIRecoveryContract:
    """API must recover within 5 minutes of failover trigger."""

    RTO = timedelta(minutes=5)
    RPO = None  # Stateless, no data loss concern

    @staticmethod
    def assert_recovery(failover_triggered_at: datetime, service_healthy_at: datetime) -> bool:
        """
        Assert: recovery_time < RTO

        >>> failover = datetime(2025, 1, 1, 12, 0, 0)
        >>> healthy = datetime(2025, 1, 1, 12, 3, 30)  # 3.5 min later
        >>> APIRecoveryContract.assert_recovery(failover, healthy)
        True
        """
        recovery_time = service_healthy_at - failover_triggered_at
        return recovery_time < APIRecoveryContract.RTO
```

### Validation Procedure

1. **Simulate Failover**:
   ```bash
   # Record start time
   START=$(date +%s)

   # Trigger DNS failover (simulate primary region down)
   # In production: Route53/CloudFlare health check failure

   # In test: directly update DNS or use chaos tool
   kubectl delete deployment kgent-api -n kgents-triad
   ```

2. **Measure Recovery**:
   ```bash
   # Poll health endpoint until success
   while ! curl -sf https://api.kgents.io/health; do
     sleep 5
   done

   END=$(date +%s)
   RECOVERY_TIME=$((END - START))

   # Assert
   if [ $RECOVERY_TIME -lt 300 ]; then
     echo "PASS: Recovery in ${RECOVERY_TIME}s (< 300s)"
   else
     echo "FAIL: Recovery in ${RECOVERY_TIME}s (>= 300s)"
   fi
   ```

### Dependencies

- DNS TTL: 60 seconds (recommended)
- Pod startup time: ~30 seconds
- Health check interval: 10 seconds
- Failover detection: 2-3 failed checks

### Failure Modes

| Failure | Impact on RTO | Mitigation |
|---------|---------------|------------|
| DNS propagation delay | +60-120s | Lower TTL to 30s |
| Slow pod startup | +30-60s | Pre-pull images, tune probes |
| DB connection timeout | +30s | Connection pool warm-up |

---

## Contract 2: NATS Stream Recovery

### Targets

```python
class NATSRecoveryContract:
    """NATS streams must recover within 15 minutes with < 5 min data loss."""

    RTO = timedelta(minutes=15)
    RPO = timedelta(minutes=5)

    @staticmethod
    def assert_rto(failover_triggered_at: datetime, streams_healthy_at: datetime) -> bool:
        """Assert: stream recovery < 15 minutes."""
        recovery_time = streams_healthy_at - failover_triggered_at
        return recovery_time < NATSRecoveryContract.RTO

    @staticmethod
    def assert_rpo(last_replicated_seq: int, current_origin_seq: int, msg_rate_per_min: float) -> bool:
        """
        Assert: message lag < 5 minutes worth of messages.

        >>> # Mirror is 100 messages behind, rate is 50 msg/min
        >>> NATSRecoveryContract.assert_rpo(900, 1000, 50)
        True  # 100 msgs / 50 msg/min = 2 min < 5 min
        """
        message_lag = current_origin_seq - last_replicated_seq
        time_lag_minutes = message_lag / msg_rate_per_min if msg_rate_per_min > 0 else 0
        return time_lag_minutes < NATSRecoveryContract.RPO.total_seconds() / 60
```

### Validation Procedure

1. **Measure Mirror Lag** (continuous):
   ```bash
   # Get mirror stream info
   nats stream info AGENTESE_MIRROR --json | jq '.mirror.lag'

   # Calculate time lag
   ORIGIN_SEQ=$(nats stream info AGENTESE --json | jq '.state.last_seq')
   MIRROR_SEQ=$(nats stream info AGENTESE_MIRROR --json | jq '.state.last_seq')
   LAG=$((ORIGIN_SEQ - MIRROR_SEQ))

   # Assuming 100 msg/min average
   TIME_LAG_MIN=$((LAG / 100))

   if [ $TIME_LAG_MIN -lt 5 ]; then
     echo "PASS: Mirror lag ${TIME_LAG_MIN}min (< 5min RPO)"
   else
     echo "FAIL: Mirror lag ${TIME_LAG_MIN}min (>= 5min RPO)"
   fi
   ```

2. **Simulate Stream Failover**:
   ```bash
   # Record state
   START=$(date +%s)
   ORIGIN_SEQ=$(nats stream info AGENTESE --json | jq '.state.last_seq')

   # Kill origin cluster (simulate region failure)
   kubectl delete statefulset nats -n kgents-agents

   # Promote mirror to primary (manual step)
   # In DR region: reconfigure clients to use local stream

   # Measure recovery
   while ! nats stream info AGENTESE_DR; do
     sleep 5
   done

   END=$(date +%s)
   RTO_ACTUAL=$((END - START))
   ```

### Mirror Configuration

```yaml
# NATS stream mirror configuration
streams:
  - name: AGENTESE
    cluster: rg1-primary
    subjects: ["agentese.>"]
    retention: limits
    max_msgs: 1000000

  - name: AGENTESE_MIRROR
    cluster: rg2-dr
    mirror:
      name: AGENTESE
      filter_subject: "agentese.>"
    # Mirror inherits retention from source
```

### Failure Modes

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Gateway disconnect | RPO increases | Monitor gateway health |
| Mirror lag spike | RPO violation | Alert on lag > 3min |
| Split brain | Data divergence | Fencing + manual reconcile |

---

## Contract 3: Secrets/Config Recovery

### Targets

```python
class SecretsRecoveryContract:
    """Secrets must sync within 30 minutes, config within 1 hour."""

    SECRETS_RTO = timedelta(minutes=30)
    CONFIG_RPO = timedelta(hours=1)

    @staticmethod
    def assert_secrets_sync(primary_version: str, dr_version: str) -> bool:
        """Assert: DR region has same secret version as primary."""
        return primary_version == dr_version

    @staticmethod
    def assert_config_freshness(last_sync: datetime, now: datetime) -> bool:
        """Assert: config synced within RPO window."""
        age = now - last_sync
        return age < SecretsRecoveryContract.CONFIG_RPO
```

### Validation Procedure

1. **Secrets Sync Check**:
   ```bash
   # Get secret version in primary
   PRIMARY_VERSION=$(kubectl get secret kgents-api-secrets -n kgents-triad \
     -o jsonpath='{.metadata.resourceVersion}' --context=primary)

   # Get secret version in DR
   DR_VERSION=$(kubectl get secret kgents-api-secrets -n kgents-triad \
     -o jsonpath='{.metadata.resourceVersion}' --context=dr)

   # With External Secrets Operator, compare ExternalSecret status
   ESO_SYNC=$(kubectl get externalsecret kgents-api-secrets -n kgents-triad \
     -o jsonpath='{.status.syncedResourceVersion}' --context=dr)
   ```

2. **ArgoCD Sync Check**:
   ```bash
   # Check last sync time
   argocd app get kgents-saas --output json | jq '.status.operationState.finishedAt'

   # Verify sync status
   argocd app get kgents-saas --output json | jq '.status.sync.status'
   # Expected: "Synced"
   ```

### Sync Configuration

| Component | Method | Frequency | Tool |
|-----------|--------|-----------|------|
| K8s Secrets | External Secrets Operator | 5 min poll | ESO |
| K8s Manifests | GitOps | On commit | ArgoCD |
| RBAC | GitOps | On commit | ArgoCD |
| Network Policies | GitOps | On commit | ArgoCD |

---

## Contract 4: Observability Recovery

### Targets

```python
class ObservabilityRecoveryContract:
    """Observability can degrade; restore within 1 hour."""

    RTO = timedelta(hours=1)
    RPO = None  # Metrics loss acceptable during DR
    PRIORITY = "P2"  # Non-critical

    @staticmethod
    def assert_degraded_operation(api_healthy: bool, observability_healthy: bool) -> bool:
        """
        Assert: API can operate without observability.
        Observability failure should NOT cause API failure.
        """
        # API should be healthy even if observability is down
        return api_healthy  # observability_healthy is independent
```

### Validation

```bash
# Verify API operates without observability
kubectl scale deployment prometheus -n kgents-observability --replicas=0
kubectl scale deployment grafana -n kgents-observability --replicas=0

# API should still respond
curl -sf https://api.kgents.io/health
# Expected: 200 OK

# Restore
kubectl scale deployment prometheus -n kgents-observability --replicas=1
kubectl scale deployment grafana -n kgents-observability --replicas=1
```

---

## Failover Trigger Conditions

### Automatic Triggers

```yaml
# Failover trigger configuration
automatic_triggers:
  - name: health_check_failure
    condition: "consecutive_failures >= 3"
    check_interval: "30s"
    action: dns_failover
    notification: pagerduty_critical

  - name: error_rate_spike
    condition: "error_rate_5m > 50%"
    action: alert_oncall
    notification: pagerduty_warning
    # Manual confirmation required before failover

  - name: latency_degradation
    condition: "p99_latency_5m > 10s"
    action: alert_oncall
    notification: slack_warning
    # Investigate before failover
```

### Manual Triggers

```yaml
manual_triggers:
  - name: region_outage
    declared_by: ["oncall", "sre_lead", "cto"]
    action: execute_dr_runbook
    checklist:
      - confirm_primary_unreachable
      - notify_stakeholders
      - initiate_failover
      - verify_dr_health
      - update_status_page

  - name: data_corruption
    declared_by: ["sre_lead", "cto"]
    action: halt_and_investigate
    checklist:
      - stop_all_writes
      - preserve_evidence
      - assess_blast_radius
      - decide_recovery_strategy

  - name: security_incident
    declared_by: ["security_team", "cto"]
    action: isolate_and_failover
    checklist:
      - isolate_compromised_region
      - rotate_all_secrets
      - failover_to_clean_region
      - forensic_preservation
```

### Trigger Decision Matrix

| Signal | Threshold | Action | Auto/Manual |
|--------|-----------|--------|-------------|
| Health check fail | 3 consecutive | DNS failover | Auto |
| Error rate | > 50% for 5min | Alert + investigate | Manual |
| Latency p99 | > 10s for 5min | Alert + investigate | Manual |
| Region outage | Provider status | Full DR | Manual |
| NATS cluster down | All 3 pods unhealthy | Alert + consider DR | Manual |

---

## State Synchronization Requirements

### Continuous Sync (P0)

| State | Method | Lag Budget | Alert Threshold |
|-------|--------|------------|-----------------|
| NATS Streams | JetStream Mirror | < 5 min | > 3 min |
| API Secrets | ESO | < 5 min | > 10 min |

### Periodic Sync (P1)

| State | Method | Frequency | Verification |
|-------|--------|-----------|--------------|
| K8s Manifests | ArgoCD GitOps | On commit | Sync status |
| Helm Values | ArgoCD GitOps | On commit | Sync status |
| Network Policies | ArgoCD GitOps | On commit | Sync status |

### On-Demand Sync (P2)

| State | Method | Trigger | Notes |
|-------|--------|---------|-------|
| Grafana Dashboards | Git export | Pre-DR drill | JSON in repo |
| Alert Rules | Git | Pre-DR drill | YAML in repo |
| Runbooks | Git | Manual update | Markdown in repo |

---

## Testing Schedule

### Weekly

- [ ] Verify NATS mirror lag < 3 min
- [ ] Check ESO sync status
- [ ] Validate ArgoCD sync status

### Monthly

- [ ] DNS failover drill (staging)
- [ ] Secret rotation test
- [ ] Runbook review

### Quarterly

- [ ] Full DR drill (staging)
- [ ] RTO/RPO measurement
- [ ] Contract review and update

---

## Contract Violations

### Escalation Path

| Severity | Condition | Response Time | Escalation |
|----------|-----------|---------------|------------|
| P0 | RTO/RPO breach in production | < 15 min | CTO + Eng Lead |
| P1 | RTO/RPO at risk (> 80% threshold) | < 1 hour | SRE Lead |
| P2 | Sync lag warning | < 4 hours | On-call |

### Post-Incident

After any DR event or drill:
1. Measure actual RTO/RPO achieved
2. Compare against contracts
3. Document gaps and remediation
4. Update contracts if needed (via PR)

---

## References

- Phase 10 Research: `docs/saas/multi-region-research.md`
- Chaos Baseline: `docs/saas/chaos-baseline.md`
- Runbook: `docs/saas/runbook.md`
- Production Checklist: `docs/saas/production-checklist.md`

---

*Last Updated: 2025-12-14 | Phase 10: DEVELOP*
