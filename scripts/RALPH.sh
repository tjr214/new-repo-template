#!/bin/bash

# Which agent should OpenCode use to do the work?
# AGENT="bmad-master"
AGENT="build"

# Default model
DEFAULT_MODEL="synthetic/hf:nvidia/Kimi-K2.5-NVFP4"

# ANSI styles
RESET="\033[0m"
BOLD="\033[1m"
DIM="\033[2m"
CYAN="\033[36m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
MAGENTA="\033[35m"

# Function to select model
select_model() {
    local models
    models=(
        "synthetic/hf:moonshotai/Kimi-K2.5"
        "synthetic/hf:nvidia/Kimi-K2.5-NVFP4"
        "synthetic/hf:zai-org/GLM-4.7"
        "synthetic/hf:deepseek-ai/DeepSeek-V3.2"
        "synthetic/hf:MiniMaxAI/MiniMax-M2.1"
        "openai/gpt-5.3-codex"
        "opencode/kimi-k2.5-free"
        "opencode/minimax-m2.5-free"
    )

    echo "" >&2
    echo -e "${BOLD}${CYAN}Available models:${RESET}" >&2
    echo "" >&2
    local i
    for i in "${!models[@]}"; do
        echo -e "${BOLD}${MAGENTA}$((i + 1)).${RESET} ${models[$i]}" >&2
    done
    echo "" >&2

    local choice
    read -r -p "Select model (1-${#models[@]}) or press Enter for default [${DEFAULT_MODEL}]: " choice

    if [ -z "$choice" ]; then
        echo "$DEFAULT_MODEL"
        return
    fi

    if [[ "$choice" =~ ^[0-9]+$ ]]; then
        if [ "$choice" -ge 1 ] && [ "$choice" -le "${#models[@]}" ]; then
            echo "${models[$((choice - 1))]}"
            return
        fi
    fi

    for i in "${!models[@]}"; do
        if [ "${models[$i]}" = "$choice" ]; then
            echo "${models[$i]}"
            return
        fi
    done

    echo -e "${YELLOW}Invalid selection.${RESET} Defaulting to ${DEFAULT_MODEL}." >&2
    echo "$DEFAULT_MODEL"
}

# Check if optional task file parameter is provided
TASK_FILE=""
if [ -n "$1" ]; then
    TASK_FILE="$1"
else
    echo ""
    echo -e "${BOLD}${CYAN}Available task files:${RESET}"
    echo ""
    
    # Set custom prompt for select
    PS3="Select a task file (enter number): "
    
    # Use select to display menu and get user choice
    select TASK_FILE in $(find docs/tasks -maxdepth 1 -name "*.yaml" ! -name "task-template.yaml" ! -name "task-template-example.yaml" -type f | sort); do
        if [ -n "$TASK_FILE" ]; then
            echo ""
            echo -e "${GREEN}Selected:${RESET} ${YELLOW}${TASK_FILE}${RESET}"
            echo ""
            echo -e "${DIM}----------------------------------------------------------${RESET}"
            echo ""
            break
        else
            echo -e "${YELLOW}Invalid selection, please try again.${RESET}"
            echo ""
        fi
    done
    
    # Check if user cancelled (Ctrl+C would exit, but just in case)
    if [ -z "$TASK_FILE" ]; then
        echo -e "${RED}No task file selected${RESET}"
        exit 1
    fi
fi

# Validate selected task file against schema
python3 .template_scripts/validate_template.py "$TASK_FILE"
if [ $? -ne 0 ]; then
    echo -e "${RED}Task file validation failed${RESET}"
    exit 1
fi

# Decorative spacer for user UX
echo ""
echo -e "${DIM}----------------------------------------------------------${RESET}"

# Function to extract YAML data
extract_yaml_data() {
    python3 <<EOF
import yaml
import json
import sys

def extract_statuses(data, parent_key="", items=None):
    """Recursively extract all items with status fields."""
    if items is None:
        items = []
    
    if isinstance(data, dict):
        # Extract current item if it has an id and status
        if 'id' in data and 'status' in data:
            item = {
                'id': data['id'],
                'name': data.get('name', ''),
                'status': data['status'],
                'type': parent_key
            }
            if data.get('blocked_reason'):
                item['blocked_reason'] = data['blocked_reason']
            items.append(item)
        
        # Recurse through all keys
        for key, value in data.items():
            if key in ['phases', 'sub_phases', 'steps', 'instructions']:
                extract_statuses(value, key.rstrip('s'), items)
            elif isinstance(value, (dict, list)):
                extract_statuses(value, parent_key, items)
    
    elif isinstance(data, list):
        for item in data:
            extract_statuses(item, parent_key, items)
    
    return items

try:
    with open('$TASK_FILE', 'r') as f:
        yaml_content = yaml.safe_load(f)
    
    task = yaml_content.get('task', {})
    task_name = task.get('name', 'Unknown Task')
    task_status = task.get('status', 'unknown')
    
    # Extract all sub-items
    items = extract_statuses(task.get('phases', []), 'phase')
    
    output = {
        'task_name': task_name,
        'task_status': task_status,
        'items': items
    }
    
    print(json.dumps(output))
    
except Exception as e:
    print(json.dumps({'error': str(e)}), file=sys.stderr)
    sys.exit(1)
EOF
}

# Choose model (with default)
MODEL=$(select_model)
echo ""
echo -e "${GREEN}Selected model:${RESET} ${YELLOW}${MODEL}${RESET}"
echo ""
echo -e "${DIM}----------------------------------------------------------${RESET}"
# Run the visualization script
VISUALIZATION_OUTPUT=$(python3 .template_scripts/visualize_plan.py "$TASK_FILE")
echo "$VISUALIZATION_OUTPUT"
if [ $? -ne 0 ]; then
    echo -e "${RED}Task visualization failed${RESET}"
    exit 1
fi
echo ""
echo -e "${DIM}----------------------------------------------------------${RESET}"

# Track iterations
ITERATION_COUNTER=1

# -----------------------------

# Main loop - keep running until task is done
while :; do
    # Extract current YAML data
    YAML_DATA=$(extract_yaml_data)
    
    # Parse JSON output using jq
    TASK_NAME=$(echo "$YAML_DATA" | jq -r '.task_name')
    TASK_STATUS=$(echo "$YAML_DATA" | jq -r '.task_status')
    
    # Check if task is done
    if [ "$TASK_STATUS" = "done" ]; then
        echo ""
        echo -e "${BOLD}${GREEN}==========================================${RESET}"
        echo -e "${BOLD}${GREEN}🎉 Task completed:${RESET} $TASK_NAME"
        echo -e "${BOLD}${GREEN}==========================================${RESET}"
        echo ""
        break
    fi
    
    # Generate timestamp in YYYY-MM-DD-HH:MM AM/PM format
    TIMESTAMP=$(date "+%Y-%m-%d-%I:%M %p")

    # Build the Prompt
    # TODO -- write the build_prompt() function and use it here. Assign the output to PROMPT instead of what we have below:
    PROMPT="Have Bmad-Master say hello"
    
    echo ""
    echo -e "${BOLD}${CYAN}Attempt Number:${RESET} ${YELLOW}${ITERATION_COUNTER}${RESET}"
    echo -e "${GREEN}Active Task:${RESET} ${YELLOW}${TASK_NAME}${RESET} (${MAGENTA}${TASK_FILE}${RESET})"
    echo -e "${GREEN}Selected Model:${RESET} ${YELLOW}${MODEL}${RESET}"

    # Run opencode with current session title
    opencode run -m "$MODEL" --title "RALPH: $TASK_NAME [$ITERATION_COUNTER]" --agent "$AGENT" $PROMPT
    echo ""
    echo -e "${DIM}----------------------------------------------------------${RESET}"
    echo ""
    ITERATION_COUNTER=$((ITERATION_COUNTER + 1))
done
