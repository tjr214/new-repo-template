#!/bin/sh

# OpenCode Update Script
# Checks if OpenCode is installed, installs if missing, or updates if present

set -e  # Exit on any error

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

printf "${CYAN}${BOLD}OpenCode Installation/Update Script${NC}\n"
printf "${CYAN}=====================================${NC}\n"

# Check if opencode is installed
if command -v opencode &> /dev/null; then
    # Get current version
    CURRENT_VERSION=$(opencode --version 2>/dev/null | tr -d '\n')
    printf "${BLUE}OpenCode is already installed ${NC}(Version: ${BOLD}%s${NC})\n" "$CURRENT_VERSION"
    printf "${YELLOW}Updating OpenCode...${NC}\n"
    
    # Update opencode
    curl -fsSL https://opencode.ai/install | bash
    
    # Get new version
    if [ $? -eq 0 ]; then
        NEW_VERSION=$(opencode --version 2>/dev/null | tr -d '\n')
        if [ "$CURRENT_VERSION" = "$NEW_VERSION" ]; then
            printf "${GREEN}OpenCode is already up to date ${NC}(Version: ${BOLD}%s${NC})\n" "$NEW_VERSION"
        else
            printf "${GREEN}${BOLD}OpenCode updated successfully!${NC}\n"
            printf "${BLUE}Previous version: ${NC}%s\n" "$CURRENT_VERSION"
            printf "${BLUE}Current version: ${NC}${BOLD}%s${NC}\n" "$NEW_VERSION"
        fi
    else
        printf "${RED}${BOLD}Error: Update failed${NC}\n"
        exit 1
    fi
else
    printf "${YELLOW}OpenCode not found. Installing...${NC}\n"
    
    # Install opencode
    curl -fsSL https://opencode.ai/install | bash
    
    if [ $? -eq 0 ]; then
        INSTALLED_VERSION=$(opencode --version 2>/dev/null | tr -d '\n')
        printf "${GREEN}${BOLD}OpenCode installed successfully!${NC} ${NC}(Version: ${BOLD}%s${NC})\n" "$INSTALLED_VERSION"
    else
        printf "${RED}${BOLD}Error: Installation failed${NC}\n"
        exit 1
    fi
fi

printf "${GREEN}Done.${NC}\n"