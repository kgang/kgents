# Multi-Region Evaluation: Research Findings

> Phase 10 Track A: Research synthesis for multi-region patterns and DR strategy.

## Executive Summary

After evaluating multi-region patterns for Kubernetes and NATS, the **recommended approach** for kgents SaaS is:

1. **Active-Passive** (warm standby) for Kubernetes workloads
2. **Super-Cluster with Mirroring** for NATS JetStream
3. **DNS-based failover** via Route53/CloudFlare

This approach balances cost, complexity, and recovery objectives. Full active-active is not recommended at current scale.

---

## Multi-Region Deployment Patterns

### Pattern Comparison Table

| Pattern | RTO | RPO | Cost | Complexity | Best For |
|---------|-----|-----|------|------------|----------|
| **Active-Active** | ~0 | ~0 | $$$$ | Very High | Mission-critical, global users |
| **Active-Passive** | 5-15min | < 1min | $$ | Medium | Most SaaS, regional failover |
| **Pilot Light** | 15-30min | < 5min | $ | Low | Cost-sensitive, infrequent DR |
| **Backup & Restore** | 1-4h | hours | $ | Low | Dev/staging, disaster-only |

### Pattern Details

#### Active-Active (Full Redundancy)
- Both regions serve traffic simultaneously
- Requires global load balancer (CloudFlare, AWS Global Accelerator)
- Database sync complexity (CRDTs, multi-primary)
- Cost: 2x infrastructure + cross-region network
- **Not recommended** for kgents Phase 10 (overkill for current scale)

#### Active-Passive (Warm Standby) ✓ RECOMMENDED
- Primary region handles all traffic
- Secondary region ready to take over
- Automated DNS failover (5-15 min)
- State sync via backup replication
- Cost: ~1.3x infrastructure
- **Best fit** for kgents SaaS tier

#### Pilot Light (Minimal Standby)
- Minimal infrastructure in DR region
- Core components only (secrets, configs)
- Scale-up triggered on failover
- Manual intervention often required
- Good stepping stone before Active-Passive

---

## NATS Multi-Cluster Options

### Option Comparison

| Option | Consistency | Write Latency | Read Latency | Regional Failure | Cost |
|--------|-------------|---------------|--------------|------------------|------|
| **Clustered (single)** | Immediate | Low | Low | Total outage | $ |
| **Super-Cluster + Mirror** | Eventual | High→Origin | Low (local) | Writes blocked | $$ |
| **Stretch Cluster** | Immediate | High (cross-WAN) | High | Survives 1 region | $$$ |
| **Virtual Streams (v2.10+)** | Eventual | Low (local) | Low (local) | Full availability | $$ |

### Recommended: Super-Cluster with Stream Mirroring

For kgents SaaS, the **Super-Cluster with Stream Mirroring** pattern provides:

1. **Location transparency**: Clients connect to any cluster
2. **Low-latency reads**: Mirrors serve local consumers
3. **DR capability**: Mirror can become primary if origin fails
4. **Existing compatibility**: Works with current NATS 2.10 setup

#### Architecture

```
Region 1 (Primary)              Region 2 (DR)
┌─────────────────┐            ┌─────────────────┐
│  NATS Cluster   │◄──Gateway──►  NATS Cluster   │
│  (3 nodes)      │            │  (3 nodes)      │
│                 │            │                 │
│  AGENTESE       │───Mirror──►│  AGENTESE       │
│  (origin)       │            │  (mirror)       │
│                 │            │                 │
│  EVENTS         │───Mirror──►│  EVENTS         │
│  (origin)       │            │  (mirror)       │
└─────────────────┘            └─────────────────┘
```

#### Key Configuration

```yaml
# Gateway configuration (each cluster)
gateway:
  name: rg1
  gateways:
    - name: rg1
      urls: ["nats://nats-rg1-0:7222", ...]
    - name: rg2
      urls: ["nats://nats-rg2-0:7222", ...]
```

#### Stream Mirroring

```bash
# Create mirror in DR region
nats stream add AGENTESE_MIRROR \
  --mirror AGENTESE \
  --cluster=rg2
```

### Alternative: Virtual Streams (Future)

NATS 2.10+ Virtual Streams provide active-active writes but require:
- More complex configuration (9+ servers for 3-region)
- Careful subject namespace design
- Tolerance for eventual consistency

**Defer to Phase 12+** after validating basic multi-region.

---

## Kubernetes DR Strategy

### Recommended Tools

| Component | Tool | Purpose |
|-----------|------|---------|
| Backup/Restore | **Velero** | Cluster state, PVs, secrets |
| State Sync | **ArgoCD** | GitOps manifest sync |
| DNS Failover | **Route53/CloudFlare** | Health-based routing |
| Service Mesh | Istio (optional) | Cross-cluster traffic |

### Failover Flow

```
1. Health check fails (Route53/CloudFlare)
           │
           ▼
2. DNS TTL expires (60s recommended)
           │
           ▼
3. Traffic routes to DR region
           │
           ▼
4. Velero restore triggers (if needed)
           │
           ▼
5. ArgoCD syncs latest manifests
           │
           ▼
6. Services healthy in DR region
```

### GitOps Sync Strategy

- **Same repo**: Both regions pull from same Git source
- **ArgoCD ApplicationSet**: Region-specific overlays via Kustomize
- **Secrets**: External Secrets Operator with multi-region secret store

---

## Current Infrastructure Gaps

### Chaos Baseline Gaps for Multi-Region

Current chaos scenarios (Phase 9) are single-region focused:

| Gap | Impact | Mitigation |
|-----|--------|------------|
| No cross-region failover test | Unknown DR RTO | Add DNS failover scenario |
| No NATS mirror lag test | Unknown RPO for streams | Add mirror lag monitoring |
| No split-brain scenario | Data consistency risk | Add partition test |
| No secret sync validation | DR may have stale secrets | Test ESO sync |

### Proposed New Scenarios (Phase 11+)

1. **Region Failover**: Simulate primary region loss via DNS manipulation
2. **NATS Mirror Lag**: Measure replication lag under load
3. **Secret Rotation During Failover**: Validate secret sync
4. **Cross-Region Latency Spike**: Gateway timeout handling

---

## Cost Estimates

### Self-Hosted Multi-Region (AWS)

| Component | Primary | DR (Passive) | Monthly Cost |
|-----------|---------|--------------|--------------|
| EKS Cluster | 3x t3.medium | 3x t3.medium | ~$200 |
| NATS (EC2/EKS) | 3x t3.small | 3x t3.small | ~$120 |
| Cross-region transfer | - | ~100GB/month | ~$10 |
| Route53 health checks | - | 3 endpoints | ~$5 |
| S3 backup storage | 50GB | Cross-region replication | ~$5 |
| **Total** | | | **~$340/month** |

### Synadia Cloud (Managed NATS)

| Plan | Connections | Storage | Monthly |
|------|-------------|---------|---------|
| Personal | 10 | 5GB | Free |
| Starter | 100 | 25GB | $49 |
| Pro | 1,000 | 100GB | $199 |
| Premium | 10,000 | 1TB | $899 |

**For multi-region**: Pro tier ($199) + Remote System add-on ($49) = **$248/month** for managed NATS

### Comparison

| Approach | Monthly Cost | Operational Burden |
|----------|--------------|-------------------|
| Self-hosted multi-region | ~$340 | High (manage NATS, K8s) |
| Synadia Cloud + self K8s | ~$248 + ~$200 K8s = ~$448 | Medium |
| Self NATS + managed K8s | ~$120 + ~$300 = ~$420 | Medium |

**Recommendation**: Start with self-hosted Active-Passive (~$340/month). Evaluate Synadia Cloud if operational burden becomes significant.

---

## Recommendations for kgents SaaS

### Phase 10 (Evaluation/Design)
1. Document current single-region architecture
2. Define RPO/RTO targets (proposed: API RTO <5min, NATS RPO <5min)
3. Design failover procedures
4. Create DR runbook section
5. Cost approval for ~$340/month additional spend

### Phase 11 (Implementation)
1. Deploy second NATS cluster in DR region
2. Configure gateway connectivity
3. Set up stream mirroring for critical streams (AGENTESE, EVENTS)
4. Deploy Velero for cluster backup
5. Configure DNS failover

### Phase 12+ (Optimization)
1. Evaluate Virtual Streams for active-active
2. Implement automated DR testing
3. Consider Synadia Cloud migration
4. Add cross-region observability

---

## References

- [NATS JetStream Clustering](https://docs.nats.io/running-a-nats-service/configuration/clustering/jetstream_clustering)
- [NATS Super-Cluster Examples](https://natsbyexample.com/examples/use-cases/cross-region-streams-supercluster/cli)
- [Multi-Region Consistency Models (Synadia)](https://www.synadia.com/blog/multi-cluster-consistency-models)
- [Azure AKS Active-Passive](https://learn.microsoft.com/en-us/azure/aks/active-passive-solution)
- [Kubernetes DR Best Practices (Portworx)](https://portworx.com/kubernetes-disaster-recovery/)
- [Synadia Cloud Pricing](https://docs.synadia.com/cloud/pricing)

---

*Research Phase Complete. Entropy: 0.03 spent.*

⟿[DEVELOP]
