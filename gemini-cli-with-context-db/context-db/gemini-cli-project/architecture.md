---
description:
  High-level architecture — cli/core split, tool execution flow order
  (hook-first), model routing strategy stack, approval mode hierarchy with plan
  mode isolation, and plan mode auto-routing and non-interactive behavior
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
  → BeforeTool hook fires (can modify args or error out)
  → Policy engine decides allow/deny/ask_user
    └─ Safety checkers run inside policy (only if not DENY)
  → Confirmation bus (if ASK_USER, even for allowed mutators)
  → Sandbox wraps execution (if enabled)
  → Tool runs
  → AfterTool hook fires
```

**Hooks fire BEFORE policy, not after.** If a hook errors, the tool is rejected
without policy ever running (`scheduler.ts:588-616`). Hooks can modify tool args
but cannot override a policy decision — policy runs second and has final say.
Safety checkers execute inside `PolicyEngine.check()` (`policy-engine.ts:684`),
not as a separate step. Confirmation is separate from both — an allowed tool can
still require user confirmation.

See also:

- [Policy and hook gotchas](policy-and-hooks/gotchas.md) for detailed traps at
  each step.
- [Scheduler gotchas](scheduler-gotchas.md) for tool ordering and parallel
  execution traps.
- [scheduler.ts](../../packages/core/src/scheduler/scheduler.ts) — tool
  execution flow implementation.
- [modelRouterService.ts](../../packages/core/src/routing/modelRouterService.ts)
  — strategy stack implementation.

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

**Plan mode triggers automatic routing.** When using an auto model, plan mode
routes to Pro (high-reasoning) during the planning phase. On exit, if an
approved plan exists, the CLI switches to Flash (high-speed) for implementation.
This is configurable via `general.plan.modelRouting` in settings.json.

## Approval mode hierarchy

Unidirectional: `plan` → `default` → `autoEdit` → `yolo`. An approval granted in
`plan` flows to all modes. An approval in `default` flows only to `autoEdit` and
`yolo`, NOT back to `plan`.

**Plan mode is intentionally isolated from other approvals.** Tools approved in
default/autoEdit modes do NOT become approved in plan mode. This preserves plan
mode as a safe research environment. Conversely, tools approved in plan mode are
treated as intentional global trust and apply everywhere.

**Non-interactive plan mode switches to YOLO on exit.** In headless/CI
environments, the policy engine auto-approves `enter_plan_mode` and
`exit_plan_mode` without user confirmation. On exit, the CLI switches to YOLO
(not default) so implementation proceeds without hanging on approvals.

**Hooks on plan mode transitions only fire for agent-initiated switches.** Using
`/plan` command or `Shift+Tab` does NOT trigger BeforeTool/AfterTool hooks on
`enter_plan_mode`/`exit_plan_mode`. Only agent-initiated transitions (e.g.,
asking "start a plan for...") fire hooks.

See also:

- [Plan mode docs](../../docs/cli/plan-mode.md) — user-facing plan mode guide.
