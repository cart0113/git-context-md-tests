---
description:
  Build commands, test commands, preflight workflow, and workspace-specific
  test invocation
---

# Build and Test

## Build

- `npm install` — install deps.
- `npm run build` — build packages only.
- `npm run build:all` — packages + sandbox + VS Code companion.
- `npm run start` — run in dev mode.
- `npm run debug` — dev mode with Node.js inspector.

## Test

- `npm run test` — unit tests (all packages).
- `npm test -w <pkg> -- <path>` — workspace-specific. Path must be relative
  to workspace root (e.g., `-w @google/gemini-cli-core -- src/routing/modelRouterService.test.ts`).
- `npm run test:e2e` — integration/end-to-end tests.
- Memory and perf tests: nightly only. Skip locally unless changing those areas.

## Preflight

`npm run preflight` — clean, install, build, lint, typecheck, test. Slow.
Only run at the very end before PR. Use targeted commands (`npm run test`,
`npm run lint`, workspace-specific tests) to iterate on fixes first.

For non-code changes (docs, prompts), skip preflight entirely.
