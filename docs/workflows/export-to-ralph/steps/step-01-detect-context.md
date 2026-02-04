# Step 1: Detect Context and Identify BMAD Artifacts

## MANDATORY EXECUTION RULES (READ FIRST):

- 🔍 **DETECTIVE WORK**: Scan the project for BMAD planning artifacts
- 📊 **REPORT FINDINGS**: Present what was found to the user
- 🚫 **NO ASSUMPTIONS**: Only report what actually exists
- ⏸️ **WAIT FOR CONFIRMATION**: User must confirm which artifacts to use

---

## YOUR TASK:

Scan the project for BMAD planning artifacts and present findings to the user. This gives context about what planning work has already been done.

---

## EXECUTION SEQUENCE:

### 1. Scan for BMAD Artifacts

Search for planning artifacts in these locations:

**Check for brainstorming sessions:**
```bash
find _bmad-output/analysis -name "brainstorming-session-*.md" 2>/dev/null | head -10
```

**Check for quick-spec tech-specs:**
```bash
find _bmad-output/implementation -name "tech-spec-*.md" 2>/dev/null | head -10
```

**Check for product briefs:**
```bash
find _bmad-output/planning -name "product-brief.md" 2>/dev/null
```

**Check for PRDs:**
```bash
find _bmad-output/planning -name "prd.md" 2>/dev/null
```

**Check for architecture docs:**
```bash
find _bmad-output/planning -name "architecture.md" 2>/dev/null
```

**Check for epics and stories:**
```bash
find _bmad-output/planning -name "epics-*.md" 2>/dev/null | head -10
```

---

### 2. Analyze Findings

For each artifact found, extract key information:

- **File name** and **path**
- **Last modified date** (use `ls -lh` or `stat`)
- **Brief summary** (read first 50 lines, extract title/description)
- **Relevant sections** (requirements, features, decisions)

---

### 3. Present Findings to User

Report what was found in a structured format:

```markdown
## 🔍 BMAD Artifacts Detected

### Brainstorming Sessions:
- [X] Found: brainstorming-session-2026-02-03.md
  - Topic: [extracted topic]
  - Date: 2026-02-03
  - Ideas generated: [count if available]
  
### Quick-Spec Documents:
- [X] Found: tech-spec-logging-feature.md
  - Feature: [extracted feature name]
  - Date: 2026-02-02
  - Status: [extracted status]

### Product Requirements:
- [ ] Product Brief: Not found
- [X] PRD: prd.md (Last updated: 2026-01-28)
- [X] Architecture: architecture.md (Last updated: 2026-01-29)

### Epics & Stories:
- [X] Found: epics-sprint-1.md, epics-sprint-2.md
  - Total epics: [count]
  
---

## 📋 Summary

Found **[N]** planning artifacts total:
- Brainstorming: [count]
- Specs: [count]
- Planning docs: [count]
- Epics: [count]
```

---

### 4. Ask User Which Artifacts to Use

Present a menu for the user to select:

```markdown
**Which planning artifacts should inform the task plan?**

Select all that apply (you can choose multiple):

[1] Brainstorming session: {name} (Most recent ideation)
[2] Quick-Spec: {name} (Implementation spec)
[3] Product Brief (High-level vision)
[4] PRD (Detailed requirements)
[5] Architecture Doc (Technical decisions)
[6] Epics & Stories (User stories and acceptance criteria)
[7] None - I'll provide details directly during extraction
[8] All of the above

**Enter selections** (comma-separated, e.g., "2,4,5" or "8" for all):
```

---

### 5. Load Selected Artifacts

Based on user selection, read the chosen artifact files:

- Use the Read tool to load full contents
- Extract relevant sections (requirements, features, decisions, test criteria)
- Store in memory for use in Step 2 (Extract & Analyze)

**Example extraction:**

From Quick-Spec:
- Task name/feature name
- Requirements and acceptance criteria
- File paths mentioned
- Test specifications
- Performance targets

From PRD:
- Feature descriptions
- Success criteria
- Constraints

From Architecture:
- Technical decisions
- Patterns to follow
- Integration points

---

### 6. Confirm Context Loaded

```markdown
✅ **Context Loaded Successfully**

Loaded artifacts:
- [Artifact 1]: {summary}
- [Artifact 2]: {summary}
- [Artifact 3]: {summary}

This context will be used to pre-fill task plan details in Step 2.

**Ready to proceed to extraction?**
[c] Continue to Step 2
[r] Re-scan for different artifacts
[x] Cancel workflow
```

---

### 7. Handle User Selection

**If user selects 'c' (Continue):**
- Load and execute `{project-root}/docs/workflows/export-to-ralph/steps/step-02-extract.md`
- Pass loaded artifact context to Step 2

**If user selects 'r' (Re-scan):**
- Re-execute Step 1 from the beginning
- Allow different artifact selection

**If user selects 'x' (Cancel):**
- Exit workflow gracefully
- Confirm cancellation with user

---

## CONTEXT TO PASS TO STEP 2:

When loading Step 2, ensure these are in memory:

```yaml
loaded_artifacts:
  - name: "{artifact_name}"
    type: "brainstorming|quick-spec|prd|architecture|epics"
    path: "{full_path}"
    key_sections:
      task_name: "{extracted_name}"
      description: "{extracted_description}"
      requirements: ["{req1}", "{req2}"]
      technical_decisions: ["{decision1}", "{decision2}"]
      file_paths: ["{path1}", "{path2}"]
      test_criteria: ["{criteria1}", "{criteria2}"]
      performance_targets: ["{target1}", "{target2}"]
```

---

## SUCCESS CRITERIA:

✅ All BMAD artifact directories scanned  
✅ Found artifacts presented to user clearly  
✅ User selects which artifacts to use  
✅ Selected artifacts loaded into memory  
✅ Context prepared for Step 2 extraction  
✅ User confirms ready to continue  

---

## FAILURE MODES TO AVOID:

❌ Not checking if _bmad-output directory exists  
❌ Assuming artifacts exist without verifying  
❌ Loading all artifacts without user confirmation  
❌ Missing key sections during extraction  
❌ Not passing context to Step 2  

---

## NEXT STEP:

After user confirms readiness, load and execute:

**`{project-root}/docs/workflows/export-to-ralph/steps/step-02-extract.md`**

Remember: Pass the loaded artifact context to Step 2!
