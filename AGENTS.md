## Table of Contents

- [Table of Contents](#table-of-contents)
- [1. CRITICAL LEVEL INSTRUCTIONS](#1-critical-level-instructions)
  - [1.1 CRITICAL PYTHON INSTRUCTIONS](#11-critical-python-instructions)
  - [1.2 CRITICAL TYPESCRIPT INSTRUCTIONS](#12-critical-typescript-instructions)
  - [1.3 BTCA SETUP AND USAGE](#13-btca-setup-and-usage)
    - [1.3.1 When Agents Should Use BTCA](#131-when-agents-should-use-btca)
    - [1.3.2 Core BTCA Commands (Agent Reference)](#132-core-btca-commands-agent-reference)
    - [1.3.3 Standard Workflow for Adding/Updating BTCA Resources](#133-standard-workflow-for-addingupdating-btca-resources)
    - [1.3.4 Project vs Global Behavior](#134-project-vs-global-behavior)
    - [1.3.5 BTCA Safety and Maintenance Rules](#135-btca-safety-and-maintenance-rules)

## 1. CRITICAL LEVEL INSTRUCTIONS

**CRITICAL**:

- _DO NOT use lazy placeholders._ Output the FULL code block required for the search/replace.

- **SUPREMELY CRITICAL TDD INSTRUCTIONS FOR IMPLEMENTATION MODE**: When implementing, _ALWAYS use a special TDD loop we call YELLOW-RED-GREEN-BLUE._ Ensure this is properly reflected in all Plans made and executed. During the YELLOW Phase: search the codebase and read all the files necessary to understand the task at hand. Use the `btca ask` command to get the necessary context for any dependencies or libraries we are working with. RED, GREEN and BLUE (refactor) Phases remain the same as in a normal TDD loop. The YELLOW phase is to prime you with all the necessary context to correctly do the work.

- When describing your planned workflow to users, explicitly mention ALL of the parts of the YELLOW phase, including the `btca ask` command. Don't just execute the workflow or use these tools silently - communicate that it's part of the process.

- **ALWAYS** be updating the Living Documentation (`docs/LIVING_DOCS.md`) as we complete implementation sections. Ensure this is included in all Plans made and executed. This also includes updating the `PROGRESS.md` tracker in the project root and the `docs/ARCHITECTURE.md` document, as well. All the docs must be kept up-to-date and in-sync at all times.

- IMPORTANT: NEVER OVERWRITE A `SESSION_X_SUMMARY.md` file. _Always create a new session summary!_

- All of our unit and integration tests are to be stored in the `tests/` directory in the project root.

- Use the `btca` tool to get the necessary context and/or documentation for any dependencies or libraries we are working with.

- **DOUBLE CRITICAL**: You have to READ files before the system will allow you to edit, update or write to them.

- **TRIPLE CRITICAL**: Do NOT add the user's personal information to the code, tests, documentation or anything else. Any of that personal information is only for use in conversation and dialogue with the user. Only the files and directories in the project directory are backed up and protected by Git. Therefore, in order to access, write, delete, modify, or do ANYTHING with files/directories OUTSIDE the project you must first get EXPLICIT PERMISSION from the user before proceeding. Otherwise, you may cause irreversible damage to the user's system without even realizing you have done anything at all!

### 1.1 CRITICAL PYTHON INSTRUCTIONS

- **IMPORTANT**: Python projects use Python 3.14+, and `uv` and `pyproject.toml` for project management. All dev dependencies should be specified in the `dev` dependency group. Use `hatchling` as the build backend. When adding libraries to the project, look up their latest version and use that version number for the pin with the `>=` operator. Do NOT use `uv pip install` to install packages as this will not update the `pyproject.toml`. When implementing concurrency use Python 3.14+'s `concurrent.interpreters` to achieve _true multi-core parallelism._

### 1.2 CRITICAL TYPESCRIPT INSTRUCTIONS

- **IMPORTANT**: TypeScript projects use `bun` for package management. When adding libraries to the project, look up their latest version and use that version number for the pin with the `^` operator. **NEVER use the `any` type** - always use proper type definitions, generics, or `unknown` with type guards when the type is truly unknown. Prefer strict type safety and leverage TypeScript's type system fully. Use `interface` for object shapes and `type` for unions, intersections, and complex type compositions.

### 1.3 BTCA SETUP AND USAGE

- **Purpose**: BTCA is the dependency-context retrieval layer. Use it to answer implementation questions grounded in official framework/tool sources instead of guessing.
- **Source of truth**: Treat `btca` CLI output as runtime state (project + global). Also, all project-level resources from `btca status` must sync to `docs/BTCA_RESOURCES.md`. **IMPORTANT**: BTCA_RESOURCES.md must ALWAYS be an accurate reflection of the project-level resources show in `btca status`.
- **Current project BTCA config**:
  - Config file: `btca.config.jsonc`
  - Resources:
    - Run `btca resources` to see all available resources
    - Current Project-level Resources, see:

@docs/BTCA_RESOURCES.md

#### 1.3.1 When Agents Should Use BTCA

- Use BTCA during YELLOW phase research for framework/tool behavior, API specifics, config semantics, and version-specific guidance.
- Prefer BTCA over web search when configured resources already cover the question.
- If we need to add a dependency, library or package to the project, make sure to also add it to BTCA via `btca add ...` and then update the BTCA_RESOURCES.md file (see below for more on adding resources).
- If a needed dependency is missing, propose adding a resource (with the user's confirmation) before deep implementation.

#### 1.3.2 Core BTCA Commands (Agent Reference)

- Discovery and status:
  - `btca --help`
  - `btca status`
  - `btca resources`
- Asking questions:
  - `btca ask -r <resource> -q "<question>"`
  - Multi-resource query: `btca ask -r <res1> -r <res2> -q "<question>"`
  - Cleaner output for agent pipelines: add `--sub-agent` (optionally `--no-thinking --no-tools`) to strip the additional output from the CLI
- Resource management:
  - Add: `btca add -n <name> -t <git|npm|local> [reference]` (and then update `docs/BTCA_RESOURCES.md`)
  - Remove: `btca remove <name>` (also update `docs/BTCA_RESOURCES.md`)
  - Validate: `btca resources` and `btca status`

#### 1.3.3 Standard Workflow for Adding/Updating BTCA Resources

1. Scan manifests: `pyproject.toml` and `package.json`.
2. Identify major frameworks/libraries/tools that materially affect implementation decisions.
3. Propose one BTCA resource per major dependency with sensible defaults:
   - `name`: stable, concise identifier
   - `type`: `git`, `npm`, or `local`
   - `branch`: usually `main` (or dependency default branch)
   - `searchPaths`: docs and core implementation directories
   - `specialNotes`: short, actionable guidance for future agents
4. **Ask for explicit user confirmation for each proposed resource before adding.**
5. Add only confirmed resources with `btca add ...`.
6. Sync all project-level resources with the list at `docs/BTCA_RESOURCES.md`. Add in new resources as <configured_resource></configured_resource>s in between the <current_btca_resources></current_btca_resources> tags.
7. Validate with `btca resources` and `btca status`.

#### 1.3.4 Project vs Global Behavior

- `btca status` and `btca resources` may show both global and project resources.
- For repo decisions, prioritize project resources from `btca.config.jsonc`.
- Use global resources as supplemental context only; do not treat them as project defaults unless copied into project config with confirmation.

#### 1.3.5 BTCA Safety and Maintenance Rules

- **CRITICAL**: Avoid destructive commands without explicit user request:
  - `btca clear` (only safe to do if the btca tool returns an error specifying that you try running `btca clear` OR if the user requests it)
  - `btca wipe` (deletes BTCA configs -- NEVER SAFE!)
- Keep `specialNotes` practical and implementation-focused; do not include secrets or personal data.
- Re-validate after any model/provider/resource change with `btca status` + `btca resources`.
