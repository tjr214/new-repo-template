# New Repository Template with Task Master AI & Context7

A comprehensive project template with pre-configured Task Master AI integration for structured, task-driven development. This template provides a fully set up environment to help you start new projects with an AI-assisted development workflow.

## Features

- **Cursor AI Integration**: Custom Cursor rules for enhanced AI-assisted development
- **Pre-configured for Task Master AI**: Manage your development process with AI-generated tasks and structured workflows
- **MCP Server Setup**: Model Context Protocol server configurations for Task Master and Context7
- **PRD-to-Tasks Workflow**: Convert product requirements documents into structured tasks automatically
- **Task Management**: Comprehensive tools for task creation, expansion, tracking, and dependency management

## Getting Started

1. **Clone this template**:

   ```bash
   git clone https://github.com/tjr214/new-repo-template.git my-project
   cd my-project
   ```

2. **Configure environment variables**:
   Copy the example environment file and add your API keys:

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file and add:

   - `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude
   - `PERPLEXITY_API_KEY`: (Optional but recommended) Your Perplexity API key for research-backed features

3. **Install dependencies**:

   Run the following scripts to install and update required packages:

   ```bash
   # Install/update Task Master (MANDATORY)
   ./update_packages.sh taskmaster

   # Install/update npm packages (MANDATORY)
   ./update_packages.sh npm

   # Optional: For Python components (only if your project uses Python)
   ./update_packages.sh python
   ```

4. **Create your PRD**:

   - Use the `prompts/create-new-PRD-file.md` prompt to chat with the AI to create your PRD.
   - Afterwards, edit `scripts/prd.txt` to make any required manual changes.

5. **Generate initial tasks**:

   - Use the `prompts/initial-Task-generation.md` prompt to begin the initial task generation process and create the `tasks.json` file.
   - Next, use the `prompts/generate-individual-Tasks.md` prompt to generate individual task files from `tasks.json`.

6. **Start developing with Cursor AI**:
   - Open the project in Cursor IDE and leverage the custom rules and Task Master integration.

## Using Task Master

### Key Commands (CLI)

- **List tasks**: `npx task-master list`
- **Generate task files**: `npx task-master generate`
- **Parse PRD**: `npx task-master parse-prd scripts/prd.txt`
- **Show next task**: `npx task-master next`
- **Expand a task**: `npx task-master expand --id=<id>`
- **Update task status**: `npx task-master set-status --id=<id> --status=<status>`

### Development Workflow

1. **Start with a PRD**: Create a detailed PRD in `scripts/prd.txt` using the `create-new-PRD-file.md` prompt. If you already have a PRD file, place it in `scripts/prd.txt` and use the `read-PRD-file.md` prompt to process it.
2. **Generate tasks**: Parse the PRD to generate structured tasks using the `initial-Task-generation.md` and `generate-individual-Tasks.md` prompts.
3. **Analyze complexity**: Use task complexity analysis to identify tasks that need to be broken down
   - E.g., "Task 5 seems complex. Can you break it down into subtasks?"
   - "Can you help me expand Task 4?"
   - "Can you analyze the complexity of our Tasks?"
   - "I'd like to implement Task 6. What does it involve?"
   - etc.
4. **Stay on track**:
   - "What tasks are available to work on next?"
   - "What is the status of Task 5?"
   - "Show me all high priority Tasks."
   - "Task 2 is now complete. Please update its status."
   - etc.
5. **Update as you go**: Keep tasks up-to-date as your implementation evolves

## Customization

### Task Master Configuration

Edit `.env` to configure Task Master behavior:

- Model selection (Claude and Perplexity)
- Token limits and temperature
- Default subtask count and priority

### MCP Server Configuration

MCP server configurations are defined in `.cursor/mcp.json`:

- Task Master MCP server for task management integration
- Context7 for library documentation lookup

### Custom Cursor Rules

Custom rules in `.cursor/rules/` enhance the AI's capabilities:

- `dev_workflow.mdc`: Guide for Task Master development workflows
- `taskmaster.mdc`: Comprehensive Task Master tool reference
- `cursor_rules.mdc`: Guidelines for creating and maintaining Cursor rules
- `self_improve.mdc`: Guidance for continuously improving rules
- `global_rules.mdc`: Global rules for all interactions

## Requirements

- Anthropic API key
- [Cursor IDE](https://cursor.sh/) for best experience

## Learn More

- See [README-task-master.md](README-task-master.md) for a complete guide to Task Master
