#!/bin/bash
# Database Triad Verification Script
#
# Verifies the Database Triad is healthy:
# - Postgres connectivity and outbox table
# - Qdrant readiness
# - Redis connectivity
# - Synapse CronJob status
#
# Usage: ./verify-triad.sh
#
# AGENTESE: self.vitals.triad.manifest

set -e

CLUSTER_NAME="kgents-triad"
NAMESPACE="kgents-triad"

echo "=== Database Triad Verification ==="
echo ""

# Set context
kubectl config use-context "kind-${CLUSTER_NAME}" 2>/dev/null || {
    echo "ERROR: Cluster $CLUSTER_NAME not found"
    echo "Run ./setup-triad.sh first"
    exit 1
}

# Check pods
echo "[1/5] Checking pods..."
echo ""
kubectl get pods -n "$NAMESPACE"

ALL_RUNNING=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].status.phase}' | tr ' ' '\n' | sort -u)
if echo "$ALL_RUNNING" | grep -v Running | grep -v Succeeded | grep -q .; then
    echo ""
    echo "WARNING: Some pods are not running"
fi

# Verify Postgres
echo ""
echo "[2/5] Verifying PostgreSQL (Durability)..."

POSTGRES_POD=$(kubectl get pod -n "$NAMESPACE" -l app=triad-postgres -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [[ -z "$POSTGRES_POD" ]]; then
    echo "ERROR: PostgreSQL pod not found"
else
    echo "Pod: $POSTGRES_POD"

    # Check if outbox table exists
    echo "Checking outbox table..."
    kubectl exec -n "$NAMESPACE" "$POSTGRES_POD" -- \
        psql -U triad -d triad -c "SELECT COUNT(*) as pending FROM outbox WHERE NOT processed;" 2>/dev/null || \
        echo "WARNING: Could not query outbox table"
fi

# Verify Qdrant
echo ""
echo "[3/5] Verifying Qdrant (Resonance)..."

QDRANT_POD=$(kubectl get pod -n "$NAMESPACE" -l app=triad-qdrant -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [[ -z "$QDRANT_POD" ]]; then
    echo "ERROR: Qdrant pod not found"
else
    echo "Pod: $QDRANT_POD"

    # Check health
    echo "Checking health..."
    kubectl exec -n "$NAMESPACE" "$QDRANT_POD" -- \
        curl -s http://localhost:6333/readyz 2>/dev/null && echo " OK" || \
        echo "WARNING: Qdrant not ready"
fi

# Verify Redis
echo ""
echo "[4/5] Verifying Redis (Reflex)..."

REDIS_POD=$(kubectl get pod -n "$NAMESPACE" -l app=triad-redis -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [[ -z "$REDIS_POD" ]]; then
    echo "ERROR: Redis pod not found"
else
    echo "Pod: $REDIS_POD"

    # Ping Redis
    echo "Pinging Redis..."
    kubectl exec -n "$NAMESPACE" "$REDIS_POD" -- redis-cli ping 2>/dev/null || \
        echo "WARNING: Redis not responding"
fi

# Verify Synapse CronJob
echo ""
echo "[5/5] Verifying Synapse (CDC)..."

CRONJOB_STATUS=$(kubectl get cronjob -n "$NAMESPACE" synapse-cdc -o jsonpath='{.spec.schedule}' 2>/dev/null)
if [[ -z "$CRONJOB_STATUS" ]]; then
    echo "WARNING: Synapse CronJob not found"
else
    echo "CronJob schedule: $CRONJOB_STATUS"

    # Last job status
    echo "Recent jobs:"
    kubectl get jobs -n "$NAMESPACE" -l app.kubernetes.io/name=synapse --sort-by=.metadata.creationTimestamp 2>/dev/null | tail -5 || \
        echo "No jobs found yet (CronJob may not have run)"
fi

# Summary
echo ""
echo "=== Triad Health Summary ==="
echo ""

# Semantic health indicators
POSTGRES_READY=$(kubectl get pod -n "$NAMESPACE" -l app=triad-postgres -o jsonpath='{.items[0].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
QDRANT_READY=$(kubectl get pod -n "$NAMESPACE" -l app=triad-qdrant -o jsonpath='{.items[0].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
REDIS_READY=$(kubectl get pod -n "$NAMESPACE" -l app=triad-redis -o jsonpath='{.items[0].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)

echo "Layer              Status"
echo "-------------------------------"
echo "Durability (PG)    ${POSTGRES_READY:-Unknown}"
echo "Resonance (Qdrant) ${QDRANT_READY:-Unknown}"
echo "Reflex (Redis)     ${REDIS_READY:-Unknown}"

if [[ "$POSTGRES_READY" == "True" && "$QDRANT_READY" == "True" && "$REDIS_READY" == "True" ]]; then
    echo ""
    echo "Triad Status: HEALTHY"
    echo "coherency_with_truth: Pending CDC sync"
else
    echo ""
    echo "Triad Status: DEGRADED"
    echo "Some components not ready"
fi

echo ""
