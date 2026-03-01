#!/bin/sh

# Repository Setup Script
# Creates required directories and updates/installs necessary tools

set -e  # Exit on any error

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

DRY_RUN=0

for ARG in "$@"; do
    case "$ARG" in
        --dry-run|-n)
            DRY_RUN=1
            ;;
        *)
            printf "${RED}${BOLD}Error: Unknown argument: %s${NC}\n" "$ARG"
            printf "Usage: sh install.sh [--dry-run]\n"
            exit 2
            ;;
    esac
done

if [ "$DRY_RUN" -eq 1 ]; then
    printf "${CYAN}${BOLD}Repository Setup Script (DRY RUN)${NC}\n"
    printf "${CYAN}=================================${NC}\n\n"

    printf "${YELLOW}DRY RUN: no filesystem or git changes will be made.${NC}\n\n"
    printf "${BLUE}Planned actions:${NC}\n"
    printf "  - Backup install script to .template_scripts/install.sh\n"
    printf "  - Reinitialize git repository (.git removal + git init)\n"
    printf "  - Ensure docs/tasks/completed and tests directories exist\n"
    printf "  - Run .template_scripts/update-opencode.sh (tool updates)\n"
    printf "  - Run .template_scripts/update-bmad-method.sh\n"
    printf "  - Create initial commit and remove install.sh\n\n"

    if [ -f ".template_scripts/update-opencode.sh" ]; then
        printf "${BLUE}Would run:${NC} sh .template_scripts/update-opencode.sh --dry-run\n"
    else
        printf "${YELLOW}Would skip:${NC} .template_scripts/update-opencode.sh not found\n"
    fi

    if [ -f ".template_scripts/update-bmad-method.sh" ]; then
        printf "${BLUE}Would run:${NC} sh .template_scripts/update-bmad-method.sh\n"
    else
        printf "${YELLOW}Would skip:${NC} .template_scripts/update-bmad-method.sh not found\n"
    fi

    printf "\n${GREEN}Dry run completed.${NC}\n"
    exit 0
fi

# Create a backup copy of the install script
cp -f install.sh .template_scripts/install.sh

printf "${CYAN}${BOLD}Repository Setup Script${NC}\n"
printf "${CYAN}=======================${NC}\n"
printf "\n"

# Reinitialize git repository
printf "${BLUE}Reinitializing git repository...${NC}\n"
rm -rf .git
git init
printf "  ${GREEN}✓${NC} Git repository initialized\n"
printf "\n"

# Create required directories
printf "${BLUE}Creating project directories...${NC}\n"
# mkdir -p docs
# printf "  ${GREEN}✓${NC} docs/\n"

# mkdir -p docs/tasks
# printf "  ${GREEN}✓${NC} docs/tasks/\n"

mkdir -p docs/tasks/completed
printf "  ${GREEN}✓${NC} docs/tasks/completed/\n"

# mkdir -p scripts
# printf "  ${GREEN}✓${NC} scripts/\n"

mkdir -p tests
printf "  ${GREEN}✓${NC} tests/\n"

printf "\n"
printf "${GREEN}${BOLD}Directories created successfully!${NC}\n"
printf "\n"

# Update OpenCode
printf "${CYAN}${BOLD}Step 1/2: Installing / Updating OpenCode and some support tools...${NC}\n"
printf "${CYAN}------------------------------${NC}\n"
if [ -f ".template_scripts/update-opencode.sh" ]; then
    sh .template_scripts/update-opencode.sh
    if [ $? -ne 0 ]; then
        printf "${RED}${BOLD}Error: OpenCode update failed${NC}\n"
        exit 1
    fi
else
    printf "${YELLOW}Warning: update-opencode.sh not found, skipping...${NC}\n"
fi

printf "\n"

# Update BMAD Method
printf "${CYAN}${BOLD}Step 2/2: Installing BMAD Method...${NC}\n"
printf "${CYAN}----------------------------------${NC}\n"
if [ -f ".template_scripts/update-bmad-method.sh" ]; then
    sh .template_scripts/update-bmad-method.sh
    if [ $? -ne 0 ]; then
        printf "${RED}${BOLD}Error: BMAD Method installation failed${NC}\n"
        exit 1
    fi
else
    printf "${YELLOW}Warning: update-bmad-method.sh not found, skipping...${NC}\n"
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

# Cleanup Install Script
rm -rf install.sh
