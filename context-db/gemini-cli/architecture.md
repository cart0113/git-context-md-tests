---
description: >-
  High-level architecture — monorepo package map, CLI/core split, stable hook
  API contract (lossy round-trip gotcha), context merge vs settings override,
  model fallback chain, compression triggers
---

# Architecture

## Monorepo Package Map

8 packages: `core`, `cli`, `sdk`, `devtools`, `a2a-server`, `test-utils`,
`vscode-ide-companion`. The two that matter most:

- **`packages/cli`** — REPL, UI, command handlers, config loading, ACP client
- **`packages/core`** — Gemini API, tool registry, hook system, policy engine,
  agent scheduler, skills, MCP client, prompt engineering

## Key Core Subsystems and Entry Points

| Subsystem | Entry point                              | Why it matters                                              |
| --------- | ---------------------------------------- | ----------------------------------------------------------- |
| Tools     | `core/src/tools/tool-registry.ts`        | All tool discovery, MCP tools via `mcp-client-manager.ts`   |
| Agents    | `core/src/agents/registry.ts`            | Subagents wrapped as tools via `subagent-tool.ts`           |
| Policy    | `core/src/policy/policy-engine.ts`       | TOML rules in `core/src/policy/policies/`                   |
| Hooks     | `core/src/hooks/hookSystem.ts`           | Facade over `hookEventHandler.ts` + aggregator + planner    |
| Config    | `core/src/config/config.ts`              | Centralized, loads extensions via `extensions/integrity.ts` |
| Skills    | `core/src/skills/skillManager.ts`        | Loading + built-ins in `skills/builtin/`                    |
| Routing   | `core/src/routing/modelRouterService.ts` | Model selection strategy                                    |
| Safety    | `core/src/safety/checker-runner.ts`      | Includes experimental `conseca/`                            |

## Stable Hook API — But Lossy Round-Trip

Hooks consume `LLMRequest`/`LLMResponse` structures translated from the Google
SDK format via `hookTranslator`. Non-text parts (images) are filtered out.

**Gotcha:** The translator does a lossy round-trip. SDK-specific fields may not
survive `toHookLLMRequest()` → hook modification → `fromHookLLMRequest()`. If a
hook modifies a request and the translator drops an SDK field, that field is
silently lost. No error, no warning.

## Context vs Settings: Opposite Merge Strategies

- **Context (GEMINI.md):** Files are **combined** — global + project + component
  layers merge. `@file.md` import syntax for modular context.
- **Settings:** Override-based — workspace beats user beats system.

This distinction trips people up. Context accumulates, settings replace.

## Model Fallback Chain

- Rate-limited "pro" → CLI auto-switches to "flash" for the session
- Internal utilities (prompt completion, classification) silently fall back:
  `flash-lite` → `flash` → `pro` — no user prompt, no visibility
- `/model` command does NOT affect subagents — billing shows multiple models

## Compression

Fires at `model.compressionThreshold` (default 0.5 = 50% of context).
`PreCompress` hook is advisory only — async, best-effort, can't block.

See also:

- [hooks.md](hooks.md) — full hook event reference, implementation gotchas
  including the lossy round-trip in detail
- [configuration-and-policies.md](configuration-and-policies.md) — the 7-layer
  config precedence and policy engine that governs tool/agent permissions
