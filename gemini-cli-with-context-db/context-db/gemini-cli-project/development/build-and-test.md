---
description:
  Non-obvious build/test guidance — workspace-specific test paths, when to skip
  preflight, nightly-only test suites
---

# Build and Test

Commands are in root `package.json`. Key non-obvious points:

## Workspace-specific tests

`npm test -w <pkg> -- <path>` — path must be relative to workspace root, not
repo root (e.g.,
`-w @google/gemini-cli-core -- src/routing/modelRouterService.test.ts`).

## Preflight is slow — use sparingly

`npm run preflight` runs clean, install, build, lint, typecheck, and test. Only
run at the very end before PR. Use targeted commands (`npm run test`,
`npm run lint`, workspace-specific tests) to iterate on fixes first.

Skip preflight entirely for non-code changes (docs, prompts).

## Memory and perf tests are nightly-only

Skip locally unless changing those areas.
