#!/bin/bash
# chaos-test.sh - Basic chaos engineering tests for kgents SaaS
#
# Phase 9: Production Hardening
#
# Usage:
#   ./chaos-test.sh <scenario>
#
# Scenarios:
#   api-kill      - Kill an API pod and measure recovery
#   nats-kill     - Kill NATS leader and measure recovery
#   network-block - Simulate network partition to NATS
#   all           - Run all scenarios sequentially
#   health-check  - Just check current health status
#
# Requirements:
#   - kubectl configured for target cluster
#   - jq installed
#   - Appropriate RBAC permissions

set -e

# Configuration
NAMESPACE_API="${NAMESPACE_API:-kgents-triad}"
NAMESPACE_NATS="${NAMESPACE_NATS:-kgents-agents}"
TIMEOUT="${TIMEOUT:-120}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

measure_time() {
    local start=$1
    local end=$(date +%s)
    echo $((end - start))
}

health_check() {
    log_info "=== Health Check ==="

    # Check API pods
    log_info "API Pods:"
    kubectl get pods -n "$NAMESPACE_API" -l app.kubernetes.io/name=kgent-api -o wide

    echo ""

    # Check NATS pods
    log_info "NATS Pods:"
    kubectl get pods -n "$NAMESPACE_NATS" -l app.kubernetes.io/name=nats -o wide

    echo ""

    # Check API health endpoints
    log_info "API Health:"
    POD=$(kubectl get pods -n "$NAMESPACE_API" -l app.kubernetes.io/name=kgent-api -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

    if [ -n "$POD" ]; then
        kubectl exec -n "$NAMESPACE_API" "$POD" -- curl -s localhost:8000/health 2>/dev/null | jq . || echo "  (health check failed)"
        echo ""
        log_info "SaaS Health:"
        kubectl exec -n "$NAMESPACE_API" "$POD" -- curl -s localhost:8000/health/saas 2>/dev/null | jq . || echo "  (saas health check failed)"
    else
        log_warn "No API pods found"
    fi
}

scenario_api_kill() {
    log_info "=== Scenario: API Pod Kill ==="
    log_info "SLA: < 30 seconds recovery"
    echo ""

    # Get current pod count
    INITIAL_PODS=$(kubectl get pods -n "$NAMESPACE_API" -l app.kubernetes.io/name=kgent-api --no-headers | wc -l | tr -d ' ')
    log_info "Initial pod count: $INITIAL_PODS"

    # Get pod to kill
    POD=$(kubectl get pods -n "$NAMESPACE_API" -l app.kubernetes.io/name=kgent-api -o jsonpath='{.items[0].metadata.name}')
    if [ -z "$POD" ]; then
        log_error "No API pods found"
        return 1
    fi

    log_info "Killing pod: $POD"
    START=$(date +%s)

    # Delete the pod
    kubectl delete pod "$POD" -n "$NAMESPACE_API" --grace-period=0 --force 2>/dev/null || \
        kubectl delete pod "$POD" -n "$NAMESPACE_API"

    # Wait for recovery
    log_info "Waiting for new pod to be ready..."
    if kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kgent-api -n "$NAMESPACE_API" --timeout="${TIMEOUT}s" 2>/dev/null; then
        RECOVERY_TIME=$(measure_time "$START")
        log_info "Recovery time: ${RECOVERY_TIME} seconds"

        if [ "$RECOVERY_TIME" -lt 30 ]; then
            echo -e "${GREEN}PASS${NC}: Recovery within SLA (< 30s)"
        else
            echo -e "${YELLOW}WARN${NC}: Recovery exceeded SLA (${RECOVERY_TIME}s > 30s)"
        fi
    else
        log_error "Pod did not recover within timeout"
        return 1
    fi

    # Verify pod count restored
    FINAL_PODS=$(kubectl get pods -n "$NAMESPACE_API" -l app.kubernetes.io/name=kgent-api --no-headers | grep Running | wc -l | tr -d ' ')
    log_info "Final pod count: $FINAL_PODS"

    echo ""
    return 0
}

scenario_nats_kill() {
    log_info "=== Scenario: NATS Leader Kill ==="
    log_info "SLA: < 60 seconds recovery"
    echo ""

    # Check if NATS is running
    NATS_PODS=$(kubectl get pods -n "$NAMESPACE_NATS" -l app.kubernetes.io/name=nats --no-headers 2>/dev/null | wc -l | tr -d ' ')
    if [ "$NATS_PODS" -eq 0 ]; then
        log_warn "No NATS pods found, skipping scenario"
        return 0
    fi

    log_info "Initial NATS pods: $NATS_PODS"

    # Kill nats-0 (typically the leader in a fresh cluster)
    log_info "Killing nats-0 (assumed leader)"
    START=$(date +%s)

    kubectl delete pod nats-0 -n "$NAMESPACE_NATS" --grace-period=0 --force 2>/dev/null || \
        kubectl delete pod nats-0 -n "$NAMESPACE_NATS"

    # Wait for recovery
    log_info "Waiting for NATS cluster recovery..."
    if kubectl wait --for=condition=ready pod/nats-0 -n "$NAMESPACE_NATS" --timeout="${TIMEOUT}s" 2>/dev/null; then
        RECOVERY_TIME=$(measure_time "$START")
        log_info "Recovery time: ${RECOVERY_TIME} seconds"

        if [ "$RECOVERY_TIME" -lt 60 ]; then
            echo -e "${GREEN}PASS${NC}: Recovery within SLA (< 60s)"
        else
            echo -e "${YELLOW}WARN${NC}: Recovery exceeded SLA (${RECOVERY_TIME}s > 60s)"
        fi
    else
        log_error "NATS did not recover within timeout"
        return 1
    fi

    # Check circuit breaker state
    log_info "Checking circuit breaker state..."
    sleep 5  # Allow time for API to reconnect
    POD=$(kubectl get pods -n "$NAMESPACE_API" -l app.kubernetes.io/name=kgent-api -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    if [ -n "$POD" ]; then
        NATS_STATUS=$(kubectl exec -n "$NAMESPACE_API" "$POD" -- curl -s localhost:8000/health/saas 2>/dev/null | jq -r '.nats.status // "unknown"')
        log_info "NATS status after recovery: $NATS_STATUS"
    fi

    echo ""
    return 0
}

scenario_network_block() {
    log_info "=== Scenario: Network Partition (NATS Unreachable) ==="
    log_info "SLA: Circuit breaker opens, recovery < 90 seconds after restore"
    echo ""

    # Check prerequisites
    POD=$(kubectl get pods -n "$NAMESPACE_API" -l app.kubernetes.io/name=kgent-api -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    if [ -z "$POD" ]; then
        log_warn "No API pods found, skipping scenario"
        return 0
    fi

    # Get initial NATS status
    INITIAL_STATUS=$(kubectl exec -n "$NAMESPACE_API" "$POD" -- curl -s localhost:8000/health/saas 2>/dev/null | jq -r '.nats.status // "unknown"')
    log_info "Initial NATS status: $INITIAL_STATUS"

    # Apply blocking network policy
    log_info "Applying network policy to block NATS traffic..."
    cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: chaos-block-nats
  namespace: $NAMESPACE_API
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: kgent-api
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: kgents-observability
    - to:
        - ipBlock:
            cidr: 10.96.0.0/12
            except:
              - 10.96.0.0/24  # Block NATS service CIDR (adjust as needed)
EOF

    START=$(date +%s)

    # Wait for circuit breaker to open
    log_info "Waiting for circuit breaker to activate..."
    CIRCUIT_OPEN=false
    for i in $(seq 1 30); do
        STATUS=$(kubectl exec -n "$NAMESPACE_API" "$POD" -- curl -s localhost:8000/health/saas 2>/dev/null | jq -r '.nats.status // "unknown"')
        if [ "$STATUS" = "circuit_open" ] || [ "$STATUS" = "disconnected" ]; then
            CIRCUIT_OPEN=true
            OPEN_TIME=$(measure_time "$START")
            log_info "Circuit breaker opened after ${OPEN_TIME} seconds"
            break
        fi
        sleep 2
    done

    if [ "$CIRCUIT_OPEN" = false ]; then
        log_warn "Circuit breaker did not open (may already be in fallback mode)"
    fi

    # Remove network policy
    log_info "Removing network policy to restore connectivity..."
    kubectl delete networkpolicy chaos-block-nats -n "$NAMESPACE_API" 2>/dev/null || true

    # Wait for recovery
    log_info "Waiting for recovery..."
    RECOVERED=false
    for i in $(seq 1 45); do
        STATUS=$(kubectl exec -n "$NAMESPACE_API" "$POD" -- curl -s localhost:8000/health/saas 2>/dev/null | jq -r '.nats.status // "unknown"')
        if [ "$STATUS" = "connected" ] || [ "$STATUS" = "ok" ]; then
            RECOVERED=true
            RECOVERY_TIME=$(measure_time "$START")
            log_info "Connection recovered after ${RECOVERY_TIME} seconds"
            break
        fi
        sleep 2
    done

    if [ "$RECOVERED" = true ]; then
        if [ "$RECOVERY_TIME" -lt 90 ]; then
            echo -e "${GREEN}PASS${NC}: Recovery within SLA (< 90s)"
        else
            echo -e "${YELLOW}WARN${NC}: Recovery exceeded SLA (${RECOVERY_TIME}s > 90s)"
        fi
    else
        log_warn "Did not observe full recovery (may be in permanent fallback mode)"
    fi

    echo ""
    return 0
}

run_all() {
    log_info "=== Running All Chaos Scenarios ==="
    echo ""

    health_check
    echo ""
    echo "---"
    echo ""

    scenario_api_kill
    echo "---"
    echo ""

    scenario_nats_kill
    echo "---"
    echo ""

    scenario_network_block
    echo "---"
    echo ""

    log_info "=== All Scenarios Complete ==="
    health_check
}

# Main
case "${1:-help}" in
    api-kill)
        scenario_api_kill
        ;;
    nats-kill)
        scenario_nats_kill
        ;;
    network-block)
        scenario_network_block
        ;;
    all)
        run_all
        ;;
    health-check|health)
        health_check
        ;;
    *)
        echo "Usage: $0 {api-kill|nats-kill|network-block|all|health-check}"
        echo ""
        echo "Scenarios:"
        echo "  api-kill      - Kill an API pod and measure recovery (SLA: <30s)"
        echo "  nats-kill     - Kill NATS leader and measure recovery (SLA: <60s)"
        echo "  network-block - Simulate network partition to NATS (SLA: <90s)"
        echo "  all           - Run all scenarios sequentially"
        echo "  health-check  - Check current health status"
        echo ""
        echo "Environment variables:"
        echo "  NAMESPACE_API  - API namespace (default: kgents-triad)"
        echo "  NAMESPACE_NATS - NATS namespace (default: kgents-agents)"
        echo "  TIMEOUT        - Wait timeout in seconds (default: 120)"
        exit 1
        ;;
esac
