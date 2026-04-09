---
description:
  Cross-file checklists for adding safety checkers and modifying checker rules
---

# Checklists

## Adding a new in-process checker

1. Implement `InProcessChecker` interface in
   `packages/core/src/safety/built-in.ts`.
2. Register in `packages/core/src/safety/registry.ts`
   (`getBuiltInInProcessCheckers`).
3. If new checker type needed, add to `InProcessCheckerType` enum in
   `packages/core/src/policy/types.ts`.
4. Add tests in `packages/core/src/safety/`.

## Modifying safety checker rules

1. Update `SafetyCheckerRule` interface in `packages/core/src/policy/types.ts`
   if adding new matching criteria.
2. Update `ruleMatches()` in `packages/core/src/policy/policy-engine.ts` if
   match logic changes.
3. Update `check()` method in `policy-engine.ts` (lines ~684-732) if decision
   logic changes.
4. Checkers are sorted by priority at construction time. Dynamic additions via
   `addChecker()` re-sort, but batch operations do not.

## Modifying Conseca

1. `setContext()` MUST be called during Config init (`config.ts`) — removing it
   causes silent fallback to ALLOW.
2. Policy caching keys off `activeUserPrompt` — changing this breaks caching.
3. Policy generation calls the LLM with the full tool registry JSON — large
   registries increase latency.
4. Update tests in `packages/core/src/safety/conseca/conseca.test.ts`.

## Modifying ContextBuilder

1. Update `SafetyCheckInput` in `packages/core/src/safety/protocol.ts` if
   context shape changes.
2. Update `ContextBuilder` in `packages/core/src/safety/context-builder.ts`.
3. Conseca's extractor assumes `context.history.turns` exists — verify
   compatibility.
