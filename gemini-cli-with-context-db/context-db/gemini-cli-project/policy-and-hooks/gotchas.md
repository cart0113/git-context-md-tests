---
description:
  Non-obvious traps in policy, hooks, and tool registration — MCP naming,
  priority math, stdout parsing, tool aliases, global deny behavior
---

# Policy and Hook Gotchas

## Hook stdout MUST be valid JSON only

The "Golden Rule": any output to stdout other than the final JSON object breaks
parsing. A single echo before the JSON causes the entire output to be treated as
a systemMessage. All debugging must go to stderr. Exit code 0 = parse JSON. Exit
code 2 = system block. Any other code = warning.

## MCP tool names split on first underscore

Names follow mcp*{serverName}*{toolName}. The parser splits on the FIRST
underscore after mcp\_. Server names with underscores break policy matching —
use hyphens.

## Policy priority is fractional

Final priority = tier_base + (toml_priority / 1000). Five tiers: Default=1,
Extension=2, Workspace=3, User=4, Admin=5. Priority 999 in User tier (base 4) =
4.999. Priority 1 in Admin tier (base 5) = 5.001.

## Global deny removes tool from model context

A deny rule without argsPattern completely hides the tool from the model — saves
tokens but irreversible per session. Argument-specific denials keep it visible.

## Tool aliases must be checked

Tools have canonical names and legacy aliases in TOOL_LEGACY_ALIASES. Policy and
hooks must check via getToolAliases(), not just canonical names.

## Project hooks are fingerprinted per session

Hooks in .gemini/hooks/ are fingerprinted. Name or command changes trigger
untrusted warnings.

## MCP tools bypass standard registration

MCP tools from McpClientManager skip the standard ToolRegistry pipeline. Some
lifecycle hooks may not fire for them.

## Tool definitions are model-dependent

modelFamilyService maintains separate tool declaration sets per model family.
Switching models mid-session does not re-resolve tools.

## Redirection requires per-rule permission

allowRedirection applies per-rule only. In chained commands, each command needs
its own permission.

See also:

- [Config and extension gotchas](../config-and-extensions/gotchas.md) for MCP
  server identity (clientKey hash), extension rule cleanup, and skill precedence
  — MCP-related gotchas span both files.
- [Safety gotchas](../safety/gotchas.md) for checker behavior that runs between
  policy evaluation and hook firing.
- [Policy engine docs](../../../docs/reference/policy-engine.md) — user-facing
  policy reference.
- [Hooks reference docs](../../../docs/hooks/reference.md) — user-facing hook
  API reference.
