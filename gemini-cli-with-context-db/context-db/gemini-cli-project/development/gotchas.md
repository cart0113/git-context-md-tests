---
description:
  Testing and contribution traps — vi.stubEnv vs process.env, license headers,
  import restrictions between packages
---

# Development Gotchas

## Use vi.stubEnv, not process.env

Use `vi.stubEnv('NAME', 'value')` in `beforeEach` and `vi.unstubAllEnvs()` in
`afterEach`. Modifying `process.env` directly causes test leakage. To "unset"
a variable, stub with empty string.

## License headers are ESLint-enforced

All new `.ts`, `.tsx`, `.js` files need the Apache-2.0 header with current year
(`Copyright 2026 Google LLC`). ESLint fails without it.

## No cross-package relative imports

Restricted relative imports between packages are enforced by ESLint. Use
package names (`@google/gemini-cli-core`) not relative paths.

## Conventional Commits required

Commit messages must follow Conventional Commits format. PRs should be small,
focused, and linked to an existing issue.
