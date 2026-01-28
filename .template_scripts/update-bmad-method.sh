#!/bin/sh

# BMAD Method Installation Script
# Installs or updates the BMAD Method using npx

set -e  # Exit on any error

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

printf "${CYAN}${BOLD}BMAD Method Installation Script${NC}\n"
printf "${CYAN}================================${NC}\n"

# Check if npm/npx is installed
# if ! command -v npx &> /dev/null; then
if ! command -v npx > /dev/null 2>&1; then
    printf "${RED}${BOLD}Error: npx is not installed${NC}\n"
    printf "${YELLOW}Please install Node.js and npm first${NC}\n"
    exit 1
fi

# Get npm version for context
NPM_VERSION=$(npm --version 2>/dev/null | tr -d '\n')
printf "${BLUE}Using npm version: ${NC}${BOLD}%s${NC}\n" "$NPM_VERSION"
printf "\n"

printf "${YELLOW}Installing BMAD Method (alpha version)...${NC}\n"
printf "\n"

# Install bmad-method
npx bmad-method@alpha install

if [ $? -eq 0 ]; then
    printf "\n"
    printf "${GREEN}${BOLD}BMAD Method installed successfully!${NC}\n"
else
    printf "\n"
    printf "${RED}${BOLD}Error: BMAD Method installation failed${NC}\n"
    exit 1
fi

printf "${GREEN}Done.${NC}\n"
