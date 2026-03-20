---
description: "Load recent history and show the details."
---

Where did we last leave off?

IT IS CRITICAL THAT YOU FOLLOW THESE STEPS - while staying in character as the current agent persona you may have loaded:

<steps CRITICAL="TRUE">
1. Perform a YELLOW read pass before answering:
   - Read `PLAN.md` if it exists and is relevant.
   - Read `PROGRESS.md`, `docs/LIVING_DOCS.md`, and `docs/ARCHITECTURE.md`.
   - Read the most recent file in `docs/session-summaries/`.
   - If the current work is feature- or milestone-driven, also read and account for `TODO-FEATURES.md`.
2. Give a clear status report of where we last left off.
   - Identify the latest completed slice.
   - Identify the current active plan or next planned slice.
   - If applicable, explain how much of the plan has been completed so far and how much is left.
   - If applicable, give overall progress in terms of items (or checkboxes) completed/remaining and in terms of milestones completed/remaining.
   - If `TODO-FEATURES.md` is relevant, explicitly include it in your progress calculation and call out the current feature, completed features, and remaining features.
   - Call out any known blockers, open decisions, or prerequisites before work can resume.
3. If the plan/milestone structure makes it useful, the output can look similar to this:

```
- Overall PLAN checkboxes: X / Y complete
- Overall remaining: Z
- Overall completion: PERCENTAGE.0%

Milestone-only view (M0-M5) is even clearer for implementation progress:

- Milestone items complete: X / Y
- Milestone items remaining: Z
- Milestone completion: PERCENTAGE.0%

Current milestone status:

- M0: 12/13 (92.3%)
- M1: 35/35 (100% done)
- M2: 16/18 (88.9%)
- M3: 0/12
- M4: 0/17
- M5: 0/10

So we've fully finished M1, are close to finishing M2, and most remaining work is concentrated in M3-M5.
```

4. ALWAYS end by asking the user exactly one targeted question: whether they want you to prime the context window and continue the work now.
   - Do NOT automatically start priming/executing just because you were asked for status.
   - If the user says yes, immediately perform the priming/loading protocol and then continue the work without asking another permission question.
   - If the user says no, stop after the status report.
5. The priming/loading protocol means:
   - Re-read `PLAN.md`, `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, `TODO-FEATURES.md` if applicable, and the latest `docs/session-summaries/` file.
   - Re-read any additional implementation files and tests explicitly referenced by the active plan.
   - Run `btca status`.
   - Use `btca ask` with plain/simple query strings for any dependency, library, framework, packaging, or CLI behavior that affects the active work.
   - Then begin the actual work using the YELLOW-RED-GREEN-BLUE loop until the work is complete or you hit a real blocker.
</steps>
