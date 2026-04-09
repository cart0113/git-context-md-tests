---
description: Cross-file checklists for adding tools and hook event types
---

# Checklists

## Adding a new tool

1. Create in `packages/core/src/tools/` extending `BaseDeclarativeTool`.
2. Add name to `packages/core/src/tools/tool-names.ts`.
3. Export from `packages/core/src/tools/tools.ts`.
4. Add declaration to `packages/core/src/tools/definitions/coreTools.ts`.
5. If model-specific, add to `model-family-sets/`.
6. Register in `packages/core/src/config/config.ts` ToolRegistry init.
7. Add policy rules in `packages/core/src/policy/` if security-relevant.
8. If sandbox expansion needed, update `sandbox/utils/proactivePermissions.ts`.

MCP tools bypass this — they load via `McpClientManager`.

See also:

- [tool-names.ts](../../../packages/core/src/tools/tool-names.ts) — canonical
  tool name constants and legacy aliases.
- [coreTools.ts](../../../packages/core/src/tools/definitions/coreTools.ts) —
  tool declarations.

## Adding a hook event type

1. Add to `HookEventName` enum in `packages/core/src/hooks/types.ts`.
2. Add input/output interfaces in same file.
3. Add fire method to `packages/core/src/hooks/hookSystem.ts`.
4. Map event in `packages/core/src/hooks/hookEventHandler.ts`.
5. `hookPlanner.ts` is generic — usually needs no changes.
6. Call the fire method from the right place. Tool execution hooks fire from
   `packages/core/src/core/coreToolHookTriggers.ts`. Policy-related hooks fire
   from the scheduler's policy check path in
   `packages/core/src/scheduler/scheduler.ts`. Check where similar hooks fire
   and follow the pattern.

BeforeTool hooks fire AFTER policy. Denied tools never trigger hooks.

See also:

- [hooks/types.ts](../../../packages/core/src/hooks/types.ts) — `HookEventName`
  enum and input/output interfaces.
- [coreToolHookTriggers.ts](../../../packages/core/src/core/coreToolHookTriggers.ts)
  — where tool execution hooks fire from.
