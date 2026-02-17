# Step 4: Write Task File and Finalize Export

## MANDATORY EXECUTION RULES (READ FIRST):

- 📝 **WRITE FILE**: Save validated YAML to docs/tasks/
- ✅ **VERIFY SUCCESS**: Confirm file was written correctly
- 🔒 **PRESERVE BMAD SOURCES**: Never delete/archive epic and story artifacts during export
- 🎉 **COMPLETE**: Confirm workflow success

---

## CONTEXT FROM STEP 3:

You should have:

```yaml
final_yaml_content: |
  {complete_yaml_string}

file_metadata:
  task_name: "{task_name}"
  filename: "{sanitized_task_name}.yaml"
  output_path: "docs/tasks/{sanitized_task_name}.yaml"
  total_lines: { count }

loaded_artifacts: # From Step 1
  - name: "..."
    path: "..."
```

---

## YOUR TASK:

Write the validated YAML task file, verify success, and confirm that BMAD epic/story artifacts remain unchanged.

---

## EXECUTION SEQUENCE:

### 1. Prepare Output Directory

Ensure the tasks directory exists:

```bash
# Create directory if it doesn't exist
mkdir -p docs/tasks

# Verify directory exists
ls -ld docs/tasks
```

---

### 2. Generate Final Filename

Sanitize task name for filename:

```bash
# Example: "Build REST API Rate Limiter" → "build-rest-api-rate-limiter.yaml"
TASK_NAME="{task_name from metadata}"
FILENAME=$(echo "$TASK_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')
FILEPATH="docs/tasks/${FILENAME}.yaml"
```

**Verify filename:**

- Lowercase only
- Spaces replaced with hyphens
- Special characters removed
- Extension: .yaml

---

### 3. Write YAML File

Write the validated YAML content:

```bash
# Write to file
cat > "$FILEPATH" << 'EOF'
{final_yaml_content}
EOF

# Verify file was written
if [ -f "$FILEPATH" ]; then
  echo "✅ File written successfully"
  wc -l "$FILEPATH"
else
  echo "❌ Error: File not created"
  exit 1
fi
```

---

### 4. Verify File Integrity

Check that the file was written correctly:

```bash
# Check file size
FILE_SIZE=$(wc -c < "$FILEPATH")
echo "File size: $FILE_SIZE bytes"

# Check line count
LINE_COUNT=$(wc -l < "$FILEPATH")
echo "Line count: $LINE_COUNT"

# Verify YAML syntax (basic check)
head -5 "$FILEPATH"
tail -5 "$FILEPATH"
```

---

### 5. Run Final Validation

Validate the written file one more time:

```bash
# Run validation script on the written file
.template_scripts/validate_template.py "$FILEPATH"
```

**Expected:** Exit code 0 (valid)

**If validation fails:**

```markdown
❌ **Error: Written file failed validation!**

This shouldn't happen if Step 3 validation passed.

**Possible causes:**

- Encoding issues during file write
- YAML content corruption
- File system issues

**Recommendation:** Review the file manually and fix errors.

**File location:** {filepath}
```

---

### 6. Present Success Message

````markdown
## ✅ Task File Created Successfully!

**File:** `{filepath}`
**Size:** {line_count} lines ({file_size} bytes)
**Status:** ✅ Validated and ready for RALPH

### Task Summary:

- **Name:** {task_name}
- **Phases:** {phase_count}
- **Steps:** {step_count}
- **Instructions:** {instruction_count}

### Next Steps:

RALPH can now execute this task plan using:

```bash
./scripts/RALPH.sh docs/tasks/{filename}.yaml
```
````

---

### 7. Preserve BMAD Artifacts

Do not modify, delete, move, or archive any BMAD epic/story artifacts.

Confirm preservation explicitly:

```markdown
✅ **BMAD Source Artifacts Preserved**

The export workflow does not perform cleanup.
Epic and story source files remain in place for BMAD tracking and future updates.

Preserved artifacts:
{list loaded artifact paths}
```

---

### 8. Final Summary

````markdown
---

## 🎉 Export to RALPH Complete!

### ✅ Task Plan Created:

- **File:** `docs/tasks/{filename}.yaml`
- **Validated:** ✅ Schema compliant
- **Status:** Ready for RALPH implementation

### 📊 Task Details:

- **Name:** {task_name}
- **Phases:** {count}
- **Steps:** {count}
- **Instructions:** {count}
- **Estimated complexity:** {calculated from instruction count}

### 🔒 Artifact Handling:

- **Action taken:** preserved (no cleanup)
- **Files affected:** 0

### 🚀 Next Steps:

1. **Execute with the Ralph Loop:**
   ```bash
   ./scripts/RALPH.sh docs/tasks/{filename}.yaml
   ```

2. **Track progress:**
    - RALPH.sh will update status fields as work progresses
    - Completed tasks are moved to `docs/tasks/completed/` by the script

---

**Workflow complete!** 🧙
````

---

## SUCCESS CRITERIA:

✅ YAML file written to docs/tasks/
✅ File validates against schema
✅ User informed of success
✅ BMAD artifacts preserved unchanged
✅ Final summary provided
✅ Clear next steps given

---

## FAILURE MODES TO AVOID:

❌ File not written correctly
❌ Validation fails on written file
❌ Deleting or archiving BMAD epic/story artifacts
❌ Missing final summary

---

## WORKFLOW COMPLETE:

After presenting the final summary, the Export to RALPH workflow is complete!

The user now has a comprehensive, validated task plan ready for RALPH to execute.

🎉 **Well done!** 🧙

```

```
