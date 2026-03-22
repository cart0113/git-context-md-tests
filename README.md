# context-md Tests

Experiments testing whether structured context (TOC-based progressive disclosure) improves LLM coding agent performance compared to raw codebase access.

## Hypothesis

A hierarchical `CONTEXT/` folder with auto-generated TOC indexes helps LLM agents:
- Find relevant information faster (fewer tool calls)
- Produce more accurate answers (especially for architectural questions)
- Use fewer tokens overall
- Surface non-obvious context that grep/RAG wouldn't find

Secondary hypothesis: the benefit is larger for smaller/weaker models.

## Projects

Each subdirectory is a copy of an open-source project (`.git` removed) used as a test subject.

| Project | LOC | Language | Status |
|---------|-----|----------|--------|
| `fast-api-project/` | ~19K | Python | Ready |

## Branches

- **`with-context-md`** — CONTEXT/ folder with human-written docs, TOC indexes, bootstrap rule, and top-level CONTEXT.md entry point.
- **`without-context-md`** — Same markdown content files but no TOCs, no bootstrap rule, no CONTEXT.md entry point. Raw docs only.

## Test Design

Compare the two branches using the same prompts. Each prompt asks the agent to make a code change that requires architectural understanding.

### Test Tasks

Questions that require understanding beyond what grep can provide:
- Architectural reasoning ("how would you add X?")
- Bug diagnosis ("there's a bug in Y — diagnose and fix")
- Impact analysis ("what would break if we changed Z?")
- Refactoring with constraints ("refactor X without breaking the API contract")

### Metrics

- Token usage
- Number of tool calls / file reads before substantive answer
- Answer accuracy (manual evaluation)
- Time to first useful response
- Whether the agent discovers non-obvious context unprompted

## Setup

Projects are plain source copies — no git history, no virtual environments. The experiment tests context discovery, not build/run capability.
