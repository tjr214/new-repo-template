## Table of Contents

- [Table of Contents](#table-of-contents)
- [1. CRITICAL LEVEL INSTRUCTIONS](#1-critical-level-instructions)

## 1. CRITICAL LEVEL INSTRUCTIONS

**CRITICAL**:

- _DO NOT use lazy placeholders._ Output the FULL code block required for the search/replace.

- When implementing, _ALWAYS use a TDD RED-GREEN-REFACTOR loop._ Ensure this is properly reflected in all Plans made and executed.

- **ALWAYS** be updating the Living Documentation (`docs/LIVING_DOCS.md`) as we complete implementation sections. Ensure this is included in all Plans made and executed. This also includes updating the `PROGRESS.md` tracker in the project root and the `docs/ARCHITECTURE.md` document, as well. All the docs must be kept up-to-date and in-sync at all times.

- IMPORTANT: NEVER OVERWRITE A `SESSION_X_SUMMARY.md` file. _Always create a new session summary!_

- All of our unit and integration tests are to be stored in the `tests/` directory in the project root.

- **DOUBLE CRITICAL**: You have to READ files before the system will allow you to edit, update or write to them.

- **TRIPLE CRITICAL**: Do NOT add the user's personal information to the code, tests, documentation or anything else. Any of that personal information is only for use in conversation and dialogue with the user.

- **IMPORTANT**: Python projects use Python 3.14+, and `uv` and `pyproject.toml` for project management. All dev dependencies should be specified in the `dev` dependency group. Use `hatchling` as the build backend. When adding libraries to the project, look up their latest version and use that version number for the pin with the `>=` operator. When implementing concurrency use Python 3.14+'s `concurrent.interpreters` to achieve _true multi-core parallelism._
