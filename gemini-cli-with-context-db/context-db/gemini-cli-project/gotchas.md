---
description:
  Non-obvious traps — hook stdout parsing, MCP naming, policy priority math,
  sandbox persistence, tool aliases, and session fingerprinting
---

# Gotchas

## Hook stdout MUST be valid JSON only

The "Golden Rule": any output to stdout other than the final JSON object breaks
parsing. A single `echo` or `console.log` before the JSON causes the entire
output to be treated as a `systemMessage` instead of parsed. All debugging must
go to stderr. Exit code 0 = parse stdout as JSON. Exit code 2 = system block.
Any other code = warning (non-fatal).

## MCP tool names split on first underscore

MCP tool names follow `mcp_{serverName}_{toolName}`. The parser splits on the
FIRST underscore after `mcp_`. If the server name contains underscores (e.g.,
`my_server`), policy rules won't match — use hyphens (`my-server`).

## Policy priority is fractional

Final priority = `tier_base + (toml_priority / 1000)`. A priority of 999 in
User tier (base 3) becomes 3.999. Priority 1 in Admin tier (base 4) becomes
4.001. Rules within a tier are ordered by this fractional component.

## Global deny removes tool from model context

A policy rule with `decision = "deny"` and no `argsPattern` completely hides
the tool from the model — it won't even know the tool exists. Argument-specific
denials keep the tool visible but block specific invocations.

## Tool aliases must be checked

Tools have canonical names and legacy aliases in `TOOL_LEGACY_ALIASES`. Policy
rules and hooks must check aliases via `getToolAliases()`, not just canonical
names. Missing this breaks backward compatibility silently.

## Sandbox persistence on Windows

Windows Native sandbox uses `icacls` to set "Low Mandatory Level". These
integrity level changes persist after the session ends. If sandbox behavior
seems stuck, manually reset: `icacls "C:\path" /setintegritylevel Medium`.

## Session fingerprinting uses path hash

Sessions are stored per-project by hashing the absolute path. Moving a project
directory orphans its session history. No automatic migration.

## Project hooks are fingerprinted

Hooks in `.gemini/hooks/` are fingerprinted. If a hook's name or command
changes (e.g., via `git pull`), it's treated as untrusted and the user is
warned before execution. Per-session.

## GEMINI.md hierarchy can conflict

Memory discovery scans from CWD upward AND in subdirectories. Conflicting
GEMINI.md files at different levels resolve by hierarchy — subdirectory files
can override parent files. On case-insensitive filesystems, duplicate paths
with different casing are deduplicated by file identity.

## Worktree setup calls process.chdir() early

If a worktree is requested, `setupWorktree()` calls `process.chdir()` before
async tasks. This must happen before `loadCliConfig()` because config loading
depends on CWD being correct.
