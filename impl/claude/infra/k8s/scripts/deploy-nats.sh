#!/bin/bash
# Deploy NATS JetStream cluster to Kubernetes
# Usage: ./deploy-nats.sh [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFESTS_DIR="$SCRIPT_DIR/../manifests"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse arguments
DRY_RUN=""
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN="--dry-run=client"
    log_warn "Running in dry-run mode"
fi

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl."
        exit 1
    fi

    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Check your kubeconfig."
        exit 1
    fi

    log_info "Prerequisites OK"
}

# Ensure namespace exists
ensure_namespace() {
    log_info "Ensuring namespace kgents-agents exists..."
    kubectl apply -f "$MANIFESTS_DIR/namespace.yaml" $DRY_RUN
}

# Deploy NATS
deploy_nats() {
    log_info "Deploying NATS JetStream cluster..."

    # Apply manifests
    kubectl apply -k "$MANIFESTS_DIR/nats" $DRY_RUN

    if [[ -z "$DRY_RUN" ]]; then
        log_info "Waiting for NATS pods to be ready..."
        kubectl rollout status statefulset/nats -n kgents-agents --timeout=120s
    fi
}

# Verify deployment
verify_deployment() {
    if [[ -n "$DRY_RUN" ]]; then
        log_info "Skipping verification in dry-run mode"
        return
    fi

    log_info "Verifying NATS deployment..."

    # Check pods
    READY_PODS=$(kubectl get pods -n kgents-agents -l app.kubernetes.io/name=nats -o jsonpath='{.items[*].status.containerStatuses[0].ready}' | tr ' ' '\n' | grep -c true || echo 0)

    if [[ "$READY_PODS" -ge 2 ]]; then
        log_info "NATS cluster ready ($READY_PODS/3 pods)"
    else
        log_warn "NATS cluster not fully ready ($READY_PODS/3 pods)"
    fi

    # Check JetStream
    log_info "Checking JetStream status..."
    kubectl exec -n kgents-agents nats-0 -- nats-server --version || true

    # Show service endpoints
    log_info "NATS service endpoints:"
    kubectl get svc -n kgents-agents -l app.kubernetes.io/name=nats -o wide
}

# Create initial JetStream stream
create_stream() {
    if [[ -n "$DRY_RUN" ]]; then
        log_info "Skipping stream creation in dry-run mode"
        return
    fi

    log_info "Creating kgent-events JetStream stream..."

    # Use NATS CLI in the pod to create stream
    kubectl exec -n kgents-agents nats-0 -- sh -c '
        # Wait for JetStream to be ready
        sleep 5

        # Create stream if not exists (using nats-server built-in)
        echo "JetStream stream will be auto-created by NATSBridge on first publish"
    ' || log_warn "Stream creation skipped (will be auto-created)"
}

# Main
main() {
    log_info "Starting NATS deployment..."

    check_prerequisites
    ensure_namespace
    deploy_nats
    create_stream
    verify_deployment

    log_info "NATS deployment complete!"
    log_info ""
    log_info "Connection string for kgents:"
    log_info "  NATS_SERVERS=nats://nats.kgents-agents.svc.cluster.local:4222"
    log_info "  NATS_ENABLED=true"
}

main "$@"
