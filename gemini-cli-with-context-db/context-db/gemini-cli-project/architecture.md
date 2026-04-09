---
description:
  High-level architecture — cli/core split, tool execution flow order, model
  routing strategy stack, and approval mode hierarchy
---

# Architecture

`packages/cli` is the React/Ink UI. `packages/core` is the backend — API calls,
tool execution, policy, hooks, sandboxing. They communicate through config
objects and message buses. Other packages (`sdk`, `a2a-server`, `devtools`,
`vscode-ide-companion`) are secondary.

## Tool execution flow

The order matters and is a common source of confusion:

```
Model returns tool call
  → Policy engine decides allow/deny/ask_user
  → Safety checkers run (only if policy did not DENY)
  → BeforeTool hook fires (only if policy allowed)
  → Confirmation bus (even allowed tools, if they're mutators)
  → Sandbox wraps execution (if enabled)
  → Tool runs
  → AfterTool hook fires
```

**Hooks cannot override policy.** If policy denies a tool, the BeforeTool hook
never fires. Confirmation is separate from both — an allowed tool can still
require user confirmation. Safety checkers run between policy and hooks — see
[safety gotchas](safety/gotchas.md).

See also: [Policy and hook gotchas](policy-and-hooks/gotchas.md) for detailed
traps at each step. [Scheduler gotchas](scheduler-gotchas.md) for tool ordering
and parallel execution traps.

## Model routing strategy stack

Strategies evaluated in precedence order — first match wins (see
`modelRouterService.ts` `initializeDefaultStrategy()`):

1. Fallback (rate limit fallback — silent, session-scoped).
2. Override (user explicitly set a model via flag, env var, or settings).
3. Approval mode (plan/default/autoEdit/yolo).
4. Gemma classifier (if enabled via config).
5. Generic classifier (keyword-based).
6. Numerical classifier (threshold-based).
7. Default.

Model is locked in before the scheduler sees the tool call. Changing approval
mode mid-loop doesn't re-route already-dispatched calls.

## Approval mode hierarchy

Unidirectional: `plan` → `default` → `autoEdit` → `yolo`. An approval granted in
`plan` flows to all modes. An approval in `default` flows only to `autoEdit` and
`yolo`, NOT back to `plan`.
