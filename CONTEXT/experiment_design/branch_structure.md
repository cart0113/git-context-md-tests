---
description: What differs between with-context-md and without-context-md branches — exact list of files added/removed
---

# Branch Structure

## `with-context-md` branch

Everything from main plus the full context-md setup per project:

- `CONTEXT.md` — top-level entry point pointing to CONTEXT/ folders
- `CONTEXT/` — hierarchical folder of context documents
- `CONTEXT/*_toc.md` — auto-generated TOC indexes at every level
- `CONTEXT/**/<folder>.md` — description-only files marking folder nodes
- `.claude/rules/context-md.md` — bootstrap rule telling Claude how to read TOCs
- `bin/build_toc.sh` — TOC generator script

## `without-context-md` branch

Same content documents but stripped of all context-md scaffolding:

- NO `CONTEXT.md` entry point
- NO `*_toc.md` files
- NO description-only folder marker files
- NO `.claude/rules/context-md.md` bootstrap rule
- NO `bin/build_toc.sh`

The actual context content (e.g., `dependency_injection/resolution_flow.md`) remains identical. The agent can still find and read these files via grep/glob, but has no guided discovery mechanism.
