---
description:
  Cross-file checklists for adding approval modes, sandbox managers, and
  modifying config or extension lifecycle
---

# Checklists

## Adding an approval mode

1. Add to `ApprovalMode` enum in `packages/core/src/policy/types.ts`.
2. Update `packages/core/src/routing/strategies/approvalModeStrategy.ts`.
3. Update `packages/core/src/policy/policy-engine.ts` if mode affects matching.
4. Add mode display in `packages/cli/` UI components.
5. Update CLI argument parsing if settable via flags.

## Adding a sandbox manager for a new platform

1. Create `packages/core/src/sandbox/${os}/` implementing `SandboxManager`
   from `packages/core/src/services/sandboxManager.ts`.
2. Update `packages/core/src/services/sandboxManagerFactory.ts` to detect OS.
3. Add denial detection utils to
   `packages/core/src/sandbox/utils/sandboxDenialUtils.ts` if needed.
4. Shell and write-file tools use the manager automatically if the interface
   is implemented correctly.

## Modifying extension lifecycle

- Serialize start/stop operations — never interleave.
- If extension has `excludeTools`, call `maybeRefreshGeminiTools()` after.
- Disconnect old MCP client explicitly before loading new config (hash
  mismatch won't auto-disconnect).
- Set correct `source` field on policy rules for proper cleanup.

## Modifying config or settings cascade

- Never modify `ConfigParameters` after passing to Config constructor.
- If adding a config field, update both the parameter type and the private
  field copy in the constructor.
- Memory path changes require updating all results in
  `discoverMemoryPaths()`: global, extension, project, userProjectMemory.
