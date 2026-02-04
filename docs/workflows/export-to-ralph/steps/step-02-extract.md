# Step 2: Extract Data & Analyze Codebase

## MANDATORY EXECUTION RULES (READ FIRST):

- 📊 **COMPREHENSIVE EXTRACTION**: Pull ALL relevant data from artifacts (not type-limited)
- 🔍 **USE EXPLORE SUB-AGENT**: Leverage Task tool with explore sub-agent for codebase analysis
- 🏗️ **INTELLIGENT STRUCTURING**: Map extracted data to phases/steps/instructions
- ✅ **TDD ENRICHMENT**: Add YELLOW-RED-GREEN-BLUE phases to all instructions
- 🚫 **NO GAPS**: Every instruction must be complete and actionable
- 🎯 **SPECIFIC YELLOW PHASES**: Use explore findings to create precise context-gathering instructions

---

## CONTEXT FROM STEP 1:

You have loaded artifacts from Step 1:
```yaml
loaded_artifacts:
  - name: "..."
    path: "..."
    type: "..."
```

---

## YOUR TASK:

Extract all relevant implementation data from BMAD artifacts and use the explore sub-agent to analyze the codebase, generating comprehensive, specific task instructions with detailed YELLOW phases.

---

## EXECUTION SEQUENCE:

### 1. Read All Selected Artifacts

For each artifact from Step 1, read the complete file:

```bash
# Example for each artifact
cat {artifact_path}
```

Store full content in memory for extraction.

---

### 2. Extract ALL Relevant Data

**From the artifacts, extract EVERYTHING relevant:**

#### **Task-Level Information:**
- ✅ Task/feature name
- ✅ Complete description with business context
- ✅ Why this is being built (rationale)
- ✅ Success criteria
- ✅ Overall constraints

#### **Requirements & Acceptance Criteria:**
- ✅ Functional requirements
- ✅ Non-functional requirements (performance, security, etc.)
- ✅ User stories
- ✅ Acceptance criteria (Given/When/Then format)
- ✅ Edge cases to handle

#### **Architecture & Technical Decisions:**
- ✅ Technology choices and rationale
- ✅ Patterns to follow
- ✅ Integration points
- ✅ Data models and schemas
- ✅ API contracts
- ✅ Design decisions

#### **Implementation Details:**
- ✅ File paths mentioned
- ✅ Code snippets or examples
- ✅ Dependencies to install
- ✅ Configuration required
- ✅ Environment setup

#### **Testing & Validation:**
- ✅ Test specifications
- ✅ Test scenarios
- ✅ Performance targets (latency, throughput, etc.)
- ✅ Coverage requirements
- ✅ Validation criteria

#### **Context & References:**
- ✅ Existing files to reference
- ✅ Patterns used elsewhere in codebase
- ✅ Similar implementations
- ✅ Documentation references

---

### 3. Analyze Codebase for YELLOW Phase Instructions

**Use the explore sub-agent to discover codebase context:**

Launch the explore sub-agent with "very thorough" mode to analyze the codebase and identify patterns, files, and implementations relevant to the task.

**For each key component mentioned in artifacts, use the Task tool with explore sub-agent:**

#### **A. Identify Existing Patterns:**

```
Launch explore sub-agent for: "Find files and patterns related to {component_type} in the codebase. Search for similar implementations, existing patterns, and conventions. Be very thorough."

Example queries:
- "Find middleware patterns and implementations in this codebase"
- "Locate test conventions and existing test files"
- "Discover authentication/authorization patterns"
- "Find existing API route definitions and patterns"
```

#### **B. Identify Dependencies and Package Usage:**

```
Launch explore sub-agent for: "Search for usage of {package_name} in the codebase. Find import patterns, configuration files, and existing integrations. Be very thorough."

Example queries:
- "Find all Redis usage and configuration patterns"
- "Locate FastAPI usage and route definitions"
- "Discover database connection and ORM patterns"
- "Find existing dependency injection patterns"
```

#### **C. Identify Integration Points:**

```
Launch explore sub-agent for: "Identify integration points for {feature_type}. Find related files, connection patterns, and existing implementations. Be very thorough."

Example queries:
- "Find database connection patterns and configuration"
- "Locate API integration points and existing endpoints"
- "Discover service layer patterns and implementations"
- "Find error handling and logging patterns"
```

#### **D. Consolidate Explore Results:**

After explore sub-agent completes, consolidate findings:
- File paths discovered
- Purpose (what pattern/implementation it demonstrates)
- Relevance (why RALPH should read it during YELLOW phase)
- Code snippets or examples found
- Pattern observations

---

### 4. Structure Into Phases

**Infer logical implementation phases from the extracted data:**

**Common phase patterns:**

**For new features:**
1. Design & Data Modeling
2. Core Implementation
3. Testing & Validation
4. Documentation

**For refactoring:**
1. Analysis & Planning
2. Incremental Refactoring
3. Validation & Regression Testing
4. Cleanup & Documentation

**For integrations:**
1. Setup & Configuration
2. Integration Layer
3. Error Handling & Resilience
4. Testing & Monitoring

**Create phases based on artifact content, not templates!**

---

### 5. Break Down Into Steps

**For each phase, identify discrete implementation steps:**

**Example extraction logic:**

If artifact mentions "Create Redis-backed rate limiter":
- Step 1: Define configuration models
- Step 2: Implement rate limit strategy
- Step 3: Create middleware/dependency
- Step 4: Add performance tests

**Extract from requirements, not guess!**

---

### 6. Generate Comprehensive Instructions with Specific YELLOW

**For each step, create 1-5 detailed instructions:**

#### **Instruction Template:**

```yaml
- id: "instr-{N}.{M}.{P}"
  content: |
    **File:** {explicit_file_path}
    
    **YELLOW Phase (Gather Context):**
    {SPECIFIC codebase reading instructions generated from analysis}
    
    - Read `{specific_file_1}` to understand {specific_pattern}
    - Read `{specific_file_2}` for {test_conventions}
    - Search for {specific_usage}: `rg "{search_pattern}" src/`
    - Review `{config_file}` for {configuration_pattern}
    
    **RED Phase (Write Tests First):**
    {Test specifications extracted from artifact}
    
    Create `{test_file_path}`:
    
    ```python
    {complete_test_code_from_artifact_or_inferred}
    ```
    
    Run: `pytest {test_file_path} -v`
    Expected: FAIL (code doesn't exist yet)
    
    **GREEN Phase (Implement to Pass Tests):**
    {Implementation guidance from artifact}
    
    Create `{implementation_file_path}`:
    
    ```python
    {implementation_code_from_artifact_or_skeleton}
    ```
    
    Install dependencies: `uv add {package}>=X.Y.Z`
    
    Run: `pytest {test_file_path} -v`
    Expected: PASS
    
    **BLUE Phase (Refactor and Clean Up):**
    - Verify LSP shows no type errors
    - Run linter: `ruff check {file_path}`
    - Check coverage: `pytest --cov={module} {test_file_path}`
    - Ensure docstrings follow project style
    
    **Context References:**
    {From artifact and codebase analysis}
    - Follow pattern from `{existing_file}`
    - Align with {architectural_decision}
    - Use error handling from `{error_handler_file}`
    
    **Completion Criteria:**
    {From artifact}
    - All tests pass
    - Code coverage >{percentage}%
    - No LSP/linting errors
    - Performance target: <{latency}ms
  status: "pending"
```

---

### 7. Example: Generating Specific YELLOW Instructions Using Explore Results

**Given artifact content:**
> "Implement rate limiting middleware using Redis, following the existing middleware pattern"

**Use explore sub-agent:**
```
Task: "Find middleware patterns, Redis usage, and test conventions in the codebase. Be very thorough."
```

**Explore sub-agent discovers:**
```
- src/middleware/base_middleware.py (middleware pattern)
- tests/test_auth_middleware.py (test conventions)
- config/redis_config.py (Redis connection pattern)
- src/utils/decorators.py (decorator patterns)
```

**Generated YELLOW phase:**
```yaml
**YELLOW Phase (Gather Context):**
- Read `src/middleware/base_middleware.py` to understand the BaseMiddleware class pattern
- Read `tests/test_auth_middleware.py` to see how middleware tests are structured
- Review `config/redis_config.py` for Redis connection and configuration patterns
- Check `src/utils/decorators.py` for decorator usage patterns in this project
- Review explore findings for any additional Redis usage patterns
- Note any integration patterns discovered by explore sub-agent
```

**This is SPECIFIC, not generic!**

---

### 8. Validate Extraction Completeness

**Before proceeding, verify:**

- [ ] Task name and description extracted
- [ ] All requirements captured
- [ ] Architecture decisions documented
- [ ] File paths identified
- [ ] Test specifications included
- [ ] Performance targets noted
- [ ] Phases logically structured
- [ ] Steps are discrete and actionable
- [ ] ALL instructions have specific YELLOW phases
- [ ] ALL instructions have RED/GREEN/BLUE phases
- [ ] Explore sub-agent analysis completed for context
- [ ] Specific file paths identified from explore results

---

### 9. Present Extraction Summary

Show user what was extracted:

```markdown
## 📊 Extraction Complete

### Task Overview:
- **Name:** {extracted_task_name}
- **Description:** {brief_excerpt}

### Phases Identified: {count}
{List each phase with step count}

### Total Scope:
- Phases: {count}
- Steps: {count}
- Instructions: {count}

### Explore Sub-Agent Analysis Results:
- Explore sessions launched: {count}
- Files identified for YELLOW phase: {count}
- Patterns discovered: {count}
- Integration points: {count}
- Code examples found: {count}

### Sample Instruction (Step 1.1.1):
{Show first instruction with specific YELLOW phase}

---

**Does this structure accurately represent the task?**

[c] Continue to YAML transformation (Step 3)
[m] Missing information - explain what's missing
[e] Edit/refine specific sections
[r] Re-extract with different structure
[x] Cancel workflow
```

---

### 10. Handle User Response

**If user selects 'c' (Continue):**
- Pass complete extracted structure to Step 3
- Load `{project-root}/docs/workflows/export-to-ralph/steps/step-03-transform.md`

**If user selects 'm' (Missing info):**
```markdown
**What information is missing?**

Please describe what's missing from the BMAD artifacts.

Common issues:
- Incomplete requirements
- Missing architecture decisions
- No test specifications
- Unclear implementation approach
- Missing performance targets

**Recommendation:** Go back and improve the BMAD artifacts (Brainstorming/Quick-Spec/PRD/etc.) before re-running export.

**Would you like to:**
[1] Exit workflow to improve artifacts
[2] Continue anyway (some instructions may be incomplete)
```

**If user selects [1]:** Exit gracefully, provide guidance on what to add to artifacts

**If user selects 'e' (Edit):**
- Ask which section to refine
- Allow manual adjustments
- Re-present summary

---

## DATA TO PASS TO STEP 3:

```yaml
task_plan_structure:
  metadata:
    version: "1.0.0"
    created_date: "{today YYYY-MM-DD}"
    last_updated: "{today YYYY-MM-DD}"
    author: "{from config or 'Tim'}"
    license: null  # or extracted from artifact
  
  task:
    name: "{extracted_task_name}"
    description: |
      {comprehensive_multi_line_description}
    status: "pending"
    phases:
      - id: "phase-1"
        name: "{extracted_phase_name}"
        description: |
          {phase_description}
        status: "pending"
        steps:
          - id: "step-1.1"
            name: "{step_name}"
            description: "{step_description}"
            status: "pending"
            instructions:
              - id: "instr-1.1.1"
                content: |
                  {complete_instruction_with_specific_YELLOW}
                status: "pending"

explore_analysis:
  sessions_launched: [{session_1_description}, {session_2_description}, ...]
  files_for_context: ["{file1}", "{file2}", ...]
  patterns_found: ["{pattern1}", "{pattern2}", ...]
  integration_points: ["{point1}", "{point2}", ...]
  code_examples: ["{example1}", "{example2}", ...]
```

---

## SUCCESS CRITERIA:

✅ All relevant data extracted from artifacts  
✅ Explore sub-agent used for codebase analysis  
✅ Specific file paths and patterns identified  
✅ Phases logically structured  
✅ Steps are discrete and actionable  
✅ ALL instructions have specific YELLOW-RED-GREEN-BLUE  
✅ No placeholder or incomplete content  
✅ User confirms completeness  

---

## NEXT STEP:

After user confirms extraction is complete, load and execute:

**`{project-root}/docs/workflows/export-to-ralph/steps/step-03-transform.md`**

Remember: Pass the complete task_plan_structure and explore_analysis to Step 3!
