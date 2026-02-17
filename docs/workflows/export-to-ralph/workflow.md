# Export to RALPH Task Plan Workflow

**Goal:** Transform BMAD epics and stories into comprehensive YAML task plans that RALPH can execute using YELLOW-RED-GREEN-BLUE TDD methodology.

**Your Role:** You are a meticulous implementation planner who transforms BMAD epic and story artifacts into detailed, actionable task plans with explicit file paths, code snippets, test specifications, and validation criteria.

---

## WORKFLOW ARCHITECTURE

This workflow uses **step-file architecture** for disciplined execution:

### Core Principles

- **Micro-file Design**: Each step is self-contained with specific responsibilities
- **Just-In-Time Loading**: Only load current step file
- **Sequential Enforcement**: Complete steps in order
- **Context Preservation**: Pass context between steps
- **YAML Output**: Generate valid YAML following the JSON schema

### Step Processing Rules

1. **READ COMPLETELY**: Always read the entire step file before taking action
2. **FOLLOW SEQUENCE**: Execute all numbered sections in order
3. **WAIT FOR INPUT**: If a menu is presented, halt and wait for user selection
4. **SAVE STATE**: Track progress as you move through steps
5. **LOAD NEXT**: When directed, load and execute the next step file

### Critical Rules (NO EXCEPTIONS)

- 🛑 **NEVER** load multiple step files simultaneously
- 📖 **ALWAYS** read entire step file before execution
- 🚫 **NEVER** skip steps or optimize the sequence
- 🎯 **ALWAYS** follow the exact instructions in the step file
- ⏸️ **ALWAYS** halt at menus and wait for user input

---

## INITIALIZATION SEQUENCE

### 1. Configuration and Context

Set up the workflow context:

```yaml
Paths:
  - task_schema: "{project-root}/.template_scripts/task-template-schema.json"
  - task_template: "{project-root}/docs/tasks/task-template.yaml"
  - task_example: "{project-root}/docs/tasks/task-template-example.yaml"
  - output_directory: "{project-root}/docs/tasks/"
  - completed_directory: "{project-root}/docs/tasks/completed/"

BMAD Artifact Locations:
  - epics: "{project-root}/_bmad-output/planning-artifacts/*epic*.md"
  - stories: "{project-root}/_bmad-output/implementation-artifacts/*.md"
  - sprint_status: "{project-root}/_bmad-output/implementation-artifacts/sprint-status.yaml"
```

### 2. First Step Execution

Load, read the full file, and then execute `{project-root}/docs/workflows/export-to-ralph/steps/step-01-detect-context.md` to begin the workflow.

---

## WORKFLOW OVERVIEW

The export process follows this sequence:

```
Step 1: Detect Context
↓ Scan for epic and story artifacts
↓ Identify epic/story coverage and grouping
↓ Present findings to user
↓ User selects ONE epic to export

Step 2: Extract Data & Analyze Codebase
↓ Extract selected epic and all related stories
↓ Search codebase for YELLOW phase context
↓ Structure into phases/steps/instructions with TDD

Step 3: Transform to YAML & Validate
↓ Convert to YAML format
↓ Validate using .template_scripts/validate_template.py
↓ Show preview to user

Step 4: Write Task File & Preserve BMAD Artifacts
↓ Write to docs/tasks/{task-name}.yaml
↓ Preserve epic/story source artifacts (no delete/archive)
↓ Confirm success
```

---

## OUTPUT REQUIREMENTS

The generated YAML file MUST:

### Schema Compliance

- ✅ Validate using .template_scripts/validate_template.py docs/tasks/{task-name}.yaml
- ✅ Include all required fields: metadata, task, phases, steps, instructions
- ✅ Use correct status values: pending, active, blocked, done
- ✅ Follow ID patterns (phase-N, step-N.M, instr-N.M.P)

### TDD Methodology

- ✅ Every instruction includes YELLOW-RED-GREEN-BLUE phases
- ✅ YELLOW: Explicit file reads and context gathering
- ✅ RED: Complete test specifications with expected failures
- ✅ GREEN: Implementation code snippets
- ✅ BLUE: Refactoring and validation steps

### Completeness

- ✅ File paths are explicit and absolute
- ✅ Code snippets are complete and runnable
- ✅ Context references point to existing files
- ✅ Completion criteria are measurable
- ✅ Performance targets are specified
- ✅ Validation steps are clear

### Self-Containment

- ✅ All context is embedded in instructions
- ✅ No placeholders or "TBD" items
- ✅ Dependencies are explicitly stated

---

## SUCCESS METRICS

This workflow is successful when:

- ✅ Epic and story artifacts are detected and summarized
- ✅ User provides complete task context
- ✅ YAML structure validates against schema
- ✅ All instructions follow TDD methodology
- ✅ Task file is written to correct location
- ✅ Source BMAD epic/story artifacts remain unchanged
- ✅ User confirms the task plan is ready

---

## EXECUTION START

Begin by loading and executing:

**`{project-root}/docs/workflows/export-to-ralph/steps/step-01-detect-context.md`**

Remember: Read the ENTIRE step file before taking any action!
