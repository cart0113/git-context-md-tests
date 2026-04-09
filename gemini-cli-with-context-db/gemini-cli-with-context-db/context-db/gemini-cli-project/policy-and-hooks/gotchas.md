---
description:
  Non-obvious traps in policy, hooks, and tool registration — MCP naming, priority
  math, stdout parsing, tool aliases, global deny behavior
---

# Policy and Hook Gotchas

## Hook stdout MUST be valid JSON only

The "Golden Rule": any output to stdout other than the final JSON object breaks
parsing. A single `echo` or `console.log` before the JSON causes the entire
output to be treated as a `systemMessage` instead of parsed. All debugging must
go to stderr. Exit code 0 = parse as JSON. Exit code 2 = system block. Any
other code = warning (non-fatal).

## MCP tool names split on first underscore

MCP tool names follow `mcp_{serverName}_{toolName}`. The parser splits on the
FIRST underscore after `mcp_`. Server names with underscores (e.g., `my_server`)
break policy matching — use hyphens (`my-server`).

## Policy priority is fractional

Final priority = `tier_base + (toml_priority / 1000)`. Priority 999 in User
tier (base 3) = 3.999. Priority 1 in Admin tier (base 4) = 4.001.

## Global deny removes tool from model context

A policy rule with `decision = "deny"` and no `argsPattern` completely hides the
tool from the model — it won't even know it exists. Saves tokens but irreversible
per session. Argument-specific denials keep the tool visible.

## Tool aliases must be checked

Tools have canonical names and legacy aliases in `TOOL_LEGACY_ALIASES`. Policy
rules and hooks must check aliases via `getToolAliases()`, not just canonical
names.

## Project hooks are fingerprinted

Hooks in `.gemini/hooks/` are fingerprinted per session. If a hook's name or
command changes (e.g., via `git pull`), it's treated as untrusted and the user
is warned.

## MCP tools bypass standard registration

MCP tools discovered at runtime don't go through the standard `ToolRegistry`
pipeline. They're dynamically added via `McpClientManager`. Some standard tool
lifecycle hooks may not fire for MCP tools.

## Tool definitions are model-dependent

Different models see different tool declarations. `modelFamilyService` maintains
separate sets for model families (legacy, gemini-3). Switching models
mid-session doesn't re-resolve tools — the set is fixed per session start.

## Redirection requires per-rule permission

`allowRedirection` in policy rules applies only to that specific rule. In
chained commands (`cmd1 > file && cmd2`), each command's rule must permit
redirection independently.
