---
description:
  Non-obvious traps in config loading, memory discovery, MCP management,
  extension lifecycle, and skill ordering
---

# Config and Extension Gotchas

## GEMINI.md hierarchy can conflict

Discovery scans CWD upward AND subdirectories. Subdirectory files can override
parents. Case-insensitive filesystems deduplicate by file identity.

## JIT subdirectory discovery is lazy

discoverContext() for subdirectories runs on tool access, not upfront. Memory
context may be incomplete until the first tool touches that directory.

## Memory refresh busts prompt cache

refreshMcpContext() invalidates prompt cache. Only runs when extension
start/stop counts match to batch changes.

## ConfigParameters must be treated as immutable

Many params copied to private fields in constructor. Modifying after passing
to Config causes inconsistent internal state.

## Session uses absolute path hash

Moving a project directory orphans session history. No migration.

## Worktree chdir happens early

setupWorktree() calls process.chdir() before loadCliConfig(). Config loading
depends on CWD being correct.

## MCP server identity is config hash

clientKey = hash(name + config + extensionId). Config changes between reloads
cause hash mismatch — old client not auto-disconnected.

## MCP has two-level disable

Server disabled if EITHER isSessionDisabled() OR isFileEnabled(). Session
disable overrides file-level enable.

## Skill precedence silently overrides

Load order: Built-in < Extensions < User < Workspace. Same-name skills collide
without warning.

## Skill disable is case-insensitive

Disabled names lowercased at check time, skill names not normalized at storage.
UI shows MySkill, disable as myskill.

## Extension start/stop must not interleave

Counter-based batching delays refreshes if operations overlap. Serialize
lifecycle operations.

## Extension rules track source for cleanup

Rules removed by source field on extension stop. Shared source IDs between
extensions break cleanup.
