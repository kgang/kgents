#!/usr/bin/env bash
# =============================================================================
# Chromatic Setup Script
# =============================================================================
# Validates Chromatic configuration and guides through setup.
#
# Usage:
#   ./scripts/setup-chromatic.sh           # Interactive setup
#   ./scripts/setup-chromatic.sh --check   # Verify configuration only
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}==============================================================================${NC}"
echo -e "${BLUE}                    Chromatic Visual Testing Setup${NC}"
echo -e "${BLUE}==============================================================================${NC}"
echo

# Change to web directory
cd "$WEB_DIR"

# Check mode
CHECK_ONLY=false
if [[ "${1:-}" == "--check" ]]; then
    CHECK_ONLY=true
    echo -e "${BLUE}Running in check mode...${NC}"
    echo
fi

# Track issues
ISSUES=0

# -----------------------------------------------------------------------------
# Check 1: Node.js
# -----------------------------------------------------------------------------
echo -e "${BLUE}[1/6] Checking Node.js...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "  ${GREEN}OK${NC} Node.js installed: $NODE_VERSION"
else
    echo -e "  ${RED}FAIL${NC} Node.js not found"
    echo -e "  ${YELLOW}Install from: https://nodejs.org/${NC}"
    ((ISSUES++))
fi

# -----------------------------------------------------------------------------
# Check 2: npm dependencies
# -----------------------------------------------------------------------------
echo -e "${BLUE}[2/6] Checking npm dependencies...${NC}"
if [[ -d "node_modules" ]]; then
    echo -e "  ${GREEN}OK${NC} node_modules exists"
else
    echo -e "  ${YELLOW}WARN${NC} node_modules not found"
    if [[ "$CHECK_ONLY" == false ]]; then
        echo -e "  ${BLUE}Installing dependencies...${NC}"
        npm install
        echo -e "  ${GREEN}OK${NC} Dependencies installed"
    else
        echo -e "  ${YELLOW}Run 'npm install' to install dependencies${NC}"
        ((ISSUES++))
    fi
fi

# -----------------------------------------------------------------------------
# Check 3: Chromatic package
# -----------------------------------------------------------------------------
echo -e "${BLUE}[3/6] Checking Chromatic package...${NC}"
if npm list chromatic &> /dev/null; then
    CHROMATIC_VERSION=$(npm list chromatic --depth=0 2>/dev/null | grep chromatic | sed 's/.*@//')
    echo -e "  ${GREEN}OK${NC} Chromatic installed: $CHROMATIC_VERSION"
else
    echo -e "  ${RED}FAIL${NC} Chromatic not installed"
    if [[ "$CHECK_ONLY" == false ]]; then
        echo -e "  ${BLUE}Installing chromatic...${NC}"
        npm install --save-dev chromatic
        echo -e "  ${GREEN}OK${NC} Chromatic installed"
    else
        echo -e "  ${YELLOW}Add chromatic to devDependencies${NC}"
        ((ISSUES++))
    fi
fi

# -----------------------------------------------------------------------------
# Check 4: Storybook configuration
# -----------------------------------------------------------------------------
echo -e "${BLUE}[4/6] Checking Storybook configuration...${NC}"
if [[ -f ".storybook/main.ts" ]]; then
    echo -e "  ${GREEN}OK${NC} .storybook/main.ts exists"
else
    echo -e "  ${RED}FAIL${NC} .storybook/main.ts not found"
    echo -e "  ${YELLOW}Run 'npx storybook init' to initialize Storybook${NC}"
    ((ISSUES++))
fi

if [[ -f ".chromatic.config.json" ]]; then
    echo -e "  ${GREEN}OK${NC} .chromatic.config.json exists"
else
    echo -e "  ${YELLOW}WARN${NC} .chromatic.config.json not found (optional)"
fi

# -----------------------------------------------------------------------------
# Check 5: Storybook build
# -----------------------------------------------------------------------------
echo -e "${BLUE}[5/6] Checking Storybook build...${NC}"
if npm run build-storybook --dry-run &> /dev/null; then
    echo -e "  ${GREEN}OK${NC} build-storybook script exists"

    if [[ "$CHECK_ONLY" == false ]]; then
        echo -e "  ${BLUE}Building Storybook (this may take a minute)...${NC}"
        if npm run build-storybook; then
            echo -e "  ${GREEN}OK${NC} Storybook build successful"
        else
            echo -e "  ${RED}FAIL${NC} Storybook build failed"
            ((ISSUES++))
        fi
    fi
else
    echo -e "  ${RED}FAIL${NC} build-storybook script not found"
    ((ISSUES++))
fi

# -----------------------------------------------------------------------------
# Check 6: Project token
# -----------------------------------------------------------------------------
echo -e "${BLUE}[6/6] Checking Chromatic project token...${NC}"
if [[ -n "${CHROMATIC_PROJECT_TOKEN:-}" ]]; then
    # Mask token for display
    TOKEN_PREVIEW="${CHROMATIC_PROJECT_TOKEN:0:8}..."
    echo -e "  ${GREEN}OK${NC} CHROMATIC_PROJECT_TOKEN is set ($TOKEN_PREVIEW)"
else
    echo -e "  ${YELLOW}WARN${NC} CHROMATIC_PROJECT_TOKEN not set in environment"
    echo
    echo -e "  ${BLUE}To set up the project token:${NC}"
    echo -e "  1. Go to ${BLUE}https://www.chromatic.com/${NC}"
    echo -e "  2. Sign in with GitHub"
    echo -e "  3. Create or select the kgents project"
    echo -e "  4. Copy the project token from settings"
    echo -e "  5. Add to GitHub Secrets as CHROMATIC_PROJECT_TOKEN"
    echo
    echo -e "  ${BLUE}For local testing:${NC}"
    echo -e "  export CHROMATIC_PROJECT_TOKEN=your-token-here"
    echo
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo
echo -e "${BLUE}==============================================================================${NC}"
if [[ $ISSUES -eq 0 ]]; then
    echo -e "${GREEN}All checks passed!${NC}"
    echo
    echo -e "Next steps:"
    echo -e "  1. Set CHROMATIC_PROJECT_TOKEN (if not done)"
    echo -e "  2. Run: ${BLUE}npm run chromatic${NC}"
    echo -e "  3. Push to GitHub to trigger CI workflow"
    echo
    echo -e "See ${BLUE}VISUAL_TESTING.md${NC} for full documentation."
else
    echo -e "${RED}Found $ISSUES issue(s)${NC}"
    echo
    echo -e "Fix the issues above and run this script again."
fi
echo -e "${BLUE}==============================================================================${NC}"

exit $ISSUES
