---
description:
  Cross-file checklists for modifying prompt snippets, adding config options,
  and changing tool filtering
---

# Checklists

## Changing snippet content

1. Update the function in `packages/core/src/prompts/snippets.ts`.
2. Update the corresponding function in
   `packages/core/src/prompts/snippets.legacy.ts`.
3. Verify `SystemPromptOptions` interface is compatible in both files.
4. Test with both modern and legacy models (`supportsModernFeatures`
   true/false).

## Adding a config option that affects prompts

1. Add to `AgentLoopContext` or `Config` interface.
2. Read it in `PromptProvider.getCoreSystemPrompt()`.
3. Add corresponding `SystemPromptOptions` field.
4. Add render function in BOTH `snippets.ts` and `snippets.legacy.ts`.
5. If section should be toggleable, add `isSectionEnabled()` check with
   `GEMINI_PROMPT_<SECTION>` env var support.

## Modifying tool filtering logic

1. Check `tool-registry.ts` `getAllToolNames()` / `isToolActive()` to understand
   what reaches the prompt.
2. Update prompt content if tool availability assumptions change.
3. Verify both plan mode and non-plan mode handle the tool correctly.
4. Plan mode has its own tool list — check `planModeToolsList` construction.

## Modifying memory/context rendering

1. `getAllGeminiMdFilenames()` is called at prompt generation time (not cached).
2. Memory can be `string` or `HierarchicalMemory` — rendering differs: string
   wraps in "Contextual Instructions", hierarchical uses `<global_context>` /
   `<extension_context>` tags.
3. Test both memory formats.
