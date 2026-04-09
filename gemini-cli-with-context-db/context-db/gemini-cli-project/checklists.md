---
description:
  Cross-file checklists for adding tools, hook events, approval modes, and
  sandbox managers
---

# Checklists

## Adding a new tool

1. Create implementation in `packages/core/src/tools/` extending
   `BaseDeclarativeTool`.
2. Add tool name constant to `packages/core/src/tools/tool-names.ts`.
3. Export from `packages/core/src/tools/tools.ts`.
4. Add tool declaration to `packages/core/src/tools/definitions/coreTools.ts`.
5. If model-specific, add to the relevant set in
   `packages/core/src/tools/definitions/model-family-sets/`.
6. Register in `packages/core/src/config/config.ts` ToolRegistry initialization.
7. Add policy rules in `packages/core/src/policy/` if security-relevant.
8. If the tool needs sandbox expansion detection, update
   `packages/core/src/sandbox/utils/proactivePermissions.ts`.

**Gotcha:** MCP tools bypass this pipeline — they're dynamically added via
`McpClientManager` and some lifecycle hooks may not fire for them.

## Adding a hook event type

1. Add event to `HookEventName` enum in `packages/core/src/hooks/types.ts`.
2. Add input/output interfaces in the same file.
3. Add `fire${EventName}Event()` method to
   `packages/core/src/hooks/hookSystem.ts`.
4. Map event name to handler in
   `packages/core/src/hooks/hookEventHandler.ts`.
5. Update `packages/core/src/hooks/hookPlanner.ts` for execution planning.
6. Call the fire method from the appropriate location (agent-session, scheduler,
   etc.).

## Adding an approval mode

1. Add to `ApprovalMode` enum in `packages/core/src/policy/types.ts`.
2. Update `packages/core/src/routing/strategies/approvalModeStrategy.ts`.
3. Update `packages/core/src/policy/policy-engine.ts` if mode affects rule
   matching.
4. Add mode display in `packages/cli/` UI components.
5. Update CLI argument parsing if mode is settable via flags.

## Adding a sandbox manager for a new platform

1. Create `packages/core/src/sandbox/${os}/` directory implementing
   `SandboxManager` interface from
   `packages/core/src/services/sandboxManager.ts`.
2. Update `packages/core/src/services/sandboxManagerFactory.ts` to detect OS
   and instantiate your manager.
3. Add denial detection utils to
   `packages/core/src/sandbox/utils/sandboxDenialUtils.ts` if needed.
4. Shell and write-file tools automatically use the sandbox manager — no tool
   changes needed if the interface is implemented correctly.
