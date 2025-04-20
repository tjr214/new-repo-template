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

# Display usage information
display_usage() {
    echo -e "${CYAN}${BOLD}📋 Update Packages Script${NC}"
    echo
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ${BOLD}./update_packages.sh <package-type>${NC}"
    echo
    echo -e "${YELLOW}Available package types:${NC}"
    echo -e "  ${GREEN}npm${NC}        - Update npm packages using pnpm"
    echo -e "  ${GREEN}python${NC}     - Update Python packages using pip"
    echo -e "  ${GREEN}taskmaster${NC} - Update Task Master CLI tool"
    echo
    echo -e "${YELLOW}Example:${NC}"
    echo -e "  ${BOLD}./update_packages.sh npm${NC}"
    echo
}

# Check if we're in the project root
check_project_root() {
    if [ ! -d "scripts/update_scripts" ]; then
        handle_error "This script must be run from the project root directory where 'scripts/update_scripts' exists."
    fi
}

# Main execution function
update_packages() {
    local package_type="$1"
    local script_path=""
    
    case "$package_type" in
        "npm")
            script_path="scripts/update_scripts/update_npm_packages.sh"
            ;;
        "python")
            script_path="scripts/update_scripts/update_python_packages.sh"
            ;;
        "taskmaster")
            script_path="scripts/update_scripts/update_task_master.sh"
            ;;
        *)
            display_usage
            handle_error "Invalid package type: ${package_type}. Please use 'npm', 'python', or 'taskmaster'."
            ;;
    esac
    
    # Check if the script exists
    if [ ! -f "$script_path" ]; then
        handle_error "Update script not found: $script_path"
    fi
    
    # Make sure the script is executable
    chmod +x "$script_path"
    
    # Execute the appropriate update script
    echo -e "${MAGENTA}${BOLD}🚀 Running ${package_type} update script...${NC}"
    execute_command "./$script_path" "Failed to execute the ${package_type} update script."
}

# Main script logic
main() {
    # Check if running from project root
    check_project_root
    
    # Check if a package type was provided
    if [ $# -eq 0 ]; then
        display_usage
        exit 0
    fi
    
    update_packages "$1"
    echo -e "${GREEN}${BOLD}✨ Update complete for: $1${NC}"
}

# Call the main function with all script arguments
main "$@"

