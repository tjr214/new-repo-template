#!/bin/sh

# Template Repository Update Script
# Updates configuration files and scripts from the template repository

set -e  # Exit on any error

# Configuration Variables
TEMPLATE_REPO_HTTPS="https://github.com/tjr214/new-repo-template.git"
TEMPLATE_REPO_SSH="git@github.com:tjr214/new-repo-template.git"
CLONE_DIR="nr"

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

printf "${CYAN}${BOLD}Template Repository Update Script${NC}\n"
printf "${CYAN}==================================${NC}\n"
printf "\n"

# Check if running from project root
printf "${BLUE}Verifying execution directory...${NC}\n"
if [ ! -d ".opencode" ] || [ ! -d ".template_scripts" ]; then
    printf "${RED}${BOLD}Error: Must be run from project root${NC}\n"
    printf "This script must be executed from the project root directory.\n"
    printf "Expected files: .opencode/, .template_scripts/\n"
    exit 1
fi
printf "  ${GREEN}✓${NC} Running from project root\n"
printf "\n"

# Check for uncommitted changes
printf "${BLUE}Checking for uncommitted changes...${NC}\n"
if [ -n "$(git status --porcelain)" ]; then
    printf "${RED}${BOLD}Error: Repository has uncommitted changes${NC}\n"
    printf "Please commit or stash your changes before updating the template.\n"
    printf "\n"
    printf "Run: ${BOLD}git status${NC} to see uncommitted changes\n"
    exit 1
fi
printf "  ${GREEN}✓${NC} No uncommitted changes\n"
printf "\n"

# Clone template repository
printf "${BLUE}Cloning template repository...${NC}\n"

# Remove existing clone directory if present
if [ -d "$CLONE_DIR" ]; then
    printf "  ${YELLOW}Removing existing ${CLONE_DIR}/ directory...${NC}\n"
    rm -rf "$CLONE_DIR"
fi

# Try HTTPS first
if git clone "$TEMPLATE_REPO_HTTPS" "$CLONE_DIR" 2>/dev/null; then
    printf "  ${GREEN}✓${NC} Cloned from ${TEMPLATE_REPO_HTTPS}\n"
elif git clone "$TEMPLATE_REPO_SSH" "$CLONE_DIR" 2>/dev/null; then
    printf "  ${GREEN}✓${NC} Cloned from ${TEMPLATE_REPO_SSH}\n"
else
    printf "${RED}${BOLD}Error: Failed to clone template repository${NC}\n"
    printf "Tried both HTTPS and SSH methods:\n"
    printf "  - ${TEMPLATE_REPO_HTTPS}\n"
    printf "  - ${TEMPLATE_REPO_SSH}\n"
    exit 1
fi
printf "\n"

# Helper function to copy file with verification
copy_file() {
    SOURCE="$1"
    DEST="$2"
    
    if [ ! -f "$SOURCE" ]; then
        printf "${RED}${BOLD}Error: Template file missing${NC}\n"
        printf "Expected: ${SOURCE}\n"
        printf "The template repository may be incomplete or corrupted.\n"
        exit 1
    fi
    
    cp -p "$SOURCE" "$DEST"
    
    if [ $? -eq 0 ]; then
        printf "  ${GREEN}✓${NC} ${DEST}\n"
    else
        printf "${RED}${BOLD}Error: Failed to copy ${DEST}${NC}\n"
        exit 1
    fi
}

# Helper function to copy directory with verification
copy_directory() {
    SOURCE="$1"
    DEST="$2"
    
    if [ ! -d "$SOURCE" ]; then
        printf "${RED}${BOLD}Error: Template directory missing${NC}\n"
        printf "Expected: ${SOURCE}\n"
        printf "The template repository may be incomplete or corrupted.\n"
        exit 1
    fi
    
    # Remove destination if it exists
    if [ -d "$DEST" ]; then
        rm -rf "$DEST"
        printf "  ${GREEN}✓${NC} Removed old ${DEST}\n"
    fi
    
    cp -Rp "$SOURCE" "$DEST"
    
    if [ $? -eq 0 ]; then
        printf "  ${GREEN}✓${NC} Copied ${DEST}\n"
    else
        printf "${RED}${BOLD}Error: Failed to copy ${DEST}${NC}\n"
        exit 1
    fi
}

# Step 1: Update .claude/settings.json
printf "${CYAN}${BOLD}Step 1/8: Updating .claude/settings.json${NC}\n"
printf "${CYAN}------------------------------------------${NC}\n"
copy_file "$CLONE_DIR/.claude/settings.json" ".claude/settings.json"
printf "\n"

# Step 2: Update .claude/statusline-script.sh
printf "${CYAN}${BOLD}Step 2/8: Updating .claude/statusline-script.sh${NC}\n"
printf "${CYAN}----------------------------------------------${NC}\n"
copy_file "$CLONE_DIR/.claude/statusline-script.sh" ".claude/statusline-script.sh"
printf "\n"

# Step 3: Update .claude/commands/repo/
printf "${CYAN}${BOLD}Step 3/8: Updating .claude/commands/repo/${NC}\n"
printf "${CYAN}------------------------------------------${NC}\n"
copy_directory "$CLONE_DIR/.claude/commands/repo" ".claude/commands/repo"
printf "\n"

# Step 4: Update AGENTS.md
printf "${CYAN}${BOLD}Step 4/8: Updating AGENTS.md${NC}\n"
printf "${CYAN}----------------------------${NC}\n"
copy_file "$CLONE_DIR/AGENTS.md" "AGENTS.md"
printf "\n"

# Step 5: Update CLAUDE.md
printf "${CYAN}${BOLD}Step 5/8: Updating CLAUDE.md${NC}\n"
printf "${CYAN}----------------------------${NC}\n"
copy_file "$CLONE_DIR/CLAUDE.md" "CLAUDE.md"
printf "\n"

# Step 6: Update repomix.config.json
printf "${CYAN}${BOLD}Step 6/8: Updating repomix.config.json${NC}\n"
printf "${CYAN}--------------------------------------${NC}\n"
copy_file "$CLONE_DIR/repomix.config.json" "repomix.config.json"
printf "\n"

# Step 7: Update .template_scripts/
printf "${CYAN}${BOLD}Step 7/8: Updating .template_scripts/${NC}\n"
printf "${CYAN}-------------------------------------${NC}\n"
if [ ! -d "$CLONE_DIR/.template_scripts" ]; then
    printf "${RED}${BOLD}Error: Template directory missing${NC}\n"
    printf "Expected: $CLONE_DIR/.template_scripts\n"
    printf "The template repository may be incomplete or corrupted.\n"
    exit 1
fi

# Copy all scripts from template_scripts
for script in "$CLONE_DIR/.template_scripts"/*; do
    if [ -f "$script" ]; then
        SCRIPT_NAME=$(basename "$script")
        copy_file "$script" ".template_scripts/$SCRIPT_NAME"
    fi
done
printf "\n"

# Step 8: Update .opencode/command/ markdown files
printf "${CYAN}${BOLD}Step 8/8: Updating .opencode/command/*.md${NC}\n"
printf "${CYAN}------------------------------------------${NC}\n"
if [ ! -d "$CLONE_DIR/.opencode/command" ]; then
    printf "${RED}${BOLD}Error: Template directory missing${NC}\n"
    printf "Expected: $CLONE_DIR/.opencode/command\n"
    printf "The template repository may be incomplete or corrupted.\n"
    exit 1
fi

# Copy all markdown files from .opencode/command
MD_FILE_COUNT=0
for mdfile in "$CLONE_DIR/.opencode/command"/*.md; do
    if [ -f "$mdfile" ]; then
        MD_FILE_NAME=$(basename "$mdfile")
        copy_file "$mdfile" ".opencode/command/$MD_FILE_NAME"
        MD_FILE_COUNT=$((MD_FILE_COUNT + 1))
    fi
done

if [ $MD_FILE_COUNT -eq 0 ]; then
    printf "${YELLOW}Warning: No markdown files found in template .opencode/command/${NC}\n"
fi
printf "\n"

# Cleanup
printf "${BLUE}Cleaning up...${NC}\n"
rm -rf "$CLONE_DIR"
if [ $? -eq 0 ]; then
    printf "  ${GREEN}✓${NC} Removed ${CLONE_DIR}/ directory\n"
else
    printf "${YELLOW}Warning: Failed to remove ${CLONE_DIR}/ directory${NC}\n"
fi

printf "\n"
printf "${CYAN}=====================================${NC}\n"
printf "${GREEN}${BOLD}Template update completed successfully!${NC}\n"
printf "${CYAN}=====================================${NC}\n"
