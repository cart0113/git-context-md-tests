---
description:
  Non-obvious traps in config loading, memory discovery, MCP management,
  extension lifecycle, and skill ordering
---

# Config and Extension Gotchas

## GEMINI.md hierarchy can conflict

Memory discovery scans from CWD upward AND in subdirectories. Conflicting
GEMINI.md files at different levels resolve by hierarchy — subdirectory files
can override parents. On case-insensitive filesystems, duplicate paths with
different casing are deduplicated by file identity.

## JIT subdirectory discovery is lazy

`discoverContext()` for subdirectories only runs on tool access, not upfront.
Memory context may be incomplete until the first tool touches that directory.

## Memory refresh busts prompt cache

`refreshMcpContext()` calls both `memoryContextManager.refresh()` and
`refreshServerHierarchicalMemory()`. This invalidates the prompt cache. Only
done when extension start/stop counts match — to batch changes.

## ConfigParameters must be treated as immutable

Many config params are copied to private fields in the constructor. If
`ConfigParameters` is modified after passing to `Config`, internal state
becomes inconsistent.

## Session fingerprinting uses absolute path hash

Sessions are stored per-project by hashing the absolute path. Moving a project
directory orphans its session history. No automatic migration.

## Worktree setup calls process.chdir() early

`setupWorktree()` calls `process.chdir()` before async tasks. Must happen
before `loadCliConfig()` because config loading depends on CWD.

## MCP server config hashing determines identity

Server configs are hashed to generate `clientKey` (name + config + extensionId).
If an extension changes config between reloads, old client isn't disconnected
because the hash doesn't match.

## MCP has two-level disable

A server is disabled if EITHER `isSessionDisabled()` OR `isFileEnabled()`
returns true. User can disable at file level but session disable overrides —
not obvious why enablement doesn't work.

## Skill precedence silently overrides

Skills loaded in order: Built-in < Extensions < User < Workspace. Later tiers
silently override earlier. Same-name skills collide without warning.

## Skill disable is case-insensitive

Disabled names are lowercased at check time but skill names are not normalized
at storage time. UI shows "MySkill" but you must disable as "myskill".

## Extension start/stop must not interleave

`startingCount/startCompletedCount` counters batch refresh operations.
`maybeRefreshMemories()` only runs when both counts match. Interleaving
start/stop calls delays refreshes unpredictably.

## Extension policy rules track source for cleanup

Rules registered with `source` field are removed by source when extension
stops. If two extensions share a source ID, removal breaks one of them.
