---
description:
  Non-obvious traps in tool scheduling, parallel execution, confirmation loops,
  state management, and prompt construction
---

# Scheduler Gotchas

## UPDATE_TOPIC is always sorted first in a batch

Forced to front of every batch. Reordering requests that bypass _startBatch()
causes stale context for subsequent tools.

## Tools are parallelized by default

Contiguous parallelizable tools run via Promise.all(). No ordering guarantee
unless wait_for_previous: true is set. Tools writing the same file can race.

## Sandbox expansion is recursive

_execute() calls itself. state.updateArgs() MUST be called BEFORE
resolveConfirmation() — wrong order means stale invocation in state.

## Batch lifecycle is ephemeral

completedBatch is cleared at batch start AND in the finally block. Consume
completedCalls synchronously before next turn.

## State manager updates are fire-and-forget

emitUpdate() is not awaited. UI and internal state can diverge if MessageBus
listener is slow.

## Confirmation loop rebuilds tool invocation

User edits via editor rebuild with tool.build(modifiedInput). Edits are NOT
validated until next loop iteration.

## Tail call preserves original request name

originalRequestName must be set on FIRST call. If not set, intermediate tool
names leak to the LLM.

## System prompt snippets depend on model

promptProvider selects snippets or legacySnippets based on model. Model
downgrade silently changes prompt structure. Not automatic — requires explicit
rebuild.

## Section guards can silently disable features

withSection() checks GEMINI_SECTION_* env vars. Disabled sections vanish from
system prompt with no warning. Hard to debug if you do not know about it.

## MessageBus subscription is deduplicated globally

Scheduler.subscribedMessageBuses is a static WeakSet. Each bus gets listeners
once across all instances.
