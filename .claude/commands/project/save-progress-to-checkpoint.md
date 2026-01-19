---
description: "Save current session's work and create a resumption checkpoint for fresh context windows"
---

Let's save all progress from the current work session and create documentation that allows seamless resumption in a fresh, empty context window.

## Purpose

When working on a long-running project across multiple context windows, this command:

1. Commits all code changes to git
2. Updates project documentation with current status
3. Creates a detailed session summary for resumption
4. Verifies all tests pass before saving
5. Provides clear instructions for next session

## When to Use This Command

- **End of work session**: Before closing the current context window
- **Major milestone reached**: After completing a significant feature/sprint task
- **Before context switch**: When moving to a different part of the codebase
- **Regular checkpoints**: Every 2-3 hours of active development
- **Before asking for multi-session work**: To establish a known-good state

## Execution Steps

### Step 1: Check Current Git Status

```bash
git status
git diff --stat
git log --oneline -5
```

**Purpose**: Understand what has changed since the last commit.

---

### Step 2: Identify Current Sprint/Phase

Determine:

- Which sprint/phase are we in?
- What percentage complete?
- What tasks were accomplished this session?
- What's next?

**Read these files**:

- `PROGRESS.md` - Current sprint status
- `docs/LIVING_DOCS.md` - Architecture overview
- Previous `docs/SESSION_X_SUMMARY.md` - Last checkpoint

---

### Step 3: Update PROGRESS.md

**Location**: `{project-root}/PROGRESS.md`

**Updates to make**:

1. **Header section** - Update date and status:

```markdown
**Last Updated**: [Current Date]
**Current Phase**: Phase X Implementation - Sprint Y [Status]
**Overall Status**: 🔄 [Sprint Name] [Percentage]% Complete
```

2. **Quick Status Overview table** - Update progress percentage:

```markdown
| **Phase 3: Implementation** | 🔄 In Progress | ~XX% |
```

3. **Current Sprint section** - Mark completed tasks:

```markdown
### 🔄 Sprint X: [Name] (IN PROGRESS - XX%)

- [x] Completed task 1 (details)
- [x] Completed task 2 (details)
- [ ] Next task - NEXT
- [ ] Remaining task 1
```

4. **Testing Status section**:

```markdown
**Current Status**: ✅ All Tests Passing
```

Tests: XX passed, X skipped
Coverage: ~XX%

```

```

5. **Milestones section** - Add current date entry:

```markdown
- ✅ **YYYY-MM-DD**: [Previous milestone]
- 🔄 **YYYY-MM-DD**: [Current sprint] started (XX% complete)
```

6. **Footer status**:

```markdown
**Status**: 🔄 **SPRINT X IN PROGRESS (XX%)**

_Last Context Window: Session X - [Sprint Name]_
```

---

### Step 4: Create Session Summary Document

**Location**: `{project-root}/docs/SESSION_X_SUMMARY.md`

Where X = current session number (increment from last session).

**Template**:

```markdown
# Session X Summary - [Sprint Name] [Status]

**Date**: [Current Date]
**Session**: [Sprint Name] (XX% Complete)
**Status**: 🔄 **IN PROGRESS** (or ✅ **COMPLETE**)

---

## ✅ What We Accomplished

### 1. **[Feature/Component Name]** - [Status]

- ✅ [Detail 1]
- ✅ [Detail 2]
- ✅ X passing tests
- ✅ XX% test coverage

**Files Created:**

- `path/to/file1.py`
- `path/to/file2.py`

### 2. **[Feature/Component Name]** - [Status]

- ✅ [Detail 1]
- ✅ [Detail 2]

**Files Created:**

- `path/to/file3.py`

### 3. **[Additional Items]**

- ✅ [Detail]

---

## 📊 Test Status
```

Tests: XX passed, X skipped (up from YY)
Coverage: XX% (up from YY%)
New Tests Added: XX
Sprint X Progress: ~XX%

```

---

## 🎯 Next Steps (Resume Here)

### **Immediate Next Task**: [Task Name]
[Detailed description of next task]

Steps:
1. 🔴 RED: [Write failing test]
2. 🟢 GREEN: [Implement feature]
3. 🔵 REFACTOR: [Polish]
4. [Integration step]

### **Remaining Sprint X Tasks**:
- [ ] [Next task] - NEXT
- [ ] [Remaining task 1]
- [ ] [Remaining task 2]
- [ ] [Update documentation]

---

## 🏗️ Architecture Progress

### What's Built:
```

project/
├── module/
│ ├── file1.py ✅ Complete (XX% coverage)
│ └── file2.py ✅ Complete (XX% coverage)

```

### What's Next:
```

project/
├── module/
│ ├── submodule/ 🔜 Next up
│ └── widgets/ 🔜 After that

````

---

## 📝 Key Design Decisions

1. **[Decision 1]**: [Rationale]
2. **[Decision 2]**: [Rationale]
3. **[Decision 3]**: [Rationale]

---

## 🚀 How to Resume

### 1. Verify Environment (Python Example Given; if using Typescript, etc. adjust accordingly)
```bash
cd /path/to/project
uv sync --all-extras  # or npm install, etc.
uv run pytest -v      # or npm test, etc.
````

### 2. Review Documentation

- `PROGRESS.md` - Current sprint status
- `docs/LIVING_DOCS.md` - The project's living and ever-updating documentation
- `docs/ARCHITECTURE.md` - Project Architecture overview
- `docs/SESSION_X_SUMMARY.md` - This file

### 3. Continue with [Next Task]

Ask assistant:

```
"Let's continue Sprint X. [Specific next action]."
```

---

## 📁 Files Modified/Created This Session

### New Files:

- `path/to/new/file1.py`
- `path/to/new/file2.py`
- `docs/SESSION_X_SUMMARY.md` (this file)

### Modified Files:

- `PROGRESS.md` (updated sprint X status)
- `docs/LIVING_DOCS.md` (updated implementation status)
- `path/to/modified/file.py` (added feature Y)

---

## 🎓 What We Learned

1. **[Learning 1]**: [Insight]
2. **[Learning 2]**: [Insight]
3. **[Learning 3]**: [Insight]

---

## 🏆 Milestones

- ✅ [Milestone 1]
- ✅ [Milestone 2]
- ✅ Coverage increased to XX%

---

**Session Status**: ✅ **SAVED & READY TO RESUME**
**Next Session**: Continue Sprint X - [Next Task]
**Maintainer**: [Your Name]
**Assistant**: BMad Master 🧙

---

_Sprint X is XX% complete. Resume anytime with fresh context!_

````

---

### Step 5: Update Living Documentation

**Location**: `{project-root}/docs/LIVING_DOCS.md`

**Updates to make**:

1. **Header section**:
```markdown
**Last Updated**: YYYY-MM-DD
**Status**: Sprint X [Name] In Progress 🔄 (XX%)
````

2. **Implementation Status section** - Update sprint progress:

```markdown
#### Sprint X: [Name] (IN PROGRESS - XX%)

- [x] Completed task (X tests, XX% coverage)
- [x] Completed task (X tests, XX% coverage)
- [ ] Next task - NEXT
- [ ] Remaining task
```

---

### Step 6: Run Full Test Suite

**Purpose**: Verify everything works before committing.

```bash
uv run pytest -v --tb=short
```

**Check**:

- ✅ All tests pass (or document intentional skips)
- ✅ No new failures
- ✅ Coverage maintains or improves

---

### Step 7: Stage and Commit Changes

```bash
# Stage all changes
git add -A

# Review what will be committed
git status
git diff --cached --stat

# Create descriptive commit message
git commit -m "feat: [Sprint X] [High-level summary]

- [Component 1]: [What was added/changed]
  - [Detail 1]
  - [Detail 2]
  - X passing tests, XX% coverage

- [Component 2]: [What was added/changed]
  - [Detail 1]
  - [Detail 2]
  - X passing tests, XX% coverage

- Update documentation
  - PROGRESS.md: Sprint X status (XX% complete)
  - LIVING_DOCS.md: Updated implementation status
  - SESSION_X_SUMMARY.md: Session checkpoint for resume

Tests: XX passing, X skipped
Coverage: XX% (up from YY%)
Sprint X Progress: XX%"
```

**Commit message structure**:

- **Type**: feat, fix, docs, refactor, test, chore
- **Scope**: Sprint number and high-level summary
- **Body**: Bulleted list of changes with details
- **Footer**: Test/coverage statistics and sprint progress

---

### Step 8: Verify Commit

```bash
# Show recent commits
git log --oneline -3

# Verify latest commit details
git show --stat
```

---

### Step 9: Final Verification

Run tests one more time to ensure commit is clean:

```bash
uv run pytest -v --tb=short | tail -20
```

---

## Output Format

After executing this command, provide the user with:

### 1. **Checkpoint Summary**

```
✅ SPRINT X PROGRESS SAVED SUCCESSFULLY

Git Commit: [hash] - [commit message first line]

Files Saved:
- ✅ [file1] (XXX lines)
- ✅ [file2] (XXX lines)
- ✅ docs/SESSION_X_SUMMARY.md (complete resume guide)

Test Status:
✅ XX tests passing
✅ X skipped
✅ XX% coverage
✅ All green
```

### 2. **Resume Instructions**

```
HOW TO RESUME IN FRESH CONTEXT

When you start a new session, simply say:

"Let's resume Sprint X. I want to continue with [next task]."

Or:

"Review the current status of Sprint X"

I'll read:
1. PROGRESS.md - Current sprint status
2. docs/SESSION_X_SUMMARY.md - Detailed checkpoint
3. docs/LIVING_DOCS.md - Architecture overview

And we'll pick up exactly where we left off!
```

### 3. **Continuation Options**

```
NEXT STEPS:

A) Continue now with [next task]
B) Close this session and resume fresh
C) [Other relevant option]

What's your preference?
```

---

## Success Criteria

This command is successful when:

- ✅ All code changes are committed to git
- ✅ PROGRESS.md accurately reflects current state
- ✅ SESSION_X_SUMMARY.md provides complete resumption guide
- ✅ LIVING_DOCS.md is up to date
- ✅ All tests pass
- ✅ Next steps are clearly documented
- ✅ User can resume from fresh context without losing context

---

## Example Execution

**User says**:

> "Save our progress so we can resume Sprint 3 from a fresh context window."

**Assistant executes**:

1. Checks git status
2. Updates PROGRESS.md (Sprint 3 at 30%)
3. Creates docs/SESSION_3_SUMMARY.md
4. Updates docs/LIVING_DOCS.md
5. Stages all changes
6. Commits with detailed message
7. Verifies tests (91 passing)
8. Provides resume instructions

**Result**: User can close this session and resume Sprint 3 in fresh context by reading the checkpoint documents.

---

## Notes

- **Be thorough**: Better to over-document than under-document
- **Be specific**: Include file paths, test counts, coverage percentages
- **Be actionable**: Next steps should be crystal clear
- **Be honest**: Document what's NOT done as clearly as what IS done
- **Follow TDD**: Always verify tests before committing

---

**Command Status**: Ready to use
**Maintainer**: Tim
**Last Updated**: 2026-01-18
