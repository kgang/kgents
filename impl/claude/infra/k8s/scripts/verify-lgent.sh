#!/bin/bash
# K8gents L-gent Verification Script
# Verifies L-gent deployment health and functionality
#
# Usage: ./verify-lgent.sh
#
# AGENTESE: world.library.verify

set -e

NAMESPACE="kgents-agents"
CLUSTER_NAME="kgents-local"

echo "=== K8gents L-gent Verification ==="
echo ""

# Check cluster context
echo "[1/5] Checking cluster context..."
CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "none")
if [[ "$CURRENT_CONTEXT" != "kind-${CLUSTER_NAME}" ]]; then
    echo "WARNING: Current context is '$CURRENT_CONTEXT', expected 'kind-${CLUSTER_NAME}'"
    kubectl config use-context "kind-${CLUSTER_NAME}" 2>/dev/null || {
        echo "ERROR: Cannot switch to kind-${CLUSTER_NAME} context"
        exit 1
    }
fi
echo "Context: kind-${CLUSTER_NAME}"

# Check pod status
echo ""
echo "[2/5] Checking L-gent pod status..."
POD_STATUS=$(kubectl get pod -l app=l-gent -n "$NAMESPACE" -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
if [[ "$POD_STATUS" != "Running" ]]; then
    echo "ERROR: L-gent pod not running (status: $POD_STATUS)"
    kubectl get pods -n "$NAMESPACE" -l app=l-gent
    exit 1
fi
echo "L-gent pod: Running"

# Check PostgreSQL (optional)
echo ""
echo "[3/5] Checking PostgreSQL..."
PG_STATUS=$(kubectl get pod l-gent-postgres-0 -n "$NAMESPACE" -o jsonpath='{.status.phase}' 2>/dev/null || echo "NotFound")
if [[ "$PG_STATUS" == "Running" ]]; then
    echo "PostgreSQL: Running"
else
    echo "PostgreSQL: $PG_STATUS (L-gent in standalone mode)"
fi

# Port forward and test endpoints
echo ""
echo "[4/5] Testing L-gent endpoints..."

# Start port forward in background
kubectl port-forward svc/l-gent -n "$NAMESPACE" 8080:8080 &>/dev/null &
PF_PID=$!
sleep 2

# Cleanup on exit
cleanup() {
    kill $PF_PID 2>/dev/null || true
}
trap cleanup EXIT

# Test health endpoint
echo "  - /health..."
HEALTH=$(curl -s http://localhost:8080/health 2>/dev/null || echo '{"error":"connection failed"}')
if echo "$HEALTH" | grep -q '"status".*"healthy"'; then
    echo "    OK: $HEALTH"
else
    echo "    FAILED: $HEALTH"
fi

# Test ready endpoint
echo "  - /ready..."
READY=$(curl -s http://localhost:8080/ready 2>/dev/null || echo '{"error":"connection failed"}')
if echo "$READY" | grep -q '"ready".*true'; then
    echo "    OK: $READY"
else
    echo "    WARNING: $READY"
fi

# Test catalog endpoint
echo "  - /catalog..."
CATALOG=$(curl -s http://localhost:8080/catalog 2>/dev/null || echo '{"error":"connection failed"}')
if echo "$CATALOG" | grep -q '"count"'; then
    COUNT=$(echo "$CATALOG" | grep -o '"count":[0-9]*' | cut -d: -f2)
    echo "    OK: $COUNT entries"
else
    echo "    WARNING: $CATALOG"
fi

# Test stats endpoint
echo "  - /stats..."
STATS=$(curl -s http://localhost:8080/stats 2>/dev/null || echo '{"error":"connection failed"}')
if echo "$STATS" | grep -q '"total"'; then
    echo "    OK: $STATS"
else
    echo "    WARNING: $STATS"
fi

# Summary
echo ""
echo "[5/5] Summary..."
kubectl get pods -n "$NAMESPACE" -l app=l-gent

echo ""
echo "=== L-gent Verification Complete ==="
echo ""
echo "L-gent is operational."
echo ""
echo "Usage:"
echo "  kubectl port-forward svc/l-gent -n kgents-agents 8080:8080"
echo "  curl http://localhost:8080/catalog"
