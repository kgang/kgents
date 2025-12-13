#!/bin/bash
# Database Triad Teardown Script
#
# Removes the Database Triad and optionally the Kind cluster.
#
# Usage:
#   ./teardown-triad.sh         # Keep cluster, remove triad
#   ./teardown-triad.sh --full  # Remove cluster entirely
#
# AGENTESE: self.vitals.triad.forget

set -e

CLUSTER_NAME="kgents-triad"
NAMESPACE="kgents-triad"
FULL_TEARDOWN="${1:-}"

echo "=== Database Triad Teardown ==="
echo ""

# Check if cluster exists
if ! kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    echo "Cluster '$CLUSTER_NAME' does not exist"
    exit 0
fi

kubectl config use-context "kind-${CLUSTER_NAME}" 2>/dev/null || true

if [[ "$FULL_TEARDOWN" == "--full" ]]; then
    echo "Full teardown requested - deleting entire cluster..."
    kind delete cluster --name "$CLUSTER_NAME"
    echo ""
    echo "Cluster '$CLUSTER_NAME' deleted"
else
    echo "Removing Database Triad resources (keeping cluster)..."
    echo ""

    # Delete Synapse first (stops CDC)
    echo "Removing Synapse CronJob..."
    kubectl delete cronjob -n "$NAMESPACE" synapse-cdc 2>/dev/null || true
    kubectl delete jobs -n "$NAMESPACE" -l app.kubernetes.io/name=synapse 2>/dev/null || true

    # Delete services and deployments
    echo "Removing Redis..."
    kubectl delete deployment -n "$NAMESPACE" triad-redis 2>/dev/null || true
    kubectl delete svc -n "$NAMESPACE" triad-redis 2>/dev/null || true

    echo "Removing Qdrant..."
    kubectl delete statefulset -n "$NAMESPACE" triad-qdrant 2>/dev/null || true
    kubectl delete svc -n "$NAMESPACE" triad-qdrant 2>/dev/null || true
    kubectl delete svc -n "$NAMESPACE" triad-qdrant-headless 2>/dev/null || true

    echo "Removing PostgreSQL..."
    kubectl delete statefulset -n "$NAMESPACE" triad-postgres 2>/dev/null || true
    kubectl delete svc -n "$NAMESPACE" triad-postgres 2>/dev/null || true
    kubectl delete svc -n "$NAMESPACE" triad-postgres-headless 2>/dev/null || true

    # Delete PVCs (data loss!)
    echo "Removing PersistentVolumeClaims (data will be lost)..."
    kubectl delete pvc -n "$NAMESPACE" -l app.kubernetes.io/part-of=kgents 2>/dev/null || true

    # Delete configmaps and secrets
    echo "Removing ConfigMaps and Secrets..."
    kubectl delete configmap -n "$NAMESPACE" -l app.kubernetes.io/part-of=kgents 2>/dev/null || true
    kubectl delete secret -n "$NAMESPACE" triad-postgres 2>/dev/null || true
    kubectl delete secret -n "$NAMESPACE" synapse-credentials 2>/dev/null || true

    # Optionally delete namespace
    read -p "Delete namespace '$NAMESPACE'? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete namespace "$NAMESPACE" 2>/dev/null || true
    fi

    echo ""
    echo "Database Triad removed"
    echo "Cluster '$CLUSTER_NAME' still exists"
fi

echo ""
echo "=== Teardown Complete ==="
