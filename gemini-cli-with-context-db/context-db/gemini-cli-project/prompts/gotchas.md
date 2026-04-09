---
description:
  Traps in prompt construction — snippet duplication, system.md override, tool
  filtering before prompts, approval mode branching, compression model
  divergence
---

# Prompt Construction Gotchas

## Two snippet files must stay in lockstep

`promptProvider.ts` selects `snippets.ts` (modern/Gemini 3.x) or
`snippets.legacy.ts` (older models) based on `supportsModernFeatures()`. Both
implement the same render functions but with different content. Changes to one
MUST be mirrored in the other or the prompt diverges silently when the model
changes.

## GEMINI_SYSTEM_MD overrides standard composition entirely

If the `GEMINI_SYSTEM_MD` env var is set, `promptProvider` reads a file and
bypasses the full snippet composition pipeline. The file gets variable
substitutions (`${AgentSkills}`, `${SubAgents}`, tool names) but NOT the typed
`SystemPromptOptions` structure. A custom system.md can go stale if it
references removed sections, and there is no validation.

## Tool filtering happens BEFORE prompt construction

`toolRegistry.getAllToolNames()` filters tools based on config and approval mode
before the prompt is built. The filtered list is what the prompt sees. Changes
to filtering logic in `tool-registry.ts` silently change what tools appear in
the prompt — verify both sides when modifying either.

Notable filter: `ENTER_PLAN_MODE_TOOL_NAME` is removed when already in plan
mode. `EXIT_PLAN_MODE_TOOL_NAME` is removed when NOT in plan mode.

## Approval mode switches the entire workflow section

Plan mode renders `renderPlanningWorkflow()`. All other modes render
`renderPrimaryWorkflows()`. These are mutually exclusive — plan mode does NOT
include primary workflows. Each has its own tool availability checks. Modifying
one workflow section does not affect the other.

## Compression prompt may use a different model path

`getCompressionPrompt()` also selects snippets by model, but if the compression
model differs from the main model (e.g., during fallback), snippet selection may
be inconsistent. Verify model alignment when modifying compression in
`chatCompressionService.ts`.

## Prompt sections can be disabled via environment variables

`GEMINI_PROMPT_<SECTION>=false` disables individual prompt sections. Disabled
sections return empty strings — no error. This can silently remove critical
instructions if an env var is set unexpectedly.

See also: [Scheduler gotchas](../scheduler-gotchas.md) — "system prompt changes
silently on model downgrade" is the trigger for snippet switching.
