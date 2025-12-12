#!/bin/bash
# Create claude-auth Secret from ~/.claude directory
#
# This script creates a K8s Secret containing Claude CLI auth credentials
# from your local ~/.claude directory. This is the cluster-native way to
# provide LLM credentials - no hostPath mounts!
#
# Usage:
#   ./create-claude-secret.sh [namespace]
#
# Prerequisites:
#   - kubectl configured with cluster access
#   - ~/.claude/config.json exists
#   - ~/.claude/credentials.json exists (run `claude` to authenticate)
#
# AGENTESE: world.morpheus.bootstrap.script

set -euo pipefail

NAMESPACE="${1:-kgents}"
SECRET_NAME="claude-auth"
CLAUDE_DIR="${HOME}/.claude"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Install it first."
        exit 1
    fi

    # Check cluster access
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Check your kubeconfig."
        exit 1
    fi

    # Check Claude directory
    if [[ ! -d "${CLAUDE_DIR}" ]]; then
        log_error "Claude config directory not found: ${CLAUDE_DIR}"
        log_error "Run 'claude' to authenticate first."
        exit 1
    fi

    # Check config.json
    if [[ ! -f "${CLAUDE_DIR}/config.json" ]]; then
        log_error "Config not found: ${CLAUDE_DIR}/config.json"
        exit 1
    fi

    # Check credentials.json
    if [[ ! -f "${CLAUDE_DIR}/credentials.json" ]]; then
        log_error "Credentials not found: ${CLAUDE_DIR}/credentials.json"
        log_error "Run 'claude' to authenticate first."
        exit 1
    fi

    log_info "All prerequisites met."
}

# Create namespace if needed
ensure_namespace() {
    if ! kubectl get namespace "${NAMESPACE}" &> /dev/null; then
        log_info "Creating namespace: ${NAMESPACE}"
        kubectl create namespace "${NAMESPACE}"
    else
        log_info "Namespace exists: ${NAMESPACE}"
    fi
}

# Delete existing secret if present
cleanup_existing() {
    if kubectl get secret "${SECRET_NAME}" -n "${NAMESPACE}" &> /dev/null; then
        log_warn "Existing secret found. Deleting..."
        kubectl delete secret "${SECRET_NAME}" -n "${NAMESPACE}"
    fi
}

# Create the secret
create_secret() {
    log_info "Creating secret ${SECRET_NAME} in namespace ${NAMESPACE}..."

    kubectl create secret generic "${SECRET_NAME}" \
        --namespace="${NAMESPACE}" \
        --from-file=config.json="${CLAUDE_DIR}/config.json" \
        --from-file=credentials.json="${CLAUDE_DIR}/credentials.json"

    # Add labels
    kubectl label secret "${SECRET_NAME}" \
        --namespace="${NAMESPACE}" \
        app.kubernetes.io/name=claude-auth \
        app.kubernetes.io/part-of=kgents \
        app.kubernetes.io/component=credentials \
        kgents.io/secret-type=llm-credentials

    log_info "Secret created successfully!"
}

# Verify the secret
verify_secret() {
    log_info "Verifying secret..."

    # Check secret exists
    if ! kubectl get secret "${SECRET_NAME}" -n "${NAMESPACE}" &> /dev/null; then
        log_error "Secret not found after creation!"
        exit 1
    fi

    # Check keys
    KEYS=$(kubectl get secret "${SECRET_NAME}" -n "${NAMESPACE}" -o jsonpath='{.data}' | jq -r 'keys[]')
    if [[ ! "${KEYS}" == *"config.json"* ]] || [[ ! "${KEYS}" == *"credentials.json"* ]]; then
        log_error "Secret missing expected keys!"
        exit 1
    fi

    log_info "Secret verified. Keys present: config.json, credentials.json"
}

# Print usage information
print_usage() {
    echo ""
    log_info "Secret is ready. Mount it in your pods like this:"
    echo ""
    cat << 'EOF'
spec:
  containers:
    - name: morpheus
      volumeMounts:
        - name: claude-auth
          mountPath: /var/run/secrets/claude
          readOnly: true
  volumes:
    - name: claude-auth
      secret:
        secretName: claude-auth
EOF
    echo ""
    log_info "Your application can read credentials from:"
    echo "  /var/run/secrets/claude/config.json"
    echo "  /var/run/secrets/claude/credentials.json"
}

# Main
main() {
    echo "=========================================="
    echo "  kgents Cluster-Native Secret Bootstrap"
    echo "=========================================="
    echo ""

    check_prerequisites
    ensure_namespace
    cleanup_existing
    create_secret
    verify_secret
    print_usage

    echo ""
    log_info "Bootstrap complete! Secrets not hostPaths."
}

main "$@"
