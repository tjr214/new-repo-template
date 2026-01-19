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

# ============================================================================
# Update uv first
# ============================================================================
printf "\n${CYAN}${BOLD}Checking uv...${NC}\n"

# Check if uv is installed
if command -v uv &> /dev/null; then
    # Get current version
    CURRENT_UV_VERSION=$(uv --version 2>/dev/null | tr -d '\n')
    printf "${BLUE}uv is already installed ${NC}(Version: ${BOLD}%s${NC})\n" "$CURRENT_UV_VERSION"
    printf "${YELLOW}Updating uv...${NC}\n"
    
    # Update uv
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Get new version
    if [ $? -eq 0 ]; then
        NEW_UV_VERSION=$(uv --version 2>/dev/null | tr -d '\n')
        if [ "$CURRENT_UV_VERSION" = "$NEW_UV_VERSION" ]; then
            printf "${GREEN}uv is already up to date ${NC}(Version: ${BOLD}%s${NC})\n" "$NEW_UV_VERSION"
        else
            printf "${GREEN}${BOLD}uv updated successfully!${NC}\n"
            printf "${BLUE}Previous version: ${NC}%s\n" "$CURRENT_UV_VERSION"
            printf "${BLUE}Current version: ${NC}${BOLD}%s${NC}\n" "$NEW_UV_VERSION"
        fi
    else
        printf "${RED}${BOLD}Error: uv update failed${NC}\n"
        exit 1
    fi
else
    printf "${YELLOW}uv not found. Installing...${NC}\n"
    
    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    if [ $? -eq 0 ]; then
        INSTALLED_UV_VERSION=$(uv --version 2>/dev/null | tr -d '\n')
        printf "${GREEN}${BOLD}uv installed successfully!${NC} ${NC}(Version: ${BOLD}%s${NC})\n" "$INSTALLED_UV_VERSION"
    else
        printf "${RED}${BOLD}Error: uv installation failed${NC}\n"
        exit 1
    fi
fi

# ============================================================================
# Update OpenCode
# ============================================================================
printf "\n${CYAN}${BOLD}Checking OpenCode...${NC}\n"

rm -rf ~/.cache/opencode/node_modules/opencode-antigravity-auth

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

# ============================================================================
# Install/Update Antigravity OAuth Plugin
# ============================================================================
printf "\n${CYAN}${BOLD}Checking Antigravity OAuth Plugin...${NC}\n"

# Check if the plugin is already installed
if npm list -g opencode-antigravity-auth --depth=0 &> /dev/null; then
    # Get current version
    CURRENT_PLUGIN_VERSION=$(npm list -g opencode-antigravity-auth --depth=0 2>/dev/null | grep opencode-antigravity-auth | sed 's/.*@//' | tr -d '\n')
    printf "${BLUE}Antigravity OAuth Plugin is already installed ${NC}(Version: ${BOLD}%s${NC})\n" "$CURRENT_PLUGIN_VERSION"
    printf "${YELLOW}Updating Antigravity OAuth Plugin...${NC}\n"
    
    # Update plugin
    npm install -g opencode-antigravity-auth@beta
    
    # Get new version
    if [ $? -eq 0 ]; then
        NEW_PLUGIN_VERSION=$(npm list -g opencode-antigravity-auth --depth=0 2>/dev/null | grep opencode-antigravity-auth | sed 's/.*@//' | tr -d '\n')
        if [ "$CURRENT_PLUGIN_VERSION" = "$NEW_PLUGIN_VERSION" ]; then
            printf "${GREEN}Antigravity OAuth Plugin is already up to date ${NC}(Version: ${BOLD}%s${NC})\n" "$NEW_PLUGIN_VERSION"
        else
            printf "${GREEN}${BOLD}Antigravity OAuth Plugin updated successfully!${NC}\n"
            printf "${BLUE}Previous version: ${NC}%s\n" "$CURRENT_PLUGIN_VERSION"
            printf "${BLUE}Current version: ${NC}${BOLD}%s${NC}\n" "$NEW_PLUGIN_VERSION"
        fi
    else
        printf "${RED}${BOLD}Error: Plugin update failed${NC}\n"
        exit 1
    fi
else
    printf "${YELLOW}Antigravity OAuth Plugin not found. Installing...${NC}\n"
    
    # Install plugin
    npm install -g opencode-antigravity-auth@beta
    
    if [ $? -eq 0 ]; then
        INSTALLED_PLUGIN_VERSION=$(npm list -g opencode-antigravity-auth --depth=0 2>/dev/null | grep opencode-antigravity-auth | sed 's/.*@//' | tr -d '\n')
        printf "${GREEN}${BOLD}Antigravity OAuth Plugin installed successfully!${NC} ${NC}(Version: ${BOLD}%s${NC})\n" "$INSTALLED_PLUGIN_VERSION"
    else
        printf "${RED}${BOLD}Error: Plugin installation failed${NC}\n"
        exit 1
    fi
fi

printf "\n${GREEN}Done.${NC}\n"