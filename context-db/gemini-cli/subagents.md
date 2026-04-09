---
description: >-
  Subagent isolation model — agents wrapped as tools via subagent-tool.ts,
  recursion protection (cannot call other subagents even with * wildcard),
  inline MCP servers, policy targeting by subagent name, browser agent sandbox
  quirks, remote agent auth gotchas
---

# Subagents

## Core Concept

Subagents are specialists exposed to the main agent as **tools of the same
name**. Implemented in `core/src/agents/subagent-tool.ts` which wraps agent
execution as a tool call. The agent registry (`registry.ts`) discovers and loads
definitions, the scheduler (`agent-scheduler.ts`) manages execution.

## Isolation Model (Critical)

Each subagent has:

- **Independent context window** — separate conversation history, saves tokens
  in main history
- **Isolated tools** — restricted or specialized toolset via `tools` field
- **Recursion protection** — subagents **cannot call other subagents**, even
  with `*` wildcard. Prevents infinite loops and context bloat.

## Tool Wildcards

- `*` — all available tools (except other subagents)
- `mcp_*` — all MCP tools
- `mcp_myserver_*` — all tools from specific MCP server

## Agent Definition Files

Located at `.gemini/agents/*.md` (project) or `~/.gemini/agents/*.md` (user).
Must start with YAML frontmatter. Markdown body becomes the agent's system
prompt.

**Optimizing the `description` field is key** — the main agent reads it to
decide when to delegate. Include areas of expertise and example scenarios.

Inline `mcpServers` in frontmatter are **isolated to that agent** — don't affect
the global registry.

## Subagent-Specific Policies

Policy rules in `policy.toml` can target specific subagents:

```toml
[[rules]]
subagent = "pr-creator"
action = "allow"
toolName = "run_shell_command"
commandPrefix = "git push"
```

Rules without `subagent` field apply universally. Two override levels in
settings.json: `agents.overrides` (enable/disable + run config) and
`modelConfigs.overrides` (custom model settings via `overrideScope`).

## Multi-Agent Files (Remote Only)

A single `.md` file can define multiple remote subagents. Mixing local and
remote, or multiple local agents in one file, is NOT supported.

## Remote Agent Auth

Four auth methods: `apiKey`, `http` (Bearer/Basic), `google-credentials` (ADC),
`oauth` (PKCE flow).

**Dynamic value resolution:** `$ENV_VAR`, `!command` (shell exec), literal. Use
`$$` or `!!` to escape the prefix.

**Google ADC auto-selects token type by host:** `*.googleapis.com` → access
token, `*.run.app` → identity token. Only Google-owned hosts allowed.

**Agent card fetch tries unauthenticated first**, then retries with auth on
401/403. All auth auto-retries up to 2 times on failure. `!command` values are
re-executed on retry for fresh credentials.

## Browser Agent Sandbox Quirks

- **macOS seatbelt** forces `isolated` + `headless` (persistent profiles fail)
- **Docker** disabled unless `sessionMode: "existing"`, connects to host Chrome
  via `host.docker.internal:9222` (hardcoded port)
- Domain restrictions detect and block domain-as-proxy attacks
- Hard-blocks: `file://`, `javascript:`, `data:`, `chrome://extensions`,
  `chrome://settings/passwords`
- `maxActionsPerTask` (default 100) prevents runaway automation

See also:

- [configuration-and-policies.md](configuration-and-policies.md) — policy tier
  math for subagent-specific rules, MCP server naming trap (relevant for inline
  MCP servers)
- [architecture.md](architecture.md) — agent registry and scheduler entry points
  in the monorepo
