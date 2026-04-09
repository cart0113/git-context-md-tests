---
description: >-
  Extensions vs skills — when to use which, install creates copies not symlinks,
  name-must-match-directory silent failure, only 3 variables, extension policies
  can't allow/yolo, skill activation is model-initiated, precedence and conflict
  rules, custom command processing order gotcha
---

# Extensions and Skills

## Extensions vs Skills — When to Use Which

- **Extension context (GEMINI.md)** — always loaded, always costs tokens. Use
  for essential, always-needed behavior.
- **Skills** — loaded only when activated via `activate_skill` tool. Use for
  complex, occasional workflows. Saves token budget.

Putting everything in extension context is wasteful. Complex occasional
workflows should be skills.

## Extension Gotchas

**Installation creates COPIES, not symlinks.** Changes to the source repo don't
auto-sync. Users must run `gemini extensions update` or enable `--auto-update`
at install time.

**Extension name must match directory name exactly.** Silent failure if they
don't match — the extension just won't load.

**Only 3 variable substitutions work:** `${extensionPath}`, `${workspacePath}`,
`${/}`. Nothing else. No `${homeDir}`, no `${PWD}`.

**Extension policies cannot use `allow` or `yolo`.** Security restriction —
extensions are limited to `ask_user` decisions. You cannot ship an extension
that auto-approves dangerous operations.

**MCP server precedence is inverted:** settings.json overrides extension-defined
MCP servers with the same name (not the other way around).

## Skills Gotchas

**Skills are activated by the model, not user-initiated.** Users can't
force-activate via command. The model decides based on the skill's
`description`. Optimizing the description is key to consistent usage.

**Every activation requires user consent.** No "always activate" mode. This is
intentional — prevents extensions from silently loading complex instructions.

## Precedence (All Scoped Items)

**Workspace > User > Extension.** Within the same tier, `.agents/skills/` takes
precedence over `.gemini/skills/`.

## Command Conflicts

Extension commands get renamed with dot prefix if they collide with user/project
commands (e.g., `/gcp.deploy`). Extensions are second-class citizens in naming.

## Custom Command Gotchas

**Argument handling is mode-based:** presence of `{{args}}` changes behavior.
With it: args injected at placeholder. Without it: args appended to end.

**File injection (`@{...}`) is processed BEFORE shell commands (`!{...}`) and
argument substitution (`{{args}}`).** You can't use args to build a path for
file injection.

**Shell injection (`!{...}`) always requires interactive user confirmation.** No
batch mode. Affects automation workflows.

## Source Code Pointers

- Extension loading: `core/src/commands/extensions.ts`
- Integrity checking: `core/src/config/extensions/integrity.ts`
- Skill management: `core/src/skills/skillManager.ts` + `skillLoader.ts`
- Built-in skills: `core/src/skills/builtin/`

Extension manifests aren't validated at install time against referenced files.
If `contextFileName` or `commands/` entries reference missing files, they
silently fail to load.

## Gallery and Release Gotchas

Extensions aren't submitted to a registry. Auto-crawled daily from GitHub repos
with `gemini-cli-extension` topic. Forget the topic = not discoverable.

`gemini-extension.json` must be at root of the archive, not nested. Platform
binaries: `{platform}.{arch}.{name}.{extension}` — typos silently fall back to
generic. `migratedTo` field enables seamless repo moves without breaking
installs.

See also:

- [configuration-and-policies.md](configuration-and-policies.md) — extension
  policy tier (base 2), why extensions can't use allow/yolo, MCP server
  precedence details
- [hooks.md](hooks.md) — extension hooks require explicit approval, security
  model for third-party hooks
