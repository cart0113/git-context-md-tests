---
description: >-
  7-layer config precedence, policy engine tier math (tier always beats
  within-tier priority), MCP underscore naming trap, mode-aware approval
  cascading, deny removes tool from context, .geminiignore requires restart,
  YOLO is CLI-flag-only
---

# Configuration and Policies

## 7-Layer Config Precedence

defaults → system-defaults → user → project → system-override → env vars → CLI
flags

- System-override locations: `/Library/Application Support/GeminiCli/` (macOS),
  `/etc/gemini-cli/` (Linux), `C:\ProgramData\gemini-cli\` (Windows)
- Env var references in settings.json: `$VAR`, `${VAR}`, `${VAR:-DEFAULT}`
- Extensions get their own `.env` auto-loaded per extension

**Gotcha:** `general.autoConfigureMemory` is ONLY read from global user settings
— ignores workspace overrides because memory allocation happens at boot.

Source: `core/src/config/config.ts` (centralized Config class),
`cli/src/config/config.ts` (CLI-specific loading).

## Policy Engine — Tier Math

Source: `core/src/policy/policy-engine.ts`, rules in
`core/src/policy/policies/`.

```
final_priority = tier_base + (toml_priority / 1000)
```

| Tier      | Base | Source                              |
| --------- | ---- | ----------------------------------- |
| Default   | 1    | Built-in TOML in `policy/policies/` |
| Extension | 2    | Extension policies                  |
| Workspace | 3    | `.gemini/policies/*.toml`           |
| User      | 4    | `~/.gemini/policies/*.toml`         |
| Admin     | 5    | System locations                    |

**Tiers always dominate.** A `priority: 999` Workspace rule (= 3.999) loses to a
`priority: 1` User rule (= 4.001).

## MCP Server Naming Trap

**MCP server names MUST NOT contain underscores.** The FQN parser splits on the
first underscore after `mcp_` prefix. Use hyphens (`my-server` not `my_server`).

Related: `excludeTools` beats `includeTools` when both match. MCP environment
redaction auto-strips `*TOKEN*`, `*SECRET*`, `*PASSWORD*`, `*KEY*`, `*AUTH*`,
`*CREDENTIAL*` vars by default. OAuth tokens stored in plaintext at
`~/.gemini/mcp-oauth-tokens.json`.

## Mode-Aware Approval Cascading

| Granted in    | Creates rule for        |
| ------------- | ----------------------- |
| Plan mode     | ALL modes               |
| Default mode  | default, autoEdit, yolo |
| AutoEdit mode | autoEdit, yolo          |
| Yolo mode     | yolo only               |

Trust flows to more permissive modes, never to more restricted.

**Gotcha:** Approvals from non-plan modes do NOT apply to Plan Mode.

## Deny Removes Tool from Context

When a tool is globally denied (no argsPattern), it's completely **removed from
the model's context** — not just blocked. Saves tokens and improves security.

## .geminiignore

Changes require **SESSION RESTART**. Not hot-reloaded. Follows `.gitignore`
syntax. Custom ignore paths via `context.fileFiltering.customIgnoreFilePaths`
(earlier entries take priority).

## YOLO Mode

CLI flag only (`--yolo` or `--approval-mode=yolo`). Cannot be set in
settings.json. Intentional.

## Key Settings Gotchas

- `tools.disableLLMCorrection` (default: true) — edit tools fail on mismatch, no
  AI self-correction
- `tools.truncateToolOutputThreshold` (default: 40000 chars)
- `model.compressionThreshold` (default: 0.5) — triggers at 50% context
- `security.enableConseca` — experimental context-aware security using LLM
- `.env` files don't work for gemini-cli process (auto-excluded). Use
  `.gemini/.env` instead

See also:

- [hooks.md](hooks.md) — hook config hierarchy (project > user > system >
  extensions), env redaction for hook security
- [extensions-and-skills.md](extensions-and-skills.md) — extension policies
  can't allow/yolo (security restriction at tier 2)
- [subagents.md](subagents.md) — subagent-specific policy targeting via
  `subagent` field in TOML rules
- [tools-and-modes.md](tools-and-modes.md) — mode-aware approval hierarchy, plan
  mode tool boundary
