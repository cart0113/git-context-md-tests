---
description:
  Cross-file checklists for adding tools and hook event types — which files
  must change together
---

# Checklists

## Adding a new tool

1. Create implementation in `packages/core/src/tools/` extending
   `BaseDeclarativeTool`.
2. Add tool name constant to `packages/core/src/tools/tool-names.ts`.
3. Export from `packages/core/src/tools/tools.ts`.
4. Add declaration to `packages/core/src/tools/definitions/coreTools.ts`.
5. If model-specific, add to the relevant set in
   `packages/core/src/tools/definitions/model-family-sets/`.
6. Register in `packages/core/src/config/config.ts` ToolRegistry initialization.
7. Add policy rules in `packages/core/src/policy/` if security-relevant.
8. If sandbox expansion detection needed, update
   `packages/core/src/sandbox/utils/proactivePermissions.ts`.

**Gotcha:** MCP tools bypass this pipeline — they're dynamically added via
`McpClientManager`.

## Adding a hook event type

1. Add event to `HookEventName` enum in `packages/core/src/hooks/types.ts`.
2. Add input/output interfaces in the same file.
3. Add `fire${EventName}Event()` method to
   `packages/core/src/hooks/hookSystem.ts`.
4. Map event name to handler in `packages/core/src/hooks/hookEventHandler.ts`.
5. Update `packages/core/src/hooks/hookPlanner.ts` for execution planning.
6. Call the fire method from the appropriate location (agent-session, scheduler,
   etc.).

**Gotcha:** BeforeTool hooks fire AFTER policy checks. If policy denies a tool,
the hook never fires.
