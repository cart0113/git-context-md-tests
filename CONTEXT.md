# context-md Tests — Project Context

This repo tests whether context-md's TOC-based progressive disclosure improves LLM coding agent performance compared to raw markdown files.

## Reading Context

This project uses context-md to organize background knowledge in `CONTEXT/`.

Read `CONTEXT/CONTEXT_toc.md` to start. Each entry has a description and a path. Use descriptions to decide relevance — skip what you don't need.

- If the path ends in `_toc.md`, it's a subfolder — read that TOC and repeat.
- Otherwise, read the document.

## Projects

Each subdirectory under the repo root is a test project (a copy of an open-source codebase). To run a test, open Claude Code in the project subdirectory on the appropriate branch.

- **fast-api-project/** — FastAPI (~19K LOC Python). Has its own `CONTEXT.md` on the `with-context-md` branch.

## Branches

- `with-context-md` — Full context-md setup: CONTEXT/ with TOCs, top-level CONTEXT.md entry point
- `without-context-md` — Same content markdown files, but no TOCs, no CONTEXT.md entry point
