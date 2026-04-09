---
description:
  Traps in config loading, memory discovery, MCP management, extension
  lifecycle, and skill ordering
---

# Config and Extension Gotchas

## GEMINI.md hierarchy can conflict

Discovery scans CWD upward AND subdirectories. Subdirectory files can override
parents. Case-insensitive filesystems deduplicate by file identity.

## Memory refresh busts prompt cache

`refreshMcpContext()` invalidates the prompt cache. Only runs when extension
start/stop counts match — to batch changes. Extension lifecycle must serialize
around turns.

## MCP server identity is config hash

`clientKey` = hash(name + config + extensionId). Config changes between reloads
cause hash mismatch — old client not auto-disconnected. Disconnect explicitly
before loading new config.

## Skill precedence silently overrides

Load order: Built-in < Extensions < User < Workspace. Same-name skills collide
without warning. Skill disable is case-insensitive — UI shows "MySkill", disable
as "myskill".

## Extension rules track source for cleanup

Rules removed by `source` field on extension stop. Two extensions sharing a
source ID breaks cleanup.

See also: [Policy and hook gotchas](../policy-and-hooks/gotchas.md) for MCP tool
naming, policy priority math, and tool registration traps — MCP-related gotchas
span both files.
