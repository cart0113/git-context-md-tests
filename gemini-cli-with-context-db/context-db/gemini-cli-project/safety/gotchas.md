---
description:
  Traps in safety checkers — fail-closed error handling, Conseca singleton state
  persistence, checker-policy ordering, shared timeout with lifecycle asymmetry
---

# Safety Gotchas

## Fail-closed by design

Every error path in `checker-runner.ts` returns DENY — timeout, JSON parse
failure, process crash, context build failure. There is no fail-open path. This
is intentional but means a broken checker blocks ALL matching tools, not just
the unsafe ones.

## Conseca is a singleton with mutable state

`ConsecaSafetyChecker.getInstance()` returns a session-scoped singleton. Its
policy caches keyed by `activeUserPrompt` string. State persists across tool
calls. If the user prompt changes, policy regenerates via LLM call (hidden
latency). If the prompt is identical but conversation context changed, the
cached policy is reused without re-evaluation.

## Conseca context must be set during Config init

`ConsecaSafetyChecker.getInstance().setContext(this)` is called in the Config
constructor (`config.ts`). If this call is removed, Conseca silently falls back
to ALLOW — no boot-time validation that it's properly initialized.

## Safety checks run AFTER policy, not before

`policy-engine.ts` only runs checkers when `decision !== PolicyDecision.DENY`. A
DENY rule prevents all safety checkers from running. Checkers can only escalate
to ASK_USER or downgrade to DENY — they cannot override a non-DENY decision to
ALLOW.

## Checker timeout is shared, not per-type

Both in-process and external checkers share the same timeout from
`CheckerRunner`, configured at 30s in `config.ts:1286`. The `DEFAULT_TIMEOUT` of
5s in `checker-runner.ts` is a fallback never reached because `config.ts` always
provides 30s.

The real asymmetry is lifecycle: external checkers get a 5s SIGTERM→SIGKILL
grace period after timeout (`checker-runner.ts:189-194`). In-process checkers
have no grace period — the promise simply rejects.

## External checker process lifecycle has race conditions

Both `killed` and `exited` flags must be tracked to avoid double-resolution of
the result promise. The pattern in `checker-runner.ts` is delicate — modifying
process management requires careful handling of all exit paths.

## Sandbox expansion grants permissions dynamically

When a sandboxed tool fails due to permission restrictions (or is proactively
identified as needing extra permissions, like `npm install`), the CLI presents a
"Sandbox Expansion Request" to the user. If approved, the command re-runs with
extended permissions for that invocation only. The `state.updateArgs()` call
MUST happen BEFORE `resolveConfirmation()` inside the expansion path — see
[scheduler gotchas](../scheduler-gotchas.md).

## Windows sandbox integrity levels persist after session

The Windows Native sandbox uses `icacls` to set "Low Mandatory Level" on files.
These changes survive the session — files retain low integrity after the sandbox
ends. Manual reset with `icacls /setintegritylevel Medium` is required.

See also:

- [Policy and hook gotchas](../policy-and-hooks/gotchas.md) for policy priority
  math and tool matching rules that determine which checkers run.
- [checker-runner.ts](../../../packages/core/src/safety/checker-runner.ts) —
  fail-closed execution, timeout handling, process lifecycle.
- [built-in.ts](../../../packages/core/src/safety/built-in.ts) — in-process
  checker interface.
- [conseca/](../../../packages/core/src/safety/conseca/) — Conseca singleton
  implementation and tests.
- [Sandbox docs](../../../docs/cli/sandbox.md) — user-facing sandbox
  configuration guide.
