---
name: context-db-manual
description:
  'How to use context-db, a markdown knowledge base containing all project
  context, standards, and knowledge.'
allowed-tools: Bash Read
---

## What context-db is

`context-db/` is a hierarchical Markdown knowledge base that lives in the
project repo. It contains big-picture architecture, design rationale, change
patterns, and non-obvious gotchas — things you can't easily derive from reading
the code alone.

Every `.md` file has YAML frontmatter with a `description` field. A script reads
those descriptions and generates a table of contents for any folder. You browse
the TOC, read only what's relevant, and move on.

## What context-db is NOT

Context-db is not a substitute for the code. It should never duplicate
information that's already readable in the source:

- **Don't** describe how functions work — the code is the spec
- **Don't** list function signatures or exact line numbers — they go stale
- **Don't** document what the code does step-by-step — read the code
- **Do** explain WHY decisions were made (not derivable from code)
- **Do** document cross-cutting patterns that span multiple files
- **Do** call out non-obvious gotchas and surprises
- **Do** provide a file map so agents know where to start looking

The goal is one source of truth: the code. Context-db provides the map and the
"why" — the code provides the "what" and "how". If an agent can get the story
by reading the code, don't repeat it in context-db.

**Context-db is a starting point, not the full picture.** Always corroborate
context-db knowledge against the actual source before implementing changes.

## How to read it

Run the TOC script on the root folder:

```
.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/
```

The output lists every subfolder and file with a one-line description. Subfolder
paths end with `/` — run the script on them to go deeper. Only open files whose
descriptions are relevant to your task.

**Do this at the start of every conversation.** Read topics relevant to the
user's request before writing code or making suggestions.

## How to write to it

Every `.md` file requires frontmatter:

```yaml
---
description: One-line summary shown in the TOC
---
```

Optional: `status: draft | stable | deprecated` (default: `stable`).

Two file types:

- **Documents** — frontmatter + body content.
- **Folder descriptions** (`<folder-name>.md`) — frontmatter only, no body.
  Registers the folder in the parent TOC.

Descriptions must be accurate, complete summaries — not titles. An agent must be
able to judge relevance without opening the file.

**When referencing code, point to file paths and function names** (e.g.,
"look at `solve_dependencies()` in `fastapi/dependencies/utils.py`"). This
gives agents a grep target. Don't include line numbers — they shift with every
edit.

### What belongs in context-db

- Architecture maps — which files own which concerns
- Design decisions — why things are the way they are
- Change patterns — how to make common types of modifications across files
- Gotchas — non-obvious behaviors that are correct but surprising
- Pointers — file paths and function names so agents know where to look

### What does NOT belong in context-db

- How functions work (read the code)
- Function signatures (read the code)
- Step-by-step flows that mirror the code (read the code)
- Line numbers (they go stale)
- Anything an agent can learn by reading the source file

### Where to put new content

The `<project-name>-project/` folder is for knowledge **specific to this
project** — architecture, data models, domain context, design decisions. When
writing about this project, put it here (or in a subfolder of it).

Folders parallel to `<project-name>-project/` (like `coding-standards/`,
`writing-standards/`) contain **project-agnostic** knowledge — standards and
conventions that apply across many projects. These are often symlinked from a
shared standards repo. You will rarely need to create or edit these folders. If
you do, only put content there that applies universally, not content specific to
the project you're working in.

## How to maintain it

**5–10 items per folder.** When a folder exceeds this, split into subfolders.
The tree is a decision tree — each level should halve the search space.

**Keep descriptions current.** After any change, rewrite every affected
`description` to match current content.

**Post-session checklist:**

1. Capture — create or update documents with new knowledge.
2. Summarize — rewrite affected descriptions.
3. Reorganize — split or merge folders to stay at 5–10 items.
4. Verify — run `context-db-generate-toc.sh` on affected folders.
