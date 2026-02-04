# Step 4: Write Task File and Cleanup Artifacts

## MANDATORY EXECUTION RULES (READ FIRST):

- 📝 **WRITE FILE**: Save validated YAML to docs/tasks/
- ✅ **VERIFY SUCCESS**: Confirm file was written correctly
- 🧹 **CLEANUP ARTIFACTS**: Offer to delete/archive used BMAD artifacts
- 🔒 **SAFETY CHECK**: Verify artifacts aren't needed by BMAD workflows
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

Write the validated YAML task file, verify success, and offer to cleanup BMAD artifacts that were used to generate the task.

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

### 7. Check BMAD Workflow Dependencies

Before offering cleanup, check if any BMAD workflows reference the artifacts:

```bash
# Search BMAD workflows for references to artifacts
cd _bmad
for artifact_path in {loaded_artifact_paths}; do
  artifact_name=$(basename "$artifact_path")
  echo "Checking for references to: $artifact_name"

  # Search workflow files
  rg -l "$artifact_name" . 2>/dev/null || echo "No references found"
done
cd ..
```

**Safety determination:**

- ✅ **SAFE TO DELETE** if no references found
- ⚠️ **CAUTION** if references exist (show which workflows reference them)

---

### 8. Offer Artifact Cleanup

```markdown
---

## 🧹 Cleanup BMAD Artifacts

The following artifacts were used to generate this task plan:

{For each artifact:}

- 📄 `{artifact_path}`
  - Type: {artifact_type}
  - Size: {file_size}
  - Last modified: {mod_date}
  - References: {workflow_references or "None found"}

### Cleanup Options:

**[d] Delete all artifacts**

- Permanently remove the files listed above
- Safe because task plan now contains all information
- Cleanup status: {SAFE or CAUTION}

**[a] Archive artifacts**

- Move to `_bmad-output/archive/{date}/`
- Preserves artifacts for future reference
- Recommended if workflows reference them

**[k] Keep artifacts**

- Leave files as-is
- Good for manual review/verification

**[s] Selective cleanup**

- Choose which artifacts to delete/archive

**[x] Skip cleanup**

- Don't modify any artifacts

**Your choice:**
```

---

### 9. Handle Cleanup Selection

#### **If user selects 'd' (Delete):**

**If CAUTION status:**

```markdown
⚠️ **Warning: Some workflows may reference these artifacts!**

References found:

- {workflow_1} references {artifact_name}
- {workflow_2} references {artifact_name}

**Are you sure you want to delete?**
[y] Yes, delete anyway
[n] No, choose different option
```

**If user confirms or SAFE status:**

```bash
# Delete artifacts
for artifact_path in {loaded_artifact_paths}; do
  echo "Deleting: $artifact_path"
  rm "$artifact_path"

  if [ ! -f "$artifact_path" ]; then
    echo "✅ Deleted successfully"
  else
    echo "❌ Failed to delete: $artifact_path"
  fi
done
```

```markdown
✅ **Artifacts deleted successfully**

Removed {count} files totaling {total_size}

The task plan in `docs/tasks/{filename}.yaml` contains all the information from these artifacts.
```

---

#### **If user selects 'a' (Archive):**

```bash
# Create archive directory with timestamp
ARCHIVE_DIR="_bmad-output/archive/$(date +%Y-%m-%d-%H%M%S)"
mkdir -p "$ARCHIVE_DIR"

# Move artifacts to archive
for artifact_path in {loaded_artifact_paths}; do
  echo "Archiving: $artifact_path"
  mv "$artifact_path" "$ARCHIVE_DIR/"

  if [ -f "$ARCHIVE_DIR/$(basename $artifact_path)" ]; then
    echo "✅ Archived successfully"
  else
    echo "❌ Failed to archive: $artifact_path"
  fi
done

# Create archive manifest
cat > "$ARCHIVE_DIR/MANIFEST.md" << EOF
# BMAD Artifacts Archive

**Date:** $(date)
**Task:** {task_name}
**Task File:** docs/tasks/{filename}.yaml

## Archived Files:

{list each artifact with metadata}

## Reason:
These artifacts were used to generate the task plan. They have been archived for reference but are no longer needed for implementation.
EOF
```

```markdown
✅ **Artifacts archived successfully**

**Archive location:** `{archive_dir}/`

Contains:
{list archived files}

A manifest file has been created documenting the archive.
```

---

#### **If user selects 'k' (Keep):**

```markdown
✅ **Artifacts preserved**

BMAD artifacts will remain in their current locations:
{list artifact paths}

You can manually review or cleanup later.
```

---

#### **If user selects 's' (Selective):**

```markdown
**Select artifacts to delete or archive:**

{For each artifact:}
[{index}] `{artifact_path}`
Type: {type}, Size: {size}
References: {count}
[d] Delete [a] Archive [k] Keep

**Enter selections** (e.g., "1d 2a 3k" or "all-d"):
```

Process user selections individually.

---

#### **If user selects 'x' (Skip):**

```markdown
✅ **Cleanup skipped**

All BMAD artifacts remain unchanged.
```

---

### 10. Final Summary

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

### 🧹 Artifact Cleanup:

- **Action taken:** {deleted/archived/kept/selective}
- **Files affected:** {count}

### 🚀 Next Steps:

2. **Execute with the Ralph Loop:**
   ```bash
   ./scripts/RALPH.sh docs/tasks/{filename}.yaml
   ```
````

3. **Track progress:**
   - RALPH.sh will update status fields as work progresses
   - Completed tasks are moved to `docs/tasks/completed/` by the script

---

**Workflow complete!** 🧙

```

---

## SUCCESS CRITERIA:

✅ YAML file written to docs/tasks/
✅ File validates against schema
✅ User informed of success
✅ Cleanup options presented
✅ User's cleanup choice executed
✅ Final summary provided
✅ Clear next steps given

---

## FAILURE MODES TO AVOID:

❌ File not written correctly
❌ Validation fails on written file
❌ Deleting artifacts without user confirmation
❌ Not checking workflow dependencies before deletion
❌ Missing final summary

---

## WORKFLOW COMPLETE:

After presenting the final summary, the Export to RALPH workflow is complete!

The user now has a comprehensive, validated task plan ready for RALPH to execute.

🎉 **Well done!** 🧙
```
