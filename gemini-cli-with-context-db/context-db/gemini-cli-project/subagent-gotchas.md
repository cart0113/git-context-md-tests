---
description:
  Traps in subagent configuration — recursion protection, browser agent
  prerequisites, tool inheritance, container sandbox behavior
---

# Subagent Gotchas

## Subagents cannot call other subagents

Recursion protection is enforced: even if a subagent has the `*` tool wildcard,
it cannot see or invoke other agents. This prevents infinite loops and token
runaway but means multi-agent orchestration must go through the main agent.

## browser_agent is disabled by default

Unlike the other 3 built-in subagents (`codebase_investigator`, `cli_help`,
`generalist_agent`), `browser_agent` must be explicitly enabled via
`agents.overrides` in settings.json. It requires Chrome 144+. The underlying
`chrome-devtools-mcp` server is bundled — no separate install needed.

## Omitting tools list inherits ALL tools

If a custom subagent definition omits the `tools` field, the subagent inherits
every tool from the parent session — including MCP tools and mutating tools.
Always specify an explicit tool list for subagents that should be read-only or
restricted.

## Container sandbox changes browser_agent behavior

In Docker/Podman sandboxes, Chrome isn't available inside the container. The
browser agent is disabled unless `sessionMode` is `"existing"`. In existing
mode, it connects to the host via `host.docker.internal:9222` (hardcoded port).
Under macOS seatbelt, persistent/isolated modes are forced to isolated+headless.

## First-run consent dialog blocks automation

The first time `browser_agent` is invoked, a consent dialog appears. This only
happens once, but it will block headless/CI runs if the profile hasn't been
initialized interactively first.

See also:

- [Subagent docs](../../docs/core/subagents.md) — user-facing subagent guide.
- [Design decisions](design-decisions.md) — why subagents return via
  complete_task tool.
