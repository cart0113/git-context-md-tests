---
description:
  Non-obvious traps in tool scheduling, parallel execution, confirmation loops,
  state management, and prompt construction
---

# Scheduler Gotchas

## UPDATE_TOPIC is always sorted first in a batch

`UPDATE_TOPIC_TOOL_NAME` is forced to the front of every batch. If you reorder
requests bypassing `_startBatch()`, topic updates won't precede dependent tools
and the agent's context will be stale.

## Tools are parallelized by default

Contiguous parallelizable tools are dequeued together and run via
`Promise.all()`. If Tool A and Tool B both write to the same file, there's no
ordering guarantee unless `wait_for_previous: true` is set in tool args.

## Sandbox expansion is recursive

When sandbox expansion is needed, `_execute()` calls itself recursively.
`state.updateArgs()` MUST be called BEFORE `resolveConfirmation()` — if the
order is wrong, `resolveConfirmation()` fetches stale invocation from state.

## Batch lifecycle is ephemeral

`completedBatch` is intentionally cleared both at batch start and in the
finally block. Callers must consume `completedCalls` synchronously before the
next turn. Holding a reference after batch completion gives an empty array.

## State manager updates are fire-and-forget

`emitUpdate()` is not awaited — no backpressure on rapid status changes. UI
and internal state can diverge if a MessageBus listener is slow or fails.

## Confirmation loop rebuilds tool invocation

When users edit tool args via editor, the tool invocation is rebuilt with
`tool.build(modifiedInput)`. Edits are NOT validated until the next loop
iteration — if `build()` fails on invalid params, the user must start over.

## Tail call original request preservation

`originalRequestName` and `originalRequestArgs` are preserved through tail
calls. If NOT set on the first call, intermediate tool names leak to the LLM.

## System prompt snippets depend on model

`promptProvider` selects either `snippets` or `legacySnippets` based on
`supportsModernFeatures(model)`. A model downgrade silently changes the entire
prompt structure. Model changes mid-session require explicit prompt rebuild —
this is NOT automatic.

## MessageBus subscription is deduplicated globally

`Scheduler.subscribedMessageBuses` is a static WeakSet. Each messageBus gets
legacy listeners attached only ONCE across all Scheduler instances.
