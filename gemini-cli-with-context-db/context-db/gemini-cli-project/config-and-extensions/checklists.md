---
description:
  Cross-file checklists for approval modes, sandbox managers, and config changes
---

# Checklists

## Adding an approval mode

1. Add to ApprovalMode enum in packages/core/src/policy/types.ts.
2. Update packages/core/src/routing/strategies/approvalModeStrategy.ts.
3. Update packages/core/src/policy/policy-engine.ts if mode affects matching.
4. Add display in packages/cli/ UI components.
5. Update CLI argument parsing if settable via flags.

## Adding a sandbox manager

1. Create packages/core/src/sandbox/\${os}/ implementing SandboxManager.
2. Update packages/core/src/services/sandboxManagerFactory.ts.
3. Add denial utils to sandbox/utils/sandboxDenialUtils.ts if needed.
4. Shell and write-file tools use manager automatically.

## Modifying extension lifecycle

- Serialize start/stop — never interleave.
- If extension has excludeTools, call maybeRefreshGeminiTools() after.
- Disconnect old MCP client before loading new config.
- Set correct source field on policy rules.

## Modifying config cascade

- Never modify ConfigParameters after passing to Config.
- New config fields need both parameter type and private field copy.
- Memory path changes: update all results in discoverMemoryPaths().
