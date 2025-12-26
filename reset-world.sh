#!/usr/bin/env bash
# reset-world.sh — Complete system reset for kgents development
#
# Destroys all user data and rebuilds the development environment from scratch.
# Uses XDG-compliant paths for data storage.
#
# Usage:
#   ./reset-world.sh              # Interactive mode with confirmation
#   ./reset-world.sh --force      # Skip confirmation prompt
#   ./reset-world.sh --dry-run    # Show what would be destroyed without executing
#   ./reset-world.sh --help       # Show this help message
#
# Requirements:
#   - Docker and Docker Compose installed
#   - Backend code in impl/claude/
#   - Port 8000 available for API server
#
# Data Locations (XDG-compliant):
#   - Data: ~/.kgents/
#   - Config: ~/.config/kgents/
#
# Version: 3.2
# Date: 2025-12-25
#
# Changes in 3.2:
#   - Added run_migrations step to apply Alembic migrations after database initialization
#
# Changes in 3.1:
#   - Added initialize_database step to enable pgvector and create tables
#   - Fixed JSONB/GIN index compatibility in brain.py model

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

# XDG-compliant paths
# Note: For user-friendliness, kgents uses ~/.kgents as default instead of ~/.local/share/kgents
# This can be overridden with KGENTS_DATA_ROOT environment variable
# See: services/storage/provider.py
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"

KGENTS_DATA_DIR="${KGENTS_DATA_ROOT:-$HOME/.kgents}"
KGENTS_CONFIG_DIR="${XDG_CONFIG_HOME}/kgents"

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMPL_DIR="${PROJECT_ROOT}/impl/claude"
DOCKER_COMPOSE_FILE="${IMPL_DIR}/docker-compose.yml"

# Service configuration
API_URL="http://localhost:8000"
GENESIS_ENDPOINT="${API_URL}/api/genesis/seed"
MAX_WAIT_TIME=60

# Data directories to manage (aligned with services/storage/provider.py)
DATA_SUBDIRS=(
    "cosmos"      # K-Block storage
    "uploads"     # Sovereign staging area
    "vectors"     # Vector export/backup
    "witness"     # Witness marks (file backup)
    "exports"     # User exports
    "tmp"         # Temporary files
)

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly MAGENTA='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

# Flags
FORCE_MODE=false
DRY_RUN=false

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

log_info() {
    echo -e "${BLUE}▸${NC} $*"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}!${NC} $*"
}

log_error() {
    echo -e "${RED}✗${NC} $*" >&2
}

log_header() {
    echo ""
    echo -e "${BOLD}━━ $* ━━${NC}"
}

log_dry_run() {
    echo -e "${CYAN}[dry-run]${NC} $*"
}

show_banner() {
    echo ""
    echo -e "${BOLD}kgents reset-world${NC}"
    echo -e "Complete environment rebuild"
    echo ""
}

show_help() {
    cat << EOF
reset-world.sh — Complete system reset for kgents development

USAGE:
    ./reset-world.sh [OPTIONS]

OPTIONS:
    --force      Skip confirmation prompt
    --dry-run    Show actions without executing
    --help       Show this help message

DESCRIPTION:
    Complete reset: stops containers, clears data, rebuilds environment.

    Steps:
    1. Stop and remove Docker containers + volumes
    2. Clear data directories (${KGENTS_DATA_DIR}/)
    3. Clear config directories (${XDG_CONFIG_HOME}/kgents/)
    4. Rebuild and start containers
    5. Wait for PostgreSQL health check
    6. Initialize database (enable pgvector, create tables)
    7. Run database migrations (Alembic)

    Note: Genesis data is seeded automatically when you open the web UI for the first time.

DATA LOCATIONS:
    Data:   ${KGENTS_DATA_DIR}/
    Config: ${XDG_CONFIG_HOME}/kgents/

REQUIREMENTS:
    - Docker and Docker Compose
    - Backend code in impl/claude/
    - Port 8000 available for API

EXAMPLES:
    ./reset-world.sh              # Interactive with confirmation
    ./reset-world.sh --force      # Skip confirmation
    ./reset-world.sh --dry-run    # Preview actions

EOF
    exit 0
}

check_prerequisites() {
    local missing=0

    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Install from: https://docs.docker.com/get-docker/"
        missing=1
    fi

    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose not found or outdated (requires 'docker compose' command)"
        missing=1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker daemon not running. Start Docker Desktop or 'sudo systemctl start docker'"
        missing=1
    fi

    if [ ! -d "$IMPL_DIR" ]; then
        log_error "Backend code not found at: $IMPL_DIR"
        missing=1
    fi

    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        log_error "Docker Compose file not found at: $DOCKER_COMPOSE_FILE"
        missing=1
    fi

    if [ $missing -eq 1 ]; then
        log_error "Prerequisites not met. Aborting."
        exit 1
    fi

    log_success "All prerequisites met"
}

confirm_destruction() {
    if [ "$DRY_RUN" = true ]; then
        log_dry_run "Would execute full reset (use without --dry-run to proceed)"
        return 0
    fi

    if [ "$FORCE_MODE" = true ]; then
        log_warning "Force mode enabled, skipping confirmation"
        return 0
    fi

    echo ""
    echo -e "${YELLOW}This will DELETE:${NC}"
    echo "  • Docker containers and volumes"
    echo "  • ${KGENTS_DATA_DIR}/"
    echo "  • ${KGENTS_CONFIG_DIR}/"
    echo ""
    read -p "Type 'reset' to confirm: " confirm

    if [ "$confirm" != "reset" ]; then
        log_error "Aborted"
        exit 1
    fi
}

stop_containers() {
    log_header "Stop Containers"

    cd "$IMPL_DIR"

    if [ "$DRY_RUN" = true ]; then
        log_dry_run "Would stop and remove containers"
        return 0
    fi

    if docker compose ps --quiet 2>/dev/null | grep -q .; then
        log_info "Stopping containers"
        if docker compose down -v 2>&1; then
            log_success "Containers removed"
        else
            log_warning "Failed to remove containers (may not exist)"
        fi
    else
        log_info "No containers running"
    fi
}

clear_data_directories() {
    log_info "Clearing data directories"

    if [ "$DRY_RUN" = true ]; then
        for subdir in "${DATA_SUBDIRS[@]}"; do
            local full_path="${KGENTS_DATA_DIR}/${subdir}"
            [ -d "$full_path" ] && log_dry_run "Would remove: $full_path"
        done
        [ -d "$KGENTS_CONFIG_DIR" ] && log_dry_run "Would remove: $KGENTS_CONFIG_DIR"
        return 0
    fi

    local removed_count=0
    for subdir in "${DATA_SUBDIRS[@]}"; do
        local full_path="${KGENTS_DATA_DIR}/${subdir}"
        if [ -d "$full_path" ] && [ -n "$(ls -A "$full_path" 2>/dev/null)" ]; then
            rm -rf "${full_path:?}"/* 2>/dev/null || log_warning "Failed to clear: $full_path"
            removed_count=$((removed_count + 1))
        fi
    done

    if [ -d "$KGENTS_CONFIG_DIR" ] && [ -n "$(ls -A "$KGENTS_CONFIG_DIR" 2>/dev/null)" ]; then
        rm -rf "${KGENTS_CONFIG_DIR:?}"/* 2>/dev/null || log_warning "Failed to clear: $KGENTS_CONFIG_DIR"
        removed_count=$((removed_count + 1))
    fi

    if [ $removed_count -eq 0 ]; then
        log_info "No existing data to clear"
    else
        log_success "Cleared $removed_count directories"
    fi
}

rebuild_containers() {
    log_header "Rebuild Containers"

    cd "$IMPL_DIR"

    if [ "$DRY_RUN" = true ]; then
        log_dry_run "Would create data directories"
        log_dry_run "Would build Docker containers"
        return 0
    fi

    log_info "Creating data directories"
    for subdir in "${DATA_SUBDIRS[@]}"; do
        local full_path="${KGENTS_DATA_DIR}/${subdir}"
        mkdir -p "$full_path" 2>/dev/null || log_warning "Failed to create: $full_path"
    done
    mkdir -p "$KGENTS_CONFIG_DIR" 2>/dev/null || log_warning "Failed to create: $KGENTS_CONFIG_DIR"
    log_success "Directories ready"

    log_info "Building containers (this may take a few minutes)"
    if docker compose build --no-cache 2>&1 | grep -q "ERROR"; then
        log_error "Build failed, check Docker configuration"
        exit 1
    fi
    log_success "Build complete"
}

start_services() {
    log_header "Start Services"

    cd "$IMPL_DIR"

    if [ "$DRY_RUN" = true ]; then
        log_dry_run "Would start Docker Compose services"
        return 0
    fi

    log_info "Starting services"
    if ! docker compose up -d 2>&1; then
        log_error "Failed to start services"
        log_info "Check logs: cd $IMPL_DIR && docker compose logs"
        exit 1
    fi
    log_success "Services started"
}

wait_for_health() {
    log_header "Health Check"

    cd "$IMPL_DIR"

    if [ "$DRY_RUN" = true ]; then
        log_dry_run "Would wait for PostgreSQL health"
        return 0
    fi

    local elapsed=0
    local interval=2
    local spinner=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
    local spinner_idx=0

    log_info "Waiting for PostgreSQL"

    while [ $elapsed -lt $MAX_WAIT_TIME ]; do
        # Check if container is healthy
        if docker compose ps postgres 2>/dev/null | grep -q "healthy"; then
            echo ""
            log_success "PostgreSQL ready"

            # Additional connection test
            if docker compose exec -T postgres pg_isready -U kgents > /dev/null 2>&1; then
                log_success "Database connection verified"
                return 0
            fi
        fi

        # Progress indicator
        printf "\r${BLUE}▸${NC} Waiting for PostgreSQL ${spinner[$spinner_idx]} [${elapsed}s/${MAX_WAIT_TIME}s]"
        spinner_idx=$(( (spinner_idx + 1) % ${#spinner[@]} ))

        sleep $interval
        elapsed=$((elapsed + interval))
    done

    echo ""
    log_error "PostgreSQL health check timeout (${MAX_WAIT_TIME}s)"
    log_info "Container status:"
    docker compose ps postgres
    log_info "Recent logs:"
    docker compose logs --tail=20 postgres
    log_info "Troubleshooting: cd $IMPL_DIR && docker compose logs postgres"
    exit 1
}

initialize_database() {
    log_header "Initialize Database"

    cd "$IMPL_DIR"

    if [ "$DRY_RUN" = true ]; then
        log_dry_run "Would enable pgvector extension"
        log_dry_run "Would create database tables"
        return 0
    fi

    # Enable pgvector extension (required for vector columns)
    log_info "Enabling pgvector extension"
    if docker compose exec -T postgres psql -U kgents -d kgents -c "CREATE EXTENSION IF NOT EXISTS vector;" > /dev/null 2>&1; then
        log_success "pgvector extension enabled"
    else
        log_warning "Failed to enable pgvector (may already exist)"
    fi

    # Create all SQLAlchemy tables
    log_info "Creating database tables"
    if uv run python -c "
import asyncio
from models.base import init_db

async def main():
    engine = await init_db()
    await engine.dispose()

asyncio.run(main())
" 2>&1; then
        log_success "Database tables created"
    else
        log_error "Failed to create database tables"
        log_info "Check the error above and ensure all models are valid"
        exit 1
    fi
}

run_migrations() {
    log_header "Run Migrations"

    cd "$IMPL_DIR"

    if [ "$DRY_RUN" = true ]; then
        log_dry_run "Would apply database migrations"
        return 0
    fi

    log_info "Applying Alembic migrations"
    if uv run alembic upgrade head 2>&1; then
        log_success "Migrations applied successfully"
    else
        log_error "Failed to apply migrations"
        log_info "Check the error above and ensure migrations are valid"
        log_info "View migration history: cd $IMPL_DIR && uv run alembic history"
        exit 1
    fi
}

# Genesis seeding removed - happens during FTUE when user opens web UI
# See: impl/claude/web/src/pages/Genesis/GenesisPage.tsx

show_completion() {
    local mode_indicator=""
    if [ "$DRY_RUN" = true ]; then
        mode_indicator=" ${CYAN}[dry-run complete]${NC}"
        echo ""
        log_success "Dry-run complete — no changes made"
        echo ""
        echo "Run without --dry-run to execute reset"
        return 0
    fi

    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}${BOLD}Reset Complete${NC} (${SECONDS}s)"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BOLD}Next Steps:${NC}"
    echo ""
    echo "  1. Start API server:"
    echo "     cd impl/claude && uvicorn protocols.api.app:create_app --factory --reload --port 8000"
    echo ""
    echo "  2. Start Web UI:"
    echo "     cd impl/claude/web && npm install && npm run dev"
    echo ""
    echo "  3. Access application (Genesis will auto-seed on first load):"
    echo "     http://localhost:3000"
    echo ""
    echo -e "${BOLD}Services:${NC}"
    echo ""
    echo "  PostgreSQL: postgresql://kgents:kgents@localhost:5432/kgents"
    echo "  Status:     cd impl/claude && docker compose ps"
    echo "  Logs:       cd impl/claude && docker compose logs -f"
    echo ""
    echo -e "${BOLD}Data Locations:${NC}"
    echo ""
    echo "  Data:   ${KGENTS_DATA_DIR}/"
    echo "  Config: ${KGENTS_CONFIG_DIR}/"
    echo ""
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                FORCE_MODE=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --help|-h)
                show_help
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    # Execute phases
    show_banner
    check_prerequisites
    confirm_destruction
    stop_containers
    clear_data_directories
    rebuild_containers
    start_services
    wait_for_health
    initialize_database
    run_migrations
    show_completion

    if [ "$DRY_RUN" = false ]; then
        log_success "Reset complete"
    fi
}

# Run main function
main "$@"
