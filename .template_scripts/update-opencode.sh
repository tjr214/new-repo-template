#!/bin/sh

# OpenCode Update Script
# Checks if OpenCode is installed, installs if missing, or updates if present

# Continue running even if one tool fails; report failures at the end
set +e

# Color definitions
RED='\033[0;31m'
BOLD_RED='\033[1;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
MAGENTA='\033[0;35m'
DULL_YELLOW='\033[2;33m'
BG_YELLOW='\033[43m'
BOLD='\033[1m'
NC='\033[0m' # No Color
TABLE_COLOR="${WHITE}"
SEPARATOR_COLOR="${DULL_YELLOW}"

printf "${CYAN}${BOLD}OpenCode Installation/Update Script${NC}\n"
printf "${CYAN}=====================================${NC}\n"

print_section_separator() {
    printf "\n${SEPARATOR_COLOR}-------------------------------------------------------------------------------${NC}\n"
}

add_to_path_once() {
    case ":$PATH:" in
        *":$1:"*) ;;
        *)
            PATH="$1:$PATH"
            export PATH
            ;;
    esac
}

FAILED_COMPONENTS=""

mark_failure() {
    case ",$FAILED_COMPONENTS," in
        *",$1,"*) ;;
        *)
            if [ -z "$FAILED_COMPONENTS" ]; then
                FAILED_COMPONENTS="$1"
            else
                FAILED_COMPONENTS="$FAILED_COMPONENTS, $1"
            fi
            ;;
    esac
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

center_text() {
    TEXT="$1"
    WIDTH="$2"
    TEXT_LEN=${#TEXT}

    if [ "$TEXT_LEN" -ge "$WIDTH" ]; then
        printf "%s" "$TEXT"
        return
    fi

    LEFT_PAD=$(( (WIDTH - TEXT_LEN) / 2 ))
    RIGHT_PAD=$(( WIDTH - TEXT_LEN - LEFT_PAD ))
    printf "%*s%s%*s" "$LEFT_PAD" "" "$TEXT" "$RIGHT_PAD" ""
}

print_results_table() {
    HEADER_TOOL=$(center_text "Tools" 10)
    HEADER_STATUS=$(center_text "Status" 11)
    HEADER_DETAILS=$(center_text "Details" 56)

    printf "${TABLE_COLOR}+------------+-------------+----------------------------------------------------------+${NC}\n"
    CENTERED_TITLE=$(center_text "Update Results" 85)
    printf "${TABLE_COLOR}|${BOLD_RED}${BG_YELLOW}%-85s${NC}${TABLE_COLOR}|${NC}\n" "$CENTERED_TITLE"
    printf "${TABLE_COLOR}+------------+-------------+----------------------------------------------------------+${NC}\n"
    printf "${TABLE_COLOR}| %s | %s | %s |${NC}\n" "$HEADER_TOOL" "$HEADER_STATUS" "$HEADER_DETAILS"
    printf "${TABLE_COLOR}+------------+-------------+----------------------------------------------------------+${NC}\n"
    print_result_row "uv" "$UV_STATUS" "$UV_DETAIL"
    print_result_row "bun" "$BUN_STATUS" "$BUN_DETAIL"
    print_result_row "OpenCode" "$OPENCODE_STATUS" "$OPENCODE_DETAIL"
    print_result_row "btca" "$BTCA_STATUS" "$BTCA_DETAIL"
    print_result_row "ripgrep" "$RG_STATUS" "$RG_DETAIL"
    printf "${TABLE_COLOR}+------------+-------------+----------------------------------------------------------+${NC}\n"
}

print_result_row() {
    TOOL_NAME="$1"
    TOOL_STATUS="$2"
    TOOL_DETAIL="$3"

    case "$TOOL_STATUS" in
        INSTALLED|UPDATED)
            STATUS_COLOR="$GREEN"
            ;;
        UP-TO-DATE)
            STATUS_COLOR="$BLUE"
            ;;
        COMPLETED)
            STATUS_COLOR="$CYAN"
            ;;
        FAILED)
            STATUS_COLOR="$RED"
            ;;
        UNSUPPORTED|PENDING)
            STATUS_COLOR="$YELLOW"
            ;;
        *)
            STATUS_COLOR="$NC"
            ;;
    esac

    if [ "$TOOL_STATUS" = "UPDATED" ]; then
        STATUS_COLOR="${BOLD}${GREEN}"
    fi

    printf "${TABLE_COLOR}| ${YELLOW}%-10s${TABLE_COLOR} | " "$TOOL_NAME"
    printf "${STATUS_COLOR}%-11s${NC}" "$TOOL_STATUS"
    printf "${TABLE_COLOR} | ${MAGENTA}%-56s${TABLE_COLOR} |${NC}\n" "$TOOL_DETAIL"
}

UV_STATUS="PENDING"
UV_DETAIL="not run"
BUN_STATUS="PENDING"
BUN_DETAIL="not run"
OPENCODE_STATUS="PENDING"
OPENCODE_DETAIL="not run"
BTCA_STATUS="PENDING"
BTCA_DETAIL="not run"
RG_STATUS="PENDING"
RG_DETAIL="not run"

LAST_RESULT_STATUS=""
LAST_RESULT_DETAIL=""

print_install_update_result() {
    TOOL_NAME="$1"
    PREVIOUS_VERSION="$2"
    CURRENT_VERSION="$3"

    if [ -z "$PREVIOUS_VERSION" ]; then
        if [ -n "$CURRENT_VERSION" ]; then
            LAST_RESULT_STATUS="INSTALLED"
            LAST_RESULT_DETAIL="$CURRENT_VERSION"
            printf "${GREEN}${BOLD}%s installed successfully!${NC} ${NC}(Version: ${BOLD}%s${NC})\n" "$TOOL_NAME" "$CURRENT_VERSION"
        else
            LAST_RESULT_STATUS="INSTALLED"
            LAST_RESULT_DETAIL="version unavailable"
            printf "${GREEN}${BOLD}%s installed successfully!${NC}\n" "$TOOL_NAME"
        fi
    elif [ -n "$CURRENT_VERSION" ] && [ "$PREVIOUS_VERSION" = "$CURRENT_VERSION" ]; then
        LAST_RESULT_STATUS="UP-TO-DATE"
        LAST_RESULT_DETAIL="$CURRENT_VERSION"
        printf "${GREEN}%s is already up to date ${NC}(Version: ${BOLD}%s${NC})\n" "$TOOL_NAME" "$CURRENT_VERSION"
    elif [ -n "$CURRENT_VERSION" ]; then
        LAST_RESULT_STATUS="UPDATED"
        LAST_RESULT_DETAIL="$PREVIOUS_VERSION -> $CURRENT_VERSION"
        printf "${GREEN}${BOLD}%s updated successfully!${NC}\n" "$TOOL_NAME"
        printf "${BLUE}Previous version: ${NC}%s\n" "$PREVIOUS_VERSION"
        printf "${BLUE}Current version: ${NC}${BOLD}%s${NC}\n" "$CURRENT_VERSION"
    else
        LAST_RESULT_STATUS="COMPLETED"
        LAST_RESULT_DETAIL="version unavailable"
        printf "${GREEN}${BOLD}%s install/update completed successfully!${NC}\n" "$TOOL_NAME"
    fi
}

# ============================================================================
# Update uv first
# ============================================================================
printf "\n${CYAN}${BOLD}Checking uv...${NC}\n"

# Check if uv is installed
if command_exists uv; then
    # Get current version
    CURRENT_UV_VERSION=$(uv --version 2>/dev/null | tr -d '\n')
    printf "${BLUE}uv is already installed ${NC}(Version: ${BOLD}%s${NC})\n" "$CURRENT_UV_VERSION"
    printf "${YELLOW}Updating uv...${NC}\n"
    
    # Update uv
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        NEW_UV_VERSION=$(uv --version 2>/dev/null | tr -d '\n')
        print_install_update_result "uv" "$CURRENT_UV_VERSION" "$NEW_UV_VERSION"
        UV_STATUS="$LAST_RESULT_STATUS"
        UV_DETAIL="$LAST_RESULT_DETAIL"
    else
        printf "${RED}${BOLD}Error: uv update failed${NC}\n"
        mark_failure "uv"
        UV_STATUS="FAILED"
        UV_DETAIL="update failed"
    fi
else
    printf "${YELLOW}uv not found. Installing...${NC}\n"
    
    # Install uv
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        INSTALLED_UV_VERSION=$(uv --version 2>/dev/null | tr -d '\n')
        print_install_update_result "uv" "" "$INSTALLED_UV_VERSION"
        UV_STATUS="$LAST_RESULT_STATUS"
        UV_DETAIL="$LAST_RESULT_DETAIL"
    else
        printf "${RED}${BOLD}Error: uv installation failed${NC}\n"
        mark_failure "uv"
        UV_STATUS="FAILED"
        UV_DETAIL="installation failed"
    fi
fi

# ============================================================================
# Update bun second
# ============================================================================
print_section_separator
printf "\n${CYAN}${BOLD}Checking bun...${NC}\n"

# Ensure bun default install path is available in this shell
if [ -d "$HOME/.bun/bin" ]; then
    add_to_path_once "$HOME/.bun/bin"
fi

# Check if bun is installed
if command_exists bun; then
    # Get current version
    CURRENT_BUN_VERSION=$(bun --version 2>/dev/null | tr -d '\n')
    printf "${BLUE}bun is already installed ${NC}(Version: ${BOLD}%s${NC})\n" "$CURRENT_BUN_VERSION"
    printf "${YELLOW}Updating bun...${NC}\n"

    # Update bun
    if bun upgrade; then
        NEW_BUN_VERSION=$(bun --version 2>/dev/null | tr -d '\n')
        print_install_update_result "bun" "$CURRENT_BUN_VERSION" "$NEW_BUN_VERSION"
        BUN_STATUS="$LAST_RESULT_STATUS"
        BUN_DETAIL="$LAST_RESULT_DETAIL"
    else
        printf "${RED}${BOLD}Error: bun update failed${NC}\n"
        mark_failure "bun"
        BUN_STATUS="FAILED"
        BUN_DETAIL="update failed"
    fi
else
    printf "${YELLOW}bun not found. Installing...${NC}\n"

    # Install bun
    if curl -fsSL https://bun.sh/install | bash; then
        # Ensure bun command is immediately available
        export BUN_INSTALL="${BUN_INSTALL:-$HOME/.bun}"
        if [ -d "$BUN_INSTALL/bin" ]; then
            add_to_path_once "$BUN_INSTALL/bin"
        fi

        INSTALLED_BUN_VERSION=$(bun --version 2>/dev/null | tr -d '\n')
        print_install_update_result "bun" "" "$INSTALLED_BUN_VERSION"
        BUN_STATUS="$LAST_RESULT_STATUS"
        BUN_DETAIL="$LAST_RESULT_DETAIL"
        if [ -z "$INSTALLED_BUN_VERSION" ]; then
            printf "${YELLOW}bun installed, but it is not yet available in PATH for this shell.${NC}\n"
        fi
    else
        printf "${RED}${BOLD}Error: bun installation failed${NC}\n"
        mark_failure "bun"
        BUN_STATUS="FAILED"
        BUN_DETAIL="installation failed"
    fi
fi



# ============================================================================
# Update OpenCode
# ============================================================================
print_section_separator
printf "\n${CYAN}${BOLD}Checking OpenCode...${NC}\n"

rm -rf ~/.cache/opencode/node_modules/opencode-antigravity-auth

# Check if opencode is installed
if command_exists opencode; then
    # Get current version
    CURRENT_VERSION=$(opencode --version 2>/dev/null | tr -d '\n')
    printf "${BLUE}OpenCode is already installed ${NC}(Version: ${BOLD}%s${NC})\n" "$CURRENT_VERSION"
    printf "${YELLOW}Updating OpenCode...${NC}\n"
    
    # Update opencode
    if curl -fsSL https://opencode.ai/install | bash; then
        NEW_VERSION=$(opencode --version 2>/dev/null | tr -d '\n')
        print_install_update_result "OpenCode" "$CURRENT_VERSION" "$NEW_VERSION"
        OPENCODE_STATUS="$LAST_RESULT_STATUS"
        OPENCODE_DETAIL="$LAST_RESULT_DETAIL"
    else
        printf "${RED}${BOLD}Error: Update failed${NC}\n"
        mark_failure "opencode"
        OPENCODE_STATUS="FAILED"
        OPENCODE_DETAIL="update failed"
    fi
else
    printf "${YELLOW}OpenCode not found. Installing...${NC}\n"
    
    # Install opencode
    if curl -fsSL https://opencode.ai/install | bash; then
        INSTALLED_VERSION=$(opencode --version 2>/dev/null | tr -d '\n')
        print_install_update_result "OpenCode" "" "$INSTALLED_VERSION"
        OPENCODE_STATUS="$LAST_RESULT_STATUS"
        OPENCODE_DETAIL="$LAST_RESULT_DETAIL"
    else
        printf "${RED}${BOLD}Error: Installation failed${NC}\n"
        mark_failure "opencode"
        OPENCODE_STATUS="FAILED"
        OPENCODE_DETAIL="installation failed"
    fi
fi

# ============================================================================
# Update or Install `btca`
# ============================================================================
print_section_separator
printf "\n${CYAN}${BOLD}Checking btca...${NC}\n"

# Ensure bun default install path is available in this shell
if [ -d "$HOME/.bun/bin" ]; then
    add_to_path_once "$HOME/.bun/bin"
fi

if ! command_exists bun; then
    printf "${RED}${BOLD}Error: bun is required to install/update btca.${NC}\n"
    mark_failure "btca"
    BTCA_STATUS="FAILED"
    BTCA_DETAIL="bun is required"
else
    # Check if btca is installed
    if command_exists btca; then
        CURRENT_BTCA_VERSION=$(btca --version 2>/dev/null | tr -d '\n')
        if [ -n "$CURRENT_BTCA_VERSION" ]; then
            printf "${BLUE}btca is already installed ${NC}(Version: ${BOLD}%s${NC})\n" "$CURRENT_BTCA_VERSION"
        else
            printf "${BLUE}btca is already installed${NC}\n"
        fi
        printf "${YELLOW}Updating btca...${NC}\n"
    else
        printf "${YELLOW}btca not found. Installing...${NC}\n"
        CURRENT_BTCA_VERSION=""
    fi

    # Install/update btca
    if bun add -g btca; then
        NEW_BTCA_VERSION=$(btca --version 2>/dev/null | tr -d '\n')
        print_install_update_result "btca" "$CURRENT_BTCA_VERSION" "$NEW_BTCA_VERSION"
        BTCA_STATUS="$LAST_RESULT_STATUS"
        BTCA_DETAIL="$LAST_RESULT_DETAIL"
    else
        printf "${RED}${BOLD}Error: btca installation/update failed${NC}\n"
        mark_failure "btca"
        BTCA_STATUS="FAILED"
        BTCA_DETAIL="installation/update failed"
    fi
fi



# ============================================================================
# Install/Update ripgrep
# ============================================================================
print_section_separator
printf "\n${CYAN}${BOLD}Checking ripgrep...${NC}\n"

# Detect OS
OS_TYPE=$(uname -s)

# Check if ripgrep is already installed
if command_exists rg; then
    # Get current version
    CURRENT_RG_VERSION=$(rg --version 2>/dev/null | head -n1 | awk '{print $2}' | tr -d '\n')
    printf "${BLUE}ripgrep is already installed ${NC}(Version: ${BOLD}%s${NC})\n" "$CURRENT_RG_VERSION"
    printf "${YELLOW}Checking for updates...${NC}\n"
else
    printf "${YELLOW}ripgrep not found. Installing...${NC}\n"
    CURRENT_RG_VERSION=""
fi

RG_ACTION_SUCCESS=0

# Install/Update based on OS
case "$OS_TYPE" in
    Darwin)
        # macOS - Use Homebrew (official method)
        if command_exists brew; then
            if [ -z "$CURRENT_RG_VERSION" ]; then
                # Install
                if brew install ripgrep; then
                    RG_ACTION_SUCCESS=1
                else
                    printf "${RED}${BOLD}Error: ripgrep installation/update failed${NC}\n"
                    mark_failure "ripgrep"
                    RG_STATUS="FAILED"
                    RG_DETAIL="brew install failed"
                fi
            else
                # Update
                if brew upgrade ripgrep; then
                    RG_ACTION_SUCCESS=1
                else
                    printf "${YELLOW}brew upgrade did not complete; trying install command fallback...${NC}\n"
                    if brew install ripgrep; then
                        RG_ACTION_SUCCESS=1
                    else
                        printf "${RED}${BOLD}Error: ripgrep installation/update failed${NC}\n"
                        mark_failure "ripgrep"
                        RG_STATUS="FAILED"
                        RG_DETAIL="brew upgrade/install failed"
                    fi
                fi
            fi
        else
            printf "${RED}${BOLD}Error: Homebrew not found. Please install Homebrew first: https://brew.sh${NC}\n"
            mark_failure "ripgrep"
            RG_STATUS="FAILED"
            RG_DETAIL="homebrew not found"
        fi
        ;;
    
    Linux)
        # Detect Linux distribution
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO=$ID
        else
            DISTRO="unknown"
        fi
        
        case "$DISTRO" in
            ubuntu|debian)
                # Ubuntu/Debian - Use apt (official method)
                printf "${YELLOW}Installing/updating via apt...${NC}\n"
                if sudo apt update && sudo apt install -y ripgrep; then
                    RG_ACTION_SUCCESS=1
                else
                    printf "${RED}${BOLD}Error: ripgrep installation/update failed${NC}\n"
                    mark_failure "ripgrep"
                    RG_STATUS="FAILED"
                    RG_DETAIL="apt install failed"
                fi
                ;;
            
            fedora|rhel|centos)
                # Fedora/RHEL/CentOS - Use dnf (official method)
                printf "${YELLOW}Installing/updating via dnf...${NC}\n"
                if sudo dnf install -y ripgrep; then
                    RG_ACTION_SUCCESS=1
                else
                    printf "${RED}${BOLD}Error: ripgrep installation/update failed${NC}\n"
                    mark_failure "ripgrep"
                    RG_STATUS="FAILED"
                    RG_DETAIL="dnf install failed"
                fi
                ;;
            
            arch|manjaro)
                # Arch Linux - Use pacman (official method)
                printf "${YELLOW}Installing/updating via pacman...${NC}\n"
                if sudo pacman -Sy --noconfirm ripgrep; then
                    RG_ACTION_SUCCESS=1
                else
                    printf "${RED}${BOLD}Error: ripgrep installation/update failed${NC}\n"
                    mark_failure "ripgrep"
                    RG_STATUS="FAILED"
                    RG_DETAIL="pacman install failed"
                fi
                ;;
            
            opensuse*|suse)
                # openSUSE - Use zypper (official method)
                printf "${YELLOW}Installing/updating via zypper...${NC}\n"
                if sudo zypper install -y ripgrep; then
                    RG_ACTION_SUCCESS=1
                else
                    printf "${RED}${BOLD}Error: ripgrep installation/update failed${NC}\n"
                    mark_failure "ripgrep"
                    RG_STATUS="FAILED"
                    RG_DETAIL="zypper install failed"
                fi
                ;;
            
            *)
                printf "${YELLOW}${BOLD}Unsupported Linux distribution: $DISTRO${NC}\n"
                printf "${YELLOW}Please install ripgrep manually from: https://github.com/BurntSushi/ripgrep${NC}\n"
                mark_failure "ripgrep"
                RG_STATUS="UNSUPPORTED"
                RG_DETAIL="$DISTRO"
                ;;
        esac
        ;;
    
    *)
        printf "${RED}${BOLD}Unsupported operating system: $OS_TYPE${NC}\n"
        printf "${YELLOW}Please install ripgrep manually from: https://github.com/BurntSushi/ripgrep${NC}\n"
        mark_failure "ripgrep"
        RG_STATUS="UNSUPPORTED"
        RG_DETAIL="$OS_TYPE"
        ;;
esac

if [ "$RG_ACTION_SUCCESS" -eq 1 ]; then
    NEW_RG_VERSION=$(rg --version 2>/dev/null | head -n1 | awk '{print $2}' | tr -d '\n')
    print_install_update_result "ripgrep" "$CURRENT_RG_VERSION" "$NEW_RG_VERSION"
    RG_STATUS="$LAST_RESULT_STATUS"
    RG_DETAIL="$LAST_RESULT_DETAIL"
fi

# ---------------------------------------------------------------------------

printf "\n\n"
print_results_table

if [ -n "$FAILED_COMPONENTS" ]; then
    printf "\n${YELLOW}${BOLD}Done with errors.${NC}\n"
    printf "${YELLOW}Failed components: ${BOLD}%s${NC}\n" "$FAILED_COMPONENTS"
    exit 1
fi

printf "\n${GREEN}Done.${NC}\n"
