#!/bin/bash
# K8gents Cluster Verification Script
# Verifies Kind cluster health and CRD registration
#
# Usage: ./verify-cluster.sh
#
# AGENTESE: world.cluster.manifest

set -e

CLUSTER_NAME="kgents-local"
NAMESPACE="kgents-agents"

echo "=== K8gents Cluster Verification ==="
echo ""

ERRORS=0

# Check cluster exists
echo "[1/6] Checking cluster..."
if ! kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    echo "FAIL: Cluster '$CLUSTER_NAME' not found"
    echo "Run: ./setup-cluster.sh"
    exit 1
fi
echo "OK: Cluster exists"

# Check kubectl context
echo ""
echo "[2/6] Checking kubectl context..."
if ! kubectl cluster-info --context "kind-${CLUSTER_NAME}" &>/dev/null; then
    echo "FAIL: Cannot connect to cluster"
    ERRORS=$((ERRORS + 1))
else
    echo "OK: kubectl connected"
fi

# Check namespace
echo ""
echo "[3/6] Checking namespace..."
if ! kubectl get ns "$NAMESPACE" &>/dev/null; then
    echo "FAIL: Namespace '$NAMESPACE' not found"
    ERRORS=$((ERRORS + 1))
else
    echo "OK: Namespace exists"
fi

# Check CRDs
echo ""
echo "[4/6] Checking CRDs..."

CRDS=("agents.kgents.io" "pheromones.kgents.io" "memories.kgents.io" "umwelts.kgents.io" "proposals.kgents.io")
for CRD in "${CRDS[@]}"; do
    if kubectl get crd "$CRD" &>/dev/null; then
        echo "OK: $CRD"
    else
        echo "FAIL: $CRD not found"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check node status
echo ""
echo "[5/6] Checking nodes..."
NODE_STATUS=$(kubectl get nodes -o jsonpath='{.items[0].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "Unknown")
if [ "$NODE_STATUS" = "True" ]; then
    echo "OK: Node is Ready"
else
    echo "WARN: Node status: $NODE_STATUS"
fi

# Check system pods
echo ""
echo "[6/6] Checking system pods..."
KUBE_SYSTEM_PODS=$(kubectl get pods -n kube-system --no-headers 2>/dev/null | wc -l | tr -d ' ')
RUNNING_PODS=$(kubectl get pods -n kube-system --no-headers 2>/dev/null | grep -c "Running" || echo "0")
echo "kube-system: $RUNNING_PODS/$KUBE_SYSTEM_PODS pods running"

# Summary
echo ""
echo "=== Verification Summary ==="
if [ $ERRORS -eq 0 ]; then
    echo "Status: HEALTHY"
    echo ""
    echo "Cluster is ready for operator deployment."
    echo "Next: ./deploy-operators.sh"
    exit 0
else
    echo "Status: UNHEALTHY ($ERRORS errors)"
    echo ""
    echo "Fix errors before proceeding."
    exit 1
fi
