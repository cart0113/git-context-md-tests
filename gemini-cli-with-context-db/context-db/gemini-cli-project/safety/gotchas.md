---
description:
  Traps in safety checkers — fail-closed error handling, Conseca singleton state
  persistence, checker-policy ordering, and timeout asymmetry
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

## Timeout asymmetry between checker types

In-process checkers have a hardcoded 5s timeout (`checker-runner.ts`). External
checkers default to 30s, configurable via settings. External checker timeout
triggers SIGTERM then SIGKILL after 5s grace period.

## External checker process lifecycle has race conditions

Both `killed` and `exited` flags must be tracked to avoid double-resolution of
the result promise. The pattern in `checker-runner.ts` is delicate — modifying
process management requires careful handling of all exit paths.

See also: [Policy and hook gotchas](../policy-and-hooks/gotchas.md) for policy
priority math and tool matching rules that determine which checkers run.
