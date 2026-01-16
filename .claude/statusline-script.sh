#!/bin/bash

# Claude Code StatusLine Script
# Provides comprehensive session information in a clean format
# System-agnostic version using Python instead of jq

# Read JSON input from stdin
input=$(cat)

# Extract basic info using Python (works on all systems)
cwd=$(echo "$input" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('workspace', {}).get('current_dir') or data.get('cwd', ''))")
model_name=$(echo "$input" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('model', {}).get('display_name', 'Claude'))")
session_id=$(echo "$input" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('session_id', ''))")

# Function to calculate context breakdown and progress
calculate_context() {
    # Get transcript if available
    transcript_path=$(echo "$input" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('transcript_path', ''))")
    
    # Determine usable context limit (80% of theoretical before auto-compact)
    if [[ "$model_name" == *"Sonnet"* ]]; then
        context_limit=171500   # 160k usable for Sonnet models
    elif [[ "$model_name" == "glm-4.6" ]]; then
        context_limit=171500   # 160k usable for GLM-4.6 model
    else
        context_limit=171500   # 160k usable for 200k models (Opus, etc.)
    fi
    
    if [[ -n "$transcript_path" && -f "$transcript_path" ]]; then
        # Parse transcript to get real token usage from most recent main-chain message
        total_tokens=$(python3 -c "
import sys, json

try:
    with open('$transcript_path', 'r') as f:
        lines = f.readlines()
    
    most_recent_usage = None
    most_recent_timestamp = None
    
    for line in lines:
        try:
            data = json.loads(line.strip())
            # Skip sidechain entries (subagent calls)
            if data.get('isSidechain', False):
                continue
            
            # Check for usage data in main-chain messages
            if data.get('message', {}).get('usage'):
                timestamp = data.get('timestamp')
                if timestamp and (not most_recent_timestamp or timestamp > most_recent_timestamp):
                    most_recent_timestamp = timestamp
                    most_recent_usage = data['message']['usage']
        except:
            continue
    
    # Calculate context length (input + cache tokens only, NOT output)
    if most_recent_usage:
        context_length = (
            most_recent_usage.get('input_tokens', 0) +
            most_recent_usage.get('cache_read_input_tokens', 0) +
            most_recent_usage.get('cache_creation_input_tokens', 0)
        )
        print(context_length)
    else:
        print(0)
except:
    print(0)
" 2>/dev/null)
        
        # Calculate actual context usage percentage
        if [[ $total_tokens -gt 0 ]]; then
            # Use Python for floating point math (bc not available on all systems)
            progress_pct=$(python3 -c "print(f'{$total_tokens * 100 / $context_limit:.1f}')")
            progress_pct_int=$(python3 -c "print(int($total_tokens * 100 / $context_limit))")
            if [[ $progress_pct_int -gt 100 ]]; then
                progress_pct="100.0"
                progress_pct_int=100
            fi
        else
            progress_pct="0.0"
            progress_pct_int=0
        fi
    else
        # Default values when no transcript available - still add default context
        total_tokens=17900
        progress_pct=$(python3 -c "print(f'{$total_tokens * 100 / $context_limit:.1f}')")
        progress_pct_int=$(python3 -c "print(int($total_tokens * 100 / $context_limit))")
    fi
    
    # Format token count in 'k' format
    formatted_tokens=$(python3 -c "print(f'{$total_tokens // 1000}k')")
    formatted_limit=$(python3 -c "print(f'{$context_limit // 1000}k')")
    
    # Create progress bar (capped at 100%) with Ayu Dark colors
    filled_blocks=$((progress_pct_int / 10))
    if [[ $filled_blocks -gt 10 ]]; then filled_blocks=10; fi
    empty_blocks=$((10 - filled_blocks))
    
    # Ayu Dark colors (converted to closest ANSI 256)
    if [[ $progress_pct_int -lt 50 ]]; then
        bar_color="\033[38;5;114m"  # AAD94C green
    elif [[ $progress_pct_int -lt 80 ]]; then
        bar_color="\033[38;5;215m"  # FFB454 orange
    else
        bar_color="\033[38;5;203m"  # F26D78 red
    fi
    gray_color="\033[38;5;242m"     # Dim for empty blocks
    text_color="\033[38;5;250m"     # BFBDB6 light gray
    reset="\033[0m"
    
    progress_bar="${bar_color}"
    for ((i=0; i<filled_blocks; i++)); do progress_bar+="█"; done
    progress_bar+="${gray_color}"
    for ((i=0; i<empty_blocks; i++)); do progress_bar+="░"; done
    progress_bar+="${reset} ${text_color}${progress_pct}% (${formatted_tokens}/${formatted_limit})${reset}"
    
    echo -e "$progress_bar"
}

# Get model name with color
get_model_name() {
    orange="\033[38;5;215m"  # FFB454 func orange
    reset="\033[0m"
    echo -e "${orange}${model_name}${reset}"
}

# Get git branch with color
get_git_branch() {
    green="\033[38;5;114m"   # AAD94C string green
    reset="\033[0m"
    if [[ -d "$cwd/.git" ]]; then
        cd "$cwd"
        branch_name=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
        echo -e "${green}⎇ ${branch_name}${reset}"
    else
        echo -e "${green}⎇ no-git${reset}"
    fi
}

# Get current task with color
get_current_task() {
    cyan="\033[38;5;111m"    # 59C2FF entity blue
    orange="\033[38;5;215m"  # FFB454 func orange
    reset="\033[0m"
    if [[ -f "$cwd/.dev-journal/state/current_task.json" ]]; then
        # Read both task name and origin
        task_data=$(python3 -c "
import sys, json
try:
    with open('$cwd/.dev-journal/state/current_task.json', 'r') as f:
        data = json.load(f)
        task = data.get('task', 'None')
        origin = data.get('origin', 'unknown')
        print(f'{task}|{origin}')
except:
    print('None|unknown')
" 2>/dev/null)

        task_name="${task_data%|*}"
        origin="${task_data#*|}"

        if [[ "$task_name" == "None" ]]; then
            echo -e "${cyan}No Active Plan${reset}"
        else
            # Determine the prefix based on origin
            if [[ "$origin" == "gemini-cli" ]]; then
                prefix="Gemini Plan:"
            elif [[ "$origin" == "claude-plan-mode" ]]; then
                prefix="Claude Plan:"
            else
                prefix="Active Plan:"
            fi
            echo -e "${orange}${prefix} ${cyan}$task_name${reset}"
        fi
    else
        echo -e "${cyan}No Active Plan${reset}"
    fi
}

# Get DAIC mode with color
get_daic_mode() {
    if [[ -f "$cwd/.dev-journal/state/daic-mode.json" ]]; then
        mode=$(python3 -c "
import sys, json
try:
    with open('$cwd/.dev-journal/state/daic-mode.json', 'r') as f:
        data = json.load(f)
        print(data.get('mode', 'discussion'))
except:
    print('discussion')
" 2>/dev/null)
        if [[ "$mode" == "discussion" ]]; then
            purple="\033[38;5;183m"  # D2A6FF constant purple
            reset="\033[0m"
            echo -e "${purple}MODE: Discussion${reset}"
        else
            green="\033[38;5;114m"   # AAD94C string green
            reset="\033[0m"
            echo -e "${green}MODE: Implementation${reset}"
        fi
    else
        purple="\033[38;5;183m"      # D2A6FF constant purple
        reset="\033[0m"
        echo -e "${purple}MODE: Discussion${reset}"
    fi
}

# Count edited files with color
count_edited_files() {
    yellow="\033[38;5;215m"  # FFB454 func orange
    green="\033[38;5;114m"   # AAD94C string green
    reset="\033[0m"
    if [[ -d "$cwd/.git" ]]; then
        cd "$cwd"
        # Count modified and staged files
        modified_count=$(git status --porcelain 2>/dev/null | grep -E '^[AM]|^.[AM]' | wc -l | xargs || echo "0")
        # Count new/untracked files (lines starting with ??)
        new_count=$(git status --porcelain 2>/dev/null | grep -E '^\?\?' | wc -l | xargs || echo "0")

        # Build output string
        output="${yellow}✎ $modified_count modified${reset}"
        if [[ $new_count -gt 0 ]]; then
            output="$output | ${green}✦ $new_count new${reset}"
        fi
        echo -e "$output"
    else
        echo -e "${yellow}✎ 0 files${reset}"
    fi
}

# Count open tasks with color
count_open_tasks() {
    blue="\033[38;5;111m"    # 73B8FF modified blue
    orange="\033[38;5;215m"  # FFB454 func orange
    reset="\033[0m"
    tasks_dir="$cwd/.dev-journal/plans"
    if [[ -d "$tasks_dir" ]]; then
        # Count .md files that don't contain "Status: done" or "Status: completed"
        # Exclude TEMPLATE.md from count
        # Special handling for plan_from_gemini.md and plan_from_claude.md: only count if non-empty
        open_count=0
        gemini_plan_ready=false
        claude_plan_ready=false
        for task_file in "$tasks_dir"/*.md; do
            if [[ -f "$task_file" ]]; then
                filename="$(basename "$task_file")"

                # Skip TEMPLATE.md
                if [[ "$filename" == "TEMPLATE.md" ]]; then
                    continue
                fi

                # Special handling for plan_from_gemini.md and plan_from_claude.md
                if [[ "$filename" == "plan_from_gemini.md" || "$filename" == "plan_from_claude.md" ]]; then
                    # Only count if file is non-empty
                    if [[ -s "$task_file" ]]; then
                        # Check if it's not completed (match only at start of line for frontmatter)
                        if ! grep -a -q -E -i "^status:\s*(done|completed)" "$task_file" 2>/dev/null; then
                            if [[ "$filename" == "plan_from_gemini.md" ]]; then
                                gemini_plan_ready=true
                            else
                                claude_plan_ready=true
                            fi
                            ((open_count++))
                        fi
                    fi
                else
                    # Regular task files: count if not completed (match only at start of line for frontmatter)
                    if ! grep -a -q -E -i "^status:\s*(done|completed)" "$task_file" 2>/dev/null; then
                        ((open_count++))
                    fi
                fi
            fi
        done

        # Handle display logic
        if [[ "$gemini_plan_ready" == true && "$claude_plan_ready" == true ]]; then
            if [[ $open_count -eq 2 ]]; then
                # Only both AI plans exist
                echo -e "${blue}[gemini & claude plans ready]${reset}"
            else
                # Other tasks + both AI plans
                echo -e "${blue}[$open_count open tasks; ${orange}gemini & claude plans ready${blue}]${reset}"
            fi
        elif [[ "$gemini_plan_ready" == true ]]; then
            if [[ $open_count -eq 1 ]]; then
                # Only gemini plan exists
                echo -e "${blue}[gemini plan ready]${reset}"
            else
                # Other tasks + gemini plan
                echo -e "${blue}[$open_count open tasks; ${orange}gemini plan ready${blue}]${reset}"
            fi
        elif [[ "$claude_plan_ready" == true ]]; then
            if [[ $open_count -eq 1 ]]; then
                # Only claude plan exists
                echo -e "${blue}[claude plan ready]${reset}"
            else
                # Other tasks + claude plan
                echo -e "${blue}[$open_count open tasks; ${orange}claude plan ready${blue}]${reset}"
            fi
        else
            # No AI plans
            echo -e "${blue}[no plan files detected]${reset}"
        fi
    else
        echo -e "${blue}[no plan files detected]${reset}"
    fi
}

# Build the complete statusline
progress_info=$(calculate_context)
model_info=$(get_model_name)
branch_info=$(get_git_branch)
task_info=$(get_current_task)
daic_info=$(get_daic_mode)
files_info=$(count_edited_files)
tasks_info=$(count_open_tasks)

# Output the complete statusline in two lines with color support
# Line 1: Progress bar | Model name | Git branch | Current task
# Line 2: DAIC mode | Files edited | Open tasks
echo -e "$progress_info | $model_info | $branch_info"
echo -e "$daic_info | $files_info | $tasks_info | $task_info"
