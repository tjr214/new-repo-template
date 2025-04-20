#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Define colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color (reset)

# Error handling function
handle_error() {
    echo -e "${RED}${BOLD}ERROR: $1${NC}" >&2
    exit 1
}

# Execute command with error handling
execute_command() {
    local cmd="$1"
    local error_message="$2"
    
    echo -e "${BLUE}Executing: ${cmd}${NC}"
    if ! eval "$cmd"; then
        handle_error "$error_message"
    fi
}

# Check if pip is installed
echo -e "${CYAN}🔍 Checking for pip installation...${NC}"
if ! command -v pip &> /dev/null; then
    handle_error "pip is not installed. Please install pip first to continue."
fi

# Display pip version
echo -e "${MAGENTA}📊 pip version: ${BOLD}$(pip --version)${NC}"

# Check if requirements.txt exists
echo -e "${CYAN}🔍 Checking for requirements.txt...${NC}"
if [ ! -f "requirements.txt" ]; then
    handle_error "requirements.txt not found in current directory. Please run this script from your project root."
fi

# Update Python packages
echo -e "${CYAN}📦 Updating Python packages...${NC}"
execute_command "pip install -U -r requirements.txt" "Failed to update Python packages. Please check your project configuration and try again."

echo -e "${GREEN}${BOLD}✨ All done! Python packages have been updated.${NC}"
