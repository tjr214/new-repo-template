## Table of Contents

- [Table of Contents](#table-of-contents)
- [1. CRITICAL LEVEL INSTRUCTIONS](#1-critical-level-instructions)
  - [1.1 CRITICAL PYTHON INSTRUCTIONS](#11-critical-python-instructions)
  - [1.2 CRITICAL TYPESCRIPT INSTRUCTIONS](#12-critical-typescript-instructions)

## 1. CRITICAL LEVEL INSTRUCTIONS

**CRITICAL**:

- _DO NOT use lazy placeholders._ Output the FULL code block required for the search/replace.

- **SUPREMELY CRITICAL TDD INSTRUCTIONS FOR IMPLEMENTATION MODE**: When implementing, _ALWAYS use a special TDD loop we call YELLOW-RED-GREEN-BLUE._ Ensure this is properly reflected in all Plans made and executed. During the YELLOW Phase: search the codebase and read all the files necessary to understand the task at hand. RED, GREEN and BLUE (refactor) Phases remain the same as in a normal TDD loop. The YELLOW phase is to prime you with all the necessary context to correctly do the work.

- **ALWAYS** be updating the Living Documentation (`docs/LIVING_DOCS.md`) as we complete implementation sections. Ensure this is included in all Plans made and executed. This also includes updating the `PROGRESS.md` tracker in the project root and the `docs/ARCHITECTURE.md` document, as well. All the docs must be kept up-to-date and in-sync at all times.

- IMPORTANT: NEVER OVERWRITE A `SESSION_X_SUMMARY.md` file. _Always create a new session summary!_

- All of our unit and integration tests are to be stored in the `tests/` directory in the project root.

- **DOUBLE CRITICAL**: You have to READ files before the system will allow you to edit, update or write to them.

- **TRIPLE CRITICAL**: Do NOT add the user's personal information to the code, tests, documentation or anything else. Any of that personal information is only for use in conversation and dialogue with the user. Only the files and directories in the project directory are backed up and protected by Git. Therefore, in order to access, write, delete, modify, or do ANYTHING with files/directories OUTSIDE the project you must first get EXPLICIT PERMISSION from the user before proceeding. Otherwise, you may cause irreversible damage to the user's system without even realizing you have done anything at all!

### 1.1 CRITICAL PYTHON INSTRUCTIONS

- **IMPORTANT**: Python projects use Python 3.14+, and `uv` and `pyproject.toml` for project management. All dev dependencies should be specified in the `dev` dependency group. Use `hatchling` as the build backend. When adding libraries to the project, look up their latest version and use that version number for the pin with the `>=` operator. Do NOT use `uv pip install` to install packages as this will not update the `pyproject.toml`. When implementing concurrency use Python 3.14+'s `concurrent.interpreters` to achieve _true multi-core parallelism._

### 1.2 CRITICAL TYPESCRIPT INSTRUCTIONS

- **IMPORTANT**: TypeScript projects use `bun` for package management. When adding libraries to the project, look up their latest version and use that version number for the pin with the `^` operator. **NEVER use the `any` type** - always use proper type definitions, generics, or `unknown` with type guards when the type is truly unknown. Prefer strict type safety and leverage TypeScript's type system fully. Use `interface` for object shapes and `type` for unions, intersections, and complex type compositions.
