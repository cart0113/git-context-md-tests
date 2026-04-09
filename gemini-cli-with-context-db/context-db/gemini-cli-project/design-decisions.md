---
description:
  Why things are the way they are — hooks as external processes, runtime tool
  registry, tool-level sandboxing, subagent completion via tools
---

# Design Decisions

## Why hooks are external processes, not imported modules

Hooks communicate via JSON over stdio, not as imported TypeScript. This allows
hooks in any language, decouples hook lifecycle from CLI memory, and sandboxes
failures — a crashed hook doesn't crash the CLI, a buggy hook can't access
private state. The tradeoff is process spawn overhead and the "Golden Rule"
requirement for clean stdout.

## Why tool registry is dynamic, not a static map

Tools are registered at runtime and can be mutated. This enables MCP tools to be
discovered lazily as servers connect, extension tools to load conditionally, and
tools to be disabled via policy. A static map would require compile-time
knowledge of all tools, blocking extensibility.

## Why sandboxing is per-tool, not per-process

Rather than sandboxing the entire CLI process, individual tool executions
(shell, file write) are wrapped. This keeps UI rendering and config loading
fast. It also lets users toggle sandbox mode without restarting. Full-process
sandboxing was rejected because it would sandbox the React UI, breaking it in
container environments.

## Why subagents return via complete_task tool

Subagents signal completion through the `complete_task` tool instead of direct
return values. This lets subagent output be captured by hooks, logged, and
subjected to policy, like any other tool call. It also enables pause/resume
without breaking the abstraction. Direct returns would bypass the scheduler and
hook system.

## Why confirmation is separate from hooks

Confirmations (user approval) and hooks (interception points) are distinct
systems. Hooks can't block tools — only policies can. Confirmations fire even
for allowed tools if they're mutators. This separation keeps policies as the
security boundary while hooks remain advisory. Conflating them would make the
security model fragile.

## Why policy uses stable stringify for argument matching

Policy converts tool arguments to a stable JSON string for regex matching, not
JavaScript's default `JSON.stringify`. Stable stringify ensures consistent key
ordering across runs, so regex patterns are predictable. Without this, the same
rule could match on one run but not another.

## Why extension policies load at tier 2

Default = tier 1, Extension = tier 2, Workspace = tier 3, User = tier 4, Admin =
tier 5. Extensions override defaults but not workspace or user preferences. This
five-tier hierarchy acknowledges that extensions are more specific than
built-ins, workspace project config overrides extensions, explicit user
configuration overrides workspace, and admin policies override everything.

See also:

- [Hooks overview docs](../../docs/hooks/index.md) — user-facing hook concepts.
- [Extension authoring docs](../../docs/extensions/index.md) — user-facing
  extension architecture.
- [Policy engine docs](../../docs/reference/policy-engine.md) — user-facing
  policy reference including tier system.
