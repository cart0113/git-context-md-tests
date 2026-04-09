---
description: >-
  Hook system gotchas and event reference — stdout must be JSON-only, exit code
  semantics, event flow-control capabilities, union aggregation, tail calls,
  silent error swallowing, input mutation before validation, performance traps
---

# Hooks

## The #1 Gotcha: stdout Must Be JSON-Only

**stdout MUST contain ONLY the final JSON object.** Any stray `echo`, `print`,
or debug output on stdout silently breaks the hook — the JSON parser fails and
the CLI defaults to treating the entire output as a `systemMessage`.

All logging/debugging goes to **stderr** (`>&2` in bash, `console.error()` in
Node).

## Exit Codes

| Code  | Meaning           | Behavior                                                                                                  |
| ----- | ----------------- | --------------------------------------------------------------------------------------------------------- |
| 0     | Success           | stdout parsed as JSON. **All logic goes here** — including intentional denials via `{"decision": "deny"}` |
| 2     | System block      | Uses stderr as rejection reason. Blocks action but **turn continues** (agent can recover)                 |
| Other | Non-fatal warning | Interaction proceeds with original parameters                                                             |

For a hard stop, use `{"continue": false}` in JSON output with exit 0.

## Event Reference — Flow Control

| Event               | Can Block? | Key Gotcha                                                                                                      |
| ------------------- | ---------- | --------------------------------------------------------------------------------------------------------------- |
| SessionStart        | NO         | Advisory only. Flow control ignored. Can inject context.                                                        |
| BeforeAgent         | YES        | `decision: "deny"` removes from history; `continue: false` keeps it                                             |
| BeforeModel         | YES        | Can swap model, mock responses. Blocking without synthetic response = model never called AND no replacement.    |
| BeforeToolSelection | SPECIAL    | **Union aggregation** — multiple hooks' allowedFunctionNames combine. Only `mode: "NONE"` overrides.            |
| BeforeTool          | YES        | Can rewrite arguments. `decision: "deny"` blocks tool but agent continues                                       |
| AfterTool           | YES        | Can replace result or inject additionalContext (wrapped in `<hook_context>` XML tags). Supports **tail calls**. |
| AfterModel          | YES        | Fires **per chunk** during streaming. Expensive per-chunk ops tank performance.                                 |
| AfterAgent          | YES        | Can force retry with new prompt. `stop_hook_active` flag prevents infinite loops.                               |
| PreCompress         | NO         | Best-effort, async.                                                                                             |
| SessionEnd          | NO         | Non-blocking, best-effort. CLI doesn't wait.                                                                    |
| Notification        | NO         | Observability only.                                                                                             |

## Implementation Gotchas (from source code)

**All hook errors are silently swallowed.** `hookSystem.ts` catches all errors
and logs at DEBUG level only. A crashing hook doesn't block execution — it's as
if the hook doesn't exist. The only way to detect failures is debug logging.

**Duplicate failures are suppressed during streaming.** `hookEventHandler.ts`
uses a WeakMap keyed on the request object. If the same hook fails multiple
times for the same streaming request, only the first failure is reported.

**BeforeTool input mutation happens before validation.** In
`coreToolHookTriggers.ts`, `Object.assign(invocation.params, modifiedInput)`
runs first, then `tool.build()` validates. If validation fails, the params were
already mutated — the invocation object is in an inconsistent state (though the
error prevents tool execution).

**Modified tool inputs trigger a system notification.** If a hook modifies tool
args,
`[System] Tool input parameters (x, y) were modified by a hook before execution.`
is appended to the tool result. The LLM sees this.

**Hook results lose attribution.** `hookAggregator` merges multiple hook outputs
into one `finalOutput`. You cannot trace which hook contributed which field.

**`block` and `deny` are treated identically** in `types.ts` — both values exist
for semantic clarity but the code doesn't distinguish them.

**`transcript_path` can be empty.** If `hookSystem` fires before
`ChatRecordingService` is initialized, all hooks get an empty `transcript_path`.

**`toSerializableDetails()` is manual mapping.** New properties added to
`ToolCallConfirmationDetails` won't appear in hook inputs unless the serializer
in `hookSystem.ts` is explicitly updated.

## Matchers Use Different Strategies

- **Tool events** (BeforeTool, AfterTool): matchers are **regex patterns**
  (`"write_.*"`, `"write_file|replace"`)
- **Lifecycle events** (SessionStart, SessionEnd): matchers are **exact
  strings** (`"startup"`, `"exit"`, `"clear"`)
- `"*"` or `""` (empty) matches all, but matching type differs by event

## BeforeToolSelection Union Aggregation

The only event where multiple hook outputs merge instead of first-one-wins.
Multiple hooks' `allowedFunctionNames` lists are combined (union). Only
`mode: "NONE"` overrides this.

**Code detail:** `applyToolConfigModifications()` in `types.ts` always ensures
`tools` is an array (defaults to `[]` if undefined). A hook modifying
`toolConfig` doesn't automatically update the `tools` array it applies to.

## Tail Calls in AfterTool

`hookSpecificOutput.tailToolCallRequest` triggers another tool immediately after
the current one. The tail call's result **replaces** the original tool's
response. Only works in AfterTool — BeforeTool hooks cannot request tail calls.

## Performance

- Hooks run **synchronously** in the agent loop — slow hooks block the agent
- Prefer `AfterAgent` over `AfterModel` when you only need final validation
  (AfterModel fires per-chunk)
- Use specific matchers instead of `*` to avoid spawning processes for
  irrelevant events
- Cache expensive operations between invocations (e.g., hourly cache key)
- `ToolTiming` events are fire-and-forget — errors caught at debug level, never
  affect tool execution

## Security Model

- **Project hooks are untrusted by default.** Fingerprinted by name+command. If
  command changes (e.g., via `git pull`), re-warned as new untrusted hook.
- System/user hooks assumed safe. Extension hooks require explicit approval.
- Environment redaction OFF by default — enable for third-party hooks via
  `security.environmentVariableRedaction`

## Environment Variables Available to Hooks

`GEMINI_PROJECT_DIR`, `GEMINI_SESSION_ID`, `GEMINI_CWD`, `CLAUDE_PROJECT_DIR`
(compatibility alias). Sanitized — no standard process env vars unless
explicitly allowed.

**Code detail:** `SessionStartInput` passes `source` in the input object AND as
`trigger` in the hook context — different key names for the same value. The
planner uses `context.trigger` for matching.

## Hook Output Class Hierarchy

```
HookOutput (interface)
  └─ DefaultHookOutput (base implementation)
       ├─ BeforeToolHookOutput      → getModifiedToolInput()
       ├─ BeforeModelHookOutput     → applyLLMRequestModifications(), getSyntheticResponse()
       ├─ BeforeToolSelectionOutput  → applyToolConfigModifications()
       ├─ AfterModelHookOutput      → getModifiedResponse()
       └─ AfterAgentHookOutput      → shouldClearContext()
```

## Checklist: Adding a New Hook

1. Choose event type and matcher strategy (regex for tools, exact for lifecycle)
2. Write script — ALL output to stderr except final JSON to stdout
3. Test exit codes: 0 for all logic (including denials), 2 for emergency blocks
4. Register in settings.json at appropriate level (project/user/system)
5. If BeforeToolSelection — remember union aggregation with other hooks
6. If AfterModel — beware per-chunk firing, keep logic lightweight
7. If AfterAgent with retry — set `stop_hook_active` to prevent infinite loops
8. Test with debug logging enabled — hook errors are silent by default
9. If modifying tool inputs — know that params are mutated before validation

See also:

- [architecture.md](architecture.md) — monorepo package map, stable hook API
  contract and the lossy translator round-trip
- [configuration-and-policies.md](configuration-and-policies.md) — hook config
  hierarchy, env redaction patterns for third-party hooks, MCP server naming
  trap
- [tools-and-modes.md](tools-and-modes.md) — plan mode doesn't fire hooks on
  manual toggle, tool-level gotchas that interact with BeforeTool/AfterTool
  hooks
- [../context-db-tests-project/harness-defaults.md](../context-db-tests-project/harness-defaults.md)
  — test harness for evaluating hook implementations
