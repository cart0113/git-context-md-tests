---
description:
  Why things are the way they are — hooks as processes, dynamic tool registry,
  per-tool sandboxing, subagent completion, confirmation vs hooks, policy tiers,
  parallel-by-default tools, section guards for A/B testing
---

# Design Decisions

## Why hooks are external processes, not imported modules

Hooks communicate via JSON over stdio. This allows hooks in any language,
decouples hook lifecycle from CLI memory, and sandboxes failures — a crashed
hook doesn't crash the CLI, a buggy hook can't access private state. Tradeoff:
process spawn overhead and the "Golden Rule" requirement for clean stdout.

## Why tool registry is dynamic, not a static map

Tools are registered at runtime and can be mutated. MCP tools are discovered
lazily as servers connect, extension tools load conditionally, and tools can be
disabled via policy. A static map would require compile-time knowledge of all
tools.

## Why sandboxing is per-tool, not per-process

Individual tool executions (shell, file write) are wrapped rather than the
entire CLI process. This keeps UI rendering and config loading fast and lets
users toggle sandbox mode without restarting. Full-process sandboxing was
rejected because it would sandbox the React UI.

## Why subagents return via complete_task tool

Subagent output goes through `complete_task` so it can be captured by hooks,
logged, and subjected to policy like any other tool call. Direct returns would
bypass the scheduler and hook system.

## Why confirmation is separate from hooks

Hooks can't block tools — only policies can. Confirmations fire even for
allowed tools if they're mutators. Conflating them would make the security
model fragile: policies are the security boundary, hooks are advisory.

## Why policy uses stable stringify for argument matching

Tool arguments are converted to stable JSON (consistent key ordering) for
regex matching. Without this, the same policy rule could match on one run but
not another due to object key ordering differences.

## Why extension policies are tier 2

Built-in = tier 1, Extension = tier 2, User = tier 3, Admin = tier 4.
Extensions override defaults but not user preferences.

## Why system prompt uses section guards

`withSection()` checks `GEMINI_SECTION_*` environment variables. Entire feature
sections can be toggled for A/B testing. No warning when disabled — by design
for clean experiments, but hard to debug if you don't know about it.

## Why tools are parallelized by default

The scheduler runs contiguous parallelizable tools via `Promise.all()`. Tools
must opt out with `wait_for_previous: true`. Optimizes throughput but means
tools with shared state can race unless they declare serial execution.
