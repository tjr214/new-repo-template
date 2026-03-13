#!/bin/sh

# Repository Setup Script
# Creates required directories, applies scaffold output, and updates tools.

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

resolve_python_bin() {
    if command_exists python3; then
        printf "%s" "python3"
        return 0
    fi

    if command_exists python; then
        printf "%s" "python"
        return 0
    fi

    return 1
}

run_nurt_command() {
    PYTHON_BIN=$(resolve_python_bin)
    if [ $? -ne 0 ] || [ -z "$PYTHON_BIN" ]; then
        printf "${RED}${BOLD}Error: python is required for nurt command execution.${NC}\n"
        return 1
    fi

    PYTHONPATH=src NURT_UI_MODE=plain "$PYTHON_BIN" -m new_repo_template.nurt_cli "$@"
}

is_valid_target() {
    case "$1" in
        foundation|python|web|backend|desktop|mobile|tv)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

run_scaffold_command() {
    MODE="$1"
    OUTPUT_DIR="$2"
    PYTHON_BIN=$(resolve_python_bin)
    if [ $? -ne 0 ] || [ -z "$PYTHON_BIN" ]; then
        printf "${RED}${BOLD}Error: python is required for scaffold generation.${NC}\n"
        return 1
    fi

    set -- "$PYTHON_BIN" "-m" "new_repo_template.scaffold"

    for TARGET in $SCAFFOLD_TARGETS; do
        set -- "$@" "--target" "$TARGET"
    done

    if [ -n "$SCAFFOLD_AUTH" ]; then
        set -- "$@" "--auth" "$SCAFFOLD_AUTH"
    fi

    set -- "$@" "--no-interactive" "--output" "$OUTPUT_DIR"

    if [ "$MODE" = "dry-run" ]; then
        set -- "$@" "--dry-run"
    fi

    PYTHONPATH=src "$@"
}

SCAFFOLD_DRY_RUN() {
    DRY_OUTPUT_PATH="${TMPDIR:-/tmp}/new-repo-template-scaffold-dry-run"
    printf "${BLUE}Running scaffold dry-run...${NC}\n"
    if run_scaffold_command "dry-run" "$DRY_OUTPUT_PATH"; then
        printf "  ${GREEN}✓${NC} Scaffold dry-run succeeded\n"
    else
        printf "${RED}${BOLD}Error: scaffold dry-run failed${NC}\n"
        return 1
    fi
}

SCAFFOLD_APPLY() {
    TMP_SCAFFOLD_DIR=$(mktemp -d "${TMPDIR:-/tmp}/new-repo-template-scaffold.XXXXXX")
    OUTPUT_DIR="$TMP_SCAFFOLD_DIR/output"

    printf "${BLUE}Applying scaffold selection...${NC}\n"
    if run_scaffold_command "apply" "$OUTPUT_DIR"; then
        cp -R "$OUTPUT_DIR"/. .
        printf "  ${GREEN}✓${NC} Scaffold output applied\n"
    else
        rm -rf "$TMP_SCAFFOLD_DIR"
        printf "${RED}${BOLD}Error: scaffold generation failed${NC}\n"
        return 1
    fi

    rm -rf "$TMP_SCAFFOLD_DIR"
}

DRY_RUN=0
SCAFFOLD_TARGETS=""
SCAFFOLD_AUTH=""

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run|-n)
            DRY_RUN=1
            shift
            ;;
        --target)
            if [ $# -lt 2 ]; then
                printf "${RED}${BOLD}Error: --target requires a value${NC}\n"
                printf "Usage: sh install.sh [--dry-run] [--target <target>]... [--auth <clerk|better-auth>]\n"
                exit 2
            fi
            if ! is_valid_target "$2"; then
                printf "${RED}${BOLD}Error: Invalid target: %s${NC}\n" "$2"
                exit 2
            fi
            if [ -z "$SCAFFOLD_TARGETS" ]; then
                SCAFFOLD_TARGETS="$2"
            else
                SCAFFOLD_TARGETS="$SCAFFOLD_TARGETS $2"
            fi
            shift 2
            ;;
        --auth)
            if [ $# -lt 2 ]; then
                printf "${RED}${BOLD}Error: --auth requires a value${NC}\n"
                exit 2
            fi
            case "$2" in
                clerk|better-auth)
                    SCAFFOLD_AUTH="$2"
                    ;;
                *)
                    printf "${RED}${BOLD}Error: Invalid auth value: %s${NC}\n" "$2"
                    exit 2
                    ;;
            esac
            shift 2
            ;;
        *)
            printf "${RED}${BOLD}Error: Unknown argument: %s${NC}\n" "$1"
            printf "Usage: sh install.sh [--dry-run] [--target <target>]... [--auth <clerk|better-auth>]\n"
            exit 2
            ;;
    esac
done

if [ -z "$SCAFFOLD_TARGETS" ]; then
    SCAFFOLD_TARGETS="foundation"
fi

if [ "$DRY_RUN" -eq 1 ]; then
    printf "${CYAN}${BOLD}Repository Setup Script (DRY RUN)${NC}\n"
    printf "${CYAN}=================================${NC}\n\n"
    printf "${YELLOW}DRY RUN: no filesystem or git changes will be made.${NC}\n\n"

    printf "${BLUE}Resolved scaffold inputs:${NC}\n"
    printf "  - targets: %s\n" "$SCAFFOLD_TARGETS"
    if [ -n "$SCAFFOLD_AUTH" ]; then
        printf "  - auth: %s\n\n" "$SCAFFOLD_AUTH"
    else
        printf "  - auth: none\n\n"
    fi

    SCAFFOLD_DRY_RUN

    printf "\n${BLUE}Planned install actions:${NC}\n"
    printf "  - Backup install script to .template_scripts/install.sh\n"
    printf "  - Apply scaffold output in repository\n"
    printf "  - Run native BMAD dry-run via nurt before git init\n"
    printf "  - Reinitialize git repository (.git removal + git init)\n"
    printf "  - Ensure docs/tasks/completed and tests directories exist\n"
    printf "  - Create initial commit and remove install.sh\n\n"

    if [ -d "src/new_repo_template" ]; then
        printf "${BLUE}Running BMAD dry-run:${NC} nurt sync bmad --dry-run\n"
        run_nurt_command sync bmad --dry-run
    else
        printf "${YELLOW}Would skip:${NC} native nurt BMAD path unavailable\n"
    fi

    if [ -d "src/new_repo_template" ]; then
        printf "${BLUE}Running tools dry-run:${NC} nurt sync tools --dry-run\n"
        run_nurt_command sync tools --dry-run
    else
        printf "${YELLOW}Would skip:${NC} native nurt tools path unavailable\n"
    fi

    printf "\n${GREEN}Dry run completed.${NC}\n"
    exit 0
fi

printf "${CYAN}${BOLD}Repository Setup Script${NC}\n"
printf "${CYAN}=======================${NC}\n"
printf "\n"

# Create a backup copy of the install script
cp -f install.sh .template_scripts/install.sh

SCAFFOLD_APPLY
printf "\n"

# Reinitialize git repository
printf "${BLUE}Reinitializing git repository...${NC}\n"
rm -rf .git
git init
printf "  ${GREEN}✓${NC} Git repository initialized\n"
printf "\n"

# Create required directories
printf "${BLUE}Creating project directories...${NC}\n"
mkdir -p docs/tasks/completed
printf "  ${GREEN}✓${NC} docs/tasks/completed/\n"

mkdir -p tests
printf "  ${GREEN}✓${NC} tests/\n"

printf "\n"
printf "${GREEN}${BOLD}Directories created successfully!${NC}\n"
printf "\n"

# Install BMAD Method via native nurt command
printf "${CYAN}${BOLD}Step 1/2: Installing BMAD Method via nurt...${NC}\n"
printf "${CYAN}------------------------------------------${NC}\n"
if ! run_nurt_command sync bmad; then
    printf "${RED}${BOLD}Error: BMAD Method installation failed${NC}\n"
    exit 1
fi

printf "\n"
printf "${CYAN}=====================================${NC}\n"
printf "${GREEN}${BOLD}Repository setup completed successfully!${NC}\n"
printf "${CYAN}=====================================${NC}\n"

# Create initial commit
printf "\n"
printf "${BLUE}Creating initial commit...${NC}\n"
git add .
git commit -m "Initial Commit"
printf "  ${GREEN}✓${NC} Initial commit created\n"
printf "\n"

# Install / update OpenCode and support tools via native nurt command
printf "${CYAN}${BOLD}Step 2/2: Installing / Updating OpenCode and support tools via nurt...${NC}\n"
printf "${CYAN}------------------------------------------------------------------${NC}\n"
if ! run_nurt_command sync tools; then
    printf "${RED}${BOLD}Error: OpenCode/tool update failed${NC}\n"
    exit 1
fi
printf "\n"

# Cleanup Install Script
rm -rf install.sh
