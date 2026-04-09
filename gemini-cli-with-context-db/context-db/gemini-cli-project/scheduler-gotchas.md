---
description:
  Traps when modifying the scheduler — tool ordering invariant, parallel
  execution default, sandbox recursion, and prompt model dependency
---

# Scheduler Gotchas

## UPDATE_TOPIC is always sorted first in a batch

Forced to front of every batch. Any code that reorders tool requests must
preserve this invariant or subsequent tools get stale context.

## Tools are parallelized by default

Contiguous parallelizable tools run via `Promise.all()`. Tools writing the same
file can race. Set `wait_for_previous: true` in tool args to serialize.

## Sandbox expansion calls \_execute() recursively

`state.updateArgs()` MUST be called BEFORE `resolveConfirmation()` inside the
expansion path. Wrong order = stale invocation fetched from state.

## System prompt changes silently on model downgrade

`promptProvider` selects `snippets` or `legacySnippets` based on model. Flash
fallback silently changes the entire prompt structure with no rebuild.

See also:

- [Prompt construction gotchas](prompts/gotchas.md) for snippet duplication
  traps.
- [scheduler.ts](../../packages/core/src/scheduler/scheduler.ts) — tool
  ordering, batch execution, sandbox expansion implementation.
