# Step 1: Detect Context and Identify BMAD Artifacts

## MANDATORY EXECUTION RULES (READ FIRST):

- 🔍 **DETECTIVE WORK**: Scan the project for BMAD epic and story artifacts
- 📊 **REPORT FINDINGS**: Present what was found to the user
- 🚫 **NO ASSUMPTIONS**: Only report what actually exists
- ⏸️ **WAIT FOR CONFIRMATION**: User must confirm which epic to export

---

## YOUR TASK:

Scan the project for BMAD epics and stories and present findings to the user. This identifies which epic should be exported into a single RALPH task YAML.

---

## EXECUTION SEQUENCE:

### 1. Scan for Epic and Story Artifacts

Search for implementation-planning artifacts in these locations:

**Check for epic files (primary path):**

```bash
find _bmad-output/planning-artifacts -name "*epic*.md" 2>/dev/null
```

**Check for epic files (legacy fallback path):**

```bash
find _bmad-output/planning -name "*epic*.md" 2>/dev/null
```

**Check for story files:**

```bash
find _bmad-output/implementation-artifacts -name "*.md" 2>/dev/null
```

**Check for sprint status (optional context):**

```bash
find _bmad-output/implementation-artifacts -name "sprint-status.yaml" 2>/dev/null
```

---

### 2. Analyze Findings and Group by Epic

For each artifact found, extract key information:

- **File name** and **path**
- **Last modified date** (use `ls -lh` or `stat`)
- **Brief summary** (read first 50 lines, extract title/description)
- **Epic/story identifiers**:
  - Epic from headings like `## Epic 2` or filename hints
  - Story keys like `2-1-story-name.md`
- **Grouping**: map each discovered story to its epic number

---

### 3. Present Findings to User

Report what was found in a structured format:

```markdown
## 🔍 BMAD Epic/Story Artifacts Detected

### Epics:

- [x] Found: epics-platform-foundation.md
  - Path: \_bmad-output/planning-artifacts/epics-platform-foundation.md
  - Last modified: [timestamp]
  - Epics detected in file: [count/list]

### Stories:

- [x] Found story files in \_bmad-output/implementation-artifacts/
  - Total stories: [count]
  - Grouped by epic:
    - Epic 1: [count]
    - Epic 2: [count]

### Sprint Status:

- [x] sprint-status.yaml found (optional context)
- [ ] sprint-status.yaml not found

---

## 📋 Summary

Found **[N]** relevant artifacts total:

- Epic files: [count]
- Story files: [count]
- Sprint status file: [found/not found]
```

---

### 4. Ask User Which Epic to Export

Present a menu for the user to select a single epic for export:

```markdown
**Which epic should be exported to a RALPH task plan?**

Select ONE:

[1] Epic 1 - {epic_title_1} ({story_count_1} stories)
[2] Epic 2 - {epic_title_2} ({story_count_2} stories)
[3] Epic 3 - {epic_title_3} ({story_count_3} stories)
[a] Export all epics as separate YAML files
[x] Cancel workflow

**Enter selection** (e.g., "2" or "a"):
```

---

### 5. Load Selected Epic and Related Stories

Based on user selection, load:

- The selected epic section/file
- All related story files for that epic (matching story prefix like `{epic_num}-*.md`)
- `sprint-status.yaml` if available (for status context only)

Use the Read tool to load full contents and store in memory for Step 2.

**Important rules:**

- One YAML output should represent one epic and all its stories
- Do not load unrelated epics unless user selected `a`
- Preserve source BMAD artifacts unchanged

---

### 6. Confirm Context Loaded

```markdown
✅ **Context Loaded Successfully**

Loaded artifacts:

- [Epic]: {epic_file_or_section_summary}
- [Stories]: {story_count} files loaded for epic {epic_num}
- [Sprint Status]: {loaded_or_not_found}

This context will be used to generate a RALPH task plan for the selected epic in Step 2.

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
    type: "epic|story|sprint-status"
    path: "{full_path}"
    key_sections:
      epic_number: "{extracted_epic_number}"
      epic_title: "{extracted_epic_title}"
      story_keys: ["{story1_key}", "{story2_key}"]
      acceptance_criteria: ["{criteria1}", "{criteria2}"]
      dependencies: ["{dependency1}", "{dependency2}"]
```

---

## SUCCESS CRITERIA:

✅ Epic and story artifact directories scanned  
✅ Found artifacts presented to user clearly  
✅ User selects epic scope to export  
✅ Selected epic and its stories loaded into memory  
✅ Context prepared for Step 2 extraction  
✅ User confirms ready to continue

---

## FAILURE MODES TO AVOID:

❌ Not checking if \_bmad-output directory exists  
❌ Assuming artifacts exist without verifying  
❌ Loading unrelated epics without user confirmation  
❌ Missing key sections during extraction  
❌ Not passing context to Step 2

---

## NEXT STEP:

After user confirms readiness, load and execute:

**`{project-root}/docs/workflows/export-to-ralph/steps/step-02-extract.md`**

Remember: Pass the loaded artifact context to Step 2!
