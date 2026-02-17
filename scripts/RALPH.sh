#!/bin/bash

# Which agent should OpenCode use to do the work?
# AGENT="bmad-master"
AGENT="build"
BMAD_AGENT="bmad-master"

# Default model
DEFAULT_MODEL="synthetic/hf:nvidia/Kimi-K2.5-NVFP4"

# Maximum number of iterations
MAX_ITERATIONS=5

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

# Function to generate task visualization
generate_visualization() {
    local task_file="$1"
    local visualization_output

    visualization_output=$(python3 .template_scripts/visualize_plan.py "$task_file")
    local status=$?
    if [ "$status" -ne 0 ]; then
        return "$status"
    fi

    printf '%s' "$visualization_output"
}

# Build the one-time closeout prompt used after task completion.
build_closeout_prompt() {
    local task_name="$1"
    local timestamp="$2"
    local task_visualization="$3"

    cat <<EOF
You are running the automated closeout phase for a completed implementation plan.

Context:
- Timestamp: ${timestamp}
- Task name: ${task_name}

${task_visualization}

MANDATORY CLOSEOUT CONTRACT
1) BMAD epic and story artifacts are source-of-truth. Keep them intact.
2) DO NOT delete, move, archive, or rename BMAD epic/story artifacts.
3) If product/architecture context is needed, read BMAD markdown files by path.
4) Reconcile implementation state back into BMAD tracking.

Closeout Checklist (execute in order):
1. Verify completion state
   - Read the task status visualization provided above and confirm task/phases/steps/instructions are all "done".
   - Confirm no items are "blocked".

2. Synchronize BMAD execution records
   - Ensure story statuses are aligned with completed implementation.
   - Ensure epic status is aligned for this exported epic.
   - Ensure _bmad-output/implementation-artifacts/sprint-status.yaml reflects final story/epic states.

3. Update checkpoint documentation
   - Update PROGRESS.md.
   - Update docs/LIVING_DOCS.md.
   - Update docs/ARCHITECTURE.md if implementation changed architecture details.
   - Create a NEW session summary file (do not overwrite any existing SESSION_X_SUMMARY.md).

4. Validate project state
   - Run relevant test/lint/build checks used by this repo.

Important constraints:
- No destructive cleanup of BMAD artifacts.
- No placeholders; use concrete file paths and concrete updates.
- Keep responses concise and action-oriented.
EOF
}

# Build the prompt for each iterative loop
build_prompt() {
    local task_name="$1"
    local timestamp="$2"
    local task_visualization="$3"

    cat <<EOF
You are running...

Context:
- Timestamp: ${timestamp}
- Task name: ${task_name}

${task_visualization}

EOF
}

# Choose model (with default)
MODEL=$(select_model)
echo ""
echo -e "${GREEN}Selected model:${RESET} ${YELLOW}${MODEL}${RESET}"
echo ""
echo -e "${DIM}----------------------------------------------------------${RESET}"

# Track iterations
ITERATION_COUNTER=1

# -----------------------------

# Main loop - keep running until task is done
while :; do
    if [ "$ITERATION_COUNTER" -gt "$MAX_ITERATIONS" ]; then
        echo ""
        echo -e "${YELLOW}Maximum iterations reached (${MAX_ITERATIONS}). Stopping loop.${RESET}"
        break
    fi

    # Extract current YAML data
    YAML_DATA=$(extract_yaml_data)
    
    # Parse JSON output using jq
    TASK_NAME=$(echo "$YAML_DATA" | jq -r '.task_name')
    TASK_STATUS=$(echo "$YAML_DATA" | jq -r '.task_status')

    # Generate timestamp in YYYY-MM-DD-HH:MM AM/PM format
    TIMESTAMP=$(date "+%Y-%m-%d-%I:%M %p")

    # Run the visualization script, get the variable, display the output
    VISUALIZATION_OUTPUT=$(generate_visualization "$TASK_FILE")
    if [ $? -ne 0 ]; then
        echo -e "${RED}Task visualization failed${RESET}"
        exit 1
    fi
    echo "$VISUALIZATION_OUTPUT"

    # Build the Prompts
    # TODO -- write the build_prompt() function and use it here. Assign the output to PROMPT instead of what we have below:
    PROMPT=$(build_prompt "$TASK_NAME" "$TIMESTAMP" "$VISUALIZATION_OUTPUT")

    CLOSEOUT_PROMPT=$(build_closeout_prompt "$TASK_NAME" "$TIMESTAMP" "$VISUALIZATION_OUTPUT")
    
    # Check if task is done
    if [ "$TASK_STATUS" = "done" ]; then
        echo ""
        echo -e "${BOLD}${GREEN}==========================================${RESET}"
        echo -e "${BOLD}${GREEN}🎉 Task completed:${RESET} $TASK_NAME"
        echo -e "${BOLD}${GREEN}==========================================${RESET}"
        echo ""
        # TODO: build closeout prompt and run the agent to sync back up with the BMad System.
        opencode run -m "$MODEL" --title "RALPH: $TASK_NAME [CLOSEOUT PHASE]" --agent "$BMAD_AGENT" "$CLOSEOUT_PROMPT"
        break
    fi
    
    echo ""
    echo -e "${BOLD}${CYAN}Loop Number:${RESET} ${YELLOW}${ITERATION_COUNTER}${RESET}"
    echo -e "${GREEN}Active Task:${RESET} ${YELLOW}${TASK_NAME}${RESET} (${MAGENTA}${TASK_FILE}${RESET})"
    echo -e "${GREEN}Selected Model:${RESET} ${YELLOW}${MODEL}${RESET}"

    # Run opencode with current session title
    # opencode run -m "$MODEL" --title "RALPH: $TASK_NAME [$ITERATION_COUNTER]" --agent "$AGENT" $PROMPT
    echo ""
    echo -e "${DIM}----------------------------------------------------------${RESET}"
    echo ""
    ITERATION_COUNTER=$((ITERATION_COUNTER + 1))
done
