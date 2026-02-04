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

mkdir -p scripts
printf "  ${GREEN}✓${NC} scripts/\n"

mkdir -p tests
printf "  ${GREEN}✓${NC} tests/\n"

printf "\n"
printf "${GREEN}${BOLD}Directories created successfully!${NC}\n"
printf "\n"

# Update OpenCode
printf "${CYAN}${BOLD}Step 1/2: Checking OpenCode...${NC}\n"
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
printf "${CYAN}${BOLD}Step 2/2: Checking BMAD Method...${NC}\n"
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