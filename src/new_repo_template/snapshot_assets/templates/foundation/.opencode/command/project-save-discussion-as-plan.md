---
description: "Save the current discussion from Plan Mode into the PLAN.md file."
---

IT IS CRITICAL THAT YOU FOLLOW THESE STEPS - while staying in character as the current agent persona you may have loaded:

<steps CRITICAL="TRUE">
1. Run the `date` command to get the current date and time in the format `YYYY-MM-DD HH:MM:SS AM/PM`.
2. Perform a YELLOW pass before editing anything:
   - Read and study the files that are relevant to the discussion and planned work.
   - At minimum, reread `PLAN.md`, `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, and `TODO-FEATURES.md` if it is relevant to the discussion.
   - Read the most recent file in `docs/session-summaries/` to understand the latest completed slice.
   - Run `btca status`.
   - If any part of the discussion depends on library, framework, tool, packaging, or CLI behavior, use `btca ask` with a plain/simple query string before finalizing the plan.
   - When reporting back to the user, explicitly mention that the YELLOW pass included file reads, `btca status`, and any `btca ask` usage.
3. Update our docs with our findings from this discussion. This includes:
   - PROGRESS.md
   - docs/LIVING_DOCS.md
   - docs/ARCHITECTURE.md
4. If applicable, update any relevant sections in `TODO-FEATURES.md`.
5. Write a new SESSION_SUMMARY in `docs/session-summaries/`.
   - NEVER overwrite an existing session summary.
   - Use the date/time from step 1.
6. Save the entire, comprehensive plan to the `PLAN.md` file. Before building, we are going to clear the context window and start fresh. Meaning, you will lose your memory of this conversation. Therefore,
   - the PLAN file must be extensive and complete enough that it can get us right back to this point, ready to execute and build, and
   - the PLAN file must have a fresh-context restart section that tells us exactly which files to read and study before resuming work, including `PLAN.md`, `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, `TODO-FEATURES.md` (if applicable), and the new most recent file in `docs/session-summaries/`, and
   - the PLAN file must include the locked decisions, explicit non-goals, the exact next execution steps, and any commands or validations needed to restart safely from a blank context window.
   - the PLAN must be saved in Markdown task list format, meaning that each executable part of the plan have a [ ] checkbox that can be updated.
7. Give a detailed report when complete.
</steps>
